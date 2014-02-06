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
from pprint import pprint
from pytz import timezone
from gluon import current
from paideia_stats import Stats


@pytest.fixture()  # params=[n for n in range(4)]
def myStats(user_login, web2py):  # request
    """
    A pytest fixture providing a Stats object for testing.

    user_login fixture from conftest.py
    """
    # case = request.param
    db = web2py.db

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
            'count1': 0,
            'count2': 1,
            'count3': 0,
            'count4': 3,
            'count5': 0,
            'count6': 1,
            'count7': 1,
            'logs_by_tag': {},
            'logs_right': [],
            'logs_wrong': [],
            'done': 6}
    db.user_stats.insert(**usdata)
    db.commit()

    alrows = db(db.attempt_log.name == user_login['id'])
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

    data = {'user_id': user_login['id'], 'auth': current.auth}
    return Stats(**data)


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

        actual = myStats._local(dt, **data)

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
        expected = [{'secondary_right': [],
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is newly added to input
                     'cat1_reached':  (datetime.datetime(2014, 1, 1, 0, 0),
                                       'Jan  1, 2014'),
                     'cat2_reached':  (None, None),
                     'cat3_reached':  (None, None),
                     'cat4_reached':  (None, None)}]

        actual = myStats._add_promotion_data(tr)
        pprint(actual)
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
        expected = [{'secondary_right': [],
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is added by this method
                     'current_level': '1'}]
        actual = myStats._add_progress_data(tr)
        pprint(actual)

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
        expected = [{'secondary_right': [],
                     'tag': 72L,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_right': datetime.datetime(2014, 2, 1, 20, 0),
                     'tlast_wrong': datetime.datetime(2014, 1, 31, 10, 0),
                     # below is added by this method
                     'set': 3,
                     'badge_name': 'missing badge for tag 72',
                     'badge_description': None,
                     'slides': [10]}]
        actual = myStats._add_tag_data(tr)
        pprint(actual)
        assert len(actual) == len(expected)
        for k in actual[0].keys():
            assert actual[0][k] == expected[0][k]

    def test_add_log_data(self):
        """docstring for test_add_log_data"""
        pass

    def test_active_tags(self, user_login, myStats, web2py):
        """
        """
        db = web2py.db
        now = datetime.datetime(2014, 2, 2, 2, 0)
        dtw = datetime.datetime(2014, 1, 31, 10, 0)
        dtr = datetime.datetime(2014, 2, 1, 20, 0)
        tagnum = 72
        badgenum = db.badges(db.badges.tag == tagnum).id
        expected = [{'tag': tagnum,
                     'times_right': 3.5,
                     'times_wrong': 2.0,
                     'tlast_wrong': dtw,
                     'tlast_right': dtr,
                     'secondary_right': [],
                     'set': 1,
                     'rw_ratio': 3.5 / 2.0,
                     'delta_wrong': now - dtw,
                     'delta_right': now - dtr,
                     'delta_right_wrong': dtr - dtw if dtr > dtw else datetime.timedelta(days=0),
                     'badge_name': db.badges(badgenum).badge_name,
                     'badge_description': '',
                     'slides': [10],
                     'current_level': 'cat1',
                     'review_level': None,
                     'cat1_reached':  (datetime.datetime(2014, 1, 1, 0, 0), ''),
                     'cat2_reached':  (None, None),
                     'cat3_reached':  (None, None),
                     'cat4_reached':  (None, None),
                     'steplist': [b.id for b in db(db.steps.tags.contains(tagnum)
                                                   ).select()],
                     'steplist2': [b.id for b in
                                   db(db.steps.tags_secondary.contains(tagnum)
                                      ).select()],
                     'steplist3': [b.id for b in
                                   db(db.steps.tags_ahead.contains(tagnum)
                                      ).select()],
                     'datecounts': {}
                     }]

        actual = myStats.active_tags()
        assert actual == expected
