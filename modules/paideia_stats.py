import calendar
import datetime
from collections import defaultdict, OrderedDict
from dateutil.parser import parse
import traceback
from copy import copy
from operator import itemgetter
from pytz import timezone, utc
from gluon import current, DIV, SPAN, A, URL, UL, LI, B, I
from gluon import TAG
from plugin_utils import make_json, load_json
# from pprint import pprint
# from paideia import Categorizer
# from gluon.sqlhtml import SQLFORM  # , Field
# from gluon.validators import IS_DATE
from itertools import chain, groupby


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
        msel = db((db.class_membership.name == user_id) &
                  (db.class_membership.class_section == db.classes.id)).select()
        try:
            self.targetcount = [m.classes.paths_per_day for m in msel
                                if m.classes.paths_per_day][0]
        except IndexError:  # no group target for user
            self.targetcount = 20

        # progress through tag sets and levels ---------------------
        try:
            self.tag_progress = db(db.tag_progress.name == self.user_id
                                   ).select().first().as_dict()
        except AttributeError:
            self.tag_progress = {}
        # print 'Stats.__init__:: tag_progress:', self.tag_progress

        self.tag_recs = db(db.tag_records.name == self.user_id
                           ).select().as_list()  # cacheable=True
        # TODO: find and notify re. duplicate tag_records rows
        self.badge_levels, self.review_levels = self._find_badge_levels()
        self.tags = list(set([tup[1] for v
                              in self.badge_levels.values() for tup in v]))

        # date of each tag promotion
        self.badges_begun = db(db.badges_begun.name == self.user_id).select()
        if len(self.badges_begun) > 1:
            self.alerts['duplicate badges_begun records'] = [bb.id for bb
                                                        in self.badges_begun]

    def get_name(self):
        """
        Return the specified user's name as a single string, last name first.
        """
        return self.name

    def store_stats(self, statsdict, lastdt):
        '''
        Store aggregate user statistics provided by statsdict in db.user_stats.

        Argument lastdt is the updated datetime of the last user_stats row for
        the current user. This is used to determine whether that last row needs
        to be completed with data from statsdict.

        '''
        # TODO: Should there also be an annual aggregate?
        db = current.db
        data = {}
        for year, weeks in statsdict.iteritems():
            for weeknum, weekstuff in weeks.iteritems():
                dts = sorted(weekstuff[0].keys())
                done = 1 if not weeknum == weeks.keys()[-1] else 0

                weekdata = {'name': self.user_id,
                            'year': year,
                            'week': weeknum,
                            'updated': datetime.datetime.now(),
                            'day1': dts[0], 'day2': dts[1], 'day3': dts[2],
                            'day4': dts[3], 'day5': dts[4], 'day6': dts[5],
                            'day7': dts[6],
                            'count1': dts[0], 'count2': dts[1], 'count3': dts[2],
                            'count4': dts[3], 'count5': dts[4], 'count6': dts[5],
                            'count7': dts[6],
                            'logs_by_tag': make_json(weekstuff[1]),
                            'logs_right': weekstuff[2],
                            'logs_wrong': weekstuff[3],
                            'done': done
                            }
                # finish any unfinished week
                if year == statsdict.keys()[0] and \
                        weeknum == weeks.keys()[0] and \
                        lastdt.isocalendar()[1] == weeks.keys()[0] and \
                        lastdt.isocalendar()[0] == year:
                    openrow = db(db.user_stats.name == self.user_id
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

        TODO: move this aggregate data to a db table "user_stats" on calculation.
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
                dt = self._local(bbrows[cat]) if bbrows and bbrows[cat] else None
                prettydate = dt.strftime('%b %e, %Y') \
                    if isinstance(dt, datetime.datetime) else None
                tag_recs[idx]['{}_reached'.format(cat)] = (dt, prettydate)

        return tag_recs

    def _add_log_data(self, tag_recs):
        """
        Add a key-value pair giving log counts to each tag record.

        logs_by_week:   dict of {weeknumber: {date: [list of log ids]} including only
                        those attempts for steps tagged with this tag.

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
            for year, yeardata in usrows.iteritems():
                for weeknum, yrdata in yeardata.iteritems():
                    try:
                        bytag = yrdata[1][str(tag)]
                        weeklogs = {}
                        for day, count in yrdata[0].iteritems():
                            try:
                                weeklogs[parse(day)] = [c for c in count if c in bytag]
                            except (AttributeError, TypeError):
                                weeklogs[day] = [c for c in count if c in bytag]
                        t['logs_by_week'][year][weeknum] = weeklogs
                        t['logs_right'].extend([l for l in yrdata[2] if l in bytag])
                        t['logs_wrong'].extend([l for l in yrdata[3] if l in bytag])
                    except KeyError:  # no logs for this tag that week
                        pass
                    except IndexError:
                        print 'malformed usrows for ', tag, 'in week', weeknum
            all_logs = t['logs_right'] + t['logs_wrong']
            all_rows = db(db.attempt_log.id.belongs(all_logs)).select(db.attempt_log.score)
            t['avg_score'] = sum([r.score for r in all_rows]) / len(all_rows) \
                if all_rows else None
            if isinstance(t['avg_score'], float):
                t['avg_score'] = round(t['avg_score'], 1)
        return tag_recs

    def _get_avg_score(self, tag, mydays=7):
        """
        Return the user's average score on a given tag over the past N days.

        Always returns a float, since scores are floats between 0 and 1.
        """
        db = current.db
        startdt = self.utcnow - datetime.timedelta(days=mydays)
        logs = db((db.attempt_log.name == self.user_id) &
                  (db.attempt_log.dt_attempted >= startdt) &
                  (db.attempt_log.step == db.steps.id) &
                  (db.steps.tags.contains(tag))).select(db.attempt_log.score)
        try:
            avg_score = sum([l.score for l in logs]) / float(len(logs))
        except ZeroDivisionError:  # if tag not tried at all since startdt
            avg_score = 0
            # FIXME: Will this not bring tags up too early?
        return avg_score

    def active_tags(self, now=None):
        '''
        Find the tags that are currently active for this user, categorized 1-4.

        Returns a list of dictionaries, one per active tag for this user. Each
        dictionary includes the following keys:
        - from db.tag_records
            [tag]               int, tag row id
            [times_right]       double, total number of times right
            [times_wrong]       double, total number of times wrong
            [tlw]               datetime
            [tlr]               datetime

        ------calculated here -------------------------------------------------
            [rw_ratio]          ratio of times_right to times_wrong as a double.
            [delta_w]           length of time since last wrong answer
            [delta_r]           length of time since last right answer
            [delta_rw]          length of time between last right answer
                                        and previous wrong answer (0 if last
                                        answer was wrong).

        ------from self.badge_levels and self.review_levels -------------------
            [curlev]                highest level attained for tag
            [revlev]                current level used for path selection

        ------from _add_tag_data() --------------------------------------------
        - from db.tags
            [set]               the "position" in set progression, int
        - from db.badges
            [bname]
            [bdesc]

        ------from _add_progress_data()----------------------------------------
        - from db.badges_begun
            [cat1_reached]          a tuple of (datetime, prettydate string)
            [cat2_reached]          a tuple of (datetime, prettydate string)
            [cat3_reached]          a tuple of (datetime, prettydate string)
            [cat4_reached]          a tuple of (datetime, prettydate string)

        ------from ????--------------------------------------------------------
        - from db.user_stats
            [datecounts]            a dictionary of dates with the number of
                                        right and wrong attempts on each day.
        - from db.steps
            [steplist]              a list of steps tagged with this tag
            [steplist2]             a list of steps tagged with this tag as
                                        tags_secondary
            [steplist3]             a list of steps tagged with this tag as
                                        tags_ahead

        '''
        db = current.db
        tr = [r for r in self.tag_recs if r['tag'] in self.tags]

        # get bounds for today and yesterday
        offset = get_offset(self.user)
        daystart = datetime.datetime.combine(self.utcnow.date(),
                                             datetime.time(0, 0, 0, 0))
        daystart = daystart - offset
        yest_start = (daystart - datetime.timedelta(days=1))

        # collect recent attempt logs
        alltags = [r['tag'] for r in tr]
        logs = db((db.attempt_log.name == self.user_id) &
                  (db.attempt_log.step == db.steps.id) &
                  (db.attempt_log.dt_attempted > yest_start)).select()

        # shorten keys for readability
        shortforms = {'tlast_right': 'tlr',
                      'tlast_wrong': 'tlw',
                      'times_right': 'tright',
                      'times_wrong': 'twrong'}
        for k, alt in shortforms.iteritems():
            for idx, row in enumerate(tr):
                if k in row.keys():
                    tr[idx][alt] = row[k]
                    del tr[idx][k]
        now = self.utcnow if not now else now
        for idx, t in enumerate(tr):
            # remove unnecessary keys
            tr[idx] = {k: v for k, v in t.iteritems()
                    if k not in ['id', 'name', 'in_path', 'step',
                                 'secondary_right']}

            # count logs for this tag (today and yesterday)
            taglogs = logs.find(lambda r: any(tag for tag in r.steps.tags
                                              if t['tag'] == tag))
            todaylogs = taglogs.find(lambda r: r.attempt_log.dt_attempted > daystart)
            yestlogs = taglogs.find(lambda r: (r.attempt_log.dt_attempted <= daystart)
                                    and (r.attempt_log.dt_attempted > yest_start))
            tr[idx]['todaycount'] = len(todaylogs)
            tr[idx]['yestcount'] = len(yestlogs)

            # get average score over past week
            tr[idx]['avg_score'] = self._get_avg_score(t['tag'])

            # get right/wrong ratio
            try:
                tr[idx]['rw_ratio'] = t['tright'] / t['twrong']
            except (ZeroDivisionError, TypeError):
                tr[idx]['rw_ratio'] = t['tright']

            # parse last_right and last_wrong into readable form
            try:
                t['tlw'] = tr[idx]['tlw'] = parse(t['tlw'])
                t['tlw'] = tr[idx]['tlw'] = parse(t['tlr'])
            except AttributeError:
                pass

            # get time deltas
            for i in ['r', 'w']:
                try:
                    tr[idx]['delta_' + i] = now - t['tl' + i]
                except TypeError:  # record is timezone-aware, shouldn't be yet
                    t['tl' + i] = t['tl' + i].replace(tzinfo=None)
                    tr[idx]['delta_' + i] = now - t['tl' + i]
            tr[idx]['delta_rw'] = tr[idx]['tlr'] - tr[idx]['tlw'] \
                if tr[idx]['tlr'] > tr[idx]['tlw'] \
                else datetime.timedelta(days=0)

            # localize datetimes and add readable string for display
            for i in ['tlr', 'tlw']:
                t[i] = self._local(t[i])
                strf = '%b %e' if t[i].year == now.year else '%b %e, %Y'
                tr[idx][i] = (t[i], t[i].strftime(strf))

            # add level data
            # print 'badge_levels--------------'
            # print self.badge_levels
            # print 'review_levels--------------'
            # print self.review_levels
            # print 't["tag"]--------------------'
            # print t['tag']
            try:
                tr[idx]['curlev'] = [l for l, tgs in self.badge_levels.iteritems()
                                    if t['tag'] in [tg[1] for tg in tgs]][0]
            except IndexError:
                tr[idx]['curlev'] = 0
            try:
                tr[idx]['revlev'] = [l for l, tgs in self.review_levels.iteritems()
                                    if t['tag'] in [tg[1] for tg in tgs]][0]
            except IndexError:
                tr[idx]['revlev'] = 0

            # add rw_ratio
            try:
                if not t['tright']:  # TODO: tests to sanitize bad data (None)
                    t['tright'] = 0
                if not t['twrong']:
                    t['twrong'] = 0
                tr[idx]['rw_ratio'] = round((float(t['tright']) / float(t['twrong'])), 1)
            except (ZeroDivisionError, TypeError):
                tr[idx]['rw_ratio'] = round(float(t['tright']), 1)

            # round tright and twrong to closest int for readability
            for i in ['right', 'wrong']:
                try:
                    tr[idx]['t' + i] = remove_trailing_0s(t['t' + i], fmt='num')
                except TypeError:  # because value is None
                    tr[idx]['t' + i] = 0

        try:
            tr = self._add_tag_data(tr)
            tr = self._add_promotion_data(tr)
            # tr = self._add_log_data(tr)
            self.tagrecs_expanded = tr
            return tr  # make_json(tr.as_list())
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
        try:
            rank = self.tag_progress['latest_new']
        except KeyError:
            rank = 1
        categories = {k: v for k, v in self.tag_progress.iteritems()
                      if k != 'latest_new'}

        bls = self.tag_progress
        # print 'Stats._find_badge_levels:: bls:', bls
        #bls = db(db.tag_progress.name == self.user_id).select().first().as_dict()
        bl_ids = {k: v for k, v in bls.iteritems()
                  if k[:3] == 'cat' and k != 'cat1_choices'}
        # print 'Stats._find_badge_levels:: bl_ids:', bl_ids
        badge_levels = {}
        for k, v in bl_ids.iteritems():
            level = int(k[3:])
            badgelist = []
            if v:
                for tag in v:
                    mybadge = db.badges(db.badges.tag == tag)
                    badge_name = mybadge.badge_name if mybadge \
                        else 'tag id: {}'.format(tag)
                    badgelist.append((badge_name, tag))
            badge_levels[level] = badgelist

        rl_ids = {k: v for k, v in bls.iteritems() if k[:3] == 'rev'}
        review_levels = {}
        for k, v in rl_ids.iteritems():
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
        Return a dictionary of the provided log data structured as in db.user_stats.

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
            weeks_iter = groupby(yearlogs,
                                           key=lambda log: log['isocal'][1])
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
                    tags = db.steps(log['step']).tags
                    for t in tags:
                        logs_by_tag.setdefault(t, []).append(log['id'])
                days_iter = groupby(weeklogs,
                                              key=lambda d: self._local(d['dt_attempted']).date())
                for day, daylogs in days_iter:
                    daylogs = [d['id'] for d in daylogs]
                    counts[day] = daylogs
                weeksdict[weeknum] = (counts, logs_by_tag,
                                      logs_right, logs_wrong)
            weekstats[yr] = weeksdict
        return weekstats

    def _get_logs_for_range(self, startdate=None, stopdate=None):
        '''
        Assemble and return a dictionary of weeks with log-data for each day.

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
        naivestop = stopdate if stopdate else self.utcnow
        naivestart = startdate if startdate else datetime.datetime(2012, 1, 1, 0, 0)
        tz_name = self.user.time_zone if self.user.time_zone \
            else 'America/Toronto'
        tz = timezone(tz_name)
        stopwtz = tz.localize(naivestop)
        startwtz = tz.localize(naivestart)
        ustop = stopwtz.astimezone(utc)
        ustart = startwtz.astimezone(utc)

        usdict = {}
        usrows = db((db.user_stats.name == self.user_id) &
                    (db.user_stats.day7 > ustart) &
                    (db.user_stats.day7 < ustop)).select()
        usrows = usrows.as_list()
        if usrows:
            # weeks and days organized by user's local time
            # but datetimes themselves are still utc
            years = range(ustart.year, ustop.year + 1)
            usdict = {}
            for year in years:
                myrows = [r for r in usrows if r['year'] == year]
                usdict[year] = {}
                for m in myrows:
                    usdict[year][m['week']] = ({m['day1']: m['count1'],
                                                m['day2']: m['count2'],
                                                m['day3']: m['count3'],
                                                m['day4']: m['count4'],
                                                m['day5']: m['count5'],
                                                m['day6']: m['count6'],
                                                m['day7']: m['count7']
                                                },
                                               load_json(m['logs_by_tag']),
                                               m['logs_right'],
                                               m['logs_wrong'])
        # add new logs without user_stats rows
        updated = usrows[-1]['updated'] if usrows else ustart
        newlogs = db((db.attempt_log.name == self.user_id) &
                     (db.attempt_log.dt_attempted < ustop) &
                     (db.attempt_log.dt_attempted > updated)).select()
        if newlogs:
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
        monthend = calendar.monthrange(year, month)[1]
        monthname = calendar.month_name[month]
        rangelogs = self._get_logs_for_range(datetime.datetime(year, month, 1, 0, 0),
                                             datetime.datetime(year, month, monthend, 23, 59))
        newmcal = calendar.HTMLCalendar(6).formatmonth(year, month)
        mycal = TAG(newmcal)
        try:
            try:
                daycounts = {parse(k): len(v)
                             for week in rangelogs[year].values()
                             for k, v in week[0].iteritems()}
            except (TypeError, AttributeError):
                daycounts = {k: len(v)
                             for week in rangelogs[year].values()
                             for k, v in week[0].iteritems()}
            # Create html calendar and add daily count numbers
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
        except KeyError:  # if no logs for this month
            pass

        dropdown = self._monthpicker(calendar, year, month, monthname)
        mycal.elements('th.month')[0][0] = dropdown
        for link in self._navlinks(year, month):
            mycal.elements('th.month')[0].insert(0, link)
        wrap = DIV(_class='paideia_monthcal', _id='paideia_monthcal')
        wrap.append(SPAN('Questions answered each day in',
                         _class='monthcal_intro_line'))
        wrap.append(mycal)
        # TODO: Add weekly summary counts to the end of each table

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
                          SPAN(_class='fa fa-chevron-right fa-fw')),
                 'previous': (prev_month, prev_year, 0,
                              SPAN(_class='fa fa-chevron-left fa-fw'))}
        linktags = []
        for k, v in links.iteritems():
            mylink = A(v[3], _href=URL('reporting', 'calendar.load',
                                       args=[self.user_id, v[1], v[0]]),
                       _class='monthcal_nav_link {}'.format(k),
                       _disable_with=I(_class='fa fa-spinner fa-spin fa-fw').xml(),
                       cid='tab_calendar')
            linktags.append(mylink)
        return linktags

    def _monthpicker(self, calendar, year, month, monthname):
        """
        Return an html dropdown menu of months since 2011.
        """
        nowdate = datetime.date.today()
        nowmonth = nowdate.month
        nowyear = nowdate.year
        years = range(nowyear, 2011, -1)
        picker_args = {'_class': 'dropdown-menu',
                       '_role': 'menu',
                       '_aria-labelledby': 'month-label'}
        picker = UL(**picker_args)
        for y in years:
            for m in range(12, 1, -1):
                if not (m > nowmonth and y == nowyear):
                    picker.append(LI(A('{} {}'.format(calendar.month_name[m], y),
                                    _href=URL('reporting', 'calendar.load',
                                              args=[self.user_id, y, m]),
                                    _class='monthpicker',
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

    def get_badge_set_milestones(self):
        """
        Return a list of 2-member dictionaries giving the date each set was started.

        The keys for each dict are 'date' and 'badge_set'. If multiple sets
        were started on the same day, only the highest of the sets is accorded
        to that date. An extra dict is added to the end of the list with the
        current date and the highest badge_set reached (to pad out graph).
        """
        db = current.db
        today = datetime.date.today().strftime('%Y-%m-%d')

        # Retrieve dates of when all badge set 'upgrades' happened
        result = db(db.badges_begun.name == self.user_id).select(
            db.tags.tag_position,
            'DATE(MIN(badges_begun.cat1))',
            left=db.tags.on(db.tags.id == db.badges_begun.tag),
            groupby=db.tags.tag_position,
            orderby='2, 1 DESC')

        # Transform to a more lightweight form
        # Force str because of how PostgreSQL returns date column
        # PostgreSQL returns datetime object, sqlite returns string
        # So we have to force type to sting, this won't break backwards compatibility with sqlite
        data = [{'my_date': str(row._extra.values()[0]),
                 'badge_set': row.tags.tag_position}
                for row in result if row.tags.tag_position < 900]
        data = sorted(data, key=lambda i: i['badge_set'], reverse=True)

        # Make sure that the badge set number is nondecreasing.
        # Order in the SQL query above along with this ensure that there's
        # only one event per date
        milestones = []
        prev = None
        for d in data:
            if prev != None and (d['badge_set'] >= prev['badge_set']
                                 or d['my_date'] == prev['my_date']):  # comparing badge sets
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
                               (db.attempt_log.step.belongs(setstep_ids))).select().as_list()
        elif tag:
            badgesteps = db(db.steps.tags.contains(tag)).select()
            badgestep_ids = [row.id for row in badgesteps]
            attempt_query = db((db.attempt_log.name == self.user_id) &
                               (db.attempt_log.step.belongs(badgestep_ids))).select().as_list()
        else:
            attempt_query = db(db.attempt_log.name == self.user_id).select().as_list()

        pairs = [(self._local(q['dt_attempted']).date(), q['score'], q['id']) for q in attempt_query]
        sorted_attempts = sorted(pairs, key=itemgetter(0))
        result = defaultdict(list)
        for date, score, myid in sorted_attempts:
            result[date].append((score, myid))

        # Transform to a lightweight form
        counts = []
        for (date, scores_ids) in result.iteritems():
            scores = [s[0] for s in scores_ids]
            ids = [s[1] for s in scores_ids]
            total = len(scores)
            right = len(filter(lambda r: r >= 1.0, scores))

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
        Return a dictionary of stats on tag and step attempts over given period.

        daysdata = {date: {'total_attempts': [id, id, ..],
                           'repeated_steps': {id: int, id: int, ..}
                           'tags_attempted': list,
                           'cat_data': {'cat1': {'cat_attempts': [id, id, ..],
                                                 'cat_tags_attempted': {id: int, id: int, ..}
                                                 'cat_tags_missed': list},
                                        'rev1': ..
                                        }

        """
        db = current.db
        auth = current.auth

        # get time bounds and dates for each day within those bounds
        offset = get_offset(self.user)
        end -= offset  # beginning of last day
        #print 'end', end
        start -= offset
        #print 'start', start
        period = (end - start) if end != start else datetime.timedelta(days=1)
        daysnum = abs(period.days)
        #print 'daysnum', daysnum
        datelist = []
        daycounter = daysnum + 1 if daysnum > 1 else daysnum
        for d in range(daycounter):
            newdt = start + datetime.timedelta(days=d)
            datelist.append(newdt)
        datelist = datelist[::-1]  # reverse so that latest comes first

        # gather common data to later filter for each day
        uid = self.user_id
        final_dt = end + datetime.timedelta(days=1)  # to get end of last day
        logs = db((db.attempt_log.name == uid) &
                  (db.attempt_log.dt_attempted <= end) &
                  (db.attempt_log.dt_attempted > start) &
                  (db.attempt_log.step == db.steps.id)).select()

        daysdata = {}
        for daystart in datelist:
            # collect logs within day bounds
            dayend = daystart + datetime.timedelta(days=1)
            #print 'daystart', daystart
            #print 'dayend', dayend

            daylogs = logs.find(lambda l: (l.attempt_log['dt_attempted'] >= daystart) and
                                          (l.attempt_log['dt_attempted'] < dayend))

            # get all tags and total attempts for each
            alltags = [t for row in daylogs for t in row.steps.tags]
            tagcounts = {}
            for t in alltags:
                if t in tagcounts.keys():
                    tagcounts[t] += 1
                else:
                    tagcounts[t] = 1

            # reconstruct cats for this day
            nowcats = db(db.tag_progress.name == uid).select().first()
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
            for cat in usercats.keys():
                catlogs = daylogs.find(lambda l: any(t for t in l.steps.tags
                                                if t in usercats[cat]))
                cattags = list(set([t for l in catlogs for t in l.steps.tags if
                                    t in usercats[cat]]))
                cattag_counts = {t: tagcounts[t] for t in cattags}
                tagsmissed = [t for t in usercats[cat] if t not in cattags]

                catdata[cat] = {'cat_attempts': [l.attempt_log['id'] for l in catlogs],
                                'cat_tags_attempted': cattag_counts,
                                'cat_tags_missed': tagsmissed}

            stepcounts = {}
            for log in daylogs:
                stepid = log.attempt_log['step']
                if stepid in stepcounts.keys():
                    stepcounts[stepid] += 1
                else:
                    stepcounts[stepid] = 1
            repeats = {id: ct for id, ct in stepcounts.iteritems() if ct > 1}
            # print 'date', dayend.date()
            daysdata[dayend.date()] = {'total_attempts': [l.attempt_log['id'] for l in daylogs],
                                       'repeated_steps': repeats,
                                       'tags_attempted': list(set(alltags)),
                                       'cat_data': catdata
                                       }
        return daysdata

    def _get_daystart(self, mydt):
        """
        Return a datetime object for the beginning of the day of supplied datetime.

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
        Return a datetime object for the beginning of the day of supplied datetime.

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
    Return datetime objects representing the last day of this week and previous.

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
        offset = timezone(tz_name).localize(today) - now  # when to use "ambiguous"?
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
    Return a 4-member tuple giving the number of active days in the past 2 weeks.
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
            daycount = len([l for l in mylogs if (l['dt_attempted'] - offset).day == day])
            #count = len(logs.find(lambda row: tz.fromutc(row.dt_attempted).day == day))

            if daycount > 0:
                span['count'] += 1
            if daycount >= target:
                span['min_count'] += 1

    return (spans[0]['count'], spans[0]['min_count'],
            spans[1]['count'], spans[1]['min_count'])


def get_term_bounds(meminfo, start_date, end_date):
    """
    Return start and end dates for the term in datetime and readable formats

    """
    db = current.db
    now = datetime.datetime.utcnow()

    def make_readable(mydt):
        strf = '%b %e' if mydt.year == now.year else '%b %e, %Y'
        return mydt.strftime(strf)

    myclasses = db((db.class_membership.name == meminfo['name']) &
                   (db.class_membership.class_section == db.classes.id)
                   ).select().as_list()

    if len(myclasses) > 1:  # extend term bounds back to end of prev course
        end_dates = {c['classes']['id']: c['classes']['end_date'] for c in myclasses}
        custom_ends = {c['classes']['id']: c['class_membership']['custom_end']
                       for c in myclasses if c['class_membership']['custom_end']}
        if custom_ends:
            for cid, dt in end_dates.iteritems():
                if cid in custom_ends.keys() and custom_ends[cid] > dt:
                    end_dates[cid] = custom_ends[cid]
        previous = sorted(end_dates.values())[-2]
        start_date = previous if previous < start_date else start_date

    mystart = meminfo['custom_start'] if meminfo['custom_start'] else start_date
    fmt_start = make_readable(mystart)
    myend = meminfo['custom_end'] if meminfo['custom_end'] else end_date
    fmt_end = make_readable(myend)

    return mystart, fmt_start, myend, fmt_end


def compute_letter_grade(uid, myprog, startset, classrow):
    """
    Computes student's letter grade based on his/her progress in badge sets.
    """
    mymem = get_current_class(uid, datetime.datetime.utcnow(),
                              myclass=classrow['id'])
    gradedict = {}
    for let in ['a', 'b', 'c', 'd']:
        letcap = '{}_cap'.format(let)
        lettarget = '{}_target'.format(let)
        if mymem['custom_{}_cap'.format(let)]:
            mylet = mymem['custom_{}_cap'.format(let)]
        else:
            realtarget = (int(startset) + classrow[lettarget])
            if classrow[letcap] and (classrow[letcap] < realtarget):
                mylet = classrow[letcap]
            else:
                mylet = int(startset) + classrow[lettarget]
        gradedict[mylet] = let.upper()
    if myprog in gradedict.keys():

        mygrade = gradedict[myprog]
    elif any([k for k, v in gradedict.items() if myprog > k]):
        grade_prog = max([k for k, v in gradedict.items() if myprog > k])
        mygrade = gradedict[grade_prog]
    elif myprog > [k for k, v in gradedict.items() if v == 'A'][0]:
        mygrade = 'A'
    else:
        mygrade = 'F'
    return mygrade


def get_current_class(uid, now, myclass=None):
    db = current.db
    if myclass:
        myc = db((db.class_membership.name == uid) &
                 (db.class_membership.class_section == myclass)
                 ).select().first()
    else:
        myclasses = db((db.class_membership.name == uid) &
                    (db.class_membership.class_section == db.classes.id)
                    ).select()
        myclasses = myclasses.find(lambda row: row.classes.start_date != None)
        myclasses = myclasses.find(lambda row: (row.classes.start_date < now) and
                                            (row.classes.end_date > now))
        myc = myclasses.first()
    return myc


def make_classlist(member_sel, users, start_date, end_date, target, classrow):
    """
    Return a dictionary of information on each student in the class.
    """
    userlist = {}
    for user in users:
        uid = user.auth_user.id
        myname = '{}, {}'.format(user.auth_user.last_name,
                                 user.auth_user.first_name)
        meminfo = member_sel.find(lambda row: row.name == uid)[0]
        mystart, fmt_start, myend, fmt_end = get_term_bounds(
            meminfo, start_date, end_date)

        mycounts = get_daycounts(user.auth_user, target)
        startset = meminfo.starting_set if meminfo.starting_set \
            else get_set_at_date(uid, mystart)

        if datetime.datetime.utcnow() < myend:  # during class term
            currset = user.tag_progress.latest_new
        else:  # after class term
            currset = get_set_at_date(uid, myend)

        myprog = currset - int(startset)
        mygrade = compute_letter_grade(uid, myprog, startset, classrow)

        userlist[uid] = {'name': myname,
                         'counts': mycounts,
                         'current_set': currset,
                         'starting_set': startset,
                         'progress': myprog,
                         'grade': mygrade,
                         'start_date': fmt_start,
                         'end_date': fmt_end,
                         'tp_id': user.tag_progress.id}

    userlist = OrderedDict(sorted(userlist.iteritems(), key=lambda t: t[1]['name']))

    return userlist


def make_unregistered_list(users):
    """
    """
    print 'make_unregistered_list'
    db = current.db
    userlist = {}
    for user in users:
        print 'user id:', user.auth_user.id
        tp = db(db.tag_progress.name == user.auth_user.id).select().first()
        tp_id = tp.id if tp else None
        currset = get_set_at_date(user.auth_user.id, datetime.datetime.now())
        userlist[user.auth_user.id] = {'name': '{}, {}'.format(user.auth_user.last_name,
                                                               user.auth_user.first_name),
                             'counts': None,
                             'current_set': currset,
                             'starting_set': None,
                             'progress': None,
                             'grade': None,
                             'start_date': None,
                             'end_date': None,
                             'tp_id': tp_id}

    userlist = OrderedDict(sorted(userlist.iteritems(), key=lambda t: t[1]['name']))

    return userlist
