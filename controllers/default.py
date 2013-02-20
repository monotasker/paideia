# -*- coding: utf-8 -*-

from paideia_stats import Stats
from paideia_bugs import Bug
from gluon.tools import prettydate

if 0:
    from gluon import current
    from gluon.tools import Auth
    from gluon.dal import DAL
    db = DAL()
    auth = Auth()
    response, session = current.response, current.session
    T, service = current.T, current.service
    request = current.request


def index():
    """    """
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    """
    return {'form': auth()}

def info():
    """
    Return data reporting on a user's performance record.

    This controller is intended to serve the view profile.load as a modular
    page component, to be embedded in other views such as:
        default/user.html
        reporting/user.html
    The modular approach allows one controller/view pair to present the
    information at multiple places in the application, reducing maintenance
    and duplicate code.
    """
    # Allow either passing explicit user or defaulting to current user
    if 'id' in request.vars:
        user = db.auth_user[request.vars['id']]
    else:
        user = db.auth_user[auth.user_id]
    name = user.last_name + ', ' + user.first_name
    tz = user.time_zone
    email = user.email

    stats = Stats(user.id)
    active = stats.active_tags()
    cal = stats.monthcal()
    sl = stats.step_log()
    log = sl['loglist']
    duration = sl['duration']

    max_set = db(db.tag_progress.name ==
                  auth.user_id).select().first()
    if not max_set is None:
        max_set = max_set.latest_new
    else:
        max_set = 1

    b = Bug()
    blist = b.bugresponses(user.id)
    tag_progress = db((db.tag_progress.name == user.id)).select().first().as_dict()

    tag_records = db((db.tag_records.name == user.id) &
                        (db.tag_records.tag == db.tags.id)
                    ).select(orderby=db.tags.position)

    badge_dates = db(
                        (db.badges_begun.name == user.id) &
                        (db.badges_begun.tag == db.tags.id)
                    ).select(orderby=~db.tags.position)

    badgelist = []
    catlabels = ['started at beginner level',
                'promoted to apprentice level',
                'promoted to journeyman level',
                'promoted to master level']
    for bd in badge_dates:
        for c in ['cat1', 'cat2', 'cat3', 'cat4']:
            if bd.badges_begun[c]:
                tagbadge = db.badges(db.badges.tag==bd.tags.id)
                badgelist.append({'id': tagbadge.badge_name,
                                'description': tagbadge.description,
                                'level': catlabels[int(c[3:])-1],
                                'date': 'on {}'.format(bd.badges_begun[c].strftime('%b %e, %Y')),
                                'dt': bd.badges_begun[c]})
    badgelist = sorted(badgelist, key=lambda row: row['dt'], reverse=True)

    return {'form': auth(),
            'the_name': name,
            'tz': tz,
            'email': email,
            'cal': cal,
            'blist': blist,
            'active': active,
            'max_set': max_set,
            'tag_progress': tag_progress,
            'tag_records': tag_records,
            'log': log,
            'duration': duration,
            'badge_track': badgelist}

def oops():
    """A controller to handle rerouted requests that return error codes."""
    code = request.vars.code
    ticket = request.vars.ticket
    requested_uri = request.vars.requested_uri
    request_url = request.vars.request_url
    # Return the original HTTP error code
    response.status = code
    if code == 500:
        title = 'Paideia - Internal error reported'
        msg = HTML(BODY('Hello Ian,<br>I seem to have run into an error!',
                'Here is the ticket: '))
        link = A(ticket, _href=URL('admin', 'default', 'ticket', args=[ticket]),
                _target='_blank')
        msg[0].append(link)

        mail.send(mail.settings.sender, title, msg.xml())

    return {'code': code}

#def download():
    #"""
    #allows downloading of uploaded files
    #http://..../[app]/default/download/[filename]
    #"""
    #return response.download(request,db)


#def call():
    #"""
    #exposes services. for example:
    #http://..../[app]/default/call/jsonrpc
    #decorate with @services.jsonrpc the functions to expose
    #supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    #"""
    #return service()


#@auth.requires_signature()
#def data():
    #"""
    #http://..../[app]/default/data/tables
    #http://..../[app]/default/data/create/[table]
    #http://..../[app]/default/data/read/[table]/[id]
    #http://..../[app]/default/data/update/[table]/[id]
    #http://..../[app]/default/data/delete/[table]/[id[
    #http://..../[app]/default/data/select/[table]
    #http://..../[app]/default/data/search/[table]
    #but URLs bust be signed, i.e. linked with
      #A('table',_href=URL('data/tables',user_signature=True))
    #or with the signed load operator
      #LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    #"""
    #return dict(form=crud())

# TODO: does the mail function below make sense?
@auth.requires_membership(role='administrators')
def send_mail_to_user():
    addr = db(db.auth_user.id == session.the_student).select(db.auth_user.email)
    subj = session.mail_subject
    msg = session.mail_message

    if mail.send(to=addr, subject=subj, message=msg):
        response.flash('mail sent successfully')
    else:
        response.flash('There was a problem sending the mail.')

    return

# TODO: deprecated utility script
#@auth.requires_membership(role='administrators')
#def bulk_cat_qs():
    #records = db(db.question_records.id > 0).select()
    #counter = 0
    #for record in records:
        ##figure out how the student is doing with this question
        #last_right = record.last_right
        #last_wrong = record.last_wrong
        #now_date = datetime.date.today()
        #right_dur = now_date-last_right
        #wrong_dur = now_date-last_wrong
        #rightWrong_dur = last_right - last_wrong
        ##categorize this question based on student's performance
        #if right_dur < wrong_dur:
            #if (right_dur < rightWrong_dur) and (right_dur < datetime.timedelta(days=170)):
                #if right_dur > datetime.timedelta(days=14):
                    #cat = 4
                #else:
                    #cat = 3
            #else:
                #cat = 2
        #else:
            #cat = 1
        ## update database with categorization
        #db(db.question_records.id == record.id).update(category = cat)
        ## count each record updated
        #counter += 1
        #session.debug = record.id

    #message = "Success. I categorized ", counter, " records."

    #return dict(message = message)
