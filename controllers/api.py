#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from copy import copy
import datetime
from traceback import format_exc, print_exc
# from gluon.contrib.generics import pdf_from_html
from gluon.serializers import json as json_serializer
import json
import os
from pprint import pprint
from paideia import Walk
from paideia_utils import GreekNormalizer
from paideia_stats import Stats, get_set_at_date, get_term_bounds
from paideia_stats import get_current_class, get_chart1_data, my_custom_json
from paideia_bugs import Bug, trigger_bug_undo
import re
# from pydal.objects import Rows

from gluon._compat import urllib2, urlencode, urlopen, to_bytes, to_native

if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request
    db = current.db


def download():
    """
    allows downloading of uploaded files

    expects the request variable "filename"
    """
    db = current.db
    mystream = response.download(request, db)

    return mystream


def get_prompt():
    """
    Return the data to begin a step interaction.

    Private api method to handle calls from the react front-end.

    Returns:
        JSON object with the following keys:

        sid: int
        prompt_text: string
        audio: dict
        widget_img: string
        instructions: ???
        slidedecks: dict
        bg_image: string
        loc: string
        response_buttons: []
        response_form: {form_type: "text", values: null}
        bugreporter: ???
        pre_bug_step_id: int
        npc_image: string
        completed_count: int
        category: int
        pid: int
        new_content: bool
        paideia_debug: ???
    """
    auth = current.auth
    session = current.session
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = request.vars.new_user
        stepargs = {'path': None,
                    'step': None,
                    'response_string': None,
                    'set_blocks': None,
                    'repeat': False
                    }
        for k, v in request.vars.items():
            if k in stepargs.keys() \
                    and k not in ['loc', 'new_user', 'response_string']:
                stepargs[k] = v
        if session.set_review and session.set_review > 0:
            stepargs['set_review'] = session.set_review
        else:
            stepargs['set_review'] = False
        resp = Walk(new_user=new_user).start(myloc, **stepargs)
        return json_serializer(resp)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def evaluate_answer():
    """
    Private api method to handle calls from the react front-end.
    """
    auth = current.auth
    session = current.session
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = False
        stepargs = {'path': None,
                    'response_string': request.vars.response_string,
                    'set_blocks': None
                    }
        for k, v in request.vars.items():
            if k in stepargs.keys() \
                    and k not in ['loc', 'new_user']:
                stepargs[k] = v
        if session.set_review and session.set_review > 0:
            stepargs['set_review'] = session.set_review
        else:
            stepargs['set_review'] = False
        resp = Walk(new_user=new_user).start(myloc, **stepargs)
        resp['eval_text'] = copy(resp['prompt_text'])
        resp['prompt_text'] == None
        return json_serializer(resp)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def _fetch_current_coursedata(uid, mydatetime):
    """
    Private function called by _fetch_userdata and get_profile_info

    """
    current_class = get_current_class(uid, mydatetime)
    course = {}
    if current_class:
        course['daily_quota'] = current_class['classes']['paths_per_day']
        course['weekly_quota'] = current_class['classes']['days_per_week']
        course['class_info'] = {k: v for k, v in
                                current_class['classes'].items()
                                if k in ['institution', 'academic_year',
                                        'term', 'course_section',
                                        'start_date',
                                        'end_date', 'paths_per_day',
                                        'days_per_week', 'instructor',
                                        'a_target', 'a_cap', 'b_target',
                                        'b_cap', 'c_target', 'c_cap',
                                        'd_target', 'd_cap', 'f_target']
                                }
        abs_startdt = course['class_info']['start_date']

        if current_class['class_membership']['custom_start'] is not None:
            course['class_info']['custom_start_date'] = \
                current_class['class_membership']['custom_start']
            abs_startdt = course['class_info']['custom_start_date']

        course['class_info']['custom_end_date'] = \
            current_class['class_membership']['custom_end']

        mystartset = current_class['class_membership']['starting_set']
        if mystartset is None:
            mystartset = get_set_at_date(uid, abs_startdt)
        course['class_info']['starting_set'] = mystartset

    else:
        course['daily_quota'] = 20
        course['weekly_quota'] = 5
        course['class_info'] = {}

    return course


def _fetch_userdata(raw_user, vars):
    """
    Private function called by get_login and get_userdata

    This is where the actual user data collection happens
    """
    try:
        user = {k:v for k, v in raw_user.items() if k in
                ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
        memberships = db((db.auth_membership.user_id == user['id']) &
                            (db.auth_membership.group_id == db.auth_group.id)
                            ).select(db.auth_group.role).as_list()
        user['roles'] = [m['role'] for m in memberships]

        if any(r for r in ['instructors', 'administrators']
                if r in user['roles']):
            instructing = db(db.classes.instructor == user['id']).select()
            if instructing:
                user['instructing'] = []
                for i in instructing:
                    user['instructing'].append({k: v for k, v in i.items()
                        if k in ['id', 'days_per_week',
                                 'institution', 'academic_year',
                                 'term', 'course_section',
                                 'instructor', 'start_date',
                                 'end_date', 'paths_per_day',
                                 'a_target', 'a_cap', 'b_target',
                                 'b_cap', 'c_target', 'c_cap',
                                 'd_target', 'd_cap', 'f_target']
                    })
            else:
                user['instructing'] = None

        user.update(**_fetch_current_coursedata(user['id'],
                                                datetime.datetime.utcnow())
                    )

        my_progress = db(db.tag_progress.name == user['id']
                             ).select().first()
        user['current_badge_set'] = my_progress.latest_new if my_progress else 0

    except AttributeError:  # if login response was False and has no items
        print(format_exc())
        user = {'id': None}

    return user


def get_registration():
    """
    """
    debug=False
    request = current.request
    auth = current.auth
    response = current.response
    token = request.vars['my_token'].strip()
    email = request.vars['my_email'].strip()
    password = request.vars['my_password'].strip()
    tz = request.vars['my_time_zone'].strip()
    first_name = request.vars['my_first_name'].strip()
    last_name = request.vars['my_last_name'].strip()

    str_pat = re.compile('^[a-zA-Z0-9\s\-\/_]+$')
    email_pat = re.compile('^[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w+$')
    missing = {k: v for k, v in request.vars.items() if
               k not in ["my_token", "my_password"] and
               ((v in ["undefined", None, ""])
                or (k!="my_email" and not re.search(str_pat, v.strip()))
                or (k=="my_email" and not re.search(email_pat, v.strip()))
                )}
    if missing and len(missing.keys()) > 0:
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Missing request data',
                    'error': missing})

    # TODO: consider this regex that requires special characters:
    # password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
        # "(?=.*[!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~])"\
        # "[A-Za-z\d!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~]{8,20}$"
    password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
                     "[A-Za-z\d!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~]{8,20}$"
    password_pat = re.compile(password_regex)
    if re.search(password_pat, password) is None:
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Password is not strong enough',
                    'error': None})

    existing_user_count = db(db.auth_user.email==email).count()
    if existing_user_count>0:
        response.status = 409
        return json_serializer({'status': 'conflict',
                    'reason': 'User with this email exists',
                    'error': None})
    else:
        if debug: print("in api: registering new user***************")

        keydata = {}
        with open('applications/paideia/private/app.keys', 'r') as keyfile:
            for line in keyfile:
                k, v = line.split()
                keydata[k] = v
        params = urlencode({
            'secret': keydata['captcha3_private_key'],
            'response': token
        }).encode('utf-8')
        recap_request = urllib2.Request(
            url="https://www.google.com/recaptcha/api/siteverify",
            data=to_bytes(params),
            headers={'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': 'reCAPTCHA Python'})
        httpresp = urlopen(recap_request)
        content = httpresp.read()
        httpresp.close()
        response_dict = json.loads(to_native(content))
        if debug: pprint(response_dict)

        if response_dict["success"] == True and response_dict["score"] > 0.5:
            try:
                response_data = auth.register_bare(email=email,
                                                   password=password,
                                                   first_name=first_name,
                                                   last_name=last_name,
                                                   time_zone=tz,
                                                   )
                response_data = response_data.as_dict()
                response_data = {k: v for k, v in response_data.items()
                                if k in ["email", "first_name",
                                         "last_name", "id"]}
                return json_serializer(response_data)
            except Exception:
                print_exc()
                response.status = 500
                return json_serializer({'status': 'internal server error',
                            'reason': 'Unknown error in function get_registration',
                            'error': format_exc()})
        else:
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                        'reason': 'Recaptcha failed',
                        'error': None})


def get_login():
    """
    API method to log a user in with web2py's authentication system.

    Private api method to handle calls from the react front-end.

    Returns:
        JSON object with data on the user that was successfully logged in. If the login is unsuccessful, the JSON object carries just an 'id' value of None.
    """
    auth = current.auth
    session = current.session
    try:

        mylogin = auth.login_bare(request.vars['email'],
                                request.vars['password'])
        user = {k:v for k, v in mylogin.items() if k in
                ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
        pprint(user)
        full_user = _fetch_userdata(user, request.vars)
        full_user['review_set'] = session.set_review \
            if 'set_review' in session.keys() else None
        return json_serializer(full_user, default=my_custom_json)
    except Exception as e:
        print_exc()
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Login failed',
                     'error': format_exc()})


def get_userdata():
    """
    API method to get the user data for the currently logged in user.
    """
    auth = current.auth
    session = current.session
    if auth.is_logged_in():
        user = db.auth_user(auth.user_id).as_dict()
        full_user = _fetch_userdata(user, request.vars)
        full_user['review_set'] = session.set_review \
            if 'set_review' in session.keys() else None
        return json_serializer(full_user, default=my_custom_json)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def do_logout():
    """
    API method to log the current user out.

    Private api method to handle calls from the react front-end.

    Returns:
        JSON object with the same user fields returned at login, but with null
        values for each one.
    """
    print("about to log out")
    auth = current.auth
    try:
        mylogout = auth.logout_bare()
        print ("did logout")
        myuser = {k:None for k in ['email', 'first_name', 'last_name',
                                   'hide_read_queries', 'id', 'time_zone']}
        return json_serializer(myuser)
    except Exception as e:
        print(e)
        return json_serializer({'error': e})


def check_login():
    """
    API method to return the current server login status.

    """
    auth = current.auth
    session = current.session
    my_login = {'logged_in': False, 'user': 0}
    if auth.is_logged_in():
        my_login['logged_in'] = True
        my_login['user'] = auth.user_id
    return json_serializer(my_login)


def _add_posts_to_queries(queries):

    for idx, q in enumerate(queries):
        if q['bugs']['posts']:
            myposts = db(
                (db.bug_posts.id.belongs(q['bugs']['posts'])) &
                (db.bug_posts.poster==db.auth_user.id) &
                ((db.bug_posts.deleted == False) |
                 (db.bug_posts.deleted == None))
                ).select(db.auth_user.first_name,
                         db.auth_user.last_name,
                         db.bug_posts.id,
                         db.bug_posts.poster,
                         db.bug_posts.poster_role,
                         db.bug_posts.dt_posted,
                         db.bug_posts.post_body,
                         db.bug_posts.modified_on,
                         db.bug_posts.hidden,
                         db.bug_posts.deleted,
                         db.bug_posts.flagged,
                         db.bug_posts.public,
                         db.bug_posts.thread_index,
                         db.bug_posts.pinned,
                         db.bug_posts.popularity,
                         db.bug_posts.helpfulness,
                         db.bug_posts.comments,
                         orderby=db.bug_posts.thread_index
                         ).as_list()

            if not auth.has_membership('administrators'):
                if auth.has_membership('instructors'):
                    myposts = list(filter(
                        lambda x: x['bug_posts']['public'] is True
                        or x['bug_posts']['poster'] == auth.user_id
                        or _is_my_student(auth.user_id, x['bug_posts']['poster']),
                        myposts))
                else:
                    myposts = list(filter(
                        lambda x: x['bug_posts']['public'] is True
                        or x['bug_posts']['poster'] == auth.user_id,
                        myposts))
            for i, p in enumerate(myposts):
                mycomments = []
                if p['bug_posts']['comments']:
                    mycomments = db(
                        (db.bug_post_comments.id.belongs(p['bug_posts']['comments']))
                        & (db.bug_post_comments.commenter==db.auth_user.id) &
                        ((db.bug_post_comments.deleted == False) |
                         (db.bug_post_comments.deleted == None))
                        ).select(db.bug_post_comments.id,
                                 db.bug_post_comments.commenter,
                                 db.auth_user.first_name,
                                 db.auth_user.last_name,
                                 db.bug_post_comments.commenter_role,
                                 db.bug_post_comments.dt_posted,
                                 db.bug_post_comments.on_post,
                                 db.bug_post_comments.thread_index,
                                 db.bug_post_comments.comment_body,
                                 db.bug_post_comments.public,
                                 db.bug_post_comments.hidden,
                                 db.bug_post_comments.deleted,
                                 db.bug_post_comments.flagged,
                                 db.bug_post_comments.pinned,
                                 db.bug_post_comments.popularity,
                                 db.bug_post_comments.helpfulness,
                                 db.bug_post_comments.modified_on,
                                 orderby=db.bug_post_comments.thread_index
                                 ).as_list()

                    if not auth.has_membership('administrators'):
                        if auth.has_membership('instructors'):
                            mycomments = list(filter(
                                lambda x: x['bug_post_comments']['public'] is True
                                or x['bug_post_comments']['commenter'] == auth.user_id
                                or _is_my_student(auth.user_id, x['bug_post_comments']['commenter']),
                                mycomments))
                        else:
                            mycomments = list(filter(
                                lambda x: x['bug_post_comments']['public'] is True
                                or x['bug_post_comments']['commenter'] == auth.user_id,
                                mycomments))
                myposts[i]['comments'] = mycomments

            queries[idx]['posts'] = myposts
        else:
            queries[idx]['posts'] = []

    return queries


def _fetch_queries(stepid=0, userid=0, nonstep=True, unanswered=False,
                   pagesize=50, page=0, orderby="date_submitted"):
    """
    Return a list of student queries from the db.bugs table.

    If nonstep=True, this only returns general queries that aren't
    linked with a particular step.

    If unanswered=True, this only returns queries that have not yet been
    answered.

    pagination, via the "page" parameter, is zero indexed
    """
    offset_start = pagesize * page
    offset_end = offset_start + pagesize
    table_fields = [db.bugs.id,
                    db.bugs.user_name,
                    db.bugs.step,
                    db.bugs.in_path,
                    db.bugs.prompt,
                    db.bugs.step_options,
                    db.bugs.user_response,
                    db.bugs.score,
                    db.bugs.adjusted_score,
                    db.bugs.log_id,
                    db.bugs.user_comment,
                    db.bugs.date_submitted,
                    db.bugs.bug_status,
                    db.bugs.admin_comment,
                    db.bugs.deleted,
                    db.bugs.public,
                    db.bugs.posts,
                    db.bugs.pinned,
                    db.bugs.popularity,
                    db.bugs.helpfulness,
                    db.bugs.user_role,
                    db.auth_user.id,
                    db.auth_user.first_name,
                    db.auth_user.last_name]
                    # FIXME:  re-add db.bugs.hidden here and in model,

    queries = []

    if unanswered:
        answered_rows = db(db.bug_posts.id > 0)._select(db.bug_posts.on_bug)
        unanswered_term = ~(db.bugs.id.belongs(answered_rows))
        print("filtering for unanswered")
        print("raw unanswered finds {} of {} rows".format(
            db(unanswered_term).count(),
            db(db.bugs.id > 0).count()
            ))
    else:
        unanswered_term = True

    if nonstep is True:
        #  requesting general queries not tied to a step
        queries = db((db.bugs.step == None) &
                     (db.bugs.user_name == db.auth_user.id) &
                     ((db.bugs.deleted == False) | (db.bugs.deleted == None)) &
                     (unanswered_term)
                    )
    elif stepid > 0 & nonstep==False:
        #  requesting queries on specified step
        queries = db((db.bugs.step == stepid) &
                     (db.bugs.user_name == db.auth_user.id) &
                     ((db.bugs.deleted == False) | (db.bugs.deleted == None)) &
                     (unanswered_term)
                     )
    elif stepid==0 & nonstep==False:
        #  requesting queries on all steps
        queries = db((db.bugs.step != None) &
                     (db.bugs.user_name == db.auth_user.id) &
                     ((db.bugs.deleted == False) | (db.bugs.deleted == None)) &
                     (unanswered_term)
                     )
    queries_rows = queries.select(*table_fields,
                                  limitby=(offset_start, offset_end),
                                  orderby=~db.bugs[orderby]
                                  )
    queries_recs = queries_rows.as_list()
    print("in _fetch_queries===============================")
    print("got {} query rows".format(len(queries_recs)))
    queries_recs = _add_posts_to_queries(queries_recs)


    #  collect queries posted by current user

    if userid and userid > 0:
        user_queries = [q for q in queries_recs
                        if q['auth_user']['id'] == userid]

    else:
        user_queries = []

    #  collect queries posted by user's class members
    #  and queries posted by those outside the user's classes

    myclasses = db((db.class_membership.name == userid) &
                   (db.class_membership.class_section == db.classes.id)
                   ).iterselect(db.classes.id,
                                db.classes.institution,
                                db.classes.academic_year,
                                db.classes.course_section, orderby=~db.classes.start_date
                                )
    myclasses_queries = []
    external_queries = copy(queries_recs)
    member_queries = copy(queries_recs)
    for myclass in myclasses:
        members = list(set([m.name for m in
                            db(db.class_membership.class_section ==
                               myclass.id).iterselect()
                            if m.name != userid]
                            ))

        member_queries = list(filter(lambda x: x['auth_user']['id'] in members,
                                     member_queries))
        external_queries = list(filter(lambda x: x['auth_user']['id']
                                       not in members + [userid], external_queries))
        if member_queries:
            myclasses_queries.append({'id': myclass.id,
                                      'institution': myclass.institution,
                                      'year': myclass.academic_year,
                                      'section': myclass.course_section,
                                      'queries': member_queries}
                                    )

    # collect queries posted by the user's students

    mycourses_queries = []
    if auth.has_membership('instructors') or \
            auth.has_membership('administrators'):
        mycourses = db(db.classes.instructor == userid
                       ).select(orderby=~db.classes.start_date)
        # print('found {} courses'.format(len(mycourses)))
        for course in mycourses:
            students = [s['name'] for s in
                        db(db.class_membership.class_section == course.id
                           ).select(db.class_membership.name).as_list()]
            # print('found {} students'.format(len(students)))
            # print(students)
            student_queries = copy(queries_recs)
            student_queries = [s for s in student_queries
                               if s['auth_user']['id'] in students]
            # print([s['auth_user']['id'] for s in student_queries])
            # print('found {} student queries'.format(len(student_queries)))
            mycourses_queries.append({'id': course.id,
                                      'institution': course.institution,
                                      'year': course.academic_year,
                                      'section': course.course_section,
                                      'queries': student_queries})

    #  collect queries posted by other users

    if not auth.has_membership('administrators'):
        if auth.has_membership('instructors'):
            external_queries = list(filter(lambda x: (
                x['bugs']['public'] is True)
                or _is_my_student(auth.user_id, x['auth_user']['id']),
                external_queries))
        else:
            external_queries = list(filter(
                lambda x: x['bugs']['public'] is True,
                external_queries))

    return {'user_queries': user_queries,
            'class_queries': myclasses_queries,
            'course_queries': mycourses_queries,
            'other_queries': external_queries,
            'page_start': offset_start,
            'page_end': offset_end
            }


def get_queries():
    """
    API method to return queries for the selected step.
    """
    queries = _fetch_queries(request.vars['step_id'],
                             request.vars['user_id'],
                             nonstep=request.vars['nonstep'],
                             unanswered=request.vars['unanswered'],
                             pagesize=request.vars['pagesize'],
                             page=request.vars['page'],
                             orderby=request.vars['orderby']
                             )
    return json_serializer(queries)


def add_query_post():
    """
    API method to add a post in an existing query discussion.

    Expected request variables:
    query_id (int) *required
    post_text (str) *required
    public (bool) *required
    """
    vbs = False

    uid = request.vars['user_id']

    if auth.is_logged_in():
        if vbs: print('api::add_query_post: vars are', request.vars)

        data = {k: v for k, v in request.vars.items()
                    if k in ['post_body', 'public']
                    }

        data['poster_role'] = []
        if auth.has_membership('administrators'):
            data['poster_role'].append('administrators')
        if auth.has_membership('instructors'):
            data['poster_role'].append('instructors')

        post_result = Bug.record_bug_post(
            uid=uid,
            bug_id=request.vars['query_id'],
            **data
            )
        user_rec = db(db.auth_user.id==post_result['new_post']['poster']
                      ).select(db.auth_user.id,
                               db.auth_user.first_name,
                               db.auth_user.last_name
                               ).first().as_dict()
        full_rec = {'auth_user': user_rec,
                    'bug_posts': post_result['new_post'],
                    'comments': []}
        return json_serializer({'post_list': post_result['bug_post_list'],
                     'new_post': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def update_query_post():
    """
    API method to update a post in an existing query discussion.

    Expects the following required request parameters:
    user_id (int)
    query_id (int)
    post_id (int)
    post_text (str)
    public (bool)
    deleted (bool)
    hidden (bool)
    """
    vbs = False

    uid = request.vars['user_id']

    if (auth.is_logged_in() and
        (auth.user_id == uid
         or auth.has_membership('administrators')
         or auth.has_membership('instructors')
         and _is_my_student(auth.user_id, auth.user_id, uid)
         )
    ):
        if vbs: print('api::update_query_post: vars are', request.vars)
        new_data = {k: v for k, v in request.vars.items()
                    if k in ['post_body', 'public', 'deleted', 'hidden',
                                'pinned', 'popularity', 'helpfulness']}
        result = Bug.record_bug_post(
            uid=uid,
            bug_id=request.vars['query_id'],
            post_id=request.vars['post_id'],
            **new_data
            )

        user_rec = db(db.auth_user.id==result['new_post']['poster']
                    ).select(db.auth_user.id,
                             db.auth_user.first_name,
                             db.auth_user.last_name
                             ).first().as_dict()
        mycomments = []
        if result['new_post']['comments']:
            mycomments = db(
                (db.bug_post_comments.id.belongs(result['new_post']['comments'])) &
                (db.bug_post_comments.commenter==db.auth_user.id) &
                ((db.bug_post_comments.deleted == False) |
                (db.bug_post_comments.deleted == None))
                ).select(orderby=db.bug_post_comments.thread_index
                        ).as_list()
        full_rec = {'auth_user': user_rec,
                    'bug_posts': result['new_post'],
                    'comments': mycomments}

        return json_serializer({'post_list': result['bug_post_list'],
                     'new_post': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def add_post_comment():
    """
    """
    vbs = False

    uid = request.vars['user_id']

    if auth.is_logged_in():
        if vbs: print('api::add_post_comment: vars are', request.vars)

        data = {k: v for k, v in request.vars.items()
                if k in ['comment_body', 'public']
                }

        data['commenter_role'] = []
        if auth.has_membership('administrators'):
            data['commenter_role'].append('administrators')
        if auth.has_membership('instructors'):
            data['commenter_role'].append('instructors')

        result = Bug.record_post_comment(
            uid=uid,
            post_id=request.vars['post_id'],
            **data
            )
        user_rec = db(db.auth_user.id==result['new_comment']['commenter']
                      ).select(db.auth_user.id,
                               db.auth_user.first_name,
                               db.auth_user.last_name
                               ).first().as_dict()
        full_rec = {'auth_user': user_rec,
                    'bug_post_comments': result['new_comment']}
        return json_serializer({'comment_list': result['post_comment_list'],
                     'new_comment': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def update_post_comment():
    """
    API method to update a post comment in an existing query discussion.

    Expects the following request parameters:
    user_id (int)* required
    comment_id (int)* required
    post_id (int)* required
    comment_body (str)
    public (bool)
    deleted (bool)
    hidden (bool)
    pinned (bool)
    helpfulness (double)
    popularity (double)
    """
    vbs = False

    uid = request.vars['user_id']

    if (auth.is_logged_in() and
        (auth.user_id == uid
         or auth.has_membership('administrators')
         or auth.has_membership('instructors')
         and _is_my_student(auth.user_id, auth.user_id, uid)
         )
    ):
        if vbs: print('api::update_post_comment: vars are', request.vars)
        new_data = {k: v for k, v in request.vars.items()
                    if k in ['comment_body', 'public', 'deleted', 'hidden',
                             'pinned', 'popularity', 'helpfulness']}
        result = Bug.record_post_comment(
            uid=uid,
            post_id=request.vars['post_id'],
            comment_id=request.vars['comment_id'],
            **new_data
            )

        user_rec = db(db.auth_user.id==result['new_comment']['commenter']
                      ).select(db.auth_user.id,
                               db.auth_user.first_name,
                               db.auth_user.last_name
                               ).first().as_dict()
        full_rec = {'auth_user': user_rec,
                    'bug_post_comments': result['new_comment'],
                    }

        return json_serializer({'comment_list': result['post_comment_list'],
                     'new_comment': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def log_new_query():
    """
    API method to log a new user query.

    Expected request variables:
    user_id (int)
    step_id (int)
    path_id (int)
    loc_name (str)
    answer (str)
    log_id (int)
    score (double)
    user_comment (str)
    public (bool)

    Returns a json object containing the user's updated queries for the current step (if any) or for the app in general.
    """
    vbs = False
    uid = request.vars['user_id']
    auth = current.auth

    if auth.is_logged_in():
        if vbs: print('creating::submit_bug: vars are', request.vars)
        b = Bug(step_id=request.vars['step_id'],
                path_id=request.vars['path_id'],
                loc_id=db(db.locations.loc_alias == request.vars['loc_name']
                        ).select().first().id
                )
        if vbs: print('creating::submit_bug: created bug object successfully')
        logged = b.log_new(request.vars['answer'],
                           request.vars['log_id'],
                           request.vars['score'],
                           request.vars['user_comment'],
                           request.vars['public'])
        if vbs: print('creating::submit_bug: logged bug - response is', logged)

        myqueries = db((db.bugs.step == request.vars['step_id']) &
                       (db.bugs.user_name == db.auth_user.id) &
                       (db.bugs.user_name == uid) &
                       ((db.bugs.deleted == False) |
                        (db.bugs.deleted == None))
                       ).iterselect(db.bugs.id,
                                    db.bugs.step,
                                    db.bugs.in_path,
                                    db.bugs.prompt,
                                    db.bugs.step_options,
                                    db.bugs.user_response,
                                    db.bugs.score,
                                    db.bugs.adjusted_score,
                                    db.bugs.log_id,
                                    db.bugs.user_comment,
                                    db.bugs.date_submitted,
                                    db.bugs.bug_status,
                                    db.bugs.admin_comment,
                                    # db.bugs.hidden,
                                    db.bugs.deleted,
                                    db.bugs.pinned,
                                    db.bugs.flagged,
                                    db.bugs.public,
                                    db.bugs.posts,
                                    db.auth_user.id,
                                    db.auth_user.first_name,
                                    db.auth_user.last_name
                                    ).as_list()
        myqueries = _add_posts_to_queries(myqueries)
        #  confirm that the newly logged query is in the updated list
        # assert [q for q in myqueries if q['bugs']['id'] == logged]

        return json_serializer(myqueries)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def update_query():
    """
    Api method to update one bug record.

    Expects the following required request parameters:
    query_id (int)
    public (bool)
    deleted (bool)
    hidden (bool)

    A value of None for a parameter indicates that no update is requested. A value of False is a negative boolean value to be updated.
    ...
    """
    vbs = True

    uid = request.vars['user_id']

    if (auth.is_logged_in() and
        (auth.user_id == uid
         or auth.has_membership('administrators')
         or (auth.has_membership('instructors')
             and _is_my_student(auth.user_id, uid))
         )
    ):
        if vbs: print('api::update_query_post: vars are', request.vars)
        new_data = {k: v for k, v in request.vars.items()
                    if k in ['user_comment', 'public', 'deleted',
                             'pinned', 'popularity', 'helpfulness',
                             'bug_status']
                    and v is not None}
        if request.vars['score'] is not None:
            new_data['adjusted_score'] = copy(request.vars['score'])
        if vbs: print('submitting===================')
        if vbs: pprint(new_data)

        result = Bug.update_bug(request.vars["query_id"], new_data)
        if vbs: print('result:')
        if vbs: pprint(result['score'])
        if vbs: pprint(result['adjusted_score'])

        if (int(result['bug_status']) in [1, 2, 6] and
                request.vars['score'] != None and
                not (abs(result['score'] - 1) <= 0.999999999)):
            if vbs: print('undoing bug++++++')
            undone = trigger_bug_undo(**{k: v for k, v in result.items()
                                        if k in ['step',
                                                'in_path',
                                                'map_location',
                                                'id',
                                                'log_id',
                                                'score',
                                                'adjusted_score',
                                                'bug_status',
                                                'user_name',
                                                'admin_comment',
                                                'user_comment',
                                                'user_response'
                                                ]}
                                    )
            if vbs: pprint(undone)
        else:
            if vbs: print('not undoing anything++++++')

        user_rec = db(db.auth_user.id==db.bugs(result['id']).user_name
                    ).select(db.auth_user.id,
                             db.auth_user.first_name,
                             db.auth_user.last_name
                             ).first().as_dict()

        full_rec = {'auth_user': user_rec,
                    'bugs': result,
                    }
        full_rec = _add_posts_to_queries([full_rec])[0]
        return json_serializer(full_rec)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def get_vocabulary():
    """
    Api method to return the full vocabulary list.

    Expects an optional request variable "vocab_scope_selector"

    Returns a dictionary with the following keys:

    total_count :: int :: total_count
    mylemmas :: list :: each item represents a vocabulary entry, with joined
                        db data from "lemmas" and "tags" tables
    mylevel :: int :: the maximum badge set currently reached by user if
                      logged in
    """
    auth = current.auth

    mynorm = GreekNormalizer()
    mylemmas = []
    for l in db(db.lemmas.first_tag == db.tags.id
                ).iterselect(orderby=db.tags.tag_position):

        myrow = {'id': l['lemmas']['id'],
                 'accented_lemma': l['lemmas']['lemma'],
                 'normalized_lemma': mynorm.normalize(l['lemmas']['lemma']),
                 'part_of_speech': l['lemmas']['part_of_speech'],
                 'glosses': l['lemmas']['glosses'],
                 'times_in_nt': l['lemmas']['times_in_nt'],
                 'set_introduced': l['tags']['tag_position'],
                 'videos': [(t.id, t.title, t.video_url) for t in
                            db(db.lessons.lesson_tags.contains(l['tags']['id'])
                               ).select()],
                 'thematic_pattern': l['lemmas']['thematic_pattern'],
                 'real_stem': l['lemmas']['real_stem'],
                 'genitive_singular': l['lemmas']['genitive_singular'],
                 'future': l['lemmas']['future'],
                 'aorist_active': l['lemmas']['aorist_active'],
                 'perfect_active': l['lemmas']['perfect_active'],
                 'aorist_passive': l['lemmas']['aorist_passive'],
                 'perfect_passive': l['lemmas']['perfect_passive'],
                 'other_irregular': l['lemmas']['other_irregular'],
                 }
        mylemmas.append(myrow)

    return json_serializer({'total_count': len(mylemmas),
                 'mylemmas': mylemmas})


def get_lessons():
    """
    Api method to fetch information on the video lessons and associated pdfs.

    Doesn't expect any parameters or arguments, and always returns the same
    data unless the database information has changed.

    """
    lessons = db(db.lessons.active == True
                 ).select(orderby=db.lessons.lesson_position
                          ).as_list()
    for l in lessons:
        mybadges = db(db.badges.tag.belongs(l['lesson_tags'])).select()
        l['badges'] = mybadges.as_list()

    return json_serializer(lessons)


def set_review_mode():
    """
    Api method to set the user's review mode.

    Expects one argument: "review_set"
    """
    session = current.session
    try:
        myset = int(request.vars['review_set'])
    except (ValueError, TypeError):  # if passed a non-numeric value
        myset = None
    session.set_review = myset

    return json_serializer({'review_set': session.set_review})


def get_profile_info():
    """
    Api method to fetch a user's performance record.

    One optional request parameter "user" expects an integer identifying the
    user whose information is requested. If this parameter is not provided, the
    request defaults to the logged in user.

    Returns a json object with the following keys:
            the_name (str):             User's name from auth.user as lastname,
                                            firstname
            user_id(int):               The requested user's id.
            tz(str??):                  User's time zone from auth.user
                                            (extended in db.py)
            email(str):                 User's email
            starting_set(int):          badge set at which the user began
                                            his/her current course section
            end_date(str??):            ending date for user's current course
                                            section
            cal(html helper obj):       html calendar with user path stats
                                            (from Stats.monthcal)
            max_set(int):               Furthest badge set reached to date by
                                            user (from Stats.max)
            badge_levels(dict):         Dictionary with badge levels (int) as
                                            keys and a list of badge names (or
                                            tag: int) as each value.
            badge_table_data(list):     A list of dictionaries with info on
                                            user badge progress (from
                                            Stats.active_tags)
            badge_set_milestones(list): List of 'upgrades' of the highest badge
                                            set and their dates
            answer_counts(list):        List of counts of right and wrong
                                            answers for each active day
            chart1_data(dict):          dictionary of data to build stats chart
                                            in view (from get_chart1_data)
            reviewing_set():            session.set_review,
            badge_set_dict():           badge_set_dict,
            class_info:                 dict of course information if user is
                                            currently enrolled in a course
    """
    debug = False
    db = current.db
    auth = current.auth
    session = current.session
    response = current.response

    mystudents = db((db.classes.instructor == auth.user_id) &
                    (db.classes.id == db.class_membership.class_section)
                    ).select(db.class_membership.name).as_list()
    try:
        assert auth.is_logged_in();
        now = datetime.datetime.utcnow()
        # Allow passing explicit user but default to current user
        if 'userId' in request.vars.keys():
            sid = request.vars['userId']
            # only allow viewing if admin or student's instructor
            if (auth.user_id == sid
                or auth.has_membership('administrators')
                or (auth.has_membership('instructors') and
                    _is_my_student(auth.user_id, sid))):
                user = db.auth_user[sid]
            else:
                response.status = 401
                return json_serializer({'status': 'unauthorized',
                             'reason': 'Insufficient privileges'})
        else:
            user = db.auth_user[auth.user_id]
        # Return proper response code if no user with requested id
        if not user:
            response.status = 404
            return json_serializer({'status': 'Not found',
                         'reason': 'No matching record found'})

        stats = Stats(user.id)

        # get user's current course
        myc = _fetch_current_coursedata(user.id, datetime.datetime.utcnow())
        print('myc=============')
        print(myc)
        if myc['class_info']:
            starting_set = myc['class_info']['starting_set']
        # FIXME: UserProvider should be updated here with class info if new

        # tab1

        name = stats.get_name()
        tz = user.time_zone
        email = user.email
        max_set = stats.get_max()
        badge_levels = stats.get_badge_levels()
        badge_table_data = stats.active_tags()  # FIXME: 29Mi of memory use

        # tab2
        mycal = stats.monthcal()
        # badges_tested_over_time = stats.badges_tested_over_time(badge_table_data)
        # sets_tested_over_time = stats.sets_tested_over_time(badge_table_data)
        # steps_most_wrong = stats.steps_most_wrong(badge_table_data)

        # tab5
        mydata = get_chart1_data(user_id=user.id)
        chart1_data = mydata['chart1_data']  # FIXME: 3Mi of memory use
        badge_set_milestones = mydata['badge_set_milestones']
        answer_counts = mydata['answer_counts']
        badge_set_dict = {}
        set_list_rows = db().select(db.tags.tag_position, distinct=True)
        set_list = sorted([row.tag_position for row in set_list_rows
                        if row.tag_position < 90])
        all_tags = db((db.tags.id > 0) &
                    (db.badges.tag == db.tags.id)
                    ).select()
        for myset in set_list:
            set_tags = all_tags.find(lambda r: r.tags.tag_position == myset)
            set_tags_info = [{'tag': r.tags.id,
                              'badge_title': r.badges.badge_name}
                             for r in set_tags]
            badge_set_dict[myset] = set_tags_info
    except Exception:
        print(format_exc(5))
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})

    return json_serializer({'the_name': name,
            'user_id': user.id,
            'tz': tz,
            'email': email,
            'paths_per_day': myc['daily_quota'] if myc else None,
            'days_per_week': myc['weekly_quota'] if myc else None,
            'starting_set': myc['class_info']['starting_set']
                if myc['class_info'] else None,
            'cal': mycal,
            'max_set': max_set,
            'badge_levels': badge_levels,
            'badge_table_data': badge_table_data,
            'badge_set_milestones': badge_set_milestones,
            'answer_counts': answer_counts,
            'chart1_data': chart1_data,
            'reviewing_set': session.set_review,
            'badge_set_dict': badge_set_dict,
            'class_info': myc['class_info'] if myc['class_info'] else None
            },
            default=my_custom_json)


def get_calendar_month():
    """
    api method to fetch user attempt data for one calendar month

    Expects the request variables "user_id", "year", "month"
    - month is 0-based integer and year is a 4-digit year

    Returns a json object with the keys
    ::year
    ::month
    ::data

    """
    stats = Stats(request.vars.user_id)
    calendar = stats.monthcal(year=request.vars.year,
                              month=request.vars.month)
    return json_serializer(calendar, default=my_custom_json)


def update_course_membership_data():
    pass


def update_course_data():
    """
    Update a db record in the "classes" table.

    Private api method to handle calls from the react front-end. This method does not handle data on student membership in a course. That information must be updated separately with the update_course_membership_data method.

    Expects URL variables:
        course_id (int)
        course_data (dict)

    The course_data dictionary can have any of the following keys:

                institution (str)
                academic_year (int)
                term (str)
                course_section (str)
                instructor (int [reference auth_user])
                start_date (str [datetime])
                end_date (str [datetime])
                paths_per_day (int)
                days_per_week (int)
                a_target (int)
                a_cap (int)
                b_target (int)
                b_cap (int)
                c_target (int)
                c_cap (int)
                d_target (int)
                d_cap (int)
                f_target (int)

    """

    mydata = request.vars.course_data
    mydata['modified_on'] = datetime.datetime.utcnow
    course_id = request.vars.course_id

    try:
        # print('updating course', request.vars.course_id)
        course_rec = db.classes(request.vars.course_id)
        # print('old data:')
        # print(course_rec)
    except AttributeError:
        print(format_exc(5))
        response = current.response
        response.status = 404
        return json_serializer({'status': 'No such record'})

    try:
        assert auth.is_logged_in()
    except AssertionError:
        print(format_exc(5))
        response = current.response
        response.status = 401
        return json_serializer({'status': 'Not logged in'})

    try:
        assert (auth.has_membership('administrators') or
                (auth.has_membership('instructors') and
                course_rec['instructor'] == auth.user_id)
                )
    except AssertionError:
        print(format_exc(5))
        response = current.response
        response.status = 401
        return json_serializer({'status': 'Insufficient privileges'})

    myresult = db(db.classes.id == course_id).update(**mydata)
    assert myresult == 1

    return json_serializer({"update_count": myresult}, default=my_custom_json)


def get_course_data():
    """
    Return the data on a single course and its students.

    Private api method to handle calls from the react front-end.

    Expects url variables:
        course_id (int)

    Returns:
        JSON object with the following keys:
            institution
            academic_year
            term
            course_section
            instructor
            start_date
            end_date
            paths_per_day
            days_per_week
            a_target
            a_cap
            b_target
            b_cap
            c_target
            c_cap
            d_target
            d_cap
            f_target
            members
        members is an array of objects which each have the following keys:
            first_name
            last_name
            custom_start
            starting_set
            custom_end
            ending_set
            custom_a_cap
            custom_b_cap
            custom_c_cap
            custom_d_cap
            final_grade
    """
    auth = current.auth
    session = current.session
    db = current.db
    try:
        print('getting course', request.vars.course_id)
        course_rec = db.classes(request.vars.course_id).as_dict()
    except AttributeError:
        print(format_exc(5))
        response = current.response
        response.status = 404
        return json_serializer({'status': 'No such record'})

    try:
        assert auth.is_logged_in()
    except AssertionError:
        print(format_exc(5))
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})

    try:
        assert (auth.has_membership('administrators') or
                (auth.has_membership('instructors') and
                course_rec['instructor'] == auth.user_id)
                )
    except AssertionError:
        print(format_exc(5))
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Insufficient privileges'})


    mycourse = {k: v for k, v in course_rec.items() if k in [
                'id',
                'institution', 'academic_year', 'term',
                'course_section',
                'start_date', 'end_date',
                'paths_per_day', 'days_per_week',
                'a_target', 'a_cap',
                'b_target', 'b_cap',
                'c_target', 'c_cap',
                'd_target', 'd_cap',
                'f_target'
                ]}
    members = [{'first_name': m.auth_user.first_name,
                'last_name': m.auth_user.last_name,
                'custom_start': m.class_membership.custom_start,
                'starting_set': m.class_membership.starting_set,
                'custom_end': m.class_membership.custom_end,
                'ending_set': m.class_membership.ending_set,
                'custom_a_cap': m.class_membership.custom_a_cap,
                'custom_b_cap': m.class_membership.custom_b_cap,
                'custom_c_cap': m.class_membership.custom_c_cap,
                'custom_d_cap': m.class_membership.custom_d_cap,
                'final_grade': m.class_membership.final_grade}
        for m in
        db((db.class_membership.class_section==mycourse['id']) &
           (db.class_membership.name==db.auth_user.id)
           ).iterselect()
    ]
    mycourse['members'] = members

    return json_serializer(mycourse, default=my_custom_json)


def _is_my_student(user, student):
    """
    Return a boolean indicating if student is in a class taught by user
    """
    mystudents = db((db.classes.instructor == user) &
                    (db.classes.id == db.class_membership.class_section)
                    ).select(db.class_membership.name).as_list()
    mystudent_ids = list(set(s['name'] for s in mystudents))
    return True if student in mystudent_ids else False
