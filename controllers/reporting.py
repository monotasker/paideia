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
    the_user = db.auth_user[request.args[0]]
    the_name = the_user.last_name + ', ' + the_user.first_name
    try:
        attempts = db(db.attempt_log.name == request.args[0]).select()
        s=db.attempt_log.score.sum()
        row = db(db.attempt_log.name == request.args[0]).select(s).first()
        answer = row[s]
        score_avg = answer/len(attempts)*100
    except:
        score_avg = "Can't calculate average"

    # get statistics for different classes of questions
    the_records = db(db.question_records.name == request.args[0]).select()
    total_len = float(len(the_records))

    try:
        cat1 = db((db.question_records.name == request.args[0]) & (db.question_records.category == 1)).select()
        total_cat1 = len(cat1)
        percent_cat1 = (total_cat1/total_len)*100
    except:
        total_cat1 = "Can't calculate number"
    try:
        cat2 = db((db.question_records.name == request.args[0]) & (db.question_records.category == 2)).select()
        total_cat2 = len(cat2)
        percent_cat2 = (int(total_cat2)/total_len)*100
    except:
        total_cat2 = "Can't calculate number"
    try:
        cat3 = db((db.question_records.name == request.args[0]) & (db.question_records.category == 3)).select()
        total_cat3 = len(cat3)
        percent_cat3 = (total_cat3/total_len)*100
    except:
        total_cat3 = "Can't calculate number"
    try:
        cat4 = db((db.question_records.name == request.args[0]) & (db.question_records.category == 3)).select()
        total_cat4 = len(cat4)
        percent_cat4 = (total_cat4/total_len)*100
    except:
        total_cat4 = "Can't calculate number"

    form = SQLFORM.grid(db.attempt_log.name == request.args[0])

    return dict(form=form, score_avg=score_avg, the_name = the_name, total_len = total_len, total_cat1 = total_cat1, total_cat2 = total_cat2, total_cat3 = total_cat3, percent_cat1 = percent_cat1, percent_cat2 = percent_cat2, percent_cat3 = percent_cat3, total_cat4 = total_cat4, percent_cat4 = percent_cat4)
