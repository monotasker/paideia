#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from gluon.serializers import json
from gluon.tools import Service
from pprint import pprint

if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request

def get_login():
    pprint(request)
    print(request.args)
    print(request.vars)
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


