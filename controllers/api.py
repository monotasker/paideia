#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from copy import copy
from gluon.serializers import json
from pprint import pprint
from paideia import Walk

if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request


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
    pprint(request.vars)
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
    pprint(request.vars)
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
    return json({'status': auth.logged_in()})