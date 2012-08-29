import calendar
import datetime
from gluon import current, DIV, H4, TABLE, THEAD, TBODY, TR, TD, SPAN
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

    def active_tags(self):
        db = current.db

        try:
            atag_q = db(
                        (db.tag_records.name == self.user_id)
                        & (db.tag_records.tag == db.tags.id)
                        )
            atag_rows = atag_q.select(orderby=db.tags.position)
            atags = {'total': len(atag_rows)}
            furthest = atag_rows.last()
            latest = atag_rows.find(lambda row:
                                row.tags.position == furthest.tags.position)
            atags['latest'] = {r.tags.id:r.tags.tag for r in latest}
        except Exception, e:
            print 'error in Stats.average():', e
            atags['total'] = "Can't calculate total number of active tags"
            atags['latest'] = "Can't find the most recent tags reached"

        return atags

    def average(self):
        '''
        Calculates and returns the average score for the student given in
        self.user_id
        '''
        db = current.db

        try:
            attempts = db(db.attempt_log.name == self.user_id).select()
            s = db.attempt_log.score.sum()
            row = db(db.attempt_log.name == self.user_id).select(s).first()
            answer = row[s]
            avg = round(answer / len(attempts) * 100)
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
        tags = w._categorize_tags(self.user_id)
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
        monthcal = calendar.monthcalendar(year, month)

        monthdict = {'year': year, 'month_name': month}

        date_set = {}
        #build dict containing stats organized into weeks
        for week in monthcal:
            weekday = week[0]
            date_set[weekday] = {}
            for day in week:
                date_set[weekday][day] = 0

            for dtime, count in self.loglist.items():
                if dtime.month == month and dtime.day in week:
                    date_set[weekday][dtime.day] = count

        monthdict['calstats'] = date_set

        return monthdict

    def monthcal(self, year=None, month=None):
        '''
        Assemble and return an html calendar displaying the number of
        attempts per day in the month 'month' for the user represented
        by self.user_id.

        The calendar is returned as a web2py DIV helper.
        '''
        db = current.db
        auth = current.auth
        # get settings for this user's class requirements
        memberships = db(
                        (db.auth_group.id == db.auth_membership.group_id)
                        & (db.auth_membership.user_id == self.user_id)
                        ).select()

        # get current year and month as default
        if not month:
            month = datetime.date.today().month
        if not year:
            year = datetime.date.today().year

        data = self.monthstats(year, month)
        print 'DEBUG: in Stats.cal(), data=', data

        nms = calendar.month_name
        monthname = nms[data['month_name']]
        mcal = DIV(H4(monthname), _class='paideia_monthcal')

        tbl = TABLE(_class='paideia_monthcal_table')
        tbl.append(THEAD(TR('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')))
        tb = TBODY()
        for week, days in data['calstats'].iteritems():
            weekrow = TR()
            for day in days:
                # add table cell for this day
                weekrow.append(TD(_id=str(week) + '-' + str(day)))
                # append span with day number
                weekrow[-1].append(SPAN(str(day),
                                    _class='cal_num'))
                # append a span with the day's attempt-count (if non-zero)
                if days[day] != 0:
                    weekrow[-1].append(SPAN(str(days[day]),
                                        _class='cal_count'))
            tb.append(weekrow) # append week to table body

        tbl.append(tb)
        mcal.append(tbl)

        #TODO: Add weekly summary counts to the end of each table
        #row (from self.dateset)

        return mcal


