# coding: utf8
from paideia_exploring import Walk
from paideia_stats import Stats
from itertools import chain

if 0:
    from gluon import current, A, URL
    request = current.request
    session = current.session
    response = current.response
    auth = current.auth
    db = current.db

"""
These controller functions handle user-interactions for the game proper. It
does not cover any back-end actions, content creation, or retrieval and
display of student performance statistics.

Wherever possible, business logic is kept out of these controllers and are
provided by classes in the module paideia_exploring. Controllers access
that logic through a very small set of public methods:

- Walk.next_step
- Step.ask (accessed via the Step stored in the Walk object: Walk.step.ask)
- Step.process

The controller functions interact with these views:
- exploring/index.html (frame for the game ui)
- exploring/walk.load (main game ui)
- exploring/patherror.load (error screen)
- exploring/calendar.load (ajax calendar widget)
"""


def patherror():
    """
    Present a message informing the user of an error and logging error info.

    ***TODO: This function is from the old app and depends on db tables and
    session variables that may have changed. It is also not actually called
    yet from any game logic, since I haven't re-implemented any error
    handling.

    :Implemented in:
    none
    """

    if request.args[1] == 'unknown':
        db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
        #TODO: fix problem with changing column name for status
    if request.args[1] == 'regex':
        db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)

    message = """Oops! Something about that question confused me, and I'm not
    sure whether your answer was right. Let's try another one."""
    button = A('continue', _href=URL('index', args=['ask']),
        _class='button-green-grad next_q', cid=request.cid)
    #don't include this question in counting the number attempted
    session.q_counter -= 1

    return dict(message=message, button=button)



@auth.requires_membership('administrators')
def set_value():
    """
    Update specified values programmatically on several rows of a db table.

    This is another utility function that probably belongs in the util
    controller. I just re-write the code below on an ad hoc basis, but
    I should really set it up to take parameters.

    :returns: no return value

    **TODO: return the result instead of just
    printing to stdout.
    """
    pass


@auth.requires_login()
def index():
    """
    Present the frame for the game interface, which will then load via ajax
    using the walk() controller below. Preparation of the necessary session
    variables has now been moved to Walk.__init__ and doesn't need to happen
    here.

    :Permissions: user must be logged in.
    """
    return {}


def walk():
    """
    Present the various stages of the game ui and handle user responses.

    This is the main function for presenting various states of the game
    user interface. These states are determined by the first url argument.
    The states are:

    - start (default; present navigation map)
    - ask (Present prompt to begin a step OR evaluate user response and
        present the appropriate feedback and further navigation options.)
    - error

    The 'ask' state actually involves two sets of behaviours, depending on
    whether the web2py request object includes a submitted user response. If
    it does not, the 'ask' state selects an appropriate path and step and
    presents the step prompt.

    This function is intended to be accessed only via ajax, so its only view
    is exploring/walk.load. This view should be presented in the #page
    element of exploring/index.html.
    """
    debug = True

    if debug: print '\n\nStarting controller exploring.walk()'
    print 'request.vars:', request.vars
    if request.vars and request.vars['force'] == 'True':
        print 'forcing new session'
        walk = Walk(True)
    else:
        walk = Walk()

    # When user begins exploring (also default) present map
    if (request.args(0) == 'start') or (not request.args):

        if debug: print '\ncontroller exploring.walk() state: start'
        # TODO: change to a new public method Walk.set_active_location()
        walk.active_location = None  # clear in preparation for new location
        session.walk['active_location'] = None

        return {'map': walk.map}

    # After user submits response to step prompt
    # Evaluate response and present feedback via npc reply
    elif ('response' in request.vars) and (request.args(0)
                                               in ['ask', 'retry', 'test']):
        if debug: print '\ncontroller exploring.walk() state: response'
        resp = request.vars.response
        if debug: print 'response is', resp
        # if response is blank, just re-present the step prompt
        if resp in [None, '', ' ', []]:
            redirect(URL('walk.load', args=('ask'),
                            vars={'loc': request.vars['loc']}))
        # otherwise, evaluate and present response
        return walk.step.process(resp)

    # After user enters location or has completed step in this location
    #pick a path and present the prompt for the appropriate step
    elif request.args(0) == 'ask':
        if debug: print '\ncontroller exploring.walk() state: ask'
        walk.next_step()
        return walk.step.ask()

    # if user wants to retry a failed step
    elif request.args(0) == 'retry':
        if debug: print '\ncontroller exploring.walk() state: retry'
        last_pathid = session.walk['retry'][0]
        last_stepid = session.walk['retry'][1]
        walk.activate_step(last_pathid, last_stepid)
        return walk.step.ask()

    # test a specific path
    elif request.args(0) == 'test':
        if debug: print '\ncontroller exploring.walk() state: test'
        pathid = request.vars['path']
        stepid = request.vars['step']
        walk.activate_step(pathid, stepid)
        return walk.step.ask()

    #if user response results in an error
    elif request.args(0) == 'error':
        #TODO: Review bug handling and logging here
        print '\ncontroller exploring.walk() state: error'
        return patherror()


@auth.requires_membership('administrators')
def x():
    '''
    sandbox method for testing logic
    '''
    user = 25
    record_list = db(db.tag_records.name == user).select()
    discrete_tags = set([t.tag for t in record_list])
    tbdel = []
    if len(record_list) > len(discrete_tags):
        print 'duplicate rows present'
        for tag in discrete_tags:
            shortlist = record_list.find(lambda row: row.tag == tag)
            if len(shortlist) > 1:
                tbdel.append(shortlist[1:])
                # for record in shortlist[1:]:
                #     db.tag_records[record.id].delete()
        tbdel = chain([l for l in tbdel])
        print [l for l in tbdel]

    return dict(record_list=len(record_list),
                discrete_tags=discrete_tags,
                tbdel=tbdel)
