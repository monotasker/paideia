# coding: utf8
# try something like
@auth.requires_membership(role='administrators')
def index():
    reports = dict(attempts='Attemps Log',)
    return dict(reports=reports)

def attempts():
    form = SQLFORM.grid(db.attempt_log)
    return dict(form = form)

def user():
    the_user = db.auth_user[request.args[0]]
    the_name = the_user.last_name + ', ' + the_user.first_name
    try:
        attempts = db(db.attempt_log.name == request.args[0]).select()
        s=db.attempt_log.score.sum()
        row = db(db.attempt_log.name == request.args[0]).select(s).first()
        answer = row[s]
        score_avg = answer/len(attempts)
    except:
        score_avg = "Can't calculate average"
    form = SQLFORM.grid(db.attempt_log.name == request.args[0])
    return dict(form=form, score_avg=score_avg, the_name = the_name)
