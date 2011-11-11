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
        self.the_q = '' #the row object holding the selected question
        self.quiz_type = '' #the kind of algorithm used to select the question
        self.rightDate = ''
        self.wrongDate = ''
        self.rightCount = ''
        self.wrongCount = ''
        self.score = ''
   
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
        TODO: exclude questions marked with status=1
        """
        # (db.questions.id == db.question_records.question) joins questions to records
        # (db.question_records.name==auth.user_id) filters based on current user
        # (db.question_records.last_right != datetime.date.today()) removes questions gotten right today

        d = str(datetime.date.today())
        d = string.replace(d, ',', '-')
        session.debug = d
        
        q_not_today =  db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.tlast_right != d)).select()
        q_cat1 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==1) & (db.question_records.tlast_right != d)).select()
        q_cat2 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==2) & (db.question_records.tlast_right != d)).select()
        q_cat3 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==3) & (db.question_records.tlast_right != d)).select()
        q_cat4 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==4) & (db.question_records.tlast_right != d)).select()
        q_fresh = db(db.question_records.question==None).select(db.questions.ALL, db.question_records.ALL, left=db.question_records.on(db.questions.id==db.question_records.question))
        
        session.debug = datetime.date.today()
       
        the_switch = random.randint(0,9)
        #randomly choose between review (haven't answered correct today) and totally new
        if the_switch in range(3,9):
            if q_cat1:
                questions = q_cat1
                session.quiz_type = "category 1"
                question_count = len(questions) - 1
                question_index = random.randint(0,question_count)
                question_obj = questions[question_index].questions
            elif q_cat2:
                questions = q_cat2
                session.quiz_type = "category 2"
                question_count = len(questions) - 1
                question_index = random.randint(0,question_count)
                question_obj = questions[question_index].questions
            elif q_cat3:
                questions = q_cat3
                session.quiz_type = "category 3"
                question_count = len(questions) - 1
                question_index = random.randint(0,question_count)
                question_obj = questions[question_index].questions
            else:
                questions = q_cat4
                session.quiz_type = "category 4"
                question_count = len(questions) - 1
                question_index = random.randint(0,question_count)
                question_obj = questions[question_index].questions
        elif the_switch in range(1,2) and q_fresh:
            questions = q_fresh
            session.quiz_type = "fresh questions (first try)"
            question_count = len(questions) - 1
            question_index = random.randint(0,question_count)
            question_obj = questions[question_index].questions       
        #fallback is totally random review (in case all have been tried and gotten correct today)
        else:        
            questions = q_not_today
            session.quiz_type = "random"
            question_count = len(questions) - 1
            question_index = random.randint(0, question_count)
            question_obj = questions[question_index].questions
      
        session.qID = question_obj.id
        session.question_text = question_obj.question
        session.answer = question_obj.answer        
        session.answer2 = question_obj.answer2
        session.answer3 = question_obj.answer3
        session.readable_answer = question_obj.readable_answer

    def evalq(self):
        the_response = string.strip(session.response)
        self.the_q = db(db.question_records.question==session.q_ID).select().first()
        
        try:
            if re.match(session.answer, the_response, re.I):
                session.eval = 'correct'
                self.rightCount = 1
                self.wrongCount = 0
                if self.the_q:
                    self.wrongDate = self.the_q.tlast_wrong
                else:
                    self.wrongDate = datetime.datetime.utcnow()
                self.rightDate = datetime.datetime.utcnow()
                self.score = 1
            elif re.match(session.answer2,session.response) and session.answer2 != 'null':
                session.eval = 'partial'
                self.rightCount = 0
                self.wrongCount = 0
                if the_q:
                    self.wrongDate = self.the_q.tlast_wrong
                    self.rightDate = self.the_q.tlast_right
                else:
                    self.wrongDate = datetime.datetime.utcnow()
                    self.rightDate = datetime.datetime.utcnow()
                self.score = 0.5
            elif re.match(session.answer3,session.response) and session.answer3 != 'null':
                session.eval = 'partial'
                self.rightCount = 0
                self.wrongCount = 0
                if self.the_q:
                    self.wrongDate = self.the_q.tlast_wrong
                    self.rightDate = self.the_q.tlast_right
                else:
                    self.wrongDate = datetime.datetime.utcnow()
                    self.rightDate = datetime.datetime.utcnow()
                #TODO: Get this score value from the db instead of hard coding it here.
                self.score = 0.3
            else:
                session.eval = "wrong"
                self.wrongCount = 1
                self.rightCount = 0
                if self.the_q:
                    self.rightDate = self.the_q.tlast_right
                else:
                    self.rightDate = datetime.datetime.utcnow()
                self.wrongDate = datetime.datetime.utcnow()
                self.score = 0           
            
            self.recordq()
            
        #handle errors if the response cannot be evaluated        
        except re.error:
            redirect(URL('index', args=['error', 'regex']))
        
    def recordq(self):
        """
        update or create database record for question attempt after it's evaluated.
        """
        #If the user has already attempted this question once, update their record for this question
        if db((db.question_records.name==auth.user_id)&(db.question_records.question==session.q_ID)).select():
            timesR = self.the_q.times_right
            timesW = self.the_q.times_wrong
            newTimesR = int(timesR) + int(self.rightCount)
            newTimesW = int(timesW) + int(self.wrongCount)
            last_right = self.rightDate
            last_wrong = self.wrongDate
            #figure out how the student is doing with this question
            now_date = datetime.datetime.utcnow()
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
            db(db.question_records.question==session.q_ID).update(times_right=newTimesR, times_wrong=newTimesW, last_right=last_right, last_wrong=last_wrong, category=cat)
        #if the user hasn't attempted this question, create a new record for it
        else:
            db.question_records.insert(question=session.q_ID, times_right=self.rightCount, times_wrong=self.wrongCount)
