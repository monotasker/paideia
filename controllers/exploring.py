# coding: utf8
from paideia_exploring import path, tag, step, counter, map
from paideia_questions import question
import pprint

def stepreply():
    #see whether answer matches any of the three answer fields
    q = question()
    the_eval = q.evalq()

    #build response to user
    if session.eval == 'correct':
        the_reply = "Right. Κάλη."
    elif session.eval == 'partial':
        the_reply = "Οὐ κάκος. You're close."
    else:
        the_reply = "Incorrect. Try again!"

    #add a record for this attempt in db.attempt_log
    db.attempt_log.insert(question=session.q_ID, score=q.score, quiz=session.path_id)

    return dict(reply=the_reply, answer=session.readable_answer, raw_answer=session.answer, score=session.score)

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
    if response.vars and 'session_var' in response.vars:
        session_vars = response.vars['session_var']
    else:
        session_vars = 'all'
    path = paideia_path()
    path.clear_session(session_vars)
    print 'clearing session vars: ', session_vars
    print session

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
        m = map()
        '\n returned to controller exploring/index:'

        return dict(locs=m.locs, map_image=m.image)

    #after user selects quiz (or 'next question')
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

    #after submitting response
    elif request.args(0) == 'reply':
        print '\nreply state'
        return s.reply()

    #if user response results in an error
    elif request.args(0) == 'error':
        print '\nerror state'
        return patherror()
