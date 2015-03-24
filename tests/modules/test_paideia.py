#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""
# Unit tests for the paideia module
#
# Configuration and some fixtures (client, web2py) declared in
# the file tests/conftest.py
# run with py.test -xvs applications/paideia/tests/modules/
"""

import pytest
from paideia import Npc, Location, User, PathChooser, Path, Categorizer, Walk
from paideia import StepFactory, StepText, StepMultiple, NpcChooser, Step
from paideia import StepRedirect, StepViewSlides, StepAwardBadges
from paideia import StepEvaluator, MultipleEvaluator, StepQuotaReached
from paideia import Block, BugReporter, Map
from gluon import current, IMG

import datetime
from pprint import pprint
import re
from copy import copy
from random import randint
#from dateutil import parser
from difflib import Differ
from itertools import chain
from urllib import quote_plus
import pickle


# ===================================================================
# Switches governing which tests to run
# ===================================================================
global_runall = True
global_run_TestNpc = True
global_run_TestLocation = True
global_run_TestStep = True
global_run_TestStepEvaluator = True
global_run_TestMultipleEvaluator = True
global_run_TestPath = True
global_run_TestUser = True
global_run_TestCategorizer = True
global_run_TestMap = True
global_run_TestWalk = True
global_run_TestPathChooser = True
global_run_TestBugReporter = True

# ===================================================================
# Test Fixtures
# ===================================================================


def log_generator(uid, tag, count, numright, lastright, lastwrong, earliest,
                  db):
    """Generate attempt_log mock entries in the database for a test user."""
    datalist = []
    tagsteps = db(db.steps.tags.contains(tag)).select(db.steps.id).as_list()
    stepids = [t['id'] for t in tagsteps]
    steppaths = db(db.paths.steps.contains(stepids)
                   ).select(db.paths.id, db.paths.steps).as_list()
    pathids = {s: p['id'] for s in stepids for p in steppaths if s in p['steps']}
    if len(pathids.keys()) > 0:
        for n in range(count):
            mystep = pathids.keys()[randint(0, len(pathids.keys()) - 1)]
            score = 1.0 if n < numright else 0.0
            latest = lastright if (abs(score - 1) <= 0.001) else lastwrong
            if n == (numright - 1):
                mydt = lastright
            elif n == (count - 1):
                mydt = lastwrong
            else:
                mydt = earliest + datetime.timedelta(
                    seconds=randint(0, int((latest - earliest).total_seconds())))
            rowdict = {'name': uid,
                    'step': mystep,
                    'in_path': pathids[int(mystep)],
                    'score': score,
                    'dt_attempted': mydt,
                    'user_response': 'norwiegian blue'}
            datalist.append(rowdict)
    loglist = db.attempt_log.bulk_insert(datalist)
    db.commit()
    return loglist


def dt(string):
    """Return datetime object parsed from the string argument supplied"""
    try:
        format = "%Y-%m-%d"
        return datetime.datetime.strptime(string, format)
    except ValueError:
        format = "%Y-%m-%d %H:%M:%S"
        return datetime.datetime.strptime(string, format)


@pytest.fixture
def mytagpros():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'latest_new': 10,
                                   'name': 109,
                                   'cat1': [2, 5, 6, 9, 10, 16, 17, 30, 36,
                                            46, 48, 61, 62, 63, 66, 67,
                                            69, 71, 72, 73, 74, 76, 77, 82, 83,
                                            84, 85, 86, 87, 88, 90, 91, 93, 94,
                                            95, 115, 117, 118, 121, 124, 129,
                                            133],  # removed 128 to test demotion
                                   'cat2': [14],  # was [], moved to test promotion
                                   'cat3': [],  # was [14]
                                   'cat4': [18, 29, 38, 47, 49, 68, 75, 89, 92,
                                            116, 119, 120, 122, 128],  # added 128
                                   'rev1': [],
                                   'rev3': [],
                                   'rev2': [],
                                   'rev4': []},
          }
    return tp


@pytest.fixture
def mycatsout_core_algorithm():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'rev1': [1, 2, 5, 6, 9, 10, 16, 17, 24, 30,
                                            32, 35, 36, 40, 43, 46, 48, 61, 62,
                                            63, 66, 67, 69, 71, 72, 73, 74, 76,
                                            77, 82, 83, 84, 85, 86, 87, 88, 90,
                                            91, 93, 94, 95, 115, 117, 118, 121,
                                            124, 128, 129, 133],
                                            # 55, 96, 102, 103, 104, 131, 135,
                                            # 130, 132, 134 are untried
                                            # FIXME: why is 4 not here?
                                   'rev2': [],
                                   'rev3': [14],
                                   'rev4': [18, 29, 38, 47, 49, 68, 75, 89, 92,
                                            116, 119, 120, 122]},
          }
    return tp


@pytest.fixture
def mycatsout_add_untried():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'rev1': [1, 2, 4, 5, 6, 9, 10, 16, 17, 24, 30,
                                            32, 35, 36, 40, 43, 46, 48, 55, 61, 62,
                                            63, 66, 67, 69, 71, 72, 73, 74, 76,
                                            77, 82, 83, 84, 85, 86, 87, 88, 90,
                                            91, 93, 94, 95, 96, 102, 115, 117,
                                            118, 121, 124, 128, 129, 130, 131,
                                            132, 133, 135],
                                   'rev2': [],
                                   'rev3': [14],
                                   'rev4': [18, 29, 38, 47, 49, 68, 75, 89, 92,
                                            116, 119, 120, 122]},
          }
    return tp


@pytest.fixture
def mycatsout_remove_dups():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'rev1': [2, 4, 5, 6, 9, 10, 16, 17, 30,
                                            36, 46, 48, 55, 61, 62,
                                            63, 66, 67, 69, 71, 72, 73, 74, 76,
                                            77, 82, 83, 84, 85, 86, 87, 88, 90,
                                            91, 93, 94, 95, 96, 102, 115, 117,
                                            118, 121, 124, 128, 129, 130, 131,
                                            132, 133, 135],
                                   'rev2': [],
                                   'rev3': [14],
                                   'rev4': [18, 29, 38, 47, 49, 68, 75, 89, 92,
                                            116, 119, 120, 122]},
          }
    return tp


@pytest.fixture
def mycatsout_find_changes():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'cat1': [2, 4, 5, 6, 9, 10, 16, 17, 30,
                                            36, 46, 48, 55, 61, 62,
                                            63, 66, 67, 69, 71, 72, 73, 74, 76,
                                            77, 82, 83, 84, 85, 86, 87, 88, 90,
                                            91, 93, 94, 95, 96, 102, 115, 117,
                                            118, 121, 124, 129, 130, 131, 132,
                                            133, 135],
                                    # 4, 55, 96, 102, 130, 131, 132, 135 are new
                                   'cat2': [],
                                   'cat3': [14],
                                   'cat4': [18, 29, 38, 47, 49, 68, 75, 89, 92,
                                            116, 119, 120, 122, 128],
                                   'rev1': [2, 4, 5, 6, 9, 10, 16, 17, 30,
                                            36, 46, 48, 55, 61, 62,
                                            63, 66, 67, 69, 71, 72, 73, 74, 76,
                                            77, 82, 83, 84, 85, 86, 87, 88, 90,
                                            91, 93, 94, 95, 96, 102, 115, 117,
                                            118, 121, 124, 128, 129, 130, 131, 132,
                                            133, 135],
                                   'rev2': [],
                                   'rev3': [14],
                                   'rev4': [18, 29, 38, 47, 49, 68, 75, 89, 92,
                                            116, 119, 120, 122]},
          }
    return tp


@pytest.fixture
def mydemoted():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'cat1': [128],
                                   'cat2': [],
                                   'cat3': [],
                                   'cat4': []},
          }
    return tp


@pytest.fixture
def mypromoted():
    """A fixture providing mock 'promoted' values"""
    tp = {'Simon Pan 2014-03-21': {'cat1': [],
                                   'cat2': [],
                                   'cat3': [14],
                                   'cat4': [],
                                   'rev1': [],
                                   'rev3': [],
                                   'rev2': [],
                                   'rev4': []},
          }
    return tp


@pytest.fixture
def mypromotions():
    """Test fixture providing badges_begun rescoreds"""
    prom = {'Simon Pan 2014-03-21':
            [{'name': 109L,
              'tag': 14L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': datetime.datetime(2014, 1, 3, 21, 0, 0),
              'cat3': None,
              'cat4': None},
             {'name': 109L,
              'tag': 4L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 46L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 47L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 69L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 95L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 117L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 118L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 119L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'tag': 120L,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 2L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 10L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 18L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'tag': 30L,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 38L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 49L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 55L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 86L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 87L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 121L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 122L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None},
             {'name': 109L,
              'tag': 128L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None}
             ]
            }
    return prom


@pytest.fixture
def mytagrecs():
    """A fixture providing mock tag_records data."""
    tr = {'Simon Pan 2014-03-21':
          [{'id': 383380L,
            'tag': 1L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-26 19:12:41.851235',
                                '2014-02-26 21:11:21.449747',
                                '2014-02-27 22:28:50.991776',
                                '2014-02-28 17:16:35.793071',
                                '2014-03-03 00:53:41.376872',
                                '2014-03-03 00:54:27.906045',
                                '2014-03-05 04:15:45.253453',
                                '2014-03-05 22:19:12.982545',
                                '2014-03-06 22:58:36.468321',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832',
                                '2014-03-07 19:13:40.727329',
                                '2014-03-10 18:56:02.777857',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-11 18:15:09.996416',
                                '2014-03-12 20:53:03.514677',
                                '2014-03-13 19:50:36.891023',
                                '2014-03-13 19:51:27.333192',
                                '2014-03-14 20:31:20.800429',
                                '2014-03-17 22:13:59.395609',
                                '2014-03-20 00:45:07.189652',
                                '2014-03-20 01:13:10.767671',
                                '2014-03-20 01:20:07.238262',
                                '2014-03-20 01:21:42.738633'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 15, 32, 1)
            },
           {'id': 383615L, 'in_path': None,
            'tag': 4L,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:21:48.396981',
                                '2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-20 00:46:03.191941',
                                '2014-03-20 01:19:00.049401'],
            'step': None,
            'tag': 2L,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383419L,
            'tag': 5L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 23, 45, 25)},
           {'id': 383219L,
            'tag': 6L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-05 04:23:40.815243',
                                '2014-03-05 04:24:02.586695',
                                '2014-03-05 04:24:12.043533',
                                '2014-03-05 22:27:29.538283',
                                '2014-03-20 01:20:07.234653'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 9, 27, 14, 8, 27),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 383119L,
            'tag': 9L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:13:10.771437',
                                '2014-03-20 01:18:26.331487',
                                '2014-03-20 01:20:07.245236',
                                '2014-03-20 01:27:31.974083'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383613L,
            'tag': 10L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-10-07 22:48:58.563124'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383969L,
            'tag': 14L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 93.0,
            'times_wrong': 18.0,
            'tlast_right': datetime.datetime(2014, 3, 17, 22, 29, 3),
            'tlast_wrong': datetime.datetime(2014, 1, 21, 18, 21, 40)},
           {'id': 383116L,
            'tag': 16L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-18 19:17:02.407886',
                                '2014-02-18 19:17:25.063330',
                                '2014-02-19 20:36:42.985334',
                                '2014-02-19 20:37:08.797027',
                                '2014-02-20 22:59:13.563362',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847',
                                '2014-02-28 17:39:34.566118',
                                '2014-02-28 17:39:49.479375'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 384068L,
            'tag': 17L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10)},
           {'id': 383858L,
            'tag': 18L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 95.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 1, 24, 23, 32, 23),
            'tlast_wrong': datetime.datetime(2013, 10, 23, 18, 0, 5)},
           {'id': 383978L,
            'tag': 24L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 19),
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 50, 54)},
           {'id': 383546L,
            'tag': 29L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-10-03 21:37:10.915378',
                                '2013-10-03 21:38:26.430271',
                                '2013-10-03 21:38:38.754177',
                                '2013-10-04 19:48:45.218412',
                                '2013-10-05 20:14:31.792403',
                                '2013-10-05 20:16:17.321064',
                                '2013-10-05 20:17:02.739388',
                                '2013-10-07 22:45:26.615676',
                                '2013-10-08 18:14:36.129966',
                                '2013-10-20 02:14:36.180224',
                                '2013-10-25 02:05:14.367961',
                                '2013-10-25 02:06:05.067229',
                                '2013-11-16 02:22:43.965206',
                                '2013-11-16 02:23:26.988475',
                                '2014-01-24 23:29:39.321832',
                                '2014-02-10 02:13:43.091516',
                                '2014-02-11 02:53:27.756725',
                                '2014-02-12 21:11:26.680416',
                                '2014-02-12 21:33:08.570055',
                                '2014-02-20 23:05:57.762133'],
            'step': None,
            'times_right': 28.0,
            'times_wrong': 10.0,
            'tlast_right': datetime.datetime(2014, 2, 11, 2, 53, 27),
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 37, 10)},
           {'id': 383614L,
            'tag': 30L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-11-04 14:09:58.699103',
                                '2013-11-04 14:10:11.676329',
                                '2013-11-06 16:05:00.762640',
                                '2013-11-06 16:05:10.277542',
                                '2013-11-09 04:11:45.713347',
                                '2013-11-09 04:12:03.602066',
                                '2013-11-13 15:34:19.536313',
                                '2013-11-15 01:59:36.619583',
                                '2013-11-16 23:30:52.468572',
                                '2013-11-17 22:32:36.289015',
                                '2013-11-17 22:32:45.869638',
                                '2013-11-17 22:54:28.311941',
                                '2013-12-03 21:52:55.796443',
                                '2013-12-03 21:53:06.210374',
                                '2013-12-03 21:53:13.328905',
                                '2014-01-23 19:27:48.728760',
                                '2014-01-28 02:43:01.370294',
                                '2014-01-31 03:07:18.935169',
                                '2014-01-31 03:16:13.717293',
                                '2014-01-31 03:16:25.387423',
                                '2014-02-04 15:02:12.448057',
                                '2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383478L,
            'tag': 32L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-11-17 22:23:35.574534',
                                '2013-12-03 21:52:42.483799',
                                '2014-01-31 22:25:20.777146'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 10, 2, 20, 38, 45),
            'tlast_wrong': datetime.datetime(2013, 10, 2, 20, 38, 45)},
           {'id': 384067L,
            'tag': 35L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-13 20:02:54.213157',
                                '2014-03-13 20:03:06.719722'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 2, 52),
            'tlast_wrong': datetime.datetime(2014, 3, 13, 20, 2, 52)},
           {'id': 383232L,
            'tag': 36L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-26 19:12:41.851235',
                                '2014-02-26 21:11:21.449747',
                                '2014-02-27 22:28:50.991776',
                                '2014-02-28 17:16:35.793071',
                                '2014-03-03 00:53:41.376872',
                                '2014-03-03 00:54:27.906045',
                                '2014-03-05 04:15:45.253453',
                                '2014-03-05 22:19:12.982545',
                                '2014-03-06 22:58:36.468321',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832',
                                '2014-03-07 19:13:40.727329',
                                '2014-03-10 18:56:02.777857',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-11 18:15:09.996416',
                                '2014-03-12 20:53:03.514677',
                                '2014-03-13 19:50:36.891023',
                                '2014-03-13 19:51:27.333192',
                                '2014-03-13 20:02:54.213157',
                                '2014-03-13 20:03:06.719722',
                                '2014-03-14 20:31:20.800429',
                                '2014-03-17 22:13:59.395609',
                                '2014-03-20 00:45:07.175987',
                                '2014-03-20 01:13:10.776062'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 39, 59)},
           {'id': 383916L,
            'tag': 38L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 16, 32),
            'tlast_wrong': datetime.datetime(2013, 11, 20, 0, 24, 20)},
           {'id': 383979L,
            'tag': 40L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 19),
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 50, 54)},
           {'id': 383980L,
            'tag': 43L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 19),
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 50, 54)},
           {'id': 383420L,
            'tag': 46L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-10-03 21:38:26.430271',
                                '2013-10-03 21:38:38.754177',
                                '2013-10-04 19:48:45.218412',
                                '2013-10-08 18:14:36.129966',
                                '2013-10-09 19:45:40.089605',
                                '2013-10-09 19:46:49.950370',
                                '2013-10-09 19:47:14.835834',
                                '2013-10-25 02:05:14.367961',
                                '2013-10-25 02:06:05.067229',
                                '2013-11-16 02:22:43.965206',
                                '2013-11-16 02:23:26.988475',
                                '2014-02-12 21:18:52.149758',
                                '2014-02-15 03:04:08.599316',
                                '2014-02-17 01:01:49.514350',
                                '2014-02-18 01:32:22.890120'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 23, 45, 25)},
           {'id': 383421L,
            'tag': 47L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 18, 1, 32, 22),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 23, 45, 25)},
           {'id': 383222L,
            'tag': 48L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-01-13 15:17:38.961998',
                                '2014-01-13 23:00:05.839312',
                                '2014-01-20 14:23:30.474737',
                                '2014-01-20 14:35:17.591339',
                                '2014-01-23 19:27:48.728760',
                                '2014-01-28 02:43:01.370294',
                                '2014-01-31 03:07:18.935169',
                                '2014-01-31 03:16:13.717293',
                                '2014-01-31 03:16:25.387423',
                                '2014-02-04 15:02:12.448057',
                                '2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-20 01:13:10.779684'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 11, 17),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 18, 2)},
           {'id': 383890L,
            'tag': 49L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 7, 19, 22, 42),
            'tlast_wrong': datetime.datetime(2013, 11, 2, 2, 13, 11)},
           {'id': 383111L,
            'tag': 61L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:27:11.619260',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:28:33.835836',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:41:36.526278',
                                '2014-03-20 00:45:07.161951',
                                '2014-03-20 00:46:03.185017',
                                '2014-03-20 00:46:37.668822',
                                '2014-03-20 01:13:10.783458',
                                '2014-03-20 01:15:25.999184',
                                '2014-03-20 01:19:00.042374',
                                '2014-03-20 01:20:07.209399',
                                '2014-03-20 01:26:21.063121',
                                '2014-03-20 01:26:42.183147'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 48, 55)},
           {'id': 383217L,
            'tag': 62L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:25:44.135166',
                                '2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:41:36.531712',
                                '2014-03-20 00:45:07.166820',
                                '2014-03-20 00:46:03.188713',
                                '2014-03-20 00:46:37.676085',
                                '2014-03-20 01:13:10.787178',
                                '2014-03-20 01:15:26.006571',
                                '2014-03-20 01:19:00.046118',
                                '2014-03-20 01:20:07.216789',
                                '2014-03-20 01:26:21.066885'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 26, 42),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 13, 58, 40)},
           {'id': 383109L,
            'tag': 63L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:33.835836',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-20 00:41:36.521707',
                                '2014-03-20 00:45:07.170990',
                                '2014-03-20 00:46:03.181437',
                                '2014-03-20 00:46:37.665167',
                                '2014-03-20 01:13:10.790596',
                                '2014-03-20 01:15:25.995401',
                                '2014-03-20 01:19:00.038560',
                                '2014-03-20 01:20:07.205652'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 26, 21),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 45, 36)},
           {'id': 383234L,
            'tag': 66L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:28:33.835836',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:45:07.181056',
                                '2014-03-20 00:46:37.672462',
                                '2014-03-20 01:13:10.794228',
                                '2014-03-20 01:15:26.002995',
                                '2014-03-20 01:20:07.213051'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 43, 27)},
           {'id': 383117L,
            'tag': 67L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:20:07.241677',
                                '2014-03-20 01:21:42.742329',
                                '2014-03-20 01:22:46.003765',
                                '2014-03-20 01:27:31.971359'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383108L,
            'tag': 68L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-12 20:52:04.164228',
                                '2014-03-13 19:51:41.766472',
                                '2014-03-14 20:31:38.950469',
                                '2014-03-20 00:41:36.541744'],
            'step': None,
            'times_right': 77.0,
            'times_wrong': 30.0,
            'tlast_right': datetime.datetime(2014, 3, 5, 22, 39, 53),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 45, 15)},
           {'id': 383543L,
            'tag': 69L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:25:44.135166',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 01:13:10.801349'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 19, 34)},
           {'id': 384040L,
            'tag': 71L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 16, 1),
            'tlast_wrong': datetime.datetime(2014, 2, 12, 4, 3, 50)},
           {'id': 383112L,
            'tag': 72L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 02:21:46.197632',
                                '2014-02-22 02:43:30.852941',
                                '2014-02-27 22:43:40.639117',
                                '2014-03-05 22:25:54.594000',
                                '2014-03-05 22:26:05.479588',
                                '2014-03-07 19:29:25.549794',
                                '2014-03-07 19:29:37.973997',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-20 01:11:17.566601',
                                '2014-03-20 01:13:10.804879'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 28, 36),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 53, 45)},
           {'id': 383114L,
            'tag': 73L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-19 20:36:42.985334',
                                '2014-02-19 20:37:08.797027',
                                '2014-02-20 22:59:13.563362',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383414L,
            'tag': 74L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:20:07.223668',
                                '2014-03-20 01:22:45.994129'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 17, 32),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 10, 31)},
           {'id': 383411L,
            'tag': 75L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-12-03 21:54:52.981560',
                                '2014-01-20 14:29:24.439739',
                                '2014-02-25 01:05:57.858092',
                                '2014-02-25 01:07:59.061393',
                                '2014-02-25 01:09:09.356279',
                                '2014-02-25 01:10:20.265528',
                                '2014-02-25 01:11:45.086382',
                                '2014-03-20 01:20:07.227347'],
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 3, 6),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41)},
           {'id': 383347L,
            'tag': 76L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:13:10.808508'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 22, 45),
            'tlast_wrong': datetime.datetime(2013, 9, 30, 13, 52, 55)},
           {'id': 383115L,
            'tag': 77L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-25 01:11:45.086382',
                                '2014-02-25 01:13:14.462175',
                                '2014-02-25 01:13:42.069870',
                                '2014-02-25 01:41:04.161803',
                                '2014-02-25 01:43:42.693616',
                                '2014-02-26 19:11:09.105744',
                                '2014-02-26 19:11:25.514290',
                                '2014-03-05 04:23:40.815243',
                                '2014-03-05 04:24:02.586695',
                                '2014-03-05 04:24:12.043533',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832',
                                '2014-03-20 01:13:10.812152',
                                '2014-03-20 01:20:07.231051',
                                '2014-03-20 01:21:42.745721',
                                '2014-03-20 01:22:45.999836'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383220L,
            'tag': 82L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:25:44.135166',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:41:36.536662',
                                '2014-03-20 01:13:10.815555'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 383221L,
            'tag': 83L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 02:41:48.717205',
                                '2014-02-22 02:48:06.942953',
                                '2014-02-22 02:48:31.979752',
                                '2014-02-22 02:49:45.161565',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847',
                                '2014-02-25 01:17:35.500535',
                                '2014-02-25 21:50:44.559794',
                                '2014-02-25 21:51:13.463541',
                                '2014-02-27 22:43:40.639117',
                                '2014-02-28 17:54:08.870595',
                                '2014-02-28 17:56:42.590879',
                                '2014-02-28 17:58:57.035455',
                                '2014-03-05 04:23:40.815243',
                                '2014-03-05 04:24:02.586695',
                                '2014-03-05 04:24:12.043533',
                                '2014-03-20 01:13:10.818786',
                                '2014-03-20 01:15:26.009951'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 9, 27, 14, 8, 27),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 384069L,
            'tag': 84L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10)},
           {'id': 384070L,
            'tag': 85L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10)},
           {'id': 383612L,
            'tag': 86L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:26:47.680713',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:28:33.835836',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 01:13:10.821758'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383637L,
            'tag': 87L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-11-04 14:09:58.699103',
                                '2013-11-04 14:10:11.676329',
                                '2013-11-06 16:05:00.762640',
                                '2013-11-06 16:05:10.277542',
                                '2013-11-09 04:11:45.713347',
                                '2013-11-09 04:12:03.602066',
                                '2013-11-13 15:34:19.536313',
                                '2013-11-15 01:59:36.619583',
                                '2013-11-16 23:30:52.468572',
                                '2013-11-17 22:32:36.289015',
                                '2013-11-17 22:32:45.869638',
                                '2013-11-17 22:54:28.311941',
                                '2013-12-03 21:52:55.796443',
                                '2013-12-03 21:53:06.210374',
                                '2013-12-03 21:53:13.328905',
                                '2014-01-23 19:27:48.728760',
                                '2014-01-28 02:43:01.370294',
                                '2014-01-31 03:07:18.935169',
                                '2014-01-31 03:16:13.717293',
                                '2014-01-31 03:16:25.387423',
                                '2014-02-04 15:02:12.448057',
                                '2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 12, 17)},
           {'id': 383118L,
            'tag': 88L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 02:21:24.974752',
                                '2014-02-22 02:21:46.197632',
                                '2014-02-22 02:43:30.852941',
                                '2014-02-25 01:41:04.161803',
                                '2014-02-25 01:43:42.693616',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832',
                                '2014-03-13 19:52:16.747902',
                                '2014-03-20 01:13:10.824876',
                                '2014-03-20 01:15:26.013721'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383233L,
            'tag': 89L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 13, 22, 36, 47),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 41, 6)},
           {'id': 383113L,
            'tag': 90L,
            'times_right': 1.0,
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'step': None,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-14 22:33:12.662352',
                                '2014-02-22 02:14:57.149550',
                                '2014-03-20 01:20:07.220079']},
           {'name': 109L,
            'tag': 91L,
            'times_right': 1.0,
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 5, 35),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 18, 26),
            'step': None,
            'in_path': None,
            'id': 383218L,
            'secondary_right': ['2014-02-20 22:59:13.563362',
                                '2014-02-20 23:00:34.203297',
                                '2014-02-20 23:00:49.080672',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847',
                                '2014-02-25 01:05:57.858092',
                                '2014-02-25 01:07:59.061393',
                                '2014-02-25 01:09:09.356279',
                                '2014-02-25 01:10:20.265528',
                                '2014-02-25 01:11:45.086382',
                                '2014-02-28 17:39:34.566118',
                                '2014-02-28 17:39:49.479375',
                                '2014-03-13 19:52:16.747902']},
           {'name': 109L,
            'tag': 92L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 50, 13),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 5, 4, 24, 12),
            'step': None,
            'in_path': None,
            'id': 383237L,
            'secondary_right': ['2014-02-14 22:33:12.662352',
                                '2014-02-22 02:14:57.149550',
                                '2014-03-10 19:14:52.759060',
                                '2014-03-10 19:14:58.914173']},
           {'name': 109L,
            'tag': 93L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 9, 30, 13, 39, 50),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 24, 41),
            'step': None,
            'in_path': None,
            'id': 383346L,
            'secondary_right': ['2014-02-24 00:54:44.343751',
                                '2014-02-24 00:56:13.859405',
                                '2014-02-25 01:13:14.462175',
                                '2014-02-25 01:13:42.069870',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832']},
           {'name': 109L,
            'tag': 94L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 41, 56),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 0, 41, 36),
            'step': None,
            'in_path': None,
            'id': 383976L,
            'secondary_right': None},
           {'name': 109L,
            'tag': 95L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 34, 49),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'step': None,
            'in_path': None,
            'id': 383545L,
            'secondary_right': ['2013-10-03 21:38:26.430271',
                                '2013-10-03 21:38:38.754177',
                                '2013-10-04 02:49:27.280458',
                                '2013-10-04 19:50:29.608630',
                                '2013-10-07 03:11:12.707955',
                                '2013-10-08 18:14:36.129966',
                                '2013-10-18 17:39:46.227522',
                                '2013-11-16 02:22:43.965206',
                                '2013-11-16 02:23:26.988475',
                                '2013-11-21 22:29:04.960673',
                                '2013-11-30 02:58:13.544984',
                                '2013-12-03 21:54:52.981560',
                                '2014-01-20 14:29:24.439739']},
           {'name': 109L,
            'tag': 115L,
            'times_right': 1.0,
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'step': None,
            'in_path': None,
            'id': 383120L,
            'secondary_right': ['2014-02-18 19:43:17.771731',
                                '2014-02-25 01:05:57.858092',
                                '2014-02-25 01:07:59.061393',
                                '2014-02-25 01:09:09.356279',
                                '2014-02-25 01:10:20.265528',
                                '2014-02-25 01:11:45.086382',
                                '2014-02-25 01:41:04.161803',
                                '2014-02-25 01:43:42.693616',
                                '2014-02-27 22:43:40.639117',
                                '2014-03-03 01:04:00.557721',
                                '2014-03-03 01:04:17.237054',
                                '2014-03-05 22:25:54.594000',
                                '2014-03-05 22:26:05.479588',
                                '2014-03-07 19:29:25.549794',
                                '2014-03-07 19:29:37.973997',
                                '2014-03-07 19:31:03.859650',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-20 01:20:07.248791']},
           {'name': 109L,
            'tag': 116L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 10, 18, 58, 17),
            'step': None,
            'in_path': None,
            'id': 383412L,
            'secondary_right': ['2014-02-10 02:31:21.978049',
                                '2014-02-12 03:55:11.346488',
                                '2014-02-12 03:55:49.469451']},
           {'name': 109L,
            'tag': 117L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'in_path': None,
            'id': 383413L,
            'secondary_right': ['2014-03-06 22:58:36.468321',
                                '2014-03-07 19:13:40.727329',
                                '2014-03-10 18:56:02.777857',
                                '2014-03-11 18:15:09.996416',
                                '2014-03-12 20:53:03.514677',
                                '2014-03-13 19:50:36.891023',
                                '2014-03-13 19:51:27.333192',
                                '2014-03-14 20:31:20.800429',
                                '2014-03-17 22:13:59.395609',
                                '2014-03-20 00:45:07.186095']},
           {'name': 109L,
            'tag': 118L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 19, 34),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'step': None,
            'in_path': None,
            'id': 383544L,
            'secondary_right': ['2013-10-09 19:46:49.950370',
                                '2013-10-09 19:47:14.835834',
                                '2014-02-12 21:18:52.149758',
                                '2014-02-15 03:04:08.599316',
                                '2014-02-17 01:01:49.514350',
                                '2014-02-18 01:32:22.890120']},
           {'name': 109L,
            'tag': 119L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 13),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 25, 21, 51, 13),
            'step': None,
            'in_path': None,
            'id': 383541L,
            'secondary_right': ['2013-11-02 02:15:58.052970',
                                '2013-11-04 13:05:27.666637',
                                '2013-11-05 22:23:39.144027',
                                '2013-11-05 22:33:03.605229',
                                '2013-11-05 22:33:17.950054',
                                '2013-11-05 22:43:15.156061',
                                '2013-11-06 16:10:38.666253',
                                '2013-11-06 16:11:09.370731',
                                '2013-11-06 16:20:00.893924',
                                '2013-11-06 16:34:10.466328',
                                '2013-11-07 21:46:08.216755',
                                '2013-11-16 02:34:23.638274',
                                '2013-12-29 21:16:45.806782',
                                '2013-12-29 21:16:56.144887',
                                '2013-12-29 21:17:03.192653',
                                '2013-12-29 21:17:11.141901',
                                '2014-01-24 23:32:17.118887',
                                '2014-01-24 23:32:23.263044',
                                '2014-02-13 20:45:46.761445',
                                '2014-02-17 01:45:13.412419',
                                '2014-02-19 20:47:20.599505',
                                '2014-03-20 01:15:26.017334']},
           {'name': 109L,
            'tag': 120L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 11, 43),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 7, 19, 29, 37),
            'step': None,
            'in_path': None,
            'id': 383415L,
            'secondary_right': ['2013-10-04 19:50:29.608630',
                                '2013-10-07 03:11:12.707955',
                                '2013-10-18 17:39:46.227522',
                                '2013-11-21 22:29:04.960673',
                                '2013-11-30 02:58:13.544984',
                                '2013-12-03 21:54:52.981560',
                                '2014-01-20 14:29:24.439739']},
           {'name': 109L,
            'tag': 121L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'in_path': None,
            'id': 383616L,
            'secondary_right': None},
           {'name': 109L,
            'tag': 122L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 7, 46),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 17, 22, 29, 3),
            'step': None,
            'in_path': None,
            'id': 383636L,
            'secondary_right': ['2013-11-04 13:40:30.224814',
                                '2013-11-06 16:16:51.210929',
                                '2014-02-03 15:11:04.685410']},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 47, 9),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'step': None,
            'tag': 124L,
            'in_path': None,
            'id': 383977L,
            'secondary_right': None},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 17, 29),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'tag': 128L,
            'in_path': None,
            'id': 383639L,
            'secondary_right': None},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 22, 21, 33),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'tag': 129L,
            'in_path': None,
            'id': 383852L,
            'secondary_right': ['2014-03-20 01:13:10.828327']},
            {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'step': None,
            'tag': 133L,
            'in_path': None,
            'id': 384071L,
            'secondary_right': None}
           ]
          }

    return tr


@pytest.fixture
def mytagrecs_with_secondary():
    """A fixture providing mock tag_records data."""
    tr = {'Simon Pan 2014-03-21':
          [{'id': 383380L,
            'tag': 1L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:13:59.395609',
                                '2014-03-20 00:45:07.189652',
                                '2014-03-20 01:13:10.767671',
                                '2014-03-20 01:20:07.238262',
                                '2014-03-20 01:21:42.738633'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 15, 32, 1)
            },
           {'id': 383615L, 'in_path': None,
            'tag': 4L,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:21:48.396981',
                                '2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-20 00:46:03.191941',
                                '2014-03-20 01:19:00.049401'],
            'step': None,
            'tag': 2L,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383419L,
            'tag': 5L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 23, 45, 25)},
           {'id': 383219L,
            'tag': 6L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-05 04:23:40.815243',
                                '2014-03-05 04:24:02.586695',
                                '2014-03-05 04:24:12.043533',
                                '2014-03-05 22:27:29.538283',
                                '2014-03-20 01:20:07.234653'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 9, 27, 14, 8, 27),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 383119L,
            'tag': 9L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:13:10.771437',
                                '2014-03-20 01:18:26.331487',
                                '2014-03-20 01:20:07.245236',
                                '2014-03-20 01:27:31.974083'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383613L,
            'tag': 10L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-10-07 22:48:58.563124'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383969L,
            'tag': 14L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 93.0,
            'times_wrong': 18.0,
            'tlast_right': datetime.datetime(2014, 3, 17, 22, 29, 3),
            'tlast_wrong': datetime.datetime(2014, 1, 21, 18, 21, 40)},
           {'id': 383116L,
            'tag': 16L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-18 19:17:02.407886',
                                '2014-02-18 19:17:25.063330',
                                '2014-02-19 20:36:42.985334',
                                '2014-02-19 20:37:08.797027',
                                '2014-02-20 22:59:13.563362',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847',
                                '2014-02-28 17:39:34.566118',
                                '2014-02-28 17:39:49.479375'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 384068L,
            'tag': 17L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10)},
           {'id': 383858L,
            'tag': 18L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 95.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 1, 24, 23, 32, 23),
            'tlast_wrong': datetime.datetime(2013, 10, 23, 18, 0, 5)},
           {'id': 383978L,
            'tag': 24L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 19),
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 50, 54)},
           {'id': 383546L,
            'tag': 29L,
            'in_path': None,
            'name': 109L,
            'secondary_right': [],
            'step': None,
            'times_right': 29.0,
            'times_wrong': 10.0,
            'tlast_right': datetime.datetime(2014, 2, 11, 2, 53, 27),
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 37, 10)},
           {'id': 383614L,
            'tag': 30L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-04 15:02:12.448057',
                                '2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383478L,
            'tag': 32L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-11-17 22:23:35.574534',
                                '2013-12-03 21:52:42.483799',
                                '2014-01-31 22:25:20.777146'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 10, 2, 20, 38, 45),
            'tlast_wrong': datetime.datetime(2013, 10, 2, 20, 38, 45)},
           {'id': 384067L,
            'tag': 35L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-13 20:02:54.213157',
                                '2014-03-13 20:03:06.719722'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 2, 52),
            'tlast_wrong': datetime.datetime(2014, 3, 13, 20, 2, 52)},
           {'id': 383232L,
            'tag': 36L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-13 20:03:06.719722',
                                '2014-03-14 20:31:20.800429',
                                '2014-03-17 22:13:59.395609',
                                '2014-03-20 00:45:07.175987',
                                '2014-03-20 01:13:10.776062'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 39, 59)},
           {'id': 383916L,
            'tag': 38L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 16, 32),
            'tlast_wrong': datetime.datetime(2013, 11, 20, 0, 24, 20)},
           {'id': 383979L,
            'tag': 40L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 19),
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 50, 54)},
           {'id': 383980L,
            'tag': 43L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 19),
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 50, 54)},
           {'id': 383420L,
            'tag': 46L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-10-03 21:38:26.430271',
                                '2013-10-03 21:38:38.754177',
                                '2013-10-04 19:48:45.218412',
                                '2013-10-08 18:14:36.129966',
                                '2013-10-09 19:45:40.089605',
                                '2013-10-09 19:46:49.950370',
                                '2013-10-09 19:47:14.835834',
                                '2013-10-25 02:05:14.367961',
                                '2013-10-25 02:06:05.067229',
                                '2013-11-16 02:22:43.965206',
                                '2013-11-16 02:23:26.988475',
                                '2014-02-12 21:18:52.149758',
                                '2014-02-15 03:04:08.599316',
                                '2014-02-17 01:01:49.514350',
                                '2014-02-18 01:32:22.890120'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 23, 45, 25)},
           {'id': 383421L,
            'tag': 47L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 18, 1, 32, 22),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 23, 45, 25)},
           {'id': 383222L,
            'tag': 48L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-01-13 15:17:38.961998',
                                '2014-01-13 23:00:05.839312',
                                '2014-01-20 14:23:30.474737',
                                '2014-01-20 14:35:17.591339',
                                '2014-01-23 19:27:48.728760',
                                '2014-01-28 02:43:01.370294',
                                '2014-01-31 03:07:18.935169',
                                '2014-01-31 03:16:13.717293',
                                '2014-01-31 03:16:25.387423',
                                '2014-02-04 15:02:12.448057',
                                '2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-20 01:13:10.779684'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 11, 17),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 18, 2)},
           {'id': 383890L,
            'tag': 49L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 7, 19, 22, 42),
            'tlast_wrong': datetime.datetime(2013, 11, 2, 2, 13, 11)},
           {'id': 383111L,
            'tag': 61L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:26:42.183147'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 48, 55)},
           {'id': 383217L,
            'tag': 62L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:25:44.135166',
                                '2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:41:36.531712',
                                '2014-03-20 00:45:07.166820',
                                '2014-03-20 00:46:03.188713',
                                '2014-03-20 00:46:37.676085',
                                '2014-03-20 01:13:10.787178',
                                '2014-03-20 01:15:26.006571',
                                '2014-03-20 01:19:00.046118',
                                '2014-03-20 01:20:07.216789',
                                '2014-03-20 01:26:21.066885'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 26, 42),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 13, 58, 40)},
           {'id': 383109L,
            'tag': 63L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:26:16.421367',
                                '2014-03-17 22:26:34.296588',
                                '2014-03-17 22:27:30.389687',
                                '2014-03-17 22:28:09.597927',
                                '2014-03-17 22:28:33.835836',
                                '2014-03-17 22:28:55.131425',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-20 00:41:36.521707',
                                '2014-03-20 00:45:07.170990',
                                '2014-03-20 00:46:03.181437',
                                '2014-03-20 00:46:37.665167',
                                '2014-03-20 01:13:10.790596',
                                '2014-03-20 01:15:25.995401',
                                '2014-03-20 01:19:00.038560',
                                '2014-03-20 01:20:07.205652'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 26, 21),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 45, 36)},
           {'id': 383234L,
            'tag': 66L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:28:33.835836',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:45:07.181056',
                                '2014-03-20 00:46:37.672462',
                                '2014-03-20 01:13:10.794228',
                                '2014-03-20 01:15:26.002995',
                                '2014-03-20 01:20:07.213051'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 43, 27)},
           {'id': 383117L,
            'tag': 67L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:20:07.241677',
                                '2014-03-20 01:21:42.742329',
                                '2014-03-20 01:22:46.003765',
                                '2014-03-20 01:27:31.971359'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383108L,
            'tag': 68L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-12 20:52:04.164228',
                                '2014-03-13 19:51:41.766472',
                                '2014-03-14 20:31:38.950469',
                                '2014-03-20 00:41:36.541744'],
            'step': None,
            'times_right': 77.0,
            'times_wrong': 30.0,
            'tlast_right': datetime.datetime(2014, 3, 5, 22, 39, 53),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 45, 15)},
           {'id': 383543L,
            'tag': 69L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:25:44.135166',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 01:13:10.801349'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 19, 34)},
           {'id': 384040L,
            'tag': 71L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 16, 1),
            'tlast_wrong': datetime.datetime(2014, 2, 12, 4, 3, 50)},
           {'id': 383112L,
            'tag': 72L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 02:21:46.197632',
                                '2014-02-22 02:43:30.852941',
                                '2014-02-27 22:43:40.639117',
                                '2014-03-05 22:25:54.594000',
                                '2014-03-05 22:26:05.479588',
                                '2014-03-07 19:29:25.549794',
                                '2014-03-07 19:29:37.973997',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-20 01:11:17.566601',
                                '2014-03-20 01:13:10.804879'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 28, 36),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 53, 45)},
           {'id': 383114L,
            'tag': 73L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-19 20:36:42.985334',
                                '2014-02-19 20:37:08.797027',
                                '2014-02-20 22:59:13.563362',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383414L,
            'tag': 74L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:20:07.223668',
                                '2014-03-20 01:22:45.994129'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 17, 32),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 10, 31)},
           {'id': 383411L,
            'tag': 75L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2013-12-03 21:54:52.981560',
                                '2014-01-20 14:29:24.439739',
                                '2014-02-25 01:05:57.858092',
                                '2014-02-25 01:07:59.061393',
                                '2014-02-25 01:09:09.356279',
                                '2014-02-25 01:10:20.265528',
                                '2014-02-25 01:11:45.086382',
                                '2014-03-20 01:20:07.227347'],
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 3, 6),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41)},
           {'id': 383347L,
            'tag': 76L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:13:10.808508'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 22, 45),
            'tlast_wrong': datetime.datetime(2013, 9, 30, 13, 52, 55)},
           {'id': 383115L,
            'tag': 77L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-25 01:11:45.086382',
                                '2014-02-25 01:13:14.462175',
                                '2014-02-25 01:13:42.069870',
                                '2014-02-25 01:41:04.161803',
                                '2014-02-25 01:43:42.693616',
                                '2014-02-26 19:11:09.105744',
                                '2014-02-26 19:11:25.514290',
                                '2014-03-05 04:23:40.815243',
                                '2014-03-05 04:24:02.586695',
                                '2014-03-05 04:24:12.043533',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832',
                                '2014-03-20 01:13:10.812152',
                                '2014-03-20 01:20:07.231051',
                                '2014-03-20 01:21:42.745721',
                                '2014-03-20 01:22:45.999836'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383220L,
            'tag': 82L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:25:44.135166',
                                '2014-03-17 22:26:47.680713',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 00:41:36.536662',
                                '2014-03-20 01:13:10.815555'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 383221L,
            'tag': 83L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 02:41:48.717205',
                                '2014-02-22 02:48:06.942953',
                                '2014-02-22 02:48:31.979752',
                                '2014-02-22 02:49:45.161565',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847',
                                '2014-02-25 01:17:35.500535',
                                '2014-02-25 21:50:44.559794',
                                '2014-02-25 21:51:13.463541',
                                '2014-02-27 22:43:40.639117',
                                '2014-02-28 17:54:08.870595',
                                '2014-02-28 17:56:42.590879',
                                '2014-02-28 17:58:57.035455',
                                '2014-03-05 04:23:40.815243',
                                '2014-03-05 04:24:02.586695',
                                '2014-03-05 04:24:12.043533',
                                '2014-03-20 01:13:10.818786',
                                '2014-03-20 01:15:26.009951'],
            'step': None,
            'times_right': None,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 9, 27, 14, 8, 27),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 384069L,
            'tag': 84L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10)},
           {'id': 384070L,
            'tag': 85L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10)},
           {'id': 383612L,
            'tag': 86L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:26:47.680713',
                                '2014-03-17 22:28:26.372733',
                                '2014-03-17 22:28:33.835836',
                                '2014-03-17 22:29:25.135365',
                                '2014-03-17 22:29:32.526147',
                                '2014-03-20 01:13:10.821758'],
            'step': None,
            'times_right': 0.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383637L,
            'tag': 87L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-04 15:02:12.448057',
                                '2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 12, 17)},
           {'id': 383118L,
            'tag': 88L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 02:21:24.974752',
                                '2014-02-22 02:21:46.197632',
                                '2014-02-22 02:43:30.852941',
                                '2014-02-25 01:41:04.161803',
                                '2014-02-25 01:43:42.693616',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832',
                                '2014-03-13 19:52:16.747902',
                                '2014-03-20 01:13:10.824876',
                                '2014-03-20 01:15:26.013721'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383233L,
            'tag': 89L,
            'in_path': None,
            'name': 109L,
            'secondary_right': None,
            'step': None,
            'times_right': 1000.0,
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 13, 22, 36, 47),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 41, 6)},
           {'id': 383113L,
            'tag': 90L,
            'times_right': 1.0,
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'step': None,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-14 22:33:12.662352',
                                '2014-02-22 02:14:57.149550',
                                '2014-03-20 01:20:07.220079']},
           {'name': 109L,
            'tag': 91L,
            'times_right': 1.0,
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 5, 35),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 18, 26),
            'step': None,
            'in_path': None,
            'id': 383218L,
            'secondary_right': ['2014-02-20 22:59:13.563362',
                                '2014-02-20 23:00:34.203297',
                                '2014-02-20 23:00:49.080672',
                                '2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847',
                                '2014-02-25 01:05:57.858092',
                                '2014-02-25 01:07:59.061393',
                                '2014-02-25 01:09:09.356279',
                                '2014-02-25 01:10:20.265528',
                                '2014-02-25 01:11:45.086382',
                                '2014-02-28 17:39:34.566118',
                                '2014-02-28 17:39:49.479375',
                                '2014-03-13 19:52:16.747902']},
           {'name': 109L,
            'tag': 92L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 50, 13),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 5, 4, 24, 12),
            'step': None,
            'in_path': None,
            'id': 383237L,
            'secondary_right': ['2014-02-14 22:33:12.662352',
                                '2014-02-22 02:14:57.149550',
                                '2014-03-10 19:14:52.759060',
                                '2014-03-10 19:14:58.914173']},
           {'name': 109L,
            'tag': 93L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 9, 30, 13, 39, 50),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 24, 41),
            'step': None,
            'in_path': None,
            'id': 383346L,
            'secondary_right': ['2014-02-24 00:54:44.343751',
                                '2014-02-24 00:56:13.859405',
                                '2014-02-25 01:13:14.462175',
                                '2014-02-25 01:13:42.069870',
                                '2014-03-06 23:04:06.151430',
                                '2014-03-06 23:04:35.494832']},
           {'name': 109L,
            'tag': 94L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 41, 56),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 0, 41, 36),
            'step': None,
            'in_path': None,
            'id': 383976L,
            'secondary_right': None},
           {'name': 109L,
            'tag': 95L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 34, 49),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'step': None,
            'in_path': None,
            'id': 383545L,
            'secondary_right': ['2013-10-03 21:38:26.430271',
                                '2013-10-03 21:38:38.754177',
                                '2013-10-04 02:49:27.280458',
                                '2013-10-04 19:50:29.608630',
                                '2013-10-07 03:11:12.707955',
                                '2013-10-08 18:14:36.129966',
                                '2013-10-18 17:39:46.227522',
                                '2013-11-16 02:22:43.965206',
                                '2013-11-16 02:23:26.988475',
                                '2013-11-21 22:29:04.960673',
                                '2013-11-30 02:58:13.544984',
                                '2013-12-03 21:54:52.981560',
                                '2014-01-20 14:29:24.439739']},
           {'name': 109L,
            'tag': 115L,
            'times_right': 1.0,
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'step': None,
            'in_path': None,
            'id': 383120L,
            'secondary_right': ['2014-02-18 19:43:17.771731',
                                '2014-02-25 01:05:57.858092',
                                '2014-02-25 01:07:59.061393',
                                '2014-02-25 01:09:09.356279',
                                '2014-02-25 01:10:20.265528',
                                '2014-02-25 01:11:45.086382',
                                '2014-02-25 01:41:04.161803',
                                '2014-02-25 01:43:42.693616',
                                '2014-02-27 22:43:40.639117',
                                '2014-03-03 01:04:00.557721',
                                '2014-03-03 01:04:17.237054',
                                '2014-03-05 22:25:54.594000',
                                '2014-03-05 22:26:05.479588',
                                '2014-03-07 19:29:25.549794',
                                '2014-03-07 19:29:37.973997',
                                '2014-03-07 19:31:03.859650',
                                '2014-03-10 18:58:12.704988',
                                '2014-03-10 18:58:17.102850',
                                '2014-03-20 01:20:07.248791']},
           {'name': 109L,
            'tag': 116L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 10, 18, 58, 17),
            'step': None,
            'in_path': None,
            'id': 383412L,
            'secondary_right': ['2014-02-10 02:31:21.978049',
                                '2014-02-12 03:55:11.346488',
                                '2014-02-12 03:55:49.469451']},
           {'name': 109L,
            'tag': 117L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'in_path': None,
            'id': 383413L,
            'secondary_right': ['2014-03-06 22:58:36.468321',
                                '2014-03-07 19:13:40.727329',
                                '2014-03-10 18:56:02.777857',
                                '2014-03-11 18:15:09.996416',
                                '2014-03-12 20:53:03.514677',
                                '2014-03-13 19:50:36.891023',
                                '2014-03-13 19:51:27.333192',
                                '2014-03-14 20:31:20.800429',
                                '2014-03-17 22:13:59.395609',
                                '2014-03-20 00:45:07.186095']},
           {'name': 109L,
            'tag': 118L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 19, 34),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'step': None,
            'in_path': None,
            'id': 383544L,
            'secondary_right': ['2013-10-09 19:46:49.950370',
                                '2013-10-09 19:47:14.835834',
                                '2014-02-12 21:18:52.149758',
                                '2014-02-15 03:04:08.599316',
                                '2014-02-17 01:01:49.514350',
                                '2014-02-18 01:32:22.890120']},
           {'name': 109L,
            'tag': 119L,
            'times_right': 1001.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 13),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 25, 21, 51, 13),
            'step': None,
            'in_path': None,
            'id': 383541L,
            'secondary_right': ['2014-02-19 20:47:20.599505',
                                '2014-03-20 01:15:26.017334']},
           {'name': 109L,
            'tag': 120L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 11, 43),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 7, 19, 29, 37),
            'step': None,
            'in_path': None,
            'id': 383415L,
            'secondary_right': ['2013-10-04 19:50:29.608630',
                                '2013-10-07 03:11:12.707955',
                                '2013-10-18 17:39:46.227522',
                                '2013-11-21 22:29:04.960673',
                                '2013-11-30 02:58:13.544984',
                                '2013-12-03 21:54:52.981560',
                                '2014-01-20 14:29:24.439739']},
           {'name': 109L,
            'tag': 121L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'in_path': None,
            'id': 383616L,
            'secondary_right': None},
           {'name': 109L,
            'tag': 122L,
            'times_right': 1000.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 7, 46),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 17, 22, 29, 3),
            'step': None,
            'in_path': None,
            'id': 383636L,
            'secondary_right': ['2013-11-04 13:40:30.224814',
                                '2013-11-06 16:16:51.210929',
                                '2014-02-03 15:11:04.685410']},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2014, 2, 11, 2, 47, 9),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'step': None,
            'tag': 124L,
            'in_path': None,
            'id': 383977L,
            'secondary_right': None},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 17, 29),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'tag': 128L,
            'in_path': None,
            'id': 383639L,
            'secondary_right': None},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2013, 10, 22, 21, 33),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'tag': 129L,
            'in_path': None,
            'id': 383852L,
            'secondary_right': ['2014-03-20 01:13:10.828327']},
           {'name': 109L,
            'times_right': 0.0,
            'tlast_wrong': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 13, 10),
            'step': None,
            'tag': 133L,
            'in_path': None,
            'id': 384071L,
            'secondary_right': None}
           ]
          }

    return tr


@pytest.fixture
def bg_imgs(db):
    """
    Pytest fixture to provide background image info for each test location.
    """
    locs = {3: 8,
            1: 8,
            2: 8,
            6: 16,
            7: 18,
            8: 16,
            11: 15,
            13: 17}
    imgs = {l: '/paideia/static/images/{}'.format(db.images[i].image)
            for l, i in locs.iteritems()}
    return imgs


# Constant values from
@pytest.fixture
def npc_imgs(db):
    """
    Pytest fixture to provide image info for each test npc.
    """
    images = {'npc1_img': '/paideia/static/images/{}'.format(db.images[1].image),
              'npc2_img': '/paideia/static/images/{}'.format(db.images[4].image),
              'npc8_img': '/paideia/static/images/{}'.format(db.images[5].image),
              'npc14_img': '/paideia/static/images/{}'.format(db.images[2].image),
              'npc17_img': '/paideia/static/images/{}'.format(db.images[7].image),
              'npc21_img': '/paideia/static/images/{}'.format(db.images[7].image),
              'npc31_img': '/paideia/static/images/{}'.format(db.images[3].image),
              'npc32_img': '/paideia/static/images/{}'.format(db.images[10].image),
              'npc40_img': '/paideia/static/images/{}'.format(db.images[6].image),
              'npc41_img': '/paideia/static/images/{}'.format(db.images[11].image),
              'npc42_img': '/paideia/static/images/{}'.format(db.images[9].image)
              }
    return images


@pytest.fixture
def npc_data(npc_imgs):
    """
    Pytest fixture to provide npc data for tests.
    """
    npcs = {1: {'image': npc_imgs['npc1_img'],
                'name': 'Ἀλεξανδρος',
                'location': [6, 8]},
            2: {'image': npc_imgs['npc2_img'],
                'name': 'Μαρια',
                'location': [3, 1, 2, 4]},
            8: {'image': npc_imgs['npc8_img'],
                'name': 'Διοδωρος',
                'location': [1]},
            14: {'image': npc_imgs['npc14_img'],
                 'name': 'Γεωργιος',
                 'location': [3, 1, 2, 4, 7, 8, 9, 10]},
            17: {'image': npc_imgs['npc17_img'],
                 'name': 'Ἰασων',
                 'location': [3, 1, 2, 4, 7, 8]},
            21: {'image': npc_imgs['npc21_img'],
                 'name': 'Νηρευς',
                 'location': [7, 8]},
            31: {'image': npc_imgs['npc31_img'],
                 'name': 'Σοφια',
                 'location': [3, 1, 2, 4, 11]},
            32: {'image': npc_imgs['npc32_img'],
                 'name': 'Στεφανος',
                 'location': [11]},
            40: {'image': npc_imgs['npc40_img'],
                 'name': 'Σίμων',
                 'location': [3, 1, 2, 4, 7, 8]},
            41: {'image': npc_imgs['npc41_img'],
                 'name': 'Φοιβη',
                 'location': [3, 1, 4, 8]},
            42: {'image': npc_imgs['npc42_img'],
                 'name': 'Ὑπατια',
                 'location': [3, 1, 2, 4, 12, 8]}
            }
    return npcs


@pytest.fixture(params=[n for n in [1, 2, 3, 4]])
def myblocks(request):
    """ """
    casenum = request.param
    block_args = {1: {'condition': 'redirect',
                      'kwargs': None, 'data': None},
                  2: {'condition': 'award badges',
                      'kwargs': None, 'data': None},
                  3: {'condition': 'view slides',
                      'kwargs': None, 'data': None},
                  4: {'condition': 'quota reached',
                      'kwargs': None, 'data': None},
                  }
    return block_args[casenum]


@pytest.fixture()
def mysteps():
    """
        Test fixture providing step information for unit tests.
        This fixture is parameterized, so that tests can be run with each of the
        steps or with any sub-section (defined by a filtering expression in the
        test). This step fixture is also used in the mycases fixture.
    """
    responders = {'text': '<form action="#" autocomplete="off" '
                          'enctype="multipart/form-data" method="post">'
                          '<table>'
                          '<tr id="no_table_response__row">'
                          '<td class="w2p_fl">'
                          '<label for="no_table_response" id="no_table_response__label">'
                          'Response: </label>'
                          '</td>'
                          '<td class="w2p_fw">'
                          '<input class="string" id="no_table_response" name="response" '
                          'type="text" value="" />'
                          '</td>'
                          '<td class="w2p_fc"></td>'
                          '</tr>'
                          '<tr id="submit_record__row">'
                          '<td class="w2p_fl"></td>'
                          '<td class="w2p_fw">'
                          '<input type="submit" value="Submit" />'
                          '</td>'
                          '<td class="w2p_fc"></td>'
                          '</tr>'
                          '</table>'
                          '</form>',
                  'multi': '<form action="#" autocomplete="off" '
                           'enctype="multipart/form-data" method="post">'
                           '<table>'
                           '<tr id="no_table_response__row">'
                           '<td class="w2p_fl">'
                           '<label for="no_table_response" id="no_table_response__label">'
                           'Response: </label>'
                           '</td>'
                           '<td class="w2p_fw">'
                           '<input class="string" id="no_table_response" name="response" '
                           'type="text" value="" />'
                           '</td>'
                           '<td class="w2p_fc"></td>'
                           '</tr>'
                           '<tr id="submit_record__row">'
                           '<td class="w2p_fl"></td>'
                           '<td class="w2p_fw">'
                           '<input type="submit" value="Submit" />'
                           '</td>'
                           '<td class="w2p_fc"></td>'
                           '</tr>'
                           '</table>'
                           '</form>',
                  'stub': '<div>'
                          '<a class="back_to_map" data-w2p_disable_with="default" '
                          'data-w2p_method="GET" data-w2p_target="page" '
                          'href="/paideia/default/walk">Map</a>'
                          '</div>',
                  'continue': '<div><a class="back_to_map" '
                              'data-w2p_disable_with="default" '
                              'data-w2p_method="GET" data-w2p_target="page" '
                              'href="/paideia/default/walk">Map</a>'
                              '<a class="continue" data-w2p_disable_with="default" '
                              'data-w2p_method="GET" data-w2p_target="page" '
                              'href="/paideia/default/walk/ask?loc=[[loc]]">'
                              'Continue</a></div>'}
    prompts = {'redirect': 'Hi there. Sorry, I don\'t have anything for you to '
                           'do here at the moment. I think someone was looking '
                           'for you at somewhere else in town.',
               'new_badges': {3: '<div>Congratulations, Homer! \n\n'
                                 'You have been promoted to these new badge levels:\r\n'
                                 '- apprentice alphabet basics\r\n'
                                 '- apprentice alphabet (diphthongs and capitals)\r\n'
                                 'You can click on your name above to see details '
                                 'of your progress so far.</div>',
                              2: '<div>Congratulations, Homer! \n\n'
                                 'You have been promoted to these new badge levels:\r\n'
                                 '- apprentice alphabet basics\r\n'
                                 'and you&#x27;re ready to start working on some new badges:\r\n'
                                 '- beginner alphabet (intermediate)\r\n'
                                 'You can click on your name above to see details '
                                 'of your progress so far.</div>'},
               'quota': 'Well done, [[user]]. You\'ve finished '
                        'enough paths for today. But if you would '
                        'like to keep going, you\'re welcome to '
                        'continue.',
               # numbers indicate prompts for corresponding cases
               'slides': {2: '<div>Take some time now to review these new slide '
                             'sets. They will help with work on your new badges:\n'
                             '<ul class="slide_list">'
                             '<li><a data-w2p_disable_with="default" href="/paideia/'
                             'listing/slides.html/3">The Alphabet II</a></li>'
                             '<li><a data-w2p_disable_with="default" href="/paideia/'
                             'listing/slides.html/8">Greek Words II</a></li></ul>'
                             '</div>',
                          3: '<div>Take some time now to review these new slide '
                             'sets. They will help with work on your new badges:\n'
                             '<ul class="slide_list">'
                             '<li><a data-w2p_disable_with="default" href="/paideia/'
                             'listing/slides.html/3">The Alphabet II</a></li>'
                             '<li><a data-w2p_disable_with="default" href="/paideia/'
                             'listing/slides.html/8">Greek Words II</a></li></ul>'
                             '</div>'}
               }

    steps = {1: {'id': 1,
                 'paths': [2],
                 'step_type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1, 17],
                 'locations': [3, 1, 13, 7, 8, 11],
                 'raw_prompt': 'How could you write the word "meet" '
                               'using Greek letters?',
                 'final_prompt': 'How could you write the word "meet" '
                                 'using Greek letters?',
                 'redirect_prompt': prompts['redirect'],
                 'instructions': ['Focus on finding Greek letters that make '
                                  'the *sounds* of the English word. Don\'t '
                                  'look for Greek "equivalents" for each '
                                  'English letter.'],
                 'tips': None,
                 'slidedecks': {1: 'Introduction',
                                2: 'The Alphabet',
                                6: 'Noun Basics',
                                7: 'Greek Words I'},
                 'tags': [61],
                 'tags_secondary': [],
                 'responder': responders['text'],
                 'redirect_responder': responders['stub'],
                 'responses': {'response1': '^μιτ$'},
                 'readable': {'readable_short': ['μιτ'],
                              'readable_long': []},
                 'reply_text': {'correct': 'Right. Κάλον.\nYou said\n- [[resp]]',
                                'incorrect': 'Incorrect. Try again!\nYou '
                                             'said\n- [[resp]]\nThe correct '
                                             'response is[[rdbl]]'},
                 'user_responses': {'correct': 'μιτ',
                                    'incorrect': 'βλα'},
                 'widget_image': None
                 },
             2: {'id': 2,
                 'paths': [3],
                 'step_type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1],
                 'locations': [3, 1, 13, 7, 8, 11],
                 'raw_prompt': 'How could you write the word "bought" '
                               'using Greek letters?',
                 'final_prompt': 'How could you write the word "bought" '
                                 'using Greek letters?',
                 'redirect_prompt': prompts['redirect'],
                 'instructions': None,
                 'slidedecks': {1: 'Introduction',
                                2: 'The Alphabet',
                                6: 'Noun Basics',
                                7: 'Greek Words I'},
                 'tags': [61],
                 'tags_secondary': [],
                 'responder': responders['text'],
                 'redirect_responder': responders['stub'],
                 'responses': {'response1': '^β(α|ο)τ$'},
                 'readable': {'readable_short': ['βατ', 'βοτ'],
                              'readable_long': []},
                 'reply_text': {'correct': 'Right. Κάλον.\nYou said\n- '
                                           '[[resp]]\nCorrect responses '
                                           'would include[[rdbl]]',
                                'incorrect': 'Incorrect. Try again!\nYou '
                                             'said\n- [[resp]]\nCorrect responses '
                                             'would include[[rdbl]]'},
                 'tips': None,  # why is this None, but elsewhere it's []?
                 'user_responses': {'correct': 'βοτ',
                                    'incorrect': 'βλα'},
                 'widget_image': None
                 },
             19: {'id': 19,
                 'paths': [19],
                 'step_type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1],
                 'locations': [3, 1, 13, 8, 11],
                 'raw_prompt': 'How could you spell the word "pole" with '
                               'Greek letters?',
                 'final_prompt': 'How could you spell the word "pole" with '
                                 'Greek letters?',
                 'redirect_prompt': prompts['redirect'],
                 'instructions': ['Focus on finding Greek letters that make '
                                  'the *sounds* of the English word. Don\'t '
                                  'look for Greek "equivalents" for each '
                                  'English letter.'],
                 'slidedecks': None,
                 'tags': [62],
                 'tags_secondary': [61],
                 'responses': {'response1': '^πωλ$'},
                 'responder': responders['text'],
                 'redirect_responder': responders['stub'],
                 'readable': {'readable_short': ['πωλ'],
                              'readable_long': []},
                 'reply_text': {'correct': 'Right. Κάλον.\nYou said\n- [[resp]]\n',
                                'incorrect': 'Incorrect. Try again!\nYou '
                                             'said\n- [[resp]]\nThe correct '
                                             'response is[[rdbl]]'},
                 'tips': [],
                 'user_responses': {'correct': 'πωλ',
                                    'incorrect': 'βλα'},
                 'widget_image': None
                  },
             30: {'id': 30,
                  'paths': [None],
                  'step_type': StepRedirect,
                  'widget_type': 9,
                  'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                  'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                  'raw_prompt': prompts['redirect'],
                  'final_prompt': prompts['redirect'],
                  'redirect_prompt': prompts['redirect'],
                  'instructions': None,
                  'slidedecks': None,
                  'tags': [70],
                  'tags_secondary': [],
                  'redirect_responder': responders['stub'],
                  'responder': responders['stub'],
                  'widget_image': None
                  },
             101: {'id': 101,
                   'paths': [89],
                   'step_type': StepMultiple,
                   'widget_type': 4,
                   'locations': [7],
                   'npc_list': [14],
                   'raw_prompt': 'Is this an English clause?\r\n\r\n"The '
                                 'cat sat."',
                   'final_prompt': 'Is this an English clause?\r\n\r\n"The '
                                   'cat sat."',
                   'redirect_prompt': prompts['redirect'],
                   'instructions': None,
                   'slidedecks': {14: 'Clause Basics'},
                   'tags': [36],
                   'tags_secondary': [],
                   'step_options': ['ναι', 'οὐ'],
                   'responses': {'response1': 'ναι'},
                   'responder': responders['multi'],
                   'redirect_responder': responders['stub'],
                   'readable': {'readable_short': ['ναι'],
                                'readable_long': []},
                   'user_responses': {'correct': 'ναι',
                                      'incorrect': 'οὐ'},
                   'reply_text': {'correct': 'Right. Κάλον.\nYou said\n- [[resp]]',
                                  'incorrect': 'Incorrect. Try again!\nYou '
                                               'said\n- [[resp]]\nThe correct '
                                               'response is[[rdbl]]'},
                   'tips': None,
                   'widget_image': None
                   },
             125: {'id': 125,
                   'paths': [None],
                   'step_type': StepQuotaReached,
                   'widget_type': 7,
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'raw_prompt': prompts['quota'],
                   'final_prompt': prompts['quota'].replace('[[user]]', 'Homer'),
                   'instructions': None,
                   'slidedecks': None,
                   'tags': [79],
                   'tags_secondary': [],
                   'responder': responders['continue'],
                   'widget_image': None
                   },
             126: {'id': 126,
                   'paths': [None],
                   'step_type': StepAwardBadges,
                   'widget_type': 8,
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'raw_prompt': prompts['new_badges'],
                   'final_prompt': prompts['new_badges'],
                   'instructions': None,
                   'slidedecks': None,
                   'tags': [81],
                   'tags_secondary': [],
                   'responder': responders['continue'],
                   'widget_image': None
                   },
             127: {'id': 127,
                   'paths': [None],
                   'step_type': StepViewSlides,
                   'widget_type': 6,
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'raw_prompt': prompts['slides'],
                   'final_prompt': prompts['slides'],
                   'instructions': None,
                   'slidedecks': None,
                   'tags': [],
                   'tags_secondary': [],
                   'responder': responders['stub'],
                   'widget_image': None
                   }
             }
    return steps


def mycases(casenum, user_login, db):
    """
        Text fixture providing various cases for unit tests. For each step,
        several cases are specified.
    """
    allpaths = db().select(db.paths.ALL)

    # same npc and location as previous step
    # replace tag too far ahead (1) with appropriate (61)
    cases = {'case1': {'casenum': 1,
                       'loc': Location('shop_of_alexander', db),  # loc 6
                       'mynow': dt('2013-01-29'),
                       'name': user_login['first_name'],
                       'uid': user_login['id'],
                       'prev_loc': Location('ne_stoa', db),
                       'next_loc': None,
                       'prev_npc': Npc(2, db),
                       'npcs_here': [2, 8, 14, 17, 31, 40, 41, 42],
                       'pathid': 3,
                       'blocks_in': None,
                       'blocks_out': None,
                       'localias': 'shop_of_alexander',
                       'tag_records': [{'name': 1,
                                        'tag': 1,
                                        'tlast_right': dt('2013-01-29'),
                                        'tlast_wrong': dt('2013-01-29'),
                                        'times_right': 1,
                                        'times_wrong': 1,
                                        'secondary_right': None}],
                       'core_out': {'cat1': [1], 'cat2': [],
                                    'cat3': [], 'cat4': []},
                       'untried_out': {'cat1': [1, 61], 'cat2': [],
                                       'cat3': [], 'cat4': []},
                       'introduced': [62],
                       'tag_progress': {'latest_new': 1,
                                        'cat1': [1], 'cat2': [],
                                        'cat3': [], 'cat4': [],
                                        'rev1': [], 'rev2': [],
                                        'rev3': [], 'rev4': []},
                       'tag_progress_out': {'latest_new': 1,
                                            'cat1': [61], 'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_start': {'cat1': [61], 'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_out': {'cat1': [61], 'cat2': [],
                                          'cat3': [], 'cat4': [],
                                          'rev1': [], 'rev2': [],
                                          'rev3': [], 'rev4': []},
                       'paths': {'cat1': [p.id for p in allpaths if 61 in p.tags],  # [1, 2, 3, 5, 8, 63, 95, 96, 99, 102, 256],  # removed 64, 70, 97, 104, 277
                                 'cat2': [],
                                 'cat3': [],
                                 'cat4': []},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': [],
                       'new_badges': None,
                       'promoted': {},
                       'demoted': {}},
             'case2':  # same location, last npc 2,
             # promote tag based on ratio and min time
             # both new tags and promoted
                      {'casenum': 2,
                       'mynow': dt('2013-01-29'),
                       'loc': Location('agora', db),  # loc 8
                       'name': user_login['first_name'],
                       'uid': user_login['id'],
                       'prev_loc': Location('agora', db),
                       'prev_npc': Npc(1, db),
                       'npcs_here': [1, 14, 17, 21, 40, 41, 42],
                       'pathid': 89,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag': 61,
                                        'tlast_right': dt('2013-01-29'),
                                        'tlast_wrong': dt('2013-01-28'),
                                        'times_right': 10,
                                        'times_wrong': 2,
                                        'secondary_right': []}],
                       'core_out': {'cat1': [], 'cat2': [61],
                                    'cat3': [], 'cat4': []},
                       'untried_out': {'cat1': [], 'cat2': [61],
                                       'cat3': [], 'cat4': []},
                       'tag_progress': {'latest_new': 1,
                                        'cat1': [61], 'cat2': [],
                                        'cat3': [], 'cat4': [],
                                        'rev1': [], 'rev2': [],
                                        'rev3': [], 'rev4': []},
                       'introduced': [62],
                       'tag_progress_out': {'latest_new': 2,
                                            'cat1': [62], 'cat2': [61],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_start': {'cat1': [61], 'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_out': {'cat1': [62], 'cat2': [61],
                                          'cat3': [], 'cat4': [],
                                          'rev1': [], 'rev2': [],
                                          'rev3': [], 'rev4': []},
                       'paths': {'cat1': [p.id for p in allpaths if 62 in p.tags],  # [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 34, 35, 97, 98, 100, 101, 257, 261],
                                 'cat2': [p.id for p in allpaths if 61 in p.tags],  # [1, 2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256],
                                 'cat3': [],
                                 'cat4': []},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': [],
                       'new_badges': [62],
                       'promoted': {'cat2': [61]},
                       'next_loc': None,
                       'demoted': {}},
             'case3':  # same location as previous step, last npc stephanos
             # promote tag based on time (without ratio)
             # add several untried tags for current rank
             # promoted but no new tags
                      {'casenum': 3,
                       'mynow': dt('2013-01-29'),
                       'name': user_login['first_name'],
                       'uid': user_login['id'],
                       'loc': Location('synagogue', db),  # loc 11
                       'prev_loc': Location('synagogue', db),
                       'prev_npc': Npc(31, db),  # stephanos
                       'npcs_here': [31, 32],
                       'pathid': 19,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag': 61,  # promote to 2 for time
                                        'tlast_right': dt('2013-01-27'),
                                        'tlast_wrong': dt('2013-01-21'),
                                        'times_right': 10,
                                        'times_wrong': 10,
                                        'secondary_right': None},
                                       # don't promote for time bc dw > dr
                                       {'name': 1,
                                        'tag': 62,
                                        'tlast_right': dt('2013-01-10'),
                                        'tlast_wrong': dt('2013-01-1'),
                                        'times_right': 10,
                                        'times_wrong': 0,
                                        'secondary_right': None},
                                       # don't promote for time bc t_r < 10
                                       {'name': 1,
                                        'tag': 63,
                                        'tlast_right': dt('2013-01-27'),
                                        'tlast_wrong': dt('2013-01-21'),
                                        'times_right': 9,
                                        'times_wrong': 0,
                                        'secondary_right': None},
                                       # promote for time bc t_r >= 10
                                       {'name': 1,
                                        'tag': 66,
                                        'tlast_right': dt('2013-01-27'),
                                        'tlast_wrong': dt('2013-01-21'),
                                        'times_right': 10,
                                        'times_wrong': 0,
                                        'secondary_right': None}
                                       ],
                       'core_out': {'cat1': [62, 63], 'cat2': [61, 66],
                                    'cat3': [], 'cat4': []},
                       'untried_out': {'cat1': [62, 63, 68, 115, 72, 89, 36],
                                       'cat2': [61, 66],
                                       'cat3': [], 'cat4': []},
                       'tag_progress': {'latest_new': 4,
                                        'cat1': [61, 62, 63, 66],
                                        'cat2': [],
                                        'cat3': [], 'cat4': [],
                                        'rev1': [], 'rev2': [],
                                        'rev3': [], 'rev4': []},
                       'introduced': [9, 16, 48, 76, 93],
                       'tag_progress_out': {'latest_new': 4,
                                            'cat1': [62, 63, 68, 115, 72, 89, 36],
                                            'cat2': [61, 66],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_start': {'cat1': [66, 68, 115, 72, 89, 36,
                                                     61, 62, 63],
                                            'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_out': {'cat1': [68, 115, 72, 89, 36, 62, 63],
                                          'cat2': [61, 66],
                                          'cat3': [], 'cat4': [],
                                          'rev1': [], 'rev2': [],
                                          'rev3': [], 'rev4': []},
                       'paths': {'cat1': [p.id for t in [68, 115, 72, 89, 36, 62, 63]
                                          for p in allpaths if t in p.tags],  # [4, 6, 7, 9, 10, 11, 12, 13, 14,
                                 'cat2': [p.id for t in [61, 66]
                                          for p in allpaths if t in p.tags],  # [1, 2, 3, 5, 8, 26, 36, 63, 64,
                                 'cat3': [],
                                 'cat4': []},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': [],
                       'untried': [68, 89, 72, 36, 115],
                       'new_badges': None,
                       'promoted': {'cat2': [61, 66]},
                       'demoted': {},
                       'next_loc': None},
             'case4':  # different location than previous step
             # secondary_right records override date and ratio to allow promot.
             # secondary_right list sliced accordingly
                      {'casenum': 4,
                       'mynow': dt('2013-01-29'),
                       'name': user_login['first_name'],
                       'uid': user_login['id'],
                       'loc': Location('agora', db),  # loc 8
                       'prev_loc': Location('ne_stoa', db),  # loc 7
                       'next_loc': None,
                       'prev_npc': Npc(1, db),
                       'npcs_here': [1, 14, 17, 21, 40, 41, 42],
                       'pathid': 1,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag': 61,  # 2ndary overrides time
                                        'tlast_right': dt('2013-01-24'),
                                        'tlast_wrong': dt('2013-01-21'),
                                        'times_right': 9,
                                        'times_wrong': 10,
                                        'secondary_right': [dt('2013-01-28'),
                                                            dt('2013-01-28'),
                                                            dt('2013-01-28'),
                                                            dt('2013-01-29')]},
                                       {'name': 1,
                                        'tag': 62,  # 2ndary overrides ratio
                                        'tlast_right': dt('2013-01-29'),
                                        'tlast_wrong': dt('2013-01-28'),
                                        'times_right': 9,
                                        'times_wrong': 2,
                                        'secondary_right': [dt('2013-01-28'),
                                                            dt('2013-01-28'),
                                                            dt('2013-01-28')]}],
                       'tag_records_out': [{'name': 1,
                                            'tag': 61,  # 2ndary overrides time
                                            'tlast_right': dt('2013-01-28'),
                                            'tlast_wrong': dt('2013-01-21'),
                                            'times_right': 10,
                                            'times_wrong': 10,
                                            'secondary_right': [dt('2013-01-29')]
                                            },
                                           {'name': 1,
                                            'tag': 62,  # 2ndary overrides ratio
                                            'tlast_right': dt('2013-01-29'),
                                            'tlast_wrong': dt('2013-01-28'),
                                            'times_right': 10,
                                            'times_wrong': 2,
                                            'secondary_right': []}],
                       'core_out': {'cat1': [61, 62], 'cat2': [],
                                    'cat3': [], 'cat4': []},
                       'untried_out': {'cat1': [61, 62], 'cat2': [],
                                       'cat3': [], 'cat4': []},
                       'tag_progress': {'latest_new': 2,
                                        'cat1': [61, 62], 'cat2': [],
                                        'cat3': [], 'cat4': [],
                                        'rev1': [], 'rev2': [],
                                        'rev3': [], 'rev4': []},
                       'introduced': [63, 72, 115],
                       'tag_progress_out': {'latest_new': 3,
                                            'cat1': [63, 72, 115],
                                            'cat2': [61, 62],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_start': {'cat1': [61, 62], 'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_out': {'cat1': [63, 72, 115],
                                          'cat2': [61, 62],
                                          'cat3': [], 'cat4': [],
                                          'rev1': [], 'rev2': [],
                                          'rev3': [], 'rev4': []},
                       'paths': {'cat1': [p.id for t in [63, 72, 115]
                                          for p in allpaths if t in p.tags],  # [6, 20, 24, 25, 27, 28, 33, 37,
                                 'cat2': [p.id for t in [61, 62]
                                          for p in allpaths if t in p.tags],  # [1, 2, 3, 5, 8, 63, 64, 70, 95, 96,
                                 'cat3': [],
                                 'cat4': []},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': [],
                       'new_badges': [63, 72, 115],
                       'promoted': {'cat2': [61, 62]},
                       'demoted': {}},
             'case5':  # new badges present
                      {'casenum': 5,
                       'mynow': dt('2013-01-29'),
                       'name': user_login['first_name'],
                       'uid': user_login['id'],
                       'loc': Location('domus_A', db),  # loc 1
                       'prev_loc': Location('domus_A', db),  # loc 1
                       'next_loc': None,
                       'prev_npc': Npc(1, db),
                       'npcs_here': [2, 14, 17, 31, 40, 41, 42],
                       'pathid': 1,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag': 61,
                                        'tlast_right': dt('2013-01-29'),
                                        'tlast_wrong': dt('2013-01-28'),
                                        'times_right': 10,
                                        'times_wrong': 2,
                                        'secondary_right': None}],
                       'core_out': {'cat1': [], 'cat2': [61],
                                    'cat3': [], 'cat4': []},
                       'untried_out': {'cat1': [], 'cat2': [61],
                                       'cat3': [], 'cat4': []},
                       'tag_progress': {'latest_new': 1,
                                        'cat1': [61], 'cat2': [],
                                        'cat3': [], 'cat4': [],
                                        'rev1': [], 'rev2': [],
                                        'rev3': [], 'rev4': []},
                       'introduced': [62],  # assuming we call _introduce_tags
                       'tag_progress_out': {'latest_new': 2,
                                            'cat1': [62], 'cat2': [61],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_start': {'cat1': [61], 'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                       'categories_out': {'cat1': [62], 'cat2': [61],
                                          'cat3': [], 'cat4': [],
                                          'rev1': [], 'rev2': [],
                                          'rev3': [], 'rev4': []},
                       'paths': {'cat1': [p.id for t in [62]
                                          for p in allpaths if t in p.tags],  # [4, 7, 9, 10, 11, 12, 13, 14, 15,
                                 'cat2': [p.id for t in [61]
                                          for p in allpaths if t in p.tags],  # [1, 2, 3, 5, 8, 63, 95, 96, 97, 99,
                                 'cat3': [],
                                 'cat4': []},
                       'new_badges': [62],
                       'promoted': {'cat2': [61]},
                       'demoted': {},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': []}
             }
    return cases[casenum]


@pytest.fixture
def mynpcchooser(mycases, db):
    case = mycases['casedata']
    stepdata = mycases['stepdata']
    if stepdata['id'] in case['steps_here']:
        if case['casenum'] == 1:
            step = StepFactory().get_instance(db=db,
                                              step_id=stepdata['id'],
                                              loc=case['loc'],
                                              prev_loc=case['prev_loc'],
                                              prev_npc=case['prev_npc'])
            location = case['loc']
            prev_npc = case['prev_npc']
            prev_loc = case['prev_loc']
            return {'chooser': NpcChooser(step, location, prev_npc, prev_loc),
                    'casedata': case,
                    'step': step}


@pytest.fixture
def mywalk(mycases, user_login, db):
    """pytest fixture providing a paideia.Walk object for testing"""
    case = mycases['casedata']
    step = mycases['stepdata']
    userdata = user_login
    tag_progress = case['tag_progress']
    tag_records = case['tag_records']
    localias = case['loc'].get_alias()
    return {'walk': Walk(localias,
                         userdata=userdata,
                         tag_records=tag_records,
                         tag_progress=tag_progress,
                         db=db),
            'casedata': case,
            'userdata': userdata,
            'stepdata': step}


@pytest.fixture
def mycategorizer(mycases):
    """A pytest fixture providing a paideia.Categorizer object for testing."""
    case = mycases['casedata']
    step = mycases['stepdata']
    rank = case['tag_progress']['latest_new']
    cats_in = {k: v for k, v in case['tag_progress'].iteritems()
               if not k == 'latest_new'}
    cats_out = {k: v for k, v in case['tag_progress_out'].iteritems()
                if not k == 'latest_new'}
    tag_rs = case['tag_records']
    now = case['mynow']
    out = {'categorizer': Categorizer(rank, cats_in, tag_rs, utcnow=now),
           'categories_in': cats_in,
           'categories_out': cats_out,
           'tag_progress': case['tag_progress'],
           'tag_progress_out': case['tag_progress_out'],
           'core_out': case['core_out'],
           'promoted': case['promoted'],
           'demoted': case['demoted'],
           'new_tags': case['new_badges'],
           'introduced': case['introduced'],
           'untried_out': case['untried_out'],
           'tag_records': tag_rs,
           'stepdata': step}
    if 'tag_records_out' in case.keys():
        out['tag_records_out'] = case['tag_records_out']
    else:
        out['tag_records_out'] = case['tag_records']

    return out


def myuser(tag_progress, tag_records, user_login, db):
    """A pytest fixture providing a paideia.User object for testing."""
    auth = current.auth
    assert auth.is_logged_in()
    user = db.auth_user(auth.user_id)
    assert user.first_name == 'Homer'
    assert user.time_zone == 'America/Toronto'
    return User(user, tag_records, tag_progress)


@pytest.fixture
def mynpc(db):
    '''
    A pytest fixture providing a paideia.Npc object for testing.
    '''
    return Npc(1, db)


@pytest.fixture
def mynpc_stephanos(db):
    '''
    A pytest fixture providing a paideia.Npc object for testing.
    '''
    return Npc(32, db)


@pytest.fixture
def myloc(db):
    """
    A pytest fixture providing a paideia.Location object for testing.
    """
    return Location('shop_of_alexander', db)


@pytest.fixture
def myloc_synagogue(db):
    """
    A pytest fixture providing a paideia.Location object for testing.
    """
    return Location('synagogue', db)


def mypath(pathid, db):
    """
    A pytest fixture providing a paideia.Path object for testing.

    Outputs all valid path/step combinations from mypaths and mysteps (i.e.
    only combinations whose step belongs to the path in question).
    """
    path = Path(pathid, db=db)
    path_steps = db.paths[pathid].steps
    return path, path_steps


def mystep(stepid):
    """
    A pytest fixture providing a paideia.Step object for testing.
    """
    step = StepFactory().get_instance(stepid)
    return step


@pytest.fixture
def myStepMultiple(mycases, request, db):
    """A pytest fixture providing a paideia.StepMultiple object for testing."""
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['widget_type'] == 4:
        for n in [0, 1]:
            responses = ['incorrect', 'correct']
            options = step['step_options']
            right_opt = step['responses']['response1']
            right_i = options.index(right_opt)
            wrong_opts = options[:]
            right_opt = wrong_opts.pop(right_i)
            if len(wrong_opts) > 1:
                user_responses = wrong_opts[randint(0, len(wrong_opts))]
            else:
                user_responses = wrong_opts
            user_responses.append(right_opt)

            opts = ''
            for opt in options:
                opts += '<tr>' \
                        '<td>' \
                        '<input id="response{}" name="response" ' \
                        'type="radio" value="{}" />' \
                        '<label for="response{}">{}</label>' \
                        '</td>' \
                        '</tr>'.format(opt, opt, opt, opt)

            resp = '^<form action="#" enctype="multipart/form-data" ' \
                'method="post">' \
                '<table>' \
                '<tr id="no_table_response__row">' \
                '<td class="w2p_fl">' \
                '<label for="no_table_response" ' \
                'id="no_table_response__label">Response: </label>' \
                '</td>' \
                '<td class="w2p_fw">' \
                '<table class="generic-widget" ' \
                'id="no_table_response" name="response">' \
                '{}' \
                '</table>' \
                '</td>' \
                '<td class="w2p_fc"></td>' \
                '</tr>' \
                '<tr id="submit_record__row">' \
                '<td class="w2p_fl"></td>' \
                '<td class="w2p_fw">' \
                '<input type="submit" value="Submit" /></td>' \
                '<td class="w2p_fc"></td>' \
                '</tr>' \
                '</table>' \
                '<div style="display:none;">' \
                '<input name="_formkey" type="hidden" value=".*" />' \
                '<input name="_formname" type="hidden" ' \
                'value="no_table/create" />' \
                '</div>' \
                '</form>$'.format(opts)

            kwargs = {'step_id': step['id'],
                      'loc': case['loc'],
                      'prev_loc': case['prev_loc'],
                      'prev_npc': case['prev_npc'],
                      'db': db}
            return {'casenum': case['casenum'],
                    'step': StepFactory().get_instance(**kwargs),
                    'casedata': case,
                    'stepdata': step,
                    'resp_text': resp,
                    'user_response': user_responses[n],
                    'reply_text': step['reply_text'][responses[n]],
                    'score': n,
                    'times_right': n,
                    'times_wrong': [1, 0][n]}
    else:
        pass


def myStepEvaluator(stepid, mysteps):
    """
    A pytest fixture providing a paideia.StepEvaluator object for testing.
    """
    for n in [0, 1]:
        responses = ['incorrect', 'correct']
        user_responses = ['bla', mysteps[stepid]['responses']['response1']]
        kwargs = {'responses': mysteps[stepid]['responses'],
                    'tips': mysteps[stepid]['tips']}
        return {'eval': StepEvaluator(**kwargs),
                'tips': mysteps[stepid]['tips'],
                'reply_text': mysteps[stepid]['reply_text'][responses[n]],
                'score': n,
                'times_right': n,
                'times_wrong': [1, 0][n],
                'user_response': user_responses[n]}


@pytest.fixture()
def myMultipleEvaluator(mysteps):
    """
    A pytest fixture providing a paideia.MultipleEvaluator object for testing.
    """
    for n in [0, 1]:
        responses = ['incorrect', 'correct']
        user_responses = ['bla', mysteps['responses']['response1']]
        kwargs = {'responses': mysteps['responses'],
                    'tips': mysteps['tips']}
        return {'eval': MultipleEvaluator(**kwargs),
                'tips': mysteps['tips'],
                'reply_text': mysteps['reply_text'][responses[n]],
                'score': n,
                'times_right': n,
                'times_wrong': [1, 0][n],
                'user_response': user_responses[n]}


@pytest.fixture()
def myblock(myblocks):
    """
    A pytest fixture providing a paideia.Block object for testing.
    """
    return Block().set_block(**myblocks)

# ===================================================================
# Test Classes
# ===================================================================


@pytest.mark.skipif(not global_runall and not global_run_TestNpc,
                    reason='switched off')
class TestNpc():
    '''
    Tests covering the Npc class of the paideia module.
    '''

    def test_npc_get_name(self, mynpc):
        """Test for method Npc.get_name()"""
        assert mynpc.get_name() == 'Ἀλεξανδρος'

    def test_npc_get_id(self, mynpc):
        """Test for method Npc.get_id()"""
        assert mynpc.get_id() == 1

    def test_npc_get_image(self, mynpc):
        """Test for method Npc.get_image()"""
        expected = '<img src="/paideia/static/images/images.image.a23c309d310405ba.70656f706c655f616c6578616e6465722e737667.svg" />'
        actual = mynpc.get_image().xml()
        assert actual == expected

    def test_npc_get_locations(self, mynpc):
        """Test for method Npc.get_locations()"""
        locs = mynpc.get_locations()
        assert isinstance(locs[0], (int, long))
        assert locs[0] == 8  # 6 also in db but not yet active

    def test_npc_get_description(self, mynpc):
        """Test for method Npc.get_description()"""
        assert mynpc.get_description() == "Ἀλεξανδρος is a shop owner and good friend of Simon's household. His shop is in the agora."


@pytest.mark.skipif(not global_runall and not global_run_TestLocation,
                    reason='switched off')
class TestLocation():
    """
    Tests covering the Location class of the paideia module.
    """
    # TODO: parameterize to cover more locations

    def test_location_get_alias(self, myloc):
        """Test for method Location.get_alias"""
        assert myloc.get_alias() == 'shop_of_alexander'

    def test_location_get_name(self, myloc):
        """Test for method Location.get_name"""
        assert myloc.get_name() == 'πανδοκεῖον Ἀλεξανδρου'

    def test_location_get_readable(self, myloc):
        """Test for method Location.get_readable"""
        assert myloc.get_readable() == 'ἡ ἀγορά'

    def test_location_get_bg(self, myloc):
        """Test for method Location.get_bg"""
        actual = myloc.get_bg()
        expected = '/paideia/static/images/images.image.b9c9c11590e5511a.' \
                   '706c616365735f616c6578616e646572732d73686f702e706e67.png'
        assert actual == expected

    def test_location_get_id(self, myloc):
        """Test for method Location.get_id"""
        assert myloc.get_id() == 6


@pytest.mark.skipif(not global_runall and not global_run_TestStep,
                    reason='set to skip')
class TestStep():
    """
    Unit tests covering the Step class of the paideia module.
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,stype', [(1, StepText)])
    def test_step_get_id(self, stepid, stype):
        """Test for method Step.get_id """
        step = StepFactory().get_instance(stepid)
        assert step.get_id() == stepid
        assert isinstance(step, stype) is True

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize("stepid", [1, 2])
    def test_step_get_tags(self, stepid, mysteps):
        """Test for method Step.get_tags """
        step = StepFactory().get_instance(stepid)
        expected = mysteps[stepid]
        actual = step.get_tags()
        assert actual == {'primary': expected['tags'],
                          'secondary': expected['tags_secondary']}

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('caseid,stepid,alias,npcshere,promptext,instrs,'
                             'slidedecks,widgimg,rbuttons,rform,kwargs',
        [('case1', 1,  # StepText ------------------------------
          'shop_of_alexander',
          [2, 8, 17],  # npcs here (for step)
          'How could you write the word "meet" using Greek letters?',
          ['Focus on finding Greek letters that make the *sounds* of the '
           'English word. Don\'t look for Greek "equivalents" for each '
           'English letter.'],  # instructions
          {1: 'Introduction', 2: 'The Alphabet', 6: 'Noun Basics', 7: 'Greek Words I'},
          None,  # widget image
          [],  # response buttons
          '<form action="#" autocomplete="off" enctype="multipart/form-data" '
          'method="post"><table><tr id="no_table_response__row">'
          '<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          'response__label">Response: </label></td><td class="w2p_fw">'
          '<input class="string" id="no_table_response" name="response" '
          'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          '<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          '</tr></table><div style="display:none;"><input name="pre_bug_step_id" '
          'type="hidden" value="1" /></div></form>',
          None,  # kwargs
          ),
         ('case2', 2,  # StepText ------------------------------
          'agora',
          [1],  # npcs here (for step)
          'How could you write the word "bought" using Greek letters?',  # text
          None,  # instructions
          {1: 'Introduction', 2: 'The Alphabet', 6: 'Noun Basics', 7: 'Greek Words I'},
          None,  # widget image
          [],  # response buttons
          '<form action="#" autocomplete="off" enctype="multipart/form-data" '
          'method="post"><table><tr id="no_table_response__row">'
          '<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          'response__label">Response: </label></td><td class="w2p_fw">'
          '<input class="string" id="no_table_response" name="response" '
          'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          '<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          '</tr></table><div style="display:none;"><input name="pre_bug_step_id" '
          'type="hidden" value="2" /></div></form>',
          None,  # kwargs
          ),
         ('case2', 19,  # StepText ------------------------------
          'agora',
          [1],  # npcs here
          'How could you spell the word "pole" with Greek letters?',  # prompt text
          ['Focus on finding Greek letters that make the *sounds* of the '
           'English word. Don\'t look for Greek "equivalents" for each '
           'English letter.'],
          {3L: 'The Alphabet II', 8L: 'Greek Words II'},  # slide decks
          None,  # widget image
          [],  # response buttons
          '<form action="#" autocomplete="off" enctype="multipart/form-data" '
          'method="post"><table><tr id="no_table_response__row">'
          '<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          'response__label">Response: </label></td><td class="w2p_fw">'
          '<input class="string" id="no_table_response" name="response" '
          'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          '<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          '</tr></table><div style="display:none;"><input name="pre_bug_step_id" '
          'type="hidden" value=".*" /></div></form>',
          None,  # kwargs
          ),  # will redirect (currently no case works for step 19)
         ('case1', 30,  # StepRedirect ------------------------------
          'shop_of_alexander',
          [2, 8, 14, 17, 31, 40, 41, 42],  # npcs here
          'Hi there. Sorry, I don\'t have anything for you to '  # prompt text
          'do here at the moment. I think someone was looking '
          'for you at somewhere else in town.',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          None,  # kwargs
          ),  # redirect step
         ('case1', 101,  # StepMultiple ------------------------------
          'shop_of_alexander',
          [14],  # npcs here
          'Is this an English clause?\r\n\r\n"The cat sat."',
          None,  # instructions
          {14: 'Clause Basics'},
          None,  # widget image
          [],  # response buttons
          r'<form action="#" enctype="multipart/form-data" method="post"><table>'
          '<tr id="no_table_response__row"><td class="w2p_fl"><label '
          'for="no_table_response" id="no_table_response__label">Response: '
          '</label></td><td class="w2p_fw"><table class="generic-widget web2py_radiowidget" '
          'id="no_table_response" name="response"><tr><td><input '
          'id="response\xce\xbd\xce\xb1\xce\xb9" name="response" type="radio" '
          'value="\xce\xbd\xce\xb1\xce\xb9" /><label for="response\xce\xbd\xce'
          '\xb1\xce\xb9">\xce\xbd\xce\xb1\xce\xb9</label></td></tr><tr><td>'
          '<input id="response\xce\xbf\xe1\xbd\x90" name="response" '
          'type="radio" value="\xce\xbf\xe1\xbd\x90" /><label for="response'
          '\xce\xbf\xe1\xbd\x90">\xce\xbf\xe1\xbd\x90</label></td></tr></table>'
          '</td><td class="w2p_fc"></td></tr><tr id="submit_record__row"><td '
          'class="w2p_fl"></td><td class="w2p_fw"><input type="submit" '
          'value="Submit" /></td><td class="w2p_fc"></td></tr></table>'
          '<div style="display:none;"><input name="_formkey" type="hidden" '
          'value=".*" /><input name="_formname" type="hidden" '
          'value="no_table/create" /></div></form>',
          None,  # kwargs
          ),
         ('case2', 125,  # StepQuotaReached ------------------------------
          'agora',
          [1, 14, 17, 40, 41, 42],  # npcs here
          'Well done, Homer. You\'ve finished enough paths for today. But '
          'if you would like to keep going, you\'re welcome to continue.',
          None,  # instructions
          None,  # slide decks  # FIXME: no slide decks being found here
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          {'quota': 20},  # kwargs
          ),
         ('case2', 126,  # StepAwardBadges ------------------------------
          'agora',
          [1, 14, 17, 40, 41, 42],  # npcs here
          'Congratulations, Homer! \r\n'  # prompt text
          'You have been promoted to these new badge levels:\r\n'
          '- apprentice alphabet basics\r\n'  # FIXME: order is wrong in message
          '\r\n'
          ' and you\'re ready to start working on some new badges:\r\n'
          '- beginner alphabet (intermediate)\r\n'
          'You can click on your name above to see details '
          'of your progress so far.',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          {'new_tags': {'rev1': [62], 'rev2':[], 'rev3':[], 'rev4':[]},
           'promoted': {'rev2': [61]}},  # kwargs
          ),  # promoted, no new tags (for new badges)
         ('case3', 126,  # StepAwardBadges ------------------------------
          'synagogue',
          [31, 32],  # npcs here
          'Congratulations, Homer! \r\n'  # prompt text
          'You have been promoted to these new badge levels:\r\n'
          '- apprentice alphabet basics\r\n'
          '\r\n'
          'You can click on your name above to see details '
          'of your progress so far.',
          None,   # instructions
          None,   # slide decks
          None,   # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          {'promoted': {'rev2': [61]}},  # kwargs
          ),  # promoted, no new tags (for new badges)
         ('case2', 127,  # StepViewSlides ------------------------------
          'agora',
          [1, 14, 17, 21, 40, 41, 42],  # npcs here
          'Take some time now to review these new slide '
          'sets. They will help with work on your new badges:\n'
          '- [The Alphabet II http://ianwscott.webfactional.com/paideia/listing/slides.html/3]\n'
          '- [Greek Words - More Basics http://ianwscott.webfactional.com/paideia/listing/slides.html/8]',
          # removed data-w2p_disable_with="default" from <a>
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map'],  # response buttons
          None,  # response form
          {'new_tags': {'rev1': [62]}},  # kwargs
          ),  # new tags and promoted (for view slides)
         ])
    def test_step_get_prompt(self, caseid, stepid, alias, npcshere, promptext,
                             instrs, slidedecks, widgimg, rbuttons, rform,
                             kwargs, npc_data, bg_imgs, db):
        """Test for method Step.get_prompt"""
        step = StepFactory().get_instance(stepid, kwargs=kwargs)
        npc = Npc(npcshere[0], db)  # FIXME: randint(0, len(npcshere))
        loc = Location(alias, db)
        actual = step.get_prompt(loc, npc, 'Homer')

        if not isinstance(actual['prompt_text'], str):
            print 'ACTUAL'
            print actual['prompt_text']
            print 'EXPECTED'
            print promptext
            print 'DIFF'
            act = actual['prompt_text'].xml().splitlines(1)
            pprint(list(Differ().compare(act, promptext.splitlines(1))))
            assert actual['prompt_text'].xml() == promptext
        else:
            assert actual['prompt_text'] == promptext
        assert actual['instructions'] == instrs
        if actual['slidedecks']:
            assert all([d for d in actual['slidedecks'].values()
                        if d in slidedecks.values()])
        elif slidedecks:
            pprint(actual['slidedecks'])
            assert actual['slidedecks']
        assert actual['widget_img'] == widgimg  # FIXME: add case with image
        assert actual['bg_image'] == bg_imgs[loc.get_id()]
        assert actual['npc_image']['_src'] == npc_data[npc.get_id()]['image']
        if actual['response_form']:
            print 'ACTUAL'
            print actual['response_form']
            print 'EXPECTED'
            print rform
            print 'DIFF'
            act = actual['response_form'].xml().splitlines(1)
            pprint(list(Differ().compare(act, rform.splitlines(1))))
            assert re.match(rform, actual['response_form'].xml())
        elif rform:
            pprint(actual['response_form'])
            assert actual['response_form']
        assert actual['bugreporter'] == None
        assert actual['response_buttons'] == rbuttons
        assert actual['audio'] == None  # FIXME: add case with audio (path 380, step 445)
        assert actual['loc'] == alias

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,newbadges,promoted,nextloc,quota,'
                             'promptin,promptout',
        [(1,  # step
          None,  # newbadges  FIXME: doesn't test block step replacements
          None,  # promoted
          None,  # nextloc
          20,  # quota
          'How could you write the word "meet" using Greek letters?',  # promptin
          {'newstr': 'How could you write the word "meet" using Greek letters?'},  # promptout
          ),
         (2,  # step
          [62],  # newbadges
          {'cat1': [], 'cat2': [61], 'cat3': [], 'cat4': []},  # promoted
          None,  # nextloc
          20,  # quota
          'How could you write the word "bought" using Greek letters?',  # promptin
          {'newstr': 'How could you write the word "bought" using Greek letters?'},  # promptout
          ),
         (101,  # step
          [62],  # newbadges
          {'cat1': [], 'cat2': [61], 'cat3': [], 'cat4': []},  # promoted
          None,  # nextloc
          20,  # quota
          'Is this an English clause?\r\n\r\n"The cat sat."',  # promptin
          {'newstr': 'Is this an English clause?\r\n\r\n"The cat sat."'},  # promptout
          )
         ])  # don't use steps 30, 125, 126, 127 (block)
    def test_step_make_replacements(self, stepid, newbadges, promoted,
                                    nextloc, quota, promptin, promptout):
        """Unit test for method Step._make_replacements()"""
        step = mystep(stepid)
        outargs = {'raw_prompt': promptin,
                   'username': 'Homer',
                   'reps': {'next_loc': str(nextloc),
                            'new_tags': str(newbadges),
                            'promoted': str(promoted),
                            'quota': str(quota)}
                   }
        actual = step._make_replacements(**outargs)
        assert actual == promptout

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,thisloc,available_npcs', [
        (1,
         'shop_of_alexander',  # loc 6
         [2, 8, 17],  # available npcs (here and this step)
         ),
        (2,
         'agora',  # loc 8
         [1],  # available npcs (here and this step)
         ),
    ])
    def test_step_get_npc(self, stepid, thisloc, available_npcs, db):
        """Test for method Step.get_npc"""
        # TODO: make sure the npc really is randomized
        step = mystep(stepid)
        thisloc = Location(thisloc, db)
        actual = step.get_npc(thisloc)
        npcindb = db.npcs(actual.get_id())

        assert actual.get_id() in db.steps(stepid).npcs
        assert actual.get_name() == npcindb.name
        imageid = npcindb.npc_image
        imagesrc = '/paideia/static/images/{}'.format(db.images(imageid).image)
        assert actual.get_image().xml() == IMG(_src=imagesrc).xml()
        for l in actual.get_locations():
            assert l in npcindb.map_location

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,instructions',
          [(1,
            ['Focus on finding Greek letters that make the *sounds* of the '
             'English word. Don\'t look for Greek "equivalents" for each '
             'English letter.']
            ),
           (2,
            None
            )
           ])
    def test_step_get_instructions(self, stepid, instructions):
        """Test for method Step._get_instructions"""
        step = mystep(stepid)
        actual = step._get_instructions()
        assert actual == instructions

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid, readable',
            [(1,
             {'readable_short': ['μιτ'],
              'readable_long': []},
              ),
             (2,
              {'readable_short': ['βατ', 'βοτ'],
               'readable_long': []},
              ),
             (19,
              {'readable_short': ['πωλ'],
              'readable_long': []},
              )
             ])  # only StepText type
    def test_step_get_readable(self, stepid, readable):
        """Unit tests for StepText._get_readable() method"""
        step = mystep(stepid)
        assert step._get_readable() == readable

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,score,localias,npcshere,resptext,'
                             'rdblshort,rdbllong,replytext,instrs,slides,tips',
         [(1,  # step1, correct
           1.0,  # score
           'shop_of_alexander',  # loc 8
           [2, 8, 17],  # npcs here (for step)
           'μιτ',
           ['μιτ'],
           [],
           'Right. Κάλον.\nYou said\n- [[resp]]',
           ['Focus on finding Greek letters that make '  # instrs
            'the *sounds* of the English word. Don\'t '
            'look for Greek "equivalents" for each '
            'English letter.'],
           {1: 'Introduction',  # slides
            2: 'The Alphabet',
            6: 'Noun Basics',
            7: 'Greek Words - Some Basics to Start With'},
           None,  # tips
           ),
          (1,  # step1, incorrect
           0,  # score
           'shop_of_alexander',  # loc 8
           [2, 8, 17],  # npcs here (for step)
           'βλα',
           ['μιτ'],
           [],
           'Incorrect. Try again!\nYou '
           'said\n- [[resp]]\nThe correct '
           'response is[[rdbl]]',
           ['Focus on finding Greek letters that make '  # instrs
            'the *sounds* of the English word. Don\'t '
            'look for Greek "equivalents" for each '
            'English letter.'],
           {1: 'Introduction',  # slides
            2: 'The Alphabet',
            6: 'Noun Basics',
            7: 'Greek Words - Some Basics to Start With'},
           None,  # tips
           ),
          (2,  # step2, correct
           1.0,  # score
           'agora',
           [1],  # npcs here (for step)
           'βοτ',
           ['βατ', 'βοτ'],
           [],
           'Right. Κάλον.\nYou said\n- '
           '[[resp]]\nCorrect responses '
           'would include[[rdbl]]',
           None,  # instrs
           {1: 'Introduction',  # slides
            2: 'The Alphabet',
            6: 'Noun Basics',
            7: 'Greek Words - Some Basics to Start With'},
           None,  # tips
           ),
          (2,  # step2, incorrect
           0,  # score
           'agora',
           [1],  # npcs here (for step)
           'βλα',
           ['βατ', 'βοτ'],
           [],
           'Incorrect. Try again!\nYou '
           'said\n- [[resp]]\nCorrect responses '
           'would include[[rdbl]]',
           None,  # instrs
           {1: 'Introduction',  # slides
            2: 'The Alphabet',
            6: 'Noun Basics',
            7: 'Greek Words - Some Basics to Start With'},
           None,  # tips
           ),
          (101,  # step 101, correct
           1.0,  # score
           'shop_of_alexander',
           [14],  # npcs here
           'ναι',
           ['ναι'],
           [],
           'Right. Κάλον.\nYou said\n- [[resp]]',
           None,  # instrs
           {14: 'Clause Basics'},  # slides
           None,  # tips
           ),
          (101,  # step 101, incorrect
           0,  # score
           'shop_of_alexander',
           [14],  # npcs here
           'οὐ',
           ['ναι'],
           [],
           'Incorrect. Try again!\nYou '
           'said\n- [[resp]]\nThe correct '
           'response is[[rdbl]]',
           None,  # instrs
           {14: 'Clause Basics'},  # slides
           None,  # tips
           ),
          ])  # only StepText and StepMultiple types
    def test_step_get_reply(self, stepid, score, localias, npcshere, resptext,
                            rdblshort, rdbllong, replytext, instrs, slides,
                            tips, db, npc_data):
        """Unit tests for StepText._get_reply() method"""
        step = mystep(stepid)
        loc = Location(localias, db)
        step.loc = loc
        npc = Npc(npcshere[0], db)
        step.npc = npc

        actual = step.get_reply(resptext)

        replytext = replytext.replace('[[resp]]', resptext)
        rdblsub = ''
        for r in rdblshort:
            rdblsub += '\n- {}'.format(r)
        replytext = replytext.replace('[[rdbl]]', rdblsub)

        assert actual['sid'] == stepid
        assert actual['bg_image'] == loc.get_bg()
        assert actual['prompt_text'] == replytext
        assert actual['readable_long'] == rdbllong
        assert actual['npc_image']['_src'] == npc_data[npc.get_id()]['image']
        assert actual['audio'] is None
        assert actual['widget_img'] is None
        assert actual['instructions'] == instrs
        assert actual['slidedecks'] == slides
        assert actual['hints'] == tips
        assert actual['user_response'] == resptext
        assert actual['score'] == score
        assert actual['times_right'] == int(score)
        assert actual['times_wrong'] == abs(int(score) - 1)


@pytest.mark.skipif('not global_runall and not global_run_TestStepEvaluator',
                    reason='Global skip settings')
class TestStepEvaluator():
    """Class for evaluating the submitted response string for a Step"""

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,regex,uresp,rtext,score,tright,twrong,tips',
        [(1,
          {'response1': '^μιτ$'},
          'μιτ',
          'Right. Κάλον.',
          1,  # score
          1,  # times right
          0,  # times wrong
          None  # tips
          ),
         (1,
          {'response1': '^μιτ$'},
          'βλα',
          'Incorrect. Try again!',
          0,  # score
          0,  # times right
          1,  # times wrong
          None  # tips
          ),
         (2,
          {'response1': '^β(α|ο)τ$'},
          'βοτ',
          'Right. Κάλον.',
          1,  # score
          1,  # times right
          0,  # times wrong
          None  # tips
          ),
         (2,
          {'response1': '^β(α|ο)τ$'},
          'βλα',
          'Incorrect. Try again!',
          0,  # score
          0,  # times right
          1,  # times wrong
          None  # tips
          ),
         (19,
          {'response1': '^πωλ$'},  # regexes
          'πωλ',
          'Right. Κάλον.',
          1,  # score
          1,  # times right
          0,  # times wrong
          None  # tips
          ),
         (19,
          {'response1': '^πωλ$'},  # regexes
          'βλα',
          'Incorrect. Try again!',
          0,  # score
          0,  # times right
          1,  # times wrong
          None  # tips
          )
         ])
    def test_stepevaluator_get_eval(self, stepid, regex, uresp, rtext, score,
                                    tright, twrong, tips):
        """Unit tests for StepEvaluator.get_eval() method."""
        actual = StepEvaluator(responses=regex, tips=tips).get_eval(uresp)
        assert actual['score'] == score
        assert actual['reply'] == rtext
        assert actual['times_wrong'] == twrong
        assert actual['times_right'] == tright
        assert actual['user_response'] == uresp
        assert actual['tips'] == tips


@pytest.mark.skipif('global_runall is False and global_run_TestMultipleEvaluator '
                    'is False', reason='Global skip settings')
class TestMultipleEvaluator():
    """
    Unit testing class for paideia.MultipleEvaluator class.
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,regex,uresp,rtext,score,tright,twrong,tips',
        [(101,
          {'response1': 'ναι'},
          'ναι',
          'Right. Κάλον.',
          1,  # score
          1,  # times right
          0,  # times wrong
          None  # tips
          ),
         (101,
          {'response1': 'ναι'},
          'οὐ',
          'Incorrect. Try again!',
          0,  # score
          0,  # times right
          1,  # times wrong
          None  # tips
          )
         ])
    def test_multipleevaluator_get_eval(self, stepid, regex, uresp,
                                        rtext, score, tright, twrong, tips):
        """Unit tests for multipleevaluator.get_eval() method."""
        actual = StepEvaluator(responses=regex, tips=tips).get_eval(uresp)
        assert actual['score'] == score
        assert actual['reply'] == rtext
        assert actual['times_wrong'] == twrong
        assert actual['times_right'] == tright
        assert actual['user_response'] == uresp
        assert actual['tips'] == tips


@pytest.mark.skipif('global_runall is False and global_run_TestMultipleEvaluator '
                    'is False', reason='Global skip settings')
class TestPath():
    """Unit testing class for the paideia.Path object"""
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestPath is False')

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('pathid', ['3', '89', '19', '1'])
    def test_path_get_id(self, pathid, db, user_login):
        """unit test for Path.get_id()"""
        path, pathsteps = mypath(pathid, db)
        print path
        print pathsteps
        assert path.get_id() == int(pathid)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('pathid,firststep,stepsleft',
                             [(3, 2, []),
                              (89, 101, []),
                              (19, 19, []),
                              (1, 71, []),
                              (63, 66, [67, 68])])
    def test_path_prepare_for_prompt(self, pathid, firststep, stepsleft,
                                     db, user_login):
        """unit test for Path._prepare_for_prompt()"""
        path, pathsteps = mypath(pathid, db)
        actual = path._prepare_for_prompt()
        assert actual is True
        assert isinstance(path.step_for_prompt, Step)  # should cover inherited
        assert path.step_for_prompt.get_id() == firststep
        try:
            assert [s.get_id() for s in path.steps] == stepsleft
        except TypeError:  # if path.steps is now entry, can't be iterated
            assert path.steps == stepsleft

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'casenum,locid,localias,pathid,stepid,stepsleft,locs',
        [('case3', 11, 'synagogue', 19, 19, [], [3, 1, 13, 8, 11]),
         ('case4', 8, 'agora', 1, 71, [], [3, 1, 6, 7, 8, 11]),
         ('case5', 1, 'domus_A', 1, 71, [], [3, 1, 6, 7, 8, 11]),
         ('case5', 1, 'domus_A', 63, 66, [67, 68], [3, 1])
         ])
    def test_path_get_step_for_prompt(self, casenum, locid, localias, pathid,
                                      stepid, stepsleft, locs, db, user_login,
                                      mysteps):
        """
        Unit test for Path.get_step_for_prompt() where no redirect prompted.
        """
        # TODO: test edge cases with, e.g., repeat set
        # TODO: test middle of multi-step path
        path, pathsteps = mypath(pathid, db)
        actual, nextloc, errstring = path.get_step_for_prompt(Location(localias))

        assert path.step_for_prompt.get_id() == stepid
        assert path.step_for_reply == None
        assert actual.get_id() == stepid
        assert path.get_id() == pathid
        assert locid in locs
        assert locid in actual.get_locations()
        assert isinstance(actual, Step)
        try:
            assert [s.get_id() for s in path.steps] == stepsleft
        except TypeError:  # if path.steps is empty, can't be iterated
            assert path.steps == stepsleft
        assert nextloc is None
        assert errstring is None

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'casenum,locid,localias,pathid,stepid,stepsleft,locs',
        [('case1', 6, 'shop_of_alexander', 3, 2, [], [3, 1, 13, 7, 8, 11]),
         ('case2', 8, 'agora', 89, 101, [], [7])
         ])
    def test_path_get_step_for_prompt_redirect(self, casenum, locid, localias,
                                               pathid, stepid, stepsleft, locs,
                                               db, user_login, mysteps):
        """
        Unit test for Path.get_step_for_prompt() in a case that prompts redirect.
        """
        # TODO: redirect can be caused by 2 situations: bad loc or wrong npcs
        # here
        path, pathsteps = mypath(pathid, db)
        actual, nextloc, errstring = path.get_step_for_prompt(Location(localias))

        assert path.step_for_reply is None  # step isn't activated
        assert path.step_for_prompt.get_id() == stepid  # step isn't activated
        assert path.get_id() == pathid
        assert actual.get_id() == stepid
        assert locid not in locs  # NOT in locs
        assert locid not in actual.get_locations()  # NOT in locs
        assert isinstance(actual, Step)
        try:
            assert [s.get_id() for s in path.steps] == stepsleft
        except TypeError:  # if path.steps is empty, can't be iterated
            assert path.steps == stepsleft
        assert nextloc in actual.get_locations()
        assert errstring is None

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'pathid,steps',
        [(3, [2]),
         (89, [101]),
         (19, [19]),
         (1, [71]),
         (63, [66, 67, 68])
         ])
    def test_path_get_steps(self, pathid, steps, mysteps, db, user_login):
        """
        Unit test for method paideia.Path.get_step_for_reply.
        """
        path, pathsteps = mypath(pathid, db)
        expected = [mystep(sid) for sid in steps]
        actual = path.get_steps()
        assert steps == pathsteps
        assert len(actual) == len(expected)
        for idx, actual_s in enumerate(actual):
            assert actual_s.get_id() == expected[idx].get_id()
            assert isinstance(actual_s, type(expected[idx]))

    def test_path_end_prompt(self):
        pass

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'pathid,stepid,stepsleft,locs,localias',
        [(3, 2, [], [3, 1, 13, 7, 8, 11], 'domus_A'),
         (89, 101, [], [7], 'ne_stoa'),
         (19, 19, [], [3, 1, 13, 8, 11], 'domus_A'),
         (1, 71, [], [3, 1, 6, 7, 8, 11], 'domus_A'),
         (1, 71, [], [3, 1, 6, 7, 8, 11], 'domus_A'),
         # (63, 66, [67, 68], [3, 1], 'domus_A')  # first step doesn't take reply
         ])
    def test_path_get_step_for_reply(self, pathid, stepid, stepsleft, locs,
                                     localias, user_login, db):
        """
        Unit test for method paideia.Path.get_step_for_reply.
        """
        path, pathsteps = mypath(pathid, db)
        step = mystep(stepid)
        # preparing for reply stage
        path.get_step_for_prompt(Location(localias))
        path.end_prompt(stepid)

        actual = path.get_step_for_reply()

        assert path.step_for_prompt is None
        try:
            assert [s.get_id() for s in path.steps] == stepsleft
        except TypeError:  # if list empty, so can't be iterated over
            assert path.steps == stepsleft
        assert actual.get_id() == step.get_id()
        assert isinstance(actual, (StepText, StepMultiple))
        assert not isinstance(actual, StepRedirect)
        assert not isinstance(actual, StepQuotaReached)
        assert not isinstance(actual, StepViewSlides)
        assert not isinstance(actual, StepAwardBadges)

    def test_path_complete_step(self):
        pass

    def test_path_reset_steps(self):
        pass


@pytest.mark.skipif('global_runall is False '
                    'and global_run_TestUser is False')
class TestUser(object):
    """unit testing class for the paideia.User class"""

    @pytest.mark.skipif(False, reason='just because')
    def test_user_get_id(self):
        """
        Unit test for User.get_id() method.
        """
        userdata = {'first_name': 'Homer',
                    'id': 1,
                    'time_zone': 'America/Toronto'}
        tagprog = {'latest_new': 2,
                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                 'cat3': [], 'cat4': [],
                 'rev1': [], 'rev2': [61],
                 'rev3': [], 'rev4': []}
        tagrecs = [{'name': 1,
                    'tag': 1,
                    'tlast_right': dt('2013-01-29'),
                    'tlast_wrong': dt('2013-01-29'),
                    'times_right': 1,
                    'times_wrong': 1,
                    'secondary_right': None}]
        actual = User(userdata, tagrecs, tagprog)
        actual.get_id() == 1

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('condition,viewedslides,reportedbadges,expected',
                             [('redirect', False, False,
                               ['redirect']),
                              ('view_slides', False, False,
                               ['view_slides']),
                              ('view_slides', True, False,
                               []),
                              ('new_tags', False, False,
                               ['new_tags']),
                              ('new_tags', False, True,
                               []),
                              ('quota_reached', False, False,
                               ['quota_reached']),
                              ('quota_reached', True, True,
                               ['quota_reached'])
                              ])
    def test_user_set_block(self, condition, viewedslides, reportedbadges,
                            expected):
        """
        Unit test for User.set_block() method.
        """
        userdata = {'first_name': 'Homer',
                    'id': 1,
                    'time_zone': 'America/Toronto'}
        tagprog = {'latest_new': 2,
                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                 'cat3': [], 'cat4': [],
                 'rev1': [], 'rev2': [61],
                 'rev3': [], 'rev4': []}
        tagrecs = [{'name': 1,
                    'tag': 1,
                    'tlast_right': dt('2013-01-29'),
                    'tlast_wrong': dt('2013-01-29'),
                    'times_right': 1,
                    'times_wrong': 1,
                    'secondary_right': None}]
        user = User(userdata, tagrecs, tagprog)

        # set up initial state
        user.blocks = []
        user.viewed_slides = viewedslides
        user.reported_badges = reportedbadges
        user.quota_reached = False  # TODO

        print 'starting blocks:', [u.get_condition() for u in user.blocks]
        assert user.set_block(condition)
        endconditions = [u.get_condition() for u in user.blocks]
        print 'endconditions:', endconditions

        assert endconditions == expected
        assert len(user.blocks) == len(expected)
        assert all([isinstance(b, Block) for b in user.blocks])

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('theblocks',
                             [(['new_tags']),
                              ([]),
                              (['new_tags', 'redirect'])
                              ])
    def test_user_check_for_blocks(self, theblocks):
        """
        unit test for Path._check_for_blocks()

        Since this method only checks for the presence of blocks on the current
        path, it will return a blocking step for each test case (even if that
        case would not normally have a block set.)
        """
        userdata = {'first_name': 'Homer',
                    'id': 1,
                    'time_zone': 'America/Toronto'}
        tagprog = {'latest_new': 2,
                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                 'cat3': [], 'cat4': [],
                 'rev1': [], 'rev2': [61],
                 'rev3': [], 'rev4': []}
        tagrecs = [{'name': 1,
                    'tag': 1,
                    'tlast_right': dt('2013-01-29'),
                    'tlast_wrong': dt('2013-01-29'),
                    'times_right': 1,
                    'times_wrong': 1,
                    'secondary_right': None}]
        myblocks = [Block(b) for b in theblocks]
        user = User(userdata, tagrecs, tagprog, myblocks)
        startlen = len(theblocks)

        actual_return = user.check_for_blocks()
        actual_prop = user.blocks

        if theblocks:
            assert len(actual_prop) == startlen - 1
            assert all([isinstance(b, Block) for b in actual_prop])
            assert isinstance(actual_return, Block)
            assert actual_return.get_condition() == theblocks[0]
            if len(theblocks) > 1:
                assert actual_prop[0].get_condition() == theblocks[1]
            else:
                assert actual_prop == []
        else:
            assert len(actual_prop) == 0
            assert actual_prop == []
            assert actual_return is None

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('start,expected',
                             [(datetime.datetime(2013, 01, 02, 9, 0, 0), False),
                              (datetime.datetime(2013, 01, 02, 9, 0, 0), False),
                              (datetime.datetime(2013, 01, 02, 3, 0, 0), True),
                              (datetime.datetime(2012, 12, 29, 14, 0, 0), True)
                              ])
    def test_user_is_stale(self, start, expected, db):
        """
        Unit test for User.is_stale() method.
        """
        now = datetime.datetime(2013, 01, 02, 14, 0, 0)
        userdata = {'first_name': 'Homer',
                    'id': 1,
                    'time_zone': 'America/Toronto'}
        tagprog = {'latest_new': 2,
                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                 'cat3': [], 'cat4': [],
                 'rev1': [], 'rev2': [61],
                 'rev3': [], 'rev4': []}
        tagrecs = [{'name': 1,
                    'tag': 1,
                    'tlast_right': dt('2013-01-29'),
                    'tlast_wrong': dt('2013-01-29'),
                    'times_right': 1,
                    'times_wrong': 1,
                    'secondary_right': None}]
        user = User(userdata, tagrecs, tagprog)

        actual = user.is_stale(now=now, start=start, db=db)
        assert actual == expected

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('localias,completed,tpout,trecs,redirect,expected',
        [('shop_of_alexander',  # loc 6, (only 1 untried here)
          {'latest': 2,  # completed
           'paths': {2: {'right': 1, 'wrong': 0},
                     3: {'right': 1, 'wrong': 0},
                     5: {'right': 1, 'wrong': 0},
                     8: {'right': 1, 'wrong': 0},
                     9: {'right': 1, 'wrong': 0},
                     40: {'right': 1, 'wrong': 0},
                     63: {'right': 1, 'wrong': 0},
                     95: {'right': 1, 'wrong': 0},
                     96: {'right': 1, 'wrong': 0},
                     97: {'right': 1, 'wrong': 0},
                     99: {'right': 1, 'wrong': 0},
                     102: {'right': 1, 'wrong': 0},
                     256: {'right': 1, 'wrong': 0},
                     409: {'right': 1, 'wrong': 0},
                     410: {'right': 1, 'wrong': 0},
                     411: {'right': 1, 'wrong': 0},
                     412: {'right': 1, 'wrong': 0},
                     413: {'right': 1, 'wrong': 0},
                     414: {'right': 1, 'wrong': 0},
                     415: {'right': 1, 'wrong': 0},
                     416: {'right': 1, 'wrong': 0},
                     417: {'right': 1, 'wrong': 0},
                     418: {'right': 1, 'wrong': 0},
                     419: {'right': 1, 'wrong': 0},
                     420: {'right': 1, 'wrong': 0},
                     421: {'right': 1, 'wrong': 0},
                     422: {'right': 1, 'wrong': 0},
                     423: {'right': 1, 'wrong': 0},
                     444: {'right': 1, 'wrong': 0},
                     445: {'right': 1, 'wrong': 0}
                     }
           },
          {'latest_new': 1,  # tpout
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [61], 'rev2': [],
           'rev3': [], 'rev4': []},
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          None,  # redirect
          [1]  # expected
          ),
         ('synagogue',  # loc 11 [all in loc 11 completed]
          {'latest': 1,  # completed
           'paths': {1: {'right': 1, 'wrong': 0},
                     2: {'right': 1, 'wrong': 0},
                     3: {'right': 1, 'wrong': 0},
                     8: {'right': 1, 'wrong': 0},
                     95: {'right': 1, 'wrong': 0},
                     96: {'right': 1, 'wrong': 0},
                     97: {'right': 1, 'wrong': 0},
                     99: {'right': 1, 'wrong': 0},
                     102: {'right': 1, 'wrong': 0}}
           },
          {'latest_new': 1,  # tpout
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [61], 'rev2': [],
           'rev3': [], 'rev4': []},
          [{'name': 1,  # trecs
            'tag': 61,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-27'),
            'times_right': 20,
            'times_wrong': 10,
            'secondary_right': []}],
          True,  # redirect
          [5, 63, 256, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419,
           420, 421, 422, 423, 444, 445]  # expected (not in this loc)
          ),
         #(8,  # agora (no redirect, new here)
          #[17, 98, 15, 208, 12, 16, 34, 11, 23, 4, 9, 18],
          #{'latest_new': 2,  #
          #'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
          #'cat3': [], 'cat4': [],
          #'rev1': [], 'rev2': [61],
          #'rev3': [], 'rev4': []},
          #None,  # redirect
          #[7, 14, 100, 35, 19, 103, 21, 97, 13, 261, 101]  # expected
          #),
        #(8,  # agora (all for tags completed, repeat here)
        #[4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
        #19, 21, 22, 23, 34, 35, 45, 97, 98, 100, 101,
        #103, 120, 129, 139, 141, 149, 152, 161, 167,
        #176, 184, 190, 208, 222, 225, 228, 231, 236,
        #247, 255, 257, 261, 277, 333, 334, 366, 424,
        #425, 426, 427, 428, 429, 430, 431, 433, 434,
        #435, 436, 437, 439, 440, 441, 444, 445],
        #{'latest_new': 2,
        #'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
        #'cat3': [], 'cat4': [],
        #'rev1': [], 'rev2': [61],
        #'rev3': [], 'rev4': []},
        #False,
        #[101, 35, 34, 23, 16, 261, 15, 21, 208, 100,
        #17, 14, 9, 7, 18, 11, 98, 12, 4, 19, 103, 13,
        #97]  # with tags already completed here (repeat)
        #),
         ])
    def test_user_get_path(self, localias, completed, tpout, trecs,
                           redirect, expected, user_login, db):
        """
        Unit testing method for User.get_path().
        """
        user = User(user_login, trecs, tpout)
        user.completed_paths = completed
        if len(completed) > 20:
            user.past_quota = True
        else:
            user.past_quota = None
        loc = Location(localias)
        actual, acat, aredir, apastq = user.get_path(loc)
        assert actual.get_id() in expected
        assert isinstance(actual, Path)
        assert isinstance(actual.steps[0], Step)
        assert acat in range(1, 5)
        if redirect:
            assert isinstance(aredir, (int, long))
        else:
            assert aredir is None
        if len(completed) == 20:
            assert apastq is True
        else:
            assert apastq is None

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('tpin,rankout,tpout,trecs,counter,promoted,'
                             'new_tags,demoted',
        [({'latest_new': 1,  # tpin =========================================
           'cat1': [1], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          1,  # rank out
          {'latest_new': 1,  # tpout
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [61], 'rev2': [],
           'rev3': [], 'rev4': []},
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': []}],
          4,  # counter
          None,  # promoted
          {'rev1': [61], 'rev2': [],
           'rev3': [], 'rev4': []},  # new tags
          None  # demoted
          ),
         ({'latest_new': 1,  # tpin =========================================
           'cat1': [1], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [1], 'rev2': [],
           'rev3': [], 'rev4': []},
          1,  # rank out
          {'latest_new': 1,  # tpout; doesn't change because no categorization
           'cat1': [1], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [1], 'rev2': [],
           'rev3': [], 'rev4': []},
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': []}],
          3,  # counter
          None,  # promoted
          None,  # new tags
          None  # demoted
          )
         ])
    def test_user_get_categories(self, tpin, rankout, tpout, trecs, counter,
                                 promoted, demoted, new_tags, user_login, db):
        """
        Unit test for User._get_categories() method.
        """
        # set up mock user
        user = User(user_login, trecs, tpin)
        user.cats_counter = counter

        # set up tag records for user
        db(db.tag_progress.name == user_login['id']).delete()
        db.tag_progress.insert(name=user_login['id'], **tpin)

        # set up tag records for user
        db(db.tag_records.name == user_login['id']).delete()
        for tr in trecs:
            tr['name'] = user_login['id']
            db.tag_records.insert(**tr)

        # set these to allow for retrieval if counter < 5
        user.tag_progress = tpin
        user.categories = {c: l for c, l in tpin.iteritems()
                           if c[:3] in ['cat', 'rev']}

        atp, apromoted, anew_tags, ademoted = user.get_categories()
        print 'atp --------------'
        pprint(atp)
        print 'apromoted -------------'
        pprint(apromoted)
        print 'anew_tags --------------'
        pprint(anew_tags)
        print 'ademoted -------------'
        pprint(ademoted)

        newcounter = counter + 1 if counter < 4 else 0
        assert user.cats_counter == newcounter
        for c, l in tpout.iteritems():
            assert atp[c] == l
            assert user.tag_progress[c] == l
            if c in ['cat1', 'cat2', 'cat3', 'cat4']:
                assert user.categories[c] == l
        assert user.rank == tpout['latest_new']
        #print 'promoted -----------------\nactual:', apromoted, '\nexpected:', promoted
        assert apromoted == user.promoted == promoted
        #print 'new_tags -----------------\nactual:', anew_tags, '\nexpected:', new_tags
        assert anew_tags == user.new_tags == new_tags
        #print 'demoted -----------------\nactual:', ademoted, '\nexpected:', demoted
        assert ademoted == user.demoted == demoted

        for k, v in user.tag_progress.iteritems():
            print k
            print v
            assert v == atp[k]

        for idx, tr in enumerate(user.tag_records):
            for field, content in tr.iteritems():
                print field
                print content
                if field not in ['id', 'step', 'in_path', 'modified_on', 'uuid']:
                    assert content == trecs[idx][field]

    #@pytest.mark.skipif(False, reason='just because')
    #def test_user_get_old_categories(self, myuser):
        #"""
        #TODO: at the moment this is only testing initial state in which there
        #are no old categories yet.
        #"""
        ##case = myuser['casedata']
        #user = myuser['user']
        #expected = None
        ##expected = case['tag_progress']
        ##del expected['latest_new']

        #actual = user._get_old_categories()

        #assert actual == expected
        ##for c, l in actual.iteritems():
            ##assert len([i for i in l if i in expected[c]]) == len(expected[c])
            ##assert len(l) == len(expected[c])

    @pytest.mark.parametrize('pathid,psteps,alias',
        [(2, [1], 'agora')
         ])
    @pytest.mark.skipif(False, reason='just because')
    def test_user_complete_path(self, pathid, psteps, alias):
        tpout = {'latest_new': 2,
                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                 'cat3': [], 'cat4': [],
                 'rev1': [], 'rev2': [61],
                 'rev3': [], 'rev4': []}
        trecs = [{'name': 1,
                  'tag': 1,
                  'tlast_right': dt('2013-01-29'),
                  'tlast_wrong': dt('2013-01-29'),
                  'times_right': 1,
                  'times_wrong': 1,
                  'secondary_right': None}]
        userdata = {'first_name': 'Homer', 'id': 1, 'time_zone': 'America/Toronto'}
        user = User(userdata, trecs, tpout)
        # simulate being at end of active path
        user.path = Path(path_id=pathid)
        user.path.completed_steps.append(user.path.steps.pop(0))

        assert user.complete_path(True)

        assert user.completed_paths['latest'] == pathid
        assert user.completed_paths['paths'][str(pathid)]['right'] == 1
        assert user.completed_paths['paths'][str(pathid)]['wrong'] == 0
        assert user.completed_paths['paths'][str(pathid)]['path_dict']['id'] == pathid


@pytest.mark.skipif('global_runall is False '
                    'and global_run_TestCategorizer is False',
                    reason='global skip settings')
class TestCategorizer():
    """
    Unit testing class for the paideia.Categorizer class
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecsin,tagrecsout',
                             [('case1', 1, {'cat1': [1], 'cat2': [],
                                            'cat3': [], 'cat4': [],
                                            'rev1': [], 'rev2': [],
                                            'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}]
                               ),
                              ('case9', 10,
                               mytagpros()['Simon Pan 2014-03-21'],  # catsin
                               mytagrecs()['Simon Pan 2014-03-21'],  # tagrecsin
                               mytagrecs_with_secondary()['Simon Pan 2014-03-21'])  # tagrecsout
                              ])
    def test_categorizer_add_secondary_right(self, casename, rank, catsin,
                                             tagrecsin, tagrecsout, mytagpros,
                                             mytagrecs):
        """Unit test for the paideia.Categorizer._add_secondary_right method."""
        now = dt('2013-01-29')
        # 150 is random user id
        catzr = Categorizer(rank, catsin, tagrecsin, 150, utcnow=now)

        for idx, t in enumerate(tagrecsin):
            if t['secondary_right']:
                tagrecsin[idx] = catzr._add_secondary_right(t)
            else:
                pass
        actual = tagrecsin  # now that it has been run through the method
        print 'tagrecsin are', [t['tag'] for t in actual]
        pprint([t for t in actual if t['tag'] == 5])
        expected = tagrecsout
        print 'expected are', [t['tag'] for t in expected]
        pprint([t for t in actual if t['tag'] == 5])

        for idx, a in enumerate(actual):
            e = expected[idx]
            esr = [d for d in e['secondary_right']] \
                   if e['secondary_right'] else None
            print 'trying tag', a['tag']
            assert a['tag'] == e['tag']
            assert a['tlast_right'] == e['tlast_right']
            assert a['tlast_wrong'] == e['tlast_wrong']
            assert a['times_right'] == e['times_right']
            assert a['tlast_wrong'] == e['tlast_wrong']
            try:
                print 'a -------------------'
                print a['secondary_right']
                print 'esr -----------------'
                print esr
                assert a['secondary_right'] == esr
            except:
                assert not esr
                assert a['secondary_right'] == []

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,catsout,tagrecs',
                             [('case1', 1,
                               # 61 F: rw duration too short, ratio too large
                               {'cat1': [1], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [1], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [1], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 20,
                                 'times_wrong': 20,
                                 'secondary_right': None}]
                               ),
                              ('case2', 1,  # 61 F: not enough times_right
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 10,
                                 'times_wrong': 1,
                                 'secondary_right': []}],
                               ),
                              ('case2', 1,
                               # 61: T (avg>=8, rightdur<=2 days, right>=20)
                               #        despite right/wrong duration
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-28'),
                                 'tlast_wrong': dt('2013-01-28'),
                                 'times_right': 20,
                                 'times_wrong': 1,
                                 'secondary_right': []}],
                               ),
                              ('case2', 1,
                               # 61: T (duration, started > 1day, right >= 20)
                               #        despite ratio > 0.2
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 20,
                                 'times_wrong': 10,
                                 'secondary_right': []}],
                               ),
                              ('case2', 1,
                               # 61: T (avg > 0.8, right >= 20*)
                               #        despite ratio > 0.2
                               #        despite duration
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 20,
                                 'times_wrong': 10,
                                 'secondary_right': []}],
                               ),
                               ('case9',
                                10,
                                mytagpros()['Simon Pan 2014-03-21'],
                                mycatsout_core_algorithm()['Simon Pan 2014-03-21'],
                                mytagrecs()['Simon Pan 2014-03-21']
                                ),
                              ])
    def test_categorizer_core_algorithm(self, casename, rank, catsin, catsout,
                                        tagrecs, db):
        """
        Unit test for the paideia.Categorizer._core_algorithm method

        Case numbers correspond to the cases (user performance scenarios) set
        out in the myrecords fixture.
        """
        now = dt('2013-01-29')
        if casename == 'case9':
            now = dt('2014-03-21')
        # 150 is random user id
        catzr = Categorizer(rank, catsin, tagrecs, 150, utcnow=now)

        actual = catzr._core_algorithm()
        expected = catsout
        for cat, tags in actual.iteritems():
            print 'woohoo!'
            print '\n', cat
            print tags
            print 'expected:'
            print expected[cat]
            print 'diffleft:'
            print [t for t in tags if t not in expected[cat]]
            print 'diffright:'
            print [t for t in expected[cat] if t not in tags]
            assert tags == expected[cat]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecs,introduced',
                             [('case1',  # ???
                               1,
                               {'cat1': [1], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [1], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               [6, 29, 62, 82, 83]
                               ),
                              ('case2',  # promote to rank 2, introduce 62
                               1,
                               {'cat1': [], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-28'),
                                 'times_right': 10,
                                 'times_wrong': 2,
                                 'secondary_right': []}],
                               [6, 29, 62, 82, 83]
                               )
                              ])
    def test_categorizer_introduce_tags(self, casename, rank, catsin, tagrecs,
                                        introduced):
        """Unit test for the paideia.Categorizer._introduce_tags method"""
        now = dt('2013-01-29')
        catzr = Categorizer(rank, catsin, tagrecs, 150, utcnow=now)

        actual = catzr._introduce_tags()
        expected = introduced

        actual.sort()
        assert actual == expected
        assert len(actual) == len(expected)
        assert catzr.rank == rank + 1

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecs,catsout',
                             [('case1',
                               1,
                               {'rev1': [1], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               {'rev1': [1, 61], 'rev2': [],
                                'rev3': [], 'rev4': []}
                               ),
                              ('case9',
                               10,  # rank
                               mycatsout_core_algorithm()['Simon Pan 2014-03-21'],  # catsin
                               mytagrecs_with_secondary()['Simon Pan 2014-03-21'],  # tagrecs
                               mycatsout_add_untried()['Simon Pan 2014-03-21'],  # catout
                               ),
                              ])
    def test_categorizer_add_untried_tags(self, casename, rank, catsin,
                                          tagrecs, catsout):
        """
        Unit test for the paideia.Categorizer._add_untried_tags method

        catsin is the output from _core_algorithm()
        catsout should have untried tags at the user's current rank added
        to cat1.

        """
        now = dt('2013-01-29')
        if casename == 'case9':
            now = dt('2014-03-21')
        #catsin = {k: v for k, v in catsin.iteritems() if k[:3] == 'cat'}
        catzr = Categorizer(rank, catsin, tagrecs, 150, utcnow=now)

        actual = catzr._add_untried_tags(catsin)
        expected = catsout

        for cat, lst in actual.iteritems():
            lst.sort()
            print cat
            print 'actual:', lst
            print 'expected:', expected[cat]
            print 'diffleft:'
            print [t for t in lst if t not in expected[cat]]
            print 'diffright:'
            print [t for t in expected[cat] if t not in lst]
            assert lst == expected[cat]
            assert len(lst) == len(expected[cat])

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecs,catsout',
                             [('case1', 1, {'cat1': [1, 61, 61], 'cat2': [],
                                            'cat3': [], 'cat4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': []},
                               )
                              ])
    def test_categorizer_remove_dups(self, casename, rank, catsin, tagrecs,
                                     catsout):
        """
            Unit test for the paideia.Categorizer._add_untried_tags method

            catsin is the output from _core_algorithm()
            catsout should have untried tags at the user's current rank added
            to cat1.

        """
        now = dt('2013-01-29')
        catzr = Categorizer(rank, catsin, tagrecs, 150, utcnow=now)

        actual = catzr._remove_dups(catsin, rank)
        expected = catsout

        for cat, lst in actual.iteritems():
            assert lst == expected[cat]
            assert len(lst) == len(expected[cat])

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,oldcats,catsin,catsout,tagrecs,'
                             'demoted,promoted,bbrows,newtags',
                             [('case1',  # no prom or demot
                               1,  # rank
                               {'cat1': [1], 'cat2': [],  # oldcats
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [],  # catsin
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [61], 'cat2': [],  # catsout
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               None,  # demoted
                               None,  # promoted
                               None,  # bbrows
                               {'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},  # new tags
                               ),
                              ('case2',  # promote 61 for ratio and time
                               1,
                               {'cat1': [61], 'cat2': [],  # oldcats
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [],  # catsin
                                'cat3': [], 'cat4': [],
                                'rev1': [62], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               {'cat1': [62], 'cat2': [61],  # catsout
                                'cat3': [], 'cat4': [],
                                'rev1': [62], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-28'),
                                 'times_right': 10,
                                 'times_wrong': 2,
                                 'secondary_right': []}],
                               None,  # demoted
                               {'cat1': [], 'cat2': [61],  # promoted
                                'cat3': [], 'cat4': []},
                               None,  # bbrows
                               {'rev1': [62], 'rev2': [],
                                'rev3': [], 'rev4': []},  # new tags
                               ),
                              ('case9',
                               10,  # rank
                               mytagpros()['Simon Pan 2014-03-21'],  # oldcats
                               mycatsout_remove_dups()['Simon Pan 2014-03-21'],  # catsin
                               mycatsout_find_changes()['Simon Pan 2014-03-21'],  # catsout
                               mytagrecs()['Simon Pan 2014-03-21'],  # tagrecs
                               mydemoted()['Simon Pan 2014-03-21'],  # demoted
                               mypromoted()['Simon Pan 2014-03-21'],  # promoted
                               mypromotions()['Simon Pan 2014-03-21'],  # bbrows
                               {'rev1': [4, 55, 96, 102, 130, 131, 132, 135],
                                'rev2': [], 'rev3': [], 'rev4': []},  # new tags
                               )
                              ])
    def test_categorizer_find_cat_changes(self, casename, rank, oldcats, catsin,
                                          catsout, tagrecs, demoted, promoted,
                                          bbrows, newtags):
        """
        Unit test for the paideia.Categorizer._find_cat_changes method.
        """
        now = dt('2013-01-29')
        if casename == 'case9':
            now = dt('2014-03-21')  # date when profile snapshot taken
        catzr = Categorizer(rank, oldcats, tagrecs, 109, utcnow=now)

        actual = catzr._find_cat_changes(catsin, oldcats, bbrows)
        expected = {'categories': catsout,
                    'demoted': demoted,
                    'promoted': promoted}

        # FIXME: also tag progress?
        print 'categories ================================'
        for cat, lst in actual['categories'].iteritems():
            lst.sort()
            print cat
            print 'actual:', lst
            print 'expected:', expected['categories'][cat]
            print 'diffleft:'
            print [t for t in lst if t not in expected['categories'][cat]]
            print 'diffright:'
            print [t for t in expected['categories'][cat] if t not in lst]
            assert lst == expected['categories'][cat]

        print 'demoted ================================'
        if actual['demoted']:
            for cat, lst in actual['demoted'].iteritems():
                print cat
                print 'actual:'
                print lst
                print 'expected:'
                print expected['demoted'][cat]
                print 'diffleft:'
                print [t for t in lst if t not in expected['demoted'][cat]]
                print 'diffright:'
                print [t for t in expected['demoted'][cat] if t not in lst]
                assert lst == expected['demoted'][cat]
        else:
            assert actual['demoted'] is None

        print 'promoted ================================'
        if actual['promoted']:
            for cat, lst in actual['promoted'].iteritems():
                print cat
                print 'actual:'
                print lst
                print 'expected:'
                print expected['promoted'][cat]
                print 'diffleft:'
                print [t for t in lst if t not in expected['promoted'][cat]]
                print 'diffright:'
                print [t for t in expected['promoted'][cat] if t not in lst]
                assert lst == expected['promoted'][cat]
        else:
            assert actual['promoted'] is None

        print 'new tags ====================================='
        print newtags
        assert actual['new_tags'] == newtags

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecsin,'
                             'rankout,catsout,tpout,'
                             'promoted,newtags',
                             [('case1',  # remove 1 and introduce 61 in rev1
                               1,  # rank
                               {'cat1': [1], 'cat2': [],  # catsin
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,  # tagrecs in
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               1,  # rank out
                               {'cat1': [61], 'cat2': [],  # catsout
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'latest_new': 1,  # tag progress out
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               None,
                               {'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               ),
                              ('case2',  # promote 61, introduce set 2
                               1,  # rank in
                               {'cat1': [61], 'cat2': [],  # cats in
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,  # tagrecs in
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-28'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 20,
                                 'times_wrong': 1,
                                 'secondary_right': []}],
                               2,  # rank out
                               {'cat1': [6, 29, 62, 82, 83], 'cat2': [61],  # cats out
                                'cat3': [], 'cat4': [],
                                'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               {'latest_new': 2,  # tag progress out
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [61],  # promoted
                                'cat3': [], 'cat4': []},
                               {'rev1': [6, 29, 62, 82, 83], 'rev2': [],
                                'rev3': [], 'rev4': []},  # new tags
                               )
                              ])
    def test_categorizer_categorize_tags(self, casename, rank, catsin,
                                         tagrecsin, rankout, catsout, tpout,
                                         promoted, newtags, db):
        """
        Unit test for the paideia.Categorizer.categorize method.

        Test case data provided (and parameterized) by mycases fixture via the
        mycategorizer fixture.
        """
        now = dt('2013-01-29')
        # 150 is random user id
        catzr = Categorizer(rank, catsin, tagrecsin, 150, utcnow=now)

        actual = catzr.categorize_tags(rank, tagrecsin, catsin, db=db)
        expected = {'cats': catsout,
                    't_prog': tpout,
                    'nt': newtags,
                    'pro': promoted}

        for key, act in actual['categories'].iteritems():
            print key
            act.sort()
            assert act == expected['cats'][key]

        for key, act in actual['tag_progress'].iteritems():
            if isinstance(act, list):
                act.sort()
            assert act == tpout[key]

        if actual['new_tags']:
            for key, act in actual['new_tags'].iteritems():
                act.sort()
                assert actual['new_tags'][key] == expected['nt'][key]
                assert actual['new_tags'][key] == actual['categories'][key]

        if actual['promoted']:
            for key, act in actual['promoted'].iteritems():
                assert actual['promoted'][key] == expected['pro'][key]


@pytest.mark.skipif('not global_runall '
                    'and not global_run_TestMap')
class TestMap():
    """
    A unit testing class for the paideia.Map class.
    """
    def test_map_show(self):
        """Unit test for paideia.Walk._get_user()"""
        expected = {'map_image': '/paideia/static/images/town_map.svg',
                    'locations': [{'loc_alias': 'None',
                                'bg_image': 8,
                                'id': 3},
                                {'loc_alias': 'domus_A',
                                'bg_image': 8,
                                'id': 1},
                                {'loc_alias': '',
                                'bg_image': 8,
                                'id': 2},
                                {'loc_alias': None,
                                'bg_image': None,
                                'id': 4},
                                {'loc_alias': None,
                                'bg_image': None,
                                'id': 12},
                                {'loc_alias': 'bath',
                                'bg_image': 17,
                                'id': 13},
                                {'loc_alias': 'gymnasion',
                                'bg_image': 113,
                                'id': 14},
                                {'loc_alias': 'shop_of_alexander',
                                'bg_image': 16,
                                'id': 6},
                                {'loc_alias': 'ne_stoa',
                                'bg_image': 18,
                                'id': 7},
                                {'loc_alias': 'agora',
                                'bg_image': 16,
                                'id': 8},
                                {'loc_alias': 'synagogue',
                                'bg_image': 15,
                                'id': 11},
                                {'loc_alias': None,
                                'bg_image': None,
                                'id': 5},
                                {'loc_alias': None,
                                'bg_image': None,
                                'id': 9},
                                {'loc_alias': None,
                                'bg_image': None,
                                'id': 10}
                                ]}
        actual = Map().show()
        for m in expected['locations']:
            act = [a for a in actual['locations'] if a['id'] == m['id']][0]
            assert act['loc_alias'] == m['loc_alias']
            assert act['bg_image'] == m['bg_image']
        assert actual['map_image'] == expected['map_image']


@pytest.mark.skipif('not global_runall '
                    'and not global_run_TestWalk')
class TestWalk():
    """
    A unit testing class for the paideia.Walk class.
    """

    @pytest.mark.parametrize('alias,trecs,tpout',
        [('domus_A',
          [{'name': 1,
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          {'latest_new': 1,
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          )
         ])
    def test_walk_get_user(self, alias, trecs, tpout, user_login, db):
        """Unit test for paideia.Walk._get_user()"""
        thiswalk = Walk(userdata=user_login,
                        tag_records=trecs,
                        tag_progress=tpout,
                        db=db)
        thiswalk.user = None
        actual = thiswalk._get_user(userdata=user_login,
                                    tag_records=trecs,
                                    tag_progress=tpout)
        assert isinstance(actual, User)
        assert actual.get_id() == user_login['id']

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('tpin,trecs,prom,newtags,bbin',
                             [(mytagpros()['Simon Pan 2014-03-21'],  # tpin
                               mytagrecs()['Simon Pan 2014-03-21'],  # trecs
                               mypromoted()['Simon Pan 2014-03-21'],  # prom
                               [],
                               mypromotions()['Simon Pan 2014-03-21']  # bb
                               )
                              ])
    def test_walk_record_cats(self, tpin, trecs, prom, bbin, newtags,
                              user_login, db):
        """
        Unit tests for Walk._record_cats() method.
        """
        # setup ===============================================================
        prom_and_new = copy(prom)
        if newtags:
            prom_and_new['cat1'].extend(newtags)
        now = datetime.datetime.utcnow()
        thiswalk = Walk(userdata=user_login,
                        tag_records=trecs,
                        tag_progress=tpin,
                        db=db)
        db(db.badges_begun.name == user_login['id']).delete()  # clean first
        for r in bbin:
            r['name'] = user_login['id']
            db.badges_begun.insert(**r)
        db(db.tag_progress.name == user_login['id']).delete()  # clean first
        tpin['name'] = user_login['id']
        db.tag_progress.insert(**tpin)
        tpout = copy(tpin)
        for cat, lst in prom.iteritems():
            for t in lst:
                oldcat = cat[:3] + str(int(cat[3:]) - 1)
                tpout[oldcat] = [i for i in tpout[cat] if i != t]
                tpout[cat].append(t)
        tpout['cat1'].extend(newtags)

        # testing method call==================================================
        thiswalk._record_cats(tpout, prom, newtags, db)

        # tag_progress insertion ----------------------------------------------
        sel_tp = db(db.tag_progress.name == user_login['id']).select()
        assert len(sel_tp) == 1  # no extra db rows were created
        actual_tp = sel_tp.first().as_dict()
        for k, v in actual_tp.iteritems():
            tpout['name'] = user_login['id']
            if k not in ['id', 'modified_on', 'uuid', 'just_cats', 'all_cat1']:
                assert v == tpout[k]

        # badges_begun insertion ----------------------------------------------
        sel_bb = db(db.badges_begun.name == user_login['id']).select()

        if prom_and_new:
            expected_bb = {tag: cat for cat, lst in prom_and_new.iteritems()
                           for tag in lst if lst}
            if expected_bb:
                for t, v in expected_bb.iteritems():
                    print 'bb for tag', t
                    thisbb = sel_bb.find(lambda row: row.tag == t)
                    assert len(thisbb) == 1
                    assert now - thisbb.first()[v] < datetime.timedelta(hours=1)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('tag,step_id,path_id,oldrecs,firstname,tright,twrong,'
                             'got_right,score,tpout',
                             [(1,  # tag
                               174,  # step_id
                               155,  # path_id
                               mytagrecs()['Simon Pan 2014-03-21'],  # oldrecs
                               'Simon',  # firstname
                               1,  # times right
                               0,  # times wrong
                               True,  # got right
                               1.0,  # score
                               mytagpros()['Simon Pan 2014-03-21'],  # tpout
                               ),
                              (1,  # tag
                               174,  # step_id
                               155,  # path_id
                               mytagrecs()['Simon Pan 2014-03-21'],  # oldrecs
                               'Simon',  # firstname
                               0,  # times right
                               1,  # times wrong
                               False,  # got right
                               0.0,  # score
                               mytagpros()['Simon Pan 2014-03-21'],  # tpout
                               ),
                              (1,  # tag
                               174,  # step_id
                               155,  # path_id
                               mytagrecs()['Simon Pan 2014-03-21'],  # oldrecs
                               'Simon',  # firstname
                               0,  # times right
                               1,  # times wrong
                               False,  # got right
                               0.5,  # score
                               mytagpros()['Simon Pan 2014-03-21'],  # tpout
                               )
                              ])
    def test_walk_update_tag_record(self, tag, step_id, path_id, oldrecs,
                                    firstname, tright, twrong, got_right,
                                    score, tpout, user_login, db):
        """
        Simulates inaccurate tag_records data for times_right and times_wrong.
        Should be corrected automatically by method, drawing on raw logs.
        """
        now = datetime.datetime(2014, 3, 24, 0, 0, 0)
        oldrecs = [o for o in oldrecs if o['tag'] == tag]
        assert len(oldrecs) == 1
        oldrec = oldrecs[0]
        del oldrec['id']  # since new id will be assigned on insert
        pprint(oldrec)
        db((db.tag_records.name == user_login['id']) &
           (db.tag_records.tag == tag)).delete()
        db.commit()
        # FIXME: insert row for the tag here so that it has to be updated
        # instead of the test always creating a new row.

        """
        # used to simulate actual logs when method corrected inaccurate trecs
        # correction from raw logs no longer performed by method
        #last_right = now
        #earliest = datetime.datetime(2013, 9, 1, 0, 0, 0)
        #last_wrong = now - datetime.timedelta(days=3)
        #log_generator(user_login['id'],
                      #tag,
                      #20,  # total log count
                      #11,  # number right,
                      #last_right,
                      #last_wrong,
                      #earliest,  # earliest attempt
                      #db)
        """

        rightlogs = 0
        wronglogs = 1

        walk = Walk(userdata=user_login,
                    tag_records=oldrecs,
                    tag_progress=tpout,
                    db=db)
        arec = walk._update_tag_record(tag, oldrec, user_login['id'], tright,
                                       twrong, got_right, score,
                                       step_id=step_id, now=now)
        print 'arec:', arec
        arec_row = db.tag_records(arec)

        assert arec_row
        assert arec_row['times_right'] == oldrec['times_right'] + tright
        assert arec_row['times_wrong'] == oldrec['times_wrong'] + twrong
        assert arec_row['step'] == step_id
        assert arec_row['tag'] == tag
        if tright == 1:
            assert arec_row['tlast_wrong'] == oldrec['tlast_wrong']
            assert arec_row['tlast_right'] == now
        else:
            assert arec_row['tlast_right'] == oldrec['tlast_right']
            assert arec_row['tlast_wrong'] == now

        # teardown after injecting test data for user into db
        db(db.tag_records.id == arec).delete()
        db(db.attempt_log.name == user_login['id']).delete()
        db.commit()
        assert db(db.tag_records.id == arec).count() == 0
        assert db(db.attempt_log.name == user_login['id']).count() == 0

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('tag,oldrecs,firstname,tpout',
                             [(1,  # tag
                               mytagrecs()['Simon Pan 2014-03-21'],  # tag recs
                               'Simon',  # firstname
                               mytagpros()['Simon Pan 2014-03-21'],  # tpout
                               )
                              ])
    def test_walk_update_tag_secondary(self, tag, oldrecs, firstname, tpout,
                                       user_login, db):
        """Unit test for the Walk._update_tag_secondary method."""
        now = datetime.datetime(2014, 3, 24, 0, 0, 0)
        oldrec = [o for o in oldrecs if o['tag'] == tag][0]
        pprint(oldrec)
        len2right = len(oldrec['secondary_right'])
        walk = Walk(userdata=user_login,
                    tag_records=oldrecs,
                    tag_progress=tpout,
                    db=db)

        actual = walk._update_tag_secondary(tag, oldrec, user_login['id'],
                                            now=now)
        actualrow = db.tag_records[actual['id']]
        assert actualrow
        assert len(actual['secondary_right']) == len2right + 1
        assert dt(actual['secondary_right'][-1]) == now

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('path_id,step_id,steptags,oldrecs,got_right,score,'
                             'tright,twrong,rstring,newlog,tpout,trecsout',
                             [(3,  # path
                               1,  # step
                               {'primary': [61], 'secondary': []},  # step tags
                               mytagrecs()['Simon Pan 2014-03-21'],  # tag recs
                               True,  # got right
                               1.0,  # score
                               1,  # raw tright
                               0,  # raw twrong
                               'blabla',  # response string
                               {'score': 1.0,  # newlog
                                'in_path': 3,
                                'step': 1,
                                'user_response': 'blabla',
                                'dt_attempted': datetime.datetime(2014, 3, 24,
                                                                  0, 0, 0)},
                               mytagpros()['Simon Pan 2014-03-21'],  # tpout
                               mytagrecs()['Simon Pan 2014-03-21'],  # tag recs out
                               )
                              ])
    def test_walk_record_step(self, path_id, step_id, steptags, oldrecs,
                              got_right, score, tright, twrong, rstring,
                              newlog, tpout, trecsout, user_login, db):
        """
        Unit test for Paideia.Walk._record_step()
        """
        now = datetime.datetime(2014, 3, 24, 0, 0, 0)
        walk = Walk(userdata=user_login,
                    tag_records=oldrecs,
                    tag_progress=tpout,
                    db=db)
        walk.user.path = Path(path_id=path_id, db=db)
        raw_tright = tright
        raw_twrong = twrong
        starting_loglength = len(db(db.attempt_log.name == user_login['id']).select())
        actual_log_id = walk._record_step(user_login['id'], step_id, path_id, score,
                                          raw_tright, raw_twrong, oldrecs,
                                          steptags, rstring, now=now)

        # test writing to attempt_log
        logs_out = db(db.attempt_log.name == user_login['id']).select()
        assert len(logs_out) == starting_loglength + 1
        assert actual_log_id == logs_out.last().id
        newlog['name'] = user_login['id']
        newlog['id'] = actual_log_id
        for field, val in db.attempt_log(actual_log_id).as_dict().iteritems():
            if field == 'dt_attempted':  # FIXME
                pass
            else:
                #print field, '=========='
                #pprint(val)
                if field not in ['modified_on', 'uuid']:
                    assert val == newlog[field]

        # test writing to tag_records
        expected_trecs = [t for t in trecsout if t['tag'] in steptags['primary']]
        actual_trecs = db((db.tag_records.name == user_login['id']) &
                          (db.tag_records.tag.belongs(steptags['primary']))
                          ).select()
        assert len(actual_trecs) == len(steptags['primary'])
        assert len(actual_trecs) == len(expected_trecs)
        for tagrec in expected_trecs:
            tagrec['name'] = user_login['id']
            for key, val in tagrec.iteritems():
                if key in ['tlast_right', 'tlast_wrong']:  # FIXME
                    pass
                else:
                    print key, '=========='
                    pprint(val)
                    assert val == tagrec[key]

        # make sure data is removed from db after test
        assert db(db.attempt_log.id == actual_log_id).delete()
        assert db(db.tag_records.name == user_login['id']).delete()

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('tpin,tagrecs,existing_row',
                             [(mytagpros()['Simon Pan 2014-03-21'],  # tpin
                               mytagrecs()['Simon Pan 2014-03-21'],  # tagrecs
                               True  # existing_row
                               ),
                              (mytagpros()['Simon Pan 2014-03-21'],  # tpin
                               mytagrecs()['Simon Pan 2014-03-21'],  # tagrecs
                               False  # existing_row
                               )
                              ])
    def test_walk_store_user(self, tagrecs, tpin, existing_row, user_login,
                             db, web2py):
        """Unit test for Walk._store_user"""
        # setup ===============================================================
        walk = Walk(userdata=user_login,
                    tag_records=tagrecs,
                    tag_progress=tpin,
                    db=db)
        user = walk._get_user()  # initialized new user in Walk.__init__()
        assert isinstance(user, User)
        assert user.get_id() == user_login['id']

        # set up controlled record in session_data
        db(db.session_data.name == user_login['id']).delete()
        db.commit()

        if existing_row:
            newrec = db.session_data.insert(name=user_login['id'])
            db.commit()
            print 'newrec inserted for update:', newrec
        else:
            print 'newrec not inserted, creating new row for user'

        # store the user instance in db =======================================
        rowid = walk._store_user(user, db=db)  # returns id of row if successful
        print 'rowid:', rowid
        if existing_row:
            assert rowid is None
            storedrow = db(db.session_data.name == user_login['id']
                           ).select().first()
            assert storedrow
        else:
            assert rowid
            storedrow = db(db.session_data.id == rowid).select().first()
            assert storedrow

        # check data stored in db =============================================
        sd = db(db.session_data.name == user_login['id']).select().first()
        dbuser = pickle.loads(sd['other_data'])
        assert dbuser.get_id() == user_login['id']

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('pathid,stepid,alias,npcshere,trecs,tpout,redir,'
                             'promptext,instrs,slidedecks,widgimg,rbuttons,'
                             'rform,replystep',
        [(19,  # path # case3 ======================================================
          19,  # step
          'synagogue',  # alias
          [1],  # npcs here FIXME
          [{'tag': 61,  # trecs
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-21'),
            'times_right': 10,
            'times_wrong': 10,
            'secondary_right': None},
           {'tag': 62,
            'tlast_right': dt('2013-01-10'),
            'tlast_wrong': dt('2013-01-10'),
            'times_right': 10,
            'times_wrong': 0,
            'secondary_right': None},
           {'tag': 63,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-27'),
            'times_right': 9,
            'times_wrong': 0,
            'secondary_right': None},
           {'tag': 66,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-27'),
            'times_right': 10,
            'times_wrong': 0,
            'secondary_right': None}
           ],
          {'latest_new': 4,  # tpout
           'cat1': [6, 9, 29, 36, 61, 62, 63, 66, 68, 72, 79, 80, 81, 82, 83,
                    89, 115],
           'cat2': [61, 66],
           'cat3': [], 'cat4': [],
           'rev1': [6, 9, 29, 36, 61, 62, 63, 66, 68, 72, 79, 80, 81, 82, 83,
                    89, 115],
           'rev2': [61, 66],
           'rev3': [], 'rev4': []},
          False,  # redir
          'How could you spell the word "pole" with Greek letters?',  # prompt text
          ['Focus on finding Greek letters that make the *sounds* of the '
           'English word. Don\'t look for Greek "equivalents" for each '
           'English letter.'],  # instructions
          {3L: 'The Alphabet II', 8L: 'Greek Words II'},  # slide decks
          None,  # widget image
          [],  # response buttons
          '<form action="#" autocomplete="off" enctype="multipart/form-data" '
          'method="post"><table><tr id="no_table_response__row">'
          '<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          'response__label">Response: </label></td><td class="w2p_fw">'
          '<input class="string" id="no_table_response" name="response" '
          'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          '<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          '</tr></table><div style="display:none;"><input name="pre_bug_step_id" '
          'type="hidden" value="19" /></div></form>',
          True  # replystep
          ),
         (19,  # path # case2 ======================================================
          19,  # step
          'agora',  # alias
          [1],  # npcs here
          [{'name': 141,
            'tag': 61,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-28'),
            'times_right': 20,
            'times_wrong': 2,
            'secondary_right': []},
           {'name': 141,
            'tag': 62,
            'tlast_right': dt('2013-03-20'),
            'tlast_wrong': dt('2013-03-20'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': []}],
          {'latest_new': 2,  # tpout
           'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
           'cat3': [], 'cat4': [],
           'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
           'rev3': [], 'rev4': []},
          False,  # redir?
          'How could you spell the word "pole" with Greek letters?',  # prompt text
          ['Focus on finding Greek letters that make the *sounds* of the '
           'English word. Don\'t look for Greek "equivalents" for each '
           'English letter.'],  # instructions
          {3L: 'The Alphabet II', 8L: 'Greek Words II'},  # slide decks
          None,  # widget image
          [],  # response buttons
          '<form action="#" autocomplete="off" enctype="multipart/form-data" '
          'method="post"><table><tr id="no_table_response__row">'
          '<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          'response__label">Response: </label></td><td class="w2p_fw">'
          '<input class="string" id="no_table_response" name="response" '
          'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          '<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          '</tr></table><div style="display:none;"><input name="pre_bug_step_id" '
          'type="hidden" value="19" /></div></form>',
          True  # replystep
          ),
         (89,  # path # case2======================================================
          101,  # step
          'agora',  # alias
          [2, 8, 14, 17, 31, 40, 41, 42],  # npcs here
          [{'name': 1,
            'tag': 61,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-28'),
            'times_right': 10,
            'times_wrong': 2,
            'secondary_right': []}],
          {'latest_new': 2,  # tpout
           'cat1': [62], 'cat2': [61],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          True,  # redirect?
          r'Hi there. Sorry, I don\'t have anything for you to '  # prompt text
          'do here at the moment. I think someone was looking '
          'for you at .*\.',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          False  # replystep
          ),
         #(2,  # path # case1======================================================
          #1,  # step
          #'shop_of_alexander',
          #[2, 8, 17],  # npcs here (for step)
          #[{'name': 1,  # trecs
            #'tag': 1,
            #'tlast_right': dt('2013-01-29'),
            #'tlast_wrong': dt('2013-01-29'),
            #'times_right': 1,
            #'times_wrong': 1,
            #'secondary_right': None}],
          #{'latest_new': 1,  # tpout
           #'cat1': [61], 'cat2': [],
           #'cat3': [], 'cat4': [],
           #'rev1': [], 'rev2': [],
           #'rev3': [], 'rev4': []},
          #False,  # redirect?
          #'How could you write the word "meet" using Greek letters?',
          #['Focus on finding Greek letters that make the *sounds* of the '
           #'English word. Don\'t look for Greek "equivalents" for each '
           #'English letter.'],  # instructions
          #{1: 'Introduction', 2: 'The Alphabet', 6: 'Noun Basics', 7: 'Greek Words I'},
          #None,  # widget image
          #[],  # response buttons
          #'<form action="#" autocomplete="off" enctype="multipart/form-data" '
          #'method="post"><table><tr id="no_table_response__row">'
          #'<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          #'response__label">Response: </label></td><td class="w2p_fw">'
          #'<input class="string" id="no_table_response" name="response" '
          #'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          #'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          #'<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          #'</tr></table></form>',
          #True  # replystep
          #),
         #(3,  # path # case1======================================================
          #2,  # step
          #'shop_of_alexander',
          #[2, 8, 17],  # npcs here FIXME
          #[{'name': 1,  # trecs
            #'tag': 1,
            #'tlast_right': dt('2013-01-29'),
            #'tlast_wrong': dt('2013-01-29'),
            #'times_right': 1,
            #'times_wrong': 1,
            #'secondary_right': None}],
          #{'latest_new': 1,  # tpout
           #'cat1': [61], 'cat2': [],
           #'cat3': [], 'cat4': [],
           #'rev1': [], 'rev2': [],
           #'rev3': [], 'rev4': []},
          #False,  # redirect?
          #'How could you write the word "bought" using Greek letters?',  # text
          #None,  # instructions
          #{1: 'Introduction', 2: 'The Alphabet', 6: 'Noun Basics', 7: 'Greek Words I'},
          #None,  # widget image
          #[],  # response buttons
          #'<form action="#" autocomplete="off" enctype="multipart/form-data" '
          #'method="post"><table><tr id="no_table_response__row">'
          #'<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          #'response__label">Response: </label></td><td class="w2p_fw">'
          #'<input class="string" id="no_table_response" name="response" '
          #'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          #'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          #'<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          #'</tr></table></form>',
          #True  # replystep
          #),
         #(89,  # path # case1======================================================
          #101,  # step
          #'shop_of_alexander',
          #[2, 8, 14, 17, 31, 40, 41, 42],  # npcs here
          #[{'name': 1,  # trecs
            #'tag': 1,
            #'tlast_right': dt('2013-01-29'),
            #'tlast_wrong': dt('2013-01-29'),
            #'times_right': 1,
            #'times_wrong': 1,
            #'secondary_right': None}],
          #{'latest_new': 1,  # tpout
           #'cat1': [61], 'cat2': [],
           #'cat3': [], 'cat4': [],
           #'rev1': [], 'rev2': [],
           #'rev3': [], 'rev4': []},
          #True,  # redirect?
          #'Hi there. Sorry, I don\'t have anything for you to '  # prompt text
          #'do here at the moment. I think someone was looking '
          #'for you at somewhere else in town.',
          #None,  # instructions
          #None,  # slide decks
          #None,  # widget image
          #['map', 'continue'],  # response buttons
          #None,  # response form
          #False  # replystep
          #)
         ])
    def test_walk_ask(self, pathid, stepid, alias, npcshere, trecs, tpout, redir,
                      promptext, instrs, slidedecks, widgimg, rbuttons,
                      rform, replystep, npc_data, bg_imgs, db, user_login):
        """
        """
        # setting up test objects and db test data
        tpout['name'] = user_login['id']
        db(db.attempt_log.name == user_login['id']).delete()
        db.commit()
        atags = chain.from_iterable([v for k, v in tpout.iteritems()
                                     if k in ['cat1', 'cat2', 'cat3', 'cat4']])
        for t in atags:
            thisrec = [r for r in trecs if r['tag'] == t]
            s = thisrec[0] if thisrec else trecs[0]  # if no trec for tag, use first rec for data
            s['tag'] = t
            mycount = s['times_wrong'] + s['times_right']
            if mycount > 0:
                log_generator(user_login['id'], s['tag'], mycount,
                              s['times_right'], s['tlast_right'],
                              s['tlast_wrong'], dt('2013-01-01'), db)
        db(db.tag_progress.name == user_login['id']).delete()
        db.commit()
        db.tag_progress.insert(**tpout)
        db(db.tag_records.name == user_login['id']).delete()
        db.commit()
        print 'trecs:\n', trecs
        for tr in trecs:
            print 'tag:', tr['tag']
            db.tag_records.insert(**tr)
        db.commit()

        thiswalk = Walk(userdata=user_login,
                        tag_records=trecs,
                        tag_progress=tpout,
                        db=db)
        thiswalk.user.path = Path(path_id=pathid, db=db)
        thiswalk.user.categories = {k: v for k, v in tpout.iteritems()
                                    if k[:3] in ['cat', 'rev']}
        loc = Location(alias)
        # setup done

        actual = thiswalk.ask(alias)

        if redir:
            assert actual['sid'] == 30
            assert thiswalk.user.path.get_id() == pathid
        else:
            assert actual['sid'] == stepid
            assert actual['pid'] == pathid
            assert thiswalk.user.path.get_id() == pathid
        assert actual['completed_count'] == 0  # since reply not yet sent
        assert actual['category'] == None
        if not isinstance(actual['prompt_text'], str):
            assert re.match(promptext, actual['prompt_text'].xml())
        else:
            assert re.match(promptext, actual['prompt_text'])
        assert actual['instructions'] == instrs
        if actual['slidedecks']:
            assert all([d for d in actual['slidedecks'].values()
                        if d in slidedecks.values()])
        elif slidedecks:
            assert actual['slidedecks']
        assert actual['widget_img'] == widgimg  # FIXME: add case with image
        assert actual['bg_image'] == bg_imgs[loc.get_id()]
        #assert actual['npc_image']['_src'] == npc_data[npc.get_id()]['image']
        if actual['response_form']:
            print 'actual["response_form"]:\n', actual['response_form']
            print 'rform:\n', rform
            assert re.match(rform, actual['response_form'].xml())
        elif rform:
            pprint(actual['response_form'])
            assert actual['response_form']
        assert actual['bugreporter'] == None
        assert actual['response_buttons'] == rbuttons
        assert actual['audio'] == None  # FIXME: add case with audio (path 380, step 445)
        assert actual['loc'] == alias
        assert thiswalk.user.path.steps == []  # because only step activated
        if redir:
            assert thiswalk.user.path.step_for_prompt.get_id() == stepid
            assert not thiswalk.user.path.step_for_reply
        else:
            assert isinstance(thiswalk.user.path.step_for_reply, Step)
            assert thiswalk.user.path.step_for_reply.get_id() == stepid

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('pathid,stepid,alias,npcshere,trecs,tpout,'
                             'creply,wreply,instrs,slidedecks,rbuttons,'
                             'readable_short,readable_long,tips,cresponse,'
                             'wresponse',
        [(19,  # path # case3 ======================================================
          19,  # step
          'synagogue',  # alias
          [1],  # npcs here FIXME
          [{'tag': 61,  # trecs
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-21'),
            'times_right': 10,
            'times_wrong': 10,
            'secondary_right': None},
           {'tag': 62,
            'tlast_right': dt('2013-01-10'),
            'tlast_wrong': dt('2013-01-10'),
            'times_right': 10,
            'times_wrong': 0,
            'secondary_right': None},
           {'tag': 63,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-27'),
            'times_right': 9,
            'times_wrong': 0,
            'secondary_right': None},
           {'tag': 66,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-27'),
            'times_right': 10,
            'times_wrong': 0,
            'secondary_right': None}
           ],
          {'latest_new': 4,  # ------------------------------------------------ tpout
           'cat1': [62, 63, 68, 115, 72, 89, 36],
           'cat2': [61, 66],
           'cat3': [], 'cat4': [],
           'rev1': [62, 63, 68, 115, 72, 89, 36], 'rev2': [61, 66],
           'rev3': [], 'rev4': []},
          'Right. Κάλον.\nYou said\n- πωλ\n',  # ------------------------------ correct reply
          'Incorrect. Try again!\nYou said\n- βλα\nThe correct '  # ----------- wrong reply
            'response is\n- πωλ',
          ['Focus on finding Greek letters that make the *sounds* of the '  # -- instructions
           'English word. Don\'t look for Greek "equivalents" for each '
           'English letter.'],
          {3L: 'The Alphabet II', 8L: 'Greek Words - More Basics'},  # ------------------- slide decks
          [],  # -------------------------------------------------------------- response buttons
          ['πωλ'],  # --------------------------------------------------------- readable short
          [],  # -------------------------------------------------------------- readable long
          None,  # -------------------------------------------------------------- tips
          'πωλ',  # response correct ------------------------------------------
          'βλα',  # response wrong --------------------------------------------
          ),
         #(19,  # path # case2 ======================================================
          #19,  # step
          #'agora',  # alias
          #[1],  # npcs here
          #[{'name': 141,
            #'tag': 61,
            #'tlast_right': dt('2013-01-29'),
            #'tlast_wrong': dt('2013-01-28'),
            #'times_right': 20,
            #'times_wrong': 2,
            #'secondary_right': []},
           #{'name': 141,
            #'tag': 62,
            #'tlast_right': dt('2013-03-20'),
            #'tlast_wrong': dt('2013-03-20'),
            #'times_right': 1,
            #'times_wrong': 1,
            #'secondary_right': []}],
          #{'latest_new': 2,  # tpout
           #'cat1': [62], 'cat2': [61],
           #'cat3': [], 'cat4': [],
           #'rev1': [62], 'rev2': [61],
           #'rev3': [], 'rev4': []},
          #'How could you spell the word "pole" with Greek letters?',  # prompt text
          #['Focus on finding Greek letters that make the *sounds* of the '
           #'English word. Don\'t look for Greek "equivalents" for each '
           #'English letter.'],  # instructions
          #{3L: 'The Alphabet II', 8L: 'Greek Words II'},  # slide decks
          #[],  # response buttons
          #'<form action="#" autocomplete="off" enctype="multipart/form-data" '
          #'method="post"><table><tr id="no_table_response__row">'
          #'<td class="w2p_fl"><label for="no_table_response" id="no_table_'
          #'response__label">Response: </label></td><td class="w2p_fw">'
          #'<input class="string" id="no_table_response" name="response" '
          #'type="text" value="" /></td><td class="w2p_fc"></td></tr><tr '
          #'id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw">'
          #'<input type="submit" value="Submit" /></td><td class="w2p_fc"></td>'
          #'</tr></table></form>',
          #),
         #(89,  # path # case2======================================================
          #101,  # step
          #'agora',  # alias
          #[2, 8, 14, 17, 31, 40, 41, 42],  # npcs here
          #[{'name': 1,
            #'tag': 61,
            #'tlast_right': dt('2013-01-29'),
            #'tlast_wrong': dt('2013-01-28'),
            #'times_right': 10,
            #'times_wrong': 2,
            #'secondary_right': []}],
          #{'latest_new': 2,  # tpout
           #'cat1': [62], 'cat2': [61],
           #'cat3': [], 'cat4': [],
           #'rev1': [], 'rev2': [],
           #'rev3': [], 'rev4': []},
          #r'Hi there. Sorry, I don\'t have anything for you to '  # prompt text
          #'do here at the moment. I think someone was looking '
          #'for you at .*\.',
          #None,  # instructions
          #None,  # slide decks
          #['map', 'continue'],  # response buttons
          #),
         ])
    def test_walk_reply(self, pathid, stepid, alias, npcshere, trecs, tpout,
                        creply, wreply, instrs, slidedecks, rbuttons,
                        readable_short, readable_long, tips, cresponse,
                        wresponse, npc_data, bg_imgs, db, user_login):
        """Unit test for paideia.Walk.reply() method."""

        # setting up test objects and db test data
        tpout['name'] = user_login['id']
        db(db.attempt_log.name == user_login['id']).delete()
        atags = chain.from_iterable([v for k, v in tpout.iteritems()
                                     if k in ['cat1', 'cat2', 'cat3', 'cat4']])
        for t in atags:
            thisrec = [r for r in trecs if r['tag'] == t]
            s = thisrec[0] if thisrec else trecs[0]  # if no trec for tag, use first rec for data
            s['tag'] = t
            mycount = s['times_wrong'] + s['times_right']
            log_generator(user_login['id'], s['tag'], mycount, s['times_right'],
                        s['tlast_right'], s['tlast_wrong'], dt('2013-01-01'), db)
        db(db.tag_progress.name == user_login['id']).delete()
        db.tag_progress.insert(**tpout)
        db(db.tag_records.name == user_login['id']).delete()
        db.tag_records.bulk_insert(trecs)
        thiswalk = Walk(userdata=user_login,
                        tag_records=trecs,
                        tag_progress=tpout,
                        db=db)
        thiswalk.user.path = Path(path_id=pathid, db=db)
        thiswalk.user.path.step_for_reply = mystep(stepid)
        thiswalk.user.categories = {k: v for k, v in tpout.iteritems()
                                    if k[:3] in ['cat', 'rev']}
        assert thiswalk.user.path.get_id() == pathid
        assert thiswalk.user.path.step_for_reply.get_id() == stepid
        # setup done

        # test for both a correct and an incorrect response
        for n, case in enumerate(['right', 'wrong']):
            if case == 'wrong':
                score = 0
                times_right = 0
                times_wrong = 1
                response_string = wresponse
                reply_text = wreply
            else:
                score = 1
                times_right = 1
                times_wrong = 0
                response_string = cresponse
                reply_text = creply

        thiswalk.start(alias, path=pathid)
        a = thiswalk.start(alias, response_string=response_string)

        assert a['sid'] == stepid
        assert a['pid'] == pathid
        assert a['prompt_text'] == reply_text
        assert a['score'] == score
        assert a['times_right'] == times_right
        assert a['times_wrong'] == times_wrong
        assert a['readable_long'] == readable_long
        #assert a['bg_image'] == bg_imgs
        #assert a['npc_image'] == npc_data
        assert a['audio'] == None
        assert a['widget_img'] == None
        assert a['instructions'] == instrs
        assert a['slidedecks'] == slidedecks
        assert a['hints'] == tips
        assert a['response_buttons'] == ['map', 'retry', 'continue']

        lastlog = db(db.attempt_log.id > 0).select().last()
        rs = response_string.decode('utf8').encode('utf8')
        print 'rs is', type(rs)
        bug_info = (quote_plus(rs),
                    alias,
                    lastlog.id,
                    pathid,
                    score,
                    stepid)
        bug_reporter = ['<a class="bug_reporter" '
                        'data-keyboard="data-keyboard" '
                        'data-target="#bug_reporter_modal" '
                        'data-toggle="modal" '
                        'href="#bug_reporter_modal" '
                        'id="bug_reporter_modal_trigger">'
                        'Something wrong?</a>'
                        '<div aria-hidden="true" aria-labelledby="bug_reporter_modal_trigger" '
                        'class="modal fade " '
                        'data-keyboard="true" '
                        'id="bug_reporter_modal" '
                        'role="dialog" tabindex="-1">'
                        '<div class="modal-dialog modal-lg">'
                        '<div class="modal-content">'
                        '<div class="modal-header">'
                        '<h3 class="modal-title" id="myModalLabel">Did you run into a problem?</h3>'
                        '</div>'
                        '<div class="modal-body ">'
                        '<p>Think your answer should have been correct? '
                        '<a class="bug_reporter_link btn btn-danger" '
                        'data-w2p_disable_with="default" '
                        'data-w2p_method="GET" data-w2p_target="bug_reporter" '
                        'href="/paideia/creating/bug.load?.*'
                        '">click here<i class="icon-bug"></i></a> '
                        'to submit a bug report. You can find the '
                        'instructor&#x27;s response in the &quot;bug '
                        'reports&quot; tab of your user profile.</p></div>'
                        '<div class="modal-footer">'
                        '<button aria-hidden="true" class="pull-right" '
                        'data-dismiss="modal" type="button">Close</button>'
                        '</div></div></div></div>'.format(*bug_info)]
        assert re.match(bug_reporter[0], a['bugreporter'].xml())
        assert not thiswalk.user.path.step_for_reply
        assert not thiswalk.user.path.step_for_prompt
        assert thiswalk.user.path.completed_steps[-1].get_id() == stepid


@pytest.mark.skipif('global_runall is False '
                    'and global_run_TestPathChooser is False')
class TestPathChooser():
    '''
    Unit testing class for the paideia.PathChooser class.
    '''

    @pytest.mark.skipif(False, reason='just because')
    def test_pathchooser_order_cats(self):
        """
        Unit test for the paideia.Pathchooser._order_cats() method.
        """
        locid = 6  # shop_of_alexander
        completed = []
        tpout = {'latest_new': 1,
                 'cat1': [61], 'cat2': [],
                 'cat3': [], 'cat4': [],
                 'rev1': [61], 'rev2': [],
                 'rev3': [], 'rev4': []}
        chooser = PathChooser(tpout, locid, completed)
        expected = [[1, 2, 3, 4],
                    [2, 3, 4, 1],
                    [3, 4, 1, 2],
                    [4, 1, 2, 3]]
        result_count = {1: 0,
                        2: 0,
                        3: 0,
                        4: 0}
        for num in range(10000):
            actual = chooser._order_cats()
            assert actual in expected
            result_count[actual[0]] += 1
        assert result_count[1] in range(7400 - 200, 7400 + 200)
        assert result_count[2] in range(1600 - 200, 1600 + 200)
        assert result_count[3] in range(900 - 200, 900 + 200)
        assert result_count[4] in range(100 - 200, 100 + 200)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('locid,mycat,completed,tpout,expected,force_cat1',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               1,  # mycat
                               {'latest': None,  # completed
                                'paths': {102: {'right': 1, 'wrong': 0},
                                          256: {'right': 1, 'wrong': 0},
                                          40: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0}}},  # completed
                               {'latest_new': 1,  # tpout
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [1, 2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256,
                                409L, 410L, 411L, 412L, 413L, 414L, 415L,
                                416L, 417L, 418L, 419L, 420L, 421L, 422L,
                                423L],  # expected (paths with tag 61)
                               False  # force_cat1
                               ),
                              (6,  # shop_of_alexander (only 1 untried here)
                               2,  # mycat
                               {'latest': None,   # completed
                                'paths': {2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0}}},
                               {'latest_new': 1,  # tpout
                                'cat1': [62], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [62], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                19, 21, 22, 23, 34, 35, 97, 98, 100, 101, 103,
                                257, 261, 277, 424, 425, 426, 427, 428, 429,
                                430, 431, 433, 434, 435, 436, 437, 439, 440,
                                441],  # expected paths with tag 62 (forced cat1)
                               True  # force_cat1
                               ),
                              (8,  # agora
                               2,  # mycat
                               {'latest': None,   # completed
                                'paths': {2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0}}},
                               {'latest_new': 2,  # tpout
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [1, 2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256,
                                409, 410, 411, 412, 413, 414, 415, 416, 417,
                                418, 419, 420, 421, 422, 423],  # expected (tag 61)
                               False  # force_cat1
                               ),
                              (8,  # agora
                               1,  # mycat
                               {'latest': None,   # completed
                                'paths': {2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0}}},
                               {'latest_new': 2,  # tpout
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                19, 21, 22, 23, 34, 35, 97, 98, 100, 101, 103,
                                120, 141, 208, 257, 261, 277, 333, 424, 425,
                                426, 427, 428, 429, 430, 431, 433, 434, 435,
                                436, 437, 439, 440, 441, 607, 608, 609, 610,
                                611, 612, 613, 614, 615, 616, 617, 618, 619,
                                620, 621, 622, 623, 624, 625, 626, 627, 628,
                                629, 630, 631, 632, 633, 634, 635, 636, 637,
                                638, 639, 640, 641, 642, 643, 644, 645, 646,
                                647, 648],  # expected (paths with rev1 tags)
                               False  # force_cat1
                               ),
                              ])
    def test_pathchooser_paths_by_category(self, locid, mycat, completed, tpout,
                                           expected, force_cat1):
        """
        Unit test for the paideia.Pathchooser._paths_by_category() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        if force_cat1:
            chooser.cat1_choices = 0
            chooser.all_choices = 10
        cpaths, cat, forced = chooser._paths_by_category(mycat, tpout['latest_new'])

        cpath_ids = [row['id'] for row in cpaths]
        #print 'actual cpaths:', cpath_ids
        cpath_ids.sort()
        extra_actual = [row['id'] for row in cpaths if row['id'] not in expected]
        #print 'extra actual cpaths:', extra_actual
        #print 'extra expected:', [row for row in expected if row not in cpath_ids]
        assert cpath_ids == expected

        if force_cat1:
            assert cat == 1
            forced is True
            print 'cat:', cat, 'forced:', forced
        else:
            assert cat == mycat
            assert forced is False
            print 'cat:', cat, 'forced:', forced

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('locid,completed,tpout,expected,mode',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               {'latest': 2,  # completed
                                'paths': {2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          5: {'right': 1, 'wrong': 0},
                                          8: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          40: {'right': 1, 'wrong': 0},
                                          63: {'right': 1, 'wrong': 0},
                                          95: {'right': 1, 'wrong': 0},
                                          96: {'right': 1, 'wrong': 0},
                                          97: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          102: {'right': 1, 'wrong': 0},
                                          256: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0},
                                          413: {'right': 1, 'wrong': 0},
                                          414: {'right': 1, 'wrong': 0},
                                          415: {'right': 1, 'wrong': 0},
                                          416: {'right': 1, 'wrong': 0},
                                          417: {'right': 1, 'wrong': 0},
                                          418: {'right': 1, 'wrong': 0},
                                          419: {'right': 1, 'wrong': 0},
                                          420: {'right': 1, 'wrong': 0},
                                          421: {'right': 1, 'wrong': 0},
                                          422: {'right': 1, 'wrong': 0},
                                          423: {'right': 1, 'wrong': 0},
                                          444: {'right': 1, 'wrong': 0},
                                          445: {'right': 1, 'wrong': 0}}
                                },
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [1],  # expected: only one left with tag
                               'here_new'  # mode
                               ),  # ========================================
                              (11,  # synagogue [all in loc 11 completed]
                               {'latest': 1,
                                'paths': {1: {'right': 1, 'wrong': 0},
                                          2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          8: {'right': 1, 'wrong': 0},
                                          95: {'right': 1, 'wrong': 0},
                                          96: {'right': 1, 'wrong': 0},
                                          97: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          102: {'right': 1, 'wrong': 0}}
                                },
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [5, 63, 256, 409, 410, 411, 412, 413, 414, 415,
                                416, 417, 418, 419, 420, 421, 422, 423, 444,
                                445],  # expected: tag 61, not loc 11, not completed
                               'new_elsewhere'  # mode
                               ),  # ========================================
                              (8,  # agora (no redirect, new here)
                               {'latest': 17,  # completed
                                'paths': {17: {'right': 1, 'wrong': 0},
                                          98: {'right': 1, 'wrong': 0},
                                          15: {'right': 1, 'wrong': 0},
                                          208: {'right': 1, 'wrong': 0},
                                          12: {'right': 1, 'wrong': 0},
                                          16: {'right': 1, 'wrong': 0},
                                          34: {'right': 1, 'wrong': 0},
                                          11: {'right': 1, 'wrong': 0},
                                          23: {'right': 1, 'wrong': 0},
                                          4: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          18: {'right': 1, 'wrong': 0}}
                                },
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [7, 14, 100, 35, 19, 103, 21, 97, 13, 261,
                                101],  # expected
                               'here_new'  # mode
                               ),  # ========================================
                              (8,  # agora (all for tags completed, repeat here)
                               {'latest': 4,  # completed
                                'paths': {4: {'right': 1, 'wrong': 0},
                                          7: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          10: {'right': 1, 'wrong': 0},
                                          11: {'right': 1, 'wrong': 0},
                                          12: {'right': 1, 'wrong': 0},
                                          13: {'right': 1, 'wrong': 0},
                                          14: {'right': 1, 'wrong': 0},
                                          15: {'right': 1, 'wrong': 0},
                                          16: {'right': 1, 'wrong': 0},
                                          17: {'right': 1, 'wrong': 0},
                                          18: {'right': 1, 'wrong': 0},
                                          19: {'right': 1, 'wrong': 0},
                                          21: {'right': 1, 'wrong': 0},
                                          22: {'right': 1, 'wrong': 0},
                                          23: {'right': 1, 'wrong': 0},
                                          34: {'right': 1, 'wrong': 0},
                                          35: {'right': 1, 'wrong': 0},
                                          45: {'right': 1, 'wrong': 0},
                                          97: {'right': 1, 'wrong': 0},
                                          98: {'right': 1, 'wrong': 0},
                                          100: {'right': 1, 'wrong': 0},
                                          101: {'right': 1, 'wrong': 0},
                                          103: {'right': 1, 'wrong': 0},
                                          120: {'right': 1, 'wrong': 0},
                                          129: {'right': 1, 'wrong': 0},
                                          139: {'right': 1, 'wrong': 0},
                                          141: {'right': 1, 'wrong': 0},
                                          149: {'right': 1, 'wrong': 0},
                                          152: {'right': 1, 'wrong': 0},
                                          161: {'right': 1, 'wrong': 0},
                                          167: {'right': 1, 'wrong': 0},
                                          176: {'right': 1, 'wrong': 0},
                                          184: {'right': 1, 'wrong': 0},
                                          190: {'right': 1, 'wrong': 0},
                                          208: {'right': 1, 'wrong': 0},
                                          222: {'right': 1, 'wrong': 0},
                                          225: {'right': 1, 'wrong': 0},
                                          228: {'right': 1, 'wrong': 0},
                                          231: {'right': 1, 'wrong': 0},
                                          236: {'right': 1, 'wrong': 0},
                                          247: {'right': 1, 'wrong': 0},
                                          255: {'right': 1, 'wrong': 0},
                                          257: {'right': 1, 'wrong': 0},
                                          261: {'right': 1, 'wrong': 0},
                                          277: {'right': 1, 'wrong': 0},
                                          333: {'right': 1, 'wrong': 0},
                                          334: {'right': 1, 'wrong': 0},
                                          366: {'right': 1, 'wrong': 0},
                                          424: {'right': 1, 'wrong': 0},
                                          425: {'right': 1, 'wrong': 0},
                                          426: {'right': 1, 'wrong': 0},
                                          427: {'right': 1, 'wrong': 0},
                                          428: {'right': 1, 'wrong': 0},
                                          429: {'right': 1, 'wrong': 0},
                                          430: {'right': 1, 'wrong': 0},
                                          431: {'right': 1, 'wrong': 0},
                                          433: {'right': 1, 'wrong': 0},
                                          434: {'right': 1, 'wrong': 0},
                                          435: {'right': 1, 'wrong': 0},
                                          436: {'right': 1, 'wrong': 0},
                                          437: {'right': 1, 'wrong': 0},
                                          439: {'right': 1, 'wrong': 0},
                                          440: {'right': 1, 'wrong': 0},
                                          441: {'right': 1, 'wrong': 0},
                                          444: {'right': 1, 'wrong': 0},
                                          445: {'right': 1, 'wrong': 0},
                                          1: {'right': 1, 'wrong': 0},
                                          2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          5: {'right': 1, 'wrong': 0},
                                          8: {'right': 1, 'wrong': 0},
                                          95: {'right': 1, 'wrong': 0},
                                          96: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          102: {'right': 1, 'wrong': 0},
                                          256: {'right': 1, 'wrong': 0}}
                                },  # last row is cat2 [61]
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [101, 35, 34, 23, 16, 261, 15, 21, 208, 100,
                                17, 14, 9, 7, 18, 11, 98, 12, 4, 19, 103, 13,
                                97, 1, 2, 3, 5, 8, 95, 96, 99, 102,
                                256],  # expected: tags already completed here (repeat)
                               'repeated'  # FIXME: is this right? not repeat_here?
                               ),
                              ])
    def test_pathchooser_choose_from_cat(self, locid, completed, tpout,
                                         expected, mode, db):
        """
        Unit test for the paideia.Pathchooser._choose_from_cats() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        catnum = 1
        expected_rows = db(db.paths.id.belongs(expected)).select()
        path, newloc, cat, actualmode = chooser._choose_from_cat(expected_rows, catnum)
        assert path['id'] in expected
        if newloc:
            assert newloc in [l for l in db.steps(path['steps'][0]).locations]
        else:
            assert newloc is None
        assert cat == 1
        assert actualmode == mode

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('locid,completed,tpout,redirect,mode',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               {'latest': 2,  # completed
                                'paths': {2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          5: {'right': 1, 'wrong': 0},
                                          8: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          63: {'right': 1, 'wrong': 0},
                                          95: {'right': 1, 'wrong': 0},
                                          96: {'right': 1, 'wrong': 0},
                                          97: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          102: {'right': 1, 'wrong': 0},
                                          256: {'right': 1, 'wrong': 0},
                                          409: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0},
                                          413: {'right': 1, 'wrong': 0},
                                          414: {'right': 1, 'wrong': 0},
                                          415: {'right': 1, 'wrong': 0},
                                          416: {'right': 1, 'wrong': 0},
                                          417: {'right': 1, 'wrong': 0},
                                          418: {'right': 1, 'wrong': 0},
                                          419: {'right': 1, 'wrong': 0},
                                          420: {'right': 1, 'wrong': 0},
                                          421: {'right': 1, 'wrong': 0},
                                          422: {'right': 1, 'wrong': 0},
                                          423: {'right': 1, 'wrong': 0}}
                                },
                               {'latest_new': 1,  # tpout
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {1: False},  # redirect
                               'here_new'  # mode
                               ),
                              (11,  # synagogue [all in loc 11 completed] -------
                               {'latest': 1,  # completed
                                'paths': {1: {'right': 1, 'wrong': 0},
                                          2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          8: {'right': 1, 'wrong': 0},
                                          95: {'right': 1, 'wrong': 0},
                                          96: {'right': 1, 'wrong': 0},
                                          97: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          102: {'right': 1, 'wrong': 0}}
                                },
                               {'latest_new': 1,  # tpout
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                                {1: True},  # redirect
                                'new_elsewhere'  # mode
                               ),
                              (8,  # agora (no redirect, new here) --------------
                               {'latest': 17,
                                'paths': {17: {'right': 1, 'wrong': 0},
                                          98: {'right': 1, 'wrong': 0},
                                          15: {'right': 1, 'wrong': 0},
                                          208: {'right': 1, 'wrong': 0},
                                          12: {'right': 1, 'wrong': 0},
                                          16: {'right': 1, 'wrong': 0},
                                          34: {'right': 1, 'wrong': 0},
                                          11: {'right': 1, 'wrong': 0},
                                          23: {'right': 1, 'wrong': 0},
                                          4: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          18: {'right': 1, 'wrong': 0}}
                                },  # completed
                               {'latest_new': 2,  # tpout
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                                {1: False, 2: False},  # redirect
                                'here_new'  # mode
                               ),
                              (8,  # agora (all for tags completed, repeat here) --
                               {'latest': 4,
                                'paths': {4: {'right': 1, 'wrong': 0},
                                          7: {'right': 1, 'wrong': 0},
                                          9: {'right': 1, 'wrong': 0},
                                          10: {'right': 1, 'wrong': 0},
                                          11: {'right': 1, 'wrong': 0},
                                          12: {'right': 1, 'wrong': 0},
                                          13: {'right': 1, 'wrong': 0},
                                          14: {'right': 1, 'wrong': 0},
                                          15: {'right': 1, 'wrong': 0},
                                          16: {'right': 1, 'wrong': 0},
                                          17: {'right': 1, 'wrong': 0},
                                          18: {'right': 1, 'wrong': 0},
                                          19: {'right': 1, 'wrong': 0},
                                          21: {'right': 1, 'wrong': 0},
                                          22: {'right': 1, 'wrong': 0},
                                          23: {'right': 1, 'wrong': 0},
                                          34: {'right': 1, 'wrong': 0},
                                          35: {'right': 1, 'wrong': 0},
                                          45: {'right': 1, 'wrong': 0},
                                          97: {'right': 1, 'wrong': 0},
                                          98: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          100: {'right': 1, 'wrong': 0},
                                          101: {'right': 1, 'wrong': 0},
                                          103: {'right': 1, 'wrong': 0},
                                          120: {'right': 1, 'wrong': 0},
                                          129: {'right': 1, 'wrong': 0},
                                          139: {'right': 1, 'wrong': 0},
                                          141: {'right': 1, 'wrong': 0},
                                          149: {'right': 1, 'wrong': 0},
                                          152: {'right': 1, 'wrong': 0},
                                          161: {'right': 1, 'wrong': 0},
                                          167: {'right': 1, 'wrong': 0},
                                          176: {'right': 1, 'wrong': 0},
                                          184: {'right': 1, 'wrong': 0},
                                          190: {'right': 1, 'wrong': 0},
                                          208: {'right': 1, 'wrong': 0},
                                          222: {'right': 1, 'wrong': 0},
                                          225: {'right': 1, 'wrong': 0},
                                          228: {'right': 1, 'wrong': 0},
                                          231: {'right': 1, 'wrong': 0},
                                          236: {'right': 1, 'wrong': 0},
                                          247: {'right': 1, 'wrong': 0},
                                          255: {'right': 1, 'wrong': 0},
                                          257: {'right': 1, 'wrong': 0},
                                          261: {'right': 1, 'wrong': 0},
                                          277: {'right': 1, 'wrong': 0},
                                          333: {'right': 1, 'wrong': 0},
                                          334: {'right': 1, 'wrong': 0},
                                          366: {'right': 1, 'wrong': 0},
                                          409: {'right': 1, 'wrong': 0},
                                          410: {'right': 1, 'wrong': 0},
                                          411: {'right': 1, 'wrong': 0},
                                          412: {'right': 1, 'wrong': 0},
                                          413: {'right': 1, 'wrong': 0},
                                          414: {'right': 1, 'wrong': 0},
                                          415: {'right': 1, 'wrong': 0},
                                          416: {'right': 1, 'wrong': 0},
                                          417: {'right': 1, 'wrong': 0},
                                          418: {'right': 1, 'wrong': 0},
                                          419: {'right': 1, 'wrong': 0},
                                          420: {'right': 1, 'wrong': 0},
                                          421: {'right': 1, 'wrong': 0},
                                          423: {'right': 1, 'wrong': 0},
                                          424: {'right': 1, 'wrong': 0},
                                          425: {'right': 1, 'wrong': 0},
                                          426: {'right': 1, 'wrong': 0},
                                          427: {'right': 1, 'wrong': 0},
                                          428: {'right': 1, 'wrong': 0},
                                          429: {'right': 1, 'wrong': 0},
                                          430: {'right': 1, 'wrong': 0},
                                          431: {'right': 1, 'wrong': 0},
                                          433: {'right': 1, 'wrong': 0},
                                          434: {'right': 1, 'wrong': 0},
                                          435: {'right': 1, 'wrong': 0},
                                          436: {'right': 1, 'wrong': 0},
                                          437: {'right': 1, 'wrong': 0},
                                          439: {'right': 1, 'wrong': 0},
                                          440: {'right': 1, 'wrong': 0},
                                          441: {'right': 1, 'wrong': 0},
                                          444: {'right': 1, 'wrong': 0},
                                          445: {'right': 1, 'wrong': 0},
                                          607: {'right': 1, 'wrong': 0},
                                          608: {'right': 1, 'wrong': 0},
                                          609: {'right': 1, 'wrong': 0},
                                          610: {'right': 1, 'wrong': 0},
                                          611: {'right': 1, 'wrong': 0},
                                          612: {'right': 1, 'wrong': 0},
                                          613: {'right': 1, 'wrong': 0},
                                          614: {'right': 1, 'wrong': 0},
                                          615: {'right': 1, 'wrong': 0},
                                          616: {'right': 1, 'wrong': 0},
                                          617: {'right': 1, 'wrong': 0},
                                          618: {'right': 1, 'wrong': 0},
                                          619: {'right': 1, 'wrong': 0},
                                          620: {'right': 1, 'wrong': 0},
                                          621: {'right': 1, 'wrong': 0},
                                          622: {'right': 1, 'wrong': 0},
                                          623: {'right': 1, 'wrong': 0},
                                          624: {'right': 1, 'wrong': 0},
                                          625: {'right': 1, 'wrong': 0},
                                          626: {'right': 1, 'wrong': 0},
                                          627: {'right': 1, 'wrong': 0},
                                          628: {'right': 1, 'wrong': 0},
                                          629: {'right': 1, 'wrong': 0},
                                          630: {'right': 1, 'wrong': 0},
                                          631: {'right': 1, 'wrong': 0},
                                          632: {'right': 1, 'wrong': 0},
                                          633: {'right': 1, 'wrong': 0},
                                          634: {'right': 1, 'wrong': 0},
                                          635: {'right': 1, 'wrong': 0},
                                          636: {'right': 1, 'wrong': 0},
                                          637: {'right': 1, 'wrong': 0},
                                          638: {'right': 1, 'wrong': 0},
                                          639: {'right': 1, 'wrong': 0},
                                          640: {'right': 1, 'wrong': 0},
                                          641: {'right': 1, 'wrong': 0},
                                          642: {'right': 1, 'wrong': 0},
                                          643: {'right': 1, 'wrong': 0},
                                          644: {'right': 1, 'wrong': 0},
                                          645: {'right': 1, 'wrong': 0},
                                          646: {'right': 1, 'wrong': 0},
                                          647: {'right': 1, 'wrong': 0},
                                          648: {'right': 1, 'wrong': 0},
                                          1: {'right': 1, 'wrong': 0},
                                          2: {'right': 1, 'wrong': 0},
                                          3: {'right': 1, 'wrong': 0},
                                          5: {'right': 1, 'wrong': 0},
                                          8: {'right': 1, 'wrong': 0},
                                          63: {'right': 1, 'wrong': 0},
                                          95: {'right': 1, 'wrong': 0},
                                          96: {'right': 1, 'wrong': 0},
                                          99: {'right': 1, 'wrong': 0},
                                          102: {'right': 1, 'wrong': 0},
                                          256: {'right': 1, 'wrong': 0},
                                          422: {'right': 1, 'wrong': 0}
                                          }
                                },  # last row is cat2 [61]
                               {'latest_new': 2,
                                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                 'cat3': [], 'cat4': [],
                                 'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                 'rev3': [], 'rev4': []},
                               {1: False, 2: False},
                               'repeated'
                               ),
                              (8,  # agora (all but one repeated 3x) --
                               {'latest': 4,
                                'paths': {4: {'right': 1, 'wrong': 0},
                                          7: {'right': 2, 'wrong': 0},
                                          9: {'right': 2, 'wrong': 0},
                                          10: {'right': 2, 'wrong': 0},
                                          11: {'right': 2, 'wrong': 0},
                                          12: {'right': 2, 'wrong': 0},
                                          13: {'right': 2, 'wrong': 0},
                                          14: {'right': 2, 'wrong': 0},
                                          15: {'right': 2, 'wrong': 0},
                                          16: {'right': 2, 'wrong': 0},
                                          17: {'right': 2, 'wrong': 0},
                                          18: {'right': 2, 'wrong': 0},
                                          19: {'right': 2, 'wrong': 0},
                                          21: {'right': 2, 'wrong': 0},
                                          22: {'right': 2, 'wrong': 0},
                                          23: {'right': 2, 'wrong': 0},
                                          34: {'right': 2, 'wrong': 0},
                                          35: {'right': 2, 'wrong': 0},
                                          45: {'right': 2, 'wrong': 0},
                                          97: {'right': 2, 'wrong': 0},
                                          98: {'right': 2, 'wrong': 0},
                                          99: {'right': 2, 'wrong': 0},
                                          100: {'right': 2, 'wrong': 0},
                                          101: {'right': 2, 'wrong': 0},
                                          103: {'right': 2, 'wrong': 0},
                                          120: {'right': 2, 'wrong': 0},
                                          129: {'right': 2, 'wrong': 0},
                                          139: {'right': 2, 'wrong': 0},
                                          141: {'right': 2, 'wrong': 0},
                                          149: {'right': 2, 'wrong': 0},
                                          152: {'right': 2, 'wrong': 0},
                                          161: {'right': 2, 'wrong': 0},
                                          167: {'right': 2, 'wrong': 0},
                                          176: {'right': 2, 'wrong': 0},
                                          184: {'right': 2, 'wrong': 0},
                                          190: {'right': 2, 'wrong': 0},
                                          208: {'right': 2, 'wrong': 0},
                                          222: {'right': 2, 'wrong': 0},
                                          225: {'right': 2, 'wrong': 0},
                                          228: {'right': 2, 'wrong': 0},
                                          231: {'right': 2, 'wrong': 0},
                                          236: {'right': 2, 'wrong': 0},
                                          247: {'right': 2, 'wrong': 0},
                                          255: {'right': 2, 'wrong': 0},
                                          257: {'right': 2, 'wrong': 0},
                                          261: {'right': 2, 'wrong': 0},
                                          277: {'right': 2, 'wrong': 0},
                                          333: {'right': 2, 'wrong': 0},
                                          334: {'right': 2, 'wrong': 0},
                                          366: {'right': 2, 'wrong': 0},
                                          409: {'right': 2, 'wrong': 0},
                                          410: {'right': 2, 'wrong': 0},
                                          411: {'right': 2, 'wrong': 0},
                                          412: {'right': 2, 'wrong': 0},
                                          413: {'right': 2, 'wrong': 0},
                                          414: {'right': 2, 'wrong': 0},
                                          415: {'right': 2, 'wrong': 0},
                                          416: {'right': 2, 'wrong': 0},
                                          417: {'right': 2, 'wrong': 0},
                                          418: {'right': 2, 'wrong': 0},
                                          419: {'right': 2, 'wrong': 0},
                                          420: {'right': 2, 'wrong': 0},
                                          421: {'right': 2, 'wrong': 0},
                                          423: {'right': 2, 'wrong': 0},
                                          424: {'right': 2, 'wrong': 0},
                                          425: {'right': 2, 'wrong': 0},
                                          426: {'right': 2, 'wrong': 0},
                                          427: {'right': 2, 'wrong': 0},
                                          428: {'right': 2, 'wrong': 0},
                                          429: {'right': 2, 'wrong': 0},
                                          430: {'right': 2, 'wrong': 0},
                                          431: {'right': 2, 'wrong': 0},
                                          433: {'right': 2, 'wrong': 0},
                                          434: {'right': 2, 'wrong': 0},
                                          435: {'right': 2, 'wrong': 0},
                                          436: {'right': 2, 'wrong': 0},
                                          437: {'right': 2, 'wrong': 0},
                                          439: {'right': 2, 'wrong': 0},
                                          440: {'right': 2, 'wrong': 0},
                                          441: {'right': 2, 'wrong': 0},
                                          444: {'right': 2, 'wrong': 0},
                                          445: {'right': 2, 'wrong': 0},
                                          607: {'right': 2, 'wrong': 0},
                                          608: {'right': 2, 'wrong': 0},
                                          609: {'right': 2, 'wrong': 0},
                                          610: {'right': 2, 'wrong': 0},
                                          611: {'right': 2, 'wrong': 0},
                                          612: {'right': 2, 'wrong': 0},
                                          613: {'right': 2, 'wrong': 0},
                                          614: {'right': 2, 'wrong': 0},
                                          615: {'right': 2, 'wrong': 0},
                                          616: {'right': 2, 'wrong': 0},
                                          617: {'right': 2, 'wrong': 0},
                                          618: {'right': 2, 'wrong': 0},
                                          619: {'right': 2, 'wrong': 0},
                                          620: {'right': 2, 'wrong': 0},
                                          621: {'right': 2, 'wrong': 0},
                                          622: {'right': 2, 'wrong': 0},
                                          623: {'right': 2, 'wrong': 0},
                                          624: {'right': 2, 'wrong': 0},
                                          625: {'right': 2, 'wrong': 0},
                                          626: {'right': 2, 'wrong': 0},
                                          627: {'right': 2, 'wrong': 0},
                                          628: {'right': 2, 'wrong': 0},
                                          629: {'right': 2, 'wrong': 0},
                                          630: {'right': 2, 'wrong': 0},
                                          631: {'right': 2, 'wrong': 0},
                                          632: {'right': 2, 'wrong': 0},
                                          633: {'right': 2, 'wrong': 0},
                                          634: {'right': 2, 'wrong': 0},
                                          635: {'right': 2, 'wrong': 0},
                                          636: {'right': 2, 'wrong': 0},
                                          637: {'right': 2, 'wrong': 0},
                                          638: {'right': 2, 'wrong': 0},
                                          639: {'right': 2, 'wrong': 0},
                                          640: {'right': 2, 'wrong': 0},
                                          641: {'right': 2, 'wrong': 0},
                                          642: {'right': 2, 'wrong': 0},
                                          643: {'right': 2, 'wrong': 0},
                                          644: {'right': 2, 'wrong': 0},
                                          645: {'right': 2, 'wrong': 0},
                                          646: {'right': 2, 'wrong': 0},
                                          647: {'right': 2, 'wrong': 0},
                                          648: {'right': 2, 'wrong': 0},
                                          1: {'right': 2, 'wrong': 0},
                                          2: {'right': 2, 'wrong': 0},
                                          3: {'right': 2, 'wrong': 0},
                                          5: {'right': 2, 'wrong': 0},
                                          8: {'right': 2, 'wrong': 0},
                                          63: {'right': 1, 'wrong': 0},
                                          95: {'right': 2, 'wrong': 0},
                                          96: {'right': 2, 'wrong': 0},
                                          99: {'right': 2, 'wrong': 0},
                                          102: {'right': 2, 'wrong': 0},
                                          256: {'right': 2, 'wrong': 0},
                                          422: {'right': 1, 'wrong': 0}
                                          }
                                },  # last row is cat2 [61]
                               {'latest_new': 2,
                                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                 'cat3': [], 'cat4': [],
                                 'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                 'rev3': [], 'rev4': []},
                                {1: False, 2: False},
                                'repeated'
                               ),
                              (8,  # agora (all but one repeated 2x) --
                               {'latest': 4,
                                'paths': {4: {'right': 2, 'wrong': 0},
                                          7: {'right': 3, 'wrong': 0},
                                          9: {'right': 3, 'wrong': 0},
                                          10: {'right': 3, 'wrong': 0},
                                          11: {'right': 3, 'wrong': 0},
                                          12: {'right': 3, 'wrong': 0},
                                          13: {'right': 3, 'wrong': 0},
                                          14: {'right': 3, 'wrong': 0},
                                          15: {'right': 3, 'wrong': 0},
                                          16: {'right': 3, 'wrong': 0},
                                          17: {'right': 3, 'wrong': 0},
                                          18: {'right': 3, 'wrong': 0},
                                          19: {'right': 3, 'wrong': 0},
                                          21: {'right': 3, 'wrong': 0},
                                          22: {'right': 3, 'wrong': 0},
                                          23: {'right': 3, 'wrong': 0},
                                          34: {'right': 3, 'wrong': 0},
                                          35: {'right': 3, 'wrong': 0},
                                          45: {'right': 3, 'wrong': 0},
                                          97: {'right': 3, 'wrong': 0},
                                          98: {'right': 3, 'wrong': 0},
                                          99: {'right': 3, 'wrong': 0},
                                          100: {'right': 3, 'wrong': 0},
                                          101: {'right': 3, 'wrong': 0},
                                          103: {'right': 3, 'wrong': 0},
                                          120: {'right': 3, 'wrong': 0},
                                          129: {'right': 3, 'wrong': 0},
                                          139: {'right': 3, 'wrong': 0},
                                          141: {'right': 3, 'wrong': 0},
                                          149: {'right': 3, 'wrong': 0},
                                          152: {'right': 3, 'wrong': 0},
                                          161: {'right': 3, 'wrong': 0},
                                          167: {'right': 3, 'wrong': 0},
                                          176: {'right': 3, 'wrong': 0},
                                          184: {'right': 3, 'wrong': 0},
                                          190: {'right': 3, 'wrong': 0},
                                          208: {'right': 3, 'wrong': 0},
                                          222: {'right': 3, 'wrong': 0},
                                          225: {'right': 3, 'wrong': 0},
                                          228: {'right': 3, 'wrong': 0},
                                          231: {'right': 3, 'wrong': 0},
                                          236: {'right': 3, 'wrong': 0},
                                          247: {'right': 3, 'wrong': 0},
                                          255: {'right': 3, 'wrong': 0},
                                          257: {'right': 3, 'wrong': 0},
                                          261: {'right': 3, 'wrong': 0},
                                          277: {'right': 3, 'wrong': 0},
                                          333: {'right': 3, 'wrong': 0},
                                          334: {'right': 3, 'wrong': 0},
                                          366: {'right': 3, 'wrong': 0},
                                          409: {'right': 3, 'wrong': 0},
                                          410: {'right': 3, 'wrong': 0},
                                          411: {'right': 3, 'wrong': 0},
                                          412: {'right': 3, 'wrong': 0},
                                          413: {'right': 3, 'wrong': 0},
                                          414: {'right': 3, 'wrong': 0},
                                          415: {'right': 3, 'wrong': 0},
                                          416: {'right': 3, 'wrong': 0},
                                          417: {'right': 3, 'wrong': 0},
                                          418: {'right': 3, 'wrong': 0},
                                          419: {'right': 3, 'wrong': 0},
                                          420: {'right': 3, 'wrong': 0},
                                          421: {'right': 3, 'wrong': 0},
                                          423: {'right': 3, 'wrong': 0},
                                          424: {'right': 3, 'wrong': 0},
                                          425: {'right': 3, 'wrong': 0},
                                          426: {'right': 3, 'wrong': 0},
                                          427: {'right': 3, 'wrong': 0},
                                          428: {'right': 3, 'wrong': 0},
                                          429: {'right': 3, 'wrong': 0},
                                          430: {'right': 3, 'wrong': 0},
                                          431: {'right': 3, 'wrong': 0},
                                          433: {'right': 3, 'wrong': 0},
                                          434: {'right': 3, 'wrong': 0},
                                          435: {'right': 3, 'wrong': 0},
                                          436: {'right': 3, 'wrong': 0},
                                          437: {'right': 3, 'wrong': 0},
                                          439: {'right': 3, 'wrong': 0},
                                          440: {'right': 3, 'wrong': 0},
                                          441: {'right': 3, 'wrong': 0},
                                          444: {'right': 3, 'wrong': 0},
                                          445: {'right': 3, 'wrong': 0},
                                          607: {'right': 3, 'wrong': 0},
                                          608: {'right': 3, 'wrong': 0},
                                          609: {'right': 3, 'wrong': 0},
                                          610: {'right': 3, 'wrong': 0},
                                          611: {'right': 3, 'wrong': 0},
                                          612: {'right': 3, 'wrong': 0},
                                          613: {'right': 3, 'wrong': 0},
                                          614: {'right': 3, 'wrong': 0},
                                          615: {'right': 3, 'wrong': 0},
                                          616: {'right': 3, 'wrong': 0},
                                          617: {'right': 3, 'wrong': 0},
                                          618: {'right': 3, 'wrong': 0},
                                          619: {'right': 3, 'wrong': 0},
                                          620: {'right': 3, 'wrong': 0},
                                          621: {'right': 3, 'wrong': 0},
                                          622: {'right': 3, 'wrong': 0},
                                          623: {'right': 3, 'wrong': 0},
                                          624: {'right': 3, 'wrong': 0},
                                          625: {'right': 3, 'wrong': 0},
                                          626: {'right': 3, 'wrong': 0},
                                          627: {'right': 3, 'wrong': 0},
                                          628: {'right': 3, 'wrong': 0},
                                          629: {'right': 3, 'wrong': 0},
                                          630: {'right': 3, 'wrong': 0},
                                          631: {'right': 3, 'wrong': 0},
                                          632: {'right': 3, 'wrong': 0},
                                          633: {'right': 3, 'wrong': 0},
                                          634: {'right': 3, 'wrong': 0},
                                          635: {'right': 3, 'wrong': 0},
                                          636: {'right': 3, 'wrong': 0},
                                          637: {'right': 3, 'wrong': 0},
                                          638: {'right': 3, 'wrong': 0},
                                          639: {'right': 3, 'wrong': 0},
                                          640: {'right': 3, 'wrong': 0},
                                          641: {'right': 3, 'wrong': 0},
                                          642: {'right': 3, 'wrong': 0},
                                          643: {'right': 3, 'wrong': 0},
                                          644: {'right': 3, 'wrong': 0},
                                          645: {'right': 3, 'wrong': 0},
                                          646: {'right': 3, 'wrong': 0},
                                          647: {'right': 3, 'wrong': 0},
                                          648: {'right': 3, 'wrong': 0},
                                          1: {'right': 3, 'wrong': 0},
                                          2: {'right': 3, 'wrong': 0},
                                          3: {'right': 3, 'wrong': 0},
                                          5: {'right': 3, 'wrong': 0},
                                          8: {'right': 3, 'wrong': 0},
                                          63: {'right': 3, 'wrong': 0},
                                          95: {'right': 3, 'wrong': 0},
                                          96: {'right': 3, 'wrong': 0},
                                          99: {'right': 3, 'wrong': 0},
                                          102: {'right': 3, 'wrong': 0},
                                          256: {'right': 3, 'wrong': 0},
                                          422: {'right': 3, 'wrong': 0}
                                          }
                                },  # last row is cat2 [61]
                               {'latest_new': 2,
                                 'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                 'cat3': [], 'cat4': [],
                                 'rev1': [6, 29, 62, 82, 83], 'rev2': [61],
                                 'rev3': [], 'rev4': []},
                                {1: False, 2: False},
                                'repeated'
                               ),
                              ])
    def test_pathchooser_choose(self, locid, completed, tpout, redirect,
                                mode, db):
        """
        Unit test for the paideia.Pathchooser.choose() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        print 'starting choose'
        actual, newloc, catnum, actualmode = chooser.choose()
        print 'ended choose'

        # get expected paths from supplied tags
        mycat = 'cat{}'.format(catnum)
        print 'tags to be used used'
        print tpout[mycat]
        print 'taggedsteps'
        taggedsteps = db(db.steps.tags.contains(tpout[mycat])).select()
        stepids = [s.id for s in taggedsteps]
        print sorted(stepids)
        print 'taggedpaths'
        allpaths = db(db.paths.id > 0).select()
        taggedpaths = allpaths.find(lambda r: any(i for i in stepids if i in r.steps))
        #taggedpaths = db(db.paths.steps.contains(stepids)).select()
        taggedids = [p.id for p in taggedpaths]
        print sorted(taggedids)
        if any(i for i in taggedids if i not in completed['paths'].keys()):
            print 'new path expected'
            expected = taggedids
        else:  # supposed to choose from paths with fewest repeats
            print 'repeat expected'
            print 'finding expected paths with fewest repeats'
            completed_freq = {i: (f['right'] + f['wrong'])
                            for i, f in completed['paths'].iteritems()}
            completed_freq_cat = {i: f for i, f in completed_freq.iteritems()
                                  if i in taggedids}
            print 'path repeats for category'
            print pprint(completed_freq_cat)
            min_freq = min(set(f for f in completed_freq_cat.values()))
            print 'min_freq', min_freq
            expected = [i for i in taggedids if completed_freq[i] == min_freq]
        print 'CHOSEN PATH', actual['id']
        print 'using category', catnum
        print 'EXPECTED PATHS', expected

        assert catnum in range(1, 5)
        if catnum in redirect.keys() and redirect[catnum]:  # since different cats will yield different redirect results
            assert newloc
            firststep = actual['steps'][0]
            steplocs = db.steps(firststep).locations
            assert newloc in steplocs
            assert locid not in steplocs
            assert actualmode == 'new_elsewhere'
        else:
            assert actual['id'] in expected
            print 'currently in loc', locid
            pathsteps = [p.steps[0] for p in taggedpaths]
            steplocs = [db.steps(s).locations for s in pathsteps]
            steplocs_chain = list(chain.from_iterable([s for s in steplocs if s]))
            locset = list(set(steplocs_chain))
            print 'path can be begun in locs:', locset
            assert locid in locset
            if mode != 'repeated':  # TODO: when repeating choice doesn't prioritise current loc
                assert newloc is None
        assert actualmode == mode


class TestBugReporter():
    '''
    Unit testing class for the paideia.BugReporter class.
    '''

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('record_id,path_id,step_id,score,response_string,'
                             'loc_id',
                             [(22,  # record_id
                               4,  # 'path_id':
                               108,  # 'step_id':
                               0.5,  # 'score':
                               'hi',  # 'response_string':
                               8)  # 'loc_id':
                              ])
    def test_bugreporter_get_reporter(self, record_id, path_id, step_id, score,
                                      response_string, loc_id):
        """
        Unit test for BugReporter.get_reporter() method.
        """
        xpct = ['<a class="bug_reporter" data-keyboard="data-keyboard" '
                'data-target="#bug_reporter_modal" '
                'data-toggle="modal" '
                'href="#bug_reporter_modal" '
                'id="bug_reporter_modal_trigger">Something wrong?</a>'
                '<div aria-hidden="true" '
                'aria-labelledby="bug_reporter_modal_trigger" '
                'class="modal fade " data-keyboard="true" '
                'id="bug_reporter_modal" '
                'role="dialog" tabindex="-1">'
                '<div class="modal-dialog modal-lg">'
                '<div class="modal-content">'
                '<div class="modal-header">'
                '<h3 class="modal-title" id="myModalLabel">'
                'Did you run into a problem?</h3>'
                '</div>'
                '<div class="modal-body ">'
                '<p>Think your answer should have been correct? '
                '<a class="bug_reporter_link btn btn-danger" '
                'data-w2p_disable_with="default" data-w2p_method="GET" '
                'data-w2p_target="bug_reporter" href="/paideia/creating/bug.'
                'load?'
                'answer={}'
                '&amp;bug_step_id={}'
                '&amp;loc_id={}'
                '&amp;log_id={}'
                '&amp;path_id={}'
                '&amp;score={}'
                '">click here<i class="icon-bug"></i></a> '
                'to submit a bug report. You can read your instructor&#x27;s '
                'response later in the &quot;bug reports&quot; tab of your user '
                'profile.</p>'
                '</div>'
                '<div class="modal-footer">'
                '<button aria-hidden="true" class="pull-right" '
                'data-dismiss="modal" type="button">Close</button>'
                '</div>'
                '</div>'
                '</div>'
                '</div>'.format(response_string, step_id, loc_id, record_id,
                                path_id, score)]

        actual = BugReporter().get_reporter(record_id, path_id, step_id,
                                            score, response_string, loc_id)

        print 'actual---------------'
        print actual
        print 'expected------------------'
        print xpct[0]

        assert actual.xml() == xpct[0]
