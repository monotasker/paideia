# coding: utf8

import random,re,datetime

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

    #finds questions that haven't yet been tried by this user
    old_list = db(db.question_records.name==auth.user_id).select()
    q_fresh = db(~db.questions.id.belongs(old_list)).select()

    if q_not_today:
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
        question_obj = questions[question_index]
    #fallback is totally random review (in case all have been tried and gotten correct today)    
    else:
        questions = db(db.questions.id > 0).select()
        session.quiz_type = "random"
        question_count = len(questions) - 1
        question_index = random.randint(0,question_count)      
        question_obj = questions[question_index]
    
    session.qID = question_obj.id
    session.question_text = question_obj.question
    session.answer = question_obj.answer
    session.answer2 = question_obj.answer2
    session.answer3 = question_obj.answer3
    session.readable_answer = question_obj.readable_answer

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
        if re.match(session.answer, session.response, re.I):
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
        #If the user has already attempted this question once, update their record for this question
        if db((db.question_records.name==auth.user_id)&(db.question_records.question==q_ID)).select():
            timesR = the_q[0].times_right
            timesW = the_q[0].times_wrong
            newTimesR = int(timesR) + int(rightCount)
            newTimesW = int(timesW) + int(wrongCount)
            db(db.question_records.question==q_ID).update(times_right=newTimesR, times_wrong=newTimesW, last_right=rightDate, last_wrong=wrongDate)
        #if the user hasn't attempted this question, create a new record for it
        else:
            db.question_records.insert(question=q_ID, times_right=rightCount, times_wrong=wrongCount)

        #build response to user
        if session.eval == 'correct':
            the_reply = "Right. Κάλη."
        elif session.eval == 'partial':
            the_reply = "Οὐ κάκος. You're close."
        else:
            the_reply = "Incorrect. Try again!"
        the_answer = session.readable_answer
        return dict(reply=the_reply, answer=the_answer, raw_answer=session.answer, score=session.score)

    #when first arrive at start page
    else:
        the_quizzes = db().select(db.quizzes.ALL, orderby=db.quizzes.quiz)
        return dict(quizzes = the_quizzes)
