import calendar, datetime
from gluon import current, DIV
from paideia_exploring import Walk


class Stats(object):
    '''
    Provides various statistics on student performance.
    '''
    Name = "paideia_stats"

    def __init__(self, user_id):

        self.user_id = user_id
        #assert type(user_id) == StringType
        self.loglist = self.log_list()

    def average(self):
        '''
        Calculates and returns the average score for the student given in
        self.user_id
        '''
        db = current.db

        try:
            attempts = db(db.attempt_log.name == self.user_id).select()
            s=db.attempt_log.score.sum()
            row = db(db.attempt_log.name == self.user_id).select(s).first()
            answer = row[s]
            avg = round(answer/len(attempts)*100)
        except Exception, e:
            print 'error in Stats.average():', e
            avg = "Can't calculate average"

        return avg

    def categories(self):
        """
        Collects and returns the number of tags that are currently in each
        of the four performance categories for the student given in
        self.user_id.

        The categories range from 1 (need immediate review) to 4 (no review
        needed).

        Returns a dictionary with four keys corresponding to the four
        categories. The value for each key is a list holding the id's
        (integers) of the tags that are currently in the given category.

        """
        w = Walk()
        tags = w.categorize_tags(self.user_id)
        return tags

    def log_list(self):
        """
        Collect and return a dictionary in which the keys are datetime.date()
        objects and the values are an integer representing the number of
        attempt_log entries on that date by the user represented by
        self.user_id.

        These datetimes and totals are corrected from UTC to EST (UTC -5).
        """

        session, db = current.session, current.db

        log_query = db(db.attempt_log.name == self.user_id)
        logs = log_query.select(db.attempt_log.dt_attempted)
        loglist = {}

        #offset from utc time used to generate and store time stamps
        #TODO: Get utc time offset dynamically from user's locale
        utcvar = -5

        # count the number of attempts for each unique date
        for log in logs:
            newdatetime = log.dt_attempted + datetime.timedelta(hours=utcvar)
            newdate = datetime.date(newdatetime.year,
                                    newdatetime.month,
                                    newdatetime.day)
            if newdate in loglist:
                loglist[newdate] += 1
            else:
                loglist[newdate] = 1

        return loglist

    def cal(self, year=None):
        '''
        Assemble a full year calendar.
        '''
        if not year:
            #get the current year as default
            this_year = datetime.date.today().year

    def monthstats(self, year=None, month=None):
        '''
        Assemble and return a dictionary with the weeks. If the year and
        month desired are not supplied as arguments (in integer form),
        this method will by default provide stats for the current month and
        year.
        '''
        # get current year and month as default
        if not month:
            month = datetime.date.today().month
        if not year:
            year = datetime.date.today().year

        # use calendar module to get month structure
        monthcal = calendar.monthcalendar(this_year, month)

        monthdict = {'year':this_year, 'month_name':month}

        date_set = {}
        #build dict containing stats organized into weeks
        for week in monthcal:
            weekday = week[0]
            date_set[weekday] = {}
            for day in week:
                w[day] = 0

            for dt, count in self.loglist.items():
                if dt.month == month and dt.day in week:
                    w[dt.day] = count

        monthdict[weeks] = date_set

        return monthdict

    def monthcal(self, year, month):
        '''
        Assemble and return an html calendar displaying the number of
        attempts per day in the month 'month' for the user represented
        by self.user_id.

        The calendar is returned as a web2py DIV helper.
        '''
        data = self.monthdict(year, month)

        # get current year and month as default
        if not month:
            month = datetime.date.today().month
        if not year:
            year = datetime.date.today().year

        htmlcal = DIV()

        #now build html calendar as string with stats embedded
        nms = calendar.month_name
        monthname = nms[month]
        htmlcal.append(H4(monthname))

        self.htmlcal += '<h4>' + monthname + '</h4><table class="weeklycount">'
        self.htmlcal += '<theader><tr><td>Mon</td><td>Tue</td><td>Wed</td><td>Thu</td><td>Fri</td><td>Sat</td><td>Sun</td></tr></theader>'
        for week in monthcal:
            w = week[0]
            self.htmlcal += '<tr>'
            if (month in self.dateset) and (w in self.dateset[month]):
                the_m = self.dateset[month]
                the_w = the_m[w]
                for day in week:
                    self.htmlcal+= '<td>'
                    self.htmlcal+= '<span class="cal_num">' + str(day) + '</span>'
                    if day in the_w:
                        self.htmlcal+='<span class="cal_count">' + str(the_w[day]) + '</span>'
                    self.htmlcal+= '</td>'
            else:
                for day in week:
                    self.htmlcal+= '<td>'
                    self.htmlcal+= '<span class="cal_num">' + str(day) + '</span>'
                    self.htmlcal+= '</td>'
            self.htmlcal += '</tr>'
        self.htmlcal += '</table>'
        #TODO: Add weekly summary counts to the end of each table
        #row (from self.dateset)

        return htmlcal


