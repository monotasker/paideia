class paideia_stats:
    # calculates stats for paideia student performance
    Name = "paideia_stats"
    def __init__(self, user_id):
        # These values are created
        # when the class is instantiated.
        self.user_id = user_id

        try:
            attempts = db(db.attempt_log.name == self.user_id).select()
            s=db.attempt_log.score.sum()
            row = db(db.attempt_log.name == self.user_id).select(s).first()
            answer = row[s]
            self.score_avg = round(answer/len(attempts)*100, 1)
        except:
            self.score_avg = "Can't calculate average"

        # get statistics for different classes of questions
        the_records = db(db.question_records.name == self.user_id).select()
        self.total_len = float(len(the_records))

        try:
            cat1 = db((db.question_records.name == self.user_id) & (db.question_records.category == 1)).select()
            self.total_cat1 = len(cat1)
            self.percent_cat1 = round((int(self.total_cat1)/self.total_len)*100, 1)
        except:
            self.total_cat1 = "Can't calculate number"
            self.percent_cat1 = ""
        try:
            cat2 = db((db.question_records.name == self.user_id) & (db.question_records.category == 2)).select()
            self.total_cat2 = len(cat2)
            self.percent_cat2 = round((int(self.total_cat2)/self.total_len)*100, 1)
        except:
            self.total_cat2 = "Can't calculate number"
            self.percent_cat2 = ""
        try:
            cat3 = db((db.question_records.name == self.user_id) & (db.question_records.category == 3)).select()
            self.total_cat3 = len(cat3)
            self.percent_cat3 = round((int(self.total_cat3)/self.total_len)*100, 1)
        except:
            self.total_cat3 = "Can't calculate number"
            self.percent_cat3 = ""
        try:
            cat4 = db((db.question_records.name == self.user_id) & (db.question_records.category == 4)).select()
            self.total_cat4 = len(cat4)
            self.percent_cat4 = round((int(self.total_cat4)/self.total_len)*100, 1)
        except:
            self.total_cat4 = "Can't calculate number"
            self.percent_cat4 = ""
