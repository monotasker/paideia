import calendar
from collections import defaultdict
from copy import copy
import datetime
from dateutil.parser import parse
import decimal
from gluon import current
from gluon._compat import to_native, integer_types
from gluon.dal import DAL
from gluon.html import XmlComponent
from gluon.languages import lazyT
from itertools import chain, groupby
from memory_profiler import profile
from operator import itemgetter
from plugin_utils import make_json, load_json
from pprint import pprint
from pytz import timezone, utc, BaseTzInfo
import time
import traceback
from typing import Optional

GLOBAL_DEBUG = 0

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

    :set_badges_scale():    Returns a dictionary of set numbers with lists of
                             badges in each set as values. The badges should
                             be represented by a tuple including tag_id,
                             badge_name, and badge_description.
    badge_level_ring - ring chart of badges in each
    badges_time_line - multiple line chart showing number of badges in
                        each level over time.
    attempts_time_line - line chart showing number of attempts per day (week)?
    attempts_step_time_line - stacked area chart showing number of attempts
                                for each step attempted per day.
    attempts_tag_time_line - stacked area chart showing number of attempts
                                for each step attempted per day.
    attempts_set_time_line - stacked area chart showing number of attempts
                                for each step attempted per day.

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

    # @profile
    def __init__(self, user_id=None):
        """
        Initialize Stats object for tracking paideia user statistics.

        At this stage compiles
        - basic user information (user_id, auth_user row, readable name)
        - tag_progress information (dict)
        - user's tag records,

        """
        db = current.db
        auth = current.auth
        self.utcnow = datetime.datetime.utcnow()  # FIXME: calculate locally
        self.alerts = {}

        # user info --------------------------------------------------
        # FIXME: calculate all of this locally
        user_id = auth.user_id if user_id is None else user_id
        self.user_id = user_id
        self.user = db.auth_user(user_id)
        self.name = '{}, {}'.format(self.user.last_name, self.user.first_name)

        # class/group info --------------------------------------------------
        try:
            msel = get_current_class(user_id, self.utcnow)
            self.targetcount = msel.classes.paths_per_day
        except (IndexError, AttributeError):  # no group target for user
            self.targetcount = 20

        # progress through tag sets and levels ---------------------
        # FIXME: retrieve this locally
        try:
            self.tag_progress = db(db.tag_progress.name == self.user_id
                                   ).select().first().as_dict()
        except AttributeError:
            self.tag_progress = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': [],
                                 'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}

        # TODO: find and notify re. duplicate tag_records rows
        # FIXME: Retrieve this locally
        self.badge_levels, self.review_levels = self._find_badge_levels(user_id)
        self.tags = [tup[1] for v in list(self.badge_levels.values())
                     for tup in v]

        # date of each tag promotion
        # FIXME: Retrieve this locally
        self.badges_begun = db(db.badges_begun.name == self.user_id).select()
        if len(self.badges_begun) > 1:
            self.alerts['duplicate badges_begun records'] = [bb.id for bb in
                                                             self.badges_begun]

    def get_name(self):
        """
        Return the specified user's name as a single string, last name first.
        """
        return {"namestring": self.name,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name
                }

    # FIXME: Deprecated and never called
    # def store_stats(self, statsdict, lastdt):
    #     '''
    #     Store aggregate user statistics provided by statsdict in db.weekly_user_stats.

    #     Argument lastdt is the updated datetime of the last user_stats row for
    #     the current user. This is used to determine whether that last row needs
    #     to be completed with data from statsdict.
    #     '''
    #     # TODO: Should there also be an annual aggregate?
    #     db = current.db
    #     data = {}
    #     for year, weeks in list(statsdict.items()):
    #         for weeknum, weekstuff in list(weeks.items()):
    #             dts = sorted(weekstuff[0].keys())
    #             done = 1 if not weeknum == list(weeks.keys())[-1] else 0

    #             weekdata = {'name': self.user_id,
    #                         'year': year,
    #                         'week': weeknum,
    #                         'updated': datetime.datetime.now(),
    #                         'day1': dts[0], 'day2': dts[1], 'day3': dts[2],
    #                         'day4': dts[3], 'day5': dts[4], 'day6': dts[5],
    #                         'day7': dts[6],
    #                         'count1': dts[0], 'count2': dts[1],
    #                         'count3': dts[2], 'count4': dts[3],
    #                         'count5': dts[4], 'count6': dts[5],
    #                         'count7': dts[6],
    #                         'logs_by_tag': make_json(weekstuff[1]),
    #                         'logs_right': weekstuff[2],
    #                         'logs_wrong': weekstuff[3],
    #                         'done': done
    #                         }
    #             # finish any unfinished week
    #             if year == list(statsdict.keys())[0] and \
    #                     weeknum == list(weeks.keys())[0] and \
    #                     lastdt.isocalendar()[1] == list(weeks.keys())[0] and \
    #                     lastdt.isocalendar()[0] == year:
    #                 openrow = db(db.weekly_user_stats.name == self.user_id
    #                              ).select().last()

    #                 weekdata['updated'] = datetime.datetime.now()
    #                 for f in ['count1', 'count2', 'count3', 'count4',
    #                           'count5', 'count6', 'count7']:
    #                     weekdata[f].extend(openrow[f])
    #                 opentags = load_json(openrow['logs_by_tag'])
    #                 for k, v in weekdata['logs_by_tag']:
    #                     weekdata['logs_by_tag'][k].extend(opentags[k])
    #                 weekdata['logs_right'] = weekstuff[2]
    #                 weekdata['logs_wrong'] = weekstuff[3]
    #             # or add new row
    #             data.append(weekdata)

    """
    DEPRECATED
    def step_log(self, logs=None, user_id=None, duration=None):
        '''
        Get record of a user's steps attempted in the last seven days.

        TODO: move this aggregate data to a db table "user_stats"
        on calculation.
        '''
        db = current.db
        # now = self.utcnow
        # user_id = self.user_id
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
                    last_wrong = parse(last_wrong)
                last_wrong = datetime.datetime.date(last_wrong)
            except ValueError:
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
                if t not in tag_badges.keys():
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
    """

    @staticmethod
    def _add_badge_info(tag_recs: list[dict]) -> list[dict]:
        """
        Return add fields for badge information to a list of tag records.

        :param list[dict] tagrecs:  A list of tag_records records serialized
                                    as dictionaries. These are the records
                                    to which the new fields (dict keys/values)
                                    will be added.

        :returns:   Returns the same list provided, now with the following new
                    fields:
                        - set: the badge set for the tag
                        - slides: the lessons related to the tag
                        - bname: the badge name associated with the tag
                        - bdescr: the badge description associated with the tag

        :rtype: list[dict]
        """
        db = current.db
        for t in tag_recs:
            trow = db.tags(t['tag'])
            if not trow:
                brow = None
            else:
                brow = db(db.badges.tag == trow.id).select().first()
            try:
                if trow.tag_position > 100:
                    t['set'] = None
                else:
                    t['set'] = trow.tag_position
            except (RuntimeError, AttributeError):
                t['set'] = None
            try:
                t['slides'] = trow.slides
            except (RuntimeError, AttributeError):
                t['slides'] = None
            try:
                t['bname'] = brow.badge_name
                t['bdescr'] = brow.description
            except (RuntimeError, AttributeError):
                t['bname'] = 'missing badge for tag {}'.format(t['tag'])
                t['bdescr'] = None
        return tag_recs

    @classmethod
    def _add_promotion_data(cls, tag_recs: list[dict], user_id: int,
                            tz: BaseTzInfo) -> list[dict]:
        """
        Add fields for promotion data to a list of tag records.

        :param list[dict] tagrecs:  A list of tag_records records serialized
                                    as dictionaries. These are the records
                                    to which the new fields (dict keys/values)
                                    will be added.

        :returns:   Returns the same list provided, now with the following new
                    fields:
                        - cat1_reached: a tuple of [0] the datetime when the
                                        user first reached cat1, and
                                        [1] a readable formatted string
                                        representation of that datetime
                        - cat2_reached: same for cat2
                        - cat3_reached: same for cat3
                        - cat4_reached: same for cat4

        :rtype: list[dict]
        """
        db = current.db
        badges_begun = db(db.badges_begun.name == user_id).select()

        for idx, t in enumerate(tag_recs):
            try:
                bbrows = [b for b in badges_begun if b.tag == t['tag']][0]
            except IndexError:
                bbrows = None

            for k in range(1, 5):
                cat = 'cat{}'.format(k)
                dt = cls._local(bbrows[cat], tz) \
                        if bbrows and bbrows[cat] else None
                prettydate = dt.strftime('%b %e, %Y') \
                    if isinstance(dt, datetime.datetime) else None
                tag_recs[idx]['{}_reached'.format(cat)] = (dt, prettydate)

        return tag_recs

    @staticmethod
    def _get_avg_score(logs: dict[datetime.datetime, tuple]) -> float:
        """
        Return the user's average score for the supplied attempt logs.

        :param list logs:       A dictionary whose keys are datetimes and
                                whose values are a tuple of right and wrong
                                log ids

        :returns:   The average score for the supplied logs. Always returns a
                    float, since scores are floats between 0 and 1.
        :rtype:     float
        """
        db = current.db
        debug = 0
        mylogids = []
        for r in logs.values():
            mylogids.extend(r[0] + r[1])
        mylogs = db(db.attempt_log.id.belongs(mylogids)
                    ).select(db.attempt_log.score).as_list()
        myscores = [s['score'] for s in mylogs]
        try:
            avg_score = round(sum(myscores) / len(mylogs), 2)
        except ZeroDivisionError:  # if tag not tried at all since startdt
            avg_score = 0.0
        # avg_score = db(db.attempt_log.id.belongs(mylogids)
        #                ).select(db.attempt_log.score.avg())
        if debug: print('avg_score')
        if debug: print(avg_score)
        return avg_score

    @classmethod
    def _get_tag_logs_by_day(cls, user_id: int, offset: datetime.timedelta,
                             tag_id: int, recent_start: datetime.datetime
                             ) -> dict[datetime.datetime, tuple]:
        '''
        Returns the log ids for recent attempts related to a given tag.

        :param int user_id:     id of the user whose records are returned
        :param int tag_id:      id of the tag for which attempts are returned
        :param datetime recentstart:    The datetime to use as the start
                                        of the "recent" period. This should
                                        be a UTC datetime, but already be offset
                                        for the user's time zone adjustment.

        :Returns:   a dictionary whose keys are datetimes for the beginning of
                    each day with logs since "recent_start". The value for each
                    day is a 2-member tuple. The first member is a list of log
                    id numbers for correct answers on that day. The second is a
                    list of log id numbers for incorrect (score<1.0).

        :rtype: dict[datetime.datetime, tuple]
        '''
        db = current.db
        debug = 1

        # get recorded weekly stats that overlap with recent period
        mystats = db((db.weekly_user_stats.name==user_id) &
                     (db.weekly_user_stats.tag==tag_id) &
                     (db.weekly_user_stats.week_end > recent_start)
                     ).select(orderby=db.weekly_user_stats.week_end
                              ).as_list()
        if debug: print('got from db:', len(mystats))

        # get date for most recent recorded stats in recent period
        most_recent_stats = mystats[-1]['week_end'] if mystats else None
        if debug: print('most_recent is', most_recent_stats)

        # if no recent weekly stats available, find week end of most recent
        if not most_recent_stats:
            latest = db((db.weekly_user_stats.name==user_id) &
                        (db.weekly_user_stats.tag==tag_id)
                        ).select(orderby=db.weekly_user_stats.week_end
                                 ).as_list()
            most_recent_stats = latest[-1]['week_end'] if latest else None
            if debug: print('most_recent is', most_recent_stats)
        # if no recorded weekly stats at all, get most recent attempt log
        if not most_recent_stats:
            last_log = db((db.attempt_log.name == user_id) &
                          (db.attempt_log.step == db.step2tags.step_id) &
                          (db.step2tags.tag_id == tag_id)
                          ).select(db.attempt_log.dt_attempted).last()
            if last_log:
                most_recent_stats = \
                    last_log['dt_attempted'] - datetime.timedelta(days=1)
            else:
                most_recent_stats = \
                    datetime.datetime.utcnow() - datetime.timedelta(days=1)

        # collect stats more recent than those recorded
        newstats = cls._initialize_weekly_stats(user_id, offset, tag_id,
                                                recent_start,
                                                most_recent_stats)
        if debug: print('got from method:', len(newstats))
        mystats = mystats + newstats

        flatstats = {}
        for w in mystats:
            for day in range(1,8):
                mydate = datetime.datetime.strptime(
                    '{} {} {}'.format(w['year'], w['week'], day),
                    '%G %V %u')
                flatstats[mydate] = (w['day{}_right'.format(day)],
                                     w['day{}_wrong'.format(day)])

        return flatstats

    @staticmethod
    def _initialize_weekly_stats(user_id: int, offset: datetime.timedelta,
                                 tag: int, recent_start: datetime.datetime,
                                 most_recent_row: datetime.datetime,
                                 now: Optional[datetime.datetime]=None
                                 ) -> list[dict]:
        """
        Retrieve and store a user's recent weekly performance on a tag.

        The method finds the attempt log entries that were evaluated right
        and wrong for each day since the recent_start datetime. These daily
        attempts are grouped by week. If they include whole weeks that are
        finished, those weeks are also recorded as records in the
        weekly_user_stats table.

        This assumes that "most_recent_row" is in UTC time, but that day/week
        boundaries need to be offset based on the user's time zone. In
        other words, all datetimes remain in UTC time but week/day boundaries will be offset from 0,0 to fit the user's local day.

        Although the weeks follow iso calendar week numbers, they begin on the
        Sunday. The "week_end" datetime is also actually minute 0 of the following week.

        :param int user_id:     Id of the user for which records are being
                                stored.
        :param datetime.timedelta offset:   The user's time zone offset from
                                            utc time.
        :param int tag:     Id of the tag for which records are being stored.
        :param datetime recent_start:   Start of the period considered "recent"
                                        for stats purposes
        :param datetime most_recent_row:    Datetime of the most recent row in
                                            weekly_user_stats already stored.
        :param datetime now:    Datetime to treat as current. For use only for
                                dependency injection in testing.

        :returns: A list of dictionaries, each representing one week of user
                  performance logs. Each dictionary has the following keys:
                    - 'name' (int): the user's id
                    - 'tag' (int): the tag id
                    - 'year' (int): 4-digit year
                    - 'month' (int): the iso month number
                    - 'week' (int): the iso week number
                    - 'week_start': timezone-offset utc datetime for the start
                                    of the week
                    - 'week_end': timezone-offset utc datetime for the start
                                  of the week

                  Then 14 further keys with the pattern
                    - 'day1_right' (list): a list of attempt_log id numbers for
                                           right attempts on that day
                    - 'day1_wrong' (list): a list of attempt_log id numbers for
                                           wrong attempts on that day
                  Two for each day from 1 to 7

        :rtype: list[dict]
        """
        db = current.db
        debug = 1
        now = now if now else datetime.datetime.utcnow()
        now_year, now_week = now.isocalendar()[:2]
        if most_recent_row:
            firstyear, firstweek = most_recent_row.isocalendar()[:2]
        else:
            firstyear, firstweek = 2011, 1
            most_recent_row = datetime.datetime(2011, 1, 1)
        recent_year, recent_week = recent_start.isocalendar()[:2]

        def inner_build_dict(weeklogs, days):
            weekdict = {'name': user_id,
                        'tag': tag,
                        'year': year,
                        'month': start.month,  # start and days are UTC offset
                        'week': week,
                        'week_start': start,
                        'week_end': days[7],
                        }
            if len(weeklogs) > 0:
                for n in range(1, 8):
                    rlogs = [r['attempt_log']['id'] for r in weeklogs if
                            r['attempt_log']['dt_attempted'] > most_recent_row and
                            r['attempt_log']['dt_attempted'] >= days[n-1] and
                            r['attempt_log']['dt_attempted'] < days[n] and
                            (abs((r['attempt_log']['score'] or 0) - 1.0) < 0.01)]
                    wlogs = [r['attempt_log']['id'] for r in weeklogs if
                            r['attempt_log']['dt_attempted'] > most_recent_row and
                            r['attempt_log']['dt_attempted'] >= days[n-1] and
                            r['attempt_log']['dt_attempted'] < days[n] and
                            abs((r['attempt_log']['score'] or 0) - 1.0) > 0.01]
                    weekdict['day{}_right'.format(str(n))] = rlogs
                    weekdict['day{}_wrong'.format(str(n))] = wlogs
            else:
                for n in range(1, 8):
                    weekdict['day{}_right'.format(str(n))] = []
                    weekdict['day{}_wrong'.format(str(n))] = []
            return weekdict

        return_list = []
        for year in range(firstyear, now.year+1):
            if debug: print(year)
            lastweek = 53
            if year == now_year:
                lastweek = now_week + 1
                if lastweek > datetime.date(now_year, 12, 31).isocalendar()[1]:
                    lastweek = now_week
            for week in range(firstweek, lastweek + 1):
                if debug: print(week)
                naivestart = datetime.datetime.strptime(
                    '{} {} 1'.format( year, week), '%G %V %u')
                # Adjust weekday number so that week starts on Sunday
                adjustedstart = naivestart - datetime.timedelta(days=1)
                start = adjustedstart - offset
                days = [start + datetime.timedelta(days=n) for n in range(0, 8)
                        ]

                # search logs based on tz-adjusted datetimes
                mylogs = db((db.attempt_log.name == user_id) &
                            (db.attempt_log.dt_attempted >= start) &
                            (db.attempt_log.dt_attempted < days[7]) &
                            (db.attempt_log.step == db.step2tags.step_id) &
                            (db.step2tags.tag_id == tag)
                            ).select().as_list()
                if debug: print('found logs', len(mylogs))
                # build stats for week and record if week is done
                weekdict = inner_build_dict(mylogs, days)
                if days[7] < now:  # week is finished, write to db
                    myrow = db.weekly_user_stats.insert(**weekdict)
                    db.commit()
                    if debug: print('inserting row', myrow)
                    if debug: print(weekdict)
                # only add to return list if within recent period
                if year >= recent_year and week >= recent_week:
                    return_list.append(weekdict)
        if debug: print('return list=================')
        if debug: print(return_list)

        return return_list

    @staticmethod
    def _get_today_counts(tagstats: dict,
                          today: datetime.datetime) -> int:
        """
        Return the number of attempts from tagstats for a specific day
        """
        try:
            todaylogs = tagstats[today]
            todaycount = len(todaylogs[0]) + len(todaylogs[1])
        except KeyError:  # no logs from today
            todaycount = 0

        # FIXME: Was being called in active_tags like this:
        # tag_records[idx]['todaycount'] = cls._get_today_counts(
        #     tagstats, daystart_offset)
        # tag_records[idx]['yestcount'] = cls._get_today_counts(
        #     tagstats, yeststart_offset)

        # FIXME: in active_tags, this assembled dt for yesterday:
        # yeststart_offset = daystart_offset - datetime.timedelta(days=1)
        # yeststart_utc = yeststart_offset + offset
        return todaycount

    @staticmethod
    def _get_delta_right_wrong():
        """
        get time delta between last right and wrong attempts

        :rtype: datetime.timedelta
        """
        # TODO: was done in performance_by_tag, but not used in client
        # if tag_records[i]['tlast_right'] > tag_records[i]['tlast_wrong']:
        #     tag_records[i]['delta_rw'] = (
        #         tag_records[i]['tlast_right'] - tag_records[i]['tlast_wrong'])
        # else:
        #     tag_records[i]['delta_rw'] = datetime.timedelta(days=0)
        pass

    # @profile
    @classmethod
    def performance_by_tag(cls, user_id: Optional[int]=None,
                           now: Optional[datetime.datetime]=None,
                           db: DAL=None) -> list[dict]:
        '''
        Calculate and return performance stats related to each tag for one user.

        :param int user_id: The id of the user whose stats are being retrieved.
                            Optional. If not supplied, the method returns stats
                            for the currently logged in user.
        :param datetime now:    The current time, used as the reference point
                                for calculating time-based statistics. **Only
                                used for dependency injection during testing**
        :param DAL db:  The database connection represented by a web2py DAL
                        object. **Only used for dependency injection during
                        testing**

        :returns:    a list of dictionaries, one per active tag for this user.
                     Each dictionary includes the following keys:

            tag (int)                   tag row id
            times_right (float)         total number of right attempts
            times_wrong (float)         total number of wrong attempts
            rw_ratio (float)            ratio of user's total right attempts to
                                        wrong attempts with current tag
            delta_wrong (timedelta)     length of time since last wrong answer
            delta_right (timedelta)     length of time since last right answer
            recent_avg_score (float)    average score for the user's recent
                                        attempts
            curlev (int)                highest level attained for tag
            revlev (int)                current level used for path selection
            set (int)                   the tag's "position" in set sequence.
                                        From db tags.
            bname (str)                 name of the badge corresponding to this
                                        tag. From db.badges.
            bdesc (str)                 description of the badge corresponding
                                        to this tag. From db.badges
            slides (list[int])          list of ids for the video lessons
                                        (slides) related to the tag
            cat1_reached (tuple)        a tuple of (datetime, prettydate
                                        string) for date when tag became active
                                        for user. From db.badges_begun.
            cat2_reached (tuple)        same for reaching category 2
            cat3_reached (tuple)        same for reaching category 3
            cat4_reached (tuple)        same for reaching category 4
            tlast_wrong (datetime)      most recent wrong attempt
            tlast_right (datetime)      most recent right attempt

            This method used to also return the following deprecated keys,
            which are not presently returned:

            delta_rw (timedelta)    length of time between last right
                                    answer and previous wrong answer (0 if last
                                    answer was wrong).
            steplist              a list of steps tagged with this tag
            steplist2             a list of steps tagged with this tag as
                                    tags_secondary
            steplist3             a list of steps tagged with this tag as
                                    tags_ahead

        :rtype: list[dict]
        '''
        debug = GLOBAL_DEBUG or 0
        db = current.db if not db else db
        auth = current.auth
        user = db.auth_user(auth.user_id if not user_id else user_id)
        recent_period = 4

        # get bounds for today, yesterday, recent period
        now = datetime.datetime.utcnow() if not now else now
        offset = get_offset(user)
        daystart_utc = datetime.datetime.combine(now.date(),
                                                 datetime.time(0, 0, 0, 0))
        daystart_offset = daystart_utc - offset
        recent_start_offset = (
            daystart_offset - datetime.timedelta(days=recent_period))

        # retrieve basic performance records for user's active tags
        badge_levels, review_levels = cls._find_badge_levels(user.id)
        tags = [tup[1] for v in badge_levels.values() for tup in v]
        tag_records = db((db.tag_records.name == user.id) &
                         (db.tag_records.tag.belongs(tags))).select(
                            db.tag_records.tag,
                            db.tag_records.times_right,
                            db.tag_records.times_wrong,
                            db.tag_records.tlast_right,
                            db.tag_records.tlast_wrong
                         ).as_list()

        for i, t in enumerate(tag_records):
            logs_by_day = cls._get_tag_logs_by_day(user.id, offset, t['tag'],
                                                   recent_start_offset)
            tag_records[i]['recent_avg_score'] = cls._get_avg_score(logs_by_day)

            # get right/wrong ratio
            try:
                # sanitize None values before rounding
                t['times_right'] = t['times_right'] or 0
                t['times_wrong'] = t['times_wrong'] or 0
                tag_records[i]['rw_ratio'] = round(
                    t['times_right'] / t['times_wrong'], 2)
            except ZeroDivisionError:
                tag_records[i]['rw_ratio'] = round(t['times_right'], 2)

            # parse last_right and last_wrong as datetimes if necessary
            if not isinstance(t['tlast_wrong'], datetime.datetime):
                t['tlast_wrong'] = parse(t['tlast_wrong'])
                tag_records[i]['tlast_wrong'] = t['tlast_wrong']
            if not isinstance(t['tlast_right'], datetime.datetime):
                t['tlast_right'] = parse(t['tlast_right'])
                tag_records[i]['tlast_right'] = t['tlast_right']

            # get time deltas since last right and wrong
            for opt in ['right', 'wrong']:
                try:
                    tag_records[i][f'delta_{opt}'] = now - t[f'tlast_{opt}']
                except TypeError:  # record is timezone-aware, shouldn't be yet
                    t[f'tlast_{opt}'] = t[f'tlast_{opt}'].replace(tzinfo=None)
                    tag_records[i][f'delta_{opt}'] = now - t[f'tlast_{opt}']

            # localize datetimes and add readable string for display
            for z in ['tlast_right', 'tlast_wrong']:
                t[z] = cls._local(t[z], user['tz_obj'])
                strf = '%b %e' if t[z].year == now.year else '%b %e, %Y'
                tag_records[i][z] = (t[z], t[z].strftime(strf))

            # add user's historic maximum and current review levels for tag
            try:
                tag_records[i]['curlev'] = [
                    l for l, tgs in badge_levels.items()
                    if t['tag'] in tgs][0]
            except IndexError:
                tag_records[i]['curlev'] = 0
            try:
                tag_records[i]['revlev'] = [
                    l for l, tgs in review_levels.items()
                    if t['tag'] in tgs][0]
            except IndexError:
                tag_records[i]['revlev'] = 0

            # round total right and wrong attempt counts to closest int for
            # readability
            for option in ['right', 'wrong']:
                try:
                    tag_records[i][f'times_{option}'] = \
                        remove_trailing_0s(t[f'times_{option}'], fmt='num')
                except TypeError:  # because value is None
                    tag_records[i][f'times_{option}'] = 0

        tag_records = cls._add_badge_info(tag_records)
        tag_records = cls._add_promotion_data(tag_records,
                                              user.id, user['tz_obj'])
        return tag_records

    def get_max(self):
        """
        Return an integer corresponding to the user's furthest badge set.

        The 'badge set' is actually the series of ints in db.tags.tag_position.

        """
        try:
            max_set = self.tag_progress['latest_new'] \
                if self.tag_progress['latest_new'] else 1
        except KeyError:
            max_set = 1
        return max_set

    @staticmethod
    def _local(dt, tz):
        """
        Return a datetime object localized to self.user's time zone.

        :param datetime dt:     The datetime object to be localized.
        :param pytz.BaseTzInfo tz:   The timezone object to be used in
                                     localizing the datetime

        NB: The pytz.localize function just adds timezone information to the
        utc datetime object. To actually adjust the datetime you need to get
        the local offset from utc and add it manually.

        :returns:   A localized datetime object
        :rtype:     datetime
        """
        dt = utc.localize(dt)
        try:
            newdt = tz.normalize(dt.astimezone(tz))
        except (TypeError, AttributeError):
            dt = parse(dt)
            newdt = tz.normalize(dt.astimezone(tz))
        return newdt

    def get_badge_levels(self):
        """
        Return the current self.badge_levels value.
        """
        return self.badge_levels

    @staticmethod
    def _find_badge_levels(user_id: int) -> tuple[dict[int, list[tuple]],
                                                  dict[int, list[tuple]]]:
        """
        Returns the user's current badge (tag) ids grouped by level.

        :param int user_id:     The id of the user whose records
                                are being retrieved.
        :returns:   A tuple of two dictionaries listing the user's active badges
                    grouped in levels 1-4. The first dictionary uses the
                    absolute level (maximum level ever reached) and the second
                    dictionary uses the current review level (based on core
                    algorithm)

                    The keys of each dictionary are the integers 1-4. Each
                    value is a list of tuples, with each tuple representing one
                    badge assigned to the given level.

                    The badge tuples in both dictionaries include:
                        [0]     (str) the badge name
                        [1]     (int) the tag id number
                    The first dictionary (for absolute level reached) also
                    includes the following members in each badge tuple:
                        [2]     (str) the badge description
                        [3]     (list) the lessons corresponding to the
                                       given badge. Each lesson is represented
                                       by a tuple of [0] (int) lesson_position,
                                       and [1] (str) lesson title

        FIXME: Should separate fetching of badge levels from gathering of
                badge info. Only the former is used in performance_by_tag,
                which is also duplicating the gathering of badge info
                with _add_badge_info

        :rtype: tuple[dict[int, list[tuple]],
                      dict[int, list[tuple]]]
        """
        db = current.db

        try:
            raw_levels = db(db.tag_progress.name == user_id
                            ).select().first().as_dict()
        except AttributeError:
            raw_levels = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': [],
                          'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}

        badge_level_ids = {k: v for k, v in list(raw_levels.items())
                           if k[:3] == 'cat' and k != 'cat1_choices'}
        badge_levels = {}
        for k, v in list(badge_level_ids.items()):
            level = int(k[3:])
            badgelist = []
            if v:
                for tag in v:
                    if tag in [79, 80, 81]:
                        break
                        # FIXME: Hack to handle tag_progress including utility
                        # tags that have no badges
                    mybadge = db.badges(db.badges.tag == tag)
                    badge_name = mybadge.badge_name if mybadge \
                        else 'tag id: {}'.format(tag)
                    mylessons = [(l.lesson_position, l.title) for l in
                                 db(db.lessons.lesson_tags.contains(tag)
                                    ).select()
                                 ]
                    badgelist.append((badge_name, tag, mybadge['description'], mylessons))
            badge_levels[level] = badgelist

        review_level_ids = {k: v for k, v in list(raw_levels.items())
                            if k[:3] == 'rev'}
        review_levels = {}
        for k, v in list(review_level_ids.items()):
            level = int(k[3:])
            badgelist = []
            if v:
                for tag in v:
                    if tag in [79, 80, 81]:
                        break
                    mybadge = db.badges(db.badges.tag == tag)
                    badge_name = mybadge.badge_name if mybadge \
                        else 'tag id: {}'.format(tag)
                    badgelist.append((badge_name, tag))
            review_levels[level] = badgelist

        return badge_levels, review_levels

    def _make_logs_into_weekstats(self, logs):
        """
        Return a dictionary of the provided log data structured as in
        db.user_stats.

        NB: datetime.isocalendar is weird at the beginning and end of a year.
        The first week of a year is the first in which there is a Thursday. So
        an initial Friday or Saturday can be left in the previous year's last
        week or a final Mon, Tues, Wed can be added to the next year's first
        week.
        """
        db = current.db
        logs = logs.as_list()
        for log in logs:
            # use local time for organizing of weeks/days
            # but keep dt_attempted as utc
            log['isocal'] = self._local(log['dt_attempted'],
                                        self.user['tz_obj']).isocalendar()

        years_iter = groupby(logs, key=lambda log: log['isocal'][0])
        weekstats = {}
        for yr, yearlogs in years_iter:
            weeks_iter = groupby(yearlogs, key=lambda log: log['isocal'][1])
            weeksdict = {}
            for weeknum, weeklogs in weeks_iter:
                weeklogs = [l for l in weeklogs]
                counts = {}
                logs_right = [l['id'] for l in weeklogs
                              if abs(l['score'] - 1) < 0.001]
                logs_wrong = [l['id'] for l in weeklogs
                              if abs(l['score'] - 1) >= 0.001]
                logs_by_tag = {}
                for log in weeklogs:
                    mystep = db.steps(log['step'])
                    tags = mystep.tags if mystep else []
                    for t in tags:
                        logs_by_tag.setdefault(t, []).append(log['id'])
                days_iter = groupby(weeklogs, key=lambda d:
                                    self._local(d['dt_attempted'],
                                                self.user['tz_obj']).date())
                for day, daylogs in days_iter:
                    daylogs = [d['id'] for d in daylogs]
                    counts[day] = daylogs
                weeksdict[weeknum] = (counts, logs_by_tag,
                                      logs_right, logs_wrong)
            weekstats[yr] = weeksdict
        return weekstats


    def _get_logs_for_range(self, startdate=None, stopdate=None, tag=None):
        '''
        Assemble and return aggregate log data on the user's step attempts.

        :param datetime startdate:  The beginning of the range for which attempt
                                    log data is being requested.
        :param datetime startdate:  The end of the range for which attempt
                                    log data is being requested.
        :param int tag:             The id of a tag. If provided, the returned
                                    logs are restricted to attempts involving
                                    steps with the provided tag.

        Before returning the aggregate data, this method ensures that any fresh attempts not processed and stored in the "weekly_user_stats" table are
        stored.

        Return value is a dictionary of weeks with log-data for each day.

        {year: {week#: ({datetime: [log ids],
                         datetime: [log ids],
                         datetime: [log ids],
                         datetime: [log ids],
                         datetime: [log ids],
                         datetime: [log ids],
                         datetime: [log ids]},
                        {tagid: [logs with that tag],
                         tagid: [logs]},
                        [logs_right],
                        [logs_wrong]
                        ),
                }
         }

        '''
        debug = 0
        db = current.db
        # get utc equivalents of start and stop in user's time zone
        offset = get_offset(self.user)
        naivestop = stopdate if stopdate else self.utcnow
        naivestart = startdate if startdate \
            else datetime.datetime(2012, 1, 1, 0, 0)
        tz_name = self.user.time_zone if self.user.time_zone \
            else 'America/Toronto'
        tz = timezone(tz_name)
        stopwtz = tz.localize(naivestop)
        startwtz = tz.localize(naivestart)
        ustop = stopwtz.astimezone(utc)
        if debug: print("ustop:", ustop)
        ustart = startwtz.astimezone(utc)
        if debug: print("ustart:", ustart)
        usrows = None
        # usrows = db((db.weekly_user_stats.name == self.user_id) &
        #             (db.weekly_user_stats.week_end > ustart) &
        #             (db.weekly_user_stats.week_start < ustop)).select()
        # usrows = usrows.as_list()
        # if usrows:
        #     pprint(usrows[0])
        usdict = {}
        # if usrows:
        #     # weeks and days organized by user's local time
        #     # but datetimes themselves are still utc
        #     years = list(range(ustart.year, ustop.year + 1))
        #     for year in years:
        #         myrows = [r for r in usrows if r['year'] == year]
        #         usdict[year] = {}
        #         for m in myrows:
        #             start = m['week_start']
        #             weekdates = [start + datetime.timedelta(days=n) + offset
        #                          for n in range(0, 7)]
        #             try:
        #                 for n in range(1,8):
        #                     rkey = 'day{}_right'.format(n)
        #                     wkey = 'day{}_wrong'.format(n)
        #                     total = m[rkey] + m[wkey]
        #                     usdict[year][m['week']][weekdates[n-1]] += total
        #             except KeyError:  # day hasn't yet been added to dict
        #                 usdict[year][m['week']] = {}
        #                 for n in range(1,8):
        #                     rkey = 'day{}_right'.format(n)
        #                     wkey = 'day{}_wrong'.format(n)
        #                     total = m[rkey] + m[wkey]
        #                     usdict[year][m['week']][weekdates[n-1]] = total
        # # add new logs without user_stats rows
        # updated = usrows[-1]['modified_on'] if usrows else ustart
        updated = ustart
        newlogs = db((db.attempt_log.name == self.user_id) &
                     (db.attempt_log.dt_attempted < ustop) &
                     (db.attempt_log.dt_attempted > updated)).select()
        if debug: print("userid:", self.user_id)
        if debug: print("newlogs:", len(newlogs))
        if newlogs:
            # print('newlogs:', len(newlogs))
            newus = self._make_logs_into_weekstats(logs=newlogs)
            # newstored = self.store_stats(newus)
            if usrows:
                usdict = usrows
                usdict.extend(newus)
            else:
                usdict = newus

        return usdict  # newstored

    def monthcal(self, year=None, month=None):
        '''
        Assemble and return attempt data for one month as a list of weeks.

        The returned data is a list of lists, each of which represents one calendar week (starting on Sunday). Within each week list, each day is represented by a 2-member tuple. The first member of the tuple is the datetime.date object for that day. The second member is a list of attempt log ids attempted by the current user on that date (adjusted for their time zone).

        '''
        debug = 0

        month = datetime.date.today().month if not month else int(month)
        if debug: print("MONTH", month)
        year = datetime.date.today().year if not year else int(year)
        if debug: print("YEAR", year)
        monthlists = calendar.Calendar(firstweekday=6
                                       ).monthdatescalendar(year, month)
        first = monthlists[0][0]
        if debug: print("first:", first)
        last = monthlists[-1][-1]
        if debug: print("last:", last)
        # monthname = calendar.month_name[month]
        rangelogs = self._get_logs_for_range(
            datetime.datetime(first.year, first.month, first.day, 0, 0),
            datetime.datetime(last.year, last.month, last.day, 23, 59)
            )
        if debug: pprint("rangelogs *****************************")
        if debug: pprint(rangelogs)
        flatrangelogs = {myday: mylist for year, yval in rangelogs.items()
                         for weeknum, wval in yval.items()
                         for myday, mylist in wval[0].items()}
        if debug: pprint("flatrangelogs +++++++++++++++++++++++++++++")
        if debug: pprint(flatrangelogs)

        for i, week in enumerate(monthlists):
            for daynum, day in enumerate(week):
                if day in flatrangelogs.keys():
                    monthlists[i][daynum] = (day, flatrangelogs[day])
                else:
                    monthlists[i][daynum] = (day, [])
        if debug: pprint(monthlists[-1])

        return {"year": year,
                "month": month,
                "data": monthlists}

    def get_badge_set_milestones(self):
        """
        Return a list of 2-member dictionaries giving the date each set was
        started.

        The keys for each dict are 'date' and 'badge_set'. If multiple sets
        were started on the same day, only the highest of the sets is accorded
        to that date. An extra dict is added to the end of the list with the
        current date and the highest badge_set reached (to pad out graph).
        """
        debug = 0
        db = current.db
        today = datetime.date.today().strftime('%Y-%m-%d')

        # Retrieve dates of when all badge set 'upgrades' happened
        result = db(db.badges_begun.name == self.user_id).select(
            db.tags.tag_position,
            'DATE(MIN(badges_begun.cat1))',
            left=db.tags.on(db.tags.id == db.badges_begun.tag),
            groupby=db.tags.tag_position,
            orderby='2, 1 DESC')
        if debug: print('Stats::get_badge_set_milestones: result==============')
        if debug: pprint(result)

        # Transform to a more lightweight form
        # Force str because of how PostgreSQL returns date column
        # PostgreSQL returns datetime object, sqlite returns string
        # So we have to force type to sting, this won't break backwards
        # compatibility with sqlite
        data = [{'my_date': str(list(row._extra.values())[0]),
                 'badge_set': row.tags.tag_position}
                for row in result if row.tags.tag_position < 900]
        data = sorted(data, key=lambda i: i['badge_set'], reverse=True)
        if debug: pprint(data)

        # Make sure that the badge set number is nondecreasing.
        # Order in the SQL query above along with this ensure that there's
        # only one event per date
        # milestones = []
        # prev = None
        # for d in data:
        #     if prev is not None and (d['badge_set'] >= prev['badge_set'] or
        #                              d['my_date'] == prev['my_date']):
        #                             # comparing badge sets
        #         continue
        #     milestones.append(d)
        #     prev = d
        milestones = data

        # Pad the data until today

        milestones = sorted(milestones, key=lambda i: i['badge_set'])
        try:
            if milestones[-1]['my_date'] != today:
                milestones.append({'my_date': today,
                                   'badge_set': milestones[-1]['badge_set']})
        except IndexError:
            pass

        return milestones

    def get_answer_counts(self, set=None, tag=None):
        '''
        Return dictionary of right/wrong answer counts for each date.

        :set:       int     Optional number of a badge set. If specified, the
                            returned counts are for attempts related to that
                            badge set only.

        :badge:     int     Optional id of a tag. If specified, the returned
                            counts are for attempts related to that one tag
                            only.

        '''
        db = current.db

        # Retrieve scores reached on given days
        if set:
            settags = db(db.tags.tag_position == set).select()
            settag_ids = [row.id for row in settags]
            setsteps = db(db.steps.tags.contains(settag_ids)).select()
            setstep_ids = [row.id for row in setsteps]
            attempt_query = db((db.attempt_log.name == self.user_id) &
                               (db.attempt_log.step.belongs(setstep_ids))
                               ).select().as_list()
        elif tag:
            badgesteps = db(db.steps.tags.contains(tag)).select()
            badgestep_ids = [row.id for row in badgesteps]
            attempt_query = db((db.attempt_log.name == self.user_id) &
                               (db.attempt_log.step.belongs(badgestep_ids))
                               ).select().as_list()
        else:
            attempt_query = db(db.attempt_log.name == self.user_id
                               ).select().as_list()

        pairs = [(self._local(q['dt_attempted'], self.user['tz_obj']).date(),
                  q['score'], q['id'])
                 for q in attempt_query]
        sorted_attempts = sorted(pairs, key=itemgetter(0))
        result = defaultdict(list)
        for date, score, myid in sorted_attempts:
            result[date].append((score, myid))

        # Transform to a lightweight form
        counts = []
        for (date, scores_ids) in list(result.items()):
            scores = [(s[0] or 0) for s in scores_ids if s[0]]
            ids = [s[1] for s in scores_ids]
            total = len(scores)
            right = len([r for r in scores if r >= 1.0])

            # Force str because of how PostgreSQL returns date column
            # PostgreSQL returns datetime object, sqlite returns string
            # So we have to force type to string, this won't break backwards
            # compatibility with sqlite
            counts.append({'my_date': str(date),
                           'right': right,
                           'wrong': total - right,
                           'ids': ids
                           })

        return counts

    def get_tag_counts_over_time(self, start, end, uid=None):
        """
        Return a dictionary of stats on tag and step attempts over given
        period.

        daysdata = {date: {'total_attempts': [id, id, ..],
                           'repeated_steps': {id: int, id: int, ..}
                           'tags_attempted': list,
                           'cat_data': {'cat1': {'cat_attempts': [id, id, ..],
                                                 'cat_tags_attempted':
                                                     {id: int, id: int, ..},
                                                 'cat_tags_missed': list},
                                        'rev1': ..
                                        }

        """
        db = current.db
        # FIXME: unused: auth = current.auth

        # get time bounds and dates for each day within those bounds
        offset = get_offset(self.user)
        end -= offset  # beginning of last day
        # print 'end', end
        start -= offset
        # print 'start', start
        period = (end - start) if end != start else datetime.timedelta(days=1)
        daysnum = abs(period.days)
        # print 'daysnum', daysnum
        datelist = []
        daycounter = daysnum + 1 if daysnum > 1 else daysnum
        for d in range(daycounter):
            newdt = start + datetime.timedelta(days=d)
            datelist.append(newdt)
        datelist = datelist[::-1]  # reverse so that latest comes first

        # gather common data to later filter for each day
        uid = self.user_id
        # FIXME: unused: final_dt = end + datetime.timedelta(days=1)
        # # to get end of last day
        logs = db((db.attempt_log.name == uid) &
                  (db.attempt_log.dt_attempted <= end) &
                  (db.attempt_log.dt_attempted > start) &
                  (db.attempt_log.step == db.steps.id)).select()

        daysdata = {}
        for daystart in datelist:
            # collect logs within day bounds
            dayend = daystart + datetime.timedelta(days=1)
            # print 'daystart', daystart
            # print 'dayend', dayend

            daylogs = logs.find(lambda l: (l.attempt_log['dt_attempted'] >=
                                           daystart) and
                                          (l.attempt_log['dt_attempted'] <
                                           dayend))

            # get all tags and total attempts for each
            alltags = [t for row in daylogs for t in row.steps.tags]
            tagcounts = {}
            for t in alltags:
                if t in list(tagcounts.keys()):
                    tagcounts[t] += 1
                else:
                    tagcounts[t] = 1

            # reconstruct cats for this day
            # FIXME: unused: nowcats = db(db.tag_progress.name ==
            #  uid).select().first()
            proms = db(db.badges_begun.name == uid).select()
            usercats = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
            for row in proms:
                for cat in ['cat4', 'cat3', 'cat2', 'cat1']:
                    if row[cat] and row[cat] < dayend:
                        usercats[cat].append(row.tag)
                        break
                    else:
                        continue
            # FIXME: doesn't account for promotions during the day

            # find attempts for each category
            catdata = {}
            for cat in list(usercats.keys()):
                catlogs = daylogs.find(lambda l: any(t for t in l.steps.tags
                                       if t in usercats[cat]))
                cattags = list(set([t for l in catlogs for t in l.steps.tags if
                                    t in usercats[cat]]))
                cattag_counts = {t: tagcounts[t] for t in cattags}
                tagsmissed = [t for t in usercats[cat] if t not in cattags]

                catdata[cat] = {'cat_attempts': [l.attempt_log['id']
                                for l in catlogs],
                                'cat_tags_attempted': cattag_counts,
                                'cat_tags_missed': tagsmissed}

            stepcounts = {}
            for log in daylogs:
                stepid = log.attempt_log['step']
                if stepid in list(stepcounts.keys()):
                    stepcounts[stepid] += 1
                else:
                    stepcounts[stepid] = 1
            repeats = {id: ct for id, ct in list(stepcounts.items()) if ct > 1}
            # print 'date', dayend.date()
            daysdata[dayend.date()] = {'total_attempts': [l.attempt_log['id']
                                       for l in daylogs],
                                       'repeated_steps': repeats,
                                       'tags_attempted': list(set(alltags)),
                                       'cat_data': catdata
                                       }
        return daysdata

    def _get_daystart(self, mydt):
        """
        Return a datetime object for the beginning of the day of supplied
        datetime.

        """
        daystart = datetime.datetime(year=mydt.year,
                                     month=mydt.month,
                                     day=mydt.day,
                                     hour=0,
                                     minute=0,
                                     second=0)
        return daystart

    def _get_dayend(self, mydt):
        """
        Return a datetime object for the beginning of the day of supplied
        datetime.

        """
        daystart = datetime.datetime(year=mydt.year,
                                     month=mydt.month,
                                     day=mydt.day,
                                     hour=0,
                                     minute=0,
                                     second=0)
        dayend = daystart + datetime.timedelta(days=1)
        return dayend


def week_bounds(weekday=None):
    '''
    Return datetime objects representing the last day of this week and
    previous.

    alternate version:

    def week_magic(day):
        day_of_week = day.weekday()

        to_beginning_of_week = datetime.timedelta(days=day_of_week)
        beginning_of_week = day - to_beginning_of_week

        to_end_of_week = datetime.timedelta(days=6 - day_of_week)
        end_of_week = day + to_end_of_week

        return (beginning_of_week, end_of_week)
    '''
    today = datetime.datetime.utcnow() if not weekday else weekday
    thismonth = calendar.monthcalendar(today.year, today.month)

    thisweek = [w for w in thismonth if today.day in w][0]
    today_index = thisweek.index(today.day)
    tw_index = thismonth.index(thisweek)

    lastweek = thismonth[tw_index - 1]
    delta = datetime.timedelta(days=(8 + today_index))
    lw_firstday = today - delta

    def get_lastmonth(yr, mth):
        if mth == 1:
            lastmonth = calendar.monthcalendar(yr - 1, 12)
        else:
            lastmonth = calendar.monthcalendar(yr, mth - 1)
        return lastmonth

    tw_prev = None
    if 0 in thisweek:  # first week of month
        if thisweek.index(0) < thisweek.index(today.day):
            lastmonth = get_lastmonth(today.year, today.month)
            tw_prev = lastmonth[-1]
            lastweek = lastmonth[-2]
            thisweek = [d for d in chain(thisweek, tw_prev) if d != 0]

    lw_prev = None
    if 0 in lastweek:  # last week was first of month
        lastmonth = get_lastmonth(today.year, today.month)
        lw_prev = lastmonth[-1]
        lastweek = [d for d in chain(lastweek, lw_prev) if d != 0]

    return lastweek, lw_firstday, thisweek


def get_weeks(year=None):
    """
    Return a list of lists, one for each week in the year.

    The list for each week contains seven datetime.datetime objects, one for
    each weekday, in their calendar order.
    """
    year = datetime.datetime.utcnow().year if not year else year
    cal = calendar.Calendar().yeardatescalendar(year)
    months = [m for row in cal for m in row]
    weeks = []
    for m in months:
        for w in m:
            if w not in weeks:
                weeks.append(w)
    return weeks


def get_offset(user):
    '''
    Return the user's offset from utc time based on their time zone.
    '''
    try:
        user.offset
    except AttributeError:
        today = datetime.datetime.utcnow()
        now = timezone('UTC').localize(today)
        tz_name = user.time_zone if user.time_zone \
            else 'America/Toronto'
        offset = timezone(tz_name).localize(today) - now
        # TODO: when to use "ambiguous"?
    return offset


def remove_trailing_0s(num, fmt='str'):
    """
    Return num (a float) with trailing zeros stripped.

    If there are no significant decimal places, removes the decimal point. By
    default the return value is a string. This can be changed to an int or
    float (as necessary for return value) by passing the value 'num' for the
    keyword argument 'fmt'.
    """
    out = ('%f' % num).rstrip('0').rstrip('.')
    if fmt == 'num':
        if len(out.split('.')) > 1:
            out = float(out)
        else:
            out = int(out)
    return out


def get_set_at_date(user_id, mydt):
    '''
    Return the badge set a user had reached at start_date.
    '''
    db = current.db
    bb = db((db.badges_begun.name == user_id) &
            (db.badges_begun.tag == db.tags.id)).select()
    try:
        bb = bb.find(lambda row: row.badges_begun.cat1 < mydt)
        highest = max(b.tags.tag_position for b in bb
                      if b.tags.tag_position < 900)
    except ValueError:
        highest = 1

    return highest


def get_daycounts(user, target):
    """
    Return a 4-member tuple giving the number of active days in the past 2
    weeks. The members are:
        [0] days active in current week
        [1] days meeting minimum class target in current week
        [2] days active in previous week
        [3] days meeting minimum class target in previous week
    """
    db = current.db
    offset = get_offset(user)
    lastweek, lw_firstday, thisweek = week_bounds()
    spans = [{'days': thisweek, 'count': 0, 'min_count': 0},
             {'days': lastweek, 'count': 0, 'min_count': 0}]

    logs = db((db.attempt_log.name == user.id) &
              (db.attempt_log.dt_attempted > lw_firstday)
              ).select(db.attempt_log.dt_attempted, db.attempt_log.name)

    mylogs = logs.find(lambda row: row.name == user.id)
    for span in spans:
        for day in span['days']:
            daycount = len([l for l in mylogs
                            if (l['dt_attempted'] - offset).day == day])
            # count = len(logs.find(lambda row:
            # tz.fromutc(row.dt_attempted).day == day))

            if daycount > 0:
                span['count'] += 1
            if daycount >= target:
                span['min_count'] += 1

    return (spans[0]['count'], spans[0]['min_count'],
            spans[1]['count'], spans[1]['min_count'])


def get_term_bounds(meminfo, start_date, end_date):
    """
    Return start and end dates for the term in datetime and readable formats.

    Also returns the end date for the user's most recent previous course, also
    in datetime and readable formats.

    """
    debug = False
    db = current.db
    if debug: print('starting paideia_stats/get_term_bounds =================')
    if debug: print(db.auth_user(meminfo['name']).last_name)

    db = current.db
    now = datetime.datetime.utcnow()

    def make_readable(mydt):
        strf = '%b %e' if mydt.year == now.year else '%b %e, %Y'
        return mydt.strftime(strf)

    myclasses = db((db.class_membership.name == meminfo['name']) &
                   (db.class_membership.class_section == db.classes.id)
                   ).select().as_list()
    if debug: print('myclasses', len(myclasses))

    if len(myclasses) > 1:  # get end of previous course
        try:
            end_dates = {c['classes']['id']: c['classes']['end_date']
                         for c in myclasses}
            if debug: pprint(end_dates)
            custom_ends = {c['classes']['id']:
                           c['class_membership']['custom_end'] for c
                           in myclasses if c['class_membership']['custom_end']}
            if debug: pprint(custom_ends)
            if custom_ends:
                for cid, dt in list(end_dates.items()):
                    if cid in list(custom_ends.keys()) and custom_ends[cid] > dt:
                        end_dates[cid] = custom_ends[cid]
            prevend = sorted(end_dates.values())[-2]
            fmt_prevend = make_readable(prevend)
            if debug: print('previous end:', pprint(fmt_prevend))
            if prevend in [meminfo['custom_end'], end_date]:
                prevend = None
                fmt_prevend = 'none'
        except Exception:
            if debug: print(traceback.format_exc(5))
            prevend = None
            fmt_prevend = 'could not retrieve'
    else:
        prevend = None
        fmt_prevend = 'none'

    mystart = meminfo['custom_start'] if meminfo['custom_start'] \
        else start_date
    fmt_start = make_readable(mystart)
    myend = meminfo['custom_end'] if meminfo['custom_end'] else end_date
    fmt_end = make_readable(myend)
    if debug: print('finished get_term_bounds')
    if debug: print(mystart, fmt_start, myend, fmt_end)

    return mystart, fmt_start, myend, fmt_end, prevend, fmt_prevend


def compute_letter_grade(uid, myprog, startset, classrow, membership):
    """
    Computes student's letter grade based on his/her progress in badge sets.
    """
    debug = False
    if debug: print('stats::compute_letter_grade: uid = ', uid)
    if debug: db = current.db
    if debug: print(db.auth_user[uid].last_name)
    if debug: print('stats::compute_letter_grade: start = ', startset)
    if debug: print('stats::compute_letter_grade: progress = ', myprog)
    gradedict = {}
    endset = int(startset) + myprog
    if debug: print('stats::compute_letter_grade: endset = ', endset)
    for let in ['a', 'b', 'c', 'd']:
        letcap = '{}_cap'.format(let)
        lettarget = '{}_target'.format(let)
        if membership['custom_{}_cap'.format(let)]:
            mylet = membership['custom_{}_cap'.format(let)]
        else:
            realtarget = (int(startset) + classrow[lettarget])
            if classrow[letcap] and (classrow[letcap] < realtarget):
                mylet = classrow[letcap]
            else:
                mylet = realtarget
        gradedict[mylet] = let.upper()
    if debug: pprint(gradedict)
    if endset in list(gradedict.keys()):
        mygrade = gradedict[endset]
    elif any([k for k, v in list(gradedict.items()) if endset > k]):
        grade_prog = max([k for k, v in list(gradedict.items()) if endset > k])
        mygrade = gradedict[grade_prog]
    elif endset > [k for k, v in list(gradedict.items()) if v == 'A'][0]:
        mygrade = 'A'
    else:
        mygrade = 'F'
    if debug: print('stats::compute_letter_grade: grade = ', mygrade)
    if debug: print('')

    return mygrade


def get_current_class(uid, now, myclass=None):
    debug = 0
    db = current.db
    myreturn = None
    myrow = None
    if debug: print('paideia_stats::get_current_class: uid:', uid)
    if debug: print('paideia_stats::get_current_class: myclass:', myclass)
    if debug: print('paideia_stats::get_current_class: now:', now)
    if myclass:
        myrow = db((db.class_membership.name == uid) &
                   (db.class_membership.class_section == myclass)
                   ).select().first().as_dict()
    else:
        myclasses = db((db.class_membership.name == uid) &
                       (db.class_membership.class_section == db.classes.id)
                       ).select()
        if debug: print('paideia_stats::get_current_class: myclasses:')
        if debug: print(myclasses)
        if debug: print(type(myclasses))
        if debug: print(len(myclasses))
        if debug: print(myclasses[-1])
        # FIXME: TypeError because legacy start/end dates are tz naive
        try:
            myclasses = myclasses.find(lambda row: (row.classes.start_date is not
                                                    None) and
                                    (row.classes.start_date < now) and
                                    (row.classes.end_date > now)
                                    )
        except TypeError:
            now = now.replace(tzinfo=None)
            myclasses = myclasses.find(lambda row: (row.classes.start_date is not
                                                    None) and
                                    (row.classes.start_date < now) and
                                    (row.classes.end_date > now)
                                    )

        if debug: print('paideia_stats::get_current_class: myclasses:')
        if debug: print(myclasses)
        if debug: print(type(myclasses))
        if debug: print(len(myclasses))
        try:
            myrow = myclasses.first().as_dict()
        except AttributeError:  # because no matching row after filtering
            myrow = None
    if myrow:
        myc = myrow
        myreturn = myc

        myprof = db.auth_user(myc['classes']['instructor'])
        myreturn['classes']['instructor'] = {'first_name': myprof['first_name'],
                                             'last_name': myprof['last_name'],
                                             'id': myprof['id']}

    return myreturn


def make_classlist(memberships, users, start_date, end_date, target, classrow):
    """
    Return a dictionary of information on each student in the class.
    """
    debug = False
    if debug: print('starting paideia_status/make_classlist ==============')
    db = current.db
    class_in_process = end_date > datetime.datetime.utcnow()
    if debug: print('class_in_process', class_in_process)
    userlist = []
    for member in memberships:
        uid = member.name
        if debug: print("user---------")
        if debug: print(uid)
        try:
            user = users.find(lambda row: row.auth_user.id == uid)[0]
        except IndexError:
            print('oops!')
            db = current.db
            user = {'auth_user': db.auth_user(uid)}
        # meminfo = memberships.find(lambda row: row.name == uid)[0]
        mystart, fmt_start, myend, fmt_end, prevend, fmt_prevend = \
            get_term_bounds(member, start_date, end_date)
        if debug: print("term bounds")
        if debug: print(mystart, myend)

        mycounts = get_daycounts(user['auth_user'], target)
        startset = copy(member.starting_set) if member.starting_set \
            else get_set_at_date(uid, mystart)
        if debug: print("startset**************")
        if debug: print(startset)

        if datetime.datetime.utcnow() < myend and \
                'tag_progress' in list(user.keys()):  # during class term
            currset = user['tag_progress'].latest_new
        else:  # after class term
            currset = get_set_at_date(uid, myend)

        endset = member['ending_set']
        if (not endset or endset!=currset) and not class_in_process:
            endset = currset
            if debug: print("writing endset", endset)
            db((db.class_membership.name==uid) &
               (db.class_membership.class_section==classrow['id'])
               ).update(ending_set=currset)
            db.commit()
            if debug: print(db((db.class_membership.name==uid) &
                               (db.class_membership.class_section==classrow['id'])
                               ).select().first()
                            )

        myprog = currset - int(startset)

        # if debug: print('classrow======================')
        # if debug: print(classrow)
        # if debug: print(type(classrow))
        mygrade = compute_letter_grade(uid, myprog, startset,
                                        classrow, member)
        if not mygrade or mygrade!=member['final_grade']:
            if not class_in_process:
                if debug: print("writing grade", mygrade)
                db((db.class_membership.name==uid) &
                   (db.class_membership.class_section==classrow['id'])
                   ).update(final_grade=mygrade)
                db.commit()
                if debug: print(db((db.class_membership.name==uid) &
                                   (db.class_membership.class_section==classrow['id'])
                                   ).select().first()
                                )

        try:
            tp_id = user['tag_progress'].id
        except KeyError:  # if no 'tag_progress' key in user dict
            try:
                tp_id = db(db.tag_progress.name == uid).select().first().id
            except AttributeError:  # if no tag_progress record for user
                tp_id = None
        if debug: print('tp_id', tp_id)
        if debug: print("startset**************")
        if debug: print(startset)

        mydict = {'uid': uid,
                  'first_name': user['auth_user'].first_name,
                  'last_name': user['auth_user'].last_name,
                  'counts': mycounts,
                  'current_set': currset,
                  'starting_set': startset,
                  'progress': myprog,
                  'grade': mygrade,
                  'start_date': fmt_start,
                  'end_date': fmt_end,
                  'previous_end_date': fmt_prevend,
                  'tp_id': tp_id,
                  'custom_start': member['custom_start'],
                  'custom_end': member['custom_end'],
                  'ending_set': endset,
                  'custom_a_cap': member['custom_a_cap'],
                  'custom_b_cap': member['custom_b_cap'],
                  'custom_c_cap': member['custom_c_cap'],
                  'custom_d_cap': member['custom_d_cap'],
                  'final_grade': member['final_grade']
                  }
        print("in dict")
        print(mydict["starting_set"])
        userlist.append(mydict)
    userlist = sorted(userlist, key=lambda t: (t['last_name'].capitalize(),
                                               t['first_name'].capitalize()))
    if debug: print('returning userlist --------------------')
    if debug: pprint({r['uid']:r['starting_set'] for r in userlist})

    return userlist


def make_unregistered_list(users):
    """
    """
    debug = False
    if debug: print('make_unregistered_list')
    db = current.db
    userlist = []
    for user in users:
        if debug: print('user id:', user.auth_user.id)
        tp = db(db.tag_progress.name == user.auth_user.id).select().first()
        tp_id = tp.id if tp else None
        currset = get_set_at_date(user.auth_user.id, datetime.datetime.now())
        userlist.append({'name': '{}, {}'.format(user.auth_user.last_name,
                                                 user.auth_user.first_name),
                         'uid': user.auth_user.id,
                         'counts': None,
                         'current_set': currset,
                         'starting_set': None,
                         'progress': None,
                         'grade': None,
                         'start_date': None,
                         'end_date': None,
                         'previous_end_date': None,
                         'tp_id': tp_id})
    userlist = sorted(userlist, key=lambda t: t['name'].capitalize())

    return userlist


def get_chart1_data(user_id=None, set=None, tag=None):
    '''
    Fetch raw data to present in first user profile chart.

    This function is isolated so that it can be called directly from ajax
    controls on the chart itself, as well as programmatically from info().

    Returns:
        dict:

    '''
    # def milliseconds(dt):
    #     return (dt-datetime.datetime(1970,1,1)).total_seconds() * 1000
    user_id = user_id if user_id else auth.user_id
    stats = Stats(user_id)
    badge_set_milestones = stats.get_badge_set_milestones()
    pprint(badge_set_milestones)
    answer_counts = stats.get_answer_counts(set=set, tag=tag)

    chart1_data = {'badge_set_reached': [{'date': dict['my_date'],
                                          'set': dict['badge_set']} for dict
                                         in badge_set_milestones],
                   'answer_counts': [{'date': dict['my_date'],
                                      'total': dict['right'] + dict['wrong'],
                                      'ys': [{'class': 'right',
                                              'y0': 0,
                                              'y1': dict['right']},
                                             {'class': 'wrong',
                                              'y0': dict['right'],
                                              'y1': dict['right'] +
                                              dict['wrong']}
                                             ],
                                      'ids': dict['ids']
                                      } for dict in answer_counts],
                   # above includes y values for stacked bar graph
                   # and 'ids' for modal presentation of daily attempts
                   }

    return {'chart1_data': chart1_data,
            'badge_set_milestones': badge_set_milestones,
            'answer_counts': answer_counts}


def my_custom_json(o):
    """
    A fork of gluon.serializers.custom_json that handles timedeltas

    """
    if hasattr(o, 'custom_json') and callable(o.custom_json):
        return o.custom_json()
    if isinstance(o, (datetime.date,
                      datetime.datetime,
                      datetime.time)):
        return o.isoformat()[:19].replace('T', ' ')
    elif isinstance(o, datetime.timedelta):
        return o.total_seconds()
    elif isinstance(o, integer_types):
        return int(o)
    elif isinstance(o, decimal.Decimal):
        return float(o)
    elif isinstance(o, (bytes, bytearray)):
        return str(o)
    elif isinstance(o, lazyT):
        return str(o)
    elif isinstance(o, XmlComponent):
        return to_native(o.xml())
    elif isinstance(o, set):
        return list(o)
    elif hasattr(o, 'as_list') and callable(o.as_list):
        return o.as_list()
    elif hasattr(o, 'as_dict') and callable(o.as_dict):
        return o.as_dict()
    else:
        raise TypeError(repr(o) + " is not JSON serializable")
