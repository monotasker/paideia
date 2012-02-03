import random,re,datetime,string
from gluon import current, redirect, URL

class question:
    """
    handles selection, presentation, and evaluation of one active question
    methods: selectq, evalq, recordq

    """
    def __init__(self):
        self.the_q = '' #the row object holding the selected question
        self.quiz_type = '' #the kind of algorithm used to select the question
        self.rightCount = 0
        self.wrongCount = 0
        self.score = 0
        self.newTimesR = {}
        self.newTimesW = {}
        self.last_right = {}
        self.last_wrong = {}
        self.cat = {}

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

        session, auth, db = current.session, current.auth, current.db

        d = str(datetime.date.today())
        d = string.replace(d, ',', '-')
        session.debug = d

        q_not_today =  db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.tlast_right != d)).select()
        q_cat1 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==1) & (db.question_records.tlast_right != d)).select()
        q_cat2 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==2) & (db.question_records.tlast_right != d)).select()
        q_cat3 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==3) & (db.question_records.tlast_right != d)).select()
        q_cat4 = db((db.questions.id == db.question_records.question) & (db.question_records.name==auth.user_id) & (db.question_records.category==4) & (db.question_records.tlast_right != d)).select()
        q_fresh = db(db.question_records.question==None).select(db.questions.ALL, db.question_records.ALL, left=db.question_records.on(db.questions.id==db.question_records.question))

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
        # get web2py session objects
        session, db, auth = current.session, current.db, current.auth
        # get the student's response to the question
        the_response = string.strip(session.response)
        # retrieve the question data from the db to use in evaluating the answer
        self.the_q = db(db.question_records.question == session.qID).select().first()
        # compare the student's response to the regular expressions
        try:
            if re.match(session.answer, the_response, re.I):
                session.eval = 'correct'
                self.rightCount = 1
                self.score = 1
            elif re.match(session.answer2,session.response) and session.answer2 != 'null':
                session.eval = 'partial'
                self.score = 0.5
                #TODO: Get this score value from the db instead of hard coding it here.
            elif re.match(session.answer3,session.response) and session.answer3 != 'null':
                session.eval = 'partial'
                #TODO: Get this score value from the db instead of hard coding it here.
                self.score = 0.3
            else:
                session.eval = "wrong"
                self.wrongCount = 1
            # record the results in statistics for this question
            self.recordq(session.qID)
            # record the results in statistics for this question's tags
            self.recordtag(session.qID)
        #handle errors if the student's response cannot be evaluated
        except re.error:
            redirect(URL('index', args=['error', 'regex']))

    def recordq(self, qID):
        """
        update or create database record for this question after the attempt is evaluated.
        """
        # get web2py session objects
        session, db, auth = current.session, current.db, current.auth
        #If the user has already attempted this question once, update their record for this question
        qrecord = db((db.question_records.name == auth.user_id) & (db.question_records.question == qID)).select().first()
        if qrecord:
            indx = 'q%s' % qID
            #PRINT - for debugging purposes
            print indx
            #calculate updated performance statistics
            self.stats(qrecord)
            #update the db record
            #PRINT - for debugging purposes
            print '\n\n', 'question (update)', qID, 'times_right', self.newTimesR[indx], 'times_wrong', self.newTimesW[indx], 'tlast_right', self.last_right[indx], 'tlast_wrong', self.last_wrong[indx], 'cat', self.cat[indx], '\n'
            qrecord.update_record(
                times_right = self.newTimesR[indx],
                times_wrong = self.newTimesW[indx],
                tlast_right = self.last_right[indx],
                tlast_wrong = self.last_wrong[indx],
                category = self.cat[indx])
        #if the user hasn't attempted this question, create a new record for it
        else:
            #PRINT - for debugging purposes
            print '\n\n', 'question (new)', qID, 'times_right', self.rightCount, 'times_wrong', self.wrongCount, 'cat', 1, '\n'
            db.question_records.insert(
                question = qID,
                times_right = self.rightCount,
                times_wrong = self.wrongCount,
                category = 1)

    def recordtag(self, qID):
        """
        update or create database record for this question after the attempt is evaluated.
        """
        #get web2py objects from current
        session, db, auth = current.session, current.db, current.auth
        # calculate and record stats for each tag attached to this question
        tags = db(db.questions.id == qID).select(db.questions.tags).first()
        for k, v in tags.items():
            for tag in v:
                # select record for this user on this tag
                trecord = db((db.tag_records.name == auth.user_id)&(db.tag_records.tag == tag)).select().first()
                # if the user has already tried this tag, update the record
                if trecord:
                    indx = 't%s' % tag
                    #calculate updated performance statistics
                    self.stats(trecord)
                    #update the db record
                    #PRINT - for debugging purposes
                    print 'tag (update)', tag, 'times_right', self.newTimesR[indx], 'times_wrong', self.newTimesW[indx], 'tlast_right', self.last_right[indx], 'tlast_wrong', self.last_wrong[indx], 'cat', self.cat[indx], '\n'
                    db(db.tag_records.tag==tag).update(
                        times_right = self.newTimesR[indx],
                        times_wrong = self.newTimesW[indx],
                        tlast_right = self.last_right[indx],
                        tlast_wrong = self.last_wrong[indx],
                        category = self.cat[indx])
                # if this is the user's first time for this tag, create a new record
                else:
                    #PRINT - for debugging purposes
                    print 'tag (new)', tag, 'times_right', self.rightCount, 'times_wrong', self.wrongCount, 'category', 1, '\n'
                    db.tag_records.insert(
                        tag = tag,
                        times_right = self.rightCount,
                        times_wrong = self.wrongCount,
                        category = 1)

    def stats(self, record):
        #figure out right and wrong counts for this q or tag
        if record.has_key('tag'):
            indx = 't%s' % record.tag
            #PRINT - for debugging purposes
            print indx
        else:
            indx = 'q%s' % record.question
            #PRINT - for debugging purposes
            print indx
        #set times right and times wrong
        timesR = record.times_right or 0
        #PRINT - debugging
        print 'timesR is ', timesR
        timesW = record.times_wrong or 0
        self.newTimesR[indx] = int(timesR) + int(self.rightCount)
        self.newTimesW[indx] = int(timesW) + int(self.wrongCount)
        #set last_right and last_wrong
        now_date = datetime.datetime.utcnow()
        if self.rightCount == 1:
            self.last_right[indx] = now_date
            self.last_wrong[indx] = record.tlast_wrong or now_date
        elif (self.rightCount == 0) and (self.wrongCount == 0):
            self.last_right[indx] = record.tlast_right or now_date
            self.last_wrong[indx] = record.tlast_wrong or now_date
        else:
            self.last_right[indx] = record.tlast_right or now_date
            self.last_wrong[indx] = now_date
            self.wrongDate = now_date
        #figure out time-based stats for this q or tag
        right_dur = now_date - self.last_right[indx]
        wrong_dur = now_date - self.last_wrong[indx]
        rightWrong_dur = self.last_right[indx] - self.last_wrong[indx]
        #categorize q or tag based on this performance
        self.cat[indx] = self.categorize(right_dur, wrong_dur, rightWrong_dur)

    def categorize(self, right_dur, wrong_dur, rightWrong_dur):
        """
        given time data, categorize performance on a given question or tag
        """
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
        return cat