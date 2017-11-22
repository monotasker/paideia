# coding: utf8
from paideia import Walk, Map
from ast import literal_eval
# from applications.paideia.modules.paideia_utils import simple_obj_print


if 0:
    from gluon import current, SQLFORM, Field, URL, redirect
    session = current.session
    response = current.response
    auth = current.auth
    db = current.db

"""
These controller functions handle user-interactions for the game proper. It
does not cover any admin actions, content creation, or retrieval and
display of student performance statistics.

Wherever possible, business logic is kept out of these controllers and is
provided by classes in modules/paideia. Controllers access
that logic through two public methods:

- paideia.Walk.map
- paideia.Walk.start

The controller functions interact with these views:
- exploring/index.html (frame for the game ui)
- exploring/walk.load (main game ui)
- exploring/patherror.load (error screen)
- exploring/calendar.load (ajax calendar widget)

Errors are sent (by routes.py) to default/oops
"""


@auth.requires_login()
def index():
    """
    Present the frame for the game interface, which will then load via ajax
    using the walk() controller below. Preparation of the necessary session
    variables has now been moved to Walk.__init__ and doesn't need to happen
    here.

    :Permissions: user must be logged in.
    """
    request = current.request
    debug = 0
    if debug:
        print 'getting index'
        print 'vars', request.vars
        print 'args', request.args
    response.files.append(URL('static', 'js/jquery.jplayer.min.js'))
    response.files.append(URL('static', 'js/play_audio_clip.js'))
    response.files.append(URL('static', 'css/jplayer.pink.flag.css'))
    response.files.append(URL('static', 'js/svg-pan-zoom.min.js'))
    # to add panning and zooming to svg map
    response.files.append(URL('static', version_file('js/exploring.js')))
    return {}


@auth.requires_login()
def walk():
    """
    Present the various stages of the game ui and handle user responses.

    This is the main function for presenting various states of the game
    user interface. These states are determined by the first url argument.
    The states are:

    - map (default; present navigation map)
    - step (Present prompt to begin a step OR evaluate user response and
        present the appropriate feedback and further navigation options.)
    - error

    The 'step' state elicits two different behaviours from the
    paideia module, depending on whether the web2py request object includes a
    submitted user response.
    - no: begin a step (choose appropriate path/step and retrieve prompt)
    - yes: evaluate the user's reply to the previous step prompt

    This function is intended to be accessed only via ajax, so its only view
    is exploring/walk.load. This view should be presented in the #page
    element of exploring/index.html.
    """
    debug = 0
    request = current.request

    if debug:
        print "\n\nstarting walk controller================================"
    rvars = request.vars
    rargs = request.args
    # print "in controller.walk:"
    # print "args:", request.args
    # print "vars:", request.vars
    # simple_obj_print(request.body.read(), "request body:")
    # simple_obj_print(request, "request:")
    # simple_obj_print(request.vars, "request.vars:")
    # simple_obj_print(request.args, "request.args:")

    # form for testing paths; returned and embedded in view
    testform = SQLFORM.factory(Field('path', 'integer'),
                               Field('location', 'reference locations'),
                               Field('blocks'),
                               Field('new_user', 'boolean'),
                               )
    if testform.process().accepted:
        redirect(URL('exploring', 'walk.load', args=['ask'],
                     vars=request.vars))
    elif testform.errors:
        response.flash = 'Form had errors'
        print testform.errors

    if debug:
        print "controller.walk: Auth.user_id is", auth.user_id
        print "controller.walk: first_name is", \
            db.auth_user(auth.user_id).first_name
    # When user begins exploring (also default) present map
    if (not rargs) or (rargs[0] == 'map'):
        print "controller.walk: getting map"
        return {'map': Map().show(),
                'form': testform}
    elif rargs[0] == 'repeat' and 'response' not in rvars.keys():
        print "controller.walk: setting repeat signal"
        stepargs = {'repeat': True}
    else:
        print "controller.walk: setting response string", rvars['response']
        stepargs = {}
        # if condition prevents submission of blank response
        stepargs['response_string'] = rvars['response'] if \
            ('response' in rvars and 'response' not in [' ', None]) else None
    if session.set_review:
        stepargs['set_review'] = session.set_review

    # pass along test settings to Walk.ask()
    if debug:
        print '----------------args & vars------------'
        print 'vars:'
        for x in rvars:
            print {x: rvars[x]}
        print 'args:'
        for x in rargs:
            print x
        # print 'cookies'
        # for x in request.cookies: print {x : request.cookies[x].value}
        print '------------end args & vars------------'
    if ('blocks' in rvars) and \
            not (rvars['blocks'] in ['', None, 'undefined']):
        stepargs['set_blocks'] = literal_eval(rvars['blocks'])
        if debug:
            print {'----------blocks passed------------': rvars['blocks']}
    if 'path' in rvars and not (rvars['path'] in ['', None, 'undefined']):
        stepargs['path'] = rvars['path']
    # JOB ... oct 18, 2014 ... bug step id
    if 'pre_bug_step_id' in rvars and \
            not (rvars['pre_bug_step_id'] in ['', None, 'undefined']):
        stepargs['pre_bug_step_id'] = rvars['pre_bug_step_id']

    if not request.vars.loc:  # TODO: Does this do anything?
        request.vars.loc = None

    # variables for Walk init
    new_user = False
    if 'new_user' in request.vars and request.vars.new_user == 'on':
        print 'forcing new user'
        new_user is True

    resp = Walk(new_user=new_user).start(request.vars.loc,
                                         **stepargs)
    if 'bmodal' not in resp.keys():
        resp['bmodal'] = ''
    resp['form'] = testform

    return resp
