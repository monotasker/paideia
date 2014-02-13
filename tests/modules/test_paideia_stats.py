#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the modulename module

 Configuration and some fixtures
 the file tests/conftest.py
 run with py.test -xvs path/to/tests/dir

"""

import pytest
import datetime
from dateutil import parser
from pprint import pprint
from pytz import timezone
from gluon import current
from paideia_stats import Stats
from paideia_utils import make_json


@pytest.fixture()  # params=[n for n in range(4)]
def myStats(user_login, web2py):  # request
    """
    A pytest fixture providing a Stats object for testing.

    user_login fixture from conftest.py
    """
    # case = request.param
    db = web2py.db

    alrows = db(db.attempt_log.name == user_login['id'])
    print '============================================================='
    print 'found', alrows.count(), 'attempt_log rows'
    if not alrows.isempty():
        alrows.delete()
    tagsteps = db(db.steps.tags.contains(72)).select()
    tagpaths = db(db.paths.steps.contains(tagsteps[0].id)).select()
    aldata = [{'name': user_login['id'],
               'step': tagsteps[0].id,
               'in_path': tagpaths[0],
               'score': 1.0,
               'dt_attempted': datetime.datetime(2014, 1, 27),
               'user_response': 'βλα',
               },
              {'name': user_login['id'],
               'step': tagsteps[0].id,
               'in_path': tagpaths[0],
               'score': 1.0,
               'dt_attempted': datetime.datetime(2014, 1, 29),
               'user_response': 'βλα',
               },
              {'name': user_login['id'],
               'step': tagsteps[0].id,
               'in_path': tagpaths[0],
               'score': 0.5,
               'dt_attempted': datetime.datetime(2014, 1, 29),
               'user_response': 'βλα',
               },
              {'name': user_login['id'],
               'step': tagsteps[0].id,
               'in_path': tagpaths[0],
               'score': 0,
               'dt_attempted': datetime.datetime(2014, 1, 29),
               'user_response': 'βλα',
               },
              {'name': user_login['id'],
               'step': tagsteps[0].id,
               'in_path': tagpaths[0],
               'score': 0,
               'dt_attempted': datetime.datetime(2014, 1, 31),
               'user_response': 'βλα',
               },
              {'name': user_login['id'],
               'step': tagsteps[0].id,
               'in_path': tagpaths[0],
               'score': 1.0,
               'dt_attempted': datetime.datetime(2014, 2, 1),
               'user_response': 'βλα',
               }]
    logs = web2py.db.attempt_log.bulk_insert(aldata)
    web2py.db.commit()
    print 'logs are', logs

    bbrows = db(db.badges_begun.name == user_login['id'])
    if not bbrows.isempty():
        bbrows.delete()
    bbdata = {'name': user_login['id'],
              'cat1': datetime.datetime(2014, 1, 1, 0, 0),
              'tag': 72
              }
    db.badges_begun.insert(**bbdata)
    db.commit()

    tprows = db(db.tag_progress.name == user_login['id'])
    if not tprows.isempty():
        tprows.delete()
    tpdata = {'name': user_login['id'],
              'cat1': [72]
              }
    db.tag_progress.insert(**tpdata)
    db.commit()

    trrows = db((db.tag_records.name == user_login['id']) &
                (db.tag_records.tag == 72))
    if not trrows.isempty():
        trrows.delete()
    trdata = {'name': user_login['id'],
            'tag': 72,
            'times_right': 3.5,
            'times_wrong': 2.0,
            'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
            'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
            'secondary_right': []}
    db.tag_records.insert(**trdata)
    db.commit()

    usrows = db(db.user_stats.day1 == datetime.date(2014, 1, 26))
    if not usrows.isempty():
        usrows.delete()
    usdata = {'name': user_login['id'],
            'year': 2014,
            'month': 1,
            'week': 5,
            'updated': datetime.datetime.now(),
            'day1': datetime.date(2014, 1, 26),
            'day2': datetime.date(2014, 1, 27),
            'day3': datetime.date(2014, 1, 28),
            'day4': datetime.date(2014, 1, 29),
            'day5': datetime.date(2014, 1, 30),
            'day6': datetime.date(2014, 1, 31),
            'day7': datetime.date(2014, 2, 1),
            'count1': [],
            'count2': [logs[0]],
            'count3': [],
            'count4': [l for l in logs[1:4]],
            'count5': [],
            'count6': [logs[4]],
            'count7': [logs[5]],
            'logs_by_tag': make_json({72: logs}),
            'logs_right': [logs[0], logs[1], logs[5]],
            'logs_wrong': [logs[2], logs[3], logs[4]],
            'done': 6}
    db.user_stats.insert(**usdata)
    db.commit()

    data = {'user_id': user_login['id'], 'auth': current.auth}
    return Stats(**data), logs


class TestStats():
    '''
    Unit testing class for the Stats class in modules/paideia_stats.py
    '''

    def test_local(self, myStats):
        """
        Unit test for methodname.

        # TODO: add test for daylight savings handling
        """
        dt = datetime.datetime(2014, 2, 2, 2, 0)
        data = {'tz': timezone('America/Toronto')}

        expected = {'year': 2014,
                    'month': 2,
                    'day': 1}

        actual = myStats[0]._local(dt, **data)

        assert actual.year == expected['year']
        assert actual.month == expected['month']
        assert actual.day == expected['day']

    def test_add_promotion_data(self, myStats, web2py, user_login):
        """
        """
        db = web2py.db
        tr = db(db.tag_records.name == user_login['id']).select().as_list()
        for idx, t in enumerate(tr):
            tr[idx] = {k: v for k, v in t.iteritems()
                    if k not in ['id', 'name', 'in_path', 'step']}
            print 'lastright = ', parser.parse(t['tlast_right'])
            tr[idx]['tlast_right'] = parser.parse(t['tlast_right'])
            tr[idx]['tlast_wrong'] = parser.parse(t['tlast_wrong'])

        expected = [{'secondary_right': [],
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is newly added to input
                     'cat1_reached':  (datetime.datetime(2013, 12, 31, 19, 0),
                                       'Dec 31, 2013'),
                     'cat2_reached':  (None, None),
                     'cat3_reached':  (None, None),
                     'cat4_reached':  (None, None)}]

        actual = myStats[0]._add_promotion_data(tr)
        assert len(actual) == len(expected)
        for k in expected[0].keys():
            assert actual[0][k] == expected[0][k]

    def test_add_progress_data(self, myStats, web2py, user_login):
        """
        """
        db = web2py.db
        tr = db(db.tag_records.name == user_login['id']).select().as_list()
        for idx, t in enumerate(tr):
            tr[idx] = {k: v for k, v in t.iteritems()
                    if k not in ['id', 'name', 'in_path', 'step']}
            print 'lastright = ', parser.parse(t['tlast_right'])
            tr[idx]['tlast_right'] = parser.parse(t['tlast_right'])
            tr[idx]['tlast_wrong'] = parser.parse(t['tlast_wrong'])

        expected = [{'secondary_right': [],
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is added by this method
                     'current_level': 1,
                     'review_level': 1}]
        actual = myStats[0]._add_progress_data(tr)
        assert len(actual) == len(expected)
        for k in actual[0].keys():
            assert actual[0][k] == expected[0][k]

    def test_add_tag_data(self, myStats, web2py, user_login):
        """docstring for test_add_tag_data"""
        db = web2py.db
        tr = db(db.tag_records.name == user_login['id']).select().as_list()
        for idx, t in enumerate(tr):
            tr[idx] = {k: v for k, v in t.iteritems()
                    if k not in ['id', 'name', 'in_path', 'step']}
            print 'lastright = ', parser.parse(t['tlast_right'])
            tr[idx]['tlast_right'] = parser.parse(t['tlast_right'])
            tr[idx]['tlast_wrong'] = parser.parse(t['tlast_wrong'])
        expected = [{'secondary_right': [],
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is added by this method
                     'set': 3,
                     'badge_name': 'the definite article',
                     'badge_description': 'using singular forms of the '
                                          'definite article',
                     'slides': [10]}]
        actual = myStats[0]._add_tag_data(tr)
        pprint(actual)
        assert len(actual) == len(expected)
        for k in actual[0].keys():
            assert actual[0][k] == expected[0][k]

    def test_make_logs_into_weekstats(self, myStats, web2py):
        """docstring for _get_stats_from_logs"""
        db = web2py.db
        logs = myStats[1]
        expected = {2014: {4: ({datetime.date(2014, 1, 26): [243906L]},
                               {72L: [243906L]},
                               [243906L],
                               []),
                           5: ({datetime.date(2014, 1, 28): [243907L, 243908L, 243909L],
                               datetime.date(2014, 1, 30): [243910L],
                               datetime.date(2014, 1, 31): [243911L]},
                               {72L: [243907L, 243908L, 243909L, 243910L, 243911L]},
                               [243907L, 243911L],
                               [243908L, 243909L, 243910L])}}
        logs = db(db.attempt_log.id.belongs(myStats[1])).select()
        actual = myStats[0]._make_logs_into_weekstats(logs)
        pprint(actual)
        for year, weeks in actual.iteritems():
            for weeknum, tup in weeks.iteritems():
                for dt, count in tup[0].iteritems():
                    assert count == expected[year][weeknum][0][dt]
                for tag, lst in tup[1].iteritems():
                    assert lst == expected[year][weeknum][1][tag]
                assert tup[2:] == expected[year][weeknum][2:]

    def test_add_log_data(self, myStats, web2py, user_login):
        """docstring for test_add_log_data"""
        db = web2py.db
        logs = myStats[1]
        tr = db(db.tag_records.name == user_login['id']).select().as_list()
        for idx, t in enumerate(tr):
            tr[idx] = {k: v for k, v in t.iteritems()
                    if k not in ['id', 'name', 'in_path', 'step']}
            print 'lastright = ', parser.parse(t['tlast_right'])
            tr[idx]['tlast_right'] = parser.parse(t['tlast_right'])
            tr[idx]['tlast_wrong'] = parser.parse(t['tlast_wrong'])
        expected = [{'secondary_right': [],
                     'avg_score': 0.6,
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is added by this method
                     'logs_by_week': {2012: {},
                                      2013: {},
                                      2014: {5L: {datetime.datetime(2014, 1, 26, 0, 0): [],
                                                  datetime.datetime(2014, 1, 27, 0, 0): [logs[0]],
                                                  datetime.datetime(2014, 1, 28, 0, 0): [],
                                                  datetime.datetime(2014, 1, 29, 0, 0): [logs[1],
                                                                                         logs[2],
                                                                                         logs[3]],
                                                  datetime.datetime(2014, 1, 30, 0, 0): [],
                                                  datetime.datetime(2014, 1, 31, 0, 0): [logs[4]],
                                                  datetime.datetime(2014, 2, 1, 0, 0): [logs[5]]},
                                             }
                                      },
                     'logs_right': [logs[0], logs[1], logs[5]],
                     'logs_wrong': [logs[2], logs[3], logs[4]]
                     }]
        actual = myStats[0]._add_log_data(tr)
        pprint(actual)
        assert len(actual) == len(expected)
        assert len(actual[0].keys()) == len(actual[0].keys())
        for k in actual[0].keys():
            if isinstance(actual[0][k], dict):
                for sk in actual[0][k].keys():
                    if isinstance(actual[0][k][sk], dict):
                        for ssk in actual[0][k][sk].keys():
                            assert actual[0][k][sk][ssk] == expected[0][k][sk][ssk]
                    else:
                        assert actual[0][k][sk] == expected[0][k][sk]
            else:
                assert actual[0][k] == expected[0][k]

    def test_active_tags(self, user_login, myStats, web2py):
        """
        """
        db = web2py.db
        logs = myStats[1]
        now = datetime.datetime(2014, 2, 2, 2, 0)
        dtw = datetime.datetime(2014, 1, 31, 10, 0)
        dtr = datetime.datetime(2014, 2, 1, 20, 0)
        dtw_local = datetime.datetime(2014, 1, 31, 05, 0)
        dtr_local = datetime.datetime(2014, 2, 1, 15, 0)
        print 'delta_right:', now - dtr
        print 'delta_wrong:', now - dtw
        tagnum = 72
        badgerow = db.badges(db.badges.tag == tagnum)
        expected = [{'tag': tagnum,
                     'avg_score': 0.6,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_wrong': (dtw_local, 'Jan 31'),
                     'tlast_right': (dtr_local, 'Feb  1'),
                     'secondary_right': [],
                     'set': 3,
                     'rw_ratio': 3.5 / 2.0,
                     'delta_wrong': now - dtw,
                     'delta_right': now - dtr,
                     'delta_right_wrong': dtr - dtw if dtr > dtw else datetime.timedelta(days=0),
                     'badge_name': badgerow.badge_name,
                     'badge_description': badgerow.description,
                     'slides': [10],
                     'current_level': 1,
                     'review_level': 1,
                     'cat1_reached':  (datetime.datetime(2013, 12, 31, 19, 0), 'Dec 31, 2013'),
                     'cat2_reached':  (None, None),
                     'cat3_reached':  (None, None),
                     'cat4_reached':  (None, None),
                     'logs_by_week': {2012: {},
                                      2013: {},
                                      2014: {5L: {datetime.datetime(2014, 1, 26, 0, 0): [],
                                                  datetime.datetime(2014, 1, 27, 0, 0): [logs[0]],
                                                  datetime.datetime(2014, 1, 28, 0, 0): [],
                                                  datetime.datetime(2014, 1, 29, 0, 0): [logs[1],
                                                                                         logs[2],
                                                                                         logs[3]],
                                                  datetime.datetime(2014, 1, 30, 0, 0): [],
                                                  datetime.datetime(2014, 1, 31, 0, 0): [logs[4]],
                                                  datetime.datetime(2014, 2, 1, 0, 0): [logs[5]]},
                                             }
                                      },
                     'logs_right': [logs[0], logs[1], logs[5]],
                     'logs_wrong': [logs[2], logs[3], logs[4]],
                     'steplist': [b.id for b in db(db.steps.tags.contains(tagnum)
                                                   ).select()],
                     'steplist2': [b.id for b in
                                   db(db.steps.tags_secondary.contains(tagnum)
                                      ).select()],
                     'steplist3': [b.id for b in
                                   db(db.steps.tags_ahead.contains(tagnum)
                                      ).select()],
                     }]

        actual = myStats[0].active_tags(now=now)
        print 'actal dw:', actual[0]['delta_wrong']
        print 'actal dr:', actual[0]['delta_right']
        pprint(actual)
        assert len(actual) == len(expected)
        for k in actual[0].keys():
            assert actual[0][k] == expected[0][k]

    def test_monthcal(self, myStats):
        """docstring for test_monthcal"""
        expected = '<div class="paideia_monthcal">' \
                   '<span class="monthcal_intro_line">Questions answered each day in</span>' \
                   '<table border="0" cellpadding="0" cellspacing="0" class="month">\n' \
                   '<tr>' \
                   '<th class="month" colspan="7">' \
                   '<a class="monthcal_nav_link next" ' \
                   'href="/paideia/reporting/calendar.load/139/2014/2" ' \
                   'onclick="web2py_component(&quot;/paideia/reporting/' \
                   'calendar.load/139/2014/2&quot;,&quot;tab_calendar&quot;);return ' \
                   'false;">' \
                   '<span class="icon-chevron-right"></span>' \
                   '</a>' \
                   '<a class="monthcal_nav_link previous" ' \
                   'href="/paideia/reporting/calendar.load/139/2013/12" ' \
                   'onclick="web2py_component(&quot;/paideia/reporting/' \
                   'calendar.load/139/2013/12&quot;,&quot;tab_calendar&quot;);return ' \
                   'false;">' \
                   '<span class="icon-chevron-left"></span>' \
                   '</a>' \
                   '<span class="dropdown">' \
                   '<a class="dropdown-toggle" data-target="#" ' \
                   'data-toggle="dropdown" href="#" id="month-label" role="button">' \
                   'January 2014 <b class="caret"></b>' \
                   '</a>' \
                   '<ul aria-labelledby="month-label" class="dropdown-menu" role="menu">' \
                   '<li class="divider"></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/12" ' \
                   'tabindex="-1">December 2013' \
                   '</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/11" ' \
                   'tabindex="-1">November 2013' \
                   '</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/10" ' \
                   'tabindex="-1">October 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/9" ' \
                   'tabindex="-1">September 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/8" ' \
                   'tabindex="-1">August 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/7" ' \
                   'tabindex="-1">July 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/6" ' \
                   'tabindex="-1">June 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/5" ' \
                   'tabindex="-1">May 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/4" ' \
                   'tabindex="-1">April 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/3" ' \
                   'tabindex="-1">March 2013</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2013/2" ' \
                   'tabindex="-1">February 2013</a></li>' \
                   '<li class="divider"></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/12" ' \
                   'tabindex="-1">December 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/11" ' \
                   'tabindex="-1">November 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/10" ' \
                   'tabindex="-1">October 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/9" ' \
                   'tabindex="-1">September 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/8" ' \
                   'tabindex="-1">August 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/7" ' \
                   'tabindex="-1">July 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/6" ' \
                   'tabindex="-1">June 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/5" ' \
                   'tabindex="-1">May 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/4" ' \
                   'tabindex="-1">April 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/3" ' \
                   'tabindex="-1">March 2012</a></li>' \
                   '<li><a href="/paideia/reporting/calendar.load/139/2012/2" ' \
                   'tabindex="-1">February 2012</a></li>' \
                   '<li class="divider"></li>' \
                   '</ul>' \
                   '</span>' \
                   '</th>' \
                   '</tr>\n' \
                   '<tr>' \
                        '<th class="sun">Sun</th>' \
                        '<th class="mon">Mon</th>' \
                        '<th class="tue">Tue</th>' \
                        '<th class="wed">Wed</th>' \
                        '<th class="thu">Thu</th>' \
                        '<th class="fri">Fri</th>' \
                        '<th class="sat">Sat</th>' \
                    '</tr>\n' \
                    '<tr>' \
                        '<td class="noday"><span class="cal_num">\xc2\xa0</span></td>' \
                        '<td class="noday"><span class="cal_num">\xc2\xa0</span></td>' \
                        '<td class="noday"><span class="cal_num">\xc2\xa0</span></td>' \
                        '<td class="wed"><span class="cal_num">1</span><span class="daycount">1</span></td>' \
                        '<td class="thu"><span class="cal_num">2</span></td>' \
                        '<td class="fri"><span class="cal_num">3</span></td>' \
                        '<td class="sat"><span class="cal_num">4</span></td>' \
                    '</tr>\n' \
                    '<tr>' \
                        '<td class="sun"><span class="cal_num">5</span></td>' \
                        '<td class="mon"><span class="cal_num">6</span></td>' \
                        '<td class="tue"><span class="cal_num">7</span></td>' \
                        '<td class="wed"><span class="cal_num">8</span></td>' \
                        '<td class="thu"><span class="cal_num">9</span></td>' \
                        '<td class="fri"><span class="cal_num">10</span></td>' \
                        '<td class="sat"><span class="cal_num">11</span></td>' \
                    '</tr>\n' \
                    '<tr>' \
                        '<td class="sun"><span class="cal_num">12</span></td>' \
                        '<td class="mon"><span class="cal_num">13</span></td>' \
                        '<td class="tue"><span class="cal_num">14</span></td>' \
                        '<td class="wed"><span class="cal_num">15</span></td>' \
                        '<td class="thu"><span class="cal_num">16</span></td>' \
                        '<td class="fri"><span class="cal_num">17</span></td>' \
                        '<td class="sat"><span class="cal_num">18</span></td>' \
                    '</tr>\n' \
                    '<tr>' \
                        '<td class="sun"><span class="cal_num">19</span></td>' \
                        '<td class="mon"><span class="cal_num">20</span></td>' \
                        '<td class="tue"><span class="cal_num">21</span></td>' \
                        '<td class="wed"><span class="cal_num">22</span></td>' \
                        '<td class="thu"><span class="cal_num">23</span></td>' \
                        '<td class="fri"><span class="cal_num">24</span></td>' \
                        '<td class="sat"><span class="cal_num">25</span></td>' \
                    '</tr>\n' \
                    '<tr>' \
                    '<td class="sun"><span class="cal_num">26</span><span class="daycount">0</span></td>' \
                    '<td class="mon"><span class="cal_num">27</span>' \
                                    '<span class="daycount">1</span>' \
                    '</td>' \
                    '<td class="tue"><span class="cal_num">28</span><span class="daycount">0</span></td>' \
                    '<td class="wed"><span class="cal_num">29</span>' \
                                    '<span class="daycount">3</span>' \
                    '</td>' \
                    '<td class="thu"><span class="cal_num">30</span><span class="daycount">0</span></td>' \
                    '<td class="fri"><span class="cal_num">31</span>' \
                                    '<span class="daycount">1</span>' \
                    '</td>' \
                    '<td class="noday"><span class="cal_num">\xc2\xa0</span></td>' \
                    '</tr>\n' \
                    '</table>\n' \
                    '</div>'
        actual = myStats[0].monthcal(year=2014, month=1)
        pprint(actual.xml())
        pprint(expected)
        assert actual.xml() == expected
