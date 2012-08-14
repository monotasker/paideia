# coding: utf8

if 0:
    from gluon import current, Auth, SQLFORM
    from gluon.dal import DAL
    auth = Auth()
    db = DAL()
    request = current.request

from paideia_stats import paideia_stats, paideia_timestats, paideia_weeklycount


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
            print s.id
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
    # get student's user id and name
    the_user = db.auth_user[request.args[0]]
    the_name = the_user.last_name + ', ' + the_user.first_name

    s = Stats(request.args[0])
    avg = s.average()
    cats = s.categories()
    cal = s.monthcal()

    b = Bug()
    blist = b.bugresponses(the_user)

    return dict(the_name=the_name,
            score_avg=avg,
            categories=cats,
            calendar=cal
            blist=blist)
