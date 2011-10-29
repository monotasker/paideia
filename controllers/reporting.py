# coding: utf8

@auth.requires_membership(role='administrators')
def index():
    reports = dict(attempts='Attemps Log',)
    return dict(reports=reports)

@auth.requires_membership(role='administrators')
def attempts():
    form = SQLFORM.grid(db.attempt_log)
    return dict(form = form)

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

    return dict(the_name = the_name, score_avg=s.score_avg, total_len = t.total_len, total_cat1 = t.total_cat1, total_cat2 = t.total_cat2, total_cat3 = t.total_cat3, percent_cat1 = t.percent_cat1, percent_cat2 = t.percent_cat2, percent_cat3 = t.percent_cat3, total_cat4 = t.total_cat4, percent_cat4 = t.percent_cat4, dateset = w.dateset, htmlcal = w.htmlcal)
