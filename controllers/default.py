# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

import datetime

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    return dict(message=T('Hello World'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    try:
        attempts = db(db.attempt_log.name == auth.user_id).select()
        s=db.attempt_log.score.sum()
        row = db(db.attempt_log.name == auth.user_id).select(s).first()
        answer = row[s]
        score_avg = answer/len(attempts)*100
    except:
        score_avg = "Can't calculate average"

    # get statistics for different classes of questions
    the_records = db(db.question_records.name == auth.user_id).select()
    total_len = float(len(the_records))

    try:
        cat1 = db((db.question_records.name == auth.user_id) & (db.question_records.category == 1)).select()
        total_cat1 = len(cat1)
        percent_cat1 = (total_cat1/total_len)*100
    except:
        total_cat1 = "Can't calculate number"
    try:
        cat2 = db((db.question_records.name == auth.user_id) & (db.question_records.category == 2)).select()
        total_cat2 = len(cat2)
        percent_cat2 = (int(total_cat2)/total_len)*100
    except:
        total_cat2 = "Can't calculate number"
    try:
        cat3 = db((db.question_records.name == auth.user_id) & (db.question_records.category == 3)).select()
        total_cat3 = len(cat3)
        percent_cat3 = (total_cat3/total_len)*100
    except:
        total_cat3 = "Can't calculate number"
    try:
        cat4 = db((db.question_records.name == auth.user_id) & (db.question_records.category == 3)).select()
        total_cat4 = len(cat4)
        percent_cat4 = (total_cat4/total_len)*100
    except:
        total_cat4 = "Can't calculate number"

    return dict(form=auth(), score_avg=score_avg, total_len = total_len, total_cat1 = total_cat1, total_cat2 = total_cat2, total_cat3 = total_cat3, percent_cat1 = percent_cat1, percent_cat2 = percent_cat2, percent_cat3 = percent_cat3, total_cat4 = total_cat4, percent_cat4 = percent_cat4)


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id[
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

@auth.requires_membership(role='administrators')
def send_mail():
    addr = db(db.auth_user.id == session.the_student).select(db.auth_user.email)
    subj = session.mail_subject
    msg = session.mail_message

    if mail.send(to=addr, subject=subj, message=msg):
        response.flash('mail sent successfully')
    else:
        response.flash('There was a problem sending the mail.')

    return

@auth.requires_membership(role='administrators')
def bulk_cat_qs():
    records = db(db.question_records.id > 0).select()
    counter = 0
    for record in records:
        #figure out how the student is doing with this question
        last_right = record.last_right
        last_wrong = record.last_wrong
        now_date = datetime.date.today()
        right_dur = now_date-last_right
        wrong_dur = now_date-last_wrong
        rightWrong_dur = last_right - last_wrong
        #categorize this question based on student's performance
        if right_dur < wrong_dur:
            if (right_dur < rightWrong_dur) and (right_dur < datetime.timedelta(days=170)):
                if rightWrong_dur > datetime.timedelta(days=14):
                    cat = 4
                else:
                    cat = 3
            else:
                cat = 2
        else:
            cat = 1
        # update database with categorization
        db(db.question_records.id == record.id).update(category = cat)
        # count each record updated
        counter += 1
        session.debug = record.id

    message = "Success. I categorized ", counter, " records."

    return dict(message = message)
