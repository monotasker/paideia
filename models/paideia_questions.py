import random,re,datetime,string

if 0:
    from gluon import current, redirect, URL
    from gluon.dal import DAL
    from gluon.tools import Auth
    request,session,response,T,cache=current.request,current.session,current.response,current.t,current.cache
    db = DAL()
    auth = Auth() 

class question:
    """
    handles selection, presentation, and evaluation of one active question
    methods: selectq, evalq, recordq
    
    """
    def __init__(self):
        self.qID = [] #the ID of the selected question
        self.the_q = '' #the row object holding the selected question
        self.quiz_type = '' #the kind of algorithm used to select the question
        self.question_text = ''
        self.answer = ''
        self.answer2 = ''
        self.answer3 = ''
        self.readable_answer = ''

    def selectq(self):
        """
        selects the question to present to a user at the start of a step in any path
        
        q_not_today -- questions the student hasn't attempted today 
        q_fresh -- questions the student hasn't ever attempted
        q_cat1 -- questions that are in category1 for this student
        q_cat2 -- questions that are in category2 for this student
        q_cat3 -- questions that are in category3 for this student
        q_cat4 -- questions that are in category4 for this student

        TODO: still need to code following conditions 1) include only tags for this quiz; 2) include only frequency for this quiz        
        TODO: add a session counter dict that counts the number of times each question is failed today -- qID:#
        TODO: handle browser refresh more intelligently (to next q rather than path selection)
        TODO: handle system errors gracefully
        TODO: tweak selection algorithm
        """
        # (db.questions.id == db.question_records.question) joins questions to records
        # (db.question_records.name==auth.user_id) filters based on current user
        # (db.question_records.last_right != datetime.date.today()) removes questions gotten right today
        q_not_today =  db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.last_right != datetime.date.today())).select()
        q_cat1 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==1) & (db.question_records.last_right != datetime.date.today())).select()
        q_cat2 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==2) & (db.question_records.last_right != datetime.date.today())).select()
        q_cat3 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==3) & (db.question_records.last_right != datetime.date.today())).select()
        q_cat4 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==4) & (db.question_records.last_right != datetime.date.today())).select()
        q_fresh = db(db.question_records.question==None).select(db.questions.ALL, db.question_records.ALL, left=db.question_records.on(db.questions.id==db.question_records.question))
        session.debug = q_cat1
       
        the_switch = random.randint(0,9)
        #randomly choose between review (haven't answered correct today) and totally new
        if the_switch in range(5,9) and q_cat1:
            questions = q_cat1
            session.quiz_type = "category 1"
            question_count = len(questions) - 1
            question_index = random.randint(0,question_count)
            question_obj = questions[question_index].questions
        elif the_switch in range(3,4) and q_cat2:
            questions = q_cat2
            session.quiz_type = "category 2"
            question_count = len(questions) - 1
            question_index = random.randint(0,question_count)
            question_obj = questions[question_index].questions
        elif the_switch in range(1,2) and q_cat3:
            questions = q_cat2
            session.quiz_type = "category 2"
            question_count = len(questions) - 1
            question_index = random.randint(0,question_count)
            question_obj = questions[question_index].questions
        elif the_switch == 0 and q_not_today:
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
            question_index = random.randint(0, question_count)
            question_obj = questions[question_index]
    
        if question_obj.q_status == 1:
            self.selectq()
    
        session.qID = question_obj.id
        session.question_text = question_obj.question
        session.answer = question_obj.answer
        session.answer2 = question_obj.answer2
        session.answer3 = question_obj.answer3
        session.readable_answer = question_obj.readable_answer

    def evalq(self, the_q):
        the_response = string.strip(session.response)
        try:
            if re.match(session.answer, the_response, re.I):
                session.eval = 'correct'
                rightCount = 1
                wrongCount = 0
                if the_q:
                    wrongDate = the_q[0].last_wrong
                else:
                    wrongDate = datetime.date.today()
                rightDate = datetime.date.today()
                score = 1
            elif re.match(session.answer2,session.response) and session.answer2 != 'null':
                session.eval = 'partial'
                rightCount = 0
                wrongCount = 0
                if the_q:
                    wrongDate = the_q[0].last_wrong
                    rightDate = the_q[0].last_right
                else:
                    wrongDate = datetime.date.today()
                    rightDate = datetime.date.today()
                score = 0.5
            elif re.match(session.answer3,session.response) and session.answer3 != 'null':
                session.eval = 'partial'
                rightCount = 0
                wrongCount = 0
                if the_q:
                    wrongDate = the_q[0].last_wrong
                    rightDate = the_q[0].last_right
                else:
                    wrongDate = datetime.date.today()
                    rightDate = datetime.date.today()
                score = 0.3
            else:
                session.eval = "wrong"
                wrongCount = 1
                rightCount = 0
                if the_q:
                    rightDate = the_q[0].last_right
                else:
                    rightDate = datetime.date.today()
                wrongDate = datetime.date.today()
                score = 0
            return dict(the_q = the_q, rightDate = rightDate, wrongDate = wrongDate, rightCount = rightCount, wrongCount = wrongCount, score = score)
        except re.error:
            redirect(URL('index', args=['error', 'regex']))
        else:
            redirect(URL('index', args=['error', 'unknown']))

    def recordq(self, the_q, the_eval, q_ID):
        #update or create database record for
        #If the user has already attempted this question once, update their record for this question
        if db((db.question_records.name==auth.user_id)&(db.question_records.question==q_ID)).select():
            timesR = the_q[0].times_right
            timesW = the_q[0].times_wrong
            newTimesR = int(timesR) + int(the_eval['rightCount'])
            newTimesW = int(timesW) + int(the_eval['wrongCount'])
            last_right = the_eval['rightDate']
            last_wrong = the_eval['wrongDate']
            #figure out how the student is doing with this question
            now_date = datetime.date.today()
            right_dur = now_date-last_right
            wrong_dur = now_date-last_wrong
            rightWrong_dur = last_right - last_wrong
            #categorize this question based on student's performance
            if right_dur < wrong_dur:
                if (right_dur < rightWrong_dur) and (right_dur < datetime.timedelta(days=170)):
                    if right_dur > datetime.timedelta(days=14):
                        cat = 4
                    else:
                        cat = 3
                else:
                    cat = 2
            else:
                cat = 1

            #update the db record
            db(db.question_records.question==q_ID).update(times_right=newTimesR, times_wrong=newTimesW, last_right=last_right, last_wrong=last_wrong, category=cat)
        #if the user hasn't attempted this question, create a new record for it
        else:
            db.question_records.insert(question=q_ID, times_right=the_eval['rightCount'], times_wrong=the_eval['wrongCount'])

