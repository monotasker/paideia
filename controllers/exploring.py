# coding: utf8

import random,re,datetime,string

def set_path():
    #set the quiz and retrieve its data
    if not session.path_length:
        the_path = db(db.quizzes.id == request.vars.path).select()
        session.path_id = the_path[0].id
        session.path_length = the_path[0].length
        session.path_name = the_path[0].quiz
        session.path_freq = the_path[0].frequency
        session.path_tags = the_path[0].tags

def set_counter():
    #include this question in the count for this quiz, send to 'end' if quiz is finished
    if session.q_counter:
        if int(session.q_counter) >= int(session.path_length):
            session.q_counter = 0
            redirect(URL('index', args=['end']))
            return dict(end="yes")
        else:
            session.q_counter += 1
    else:
        session.q_counter = 1

def get_question():

    #still need to code following conditions:
    #include only tags for this quiz
    #include only frequency for this quiz

    # (db.questions.id == db.question_records.question) joins questions to records
    # (db.question_records.name==auth.user_id) filters based on current user
    # (db.question_records.last_right != datetime.date.today()) removes questions gotten right today
    q_not_today =  db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.last_right != datetime.date.today())).select()

    #finds questions that haven't yet been tried by this user (using left join)
    q_fresh = db(db.question_records.question==None).select(db.questions.ALL, db.question_records.ALL, left=db.question_records.on(db.questions.id==db.question_records.question))

    #old_list = db(db.question_records.name==auth.user_id).select()
    #q_fresh = db(~db.questions.id.belongs(old_list)).select()

    the_switch = random.randint(0,1)
    #randomly choose between review (haven't answered correct today) and totally new
    if q_not_today and the_switch == 0:
        questions = q_not_today
        session.quiz_type = "regular review (haven't gotten correct today)"
        question_count = len(questions) - 1
        question_index = random.randint(0,question_count)
        question_obj = questions[question_index].questions
    elif q_fresh:
        questions = q_fresh
        session.quiz_type = "fresh questions (first try)"
        question_count = len(questions) - 1
        question_index = random.randint(0,question_count)
        question_obj = questions[question_index].questions
    #fallback is totally random review (in case all have been tried and gotten correct today)
    else:
        questions = db(db.questions.id > 0).select()
        session.quiz_type = "random"
        question_count = len(questions) - 1
        question_index = random.randint(0,question_count)
        question_obj = questions[question_index]
    
    if question_obj.status == 1:
        get_question()
        
    session.qID = question_obj.id
    session.question_text = question_obj.question
    session.answer = question_obj.answer
    session.answer2 = question_obj.answer2
    session.answer3 = question_obj.answer3
    session.readable_answer = question_obj.readable_answer

def eval_response(the_q):
    the_response = string.strip(session.response)
    try:
        if re.match(session.answer, the_response, re.I):
            session.eval = 'correct'
            rightCount = 1
            wrongCount = 0
            if the_q:
                wrongDate = the_q[0].last_wrong
            else:
                wrongDate = request.now
            rightDate = request.now
            session.score = 1
        elif re.match(session.answer2,session.response) and session.answer2 != 'null':
            session.eval = 'partial'
            rightCount = 0
            wrongCount = 0
            if the_q:
                wrongDate = the_q[0].last_wrong
                rightDate = the_q[0].last_right
            else:
                wrongDate = request.now
                rightDate = request.now
            session.score = 0.5
        elif re.match(session.answer3,session.response) and session.answer3 != 'null':
            session.eval = 'partial'
            rightCount = 0
            wrongCount = 0
            if the_q:
                wrongDate = the_q[0].last_wrong
                rightDate = the_q[0].last_right
            else:
                wrongDate = request.now
                rightDate = request.now
            session.score = 0.3
        else:
            session.eval = "wrong"
            wrongCount = 1
            rightCount = 0
            if the_q:
                rightDate = the_q[0].last_right
            else:
                rightDate = request.now
            wrongDate = request.now
            session.score = 0
        return dict(the_q = the_q, rightDate = rightDate, wrongDate = wrongDate, rightCount = rightCount, wrongCount = wrongCount)
    except re.error:
        redirect(URL('index', args=['error', 'regex']))
    else:
        redirect(URL('index', args=['error', 'unknown']))

@auth.requires_login()
def index():

    #after user selects quiz (or 'next question')
    if request.args(0) == 'ask':
        if not request.vars.response:
            set_path()
            set_counter()
            get_question()

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
        the_eval = eval_response(the_q)
        #update or create database record for
        #If the user has already attempted this question once, update their record for this question
        if db((db.question_records.name==auth.user_id)&(db.question_records.question==q_ID)).select():
            timesR = the_q[0].times_right
            timesW = the_q[0].times_wrong
            newTimesR = int(timesR) + int(the_eval['rightCount'])
            newTimesW = int(timesW) + int(the_eval['wrongCount'])
            db(db.question_records.question==q_ID).update(times_right=newTimesR, times_wrong=newTimesW, last_right=the_eval['rightDate'], last_wrong=the_eval['wrongDate'])
        #if the user hasn't attempted this question, create a new record for it
        else:
            db.question_records.insert(question=q_ID, times_right=the_eval['rightCount'], times_wrong=the_eval['wrongCount'])

        #build response to user
        if session.eval == 'correct':
            the_reply = "Right. Κάλη."
        elif session.eval == 'partial':
            the_reply = "Οὐ κάκος. You're close."
        else:
            the_reply = "Incorrect. Try again!"
        the_answer = session.readable_answer
        return dict(reply=the_reply, answer=the_answer, raw_answer=session.answer, score=session.score)

    #if there's an error thrown after submitting an answer
    elif request.args(0) == 'error':
        if request.args(1) == 'unknown':
            db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
        if request.args(1) == 'regex':
            db.q_bugs.insert(question=session.qID, a_submitted=request.vars.answer)
        message = "Oops! Something about that question confused me, and I'm not sure whether your answer was right. Let's try another one."
        button = A('continue', _href=URL('index', args=['ask']), _class='button-green-grad next_q', cid=request.cid)
        #don't include this question in counting the number attempted
        session.q_counter -= 1
        return dict(message = message, button = button)

    #when first arrive at start page
    else:
        the_quizzes = db().select(db.quizzes.ALL, orderby=db.quizzes.quiz)
        return dict(quizzes = the_quizzes)
