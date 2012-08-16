# coding: utf8
from paideia_exploring import Walk, Location, Step, StepStub
#, Npc, Path, Step, StepStub, StepMultipleChoice, Counter, Map, Location
import pprint

"""
Controller: Handle user-interactions for the game proper.

This controller handles everything from preparing the necessary session
variables before game activities begin to evaluating and recording the
student's performance. It does not cover any back-end actions or content
creation. Neither does it handle retrieval or display of student
statistics.

Terminology:

The basic metaphor for this educational game is that
of a character exploring a new town. Hence the name "exploring" for this
controller. That same metaphor is followed through in the naming of other
functions here and (especially) in the module paideia_exploring.

:path:
The game is built on a quest-like model, but each quest or task is called a
"path." This term does not refer in most cases to a file path but to a
discrete set of interactions that the student must perform in sequence. In
the rare case where a file path is intended this will be clear both from
context and in the docstring. A "path" is represented by the Path class in
the paideia_exploring module.

:step:
A path (i.e., quest or task) consists of several individual "steps." Each
"step" is a single user interaction involving
- a prompt (an npc question or other stimulus calling for user response),
- a user response (entered as form data, through a number of possible widgets)
- a reply (feedback presented to the user, along with the user's next
    navigation options)
A single step is represented by the Step class in the paideia_exploring module.
Some paths may include just a single step, while others may include a sequence
of several steps.

The base Step class involves a simple question prompt, calling for a text
response entered in a regular text input field. This class is extended by
several other classes, allowing for different kinds of user response. These
class names each begin with Step.

:walking:
Following the same metaphor, the movement through the steps of a path (and
from one path to the next) is referred to as a "walk." So the controller
function handling this movement is called walk() and the module includes a
Walk class that holds logic related to transitions from one step to the next.

These transitions are complicated because the steps in a path often have to be
completed in different locations around the fictional town of the game
setting. Since the user is free to move as they choose from one town location
to another, they may sometimes begin a second path in a new location before
moving on to the location where the original path can be completed.

Session variables:

The movement between steps and between paths is controlled by means of
several variables set on the web2py session object:
- session.tag_set (stores categorized grammatical tags for selecting paths;
    this information is calculated at the beginning of a new user session
    and then persists until the session expires.)
- session.active_paths (tracks the paths that are currently active, along with the
    last step that has been initiated for each one)
- session.completed (a cumulative list of the paths completed during the
    current user session)
- session.blocks (stores flags for any blocking conditions, checked just
    prior to each path and step selection)

Several other session variables provide data persistence across the various
states of a single step.
- session.location (reset to None whenever the user returns to town map)
- session.step (stores the Step instance initialized in the 'ask' state
    so that it can be reused to evaluate the user response; reset to None
    just before 'reply' view is presented to user)

Division of labour between controller and module:

Most of the business logic is referred to classes in the module
paideia_exploring. In a few cases it is a bit arbitrary whether to put
activity in the module or here in the controller functions. My basic
principles have been:
1. If in doubt, put it in the module (keep the controllers clean)
2. Keep all reading and writing to session variables in the controller (this
    is partly to minimize dependencies in the module classes, but also to
    avoid confusion about where and when the session is being modified.)
3. Keep db interaction in the controller if it is not too awkward. (This is
    mostly to minimize dependency in the classes and simplify unit testing.
    So far it hasn't seemed sensible to make it a hard rule, but more of the
    db interactions can probably be moved back to the controller.)

Controls these views:

- exploring/index.html
- exploring/walk.load
- exploring/patherror.load
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

@auth.requires_login()
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

@auth.requires_login()
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
    Present game interface and prepare the necessary session variables.

    Little of the game logic happens here. This function is used mainly just
    to set up the static page elements, including the #page element which
    will load the walk() function.

    :Permissions: user must be logged in.
    """

    walk = Walk()

    # Check to see whether this user session has been initialized
    if not walk.tag_set:
        print '\ninitializing new user session'
        # Categorize available tags for this student, store in Walk instance
        walk.categorize_tags()
        # Find and re-initialize any paths that were previously started but
        # not finished
        walk.unfinished()
        # Update the session
        # TODO: Make sure that the session is refreshed at the start of each
        # new day
        walk.save_session_data()

    return dict(active = walk.active_paths)

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
    debug = False

    walk = Walk()
    if debug: print '\n\nDEBUG: controller exploring.walk()'

    # When user begins exploring (also default) present map
    if (request.args(0) == 'start') or (not request.args):

        if debug: print '\nDEBUG: controller state: start'
        # TODO: change to a new public method Walk.set_active_location()
        walk.active_location = None #clear in preparation for new location
        walk.save_session_data()

        # If we got here from a StepStub, we need to complete the step
        if walk.step and isinstance(walk.step, StepStub):
            walk.step.complete()

        return {'map': walk.map}

    # After user submits response to step prompt
    # Evaluate response and present feedback via npc reply
    elif ('response' in request.vars) and (request.args(0) == 'ask'):

        if debug: print '\nDEBUG: controller state: response'
        if debug: print 'DEBUG: in controller.walk(), session.walk =',\
                                                                session.walk
        data = walk.step.process(request.vars.response)
        walk.save_session_data()
        return data

    #after enters location or has completed step in this location
    #pick a path and present the prompt for the appropriate step
    elif request.args(0) == 'ask':

        print '\nDEBUG: controller state: ask'
        # Walk.stay() handles transition to another path/step in the
        # same location
        walk.staying = False
        stay = request.vars['stay']
        if stay:
            walk.staying = walk.stay()
        # TODO: not sure what's going on here with location
        else:
            loc = request.vars['loc']
            if loc:
                walk.active_location = Location(loc)
        print 'DEBUG: staying =', walk.staying
        if not walk.staying:
            walk.next_step()
        data = walk.step.ask()
        walk.save_session_data()

        return data

    #if user response results in an error
    elif request.args(0) == 'error':

        #TODO: Review bug handling and logging here
        print '\nDEBUG: controller state: error'
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

