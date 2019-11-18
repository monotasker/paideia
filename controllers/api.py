#! /usr/bin/python3.6
# -*- coding: utf-8 -*-
from gluon.serializers import json

if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request


def do_login():
    print(request.args)
    print(request.vars)
    mylogin = auth.login_bare(request.vars['email'], request.vars['password'])
    myuser = {k:v for k, v in mylogin.items() if k in 
              ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
    return json(myuser)


