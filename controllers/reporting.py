# coding: utf8

if 0:
    from gluon import current, Auth, SQLFORM
    from gluon.dal import DAL
    auth = Auth()
    db = DAL()
    request = current.request

from paideia_stats import Stats
from paideia_bugs import Bug


@auth.requires_membership(role='administrators')
def index():
    reports = dict(attempts='Attemps Log',)
    return dict(reports=reports)


@auth.requires_membership(role='administrators')
def paths_by_tag():
    tags = db(db.tags.id > 0).select()
    taglist = []
    for t in tags:
        steps = db(db.steps.tags.contains(str(t.id))).select()
        pathlist = []
        for s in steps:
            paths = db(db.paths.steps.contains(s.id)).select()
            pathlist += [p.id for p in paths]
        pathlist = list(set(pathlist))
        pathset = db(db.paths.id.belongs(pathlist)).select()
        tagdict = dict(id=t.id, name=t.tag, position=t.position,
                        pathset=pathset, count=len(pathlist))
        taglist.append(tagdict)

    taglist = sorted(taglist, key=lambda k: k['position'])

    return dict(taglist=taglist)


@auth.requires_membership(role='administrators')
def attempts():
    if len(request.args) > 0:
        form = SQLFORM.grid(db.attempt_log.name == request.args[0])
    else:
        form = SQLFORM.grid(db.attempt_log)
    return dict(form=form)


@auth.requires_membership(role='administrators')
def user():
    user = request.args[0]
    return {'id': user}


def calendar():
    '''
    Provides a calendar with user activity information for a given month/year.
    Intended to be used via an ajax component on the user's profile and the
    instructor's user reports.
    '''
    debug = False

    if debug: print '\n\nStarting controller exploring.calendar()'
    if debug: print 'request.args:', request.args
    if debug: print 'request.vars:', request.vars

    user_id = request.args[0]
    year = request.args[1]
    month = request.args[2]

    s = Stats(user_id)
    cal = s.monthcal(year, month)

    return {'cal': cal}


