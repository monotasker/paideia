#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from copy import copy
from gluon.serializers import json
from pprint import pprint
from paideia import Walk
from paideia_bugs import Bug
from paideia_utils import GreekNormalizer

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
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = request.vars.new_user
        stepargs = {'path': None,
                    'pre_bug_step_id': None,
                    'repeat': False,
                    'response_string': None,
                    'set_blocks': None,
                    'set_review': False}
        for k, v in request.vars.items():
            if k in stepargs.keys() \
                    and k not in ['loc', 'new_user', 'response_string']:
                stepargs[k] = v
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
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = False
        stepargs = {'response_string': request.vars.response_string,
                    'path': None,
                    'pre_bug_step_id': None,
                    'repeat': False,
                    'set_blocks': None,
                    'set_review': False}
        for k, v in request.vars.items():
            if k in stepargs.keys() \
                    and k not in ['loc', 'new_user', 'response_string']:
                stepargs[k] = v
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

        except AttributeError:  # if login response was False and has no items
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
    auth = current.auth
    try:
        mylogout = auth.logout_bare()
        myuser = {k:None for k in ['email', 'first_name', 'last_name',
                                   'hide_read_queries', 'id', 'time_zone']}
        return json(myuser)
    except Exception as e:
        return json({'error': e})


def check_login():
    """
    API method to return the current server login status.

    """
    auth = current.auth
    return json({'status': auth.is_logged_in()})


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
                 'videos': l['tags']['slides'],
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