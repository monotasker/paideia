#! /usr/bin/python3.9
# encoding: utf-8
from copy import copy
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import dateutil
from itertools import permutations
import os
from traceback import format_exc, print_exc
# from gluon.contrib.generics import pdf_from_html
from gluon.serializers import custom_json, json as json_serializer
from gluon.utils import web2py_uuid
from itertools import chain
import json
import os
from pprint import pprint
from paideia import Walk
from paideia_utils import GreekNormalizer
from paideia_stats import Stats, get_set_at_date, make_classlist, \
    get_term_bounds
from paideia_stats import get_current_class, get_chart1_data, my_custom_json
from paideia_bugs import Bug, trigger_bug_undo
from paideia_user_management import do_user_promotion, do_user_demotion
import pytz
import re
import stripe
import time
from typing import List
# from pydal.objects import Rows

from gluon._compat import urllib2, urlencode, urlopen, to_bytes, to_native

if 0:
    from gluon import Auth, Response, Request, Current
    auth = Auth
    current = Current
    response = current.response
    request = current.request
    db = current.db


def content_pages():
    """
    Return a list of the text for each content page matching provided tags.
    """
    db = current.db
    request = current.request
    tag_list = request.vars['tag_list']
    if request.method == "POST":
        mypages = db(db.content_pages.topics.contains(tag_list)
                     ).select().as_list()
        return json_serializer(mypages)
    else:
        return json_serializer({'status': 'bad request',
                    'reason': f'${request.method} not a valid method ' \
                               'for this endpoint',
                    'error': None})


def download():
    """
    allows downloading of uploaded files

    expects the request variable "filename"
    """
    db = current.db
    mystream = response.download(request, db)

    return mystream


def get_prompt():
    """
    Return the data to begin a step interaction.

    Private api method to handle calls from the react front-end.

    Expects the following variables in the call payload ()
        loc: str
        repeat: bool = False
        response_string: str
        set_review: bool
        path: int = None
        step: int = None
        set_blocks: Dict = None
        new_user: bool = false
        pre_bug_step_id: int = None
        testing: bool = False

    Returns:
        JSON object with the following keys:

        audio: dict
        bg_image: string
        sid: int
        prompt_text: str
        widget_img: str
        instructions: ???
        slidedecks: dict
        loc: str
        response_buttons: list(str)
        response_form: {form_type: "text", values: null}
        bugreporter: ???
        pre_bug_step_id: int
        npc_image: str
        completed_count: int
        category: int
        pid: int
        new_content: bool
        paideia_debug: ???
    """
    auth = current.auth
    session = current.session
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = request.vars.new_user
        stepargs = {'path': None,
                    'step': None,
                    'response_string': None,
                    'set_blocks': None,
                    'repeat': False
                    }
        for k, v in request.vars.items():
            if k in stepargs.keys() \
                    and k not in ['loc', 'new_user', 'response_string']:
                stepargs[k] = v
        # handle setting of 'loc' or 'new_user' in testing scenario
        if request.vars['testing'] is True:
            stepargs['loc'] = request.vars['loc']
            if request.vars['new_user'] is True:
                stepargs['new_user'] = request.vars['new_user']

        # handle setting of badge set review level
        if session.set_review and session.set_review > 0:
            stepargs['set_review'] = session.set_review
        else:
            stepargs['set_review'] = False
        resp = Walk(new_user=new_user).start(myloc, **stepargs)
        return json_serializer(resp)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def set_viewed_slides():
    """
    Sets a user's "viewed_slides" value of the stored session data to True
    """
    auth = current.auth
    if auth.is_logged_in():
        # find the current user's session data
        db(db.session_data.name == auth.user_id
           ).update(viewed_slides=True)
        # update the "viewed_slides" value
        db.commit()
        return json_serializer({'message': 'set "viewed_slides" to "True"'})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def evaluate_answer():
    """
    Private api method to handle calls from the react front-end.
    """
    auth = current.auth
    session = current.session
    if auth.is_logged_in():
        myloc = request.vars.loc
        new_user = False
        stepargs = {'path': None,
                    'response_string': request.vars.response_string,
                    'set_blocks': None
                    }
        for k, v in request.vars.items():
            if k in stepargs.keys() \
                    and k not in ['loc', 'new_user']:
                stepargs[k] = v
        if session.set_review and session.set_review > 0:
            stepargs['set_review'] = session.set_review
        else:
            stepargs['set_review'] = False
        resp = Walk(new_user=new_user).start(myloc, **stepargs)
        resp['eval_text'] = copy(resp['prompt_text'])
        resp['prompt_text'] == None
        return json_serializer(resp)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def _fetch_other_coursedata(uid, current_class, mydatetime):
    """
    Private function to gather course data other than the current one.

    Called by get_profile_info.

    """
    debug = 0
    myclasses = db((db.class_membership.name == uid) &
                   (db.class_membership.class_section != current_class) &
                   (db.class_membership.class_section == db.classes.id)
                   ).select(orderby=db.classes.academic_year|db.classes.end_date).as_list()
    for idx, c in enumerate(myclasses):
        myprof = db.auth_user(c['classes']['instructor'])
        myclasses[idx]['classes']['instructor'] = {'first_name': myprof['first_name'],
                                             'last_name': myprof['last_name'],
                                             'id': myprof['id']}
    myclasses_prior = [c for c in myclasses if pytz.utc.localize(c['classes']['end_date']) < mydatetime]
    myclasses_latter = [c for c in myclasses if pytz.utc.localize(c['classes']['start_date']) >= mydatetime]
    if debug:
        print ("=======================================================")
        for c in myclasses_prior:
            print (c['classes']['id'], c['class_membership']['id'], c['classes']['academic_year'], c['classes']['course_section'], c['classes']['term'])

        print ("-------------------------------------------------------")
        for c in myclasses_latter:
            print (c['classes']['id'], c['class_membership']['id'], c['classes']['academic_year'], c['classes']['course_section'], c['classes']['term'])


    return {"prior_classes": myclasses_prior,
            "latter_classes": myclasses_latter}


def _fetch_current_coursedata(uid, mydatetime):
    """
    Private function called by _fetch_userdata and get_profile_info

    """
    current_class = get_current_class(uid, mydatetime)
    course = {}
    if current_class:
        course['daily_quota'] = current_class['classes']['paths_per_day']
        course['weekly_quota'] = current_class['classes']['days_per_week']
        course['class_info'] = {k: v for k, v in
                                current_class['classes'].items()
                                if k in ['institution', 'academic_year',
                                        'term', 'course_section',
                                        'start_date',
                                        'end_date', 'paths_per_day',
                                        'days_per_week', 'instructor',
                                        'a_target', 'a_cap', 'b_target',
                                        'b_cap', 'c_target', 'c_cap',
                                        'd_target', 'd_cap', 'f_target']
                                }
        abs_startdt = course['class_info']['start_date']

        if current_class['class_membership']['custom_start'] is not None:
            course['class_info']['custom_start_date'] = \
                current_class['class_membership']['custom_start']
            abs_startdt = course['class_info']['custom_start_date']

        course['class_info']['custom_end_date'] = \
            current_class['class_membership']['custom_end']

        mystartset = current_class['class_membership']['starting_set']
        if mystartset is None:
            mystartset = get_set_at_date(uid, abs_startdt)
        course['class_info']['starting_set'] = mystartset

    else:
        course['daily_quota'] = 20
        course['weekly_quota'] = 5
        course['class_info'] = {}

    return course


def _fetch_userdata(raw_user, vars):
    """
    Private function called by get_login and get_userdata

    This is where the actual user data collection happens
    """
    try:
        user = {k:v for k, v in raw_user.items() if k in
                ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
        memberships = db((db.auth_membership.user_id == user['id']) &
                            (db.auth_membership.group_id == db.auth_group.id)
                            ).select(db.auth_group.role).as_list()
        user['roles'] = [m['role'] for m in memberships]

        if any(r for r in ['instructors', 'administrators']
                if r in user['roles']):
            instructing = db(db.classes.instructor == user['id']).select()
            if instructing:
                user['instructing'] = []
                for i in instructing:
                    user['instructing'].append({k: v for k, v in i.items()
                        if k in ['id', 'days_per_week',
                                 'institution', 'academic_year',
                                 'term', 'course_section',
                                 'instructor', 'start_date',
                                 'end_date', 'paths_per_day',
                                 'a_target', 'a_cap', 'b_target',
                                 'b_cap', 'c_target', 'c_cap',
                                 'd_target', 'd_cap', 'f_target']
                    })
            else:
                user['instructing'] = None

        user.update(**_fetch_current_coursedata(user['id'],
                                                datetime.now(timezone.utc))
                    )

        my_progress = db(db.tag_progress.name == user['id']
                             ).select().first()
        user['current_badge_set'] = my_progress.latest_new if my_progress else 0

    except AttributeError:  # if login response was False and has no items
        print(format_exc())
        user = {'id': None}

    return user


def _check_password_strength(password):
    # TODO: consider this regex that requires special characters:
    # password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
        # "(?=.*[!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~])"\
        # "[A-Za-z\d!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~]{8,20}$"
    password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
                     "[A-Za-z\d!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~]{8,20}$"
    password_pat = re.compile(password_regex)
    # print('password', password)
    # print('password_pat', password_pat)
    return re.search(password_pat, password)


def _is_safe_string(mystring, length=0):
    """
    Returns true if string is regular alphanumeric string

    If length is specified as a single number (or numeric string), also requires that the string be the set length.
    Otherwise no length constraints required.
    """
    if type(length) is list:
        mylength = "{},{}".format(str(length[0]), str(length[1]))
    else:
        mylength = str(length) if length!=0 else "1,64"
    str_pat = re.compile(r'^[a-zA-Z0-9\s\-\/_]{{{}}}$'.format(mylength))

    return re.search(str_pat, mystring)


def do_password_reset():
    """
    Actually allow a user to reset their password after email link followed.
    """
    debug = 0
    request = current.request
    response = current.response

    key = request.vars['key']
    token = request.vars['token']
    new_password_A = request.vars['password_A']
    new_password_B = request.vars['password_B']


    missing = {k: v for k, v in request.vars.items() if
               k in ['key', 'password_A', 'password_B']
               and v in [None, "null", "undefined", ""]}
    if missing and len(missing.keys()) > 0:
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Missing request data',
                    'error': missing})
    if new_password_A != new_password_B:
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'New passwords do not match',
                    'error': None})
    if not _check_password_strength(new_password_A):
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Password is not strong enough',
                    'error': None})

    keydata = {}
    with open('applications/paideia/private/app.keys', 'r') as keyfile:
        for line in keyfile:
            k, v = line.split()
            keydata[k] = v
    params = urlencode({
        'secret': keydata['captcha3_private_key'],
        'response': token
    }).encode('utf-8')
    recap_request = urllib2.Request(
        url="https://www.google.com/recaptcha/api/siteverify",
        data=to_bytes(params),
        headers={'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'reCAPTCHA Python'})
    httpresp = urlopen(recap_request)
    content = httpresp.read()
    httpresp.close()
    response_dict = json.loads(to_native(content))

    if response_dict["success"] == True and response_dict["score"] > 0.5:
        try:

            t0 = int(key.split('-')[0])
            if time.time() - t0 > 60 * 60 * 48:
                response.status = 403
                return json_serializer({'status': 'forbidden',
                                        'reason': 'Password reset key was bad',
                                        'error': None})
            user = db(db.auth_user.reset_password_key==key).select().first()
            if not user:
                response.status = 404
                return json_serializer({'status': 'not found',
                            'reason': 'User does not exist',
                            'error': None})
            rkey = user.registration_key
            if rkey in ('pending', 'disabled', 'blocked') or (rkey or '').startswith('pending'):
                response.status = 409
                return json_serializer({'status': 'conflict',
                                        'reason': 'Action blocked',
                                        'error': "Reset blocked or pending"})
            if debug: print('USER=========================')
            if debug: pprint(user)
            encrypted_password = db.auth_user.password.validate(new_password_B)[0]
            user.update_record(**{'password': encrypted_password,
                                'registration_key': '',
                                'reset_password_key': ''})
            return json_serializer({'status': 'success',
                                    'reason': 'Password reset successfully'})

        except Exception:
            print_exc()
            response.status = 500
            return json_serializer({'status': 'internal server error',
                        'reason': 'Unknown error in function do_password_reset',
                        'error': format_exc()})
    else:
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                    'reason': 'Recaptcha failed',
                    'error': None})


def my_email_reset_password(auth, user):
    """
    Duplicates gluon.tools.email_reset_password to allow proper url format
    """
    reset_password_key = str(int(time.time())) + '-' + web2py_uuid()
    link = auth.url(auth.settings.function,
                    args=('reset_password',), vars={'key': reset_password_key},
                    scheme=True)
    # strip out unnecessary controller/function from url
    regex = '/api/start_password_reset'
    link = re.sub(regex, "", link)

    d = dict(user)
    d.update(dict(key=reset_password_key, link=link))
    if auth.settings.mailer and auth.settings.mailer.send(
        to=user.email,
        subject=auth.messages.reset_password_subject % d,
            message=auth.messages.reset_password % d):
        user.update_record(reset_password_key=reset_password_key)
        return True
    return False

def start_password_reset():
    """
    Initiate a password reset by sending user an email with a link.
    """
    auth = current.auth
    auth.settings.function = ""
    auth.settings.controller = ""
    auth.messages.reset_password = (
        "<html><p>Hi %(first_name)s %(last_name)s,</p>"
        "<p>Greetings from the people at "
        "<a href='https://learngreek.ca/paideia'>Paideia</a>! Someone asked " "to reset the account password for %(email)s. "
        "If this was you, click on the link below and enter your "
        "new password in the form there. If you didn't request this "
        "reset, or you have changed your mind, you can ignore this email "
        "and your password will remain unchanged."
        "<p>Reset password link: %(link)s</p> "
        "<p>This link will be valid for 48 hours. After that you'll need to "
        "request a new one.<p>"
        "<p>All the best,</p>"
        "<p>The Paideia people</p></html>")
    auth.messages.reset_password_subject = "Paideia Password reset requested for %(first_name)s %(last_name)s"
    response = current.response
    email = request.vars['email']
    token = request.vars['token']

    email_pat = re.compile('^([a-zA-Z0-9]?[\._]?[a-zA-Z0-9]+)+[@]\w+[.]\w+$')
    if email in [None, "null", "undefined", ""] \
            or not re.search(email_pat, email.strip()):
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Missing request data',
                    'error': {'email': email}})
    else:
        email=email.strip()

    user = db(db.auth_user.email==email).select().first()
    if not user:
        response.status = 404
        return json_serializer({'status': 'not found',
                    'reason': 'User does not exist',
                    'error': None})

    keydata = {}
    with open('applications/paideia/private/app.keys', 'r') as keyfile:
        for line in keyfile:
            k, v = line.split()
            keydata[k] = v
    params = urlencode({
        'secret': keydata['captcha3_private_key'],
        'response': token
    }).encode('utf-8')
    recap_request = urllib2.Request(
        url="https://www.google.com/recaptcha/api/siteverify",
        data=to_bytes(params),
        headers={'Content-type': 'application/x-www-form-urlencoded',
                'User-agent': 'reCAPTCHA Python'})
    httpresp = urlopen(recap_request)
    content = httpresp.read()
    httpresp.close()
    response_dict = json.loads(to_native(content))

    if response_dict["success"] == True and response_dict["score"] > 0.5:
        try:
            key = user.registration_key

            if key in ('pending', 'disabled', 'blocked') or (key or '').startswith('pending'):
                response.status = 409
                return json_serializer({'status': 'conflict',
                            'reason': 'Action already pending',
                            'error': None})

            if my_email_reset_password(auth, user):
                return json_serializer({'status': 'success',
                            'reason': 'Reset email sent',
                            'email': email})
            else:
                response.status = 500
                return json_serializer({'status': 'internal server error',
                            'reason': 'Could not send reset email',
                            'error': None})

        except Exception:
            print_exc()
            response.status = 500
            return json_serializer({'status': 'internal server error',
                        'reason': 'Unknown error in function start_password_reset',
                        'error': format_exc()})
    else:
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                    'reason': 'Recaptcha failed',
                    'error': None})


def get_registration():
    """
    """
    debug=False
    request = current.request
    auth = current.auth
    response = current.response
    token = request.vars['token'].strip()
    email = request.vars['email'].strip()
    password = request.vars['password'].strip()
    tz = request.vars['time_zone'].strip()
    first_name = request.vars['first_name'].strip()
    last_name = request.vars['last_name'].strip()

    str_pat = re.compile('^[a-zA-Z0-9\s\-\/_]+$')
    email_pat = re.compile('^([a-zA-Z0-9]?[\._]?[a-zA-Z0-9]+)+[@]\w+[.]\w+$')
    missing = {k: v for k, v in request.vars.items() if
               k not in ["token", "password"] and
               ((v in ["undefined", None, "", "null"])
                or (k!="email" and not re.search(str_pat, v.strip()))
                or (k=="email" and not re.search(email_pat, v.strip()))
                )}
    if missing and len(missing.keys()) > 0:
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Missing request data',
                    'error': missing})

    if not _check_password_strength(password):
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Password is not strong enough',
                    'error': {"password": password}})

    existing_user_count = db(db.auth_user.email==email).count()
    if existing_user_count>0:
        response.status = 409
        return json_serializer({'status': 'conflict',
                    'reason': 'User with this email exists',
                    'error': None})
    else:
        if debug: print("in api: registering new user***************")

        keydata = {}
        with open('applications/paideia/private/app.keys', 'r') as keyfile:
            for line in keyfile:
                k, v = line.split()
                keydata[k] = v
        params = urlencode({
            'secret': keydata['captcha3_private_key'],
            'response': token
        }).encode('utf-8')
        recap_request = urllib2.Request(
            url="https://www.google.com/recaptcha/api/siteverify",
            data=to_bytes(params),
            headers={'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': 'reCAPTCHA Python'})
        httpresp = urlopen(recap_request)
        content = httpresp.read()
        httpresp.close()
        response_dict = json.loads(to_native(content))
        if debug: pprint(response_dict)

        if response_dict["success"] == True and response_dict["score"] > 0.5:
            try:
                response_data = auth.register_bare(email=email,
                                                   password=password,
                                                   first_name=first_name,
                                                   last_name=last_name,
                                                   time_zone=tz,
                                                   )
                response_data = response_data.as_dict()
                response_data = {k: v for k, v in response_data.items()
                                if k in ["email", "first_name",
                                         "last_name", "id"]}
                return json_serializer(response_data)
            except Exception:
                print_exc()
                response.status = 500
                return json_serializer({'status': 'internal server error',
                            'reason': 'Unknown error in function get_registration',
                            'error': format_exc()})
        else:
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                        'reason': 'Recaptcha failed',
                        'error': None})


def _check_class_key(myclass_key):
    """
    """
    myclass = None
    if (not myclass_key or myclass_key in ['null', 'undefined']
            or not _is_safe_string(myclass_key)):
        print('bad key')
        return {"status": "bad key"}

    myclass_rows = db((db.class_keys.class_key==myclass_key) &
                (db.class_keys.class_section==db.classes.id)
                ).select()
    if len(myclass_rows) == 0:
        print('no such key')
        return {"status": "no such key"}

    expiration_dt = datetime.now(timezone.utc) + timedelta(days=30)
    time_valid_rows = myclass_rows.find(lambda r:
        r.class_keys.created_date.replace(tzinfo=pytz.UTC) <= expiration_dt)
    if len(time_valid_rows) == 0:
        print('key expired')
        return {"status": "key expired"}

    valid_rows = time_valid_rows.find(lambda r:
                                      r.class_keys.cancelled==False)
    if len(valid_rows) == 0:
        print('key cancelled')
        return {"status": "key cancelled"}

    myclass = valid_rows[0]
    # print('in check:')
    # pprint(myclass)

    return {"status": "ok",
            "class_row": myclass}


def validate_class_key():
    """
    """
    response = current.response
    myclass_key = request.vars['course_key']
    user_id = request.vars['user_id']
    myclass = None

    try:
        myresult = _check_class_key(myclass_key)

        if myresult['status'] == "bad key":
            response.status = 400
            return json_serializer({'status': 'bad request',
                        'reason': 'Missing request data',
                        'error': {'course_key': myclass_key}})

        if myresult['status'] == "no such key":
            response.status = 404
            return json_serializer({'status': 'Not found',
                                    'reason': 'No matching record found'})

        if myresult['status'] == "key expired":
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Class key is expired'})

        if myresult['status'] == "key cancelled":
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Class key was cancelled'})

        myclass = myresult['class_row']

        my_memberships = db((db.class_membership.name==user_id) &
                            (db.class_membership.class_section==myclass.classes.id)
                            ).select()
        if len(my_memberships) > 0:
            response.status = 409
            return json_serializer({'status': 'conflict',
                                    'reason': 'Action blocked',
                                    'error': "A membership for this user already exists in the course group"})

        class_label = "{}, {} {}, {}".format(myclass.classes.course_section,
                                        myclass.classes.term,
                                        myclass.classes.academic_year,
                                        myclass.classes.institution
                                        )
        response.status = 200
        return json_serializer({'status': 'success',
                                'class_label': class_label,
                                'class_id': myclass.classes.id})

    except Exception:
        response.status = 500
        return json_serializer({'status': 'internal server error',
                    'reason': 'Unknown error in function validate_class_key',
                    'error': format_exc()})


def join_class_group():
    debug = 0
    event = None
    class_key = request.vars['course_key']
    class_id = int(request.vars['course_id'])
    user_id = int(request.vars['user_id'])
    try:
        result = ""

        validity = _check_class_key(class_key)
        if debug: print('in join')
        if debug: print(validity)
        if debug: print(type(validity['class_row']['classes']['id']))
        if debug: print(type(class_id))
        if (validity['status'] != "ok") \
                or (validity['class_row']['classes']['id'] != class_id):
            if debug: print(validity['status'] != "ok")
            if debug: print(validity['class_row']['classes']['id'] != class_id)
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Insufficient privileges',
                                    'error': 'Could not validate the course key provided'})

        my_memberships = db((db.class_membership.name==user_id) &
                            (db.class_membership.class_section==class_id)
                            ).select()
        if len(my_memberships) > 0:
            response.status = 409
            return json_serializer({'status': 'conflict',
                                    'reason': 'Action blocked',
                                    'error': "A membership for this user already exists in the course group"})

        result = db.class_membership.insert(**{'name': user_id,
                                               'class_section': class_id
                                               })

        response.status = 200
        return json_serializer({'status': "success",
                                'result_row': result})
    except Exception:
        response.status = 500
        return json_serializer({'status': 'internal server error',
                                'reason': 'Unknown error in function validate_class_key',
                                'error': format_exc()})


def calculate_order_amount(itemLabels):
    """
    """

    return 1500


def create_checkout_intent():
    """
    Create a Stripe payment checkout session for hosted checkout page.
    """
    response = current.response
    order_items = request.vars['order_items']
    myclass_key = request.vars['course_key']
    user_id = request.vars['user_id']
    user_row = db.auth_user(user_id);
    myclass = None
    class_label = ""
    if myclass_key and myclass_key not in ['null', 'undefined']:
        expiration_dt = datetime.now(timezone.utc) + timedelta(days=30)
        myclass = db((db.class_keys.class_key==myclass_key) &
                     (db.class_keys.created_date <= expiration_dt) &
                     (db.class_keys.cancelled==False) &
                     (db.class_keys.class_section==db.classes.id)
                     ).select().first()
        class_label = "{}, {} {}, {}".format(myclass.classes.course_section,
                                          myclass.classes.term,
                                          myclass.classes.academic_year,
                                          myclass.classes.institution
                                          )

    try:
        keydata = {}
        with open('applications/paideia/private/app.keys', 'r') as keyfile:
            for line in keyfile:
                k, v = line.split()
                keydata[k] = v
        # FIXME: use real api key in production
        stripe.api_key = keydata['stripe_secret_key']
        # stripe.api_key = "sk_test_51IYtbhCzY7JkMiXGFmXzguuMQHrNB40wpVI78TDjYWgJP5r3xahRDqVU3qKXnhMchItpWky45eSRBh0X7LtH1tCg00eOgWcggP"
        checkout_intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(order_items),
            currency='cad',
            # customer='{}: {}, {}'.format(user_id,
            #                              user_row['last_name'],
            #                              user_row['first_name']),
            description="Paideia student membership for {}".format(class_label),
            receipt_email=user_row["email"],
            statement_descriptor="Paideia course member"
            )
        return json_serializer(
            {'clientSecret': checkout_intent['client_secret'],
             'userId': user_id}
            )

    except Exception:
        response.status = 403
        return json_serializer({'status': 'insufficient privileges',
                    'reason': 'Stripe checkout session creation failed',
                    'error': format_exc()})


def get_login():
    """
    API method to log a user in with web2py's authentication system.

    Private api method to handle calls from the react front-end.

    Returns:
        JSON object with data on the user that was successfully logged in. If the login is unsuccessful, the JSON object carries just an 'id' value of None.
    """
    debug=False
    request = current.request
    auth = current.auth
    session = current.session
    response = current.response
    token = request.vars['token'].strip() if request.vars['token'] else None
    email = request.vars['email'].strip() if request.vars['email'] else None
    if debug: print('api::get_login: email:', email)
    password = request.vars['password'].strip()
    # if debug: print('api::get_login: password:', password)

    email_pat = re.compile('^([a-zA-Z0-9]?[\._]?[a-zA-Z0-9]+)+[@]\w+[.]\w+$')
    password_pat = re.compile("^[A-Za-z\d!\"#\$%&'\(\)\*\+,-\.\/:;<=>\?@\[\]\\\^_`\{\|\}~]{2,50}$")

    missing = {k: v for k, v in request.vars.items() if
               k!="token" and
               ((v in ["undefined", None, "", "null"])
                or (k=="password" and not re.search(password_pat, password))
                or (k=="email" and not re.search(email_pat, email))
                )
               }
    if missing and len(missing.keys()) > 0:
        response.status = 400
        return json_serializer({'status': 'bad request',
                    'reason': 'Missing request data',
                    'error': missing})

    try:
        keydata = {}
        with open('applications/paideia/private/app.keys', 'r') as keyfile:
            for line in keyfile:
                k, v = line.split()
                keydata[k] = v
        params = urlencode({
            'secret': keydata['captcha3_private_key'],
            'response': token
        }).encode('utf-8')
        recap_request = urllib2.Request(
            url="https://www.google.com/recaptcha/api/siteverify",
            data=to_bytes(params),
            headers={'Content-type': 'application/x-www-form-urlencoded',
                    'User-agent': 'reCAPTCHA Python'})
        httpresp = urlopen(recap_request)
        content = httpresp.read()
        httpresp.close()
        response_dict = json.loads(to_native(content))
        if debug: pprint(response_dict)

        if response_dict["success"] == True and response_dict["score"] > 0.5:
            mylogin = auth.login_bare(email, password)
            if debug: print('mylogin********')
            if debug: print(mylogin)
            if mylogin == False:
                response.status = 401
                return json_serializer({'status': 'unauthorized',
                            'reason': 'Login failed',
                            'error': 'Did not recognize email-password combination'})
            else:
                user = {k:v for k, v in mylogin.items() if k in
                        ['email', 'first_name', 'last_name', 'hide_read_queries', 'id', 'time_zone']}
                full_user = _fetch_userdata(user, request.vars)
                full_user['review_set'] = session.set_review \
                    if 'set_review' in session.keys() else None
                response.status = 200
                return json_serializer(full_user, default=my_custom_json)

        else:
            response.status = 500
            return json_serializer({'status': 'internal server error',
                        'reason': 'Unknown error in function get_registration',
                        'error': "failed recaptcha check: {}".format(response_dict["score"])})
    except Exception:
        response.status = 500
        return json_serializer({'status': 'internal server error',
                    'reason': 'Unknown error in function get_registration',
                    'error': format_exc()})


def get_userdata():
    """
    API method to get the user data for the currently logged in user.
    """
    auth = current.auth
    session = current.session
    if auth.is_logged_in():
        user = db.auth_user(auth.user_id).as_dict()
        full_user = _fetch_userdata(user, request.vars)
        full_user['review_set'] = session.set_review \
            if 'set_review' in session.keys() else None
        return json_serializer(full_user, default=my_custom_json)
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def do_logout():
    """
    API method to log the current user out.

    Private api method to handle calls from the react front-end.

    Returns:
        JSON object with the same user fields returned at login, but with null
        values for each one.
    """
    # print("about to log out")
    auth = current.auth
    try:
        mylogout = auth.logout_bare()
        # print ("did logout")
        myuser = {k:None for k in ['email', 'first_name', 'last_name',
                                   'hide_read_queries', 'id', 'time_zone']}
        return json_serializer(myuser)
    except Exception as e:
        print(e)
        return json_serializer({'error': e})


def check_login():
    """
    API method to return the current server login status.

    """
    auth = current.auth
    session = current.session
    my_login = {'logged_in': False, 'user': 0}
    if auth.is_logged_in():
        my_login['logged_in'] = True
        my_login['user'] = auth.user_id
    return json_serializer(my_login)


def _add_posts_to_queries(queries, unread_posts, unread_comments):

    debug = 0
    for idx, q in enumerate(queries):
        if q['bugs']['posts']:
            myposts = db(
                (db.bug_posts.id.belongs(q['bugs']['posts'])) &
                (db.bug_posts.poster==db.auth_user.id) &
                ((db.bug_posts.deleted == False) |
                 (db.bug_posts.deleted == None))
                ).select(db.auth_user.first_name,
                         db.auth_user.last_name,
                         db.bug_posts.id,
                         db.bug_posts.poster,
                         db.bug_posts.poster_role,
                         db.bug_posts.dt_posted,
                         db.bug_posts.post_body,
                         db.bug_posts.modified_on,
                         db.bug_posts.hidden,
                         db.bug_posts.deleted,
                         db.bug_posts.flagged,
                         db.bug_posts.public,
                         db.bug_posts.thread_index,
                         db.bug_posts.pinned,
                         db.bug_posts.popularity,
                         db.bug_posts.helpfulness,
                         db.bug_posts.comments,
                         orderby=db.bug_posts.thread_index
                         ).as_list()

            if not auth.has_membership('administrators'):
                if auth.has_membership('instructors'):
                    myposts = list(filter(
                        lambda x: x['bug_posts']['public'] is True
                        or x['bug_posts']['poster'] == auth.user_id
                        or _is_my_student(auth.user_id, x['bug_posts']['poster']),
                        myposts))
                else:
                    myposts = list(filter(
                        lambda x: x['bug_posts']['public'] is True
                        or x['bug_posts']['poster'] == auth.user_id,
                        myposts))
            for i, p in enumerate(myposts):
                p['read'] = False if p['bug_posts']['id'] in unread_posts \
                    else True
                mycomments = []
                if p['bug_posts']['comments']:
                    mycomments = db(
                        (db.bug_post_comments.id.belongs(p['bug_posts']['comments']))
                        & (db.bug_post_comments.commenter==db.auth_user.id) &
                        ((db.bug_post_comments.deleted == False) |
                         (db.bug_post_comments.deleted == None))
                        ).select(db.bug_post_comments.id,
                                 db.bug_post_comments.commenter,
                                 db.auth_user.first_name,
                                 db.auth_user.last_name,
                                 db.bug_post_comments.commenter_role,
                                 db.bug_post_comments.dt_posted,
                                 db.bug_post_comments.on_post,
                                 db.bug_post_comments.thread_index,
                                 db.bug_post_comments.comment_body,
                                 db.bug_post_comments.public,
                                 db.bug_post_comments.hidden,
                                 db.bug_post_comments.deleted,
                                 db.bug_post_comments.flagged,
                                 db.bug_post_comments.pinned,
                                 db.bug_post_comments.popularity,
                                 db.bug_post_comments.helpfulness,
                                 db.bug_post_comments.modified_on,
                                 orderby=db.bug_post_comments.thread_index
                                 ).as_list()

                    if not auth.has_membership('administrators'):
                        if auth.has_membership('instructors'):
                            mycomments = list(filter(
                                lambda x: x['bug_post_comments']['public'] is True
                                or x['bug_post_comments']['commenter'] == auth.user_id
                                or _is_my_student(auth.user_id, x['bug_post_comments']['commenter']),
                                mycomments))
                        else:
                            mycomments = list(filter(
                                lambda x: x['bug_post_comments']['public'] is True
                                or x['bug_post_comments']['commenter'] == auth.user_id,
                                mycomments))
                    for c in mycomments:
                        c['read'] = False if c['bug_post_comments']['id'] \
                            in unread_comments else True
                myposts[i]['comments'] = mycomments
                if debug: pprint('===================================')
                if debug: pprint(mycomments)

            queries[idx]['posts'] = myposts
        else:
            queries[idx]['posts'] = []

    return queries


def _fetch_unread_queries(user_id):
    """
    Returns queries, posts, and comments for which user has unread items.

    Each is returned as a list of ids. Each list includes items themselves
    marked as unread, as well as those items with unread children.

    Expects just one required parameter:
    user_id (int)

    """
    vbs = 1
    if vbs: print("user_id:", user_id)
    db = current.db
    unread_queries = db((db.bugs_read_by_user.user_id==user_id) &
                        (db.bugs_read_by_user.read_status==False)
                        ).select(db.bugs_read_by_user.read_item_id).as_list()
    unread_posts = db((db.posts_read_by_user.user_id==user_id) &
                    (db.posts_read_by_user.read_status==False)
                    ).select(db.posts_read_by_user.read_item_id,
                            db.posts_read_by_user.read_status,
                            db.posts_read_by_user.on_bug).as_list()
    unread_comments = db((db.comments_read_by_user.user_id==user_id) &
                        (db.comments_read_by_user.read_status==False)
                        ).select(db.comments_read_by_user.read_item_id,
                                db.comments_read_by_user.read_status,
                                db.comments_read_by_user.on_bug,
                                db.comments_read_by_user.on_bug_post
                                ).as_list()
    unread_queries = [i['read_item_id'] for i in unread_queries] \
        if unread_queries else []
    unread_posts = [p['read_item_id'] for p in unread_posts] \
        if unread_posts else []
    unread_comments = [p['read_item_id'] for p in unread_comments] \
        if unread_comments else []

    return unread_queries, unread_posts, unread_comments

def get_view_queries():
    """

    Page request parameter is indexed from 1. A value of 0 indicates the request
    is not paginated.
    """
    vbs=False
    stepid = request.vars['step_id']
    userid = request.vars['user_id']
    own_queries = request.vars['own_queries']
    nonstep = request.vars['nonstep']
    unanswered = request.vars['unanswered']
    unread = request.vars['unread']
    pagesize = request.vars['pagesize']
    page = request.vars['page']
    orderby = request.vars['orderby']
    classmates_course = int(request.vars['classmates_course'])
    students_course = int(request.vars['students_course'])
    if vbs: print(request.vars)

    offset_start = pagesize * (page - 1)
    offset_end = offset_start + pagesize
    table_fields = [db.bugs.id,
                    db.bugs.user_name,
                    db.bugs.step,
                    db.bugs.in_path,
                    db.bugs.prompt,
                    db.bugs.step_options,
                    db.bugs.user_response,
                    db.bugs.sample_answers,
                    db.bugs.score,
                    db.bugs.adjusted_score,
                    db.bugs.log_id,
                    db.bugs.user_comment,
                    db.bugs.date_submitted,
                    db.bugs.bug_status,
                    db.bugs.admin_comment,
                    db.bugs.deleted,
                    db.bugs.public,
                    db.bugs.posts,
                    db.bugs.pinned,
                    db.bugs.popularity,
                    db.bugs.helpfulness,
                    db.bugs.user_role,
                    db.auth_user.id,
                    db.auth_user.first_name,
                    db.auth_user.last_name]
                    # FIXME:  re-add db.bugs.hidden here and in model,

    queries = []
    unread_queries, unread_posts, unread_comments = _fetch_unread_queries(userid)
    if vbs: print("api::_get_view_queries: unread_queries")
    if vbs: print(unread_queries)
    if vbs: print("api::_get_view_queries: unread_posts")
    if vbs: print(unread_posts)
    if vbs: print("api::_get_view_queries: unread_comments")
    if vbs: print(unread_comments)

    unanswered_term = True
    if unanswered==True:
        answered_rows = db(db.bug_posts.id > 0)._select(db.bug_posts.on_bug)
        unanswered_term = ~(db.bugs.id.belongs(answered_rows))
        if vbs: print("filtering for unanswered")
        if vbs: print("raw unanswered finds {} of {} rows".format(
            db(unanswered_term).count(),
            db(db.bugs.id > 0).count()
            ))

    if vbs: print('A')

    step_term = (db.bugs.step == stepid) # queries tied to specified step
    if nonstep==True:  # queries not tied to step
        if vbs: print("not filtering for a step")
        step_term = (db.bugs.step == None)
    elif stepid==0:  #  queries on all steps, not just one
        if vbs: print("filtering for any step")
        step_term = (db.bugs.step != None)
    else:
        if vbs: print("filtering for step", stepid)
    if vbs: print("found", db())

    if vbs: print('b')

    basic_term = ((db.bugs.user_name == db.auth_user.id) &
                 ((db.bugs.deleted == False) | (db.bugs.deleted == None)))
    if vbs: print("with basic_term found ", db((step_term) & (basic_term)).count(), "records")

    #  requesting queries not marked as read
    unread_term = True
    if unread is True:
        unread_term = (db.bugs.id.belongs(unread_queries))
    if vbs: print("with unread_term found ", db((step_term) & (basic_term) & (unread_term)).count(), "records")


    own_queries_term = (db.bugs.user_name != userid)
    if own_queries is True:
        own_queries_term = (db.bugs.user_name == userid)
    if vbs: print("with own_queries term found ", db((step_term) & (basic_term) & (unread_term) & (own_queries_term)).count(), "records")

    #  requesting queries for own class's students
    students_term = True
    if vbs: print("students_course is", students_course)
    if students_course not in [None, 0]:
        myclass = db.classes[students_course]
        assert userid == myclass.instructor
        members = list(set([m.name for m in
                            db(db.class_membership.class_section ==
                               students_course).iterselect()
                            if m.name != userid]
                            ))
        students_term = ((db.bugs.user_name.belongs(members)) &
                         (db.bugs.date_submitted >= myclass.start_date) &
                         (db.bugs.date_submitted <= myclass.end_date))
    if vbs and students_course != 0: print("with students_term found ", len(list(set(m.bugs.id for m in db((step_term) & (basic_term) & (unread_term) & (own_queries_term) & (students_term)).select()))), "records")

    #  requesting queries for own classmates
    classmates_term = True
    if vbs: print("classmates_course is", classmates_course)
    if classmates_course not in [None, 0]:
        myclass = db.classes[classmates_course]
        members = list(set([m.name for m in
                            db(db.class_membership.class_section ==
                               classmates_course).iterselect()
                            if m.name != userid]
                           ))
        # assert userid in members
        # other_members = [m for m in members if m != userid]
        classmates_term = ((db.bugs.user_name.belongs(members)) &
                           (db.bugs.date_submitted >= myclass.start_date) &
                           (db.bugs.date_submitted <= myclass.end_date))
    if vbs: print("with classmates_term found ", db((step_term) & (basic_term) & (unread_term) & (own_queries_term) & (classmates_term)).count(), "records")

    # requesting queries not by self, student, or classmates
    # FIXME: make current class?
    external_term = True
    if (not own_queries) and \
            students_course in [None, 0] and classmates_course in [None, 0]:
        class_queries = []
        myclasses = list(set(c.class_section for c in
                             db(db.class_membership.name == userid
                                ).iterselect(db.class_membership.class_section)
                             )
                         )
        if vbs: print("myclasses: ", myclasses)
        for c in myclasses:
            if vbs: print("c:")
            if vbs: print(c)
            classmembers = list(set([m.name for m in
                db(db.class_membership.class_section == c
                ).iterselect(db.class_membership.name)]
                ))
            if vbs: print("classmembers:", [m for m in classmembers])
            my_m_class = db(db.classes.id == c
                         ).select(db.classes.start_date, db.classes.end_date).first()
            # if vbs: print("myclass:")
            # if vbs: print(myclass)
            if vbs: print("myclass.start_date", my_m_class.start_date)
            if vbs: print("myclass.end_date", my_m_class.end_date)
            myqueries = [q.id for q in
                         db((db.bugs.user_name.belongs(classmembers)) &
                            (db.bugs.date_submitted >= my_m_class.start_date) &
                            (db.bugs.date_submitted <= my_m_class.end_date)
                            ).select(db.bugs.id)]
            class_queries.extend(myqueries)
            if vbs: print("class_queries:", class_queries)

        instructing_queries = []
        instructing = list(set(db(db.classes.instructor == userid
                                  ).iterselect(db.classes.id)))
        if vbs: print("instructing: ", instructing)
        for i in instructing:
            instructingmembers = list(set([m.name for m in
                db(db.class_membership.class_section == i.id
                ).iterselect(db.class_membership.name)]
                ))
            if vbs: print("instructingmembers is")
            if vbs: print(instructingmembers)
            my_i_class = db(db.classes.id == i.id
                         ).select(db.classes.start_date, db.classes.end_date).first()
            if vbs: print("myclass.start_date", my_i_class.start_date)
            if vbs: print("myclass.end_date", my_i_class.end_date)
            myqueries = [q.id for q in
                         db((db.bugs.user_name.belongs(instructingmembers)) &
                            (db.bugs.date_submitted >= my_i_class.start_date) &
                            (db.bugs.date_submitted <= my_i_class.end_date)
                            ).select(db.bugs.id)]
            if vbs: print("found", len(myqueries), "queries")
            instructing_queries.extend(myqueries)
        if vbs: print("excluding", len(class_queries), "class queries")
        if vbs: print("excluding", len(instructing_queries), "instructing queries")

        external_term = ~(db.bugs.id.belongs(chain(class_queries,
                                                   instructing_queries)))

    if vbs: print("with external_term found ", db((step_term) & (basic_term) & (unread_term) & (own_queries_term) & (classmates_term) & (external_term)).count(), "records")

    if vbs: print('c')
    queries = db((step_term) &
                 (basic_term) &
                 (unread_term) &
                 (unanswered_term) &
                 (classmates_term) &
                 (students_term) &
                 (own_queries_term) &
                 (external_term)
                 ).select(*table_fields,
                          orderby=~db.bugs[orderby],
                          limitby=(offset_start, offset_end)
                          )
    if vbs: print(queries[0] if len(queries) else "No records found")

    if vbs: print('d')
    queries_list = queries.as_list()
    if vbs: print('e')
    for q in queries_list:
        q['read'] = False if q['bugs']['id'] in unread_queries else True
    if vbs: print('f')
    if vbs: print("in _get_view_queries===============================")
    if vbs: print("got {} query rows".format(len(queries_list)))
    if vbs: print('g')
    queries_list = _add_posts_to_queries(queries_list,
                                         unread_posts, unread_comments)

    return json_serializer(queries_list)


def get_queries_metadata():
    """
    Return counts for query categories.
    """
    vbs=True
    db = current.db
    if vbs: print("api::get_queries_metadata============================")

    user_id = request.vars["user_id"]
    step_id = request.vars["step_id"]
    nonstep = request.vars["nonstep"]
    unanswered = request.vars["unanswered"]

    unread_queries, unread_posts, unread_comments = _fetch_unread_queries(user_id)
    if vbs: print("unread_queries:")
    if vbs: print(unread_queries)

    unanswered_term = True
    if unanswered==True:
        answered_rows = db(db.bug_posts.id > 0)._select(db.bug_posts.on_bug)
        unanswered_term = ~(db.bugs.id.belongs(answered_rows))

    step_term = (db.bugs.step == step_id) # queries tied to specified step
    if nonstep==True:  # queries not tied to step
        step_term = (db.bugs.step == None)
    elif step_id==0:  #  queries on all steps, not just one
        step_term = (db.bugs.step != None)

    basic_terms = ((step_term) &
                   ((db.bugs.deleted == False) | (db.bugs.deleted == None)) &
                   (unanswered_term))
    if vbs: print("basic_query:", db(basic_terms).count())
    basic_unread_terms = (basic_terms & db.bugs.id.belongs(unread_queries))
    if vbs: print("basic_unread_query:", db(basic_unread_terms).count())

    # count user's queries
    user_term = db.bugs.user_name==user_id
    user_query_count = db(basic_terms & user_term).count()
    user_unread_count = db(basic_unread_terms & user_term).count()

    # count classmates' queries
    classmates_counts = []
    classmates_query_ids = []
    myclasses = db((db.class_membership.name == user_id) &
                   (db.class_membership.class_section == db.classes.id)
                   ).iterselect(db.classes.id,
                                db.classes.institution,
                                db.classes.academic_year,
                                db.classes.course_section,
                                db.classes.start_date,
                                db.classes.end_date,
                                orderby=~db.classes.start_date
                                )
    for myclass in myclasses:
        # if vbs: pprint(myclass)
        if vbs: print("class", myclass.id)
        members = list(set([m.name for m in
                            db(db.class_membership.class_section ==
                               myclass.id).iterselect()
                            if m.name != user_id]
                            ))
        if vbs: print("members:", members)
        if vbs: print("start_date:", myclass.start_date)
        if vbs: print("end_date:", myclass.end_date)
        member_queries = list(set(
            db(basic_terms &
               db.bugs.user_name.belongs(members) &
               (db.bugs.date_submitted >= myclass.start_date) &
               (db.bugs.date_submitted <= myclass.end_date)
               ).select(db.bugs.id)
        ))
        if vbs: print("found member queries:", len(member_queries))
        member_unread = [u for u in member_queries if u.id in unread_queries]
        if member_queries:
            classmates_counts.append({'id': myclass.id,
                                      'institution': myclass.institution,
                                      'year': myclass.academic_year,
                                      'section': myclass.course_section,
                                      'queries_count': len(member_queries),
                                      'unread_count': len(member_unread)
                                      }
                                    )
            classmates_query_ids.extend([q.id for q in member_queries])
    classmates_unread_count = len(list(set(u for u in classmates_query_ids
                                         if u in unread_queries)))
    if vbs: print("classmates_query_ids length:", len(classmates_query_ids))
    if vbs: print("classmates_unread_count:", classmates_unread_count)

    # count students' queries
    students_counts = []
    students_query_ids = []
    if auth.has_membership('instructors') or \
            auth.has_membership('administrators'):
        mycourses = db(db.classes.instructor == user_id
                       ).select(orderby=~db.classes.start_date)
        # print('found {} courses'.format(len(mycourses)))
        for course in mycourses:
            if vbs: print("course", course.id)
            students = list(set(s['name'] for s in
                                db(db.class_membership.class_section == course.id
                                   ).select(db.class_membership.name)
                                ))
            # print('found {} students'.format(len(students)))
            # print(students)
            students_queries = list(set(
                db(basic_terms &
                   db.bugs.user_name.belongs(students) &
                   (db.bugs.date_submitted >= course['start_date']) &
                   (db.bugs.date_submitted <= course['end_date'])
                   ).select(db.bugs.id)
            ))
            students_query_ids.extend([q.id for q in students_queries])
            if vbs: print("found", len(students_queries), "queries for this course")
            students_unread = [s for s in students_queries
                               if s.id in unread_queries]
            # print([s['auth_user']['id'] for s in student_queries])
            # print('found {} student queries'.format(len(student_queries)))
            instructor_row = db.auth_user(course.instructor)
            instructor_name = " ".join([instructor_row['first_name'],
                                        instructor_row['last_name']])
            students_counts.append({'id': course.id,
                                    'institution': course.institution,
                                    'year': course.academic_year,
                                    'section': course.course_section,
                                    'term': course.term,
                                    'instructor': instructor_name,
                                    'queries_count': len(students_queries),
                                    'unread_count': len(students_unread)})
    students_unread_count = len(list(set(u for u in students_query_ids
                                         if u in unread_queries)))
    if vbs: print("students_query_ids length:", len(students_query_ids))
    if vbs: print(students_query_ids)
    if vbs: print("students_unread_count:", students_unread_count)

    # count others' queries
    excluded_queries = classmates_query_ids + students_query_ids
    other_term = ((db.bugs.user_name!=user_id) &
                  (~db.bugs.id.belongs(excluded_queries)))
    other_queries_count = db(basic_terms & other_term).count()
    other_unread_count = db(basic_unread_terms & other_term).count()

    return json_serializer({"user_query_count": user_query_count,
                            "user_unread_count": user_unread_count,
                            "classmates_total_count": len(list(set(classmates_query_ids))),
                            "classmates_unread_count": classmates_unread_count,
                            "classmates_counts": classmates_counts,
                            "students_total_count": len(list(set(students_query_ids))),
                            "students_unread_count": students_unread_count,
                            "students_counts": students_counts,
                            "other_queries_count": other_queries_count,
                            "other_unread_count": other_unread_count
                            })

#  FIXME: This function is deprecated
def _fetch_queries(stepid=0, userid=0, nonstep=True, unread=False,
                   unanswered=False, pagesize=20, page=0,
                   orderby="date_submitted"):
    """
    Return a list of student queries from the db.bugs table.

    If nonstep=True, this only returns general queries that aren't
    linked with a particular step.

    If unanswered=True, this only returns queries that have not yet been
    answered.

    pagination, via the "page" parameter, is zero indexed
    """
    vbs=False
    offset_start = pagesize * page
    offset_end = offset_start + pagesize
    table_fields = [db.bugs.id,
                    db.bugs.user_name,
                    db.bugs.step,
                    db.bugs.in_path,
                    db.bugs.prompt,
                    db.bugs.step_options,
                    db.bugs.user_response,
                    db.bugs.sample_answers,
                    db.bugs.score,
                    db.bugs.adjusted_score,
                    db.bugs.log_id,
                    db.bugs.user_comment,
                    db.bugs.date_submitted,
                    db.bugs.bug_status,
                    db.bugs.admin_comment,
                    db.bugs.deleted,
                    db.bugs.public,
                    db.bugs.posts,
                    db.bugs.pinned,
                    db.bugs.popularity,
                    db.bugs.helpfulness,
                    db.bugs.user_role,
                    db.auth_user.id,
                    db.auth_user.first_name,
                    db.auth_user.last_name]
                    # FIXME:  re-add db.bugs.hidden here and in model,

    queries = []
    unread_queries, unread_posts, unread_comments = _fetch_unread_queries(userid)
    if vbs: print("api::_fetch_queries: unread_queries")
    if vbs: print(unread_posts)
    if vbs: print("api::_fetch_queries: unread_posts")
    if vbs: print(unread_posts)
    if vbs: print("api::_fetch_queries: unread_queries")
    if vbs: print(unread_posts)

    unanswered_term = True
    if unanswered==True:
        answered_rows = db(db.bug_posts.id > 0)._select(db.bug_posts.on_bug)
        unanswered_term = ~(db.bugs.id.belongs(answered_rows))
        # if vbs: print("filtering for unanswered")
        # if vbs: print("raw unanswered finds {} of {} rows".format(
            # db(unanswered_term).count(),
            # db(db.bugs.id > 0).count()
            # ))

    if vbs: print('A')

    step_term = (db.bugs.step == stepid) # queries tied to specified step
    if nonstep==True:  # queries not tied to step
        step_term = (db.bugs.step == None)
    elif stepid==0:  #  queries on all steps, not just one
        step_term = (db.bugs.step != None)

    if vbs: print('b')
    #  requesting queries not marked as read
    unread_term = True
    if unread is True:
        unread_term = (db.bugs.id.belongs(unread_queries))

    if vbs: print('c')
    queries = db((step_term) &
                 (db.bugs.user_name == db.auth_user.id) &
                 ((db.bugs.deleted == False) | (db.bugs.deleted == None)) &
                 (unread_term) &
                 (unanswered_term)
                 ).select(*table_fields,
                          orderby=~db.bugs[orderby]
                          )  #   limitby=(offset_start, offset_end),

    if vbs: print('d')
    queries_list = queries.as_list()
    if vbs: print('e')
    for q in queries_list:
        q['read'] = False if q['bugs']['id'] in unread_queries else True
    if vbs: print('f')
    if vbs: print("in _fetch_queries===============================")
    if vbs: print("got {} query rows".format(len(queries_list)))
    if vbs: print('g')
    queries_recs = _add_posts_to_queries(queries_list,
                                         unread_posts, unread_comments)

    if vbs: print('h')
    #  collect queries posted by current user
    user_queries = []
    if userid and userid > 0:
        user_queries = [q for q in queries_recs
                        if q['auth_user']['id'] == userid]

    if vbs: print('i')
    #  collect queries posted by user's class members
    #  and queries posted by those outside the user's classes
    myclasses = db((db.class_membership.name == userid) &
                   (db.class_membership.class_section == db.classes.id)
                   ).iterselect(db.classes.id,
                                db.classes.institution,
                                db.classes.academic_year,
                                db.classes.course_section, orderby=~db.classes.start_date
                                )

    if vbs: print('j')
    myclasses_queries = []
    external_queries = copy(queries_recs)
    member_queries = copy(queries_recs)
    for myclass in myclasses:
        members = list(set([m.name for m in
                            db(db.class_membership.class_section ==
                               myclass.id).iterselect()
                            if m.name != userid]
                            ))

        member_queries = list(filter(lambda x: x['auth_user']['id'] in members,
                                     member_queries))
        external_queries = list(filter(lambda x: x['auth_user']['id']
                                       not in members + [userid], external_queries))
        if member_queries:
            myclasses_queries.append({'id': myclass.id,
                                      'institution': myclass.institution,
                                      'year': myclass.academic_year,
                                      'section': myclass.course_section,
                                      'queries': member_queries}
                                    )

    if vbs: print('k')

    # collect queries posted by the user's students and remove from
    # external queries as well

    mycourses_queries = []
    if auth.has_membership('instructors') or \
            auth.has_membership('administrators'):
        mycourses = db(db.classes.instructor == userid
                       ).select(orderby=~db.classes.start_date)
        # print('found {} courses'.format(len(mycourses)))
        for course in mycourses:
            students = [s['name'] for s in
                        db(db.class_membership.class_section == course.id
                           ).select(db.class_membership.name).as_list()]
            # print('found {} students'.format(len(students)))
            # print(students)
            student_queries = copy(queries_recs)
            student_queries = [s for s in student_queries
                               if s['auth_user']['id'] in students]
            # print([s['auth_user']['id'] for s in student_queries])
            # print('found {} student queries'.format(len(student_queries)))
            instructor_row = db.auth_user(course.instructor)
            instructor_name = " ".join([instructor_row['first_name'],
                                        instructor_row['last_name']])
            mycourses_queries.append({'id': course.id,
                                      'institution': course.institution,
                                      'year': course.academic_year,
                                      'section': course.course_section,
                                      'term': course.term,
                                      'instructor': instructor_name,
                                      'queries': student_queries})
            external_queries = list(filter(lambda x: x['auth_user']['id']
                                           not in students + [userid],
                                           external_queries))

    if vbs: print('l')
    #  collect queries posted by other users

    if not auth.has_membership('administrators'):
        if auth.has_membership('instructors'):

            mystudents = db((db.classes.instructor == userid) &
                            (db.classes.id == db.class_membership.class_section)
                            ).select(db.class_membership.name).as_list()
            mystudent_ids = list(set(s['name'] for s in mystudents))

            external_queries = list(filter(lambda x:
                (x['bugs']['public'] is True)
                or auth.user_id in mystudent_ids,
                external_queries))
        else:
            external_queries = list(filter(
                lambda x: x['bugs']['public'] is True,
                external_queries))

    if vbs: print('m')
    return {'user_queries': user_queries,
            'class_queries': myclasses_queries,
            'course_queries': mycourses_queries,
            'other_queries': external_queries,
            'page_start': offset_start,
            'page_end': offset_end
            }


#  FIXME: This function is deprecated
def get_queries():
    """
    API method to return queries for the selected step.
    """
    queries = _fetch_queries(request.vars['step_id'],
                             request.vars['user_id'],
                             nonstep=request.vars['nonstep'],
                             unanswered=request.vars['unanswered'],
                             unread=request.vars['unread'],
                             pagesize=request.vars['pagesize'],
                             page=request.vars['page'],
                             orderby=request.vars['orderby']
                             )
    return json_serializer(queries)


def add_query_post():
    """
    API method to add a post in an existing query discussion.

    Expected request variables:
    query_id (int) *required
    post_text (str) *required
    public (bool) *required
    """
    vbs = False

    uid = request.vars['user_id']

    if auth.is_logged_in():
        if vbs: print('api::add_query_post: vars are', request.vars)

        data = {k: v for k, v in request.vars.items()
                    if k in ['post_body', 'public']
                    }

        data['poster_role'] = []
        if auth.has_membership('administrators'):
            data['poster_role'].append('administrators')
        if auth.has_membership('instructors'):
            data['poster_role'].append('instructors')

        post_result = Bug.record_bug_post(
            uid=uid,
            bug_id=request.vars['query_id'],
            **data
            )

        # subscribe op to notices of updates/replies
        read_status_updates = _flag_conversation_change(auth.user_id, 'reply',
            op=auth.user_id, new_item_id=post_result['new_post']['id'], db=db)

        user_rec = db(db.auth_user.id==post_result['new_post']['poster']
                      ).select(db.auth_user.id,
                               db.auth_user.first_name,
                               db.auth_user.last_name
                               ).first().as_dict()
        full_rec = {'auth_user': user_rec,
                    'bug_posts': post_result['new_post'],
                    'comments': []}
        full_rec['read'] = read_status_updates['reply']['op_sub']['read_status']
        return json_serializer({'post_list': post_result['bug_post_list'],
                     'new_post': full_rec,
                     'read_status_updates': read_status_updates})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def update_query_post():
    """
    API method to update a post in an existing query discussion.

    Expects the following required request parameters:
    user_id (int)
    query_id (int)
    post_id (int)
    post_text (str)
    public (bool)
    deleted (bool)
    hidden (bool)
    """
    vbs = False

    uid = request.vars['user_id']

    if (auth.is_logged_in() and
        (auth.user_id == uid
         or auth.has_membership('administrators')
         or auth.has_membership('instructors')
         and _is_my_student(auth.user_id, auth.user_id, uid)
         )
    ):
        if vbs: print('api::update_query_post: vars are', request.vars)
        new_data = {k: v for k, v in request.vars.items()
                    if k in ['post_body', 'public', 'deleted', 'hidden',
                                'pinned', 'popularity', 'helpfulness']}
        if vbs: print('api::update_query_post: new_data')
        result = Bug.record_bug_post(
            uid=uid,
            bug_id=request.vars['query_id'],
            post_id=request.vars['post_id'],
            **new_data
            )

        if not new_data['deleted']:
            if vbs: print('api::update_query_post: flagging read status')
            read_status_updates = _flag_conversation_change(auth.user_id, 'reply',
                op=result['new_post']['poster'],
                new_item_id=result['new_post']['id'],
                db=db)

        user_rec = db(db.auth_user.id==result['new_post']['poster']
                    ).select(db.auth_user.id,
                             db.auth_user.first_name,
                             db.auth_user.last_name
                             ).first().as_dict()
        mycomments = []
        if result['new_post']['comments']:
            mycomments = db(
                (db.bug_post_comments.id.belongs(result['new_post']['comments'])) &
                (db.bug_post_comments.commenter==db.auth_user.id) &
                ((db.bug_post_comments.deleted == False) |
                (db.bug_post_comments.deleted == None))
                ).select(orderby=db.bug_post_comments.thread_index
                        ).as_list()
        full_rec = {'auth_user': user_rec,
                    'bug_posts': result['new_post'],
                    'comments': mycomments}

        if not new_data['deleted']:
            full_rec['read'] = read_status_updates['reply'
                                                   ]['op_sub']['read_status']

        return json_serializer({'post_list': result['bug_post_list'],
                     'new_post': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def add_post_comment():
    """
    """
    vbs = False

    uid = request.vars['user_id']

    if auth.is_logged_in():
        if vbs: print('api::add_post_comment: vars are', request.vars)

        data = {k: v for k, v in request.vars.items()
                if k in ['comment_body', 'public']
                }

        data['commenter_role'] = []
        if auth.has_membership('administrators'):
            data['commenter_role'].append('administrators')
        if auth.has_membership('instructors'):
            data['commenter_role'].append('instructors')

        result = Bug.record_post_comment(
            uid=uid,
            post_id=request.vars['post_id'],
            **data
            )
        db.commit()

        # add subscription and notify those subscribed to ancestors
        read_status_updates = _flag_conversation_change(auth.user_id, 'comment',
            op=auth.user_id, new_item_id=result['new_comment']['id'], db=db)


        user_rec = db(db.auth_user.id==result['new_comment']['commenter']
                      ).select(db.auth_user.id,
                               db.auth_user.first_name,
                               db.auth_user.last_name
                               ).first().as_dict()
        full_rec = {'auth_user': user_rec,
                    'bug_post_comments': result['new_comment']}
        return json_serializer({'comment_list': result['post_comment_list'],
                     'new_comment': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def update_post_comment():
    """
    API method to update a post comment in an existing query discussion.

    Expects the following request parameters:
    user_id (int)* required
    comment_id (int)* required
    post_id (int)* required
    comment_body (str)
    public (bool)
    deleted (bool)
    hidden (bool)
    pinned (bool)
    helpfulness (double)
    popularity (double)
    """
    vbs = False

    uid = request.vars['user_id']

    if (auth.is_logged_in() and
        (auth.user_id == uid
         or auth.has_membership('administrators')
         or auth.has_membership('instructors')
         and _is_my_student(auth.user_id, auth.user_id, uid)
         )
    ):
        if vbs: print('api::update_post_comment: vars are', request.vars)
        new_data = {k: v for k, v in request.vars.items()
                    if k in ['comment_body', 'public', 'deleted', 'hidden',
                             'pinned', 'popularity', 'helpfulness']}
        result = Bug.record_post_comment(
            uid=uid,
            post_id=request.vars['post_id'],
            comment_id=request.vars['comment_id'],
            **new_data
            )
        db.commit()

        # subscribe op to notices of updates/replies
        read_status_updates = _flag_conversation_change(auth.user_id, 'comment',
            op=auth.user_id, new_item_id=result['new_comment']['id'], db=db)
        if vbs: pprint(read_status_updates)

        user_rec = db(db.auth_user.id==result['new_comment']['commenter']
                      ).select(db.auth_user.id,
                               db.auth_user.first_name,
                               db.auth_user.last_name
                               ).first().as_dict()
        full_rec = {'auth_user': user_rec,
                    'bug_post_comments': result['new_comment'],
                    }
        if not new_data['deleted']:
            full_rec['read'] = read_status_updates['query'
                                                   ]['op_sub']['read_status']

        return json_serializer({'comment_list': result['post_comment_list'],
                     'new_comment': full_rec})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def log_new_query():
    """
    API method to log a new user query.

    Expected request variables:
    user_id (int)
    step_id (int)
    path_id (int)
    loc_name (str)
    answer (str)
    log_id (int)
    score (double)
    user_comment (str)
    public (bool)

    Returns a json object containing the user's updated queries for the current step (if any) or for the app in general.
    """
    vbs = False
    user_id = request.vars['user_id']
    auth = current.auth
    db = current.db

    if auth.is_logged_in():
        if vbs: print('creating::submit_bug: vars are', request.vars)
        b = Bug(step_id=request.vars['step_id'],
                path_id=request.vars['path_id'],
                loc_id=db(db.locations.loc_alias == request.vars['loc_name']
                        ).select().first().id
                )
        if vbs: print('creating::submit_bug: created bug object successfully')
        logged = b.log_new(request.vars['answer'],
                           request.vars['log_id'],
                           request.vars['score'],
                           request.vars['user_comment'],
                           request.vars['public'])
        if vbs: print('creating::submit_bug: logged bug - response is', logged)

        read_status_changes = _flag_conversation_change(user_id, 'query',
                                                        user_id,
                                                        new_item_id=logged,
                                                        db=db)

        myqueries = db((db.bugs.step == request.vars['step_id']) &
                       (db.bugs.user_name == db.auth_user.id) &
                       (db.bugs.user_name == user_id) &
                       ((db.bugs.deleted == False) |
                        (db.bugs.deleted == None))
                       ).iterselect(db.bugs.id,
                                    db.bugs.step,
                                    db.bugs.in_path,
                                    db.bugs.prompt,
                                    db.bugs.step_options,
                                    db.bugs.user_response,
                                    db.bugs.score,
                                    db.bugs.adjusted_score,
                                    db.bugs.log_id,
                                    db.bugs.user_comment,
                                    db.bugs.date_submitted,
                                    db.bugs.bug_status,
                                    db.bugs.admin_comment,
                                    # db.bugs.hidden,
                                    db.bugs.deleted,
                                    db.bugs.pinned,
                                    db.bugs.flagged,
                                    db.bugs.public,
                                    db.bugs.posts,
                                    db.auth_user.id,
                                    db.auth_user.first_name,
                                    db.auth_user.last_name
                                    ).as_list()

        unread_queries, unread_posts, unread_comments = \
            _fetch_unread_queries(user_id)
        for q in myqueries:
            q['read'] = False if q['bugs']['id'] in unread_queries else True
        myqueries = _add_posts_to_queries(myqueries,
                                          unread_posts, unread_comments)
        #  confirm that the newly logged query is in the updated list
        # assert [q for q in myqueries if q['bugs']['id'] == logged]

        return json_serializer({'status': 'success',
                                'read_status_updates': read_status_changes,
                                'queries': myqueries})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                                'reason': 'Not logged in'})


def update_query():
    """
    Api method to update one bug record.

    Expects the following required request parameters:
    query_id (int)
    public (bool)
    deleted (bool)
    hidden (bool)

    A value of None for a parameter indicates that no update is requested. A value of False is a negative boolean value to be updated.
    ...
    """
    vbs = True
    response = current.response

    user_id = request.vars['user_id']
    query_id = request.vars['query_id']
    score = request.vars['score']
    adjusted_score = request.vars['adjusted_score']
    op_id = db.bugs[query_id].user_name

    if vbs: print("administrator?", auth.has_membership('administrators'))
    if vbs: print("instructor?", auth.has_membership('instructors'))
    if vbs: print("my student?", _is_my_student(auth.user_id, op_id))

    if (auth.is_logged_in() and
        (auth.user_id == op_id
         or auth.has_membership('administrators')
         or (auth.has_membership('instructors')
             and _is_my_student(auth.user_id, op_id))
         )
    ):
        new_data = {k: v for k, v in request.vars.items()
                    if k in ['user_comment', 'public', 'deleted',
                             'pinned', 'popularity', 'helpfulness',
                             'bug_status']
                    and v is not None}
        if score is not None:
            new_data['adjusted_score'] = copy(score)

        result = Bug.update_bug(query_id, new_data)

        if result == 'false':
            response.status = 500
            return json_serializer({'status': 'internal server error',
                                    'reason': 'Could not update bug record'})
        else:
            read_status_updates = _flag_conversation_change(
                auth.user_id, 'query', op=op_id,
                edited_item_id=result['id'], db=db)

            if (int(result['bug_status']) in [1, 2, 6] and
                    score != None and
                    not (abs(result['score'] - 1) <= 0.999999999)):
                undone = trigger_bug_undo(**{k: v for k, v in result.items()
                                            if k in ['step',
                                                    'in_path',
                                                    'map_location',
                                                    'id',
                                                    'log_id',
                                                    'score',
                                                    'adjusted_score',
                                                    'bug_status',
                                                    'user_name',
                                                    'admin_comment',
                                                    'user_comment',
                                                    'user_response'
                                                    ]}
                                        )
                if vbs: pprint(undone)
            else:
                if vbs: print('not undoing anything++++++')

            user_rec = db(db.auth_user.id==result['user_name']
                        ).select(db.auth_user.id,
                                db.auth_user.first_name,
                                db.auth_user.last_name
                                ).first().as_dict()

            full_rec = {'auth_user': user_rec,
                        'bugs': result,
                        }
            unread_queries, unread_posts, unread_comments = \
                _fetch_unread_queries(user_id)
            full_rec = _add_posts_to_queries([full_rec],
                                             unread_posts, unread_comments)[0]
            full_rec['read'] = read_status_updates['query'
                                                   ]['op_sub']['read_status']
            return json_serializer({'status': 'success',
                                    'new_item': full_rec,
                                    'read_status_updates': read_status_updates})
    else:
        response = current.response
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})


def mark_read_status():
    """
    Api method to mark on user query as read for a single user.
    This can only be called by a logged-in user to mark their own
    read status.

    Expects the following required request parameters:
    user_id (int)
    query_id (int)
    read_status (bool)
    post_level (string) the level of the identified post in the
        conversation thread hierarchy. This tells us which table
        to look at to record the item's read status. Allowed
        values are 'query', 'post', and 'comment'
    """
    vbs = False
    auth = current.auth
    db = current.db
    response = current.response
    request = current.request
    user_id = request.vars['user_id']
    post_id = request.vars['post_id']
    read_status = request.vars['read_status']
    post_level = request.vars['post_level']
    db_tables = {'query': db.bugs_read_by_user,
                 'reply': db.posts_read_by_user,
                 'comment': db.comments_read_by_user}
    db_item_tables = {'query': db.bugs,
                      'reply': db.bug_posts,
                      'comment': db.bug_post_comments}
    if vbs: print('api::mark_read_status')

    def _mark_parents_read(i_post_level, i_post_id, i_user_id):
        parent_level = 'query' if i_post_level == 'reply' else 'reply'
        if vbs: print('parent_level', parent_level)
        if vbs: print(db_tables[parent_level])
        parent_item_field = 'on_bug' if i_post_level == 'reply' \
            else 'on_bug_post'
        if vbs: print('parent_item_field', parent_item_field)
        parent_item_id = db(db_tables[i_post_level].read_item_id==i_post_id).select().first().as_dict()[parent_item_field]
        if vbs: print('parent_item_id', parent_item_id)
        if vbs: print(db(
            (db_tables[parent_level].read_item_id==parent_item_id) &
            (db_tables[parent_level].user_id==i_user_id)).select().first())
        item_parent_count = db(
            (db_tables[parent_level].read_item_id==parent_item_id) &
            (db_tables[parent_level].user_id==i_user_id)
            ).update(read_status=False)
        if parent_level == 'reply':
            _mark_parents_read('reply', parent_item_id, i_user_id)

    def _mark_children_read(i_post_level, i_post_id, i_user_id):
        if vbs: print('api::mark_read_status::_mark_children_read')
        if vbs: print(i_post_level, i_post_id, i_user_id)
        child_level = 'reply' if i_post_level == 'query' else 'comment'
        parent_item_field = 'on_bug' if i_post_level == 'query' \
            else 'on_bug_post'
        item_children_count = db(
            (db_tables[child_level][parent_item_field]==i_post_id) &
            (db_tables[child_level].user_id==i_user_id)
            ).update(read_status=True)
        if vbs: print('api::mark_read_status::_mark_children_read')
        if vbs: print('item_children_count', item_children_count)
        if item_children_count > 0 and child_level=='reply':
            item_children = [r.read_item_id for r in db(
                (db_tables[child_level][parent_item_field]==i_post_id) &
                (db_tables[child_level].user_id==i_user_id)
                ).select()]
            if vbs: print('item_children', item_children)
            for i in item_children:
                _mark_children_read(child_level, i, i_user_id)

    try:
        if not auth.is_logged_in():
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                                    'reason': 'Not logged in',
                                    'error': None})
        if user_id!=auth.user_id:
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                                    'reason': 'Insufficient privileges',
                                    'error': None})
        try:
            my_item_row = db_item_tables[post_level][post_id]
            my_args = {'user_id': user_id,
                       'read_item_id': post_id,
                       'read_status': read_status
                       }
            if post_level == 'reply':
                my_args['on_bug'] = my_item_row['on_bug']
            if post_level == 'comment':
                my_args['on_bug_post'] = my_item_row['on_post']
                my_reply_row= db.bug_posts[my_item_row['on_post']]
                my_args['on_bug'] = my_reply_row['on_bug']
            db_tables[post_level].update_or_insert(
                (db_tables[post_level].user_id==user_id) &
                (db_tables[post_level].read_item_id==post_id),
                **my_args
                )
            db.commit()
            if vbs: print('read status:', read_status)
            if vbs: print('post id:', post_id)
            my_record = db((db_tables[post_level].user_id==user_id) &
                           (db_tables[post_level].read_item_id==post_id)
                           ).select().first().as_dict()
            if vbs: print('my_record:', my_record['id'])

            if post_level != 'comment' and read_status == True:
                _mark_children_read(post_level, post_id, user_id)
            if post_level != 'query' and read_status == False:
                _mark_parents_read(post_level, post_id, user_id)

            return json_serializer({'status': 'success',
                                    'result': my_record})
        except:
            response.status = 500
            return json_serializer({'status': 'internal server error',
                                    'reason': 'Unknown error in function '
                                            'mark_read_status',
                                    'error': format_exc()})
    except:
        print_exc()


def _flag_conversation_change(user_id, post_level, op=0,
                              new_item_id=0, edited_item_id=0, db=None):
    """
    Handle unread notifications when a query, post, or comment is added/updated.

    When new item is created:
    - subscribe creator to item, mark read
    - subscribe creator to parents if they're not already, mark parents read
    - subscribe creator's instructors to item, mark item unread
    - subscribe others who are subscribed to parent, mark item and parents unread

    When item is edited:
    - subscribe editor to item, mark read
    - if editor isn't op, mark as unread for op
    - mark unread for anyone subscribed to item

    """
    vbs = False
    db = current.db if not db else db
    active_item_id = new_item_id if new_item_id > 0 else edited_item_id
    if vbs: print('_flag_conversation_change: active_item_id')
    if vbs: print(active_item_id)
    if vbs: print('_flag_conversation_change: user_id')
    if vbs: print(user_id)
    if vbs: print('_flag_conversation_change: op')
    if vbs: print(op)
    db_tables = {'query': db.bugs_read_by_user,
                 'reply': db.posts_read_by_user,
                 'comment': db.comments_read_by_user}

    def _subscribe_to_children(post_level, active_item_id, return_obj):
        """
        Find children of active item and
        """
        new_subs = []
        if vbs: print('_subscribe_to_children: finding child items')
        child_level = 'comment' if post_level in ['post', 'reply'] \
            else 'reply'
        if vbs: print('_subscribe_to_children: child level')
        if vbs: print(child_level)
        this_item_field = 'on_bug' if child_level in ['post', 'reply'] \
            else 'on_bug_post'
        if child_level not in list(return_obj.keys()):
            if vbs: print('_subscribe_to_children: child level not yet processed')
            child_items = db(
                db_tables[child_level
                            ][this_item_field]==active_item_id).select()
            child_item_ids = list(set(c.read_item_id for c in child_items))
            if vbs: print('_subscribe_to_children: child_items ids')
            if vbs: print(child_item_ids)
            if child_item_ids:
                my_sub_users = [i.user_id for i in db(
                    db_tables[post_level].read_item_id==active_item_id
                    ).select(db_tables[post_level].user_id)
                    ]
                if vbs: print('_subscribe_to_children: my_sub_users')
                if vbs: print(my_sub_users)
                for u in my_sub_users:
                    for c in child_item_ids:
                        myrows = db(
                            (db_tables[child_level].read_item_id==c) &
                            (db_tables[child_level].user_id==u)
                            ).select()
                        if len(myrows)==0:
                            my_child_sub = db_tables[child_level].insert(
                                **{this_item_field: active_item_id,
                                'user_id': u,
                                'read_item_id': c,
                                'read_status': True
                                })
                            if vbs: print('_subscribe_to_children: added child sub')
                            if vbs: print('id', my_child_sub)
                            new_subs.append(my_child_sub)

                db.commit()
        return_obj[child_level] = {'others_subs': new_subs}
        return return_obj

    def _inner_handle_change(i_user_id, i_active_item_id, i_post_level,
                             return_obj={}):
        if vbs: print('_inner_handle_change: i_active_item_id')
        if vbs: print(i_active_item_id)
        if vbs: print('_inner_handle_change: i_user_id')
        if vbs: print(i_user_id)
        inner_obj = {}

        extra_fields={}
        if i_post_level=='reply':
            extra_fields={'on_bug': db.bug_posts[i_active_item_id].on_bug}
        if i_post_level=='comment':
            my_comment = db.bug_post_comments[i_active_item_id]
            my_post = db.bug_posts[my_comment['on_post']]
            extra_fields={'on_bug': my_post.on_bug,
                          'on_bug_post': my_comment['on_post']}
        if vbs: print('_inner_handle_change: extra_fields')
        if vbs: print(extra_fields)

        # subscribe op if not already subscribed, mark read
        if vbs: print('_inner_handle_change: op_sub')
        op_read_status=True if user_id==op else False
        db_tables[i_post_level].update_or_insert(
            (db_tables[i_post_level].user_id==i_user_id) &
            (db_tables[i_post_level].read_item_id==i_active_item_id),
            user_id=i_user_id,
            read_item_id=i_active_item_id,
            read_status=op_read_status,
            **extra_fields
            )
        db.commit()
        op_sub = db((db_tables[i_post_level].user_id==i_user_id) &
                    (db_tables[i_post_level].read_item_id==i_active_item_id)
                    ).select().first()
        if vbs: print(op_sub.id)
        if vbs: print(op_sub.read_status)
        inner_obj['op_sub'] = op_sub
        #  subscribe instructors of op if not already, mark unread
        instructors = _is_student_of(i_user_id)
        instructors_subs = []
        if instructors:
            for i in instructors:
                db_tables[i_post_level].update_or_insert(
                    (db_tables[i_post_level].user_id==i) &
                    (db_tables[i_post_level].read_item_id==i_active_item_id),
                    user_id=i,
                    read_item_id=i_active_item_id,
                    read_status=False,
                    **extra_fields
                    )
                if vbs: print('_inner_handle_change: instructor', i)
                read_row = db((db_tables[i_post_level].user_id==i) &
                              (db_tables[i_post_level
                                         ].read_item_id==i_active_item_id)
                              ).select().first()
                if vbs: print(read_row)
                instructors_subs.append(read_row)
                db.commit()
        inner_obj['instructors_subs'] = instructors_subs

        #  for others already subscribed, mark unread
        others_subs = db((db_tables[i_post_level
                                    ].read_item_id==i_active_item_id) &
                        (db_tables[i_post_level].user_id!=i_user_id)
                        ).update(read_status=False)
        db.commit()
        if vbs: print('_inner_handle_change: other_subs')
        if vbs: print(others_subs)
        others_subs_recs = db((db_tables[i_post_level
                                    ].read_item_id==i_active_item_id) &
                        (db_tables[i_post_level].user_id!=i_user_id)).select()
        if vbs: print([i.id for i in others_subs_recs])
        inner_obj['others_subs'] = others_subs_recs.as_list() \
            if len(others_subs_recs) > 0 else []

        #  check for parent, execute up recursively
        if i_post_level != 'query':
            i_parent_level = 'query' if i_post_level in ['post', 'reply'] \
                else 'reply'
            if vbs: print('_inner_handle_change: parent_level')
            if vbs: print(i_parent_level)
            if vbs: print('_inner_handle_change: i_post_level')
            if vbs: print(i_post_level)
            if vbs: print(db_tables[i_post_level])
            this_item = db(db_tables[i_post_level
                                     ].read_item_id==i_active_item_id
                           ).select().first()
            parent_item_id = this_item['on_bug'] if i_parent_level=='query' \
                else this_item['on_bug_post']
            if vbs: print('_inner_handle_change: parent_item_id')
            if vbs: print(parent_item_id)
            return_obj[i_post_level] = None
            return_obj = _inner_handle_change(i_user_id, parent_item_id,
                                              i_parent_level, return_obj)

        return_obj[i_post_level] = inner_obj

        return return_obj

    # recursively subscribe/set unread for self, instructors, and other subs
    return_obj = _inner_handle_change(user_id, active_item_id, post_level)

    #  check for children, subscribe (set read) anyone subscribed to this item
    if post_level != 'comment':
        return_obj = _subscribe_to_children(post_level, active_item_id,
                                            return_obj)

    # if current item is new, subscribe/set unread anyone subscribed to parent
    if new_item_id > 0 and post_level != 'query':
        if vbs: print('_flag_conversation_change: NEW ITEM')
        if vbs: print('looking for other parent subs')
        parent_level = 'query' if post_level in ['post', 'reply'] \
            else 'reply'
        this_item = db(
            db_tables[post_level].read_item_id==active_item_id
            ).select().first()
        parent_ref_field = 'on_bug' if parent_level=='query' \
            else 'on_bug_post'
        parent_item_id = this_item[parent_ref_field]
        parent_sub_users = [r.user_id for r in
            db((db_tables[parent_level].read_item_id==parent_item_id) &
               (db_tables[parent_level].user_id!=user_id)
               ).select(db_tables[parent_level].user_id)]
        for u in parent_sub_users:
            myrow = db((db_tables[post_level].read_item_id==new_item_id) &
                       (db_tables[post_level].user_id==u))
            if myrow.count() == 0:
                mydict = {'read_item_id': new_item_id,
                          'user_id': u,
                          parent_ref_field: parent_item_id,
                          'read_status': False
                          }
                if vbs: print('_flag_conversation_change: inserting new child sub')
                if post_level == 'comment':
                    mydict['on_bug'] = db_tables[parent_level
                                                 ][parent_item_id].on_bug
                if vbs: print(mydict)
                newsub = db_tables[post_level].insert(**mydict)
                if vbs: print('inserted', db_tables[post_level], newsub)
                return_obj[post_level]['others_subs'].append(newsub)
        db.commit()

    return return_obj


def get_vocabulary():
    """
    Api method to return the full vocabulary list.

    Expects an optional request variable "vocab_scope_selector"

    Returns a dictionary with the following keys:

    total_count :: int :: total_count
    mylemmas :: list :: each item represents a vocabulary entry, with joined
                        db data from "lemmas" and "tags" tables
    mylevel :: int :: the maximum badge set currently reached by user if
                      logged in
    """
    debug = 0
    db = current.db

    mynorm = GreekNormalizer()
    mylemmas = []
    for l in db(db.lemmas.first_tag == db.tags.id
                ).iterselect(orderby=db.tags.tag_position):
        inflected_fields = [l['lemmas'][n] if l['lemmas'][n] is not None
                            else " " for n in
                            ['real_stem',
                            'genitive_singular',
                            'future',
                            'aorist_active',
                            'perfect_active',
                            'aorist_passive',
                            'perfect_passive',
                            'other_irregular']]
        # if debug: print(inflected_fields)
        inflected_forms_string = ' '.join(inflected_fields)
        normalized_inflected_string = mynorm.normalize(inflected_forms_string)

        myrow = {'id': l['lemmas']['id'],
                 'accented_lemma': l['lemmas']['lemma'],
                 'normalized_lemma': mynorm.normalize(l['lemmas']['lemma']),
                 'normalized_other_forms': normalized_inflected_string,
                 'part_of_speech': l['lemmas']['part_of_speech'],
                 'glosses': l['lemmas']['glosses'],
                 'times_in_nt': l['lemmas']['times_in_nt'],
                 'set_introduced': l['tags']['tag_position'],
                 'videos': [(t.lesson_position, t.title, t.video_url) for t in
                            db(db.lessons.lesson_tags.contains(l['tags']['id'])
                               ).select()],
                 'thematic_pattern': l['lemmas']['thematic_pattern'],
                 'real_stem': l['lemmas']['real_stem'],
                 'genitive_singular': l['lemmas']['genitive_singular'],
                 'future': l['lemmas']['future'],
                 'aorist_active': l['lemmas']['aorist_active'],
                 'perfect_active': l['lemmas']['perfect_active'],
                 'aorist_passive': l['lemmas']['aorist_passive'],
                 'perfect_passive': l['lemmas']['perfect_passive'],
                 'other_irregular': l['lemmas']['other_irregular'],
                 }
        mylemmas.append(myrow)

    return json_serializer({'total_count': len(mylemmas),
                 'mylemmas': mylemmas})


def get_lessons():
    """
    Api method to fetch information on the video lessons and associated pdfs.

    Doesn't expect any parameters or arguments, and always returns the same
    data unless the database information has changed.

    """
    lessons = db(db.lessons.active == True
                 ).select(orderby=db.lessons.lesson_position
                          ).as_list()
    for l in lessons:
        mybadges = db(db.badges.tag.belongs(l['lesson_tags'])).select()
        l['badges'] = mybadges.as_list()

    return json_serializer(lessons)


def set_review_mode():
    """
    Api method to set the user's review mode.

    Expects one argument: "review_set"
    """
    session = current.session
    try:
        myset = int(request.vars['review_set'])
    except (ValueError, TypeError):  # if passed a non-numeric value
        myset = None
    session.set_review = myset

    return json_serializer({'review_set': session.set_review})


def get_profile_info():
    """
    Api method to fetch a user's performance record.

    One optional request parameter "user" expects an integer identifying the
    user whose information is requested. If this parameter is not provided, the
    request defaults to the logged in user.

    Returns a json object with the following keys:
            answer_counts(list):        List of counts of right and wrong
                                            answers for each active day
            badge_levels(dict):         Dictionary with badge levels (int) as
                                            keys and a list of badge names (or
                                            tag: int) as each value.
            badge_set_dict():           badge_set_dict,
            badge_set_milestones(list): List of 'upgrades' of the highest badge
                                            set and their dates
            badge_table_data(list):     A list of dictionaries with info on
                                            user badge progress (from
                                            Stats.active_tags)
            cal(html helper obj):       html calendar with user path stats
                                            (from Stats.monthcal)
            chart1_data(dict):          dictionary of data to build stats chart
                                            in view (from get_chart1_data)
            class_info:                 dict of course information if user is
                                            currently enrolled in a course
            days_per_week(int):         number of active days per week required
                                        for user in course
            email(str):                 User's email
            max_set(int):               Furthest badge set reached to date by
                                            user (from Stats.max)
            other_class_info(dict):     Information about the user's other
                                        classes with the keys "prior_classes"
                                        and "latter_classes". Each of these
                                        contains a list of objects, each
                                        representing data on one class
            paths_per_day(int):         number of paths per day required for
                                        user for the current course.
            reviewing_set():            session.set_review
            starting_set(int):          badge set at which the user began
                                            his/her current course section
            the_name (dict):            User's name from auth.user as
                                        dictionary with 'last_name',
                                        'first_name', and a 'namestring'
                                        formatted first, last
            tz(str):                    User's time zone from auth.user
                                            (extended in db.py)
            user_id(int):               The requested user's id.
    """
    debug = 0
    db = current.db
    auth = current.auth
    session = current.session
    response = current.response

    mystudents = db((db.classes.instructor == auth.user_id) &
                    (db.classes.id == db.class_membership.class_section)
                    ).select(db.class_membership.name).as_list()


    if not auth.is_logged_in():
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                     'reason': 'Not logged in'})

    try:
        now = datetime.now(timezone.utc)
        # Allow passing explicit user but default to current user
        if 'userId' in request.vars.keys():
            sid = request.vars['userId']
            # only allow viewing if admin or student's instructor
            if (auth.user_id == sid
                or auth.has_membership('administrators')
                or (auth.has_membership('instructors') and
                    _is_my_student(auth.user_id, sid))):
                user = db.auth_user[sid]
            else:
                response.status = 401
                return json_serializer({'status': 'unauthorized',
                             'reason': 'Insufficient privileges'})
        else:
            user = db.auth_user[auth.user_id]
        # Return proper response code if no user with requested id
        if not user:
            response.status = 404
            return json_serializer({'status': 'not found',
                                    'reason': 'No matching record found'})

        stats = Stats(user.id)

        # get user's current course
        if debug: print('getting current course')
        myc = _fetch_current_coursedata(user.id, datetime.now(timezone.utc))
        myc_id = myc['classes']['id'] if 'classes' in myc else 0
        myc_other = _fetch_other_coursedata(user.id, myc_id,
                                            datetime.now(timezone.utc))
        if debug: print('myc=============')
        if debug: print(myc)
        if myc['class_info']:
            starting_set = myc['class_info']['starting_set']
        # FIXME: UserProvider should be updated here with class info if new

        # tab1

        if debug: print('getting user data')
        name = stats.get_name()
        tz = user.time_zone
        email = user.email
        if debug: print('getting max set')
        max_set = stats.get_max()
        if debug: print('getting badge_levels')
        badge_levels = stats.get_badge_levels()
        if debug: print('getting active_tags')
        badge_table_data = stats.active_tags()  # FIXME: 29Mi of memory use

        # tab2
        if debug: print('getting monthcal')
        mycal = stats.monthcal()
        # badges_tested_over_time = stats.badges_tested_over_time(badge_table_data)
        # sets_tested_over_time = stats.sets_tested_over_time(badge_table_data)
        # steps_most_wrong = stats.steps_most_wrong(badge_table_data)

        # tab5
        if debug: print('getting chart1_data')
        mydata = get_chart1_data(user_id=user.id)
        chart1_data = mydata['chart1_data']  # FIXME: 3Mi of memory use
        if debug: print('getting milestones')
        badge_set_milestones = mydata['badge_set_milestones']
        if debug: print('getting answer_counts')
        answer_counts = mydata['answer_counts']
        if debug: print('getting badge_set_dict')
        badge_set_dict = {}
        set_list_rows = db().select(db.tags.tag_position, distinct=True)
        set_list = sorted([row.tag_position for row in set_list_rows
                        if row.tag_position < 90])
        all_tags = db((db.tags.id > 0) &
                    (db.badges.tag == db.tags.id)
                    ).select()
        for myset in set_list:
            set_tags = all_tags.find(lambda r: r.tags.tag_position == myset)
            set_tags_info = [{'tag': r.tags.id,
                              'badge_title': r.badges.badge_name}
                             for r in set_tags]
            badge_set_dict[myset] = set_tags_info
    except Exception:
        print(format_exc(5))
        response.status = 500
        return json_serializer({'status': 'internal server error',
                                'reason': 'Unknown error in function get_profile_info',
                                'error': format_exc()})

    return json_serializer({'the_name': name,
            'user_id': user.id,
            'tz': tz,
            'email': email,
            'paths_per_day': myc['daily_quota'] if myc else None,
            'days_per_week': myc['weekly_quota'] if myc else None,
            'starting_set': myc['class_info']['starting_set']
                if myc['class_info'] else None,
            'cal': mycal,
            'max_set': max_set,
            'badge_levels': badge_levels,
            'badge_table_data': badge_table_data,
            'badge_set_milestones': badge_set_milestones,
            'answer_counts': answer_counts,
            'chart1_data': chart1_data,
            'reviewing_set': session.set_review,
            'badge_set_dict': badge_set_dict,
            'class_info': myc['class_info'] if myc['class_info'] else None,
            'other_class_info': myc_other
            },
            default=my_custom_json)


def get_calendar_month():
    """
    api method to fetch user attempt data for one calendar month

    Expects the request variables "user_id", "year", "month"
    - month is 0-based integer and year is a 4-digit year

    Returns a json object with the keys
    ::year
    ::month
    ::data

    """
    stats = Stats(request.vars.userId)
    calendar = stats.monthcal(year=request.vars.year,
                              month=request.vars.month)
    return json_serializer(calendar, default=my_custom_json)


def update_course_membership_data():
    pass


def update_student_data():
    """
    Update a db record in the "course_memberships" table.

    Ignores fields with values of None, "null", or "undefined" UNLESS only one
    field is passed. Then the method assumes we're updating a single field and
    this could include clearing its value.

    Private api method to handle calls from the react front-end. This method does not add or remove students from a course. That information must be updated separately with the update_course_membership_data method.

    Expects URL variables:
        name (int reference auth_user)
        custom_start (str)
        custom_end (str)
        custom_a_cap (int)
        custom_b_cap (int)
        custom_c_cap (int)
        custom_d_cap (int)
        class_section (int reference classes)
    """
    debug = 0
    response = current.response
    mydata = {k: v for k, v in request.vars.items()
              if k not in ["name", "class_section"]}
    course_id = request.vars.class_section
    uid = request.vars.name
    if debug: print("api::update_student_data::course_id:", course_id)
    if debug: print("api::update_student_data::mydata:")
    if debug: print(mydata)

    try:
        try:
            # print('updating course', request.vars.course_id)
            member_rec = db(
                (db.class_membership.name==uid) &
                (db.class_membership.class_section==course_id)
                ).select().first()

            if (len(mydata)==1) and (
                    list(mydata.values())[0] in [None, "undefined", "null"]):
                update_data = mydata
                if list(update_data.values())[0] in ["undefined", "null"]:
                    update_data = {k: None for k, v in update_data.items()}
            else:
                update_data = {k: v for k, v in mydata.items() if k in
                    ["custom_start", "custom_end", "custom_a_cap",
                    "custom_b_cap", "custom_c_cap", "custom_d_cap"
                    ] and v not in ["undefined", "null", None]
                    }
            if len(update_data.keys()) == 0:
                response.status = 200
                return json_serializer({'status': 'success',
                            'reason': 'no update data',
                            'error': format_exc()})

            update_data['modified_on'] = datetime.now(timezone.utc)

            if "custom_start" in update_data.keys() \
                    and update_data["custom_start"] is not None:
                update_data['custom_start'] = dateutil.parser.parse(
                    update_data['custom_start'])
            if "custom_end" in update_data.keys() \
                    and update_data["custom_end"] is not None:
                update_data['custom_end'] = dateutil.parser.parse(
                    update_data['custom_end'])

            # print('old data:')
            # print(course_rec)
        except AttributeError:
            print(format_exc(5))
            response.status = 404
            return json_serializer({'status': 'No such record'})

        if not auth.is_logged_in():
            response.status = 401
            return json_serializer({'status': 'Not logged in'})

        instructor = db.classes(course_id).instructor
        if not (auth.has_membership('administrators') or
                (auth.has_membership('instructors') and
                instructor == auth.user_id)
                ):
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Insufficient privileges'})

        if debug: print('api::update_student_data: member_rec:')
        if debug: print(member_rec)
        if debug: print('api::update_student_data: update_data:')
        if debug: print(update_data)
        myresult = member_rec.update_record(**update_data)
        if debug: print('api::update_student_data: myresult:')
        if debug: print(myresult)
        if not myresult:
            raise ValueError("Class membership record was not updated")
        db.commit()

    except Exception:
        print_exc()
        response.status = 500
        return json_serializer({'status': 'internal server error',
                    'reason': 'Unknown error in function update_student_data',
                    'error': format_exc()})

    return json_serializer({"status": 'success',
                            "updated_record": myresult}, default=my_custom_json)

def promote_user():
    debug = 0
    if debug: print("in api::promote_user ----------------------------")
    uid = request.vars.uid
    if debug: print("uid:", uid)
    classid = request.vars.classid
    if debug: print("classid:", classid)
    db = current.db
    auth = current.auth
    try:
        if (uid in ["undefined", "none", None, "null", 0, "0"]) or \
                (classid in ["undefined", "none", None, "null", 0, "0"]):
            response.status = 400
            return json_serializer({'status': 'bad request',
                                    'reason': 'Missing request data'})

        tp_rec = db(db.tag_progress.name==uid).select()

        if not len(tp_rec) > 0:
            response.status = 404
            return json_serializer({'status': 'not found',
                                    'reason': 'No such user progress record'})

        if not auth.is_logged_in():
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                                    'reason': 'Not logged in'})

        instructor = db.classes(classid).instructor
        if not (auth.has_membership('administrators') or
                (auth.has_membership('instructors') and
                instructor == auth.user_id)
                ):
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Insufficient privileges'})

        myresult = do_user_promotion(uid=uid, classid=classid)

    except Exception:
        print_exc()
        response.status = 500
        return json_serializer({'status': 'internal server error',
                    'reason': 'Unknown error in function promote_user',
                    'error': format_exc()})

    return json_serializer({"status": 'success',
                            "updated_record": myresult}, default=my_custom_json)

def demote_user():
    debug = 0
    if debug: print("in api::demote_user ----------------------------")
    uid = request.vars.uid
    if debug: print("uid:", uid)
    classid = request.vars.classid
    if debug: print("classid:", classid)
    db = current.db
    auth = current.auth
    try:
        if (uid in ["undefined", "none", None, "null", 0, "0"]) or \
                (classid in ["undefined", "none", None, "null", 0, "0"]):
            response.status = 400
            return json_serializer({'status': 'bad request',
                                    'reason': 'Missing request data'})

        tp_rec = db(db.tag_progress.name==uid).select()

        if not len(tp_rec) > 0:
            response.status = 404
            return json_serializer({'status': 'not found',
                                    'reason': 'No such user progress record'})

        if not auth.is_logged_in():
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                                    'reason': 'Not logged in'})

        instructor = db.classes(classid).instructor
        if not (auth.has_membership('administrators') or
                (auth.has_membership('instructors') and
                instructor == auth.user_id)
                ):
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Insufficient privileges'})

        myresult = do_user_demotion(uid=uid, classid=classid)

    except Exception:
        print_exc()
        response.status = 500
        return json_serializer({'status': 'internal server error',
                    'reason': 'Unknown error in function demote_user',
                    'error': format_exc()})

    return json_serializer({"status": 'success',
                            "updated_record": myresult}, default=my_custom_json)


def update_course_data():
    """
    Update a db record in the "classes" table.

    Ignores fields with values of None, "null", or "undefined" UNLESS only one
    field is passed. Then the method assumes we're updating a single field and
    this could include clearing its value.

    Private api method to handle calls from the react front-end. This method does not handle data on student membership in a course. That information must be updated separately with the update_course_membership_data method.

    Expects URL variables:
        id (int)
        institution (str)
        academic_year (int)
        term (str)
        course_section (str)
        instructor (int [reference auth_user])
        start_date (str [datetime])
        end_date (str [datetime])
        paths_per_day (int)
        days_per_week (int)
        a_target (int)
        a_cap (int)
        b_target (int)
        b_cap (int)
        c_target (int)
        c_cap (int)
        d_target (int)
        d_cap (int)
        f_target (int)

    """
    debug = 0
    response = current.response
    mydata = request.vars
    mydata['modified_on'] = datetime.now(timezone.utc)
    course_id = request.vars.id
    if debug: print("api::update_course_data::course_id:", course_id)
    if debug: print("api::update_course_data::mydata:")
    if debug: print(mydata)

    try:
        try:
            # print('updating course', request.vars.course_id)
            course_rec = db.classes(course_id)

            if (len(mydata)==1) and (
                    list(mydata.values())[0] in [None, "undefined", "null"]):
                update_data = mydata
                if list(update_data.values())[0] in ["undefined", "null"]:
                    update_data = {k: None for k, v in update_data.items()}
            else:
                update_data = {k: v for k, v in mydata.items() if k in
                    ["institution", "academic_year", "term", "course_section",
                    "instructor", "start_date", "end_date", "paths_per_day",
                    "days_per_week", "a_target", "a_cap", "b_target", "b_cap",
                    "c_target", "c_cap", "d_target", "d_cap", "f_target"
                    ] and v not in ["undefined", "null", None]
                    }
            if "start_date" in update_data.keys():
                update_data['start_date'] = dateutil.parser.parse(
                    update_data['start_date'])
            if "end_date" in update_data.keys():
                update_data['end_date'] = dateutil.parser.parse(
                    update_data['end_date'])

            if debug: print('api::update_course_data: received start_date:',
                            update_data['start_date'])
            if debug: print(type(update_data['start_date']))
            # print('old data:')
            # print(course_rec)
        except AttributeError:
            print(format_exc(5))
            response.status = 404
            return json_serializer({'status': 'not found',
                                    'reason': 'No such record'})

        if not auth.is_logged_in():
            response.status = 401
            return json_serializer({'status': 'unauthorized',
                                    'reason': 'Not logged in'})

        if not (auth.has_membership('administrators') or
                (auth.has_membership('instructors') and
                course_rec['instructor'] == auth.user_id)
                ):
            response.status = 403
            return json_serializer({'status': 'forbidden',
                                    'reason': 'Insufficient privileges'})

        if debug: print('api::update_course_data: course_rec:')
        if debug: print(course_rec)
        if debug: print('api::update_course_data: update_data:')
        if debug: print(update_data)
        myresult = course_rec.update_record(**update_data)
        if debug: print('api::update_course_data: myresult:')
        if debug: print(myresult)
        if not myresult:
            raise ValueError("Course record was not updated")
        db.commit()

    except Exception:
        print_exc()
        response.status = 500
        return json_serializer({'status': 'internal server error',
                    'reason': 'Unknown error in function update_course_data',
                    'error': format_exc()})

    return json_serializer({"status": 'success',
                            "updated_record": myresult}, default=my_custom_json)


def get_course_data():
    """
    Return the data on a single course and its students.

    Private api method to handle calls from the react front-end.

    Expects url variables:
        course_id (int)

    Returns:
        JSON object with the following keys:
            institution
            academic_year
            term
            course_section
            instructor
            start_date
            end_date
            paths_per_day
            days_per_week
            a_target
            a_cap
            b_target
            b_cap
            c_target
            c_cap
            d_target
            d_cap
            f_target
            class_key
            members
        members is an array of objects which each have the following keys:
            uid
            first_name
            last_name
            progress
            counts (list): [days active this week, days met target this week,
                             days active last week, days met target last week]
            current_set (int):
            custom_a_cap (int):
            custom_b_cap (int):
            custom_c_cap
            custom_d_cap
            custom_end
            custom_start
            end_date
            ending_set
            final_grade: []
            grade
            previous_end_date
            start_date
            starting_set
            tp_id: 585
            custom_start
            starting_set
            custom_end
    """
    debug = 0
    auth = current.auth
    session = current.session
    response = current.response
    db = current.db
    try:
        if debug: print('getting course', request.vars.course_id)
        course_rec = db.classes(request.vars.course_id)
    except AttributeError:
        print(format_exc(5))
        response.status = 404
        return json_serializer({'status': 'not found',
                                'reason': 'No such class record'})

    if not auth.is_logged_in():
        response.status = 401
        return json_serializer({'status': 'unauthorized',
                                'reason': 'Not logged in'})

    if not (auth.has_membership('administrators') or
            (auth.has_membership('instructors') and
            course_rec['instructor'] == auth.user_id)
            ):
        response.status = 403
        return json_serializer({'status': 'forbidden',
                     'reason': 'Insufficient privileges'})

    mycourse = {k: v for k, v in course_rec.items() if k in [
                'id',
                'institution', 'academic_year', 'term',
                'course_section',
                'start_date', 'end_date',
                'paths_per_day', 'days_per_week',
                'a_target', 'a_cap',
                'b_target', 'b_cap',
                'c_target', 'c_cap',
                'd_target', 'd_cap',
                'f_target'
                ]}
    mycourse['in_process'] = True if \
        course_rec['end_date'].replace(tzinfo=pytz.UTC) > datetime.now(timezone.utc) else False
    instructor_row = db((db.classes.instructor==course_rec['instructor']) &
                        (db.classes.instructor==db.auth_user.id)
                        ).select().first()
    mycourse['instructor'] = {"id": instructor_row.classes.instructor,
                              "first_name": instructor_row.auth_user.first_name,
                              "last_name": instructor_row.auth_user.last_name}

    expiration_dt = datetime.now(timezone.utc) - timedelta(days=30)
    mycourse_key_row = db((db.class_keys.class_section==mycourse['id']) &
                          (db.class_keys.created_date >= expiration_dt) &
                          (db.class_keys.cancelled==False)
                          ).select().first()
    if not mycourse_key_row:
        mycourse_key_row = db.class_keys.insert(class_section=mycourse['id'])
    mycourse['class_key'] = mycourse_key_row.class_key

    memberships = db(db.class_membership.class_section ==
                    course_rec['id']).select()
    users = db((db.auth_user.id == db.tag_progress.name) &
                (db.auth_user.id.belongs([m['name'] for m in memberships]))
                ).select(orderby=db.auth_user.last_name)
    if debug: print('course_rec======================')
    if debug: print(course_rec)
    if debug: print(type(course_rec))
    classlist = make_classlist(memberships, users, course_rec['start_date'],
                                course_rec['end_date'], course_rec['paths_per_day'], course_rec)

    members = [{'first_name': m.auth_user.first_name,
                'last_name': m.auth_user.last_name,
                'custom_start': m.class_membership.custom_start,
                'starting_set': m.class_membership.starting_set,
                'custom_end': m.class_membership.custom_end,
                'ending_set': m.class_membership.ending_set,
                'custom_a_cap': m.class_membership.custom_a_cap,
                'custom_b_cap': m.class_membership.custom_b_cap,
                'custom_c_cap': m.class_membership.custom_c_cap,
                'custom_d_cap': m.class_membership.custom_d_cap,
                'final_grade': m.class_membership.final_grade}
        for m in
        db((db.class_membership.class_section==mycourse['id']) &
           (db.class_membership.name==db.auth_user.id)
           ).iterselect()
    ]

    mycourse['members'] = classlist


    return json_serializer(mycourse, default=my_custom_json)


def _is_my_student(user, student):
    """
    Return a boolean indicating if student is in a class taught by user
    """
    mystudents = db((db.classes.instructor == user) &
                    (db.classes.id == db.class_membership.class_section)
                    ).select(db.class_membership.name).as_list()
    mystudent_ids = list(set(s['name'] for s in mystudents))
    return True if student in mystudent_ids else False


def _is_student_of(user_id):
    """
    Return list of ids for users who are instructors for the given user.
    """
    instructors = db((db.class_membership.name==user_id) &
                     (db.class_membership.class_section==db.classes.id)
                     ).select(db.classes.instructor).as_list()
    instructors_flat = [c['instructor'] for c in instructors] \
        if instructors else []

    return instructors_flat

