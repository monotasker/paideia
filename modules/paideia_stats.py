import calendar
import datetime
from applications.myapp.modules.pytz.__init__ import timezone
from gluon import current, DIV, H4, TABLE, THEAD, TBODY, TR, TD, SPAN
from paideia_exploring import Walk


class Stats(object):
    '''
    Provides various statistics on student performance.
    '''
    Name = "paideia_stats"
    verbose = True

    def __init__(self, user_id):
        if self.verbose: print '\nInitializing Stats object =================='
        self.user_id = user_id
        #assert type(user_id) == str
        self.loglist = self.log_list()

    def active_tags(self):
        if self.verbose: print 'calling Stats.active_tags() ------------------'
        db = current.db
        # TODO: Add a list of the badge titles (tags) to returned object
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
            atags['latest'] = dict((row.tags.id, row.tags.tag)
                                                           for row in latest)
        except Exception, e:
            print 'error in Stats.average():', e
            atags['total'] = "Can't calculate total number of active badges."
            atags['latest'] = "Can't find the most recent badge awarded."

        return atags

    def average(self):
        '''
        Calculates and returns the average score for the student given in
        self.user_id
        '''
        if self.verbose: print 'calling Stats.average() ----------------------'
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
        if self.verbose: print 'calling Stats.categories() -------------------'

        w = Walk()
        print self.user_id
        tags = w._categorize_tags(self.user_id)
        return tags

    def log_list(self):
        """
        Collect and return a dictionary in which the keys are datetime.date()
        objects and the values are an integer representing the number of
        attempt_log entries on that date by the user represented by
        self.user_id.

        These datetimes and totals are corrected from UTC to the user's
        local time zone.
        """
        if self.verbose: print 'calling Stats.log_list() ---------------------'
        debug = True
        db = current.db

        log_query = db(db.attempt_log.name == self.user_id)
        logs = log_query.select(db.attempt_log.dt_attempted)
        loglist = {}

        #offset from utc time used to generate and store time stamps
        #TODO: Get utc time offset dynamically from user's locale
        print db.auth_user[self.user_id]
        tz_name = db.auth_user[self.user_id].time_zone[0]
        tz = timezone(tz_name)
        if debug:
            print 'timezone =', tz

        # count the number of attempts for each unique date
        for log in logs:
            newdatetime = tz.fromutc(log.dt_attempted)
            newdate = datetime.date(newdatetime.year,
                                    newdatetime.month,
                                    newdatetime.day)
            if newdate in loglist:
                loglist[newdate] += 1
            else:
                loglist[newdate] = 1

        return loglist

    def monthstats(self, year=None, month=None):
        '''
        Assemble and return a dictionary with the weeks. If the year and
        month desired are not supplied as arguments (in integer form),
        this method will by default provide stats for the current month and
        year.
        '''
        if self.verbose: print 'calling Stats.monthstats() -------------------'
        debug = True

        # get current year and month as default
        if not month:
            month = datetime.date.today().month
        if not year:
            year = datetime.date.today().year

        # use calendar module to get month structure
        monthcal = calendar.monthcalendar(year, month)

        monthdict = {'year': year, 'month_name': month}

        month_list = []
        #build nested list containing stats organized into weeks
        for week in monthcal:
            week_list = []
            for day in week:
                day_set = [day, 0]

                for dtime, count in self.loglist.items():
                    if dtime.month == month and dtime.day == day:
                        day_set[1] = count

                week_list.append(day_set)
            week_list.sort(key=lambda k: k[0])
            month_list.append(week_list)
        month_list.sort(key=lambda k: k[0])

        if debug: print month_list
        monthdict['calstats'] = month_list

        return monthdict

    def monthcal(self, year=None, month=None):
        '''
        Assemble and return an html calendar displaying the number of
        attempts per day in the month 'month' for the user represented
        by self.user_id.

        The calendar is returned as a web2py DIV helper.
        '''
        debug = True
        db = current.db
        # TODO: get settings for this user's class requirements
        memberships = db(
                        (db.auth_group.id == db.auth_membership.group_id)
                        & (db.auth_membership.user_id == self.user_id)
                        ).select()
        if debug: print memberships

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
        for week in data['calstats']:
            weekrow = TR()
            for day in week:
                # add table cell for this day
                weekrow.append(TD(_id=str(week) + '-' + str(day[0])))
                # append span with day number
                weekrow[-1].append(SPAN(str(day[0]),
                                    _class='cal_num'))
                # append a span with the day's attempt-count (if non-zero)
                if day[1] != 0:
                    weekrow[-1].append(SPAN(str(day[1]),
                                        _class='cal_count'))
            tb.append(weekrow)  # append week to table body
            if debug: print 'weekrow =', weekrow

        tbl.append(tb)
        mcal.append(tbl)

        #TODO: Add weekly summary counts to the end of each table
        #row (from self.dateset)

        return mcal
