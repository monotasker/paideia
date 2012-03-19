# coding: utf8
from paideia_exploring import paideia_path, paideia_tag, counter, map
from paideia_questions import question
import pprint

def session_init():
    print 'calling session_init'

    #categorize paths for today
    tags = paideia_tag()
    session.tagset = tags.categorize_tags()
    print 'returned categorized tags'

    #add paths that weren't finished during last session
    path = paideia_path()
    session.active_paths = path.find_unfinished()
    print 'returned unfinished paths'

def step_init():
    path = paideia_path()
    path_result = path.pick()
    print 'returned to controller step_init():'
    print 'path ', path_result['path']
    print 'step ', path_result['step']
    return dict(path = path_result['path'], step = path_result['step'])

def stepask():
    
    #if not, initiate new path
    if not request.vars.response:
        set_counter = counter()
        the_question = question()
        the_question.selectq()

    form = SQLFORM.factory(
        Field('response', 'string', requires=IS_NOT_EMPTY())
    )
    if form.accepts(request.vars,  session):
        session.response = request.vars.response
        redirect(URL('index', args=['reply']))

    return dict(question=session.question_text, form=form)


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

    #check to see whether this user session has been initialized
    if not session.tagset:
        session_init()

    #when user begins exploring (also default) present map
    if (request.args(0) == 'start') or (not request.args):
        the_map = map()
        clear_session()

        return dict(locs=the_map.locs, map_image=the_map.image)

    #after user selects quiz (or 'next question')
    elif request.args(0) == 'ask':
        return step_init()

    #after submitting answer
    elif request.args(0) == 'reply':
        return stepreply()

    elif request.args(0) == 'error':
        return patherror()
