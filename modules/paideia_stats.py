import calendar
import datetime
import decimal
from collections import defaultdict
from dateutil.parser import parse
import traceback
from copy import copy
from memory_profiler import profile
from operator import itemgetter
from pytz import timezone, utc
from gluon import current, DIV, SPAN, A, URL, UL, LI, B, I
from gluon import TAG
from gluon._compat import to_native, integer_types
from gluon.languages import lazyT
from gluon.html import XmlComponent
from plugin_utils import make_json, load_json
from pprint import pprint
# from paideia import Categorizer
# from gluon.sqlhtml import SQLFORM  # , Field
# from gluon.validators import IS_DATE
from itertools import chain, groupby

if 0:
    from web2py.applications.paideia.controllers.plugin_utils import make_json, load_json
    from web2py.gluon import current, DIV, SPAN, A, URL, UL, LI, B, I, TAG


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
        self.utcnow = datetime.datetime.utcnow()
        self.alerts = {}

        # user info --------------------------------------------------
        user_id = auth.user_id if user_id is None else user_id
        self.user_id = user_id
        self.user = db.auth_user(user_id)
        self.name = '{}, {}'.format(self.user.last_name, self.user.first_name)
        # print 'Stats.__init__:: name:', self.name
        # print 'Stats.__init__:: user_id:', self.user_id

        # class/group info --------------------------------------------------
        try:
            msel = get_current_class(user_id, self.utcnow)
            self.targetcount = msel.classes.paths_per_day
        except (IndexError, AttributeError):  # no group target for user
            self.targetcount = 20

        # progress through tag sets and levels ---------------------
        try:
            self.tag_progress = db(db.tag_progress.name == self.user_id
                                   ).select().first().as_dict()
        except AttributeError:
            self.tag_progress = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': [],
                                 'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}
        # print 'Stats.__init__:: tag_progress:', self.tag_progress

        # TODO: find and notify re. duplicate tag_records rows
        self.badge_levels, self.review_levels = self._find_badge_levels()
        self.tags = list(set([tup[1] for v
                              in list(self.badge_levels.values()) for tup in v]))

        # date of each tag promotion
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

    def store_stats(self, statsdict, lastdt):
        '''
        Store aggregate user statistics provided by statsdict in db.weekly_user_stats.

        Argument lastdt is the updated datetime of the last user_stats row for
        the current user. This is used to determine whether that last row needs
        to be completed with data from statsdict.
        '''
        # TODO: Should there also be an annual aggregate?
        db = current.db
        data = {}
        for year, weeks in list(statsdict.items()):
            for weeknum, weekstuff in list(weeks.items()):
                dts = sorted(weekstuff[0].keys())
                done = 1 if not weeknum == list(weeks.keys())[-1] else 0

                weekdata = {'name': self.user_id,
                            'year': year,
                            'week': weeknum,
                            'updated': datetime.datetime.now(),
                            'day1': dts[0], 'day2': dts[1], 'day3': dts[2],
                            'day4': dts[3], 'day5': dts[4], 'day6': dts[5],
                            'day7': dts[6],
                            'count1': dts[0], 'count2': dts[1],
                            'count3': dts[2], 'count4': dts[3],
                            'count5': dts[4], 'count6': dts[5],
                            'count7': dts[6],
                            'logs_by_tag': make_json(weekstuff[1]),
                            'logs_right': weekstuff[2],
                            'logs_wrong': weekstuff[3],
                            'done': done
                            }
                # finish any unfinished week
                if year == list(statsdict.keys())[0] and \
                        weeknum == list(weeks.keys())[0] and \
                        lastdt.isocalendar()[1] == list(weeks.keys())[0] and \
                        lastdt.isocalendar()[0] == year:
                    openrow = db(db.weekly_user_stats.name == self.user_id
                                 ).select().last()

                    weekdata['updated'] = datetime.datetime.now()
                    for f in ['count1', 'count2', 'count3', 'count4',
                              'count5', 'count6', 'count7']:
                        weekdata[f].extend(openrow[f])
                    opentags = load_json(openrow['logs_by_tag'])
                    for k, v in weekdata['logs_by_tag']:
                        weekdata['logs_by_tag'][k].extend(opentags[k])
                    weekdata['logs_right'] = weekstuff[2]
                    weekdata['logs_wrong'] = weekstuff[3]
                # or add new row
                data.append(weekdata)

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

    def _add_tag_data(self, tag_recs):
        """
        Return list of tag records with additional fields for tag information.
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

    def _add_promotion_data(self, tag_recs):
        """
        Return list of tag records with additional fields for promoriont data.

        New fields are:
            - dt_cat1, dt_cat2, dt_cat3, dt_cat4
            - prettydate_cat1, prettydate_cat2, prettydate_cat3,
              prettydate_cat4
        """
        for idx, t in enumerate(tag_recs):
            try:
                bbrows = [b for b in self.badges_begun if b.tag == t['tag']][0]
            except IndexError:
                bbrows = None

            for k in range(1, 5):
                cat = 'cat{}'.format(k)
                dt = self._local(bbrows[cat]) if bbrows and bbrows[cat] \
                    else None
                prettydate = dt.strftime('%b %e, %Y') \
                    if isinstance(dt, datetime.datetime) else None
                tag_recs[idx]['{}_reached'.format(cat)] = (dt, prettydate)

        return tag_recs

    # FIXME: Deprecated
    def _add_log_data(self, tag_recs):
        """
        Add a key-value pair giving log counts to each tag record.

        logs_by_week:   dict of {weeknumber: {date: [list of log ids]}
        including only those attempts for steps tagged with this tag.

        logs_right:     list of log ids for correct attempts with this tag.

        logs_wrong:     list of log ids for incorret attempts with this tag.
        """
        db = current.db
        # usrows = db(db.user_stats.name == self.user_id).select()
        usrows = self._get_logs_for_range()
        for t in tag_recs:
            tag = t['tag']
            t['logs_by_week'] = copy(usrows)
            t['logs_right'] = []
            t['logs_wrong'] = []
            for year, yeardata in list(usrows.items()):
                for weeknum, yrdata in list(yeardata.items()):
                    try:
                        bytag = yrdata[1][str(tag)]
                        weeklogs = {}
                        for day, count in list(yrdata[0].items()):
                            try:
                                weeklogs[parse(day)] = [c for c in count
                                                        if c in bytag]
                            except (AttributeError, TypeError):
                                weeklogs[day] = [c for c in count
                                                 if c in bytag]
                        t['logs_by_week'][year][weeknum] = weeklogs
                        t['logs_right'].extend([l for l in yrdata[2]
                                                if l in bytag])
                        t['logs_wrong'].extend([l for l in yrdata[3]
                                                if l in bytag])
                    except KeyError:  # no logs for this tag that week
                        pass
                    except IndexError:
                        print('malformed usrows for ', tag, 'in week', weeknum)
            all_logs = t['logs_right'] + t['logs_wrong']
            all_rows = db(db.attempt_log.id.belongs(all_logs)
                          ).select(db.attempt_log.score)
            t['avg_score'] = sum([r.score for r in all_rows]) / len(all_rows) \
                if all_rows else None
            if isinstance(t['avg_score'], float):
                t['avg_score'] = round(t['avg_score'], 1)
        return tag_recs

    def _get_avg_score(self, tag, logs=None):
        """
        Return the user's average score on a given tag over the past N days.

        Always returns a float, since scores are floats between 0 and 1.
        """
        db = current.db
        debug = 0
        mylogids = []
        for r in logs.values():
            # print('avg:', r)
            mylogids.extend(r[0] + r[1])
        # print('mylogids', mylogids)
        mylogs = db((db.attempt_log.id.belongs(mylogids)) &
                    (db.attempt_log.step == db.step2tags.step_id) &
                    (db.step2tags.tag_id == tag)).select()
        try:
            avg_score = sum([l.attempt_log.score for l in mylogs]) / len(mylogs)
            avg_score = round(avg_score, 2)
        except ZeroDivisionError:  # if tag not tried at all since startdt
            avg_score = 0.0
        if debug: print(avg_score)
        return avg_score

    def _get_logs_for_tag(self, tag_id, recent_start):
        '''

        :param tag_id int:
        :param datetime recentstart:

        Returns a dictionary whose keys are datetimes for the beginning of each day with logs since "recent_start". The value for each day is a 2-member tuple. The first member is a list of log id numbers for correct answers on that day. The second is a list of log id numbers for incorrect (score<1.0).
        '''
        db = current.db
        debug = 0


        mystats = db((db.weekly_user_stats.name==self.user_id) &
                     (db.weekly_user_stats.tag==tag_id) &
                     (db.weekly_user_stats.week_end > recent_start)
                     ).select(orderby=db.weekly_user_stats.week_end
                              ).as_list()
        if debug: print('got from db:', len(mystats))

        most_recent_stats = mystats[-1]['week_end'] if mystats else None
        if debug: print('most_recent is', most_recent_stats)

        if not most_recent_stats:
            latest = db((db.weekly_user_stats.name==self.user_id) &
                        (db.weekly_user_stats.tag==tag_id)
                        ).select(orderby=db.weekly_user_stats.week_end
                                 ).as_list()
            most_recent_stats = latest[-1]['week_end'] if latest else None
            if debug: print('most_recent is', most_recent_stats)
        if not most_recent_stats:
                mylog = db((db.attempt_log.name == self.user_id) &
                           (db.attempt_log.step == db.step2tags.step_id) &
                           (db.step2tags.tag_id == tag_id)
                           ).select().last()
                if mylog:
                    if debug: print('any logs?', mylog.attempt_log.id)

        newstats = self._initialize_weekly_stats(tag_id, recent_start,
                                                 most_recent_stats)
        if debug: print('got from method:', len(newstats))
        mystats = mystats + newstats

        flatstats = {}
        # pprint(mystats)
        for w in mystats:
            for day in range(1,8):
                mydate = datetime.datetime.strptime(
                    '{} {} {}'.format(w['year'], w['week'], day),
                    '%G %V %u')
                flatstats[mydate] = (w['day{}_right'.format(day)],
                                     w['day{}_wrong'.format(day)])

        return flatstats

    # @profile
    def active_tags(self, now=None, db=None):
        '''
        Find the tags that are currently active for this user, categorized 1-4.

        arguments "now" and "db" are for dependency injection during testing

        Returns a list of dictionaries, one per active tag for this user. Each
        dictionary includes the following keys:
        - from db.tag_records
            [tag]               int, tag row id
            [times_right]       double, total number of times right
            [times_wrong]       double, total number of times wrong
            [tlw]               datetime, last wrong attempt
            [tlr]               datetime, last right attempt

        ------calculated here -------------------------------------------------
            [todaycount]        int, number of attempts for this tag by current
                                user today
            [yestcount]         int, number of attempts for this tag by current
                                    user yesterday
            [rw_ratio]          double, ratio of user's total right attempts to
                                    wrong attempts with current tag
            [delta_w]           timedelta, length of time since last wrong
                                    answer
            [delta_r]           timedelta, length of time since last right                              answer
            [delta_rw]          timedelta, length of time between last right
                                    answer and previous wrong answer (0 if last
                                    answer was wrong).

        ------from self.badge_levels and self.review_levels -------------------
            [curlev]            int, highest level attained for tag
            [revlev]            int, current level used for path selection

        ------from _add_tag_data() --------------------------------------------
        - from db.tags
            [set]               int, the tag's "position" in set sequence
        - from db.badges
            [bname]             str, the name of the badge corresponding to                         this tag
            [bdesc]             str, the description of the badge corresponding                     to this tag

        ------from _add_progress_data()----------------------------------------
        - from db.badges_begun
            [cat1_reached]      a tuple of (datetime, prettydate string),
                                    date when tag became active for user
            [cat2_reached]      a tuple of (datetime, prettydate string),
                                    date when tag first entered category 2 for
                                    user.
            [cat3_reached]      a tuple of (datetime, prettydate string),
                                    same for category 3
            [cat4_reached]      a tuple of (datetime, prettydate string),
                                    same for category 4

        ------from ????--------------------------------------------------------
        - from db.weekly_user_stats
            [datecounts]            a dictionary of dates with the number of
                                        right and wrong attempts on each day.
        - from db.steps
            [steplist]              a list of steps tagged with this tag
            [steplist2]             a list of steps tagged with this tag as
                                        tags_secondary
            [steplist3]             a list of steps tagged with this tag as
                                        tags_ahead

        '''
        debug = 0
        db = current.db if not db else db

        # get bounds for today and yesterday
        now = self.utcnow if not now else now
        offset = get_offset(self.user)
        start_date = self.utcnow.date() if not now else now.date()
        daystart = datetime.datetime.combine(start_date,
                                             datetime.time(0, 0, 0, 0))
        daystart = daystart - offset
        recent_start = (daystart - datetime.timedelta(days=4))
        yest_start = (daystart - datetime.timedelta(days=1))

        tag_records = db((db.tag_records.name == self.user_id) &
                         (db.tag_records.tag.belongs(self.tags))
                          ).select().as_list()  # cacheable=True
        # shorten keys for readability
        shortforms = {'tlast_right': 'tlr',
                      'tlast_wrong': 'tlw',
                      'times_right': 'tright',
                      'times_wrong': 'twrong'}
        for k, alt in list(shortforms.items()):
            for idx, row in enumerate(tag_records):
                if k in list(row.keys()):
                    tag_records[idx][alt] = row[k]
                    del tag_records[idx][k]


        # FIXME:
        # mydel = db(db.weekly_user_stats.name == self.user_id).delete()
        # db.commit()
        # print('deleted', mydel)

        # loop over tag_records entries
        for idx, t in enumerate(tag_records):
            if debug: print('D')
            if debug: print('active_tags: tag', t['tag'])
            # remove unnecessary keys
            tag_records[idx] = {k: v for k, v in list(t.items())
                if k not in ['id', 'name', 'in_path', 'step',
                             'secondary_right']}

            # Count attempt log rows for recent attempts (today, yesterday,
            # and within last 5 days)
            # log fields used below are dt_attempted, score
            tagstats = self._get_logs_for_tag(t['tag'], recent_start)

            try:
                todaylogs = tagstats[daystart + offset]
                tag_records[idx]['todaycount'] = len(todaylogs[0] + todaylogs[1])
            except KeyError:  # no logs from today
                tag_records[idx]['todaycount'] = 0
            try:
                yestlogs = tagstats[yest_start + offset]
                tag_records[idx]['yestcount'] = len(yestlogs[0] + yestlogs[1])
            except KeyError:  # no logs from yesterday
                tag_records[idx]['yestcount'] = 0

            if debug: print('F')
            # get average score over recent period
            tag_records[idx]['avg_score'] = self._get_avg_score(
                t['tag'], logs=tagstats)

            # get right/wrong ratio (from tag_records itself)
            try:
                if not t['tright']:  # TODO: tests to sanitize bad data (None)
                    t['tright'] = 0
                if not t['twrong']:
                    t['twrong'] = 0
                tag_records[idx]['rw_ratio'] = round(
                    t['tright'] / t['twrong'], 2)
            except (ZeroDivisionError, TypeError):
                tag_records[idx]['rw_ratio'] = round(t['tright'], 2)

            # parse last_right and last_wrong into readable form
            try:
                t['tlw'] = tag_records[idx]['tlw'] = parse(t['tlw']) if not \
                    isinstance(t['tlw'], datetime.datetime) else t['tlw']
                t['tlr'] = tag_records[idx]['tlr'] = parse(t['tlr']) if not \
                    isinstance(t['tlr'], datetime.datetime) else t['tlr']
            except AttributeError:
                pass

            # get time deltas since last right and wrong
            for i in ['r', 'w']:
                try:
                    tag_records[idx]['delta_' + i] = now - t['tl' + i]
                except TypeError:  # record is timezone-aware, shouldn't be yet
                    t['tl' + i] = t['tl' + i].replace(tzinfo=None)
                    tag_records[idx]['delta_' + i] = now - t['tl' + i]
            if tag_records[idx]['tlr'] > tag_records[idx]['tlw']:
                tag_records[idx]['delta_rw'] = (
                    tag_records[idx]['tlr'] - tag_records[idx]['tlw'])
            else:
                tag_records[idx]['delta_rw'] = datetime.timedelta(days=0)
            # localize datetimes and add readable string for display
            for i in ['tlr', 'tlw']:
                t[i] = self._local(t[i])
                strf = '%b %e' if t[i].year == now.year else '%b %e, %Y'
                tag_records[idx][i] = (t[i], t[i].strftime(strf))

            # add user's historic maximum and current review levels for tag
            try:
                tag_records[idx]['curlev'] = [l for l, tgs in
                    list(self.badge_levels.items())
                    if t['tag'] in [tg[1] for tg in tgs]
                    ][0]
            except IndexError:
                traceback.print_exc(5)
                tag_records[idx]['curlev'] = 0
            try:
                tag_records[idx]['revlev'] = [l for l, tgs in
                    list(self.review_levels.items())
                    if t['tag'] in [tg[1] for tg in tgs]
                    ][0]
            except IndexError:
                traceback.print_exc(5)
                tag_records[idx]['revlev'] = 0

            # round total right and wrong attempt counts to closest int for
            # readability
            for i in ['right', 'wrong']:
                try:
                    tag_records[idx]['t' + i] = remove_trailing_0s(t['t' + i],
                                                          fmt='num')
                except TypeError:  # because value is None
                    tag_records[idx]['t' + i] = 0

        try:
            if debug: print('J')
            tag_records = self._add_tag_data(tag_records)
            if debug: print('K')
            tag_records = self._add_promotion_data(tag_records)
            # tr = self._add_log_data(tr)
            if debug: print('L')
            return tag_records
        except Exception:
            traceback.print_exc(5)
            return None

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

    def _local(self, dt, tz=None):
        """
        Return a datetime object localized to self.user's time zone.

        NB: The pytz.localize function just adds timezone information to the
        utc datetime object. To actually adjust the datetime you need to get
        the local offset from utc and add it manually.

        The tz argument is simply for dependency injection during testing.

        """
        tz = self.user.tz_obj if not tz else tz
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

    def _find_badge_levels(self):
        """
        Return a dictionary listing the user's badges in levels 1-4.
        """
        db = current.db
        # try:
        #   rank = self.tag_progress['latest_new']
        # except KeyError:
        #    rank = 1
        # FIXME: unused: categories = {k: v for k, v
        # in self.tag_progress.iteritems() if k != 'latest_new'}

        bls = self.tag_progress
        # print 'Stats._find_badge_levels:: bls:', bls
        # bls = db(db.tag_progress.name ==
        # self.user_id).select().first().as_dict()
        bl_ids = {k: v for k, v in list(bls.items())
                  if k[:3] == 'cat' and k != 'cat1_choices'}
        # print 'Stats._find_badge_levels:: bl_ids:', bl_ids
        badge_levels = {}
        for k, v in list(bl_ids.items()):
            level = int(k[3:])
            badgelist = []
            if v:
                for tag in v:
                    # print("tag ", tag)
                    if tag in [79, 80, 81]:
                        break
                        # FIXME: Hack to handle tag_progress including utility
                        # tags that have no badges
                    mybadge = db.badges(db.badges.tag == tag)
                    # print(mybadge)
                    badge_name = mybadge.badge_name if mybadge \
                        else 'tag id: {}'.format(tag)
                    mylessons = [(l.lesson_position, l.title) for l in
                                 db(db.lessons.lesson_tags.contains(tag)
                                    ).select()
                                 ]
                    badgelist.append((badge_name, tag, mybadge['description'], mylessons))
            badge_levels[level] = badgelist

        rl_ids = {k: v for k, v in list(bls.items()) if k[:3] == 'rev'}
        review_levels = {}
        for k, v in list(rl_ids.items()):
            level = int(k[3:])
            badgelist = []
            if v:
                for tag in v:
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
            log['isocal'] = self._local(log['dt_attempted']).isocalendar()

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
                                    self._local(d['dt_attempted']).date())
                for day, daylogs in days_iter:
                    daylogs = [d['id'] for d in daylogs]
                    counts[day] = daylogs
                weeksdict[weeknum] = (counts, logs_by_tag,
                                      logs_right, logs_wrong)
            weekstats[yr] = weeksdict
        return weekstats

    def _initialize_weekly_stats(self, tag, recent_start,
                                 most_recent_row=None, now=None):
        """Process and  store user's logs and return newly stored recent stats.

        This assumes that "most_recent_row" is in UTC time, but that day/week
        boundaries need to be adjusted based on the user's timezone offset. In
        other words, all datetimes remain in UTC time but week/day boundaries will be offset from 0,0 to fit the user's local day.

        Although the weeks follow iso calendar week numbers, they begin on the
        Sunday. The "week_end" datetime is also actually minute 0 of the following week.

        :param int tag:     Id of the tag for which records are being stored.
        :param datetime most_recent_row:    Datetime of the most recent row in
                                            weekly_user_stats already stored.
        :param datetime now:    Datetime to treat as current. For use only for
                                dependency injection in testing.
        """
        db = current.db
        debug = 0
        now = now if now else self.utcnow
        offset = get_offset(self.user)
        if most_recent_row:
            firstyear, firstweek = most_recent_row.isocalendar()[:2]
        else:
            firstyear, firstweek = 2011, 1
            most_recent_row = datetime.datetime(2011, 1, 1)
        recent_year, recent_week = recent_start.isocalendar()[:2]

        def inner_build_dict(weeklogs):
            weekdict = {'name': self.user_id,
                        'tag': tag,
                        'year': year,
                        'month': start.month,  # start and days are UTC offset
                        'week': week,
                        'week_start': start,
                        'week_end': days[7],
                        }
            valid = 0
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
                if len(rlogs) or len(wlogs):
                    valid = 1
                weekdict['day{}_right'.format(str(n))] = rlogs
                weekdict['day{}_wrong'.format(str(n))] = wlogs
            return weekdict if valid else None

        return_list = []
        for year in range(firstyear, now.year+1):
            # print(year)
            for week in range(firstweek, 54):
                # print(week)
                naivestart = datetime.datetime.strptime(
                    '{} {} 1'.format( year, week), '%G %V %u')
                # Adjust weekday number so that week starts on Sunday
                adjustedstart = naivestart - datetime.timedelta(days=1)
                start = adjustedstart - offset
                days = [start + datetime.timedelta(days=n) for n in range(0, 8)
                        ]

                # search logs based on tz-adjusted datetimes
                mylogs = db((db.attempt_log.name == self.user_id) &
                            (db.attempt_log.dt_attempted >= start) &
                            (db.attempt_log.dt_attempted < days[7]) &
                            (db.attempt_log.step == db.step2tags.step_id) &
                            (db.step2tags.tag_id == tag)
                            ).select().as_list()
                if mylogs:
                    weekdict = inner_build_dict(mylogs)
                    if weekdict:
                        if days[7] < now:  # week is finished, write to db
                            myrow = db.weekly_user_stats.insert(**weekdict)
                            db.commit()
                            if debug: print('inserting row', myrow)
                        # only return if
                        if year >= recent_year and week >= recent_week:
                            return_list.append(weekdict)
                    else:
                        pass  # week had no logs
        # print ('finished')

        return return_list


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
        ustart = startwtz.astimezone(utc)
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
        debug = 1

        month = datetime.date.today().month if not month else int(month)
        if debug: print("MONTH", month)
        year = datetime.date.today().year if not year else int(year)
        if debug: print("YEAR", year)
        monthlists = calendar.Calendar(firstweekday=6
                                       ).monthdatescalendar(year, month)
        first = monthlists[0][0]
        last = monthlists[-1][-1]
        # monthname = calendar.month_name[month]
        rangelogs = self._get_logs_for_range(
            datetime.datetime(first.year, first.month, first.day, 0, 0),
            datetime.datetime(last.year, last.month, last.day, 23, 59)
            )
        flatrangelogs = {myday: mylist for year, yval in rangelogs.items()
                         for weeknum, wval in yval.items()
                         for myday, mylist in wval[0].items()}

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
        debug = False
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
        milestones = []
        prev = None
        for d in data:
            if prev is not None and (d['badge_set'] >= prev['badge_set'] or
                                     d['my_date'] == prev['my_date']):
                                    # comparing badge sets
                continue
            milestones.append(d)
            prev = d

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

        pairs = [(self._local(q['dt_attempted']).date(), q['score'], q['id'])
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
