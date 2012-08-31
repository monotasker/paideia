# coding: utf8
from paideia_exploring import Walk, Location, Step, StepStub
#, Npc, Path, Step, StepStub, StepMultipleChoice, Counter, Map, Location
import pprint

"""
These controller functions handle user-interactions for the game proper. It
does not cover any back-end actions, content creation, or retrieval and
display of student performance statistics.

Wherever possible, business logic is kept out of these controllers and are
provided by classes in the module paideia_exploring. Controllers access
that logic through a very small set of public methods:

- Walk.next_step
- Walk.activate_step (for those cases in which
- Step.ask (accessed via the Step stored in the Walk object: Walk.step.ask)
- Step.process
(Walk._categorize_tags is also accessed externally from paideia_stats.py)

The controller functions interact with these views:
- exploring/index.html (frame for the game ui)
- exploring/walk.load (main game ui)
- exploring/patherror.load (error screen)
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

    if request.args(1) == 'unknown':
        db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
        #TODO: fix problem with changing column name for status
    if request.args(1) == 'regex':
        db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)

    message = """Oops! Something about that question confused me, and I'm not
    sure whether your answer was right. Let's try another one."""
    button = A('continue', _href=URL('index', args=['ask']),
        _class='button-green-grad next_q', cid=request.cid)
    #don't include this question in counting the number attempted
    session.q_counter -= 1

    return dict(message=message, button=button)

@auth.requires_membership('administrators')
def clear_session():
    """
    Reset the requested session variables to None.

    This is a utility function. It doesn't really belong in this controller
    and it is not intended to present any view. All of the logic is in the
    Utils class.

    :See also: modules/paideia_exploring.Utils

    :returns: no return value

    **TODO: provide a return value and use web2py response.flash to notify
    user of successful result.
    """
    Utils().clear_session()

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

    query = db(db.steps.id > 0).select()
    for q in query:
        q.update_record(widget_type = 1)
    print 'updated ', len(query), ' records'

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
    walk = Walk()

    # When user begins exploring (also default) present map
    if (request.args(0) == 'start') or (not request.args):

        if debug: print '\ncontroller exploring.walk() state: start'
        # TODO: change to a new public method Walk.set_active_location()
        walk.active_location = None #clear in preparation for new location
        session.walk['active_location'] = None

        # If we got here from a StepStub, we need to complete the step
        if walk.step and isinstance(walk.step, StepStub):
            walk.step.complete()

        return {'map': walk.map}

    # After user submits response to step prompt
    # Evaluate response and present feedback via npc reply
    elif ('response' in request.vars) and (request.args(0) == 'ask'):
        if debug:
            print '\ncontroller exploring.walk() state: response'

        data = walk.step.process(request.vars.response)

        return data

    # After user enters location or has completed step in this location
    #pick a path and present the prompt for the appropriate step
    elif request.args(0) == 'ask':

        if debug: print '\ncontroller exploring.walk() state: ask'
        walk.next_step()

        return walk.step.ask()

    #if user wants to retry a failed step
    elif request.args(0) == 'retry':
        last_pathid = session.walk['path']
        last_stepid = session.walk['step']
        walk.activate_step(last_pathid, last_stepid)

    #if user response results in an error
    elif request.args(0) == 'error':

        #TODO: Review bug handling and logging here
        print '\ncontroller exploring.walk() state: error'

        if debug: print 'session.walk["step"] =', session.walk['step']
        if debug: print 'session.walk["path"] =', session.walk['path']

        return patherror()

    # TODO: make sure these still work
    #this and the following function are for testing a specific step
    if (request.args(0) == 'test_step') and ('response' in request.vars):
        s = Step(request.args(0))
        return s.process()

    if (request.args(0) == 'test_step'):
        sid = request.args(1)
        pid = db(db.paths.steps.contains(sid)).select().first().id
        session.path = pid
        session.active_paths = {pid:sid}
        session.location = 1
        w = db.steps[sid].widget_type.step_class
        session.widget = w
        if w == 'step_multipleChoice':
            s = StepMultipleChoice(sid)
        else:
            s = Step(sid)
        return s.ask()

