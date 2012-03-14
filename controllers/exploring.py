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
    print 'session.tagset: ', pprint.pprint(session.tagset)
    #add paths that weren't finished during last session
    path = paideia_path()
    session.active_paths = path.find_unfinished()
    print 'returned unfinished paths'
    print 'session active_paths: ', session.active_paths

def step_init():
    print '\n calling step_init()'
    #find out what location has been entered
    curr_loc = db(db.locations.alias == request.vars['loc']).select().first()
    print 'current location: ', curr_loc.alias, curr_loc.id

    #check to see whether any constraints are in place 
    if 'blocks' in session:
        print 'active block conditions: ', session.blocks
        #TODO: Add logic here to handle blocking conditions
    else:
        print 'no blocking conditions'
    
    #find out what paths (if any) are currently active
    a_paths = session.active_path or None
    print 'active paths: ', a_paths
    
    #if an active path has a step here, initiate that step
    if a_paths:
        pathsteps = db((db.paths.steps.contains(a_paths)) 
                       & (db.paths.locations.contains(curr_loc.id))).select()
        p = pathsteps.first()

    if 'pathsteps' in locals():
        print 'continuing active path ', p
    else:
        print 'no active paths here'
        print 'selecting new path . . .'
    
        #look for tags with high priority    
        cat1tags = session.tagset[1]
        print 'category 1 tags: ', cat1tags
        cat1paths = db(db.paths.tags.contains(cat1tags)).select()
        print db(db.paths.tags.contains(cat1tags)).count()
    
    #if none look for tags with medium priority
    #if none,  
        return dict()

def stepask():
    #check to see whether a path is active and determines the next step
    if session.active_path:
        pass
    
    #if not, initiate new path 
    if not request.vars.response:
        set_path = paideia_path()
        set_counter = counter()
        the_question = question()
        the_question.selectq()

    form = SQLFORM.factory(
        Field('response', 'string', requires=IS_NOT_EMPTY())
    )
    if form.accepts(request.vars,session):
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
    return dict(message = message, button = button)

@auth.requires_login()
def index():
    #check to see whether this user session has been initialized
    if not session.tagset:
        session_init()

    #when user begins exploring (also default) present map
    if (request.args(0) == 'start') or (not request.args):
        the_map = map()
        for i in ['blocks', 'active_paths', 'completed_paths']:
            if not session[i]:
                print i
                session[i] = None
             
        return dict(locs = the_map.locs, map_image = the_map.image)

    #after user selects quiz (or 'next question')
    elif request.args(0) == 'ask':
        return step_init()

    #after submitting answer
    elif request.args(0) == 'reply':
        return stepreply()
    
    elif request.args(0) == 'error':
        return patherror()
        
    