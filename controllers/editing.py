# coding: utf8

if 0:
    from gluon import current
    auth = current.auth
    db = current.db
    request = current.request
from paideia_bugs import Bug

@auth.requires_membership(role='administrators')
def listing():
    return dict()

@auth.requires_membership(role='administrators')
def undo_bug():
    '''
    Controller to receive ajax signal and trigger the Bug class method to undo
    the effects of a reported bug on the user's performance record.
    '''
    b = Bug(request.vars.step, request.vars.in_path, request.vars.map_location)
    u = b.undo(request.vars.id, request.vars.log_id, float(request.vars.score),
               request.vars.bug_status, request.vars.user_name,
               request.vars.admin_comment)
    return u
