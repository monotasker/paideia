import calendar
import datetime
import dateutil.parser
import traceback
from pytz import timezone
from gluon import current, DIV, H4, TABLE, THEAD, TBODY, TR, TD, SPAN, A, URL
from pprint import pprint
#from guppy import hpy
import logging
logger = logging.getLogger('web2py.app.paideia')
logger.setLevel(logging.DEBUG)


class Stats(object):
    '''
    Provides various statistics on student performance.
    '''
    Name = "paideia_stats"
    verbose = False

    def __init__(self, user_id=None, auth=None, cache=None):
        if self.verbose: print '\nInitializing Stats object =================='
        if auth is None:
            auth = current.auth
        if user_id is None:
            user_id = auth.user_id
        self.user_id = user_id
        self.loglist = self.log_list()
        db = current.db
        self.tag_badges = {tb.tags.id: {'badge': tb.badges.badge_name,
                                        'description': tb.badges.description,
                                        'tag': tb.tags.tag}
                           for tb in db(db.tags.id == db.badges.tag
                                        ).select(cache=(cache.ram, 360000),
                                                 cacheable=True)}

    def store_stats(self, user_id, weekstart, weekstop, weeknum):
        '''
        Store aggregate user statistics on a weekly basis to speed up analysis.
        weekstart and weekstop should be datetime.datetime objects
        TODO: Should there also be an annual aggregate?
        '''
        db = current.db
        monthdays = calendar.Calendar().monthdatescalendar(weekstart.year,
                                                           weekstart.month)
        weekdays = [w for w in monthdays if weekstart.date() in w][0]
        weeklogs_q = db((db.user_stats.name == user_id) &
                        (db.user_stats.year == weekstart.year) &
                        (db.user_stats.week == weeknum))
        # FIXME: adjust for time zones (convert weekstart and weekstop)
        if weeklogs_q.empty():
            mylogs = db((db.attempt_log.name == user_id) &
                        (db.attempt_log.dt_attempted >= weekstart) &
                        (db.attempt_log.dt_attempted <= weekstop)
                        ).select().as_list()
            logsright = [s for s in mylogs if abs(s['score'] - 1) < 0.001]
            myargs = {'logs_right': [l['id'] for l in logsright]}
            logswrong = [s for s in mylogs if abs(s['score'] - 1) >= 0.001]
            myargs['logs_wrong'] = [l['id'] for l in logswrong]
            for n in range(7):
                mykey = 'day{}'.format(n + 1)
                myval = [l for l in mylogs
                         if l['dt_attempted'].day == weekdays[n].day]
                myargs.update({mykey: myval})
        else:
            weeklogs_s = weeklogs_q.select().as_list()
            assert len(weeklogs_s) == 1
            mylog = weeklogs_s[0]
            updated = mylog['updated']
            if updated < weekstop:
                # TODO: Is there a risk of double-counting records with same
                # datetime?
                mylogs = db((db.attempt_log.name == user_id) &
                            (db.attempt_log.dt_attempted >= updated) &
                            (db.attempt_log.dt_attempted <= weekstop)
                            ).select().as_list()

    def step_log(self, logs=None, user_id=None, duration=None, db=None):
        '''
        Get record of a user's steps attempted in the last seven days.

        TODO: move this aggregate data to a db table "user_stats" on calculation.
        '''
        now = datetime.datetime.utcnow()
        if not user_id:
            user_id = self.user_id
        if not duration:
            duration = datetime.timedelta(days=7)
        if not db:
            db = current.db
        if not logs:
            logstart = now - duration  # yields datetime obj
            logs = db((db.attempt_log.name == user_id) &
                      (db.attempt_log.dt_attempted >= logstart)
                      ).select().as_list()

        #TODO: Get utc time offset dynamically from user's locale
        logset = []
        stepset = set(l['step'] for l in logs)
        tag_badges = self.tag_badges

        for step in stepset:
            steprow = db.steps[step].as_dict()
            print 'got_steprow'
            steplogs = [l for l in logs if l['step'] == step]
            print 'got_steplogs'
            stepcount = len(steplogs)
            stepright = [s for s in steplogs if abs(s['score'] - 1) < 0.001]
            stepwrong = [s for s in steplogs if abs(s['score'] - 1) >= 0.001]

            try:
                last_wrong = max([s['dt_attempted'] for s in stepwrong if
                                 s['dt_attempted']])
                if isinstance(last_wrong, str):
                    last_wrong = dateutil.parser.parse(last_wrong)
                last_wrong = datetime.datetime.date(last_wrong)
            except ValueError:
                print traceback.format_exc(5)
                last_wrong = 'never'

            try:
                right_since = len([s for s in stepright
                                if s['dt_attempted'] > last_wrong])
            except TypeError:
                right_since = stepcount
            steptags = {t: {'tagname': tag_badges[t]['tag'],
                            'badge': tag_badges[t]['badge'],
                            'description': tag_badges[t]['description']}
                        for t in steprow['tags']
                        if t in tag_badges.keys()}
            # check for tags without badges
            # TODO: move this check to maintenance cron job
            for t in steprow['tags']:
                if not t in tag_badges.keys():
                    print 'There seems to be no badge for tag {}'.format(t)
                    mail = current.mail
                    mail.send(mail.settings.sender,
                            'Paideia error: Missing badge',
                            'There seems to be no badge for tag {}'.format(t))
            step_dict = {'step': step,
                         'count': stepcount,
                         'right': len(stepright),
                         'wrong': len(stepwrong),
                         'last_wrong': last_wrong,
                         'right_since': right_since,
                         'tags': steptags,
                         'prompt': steprow['prompt'],
                         'logs': steplogs}
            logset.append(step_dict)

        return {'loglist': logset, 'duration': duration}

    def active_tags(self):
        '''
        Find the tags that are currently active for this user, categorized 1-4.
        '''
        if self.verbose: print 'calling Stats.active_tags() ------------------'
        db = current.db
        #debug = False
        #try:
        atag_s = db(db.tag_progress.name == self.user_id).select().first()
        atags = {}
        atags1 = atags['cat1'] = list(set(atag_s.cat1))  # remove dup's
        atags2 = atags['cat2'] = list(set(atag_s.cat2))
        atags3 = atags['cat3'] = list(set(atag_s.cat3))
        atags4 = atags['cat4'] = list(set(atag_s.cat4))
        #atags5 = atags['rev1'] = list(set(atag_s.rev1))  # remove dup's
        #atags6 = atags['rev2'] = list(set(atag_s.rev2))
        #atags7 = atags['rev3'] = list(set(atag_s.rev3))
        #atags8 = atags['rev4'] = list(set(atag_s.rev4))
        for c, lst in atags.iteritems():
            # allow for possibility that tag hasn't got badge yet
            try:
                atags[c] = [self.tag_badges[t]['badge'] for t in lst
                            if t in self.tag_badges.keys()]
            except AttributeError:
                # TODO: send notice here
                pass
        try:
            total = []
            for c in [atags1, atags2, atags3, atags4]:
                if c: total.extend(c)
            atags['total'] = len(total)
        except Exception:
            print Exception
            print 'hi \n'
            atags['total'] = 'an unknown number of'

        latest_rank = atag_s.latest_new
        # fix any leftover records with latest rank stuck at 0
        if latest_rank == 0:
            atag_s.update_record(latest_new=1)
            latest_rank = 1
        latest_tags = db(db.tags.position == latest_rank).select()
        if latest_tags is None:
            latest_badges = ['Sorry, I can\'t find them!']
        else:
            latest_badges = []
            for t in latest_tags:
                l = self.tag_badges[t.id]
                if l:
                    latest_badges.append(l['badge'])
                else:
                    pass
            if latest_badges is None:
                latest_badges = ['Sorry, I couldn\'t find that!']
            atags['latest'] = latest_badges
        #except Exception, e:
            #print type(e), e
            #atags['total'] = "Can't calculate total number of active badges."
            #atags['latest'] = ["Can't find the most recent badge awarded."]

        return atags

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
        #debug = False
        db = current.db

        log_query = db(db.attempt_log.name == self.user_id)
        logs = log_query.select(db.attempt_log.dt_attempted)
        loglist = {}

        #offset from utc time used to generate and store time stamps
        tz_name = db.auth_user[self.user_id].time_zone
        tz = timezone(tz_name)

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
        debug = False

        # get current year and month as default
        if not month:
            month = datetime.date.today().month
        if not year:
            year = datetime.date.today().year

        # use calendar module to get month structure
        monthcal = calendar.monthcalendar(year, month)
        if debug: pprint(monthcal)

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
            month_list.append(week_list)

        if debug: pprint(month_list)
        monthdict['calstats'] = month_list

        return monthdict

    def monthcal(self, year=None, month=None):
        '''
        Assemble and return an html calendar displaying the number of
        attempts per day in the month 'month' for the user represented
        by self.user_id.

        The calendar is returned as a web2py DIV helper.
        '''
        debug = False
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
        else: month = int(month)
        if not year:
            year = datetime.date.today().year
        else: year = int(year)

        # get structured data to use in building table
        data = self.monthstats(year, month)
        if debug: print 'data=', data

        nms = calendar.month_name
        monthname = nms[data['month_name']]

        # Create wrapper div with title line and month name
        mcal = DIV(SPAN('Questions answered each day in',
                        _class='monthcal_intro_line'),
                   _class='paideia_monthcal')

        tbl = TABLE(_class='paideia_monthcal_table')
        tbl.append(THEAD(TR('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')))
        tb = TBODY()
        for week in data['calstats']:
            weeknum = data['calstats'].index(week)
            weekrow = TR()
            for day in week:
                # add table cell for this day
                weekrow.append(TD(_id='{}-{}'.format(weeknum, day[0])))
                # append empty span if no day number
                if day[0] == 0:
                    weekrow[-1].append(SPAN('', _class='cal_num'))
                else:
                    weekrow[-1].append(SPAN(str(day[0]),
                                    _class='cal_num'))
                # append a span with the day's attempt-count (if non-zero)
                if day[1] != 0:
                    weekrow[-1].append(SPAN(str(day[1]),
                                        _class='cal_count'))
            tb.append(weekrow)  # append week to table body
            if debug: print 'weekrow =', weekrow

        # build nav link for previous month
        prev_month = (month - 1) if month > 1 else 12
        if prev_month == 12:
            prev_year = year - 1
        else:
            prev_year = year
        prev_link = A('previous', _href=URL('reporting', 'calendar.load',
                                            args=[self.user_id,
                                                  prev_year,
                                                  prev_month]),
                      _class='monthcal_prev_link',
                      cid='tab_calendar')
        mcal.append(prev_link)

        # build nav link for next month
        next_month = (month + 1) if month < 12 else 1
        if next_month == 1:
            next_year = year + 1
        else:
            next_year = year

        next_link = A('next', _href=URL('reporting', 'calendar.load',
                                        args=[self.user_id,
                                              next_year,
                                              next_month]),
                      _class='monthcal_next_link',
                      cid='tab_calendar')
        mcal.append(next_link)
        mcal.append(H4(monthname))

        tbl.append(tb)
        mcal.append(tbl)

        #TODO: Add weekly summary counts to the end of each table
        #row (from self.dateset)

        return mcal
