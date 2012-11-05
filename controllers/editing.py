# coding: utf8

if 0:
    from gluon import current, A, crud, URL, H3
    auth = current.auth
    db = current.db
    request = current.request
from paideia_bugs import Bug
import datetime

@auth.requires_membership(role='administrators')
def listing():
    return dict()

@auth.requires_membership(role='administrators')
def undo_bug():
    '''
    Controller to receive ajax signal and trigger the Bug class method to undo
    the effects of a reported bug on the user's performance record.
    '''
    debug = True
    if debug: print 'calling controller edit.undo_bug'
    b = Bug(request.vars.step, request.vars.path, request.vars.location)
    u = b.undo(request.vars.user_name, request.vars.id, request.vars.log_id)

    return u
