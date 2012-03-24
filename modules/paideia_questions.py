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

