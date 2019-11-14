#! /usr/bin/python3.6
# -*- coding: utf-8 -*-

from gluon.tools import service
if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request

auth.settings.allow_basic_login = True


@service.json
def get_login():

    return {"myword": "gotcha"}
