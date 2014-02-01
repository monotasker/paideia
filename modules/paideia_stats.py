import calendar
import datetime
from collections import Counter
import dateutil.parser
import traceback
#from pytz import timezone
from gluon import current, DIV, SPAN, A, URL, UL, LI, B
from gluon import TAG
from paideia_utils import make_json
#from pprint import pprint
#import logging
import itertools
#logger = logging.getLogger('web2py.app.paideia')


class Stats(object):
    '''
    Provides various statistics on student performance.

    Exposes the following methods as its public interface:

    :active_tags():         Returns
    :get_max():             Returns the user's current set
    :get_sets():            Returns a list of the tag id's in each of the four
                                categories, along with their badge names.
    :tags_over_time():      Returns a dictionary of dates with the number of
                                attempts for each active tag on that date.
    :sets_over_time():
    :paths_over_time():     Returns a dictionary of dates with the number of
                                attempts for each active tag on that date.
    :monthcal():            Returns an html calendar for one month of user
                                performance stats.
    :store_stats():         Returns True if it successfully collates any
                                fresh performance data for the current user in
                                db.user_stats. Otherwise returns False

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
        msel = db((db.auth_membership.user_id == self.user_id) &
                  (db.auth_membership.group_id == db.auth_group.id)).select()
        try:
            self.targetcount = [m.auth_group.paths_per_day for m in msel
                                if m.auth_group.paths_per_day][0]
        except Exception:
            print traceback.format_exc(5)
            self.targetcount = 20
        self.name = '{}, {}'.format(self.user.last_name, self.user.first_name)

        # overall progress through tag sets and levels
        self.tag_progress = db(db.tag_progress.name == self.user_id
                               ).select().first().as_dict()

        # performance on each tag
        self.tag_recs = db(db.tag_records.name == self.user_id
                           ).select(cacheable=True)
        tags = [rec.tag for rec in self.tag_recs]
        dups = [tag for tag, count in Counter(tags).items() if count > 1]
        if dups:
            self.alerts['duplicate tag_records rows'] = dups

        # date of each tag promotion
        self.badges_begun = db(db.badges_begun.name == self.user_id).select()
        if len(self.badges_begun) > 1:
            self.alerts['duplicate badges_begun records'] = [bb.id for bb
                                                        in self.badges_begun]

        # log of individual attempts for duration (default is 30 days)
        self.duration = datetime.timedelta(days=120) if not duration else duration
        self.utcnow = datetime.datetime.utcnow()
        self.cutoff = self.utcnow - self.duration
        self.logs, self.loglist = self.log_list(self.cutoff)
        print '=========================================='
        print self.user.tz_obj

    def get_name(self):
        """
        Return the specified user's name as a single string, last name first.
        """
        return self.name

    def store_stats(self, user_id, weekstart, weekstop, weeknum):
        '''
        Store aggregate user statistics on a weekly basis to speed up analysis.
        weekstart and weekstop should be datetime.datetime objects
        '''
        # TODO: Should there also be an annual aggregate?
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
        #now = self.utcnow
        #user_id = self.user_id
        duration = self.duration
        logs = self.logs

        logset = []
        stepset = set(l['step'] for l in logs)
        tag_badges = self.tag_badges

        for step in stepset:
            steprow = db.steps[step].as_dict()
            steplogs = [l for l in logs if l['step'] == step]
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
            for k in range(1, 5):
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

        Returns a list of dictionaries, one per active tag for this user. Each
        dictionary includes the following keys:
        - from db.tag_records
            [name]
            [tag]
            [times_right]           double, total number of times right
            [times_wrong]           double, total number of times wrong
            [tlast_wrong]           datetime
            [tlast_right]           datetime
            [secondary_right]       list of datetime objects for successes
                                        where the step had the tag as secondary.
        - calculated
            [rw_ratio]              ratio of times_right to times_wrong as
                                        a double.
            [delta_wrong]           length of time since last wrong answer
            [delta_right]           length of time since last right answer
            [delta_right_wrong]     length of time between last right answer
                                        and previous wrong answer (0 if last
                                        answer was wrong).
        - from db.tag_progress
            [current_level]         highest level attained for tag
            [review_level]          current level used for path selection
        - from db.badges_begun
            [cat1]                  a tuple of (datetime, prettydate string)
            [cat2]                  a tuple of (datetime, prettydate string)
            [cat3]                  a tuple of (datetime, prettydate string)
            [cat4]                  a tuple of (datetime, prettydate string)
        - from db.user_stats


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
        for l in logs:
            for tag in l.step.tags:
                myl = l.as_dict()
                myl['tag'] = tag
                tagrec = [trow for trow in tag_recs if trow['tag'] == tag]
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

    def _local(self, dt):
        """
        Return a datetime object localized to self.user's time zone.

        NB: The pytz.localize function just adds timezone information to the
        utc datetime object. To actually adjust the datetime you need to get
        the local offset from utc and add it manually.
        """
        tz = self.user.tz_obj
        offset = tz.utcoffset(dt)  # handles dst adjustments
        newdt = dt + offset
        return newdt

    def log_list(self, cutoff):
        """
        Return a list of logs and a dict of attempt counts per day.

        The keys of the dict are datetime objects, while the values are
        integers representing the number of attempt_log entries on that date
        by the user represented by self.user_id.

        These datetimes and totals are corrected from UTC to the user's
        local time zone.

        """
        db = current.db
        logs = db((db.attempt_log.name == self.user_id) &
                  (db.attempt_log.dt_attempted >= self.cutoff)).select()
        loglist = {}

        for log in logs:
            print 'UTC time:', log.dt_attempted
            newdt = self._local(log.dt_attempted)
            print 'localized:', newdt
            newdate = datetime.date(newdt.year, newdt.month, newdt.day)
            print 'localized:', newdate
            print '-------------------------------------------------'
            log.dt_local = newdate
            if newdate in loglist:
                loglist[newdate] += 1
            else:
                loglist[newdate] = 1
            if not log.dt_local:
                log.dt_local = 'n/a'

        return logs, loglist

    def monthstats(self, year, month):
        '''
        Assemble and return a dictionary with the weeks. If the year and
        month desired are not supplied as arguments (in integer form),
        this method will by default provide stats for the current month and
        year.
        '''
        daycounts = {k: v for k, v in self.loglist.iteritems()
                     if k.month == month}
        return daycounts

    def monthcal(self, year=None, month=None):
        '''
        Assemble and return an html calendar displaying the number of
        attempts per day in the month 'month' for the user represented
        by self.user_id.

        The calendar is returned as a web2py DIV helper.

        The calendar html structure is:

        <table border="0" cellpadding="0" cellspacing="0" class="month">\n
        <tr>
            <th class="month" colspan="7">December 2013</th>
        </tr>\n
        <tr>
            <th class="sun">Sun</th>
            <th class="mon">Mon</th>
            <th>class="tue">Tue</th>
            <th>class="wed">Wed</th>
            <th>class="thu">Thu</th>
            <th>class="fri">Fri</th>
            <th>class="sat">Sat</th>
        </tr>\n
        <tr>
            <td class="sun">1</td>
            <td class="mon">2</td>
            <td class="tue">3</td>
            <td class="wed">4</td>
            <td class="thu">5</td>
            <td class="fri">6</td>
            <td class="sat">7</td>
        </tr>\n
        ...
        <tr>
            <td class="sun">29</td>
            <td class="mon">30</td>
            <td class="tue">31</td>
            <td class="noday">\xc2\xa0</td>
            <td class="noday">\xc2\xa0</td>
            <td class="noday">\xc2\xa0</td>
            <td class="noday">\xc2\xa0</td>
        </tr>\n
        </table>\n
        '''
        # TODO: get settings for this user's class requirements

        month = datetime.date.today().month if not month else int(month)
        year = datetime.date.today().year if not year else int(year)
        daycounts = self.monthstats(year, month)
        monthname = calendar.month_name[month]

        # Create html calendar and add daily count numbers
        newmcal = calendar.HTMLCalendar(6).formatmonth(year, month)
        mycal = TAG(newmcal)
        for week in mycal.elements('tr'):
            weekcount = 0
            for day in week.elements('td[class!="noday"]'):
                try:
                    mycount = [v for k, v in daycounts.iteritems()
                               if k.day == int(day[0])][0]
                    countspan = SPAN(mycount, _class='daycount')
                    if mycount >= self.targetcount:
                        countspan['_class'] = 'daycount full'
                        weekcount += 1
                    day.append(countspan)
                except (ValueError, IndexError):
                    pass
                day[0] = SPAN(day[0], _class='cal_num')
            if weekcount >= 5:
                week[-1].append(SPAN(_class='icon-ok success'))

        dropdown = self._monthpicker(calendar, year, month, monthname)
        mycal.elements('th.month')[0][0] = dropdown
        for link in self._navlinks(year, month):
            mycal.elements('th.month')[0].insert(0, link)
        wrap = DIV(_class='paideia_monthcal')
        wrap.append(SPAN('Questions answered each day in',
                         _class='monthcal_intro_line'))
        wrap.append(mycal)
        #TODO: Add weekly summary counts to the end of each table

        return wrap

    def _navlinks(self, year, month):
        """
        Return two html anchor elements for navigating to the previous and next
        months.
        """
        prev_month = (month - 1) if month > 1 else 12
        prev_year = year if prev_month < 12 else year - 1
        next_month = (month + 1) if month < 12 else 1
        next_year = year if next_month > 1 else year + 1
        links = {'next': (next_month, next_year, 2,
                          SPAN(_class='icon-chevron-right')),
                 'previous': (prev_month, prev_year, 0,
                              SPAN(_class='icon-chevron-left'))}
        linktags = []
        for k, v in links.iteritems():
            mylink = A(v[3], _href=URL('reporting', 'calendar.load',
                                       args=[self.user_id, v[1], v[0]]),
                       _class='monthcal_nav_link {}'.format(k),
                       cid='tab_calendar')
            linktags.append(mylink)
        return linktags

    def _monthpicker(self, calendar, year, month, monthname):
        """
        Return an html dropdown menu of months since 2011.
        """
        years = range(year, 2011, -1)
        picker_args = {'_class': 'dropdown-menu',
                       '_role': 'menu',
                       '_aria-labelledby': 'month-label'}
        picker = UL(**picker_args)
        for y in years:
            for m in range(12, 1, -1):
                if not (m > month and y == year):
                    picker.append(LI(A('{} {}'.format(calendar.month_name[m], y),
                                    _href=URL('reporting', 'calendar.load',
                                              args=[self.user_id, y, m]),
                                    _tabindex='-1')))
            picker.append(LI(_class='divider'))

        label_args = {'_id': 'month-label',
                      '_role': 'button',
                      '_class': 'dropdown-toggle',
                      '_data-toggle': 'dropdown',
                      '_data-target': '#',
                      '_href': '#'}
        dropdown = SPAN(A('{} {} '.format(monthname, year),
                         B(_class='caret'),
                         **label_args),
                       picker,
                       _class='dropdown')

        return dropdown


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
