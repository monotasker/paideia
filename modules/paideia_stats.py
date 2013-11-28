import calendar
import datetime
import dateutil.parser
import traceback
from pytz import timezone
from gluon import current, DIV, H4, TABLE, THEAD, TBODY, TR, TD, SPAN, A, URL
from paideia_utils import send_error, make_json
from pprint import pprint
#import logging
import itertools
#logger = logging.getLogger('web2py.app.paideia')


class Stats(object):
    '''
    Provides various statistics on student performance.

    Allows reporting on:
        - badges/level

        - trw/day/badge
        - trw/day/level
        - trw/day/set
        - trw/day/step

        - attempts/day (total)
        - attempts/day/level, badge, set, step

        - count badges over time (total, by set, by level)
        Flag:
            - repeated steps the same day
            - excessive changes in stats
    '''
    Name = "paideia_stats"

    def __init__(self, user_id=None, auth=None, cache=None, duration=None):
        """
        Initialize Stats object for tracking paideia user statistics.

        At this stage compiles
        - basic user information (user_id, auth_user row, readable name)
        - tag_progress information (dict)
        - user's tag records,
        """
        db = current.db
        auth = current.auth
        self.alerts = {}

        # user info
        user_id = auth.user_id if user_id is None else user_id
        self.user_id = user_id
        self.user = db.auth_user(user_id)
        self.name = '{}, {}'.format(self.user.last_name, self.user.first_name)

        # overall progress through tag sets and levels
        self.tag_progress = db(db.tag_progress.name == self.user_id
                               ).select().first().as_dict()
        #if len(self.tag_progress) > 1:
            #ids = [t.id for t in self.tag_progress]
            #self.alerts['duplicate tag_progress rows'] = ids

        # performance on each tag
        print 'init: starting to get self.tag_recs'
        self.tag_recs = db(db.tag_records.name == self.user_id
                           ).select(cacheable=True)
        dups = {}
        for t in self.tag_recs:
            if t.tag in dups.keys():
                dups[t.tag] += 1
            else:
                dups[t.tag] = 1
        dups = {k: v for k, v in dups.iteritems() if v > 1}
        if dups:
            self.alerts['duplicate tag_records rows'] = dups

        # date of each tag promotion
        self.badges_begun = db(db.badges_begun.name == self.user_id).select()
        if len(self.badges_begun) > 1:
            self.alerts['duplicate badges_begun records'] = [bb.id for bb
                                                        in self.badges_begun]

        # log of individual attempts for duration (default is 30 days)
        self.duration = datetime.timedelta(days=30) \
                        if not duration else duration
        self.utcnow = datetime.datetime.utcnow()
        self.cutoff = self.utcnow - self.duration
        self.logs, self.loglist = self.log_list(self.cutoff)

    def get_name(self):
        """
        Return the specified user's name as a single string, last name first.
        """
        return self.name

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

    def step_log(self, logs=None, user_id=None, duration=None):
        '''
        Get record of a user's steps attempted in the last seven days.

        TODO: move this aggregate data to a db table "user_stats" on calculation.
        '''
        db = current.db
        now = self.utcnow
        user_id = self.user_id
        duration = self.duration
        logs = self.logs

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
                #print traceback.format_exc(5)
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
            print 'step', steprow['id'], 'has tags', steprow['tags']
            for t in steprow['tags']:
                if not t in tag_badges.keys():
                    print 'There seems to be no badge for tag {}'.format(t)
                    print 'Removing tag'
                    newtags = steprow['tags']
                    newtags.remove(t)
                    print 'new tags are', newtags
                    db.steps[step] = {'tags': newtags}  # shorthand update
                    mail = current.mail
                    mail.send(mail.settings.sender,
                            'Paideia error: Removed bad tag',
                            'There seems to be no badge for tag {}. That tag '
                            'number has been removed from step '
                            '{}'.format(t, steprow['id']))
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

    def add_progress_data(self, tag_recs):
        """
        Return list of tag records with additional fields for progress data.
        """
        missing_cat = []
        missing_rev = []
        for t in tag_recs:
            tid = t.tag
            try:
                t['current_level'] = [k for k, v
                                      in self.tag_progress.iteritems()
                                      if k in ['cat1', 'cat2', 'cat3', 'cat4']
                                      and tid in v][0][3:]
            except IndexError:
                t['current_level'] = 1
                missing_cat.append(tid)
            try:
                t['review_level'] = [k for k, v
                                     in self.tag_progress.iteritems()
                                     if k in ['rev1', 'rev2', 'rev3', 'rev4']
                                     and tid in v][0][3:]
            except IndexError:
                t['review_level'] = 1
                missing_rev.append(tid)

        return tag_recs

    def add_tag_data(self, tag_recs):
        """
        Return list of tag records with additional fields for tag information.
        """
        db = current.db
        for t in tag_recs:
            try:
                if t.tag.tag_position > 100:
                    t['set'] = None
                else:
                    t['set'] = t.tag.tag_position
                print t['set']
            except RuntimeError:
                print 'no tag position for tag', t.tag
                t['set'] = None
            try:
                t['slides'] = t.tag.slides
            except RuntimeError:
                print 'no slides for tag', t.tag
                t['slides'] = None
            try:
                t['badge_name'] = db(db.badges.tag == t.tag).select().first().badge_name
            except:
                RuntimeError
                print 'no badge for tag {}'.format(t.tag)
                t['badge_name'] = 'missing badge for tag {}'.format(t.tag)
        return tag_recs

    def add_promotion_data(self, tag_recs):
        """
        Return list of tag records with additional fields for promoriont data.

        New fields are:
            - dt_cat1, dt_cat2, dt_cat3, dt_cat4
            - prettydate_cat1, prettydate_cat2, prettydate_cat3,
              prettydate_cat4
        """
        for t in tag_recs:
            try:
                bb = [b for b in self.badges_begun if b.tag == t['tag']][0]
            except IndexError:
                bb = None
            for k in range(1,5):
                nka = 'dt_cat{}'.format(k)
                dt = bb.cat1 if bb else 'n/a'
                nkb = 'prettydate_cat{}'.format(k)
                pdt = dt.strftime('%b %e, %Y') \
                        if isinstance(dt, datetime.datetime) else 'n/a'
                t.update({nka: dt, nkb: pdt})
        return tag_recs

    def active_tags(self):
        '''
        Find the tags that are currently active for this user, categorized 1-4.
        '''
        tr = self.tag_recs
        try:
            tr = self.add_progress_data(tr)
            tr = self.add_tag_data(tr)
            tr = self.add_promotion_data(tr)
            for t in tr:
                t['logs'] = [l.as_dict() for l in self.logs if t['tag'] in l.step.tags]
            self.tag_recs = tr
            return make_json(tr.as_list())
        except Exception:
            print traceback.format_exc(5)
            return None

    def logs_with_tagrecs(self, tag_recs):
        """
        Returns a flattened list of log entries cross-referenced with tag data.

        The resulting list represents attempts for each tag. This means that
        multiple entries may represent a single actual step attempt (since the
        step could have multiple tags). The following reductions will help to
        extract necessary data:
            attempts by step:         count # for each "step" & "dt_attempted"
                                      value, grouped by date
            attempts by date:         count occurrences of each "dt_attempted"
                                      value
            attempts by step by date: count occurrences of each "step" and
                                      "dt_attempted" combination
            attempts by tag by date:  count occurrences of each "tag" and
                                      "dt_attempted" combination
            attempts by set by date:  ???
            attempts by level by date:???
            progress for each tag:    first row for each row['tag'] value
            progress for each step:    first row for each row['step'] value
            badges by level
        """
        fl = []
        logs = self.logs
        pprint(tag_recs)
        for l in logs:
            for tag in l.step.tags:
                myl = l.as_dict()
                myl['tag'] = tag
                tagrec = [trow for trow in tag_recs if trow['tag'] == tag]
                pprint(tagrec)
                if not tagrec:
                    continue
                else:
                    print tag
                    myl.update(tagrec[0])
                    fl.append(myl)
        return make_json(fl)

    def get_max(self):
        """
        Return an integer corresponding to the user's furthest badge set.

        The 'badge set' is actually the series of ints in db.tags.tag_position.
        """
        max_set = self.tag_progress['latest_new'] \
                  if self.tag_progress['latest_new'] else 1
        return max_set

    def log_list(self, cutoff):
        """
        Collect and return a dictionary in which the keys are datetime.date()
        objects and the values are an integer representing the number of
        attempt_log entries on that date by the user represented by
        self.user_id.

        These datetimes and totals are corrected from UTC to the user's
        local time zone.
        """
        db = current.db
        logs = db((db.attempt_log.name == self.user_id) &
                  (db.attempt_log.dt_attempted >= self.cutoff)).select()
        loglist = {}

        for log in logs:
            newdatetime = self.user.tz_obj.localize(log.dt_attempted)
            newdate = datetime.date(newdatetime.year,
                                    newdatetime.month,
                                    newdatetime.day)
            log.dt_local = newdate
            if newdate in loglist:
                loglist[newdate] += 1
            else:
                loglist[newdate] = 1
            if not log.dt_local:
                log.dt_local = 'n/a'

        return logs, loglist

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

        monthdict['calstats'] = month_list

        return monthdict

    def monthcal(self, year=None, month=None):
        '''
        Assemble and return an html calendar displaying the number of
        attempts per day in the month 'month' for the user represented
        by self.user_id.

        The calendar is returned as a web2py DIV helper.
        '''
        # TODO: get settings for this user's class requirements

        # get current year and month as default
        if not month:
            month = datetime.date.today().month
        else: month = int(month)
        if not year:
            year = datetime.date.today().year
        else: year = int(year)

        # get structured data to use in building table
        data = self.monthstats(year, month)

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


def week_bounds():
    '''
    Return datetime objects representing the last day of this week and previous.
    '''
    today = datetime.datetime.utcnow()
    thismonth = calendar.monthcalendar(today.year, today.month)

    thisweek = [w for w in thismonth if today.day in w][0]
    today_index = thisweek.index(today.day)
    tw_index = thismonth.index(thisweek)

    lastweek = thismonth[tw_index - 1]
    delta = datetime.timedelta(days=(8 + today_index))
    lw_firstday = today - delta

    tw_prev = None
    if 0 in thisweek:
        if thisweek.index(0) < thisweek.index(today.day):
            lastmonth = calendar.monthcalendar(today.year, today.month - 1)
            tw_prev = lastmonth[-1]
            lastweek = lastmonth[-2]
            thisweek = [d for d in itertools.chain(thisweek, tw_prev) if d != 0]

    lw_prev = None
    if 0 in lastweek:
        lastmonth = calendar.monthcalendar(today.year, today.month - 1)
        lw_prev = lastmonth[-1]
        lastweek = [d for d in itertools.chain(lastweek, lw_prev) if d != 0]

    return lastweek, lw_firstday, thisweek


def get_offset(user):
    '''
    Return the user's offset from utc time based on their time zone.
    '''
    #today = datetime.datetime.utcnow()
    #now = timezone('UTC').localize(today)
    #tz_name = user.auth_user.time_zone if user.auth_user.time_zone \
        #else 'America/Toronto'
    #offset = now - timezone(tz_name).localize(today)  # when to use "ambiguous"?
    return user.auth_user.offset
