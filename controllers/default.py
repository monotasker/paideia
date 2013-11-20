# -*- coding: utf-8 -*-

from paideia_stats import Stats
from paideia_bugs import Bug
import traceback
from paideia_utils import send_error
from pprint import pprint
#from gluon.tools import prettydate

if 0:
    from gluon import current, cache
    from gluon.tools import Auth
    from gluon.dal import DAL
    db = DAL()
    auth = Auth()
    response, session = current.response, current.session
    T, service = current.T, current.service
    request = current.request

mail = current.mail


def index():
    """    """
    mod_topic = db(db.topics.topic == 'index-modals').select(db.topics.id).first()
    modals = db(db.content_pages.topics.contains([mod_topic.id])).select().as_list()
    print len(modals)
    hero_topic = db(db.topics.topic == 'hero').select(db.topics.id).first()
    hero = db(db.content_pages.topics.contains([hero_topic.id])).select().as_list()
    return {'modals': modals, 'hero': hero}


def faqs():
    """ """
    faqs_topic = db(db.topics.topic == 'faqs').select(db.topics.id).first()
    faqs = db(db.content_pages.topics.contains([faqs_topic.id])).select().as_list()
    return {'faqs': faqs}


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/verify_email
    http://..../[app]/default/user/retrieve_username
    http://..../[app]/default/user/request_reset_password
    http://..../[app]/default/user/reset_password
    http://..../[app]/default/user/impersonate  # user is request.args[0]
        auth.is_impersonating() checks whether current user is shadowing another
        only allowed if has_permission('impersonate', db.auth_user, user_id)
    http://..../[app]/default/user/groups
        lists user's group memberships
    http://..../[app]/default/user/not_authorized

    code for these actions is in gluon/tools.py in Auth() class
    """
    # make sure d3.js dc.js and crossfire.js are loaded
    response.files.append(URL('static', 'plugin_d3/d3/d3.js'))
    response.files.append(URL('static', 'plugin_d3/dc/dc.js'))
    response.files.append(URL('static', 'plugin_d3/crossfilter/crossfilter.js'))
    response.files.append(URL('static', 'plugin_d3/dc/dc.css'))
    return dict(form=auth())


def info():
    """
    Return data reporting on a user's performance record.

    This controller is intended to serve the view profile.load as a modular
    page component, to be embedded in other views such as:
        default/user.html
        reporting/user.html

    Returns a dict with the following keys:

    'the_name':         User's name from auth.user as lastname, firstname (str)
    'tz':               User's time zone from auth.user (extended in db.py)
    'email':            User's email (str)
    'cal':              html calendar with user path stats (from stats.monthcal)
    'blist': blist,     list of User's bug reports
    'max_set': `        max_set, Badge set reached by user (int)
    'active':           list of user's active tags with performance and badge data
        Each item is a dict with these keys:
        'name'              user's id from auth.user (int)
        'tag_records'
            'tag'           id of tag for this row (int)
            'times_right'       cumulative number of times right (double)
            'times_wrong'       cumulative number of times wrong (double)
            'tlast_wrong'       date of last wrong answer (datetime.datetime)
            'tlast_right'       date of last right answer (datetime.datetime)
            'pretty_lwrong'**   readable form (str)
            'pretty_lright'**   readable form (str)
            'in_path'           path of last question for the tag
            'step'              step of last question for the tag
            'secondary_right'   list of dates (datetime.datetime) when step with
                                this tag as secondary was answered correctly
        'badges'
            'badge_name'    ***
            'description'   ***
        'badges_begun'
            'dt_cat1'**         machine-friendly form (datetime.datetime object)
            'prettydate_cat1'** readable form (str)
            'dt_cat2'**         machine-friendly form (datetime.datetime object)
            'prettydate_cat2'** readable form (str)
            'dt_cat3'**         machine-friendly form (datetime.datetime object)
            'prettydate_cat3'** readable form (str)
            'dt_cat4'**         machine-friendly form (datetime.datetime object)
            'prettydate_cat4'** readable form (str)
        'tag_set'**         ***
        'current_level'**   number of max level achieved so far (str)
        'logs'              list of dictionaries, each with the following keys:
            'step'
            'prompt'
            'count'
            'right'
            'wrong'
            'dt_attempted'
            'dt_local'
    'log':              stats.step_log['loglist']
        'step'
        'prompt'
        'count'
        'right'
        'wrong'
        'last_wrong'
        'right_since'
    'duration':         Default duration for recent paths info (from
                        stats.step_log['duration'])
    """

    try:

        # Allow passing explicit user but default to current user
        if 'id' in request.vars:
            user = db.auth_user[request.vars['id']]
        else:
            user = db.auth_user[auth.user_id]
        tz = user.time_zone
        email = user.email

        stats = Stats(user.id, cache=cache)
        name = stats.get_name()
        active = stats.active_tags()
        cal = stats.monthcal()
        max_set = stats.get_max()
        #sl = stats.step_log()
        #log = sl['loglist']
        #duration = sl['duration']

        b = Bug()
        blist = b.bugresponses(user.id)

        catlabels = ['started at beginner level',
                    'promoted to apprentice level',
                    'promoted to journeyman level',
                    'promoted to master level']
    except Exception:
        print traceback.format_exc(5)

    return {'the_name': name,
            'tz': tz,
            'email': email,
            'cal': cal,
            'blist': blist,
            'active': active,
            'max_set': max_set,
            #'log': log,
            #'duration': duration
            }


def oops():
    """A controller to handle rerouted requests that return error codes."""
    code = request.vars.code
    ticket = request.vars.ticket

    #requested_uri = request.vars.requested_uri
    request_url = request.vars.request_url

    # Return the original HTTP error code
    response.status = code
    #if code == 500:
    title = 'Paideia - Internal error reported'
    msg = '<html><body>Hello Ian,<br>I seem to have run into an error!' \
          'request url:<br /><br />{url}' \
          '<br /><br />' \
          'Here is the ticket:<br /><br />' \
          'local: <a href="http://127.0.0.1:8000/admin/default/ticket/{t}" target="_blank">{t}</a>' \
          '<br /><br />' \
          'remote: <a href="https://ianwscott.webfactional.com/admin/default/ticket/{t}" target="_blank">{t}</a>' \
          '</body></html>'.format(url=request_url, t=ticket)

    mail.send(mail.settings.sender, title, msg)

    return {'code': code}


@auth.requires_membership(role='administrators')
def csv():
    """
    generic csv function to export a single table.

    The table is set via the first url argument.
    """
    table = request.args[0]
    items = db().select(db[table].ALL)
    return {'items': items}


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


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
