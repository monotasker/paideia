#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from gluon.serializers import json
# from gluon.tools import Service
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
    """
    pprint(request.vars)
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = request.vars.new_user
        stepargs = {k: v for k, v in request.vars.items()
                    if k not in ['loc', 'new_user']}
        resp = Walk(new_user=new_user).start(myloc, **stepargs)
        return json(resp)
    else:
        response = current.response
        response.status = 401
        return json({'status': 'unauthorized'})


def get_response():
    """
    """

    return False


def get_login():
    """
    API method to log a user in with web2py's authentication system.
    
    Returns:
        JSON object with data on the user that was successfully logged in. If the login is unsuccessful, the JSON object carries just an 'id' value of None.
    """
    try:
        mylogin = auth.login_bare(request.vars['email'],
                                  request.vars['password'])
        try:
            myuser = {k:v for k, v in mylogin.items() if k in 
                    ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
        except AttributeError:  # if login response was False and has no items
            myuser = {'id': None}
        return json(myuser)
    except Exception as e:
        return json({'error': e})


def do_logout():
    """
    API method to log the current user out.
    
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