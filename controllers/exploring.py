# coding: utf8
from paideia_exploring import path, tag, step, step_multipleChoice, counter, map
from paideia_questions import question
import pprint

def patherror():
    if request.args(1) == 'unknown':
        db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
        #TODO: fix problem with changing column name for status
        #db(db.questions.id==session.qID).update(qqq_status=1);
    if request.args(1) == 'regex':
        db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
        #db(db.questions.id==session.qID).update(qqq_status=1);
    message = "Oops! Something about that question confused me, and I'm not sure whether your answer was right. Let's try another one."
    button = A('continue', _href=URL('index', args=['ask']), _class='button-green-grad next_q', cid=request.cid)
    #don't include this question in counting the number attempted
    session.q_counter -= 1

    return dict(message=message, button=button)

def clear_session():
    the_path = path()
    the_path.clear_session()

def set_value():
    query = db(db.steps.id > 0).select()
    for q in query:
        q.update_record(widget_type = 1)
    print 'updated ', len(query), ' records'

@auth.requires_login()
def index():
    """
    Main method for presenting various states of the user interface. 
    The states are determined by the first url argument. Processed 
    initially by the view in views/exploring/index.html. The #page 
    region is then refreshed via ajax using the view in views/
    exploring/index.load

    user must be logged in to access this controller. Otherwise s/he 
    will be redirected to the default login form.
    """

    print '===================================================='
    print 'new state in controller exploring/index', datetime.datetime.utcnow()
    #check to see whether this user session has been initialized
    if not session.tagset:
        print '\ninitializing new user session'
        #categorize paths for today
        t = tag()
        session.tagset = t.categorize_tags()
        print 'stored categorized tags in session.tagset'
        #re-activate paths that weren't finished during last session
        p = path()
        session.active_paths = p.find_unfinished()
        print 'restored unfinished paths to session.active_paths'

    #when user begins exploring (also default) present map
    if (request.args(0) == 'start') or (not request.args):
        print '\nstart state'
        session.location = None #clear in preparation for new loc
        m = map()
        return dict(locs=m.locs, map_image=m.image)

    #this and the following function are for testing a specific step
    if (request.args(0) == 'test_step') and ('response' in request.vars):
        s = step(request.args(0))
        return s.process()

    if (request.args(0) == 'test_step'):
        sid = request.args(1)
        pid = db(db.paths.steps.contains(sid)).select().first().id
        session.path = pid
        session.active_paths = {pid:sid}
        session.location = 1
        w = db.steps[sid].widget_type.step_class
        session.widget_type = w
        if w == 'step_multipleChoice':
            s = step_multipleChoice(sid)
        else:
            s = step(sid)
        return s.ask()

    #after user submits response to step prompt
    #evaluate response and present feedback via npc reply
    elif ('response' in request.vars) and (request.args(0) == 'ask'):
        print '\nreply state'
        sid = session.step
        s = step(sid)
        return s.process()

    #after enters location or has completed step in this location
    #pick a path and present the prompt for the appropriate step
    elif request.args(0) == 'ask':
        print '\nask state'
        p = path()
        p_result = p.pick()
        pid = p_result['path'].id
        sid = p_result['step']
        print '\nreturned to controller exploring/index:'
        print 'path ', pid, '; step ', sid
        s = step(sid)
        return s.ask()

    #if user response results in an error
    elif request.args(0) == 'error':
        print '\nerror state'
        return patherror()

