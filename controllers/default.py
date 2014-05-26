#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from paideia_stats import Stats
from paideia_bugs import Bug
# import traceback
# from paideia_utils import send_error
# from pprint import pprint
# from gluon.tools import prettydate

if 0:
    from gluon import current, cache, URL
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

    'the_name':             User's name from auth.user as lastname, firstname (str)
    'tz':                   User's time zone from auth.user (extended in db.py)
    'email':                User's email (str)
    'cal':                  html calendar with user path stats (from stats.monthcal)
    'blist':                list of User's bug reports
    'max_set':              Badge set reached by user (int)
    'goal':
    'badge_levels':         Dictionary with badle levels (int) as keys and
                            a list of badge names (or tag: int) as each value.
    'badge_table_data':
    'badges_active_over_time':
    'badges_tested_over_time':
    'sets_tested_over_time':
    'steps_most_wrong':

    """
    # Include files for Datatables jquery plugin and bootstrap css styling
    response.files.append("https://cdn.datatables.net/1.10.0/js/jquery.dataTables.js")
    response.files.append("https://cdn.datatables.net/plug-ins/28e7751dbec/"
                          "integration/bootstrap/3/dataTables.bootstrap.css")
    # Allow passing explicit user but default to current user
    if 'id' in request.vars:
        user = db.auth_user[request.vars['id']]
    else:
        user = db.auth_user[auth.user_id]

    stats = Stats(user.id, cache=cache)

    # tab1
    name = stats.get_name()
    tz = user.time_zone
    email = user.email
    max_set = stats.get_max()
    goal = stats.get_goal()
    badge_levels = stats.get_badge_levels()
    badge_table_data = stats.active_tags()
    # badges_active_over_time = stats.badges_active_over_time(badge_table_data)

    # tab2
    mycal = stats.monthcal()
    # badges_tested_over_time = stats.badges_tested_over_time(badge_table_data)
    # sets_tested_over_time = stats.sets_tested_over_time(badge_table_data)
    # steps_most_wrong = stats.steps_most_wrong(badge_table_data)

    # tab3
    b = Bug()
    blist = b.bugresponses(user.id)

    return {'the_name': name,
            'tz': tz,
            'email': email,
            'cal': mycal,
            'blist': blist,
            'max_set': max_set,
            'goal': goal,
            'badge_levels': badge_levels,
            'badge_table_data': badge_table_data,
            # 'badges_active_over_time': badges_active_over_time,
            # 'badges_tested_over_time': badges_tested_over_time,
            # 'sets_tested_over_time': sets_tested_over_time,
            # 'steps_most_wrong': steps_most_wrong
            }


def oops():
    """A controller to handle rerouted requests that return error codes."""
    code = request.vars.code
    ticket = request.vars.ticket

    # requested_uri = request.vars.requested_uri
    request_url = request.vars.request_url

    # Return the original HTTP error code
    response.status = code
    # if code == 500:
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

"""
def call():
    '''
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    '''
    return service()


@auth.requires_signature()
def data():
    '''
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
    '''
    return dict(form=crud())
"""


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
