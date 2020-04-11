#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from copy import copy
import datetime
from traceback import format_exc
from gluon.serializers import json
from pprint import pprint
from paideia import Walk
from paideia_utils import GreekNormalizer
from paideia_stats import Stats, get_set_at_date, get_term_bounds
from paideia_stats import get_current_class, get_chart1_data, my_custom_json
from paideia_bugs import Bug, trigger_bug_undo

if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request
    db = current.db


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
        return json(resp)
    else:
        response = current.response
        response.status = 401
        return json({'status': 'unauthorized'})


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
        return json(resp)
    else:
        response = current.response
        response.status = 401
        return json({'status': 'unauthorized'})


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
        try:
            myuser = {k:v for k, v in mylogin.items() if k in
                    ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
            memberships = db((db.auth_membership.user_id == myuser['id']) &
                             (db.auth_membership.group_id == db.auth_group.id)
                             ).select(db.auth_group.role).as_list()
            myuser['roles'] = [m['role'] for m in memberships]

            myuser['current_badge_set'] = db(
                db.tag_progress.name == myuser['id']
                ).select().first().latest_new
            myuser['review_set'] = session.set_review \
                if 'set_review' in session.keys() else None

        except AttributeError:  # if login response was False and has no items
            myuser = {'id': None}
        return json(myuser)
    except Exception as e:
        return json({'error': e})


def get_userdata():
    """
    API method to get the user data for the currently logged in user.
    """
    auth = current.auth
    session = current.session
    try:
        myuser = db.auth_user(auth.user_id).as_dict()
        try:
            myuser = {k:v for k, v in myuser.items() if k in
                    ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
            memberships = db((db.auth_membership.user_id == myuser['id']) &
                             (db.auth_membership.group_id == db.auth_group.id)
                             ).select(db.auth_group.role).as_list()
            myuser['roles'] = [m['role'] for m in memberships]

            myuser['current_badge_set'] = db(
                db.tag_progress.name == myuser['id']
                ).select().first().latest_new
            myuser['review_set'] = session.set_review \
                if 'set_review' in session.keys() else None

        except AttributeError:
            myuser = {'id': None}
        return json(myuser)
    except Exception as e:
        return json({'error': e})


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
        print("about to log out")
        mylogout = auth.logout_bare()
        print ("did logout")
        myuser = {k:None for k in ['email', 'first_name', 'last_name',
                                   'hide_read_queries', 'id', 'time_zone']}
        return json(myuser)
    except Exception as e:
        print(e)
        return json({'error': e})


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
    return json(my_login)


def get_step_queries():
    """
    API method to return queries for the selected step.
    """
    print(request.vars)
    stepid = request.vars['step_id']
    queries = db((db.bugs.step == stepid) &
                 (db.bugs.user_name == db.auth_user.id)
                 ).iterselect(db.bugs.id,
                              db.bugs.step,
                              db.bugs.in_path,
                              db.bugs.step_options,
                              db.bugs.user_response,
                              db.bugs.score,
                              db.bugs.adjusted_score,
                              db.bugs.log_id,
                              db.bugs.user_comment,
                              db.bugs.date_submitted,
                              db.bugs.bug_status,
                              db.bugs.admin_comment,
                              db.bugs.hidden,
                              db.bugs.deleted,
                              db.auth_user.id,
                              db.auth_user.first_name,
                              db.auth_user.last_name
                              ).as_list()
                              #  TODO: db.bugs.public,
                              #  TODO: db.bugs.popularity,
                              #  TODO: db.bugs.pinned,
                              #  TODO: db.bugs.helpfulness,
                              #  TODO: db.bug_posts.user_id,
                              #  TODO: db.bug_posts.user_role,
                              #  TODO: db.bug_posts.post_body
                              #  TODO: db.bug_posts.response_to
                              #  TODO: db.bug_posts.posted_date
                              #  TODO: db.bug_posts.updated_date
                              #  TODO: db.bug_posts.public
                              #  TODO: db.bug_posts.popularity
                              #  TODO: db.bug_posts.helpfulness
                              #  TODO: db.bug_posts.pinned
    myuser = request.vars['user_id']
    user_queries = [q for q in queries if q['auth_user']['id'] == myuser]

    myclasses = db((db.class_membership.name == myuser) &
                   (db.class_membership.class_section == db.classes.id)
                   ).iterselect(db.classes.id,
                                db.classes.institution,
                                db.classes.academic_year,
                                db.classes.course_section, orderby=~db.classes.start_date
                                )

    myclasses_queries = []
    external_queries = copy(queries)
    for myclass in myclasses:
        members = list(set([m.name for m in
                            db(db.class_membership.class_section ==
                               myclass.id).iterselect()]
                            ))

        member_queries = list(filter(lambda x: x['auth_user']['id'] in members,
                                     queries))
        external_queries = list(filter(lambda x: x['auth_user']['id']
                                       not in members, external_queries))
        mylabel = "{}, {}, {}".format(myclass.institution,
                                      myclass.academic_year,
                                      myclass.course_section)

        if member_queries:
            myclasses_queries.append({'institution': myclass.institution,
                                      'year': myclass.academic_year,
                                      'section': myclass.course_section,
                                      'queries': member_queries}
                                    )

    return json({'user_queries': user_queries,
                 'class_queries': myclasses_queries,
                 'other_queries': external_queries
                 })


def log_new_query():
    """
    API method to log a new user query.

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
                        request.vars['user_comment'])
        if vbs: print('creating::submit_bug: logged bug - response is', logged)

        myqueries = db((db.bugs.step == request.vars['step_id']) &
                    (db.bugs.user_name == db.auth_user.id) &
                    (db.bugs.user_name == uid)
                    ).iterselect(db.bugs.id,
                                db.bugs.step,
                                db.bugs.in_path,
                                db.bugs.step_options,
                                db.bugs.user_response,
                                db.bugs.score,
                                db.bugs.adjusted_score,
                                db.bugs.log_id,
                                db.bugs.user_comment,
                                db.bugs.date_submitted,
                                db.bugs.bug_status,
                                db.bugs.admin_comment,
                                db.bugs.hidden,
                                db.bugs.deleted,
                                db.auth_user.id,
                                db.auth_user.first_name,
                                db.auth_user.last_name
                                ).as_list()
        #  confirm that the newly logged query is in the updated list
        # assert [q for q in myqueries if q['bugs']['id'] == logged]

        return json(myqueries)
    else:
        response = current.response
        response.status = 401
        return json({'status': 'unauthorized'})


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

    return json({'total_count': len(mylemmas),
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

    return json(lessons)


def set_review_mode():
    """
    Api method to set the user's review mode.

    Expects one argument: "review_set"
    """
    try:
        myset = int(request.vars['review_set'])
    except (ValueError, TypeError):  # if passed a non-numeric value
        myset = None
    session.set_review = myset

    return json({'review_set': session.set_review})


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
            badge_set_dict():           badge_set_dict
    """
    debug = False
    db = current.db
    auth = current.auth
    session = current.session

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
                raise PermissionError("Current user not authorized to view the "
                                      "requested student's record")
        else:
            user = db.auth_user[auth.user_id]

        stats = Stats(user.id)

        # get user's current course
        myc = get_current_class(user.id, datetime.datetime.utcnow())

        # tab1

        name = stats.get_name()
        tz = user.time_zone
        email = user.email
        max_set = stats.get_max()
        badge_levels = stats.get_badge_levels()
        badge_table_data = stats.active_tags()  # FIXME: 29Mi of memory use

        start_date, fmt_start, end_date, fmt_end = None, None, None, None
        if myc:
            start_date, fmt_start, end_date, fmt_end, \
                prevend, fmt_prevend = get_term_bounds(
                    myc.class_membership.as_dict(),
                    myc.classes.start_date,
                    myc.classes.end_date)
            try:
                starting_set = int(myc.class_membership.starting_set)
            except (ValueError, TypeError):
                starting_set = None
            if not starting_set:
                starting_set = get_set_at_date(user.id, start_date)
            goal = myc.classes.a_target

            if myc.class_membership.custom_a_cap:  # allow personal targets
                target_set = myc.class_membership.custom_a_cap
            else:  # default to class target/cap
                cap = myc.classes.a_cap
                target_set = starting_set + goal
                if cap and target_set > cap:
                    target_set = cap
        else:
            starting_set = None
            goal = None
            target_set = None

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
        return json({'status': 'unauthorized'})

    return json({'the_name': name,
            'user_id': user.id,
            'tz': tz,
            'email': email,
            'starting_set': starting_set,
            'target_set': target_set,
            'end_date': fmt_end,
            'cal': mycal,
            'max_set': max_set,
            'badge_levels': badge_levels,
            'badge_table_data': badge_table_data,
            'badge_set_milestones': badge_set_milestones,
            'answer_counts': answer_counts,
            'chart1_data': chart1_data,
            'reviewing_set': session.set_review,
            'badge_set_dict': badge_set_dict
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
    return json(calendar, default=my_custom_json)


def _is_my_student(user, student):
    """
    Return a boolean indicating if student is in a class taught by user
    """
    mystudents = db((db.classes.instructor == user) &
                    (db.classes.id == db.class_membership.class_section)
                    ).select(db.class_membership.name).as_list()
    mystudent_ids = list(set(s['name'] for s in mystudents))
    return True if student in mystudent_ids else False