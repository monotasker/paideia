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
    form = SQLFORM.grid(db.attempt_log)
    return dict(form=form)


@auth.requires_membership(role='administrators')
def user():
    # get student's user id and name
    the_user = db.auth_user[request.args[0]]
    the_name = the_user.last_name + ', ' + the_user.first_name
    # create instance of paideia_stats class to calculate student performance
    s = paideia_stats(request.args[0])
    t = paideia_timestats(request.args[0])
    w = paideia_weeklycount(request.args[0])
    # create dynamic grid to display list of all question attempts
    #form = SQLFORM.grid(db.attempt_log.name == request.args[0])
    #place form=auth() in returned values

    return dict(the_name=the_name, score_avg=s.score_avg,
        total_len=t.total_len, total_cat1=t.total_cat1,
        total_cat2=t.total_cat2, total_cat3=t.total_cat3,
        percent_cat1=t.percent_cat1, percent_cat2=t.percent_cat2,
        percent_cat3=t.percent_cat3, total_cat4=t.total_cat4,
        percent_cat4=t.percent_cat4, dateset=w.dateset,
        htmlcal=w.htmlcal)
