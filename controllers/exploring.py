# coding: utf8

if 0:
    from gluon import current, redirect, URL, SQLFORM, A
    from gluon.dal import DAL
    from gluon.tools import Auth
    request,session,response,T,cache=current.request,current.session,current.response,current.t,current.cache
    db = DAL()
    auth = Auth()
    from applications.paideia.models.paideia_questions import *
    from applications.paideia.models.paideia_exploring import *

@auth.requires_login()
def index():

    #after user selects quiz (or 'next question')
    if request.args(0) == 'ask':
        if not request.vars.response:
            set_path = activepath()
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

    #after submitting answer
    elif request.args(0) == 'reply':
        #get the question that was asked
        q_ID = session.qID
        the_q = db(db.question_records.question==q_ID).select()
        #see whether answer matches any of the three answer fields
        q = question()
        the_eval = q.evalq(the_q)
        q.recordq(the_q, the_eval, q_ID)
        
        #build response to user
        if session.eval == 'correct':
            the_reply = "Right. Κάλη."
        elif session.eval == 'partial':
            the_reply = "Οὐ κάκος. You're close."
        else:
            the_reply = "Incorrect. Try again!"
        the_answer = session.readable_answer

        #add a record for this attempt in db.attempt_log
        db.attempt_log.insert(question=q_ID, score=the_eval['score'], quiz=session.path_id)

        return dict(reply=the_reply, answer=the_answer, raw_answer=session.answer, score=session.score)

    #if there's an error thrown after submitting an answer
    elif request.args(0) == 'error':
        if request.args(1) == 'unknown':
            db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
            db(db.questions.id==session.qID).update(q_status=1);
        if request.args(1) == 'regex':
            db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
            db(db.questions.id==session.qID).update(q_status=1);
        message = "Oops! Something about that question confused me, and I'm not sure whether your answer was right. Let's try another one."
        button = A('continue', _href=URL('index', args=['ask']), _class='button-green-grad next_q', cid=request.cid)
        #don't include this question in counting the number attempted
        session.q_counter -= 1
        return dict(message = message, button = button)

    #when first arrive at start page
    else:
        the_quizzes = db().select(db.quizzes.ALL, orderby=db.quizzes.quiz)
        return dict(quizzes = the_quizzes)
