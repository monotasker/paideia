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
from random import randint
from copy import copy
from dateutil import parser


# ===================================================================
# Switches governing which tests to run
# ===================================================================
global_runall = True
global_run_TestNpc = False
global_run_TestLocation = False
global_run_TestStep = False
global_run_TestStepEvaluator = False
global_run_TestMultipleEvaluator = False
global_run_TestPath = False
global_run_TestUser = True
global_run_TestCategorizer = False
global_run_TestMap = False
global_run_TestWalk = False
global_run_TestPathChooser = False
global_run_TestBugReporter = False

# ===================================================================
# Test Fixtures
# ===================================================================


def dt(string):
    """Return datetime object parsed from the string argument supplied"""
    format = "%Y-%m-%d"
    return datetime.datetime.strptime(string, format)


@pytest.fixture
def mytagpros():
    """A fixture providing mock tag_progress records"""
    tp = {'Simon Pan 2014-03-21': {'latest_new': 10,
                                   'name': 109,
                                   'id': 303,
                                   'cat1': [128, 129, 2, 131, 4, 133, 6, 135, 9,
                                           10, 130, 16, 17, 132, 30, 5, 36, 134,
                                           43, 46, 48, 55, 61, 62, 63, 66, 67,
                                           69, 71, 72, 73, 74, 76, 77, 82, 83,
                                           84, 85, 86, 87, 88, 90, 91, 93, 94,
                                           95, 96, 102, 103, 104, 115, 117, 118,
                                           121, 124],
                                   'cat2': [],
                                   'cat3': [14],
                                   'cat4': [68, 38, 75, 47, 49, 18, 116, 119,
                                           120, 89, 122, 92, 29],
                                   'rev1': [],
                                   'rev3': [],
                                   'rev2': [],
                                   'rev4': []},
          }
    return tp


@pytest.fixture
def mypromotions():
    """docstring for mypromotions"""
    prom = {'Simon Pan 2014-03-21':
            [{'name': 109L,
              'tag': 4L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 606L},
             {'name': 109L,
              'tag': 46L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 607L},
             {'name': 109L,
              'tag': 47L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 608L},
             {'name': 109L,
              'tag': 69L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 609L},
             {'name': 109L,
              'tag': 95L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 610L},
             {'name': 109L,
              'tag': 117L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 611L},
             {'name': 109L,
              'tag': 118L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 612L},
             {'name': 109L,
              'tag': 119L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 613L},
             {'name': 109L,
              'cat1': datetime.datetime(2013, 10, 3, 21, 16, 29),
              'cat2': None,
              'tag': 120L,
              'cat4': None,
              'cat3': None,
              'id': 614L},
             {'name': 109L,
              'tag': 2L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 703L},
             {'name': 109L,
              'tag': 10L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 704L},
             {'name': 109L,
              'tag': 18L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 705L},
             {'name': 109L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'tag': 30L,
              'cat4': None,
              'cat3': None,
              'id': 706L},
             {'name': 109L,
              'tag': 38L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 707L},
             {'name': 109L,
              'tag': 49L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 708L},
             {'name': 109L,
              'tag': 55L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 709L},
             {'name': 109L,
              'tag': 86L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 710L},
             {'name': 109L,
              'tag': 87L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 711L},
             {'name': 109L,
              'tag': 121L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 712L},
             {'name': 109L,
              'tag': 122L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 713L},
             {'name': 109L,
              'tag': 128L,
              'cat1': datetime.datetime(2013, 10, 5, 3, 6, 25),
              'cat2': None,
              'cat4': None,
              'cat3': None,
              'id': 714L}
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
            'secondary_right': ['2014-03-20 01:21:42.738633'],
            'step': None,
            'times_right': 8.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 1, 15, 32, 1)
            },
           {'id': 383615L, 'in_path': None,
            'tag': 4L,
            'name': 109L,
            'secondary_right': ['2014-03-20 00:46:03.191941',
                                '2014-03-20 01:19:00.049401'],
            'step': None,
            'tag': 2L,
            'times_right': 2.0,
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
            'secondary_right': ['2014-03-05 22:27:29.538283',
                                '2014-03-20 01:20:07.234653'],
            'step': None,
            'times_right': 1.0,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2014, 3, 5, 4, 23, 58, 481824),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 383119L,
            'tag': 9L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:27:31.974083'],
            'step': None,
            'times_right': 2.0,
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
            'secondary_right': [],
            'step': None,
            'times_right': 4.0,
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
            'secondary_right': ['2014-02-12 21:33:08.570055',
                                '2014-02-20 23:05:57.762133'],
            'step': None,
            'times_right': 34.0,
            'times_wrong': 10.0,
            'tlast_right': datetime.datetime(2014, 2, 11, 2, 53, 27),
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 37, 10)},
           {'id': 383614L,
            'tag': 30L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847'],
            'step': None,
            'times_right': 7.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383478L,
            'tag': 32L,
            'in_path': None,
            'name': 109L,
            'secondary_right': [],
            'step': None,
            'times_right': 1.0,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2013, 12, 18, 6, 13, 52, 945160),
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
            'secondary_right': ['2014-03-20 01:13:10.776062'],
            'step': None,
            'times_right': 8.0,
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
            'secondary_right': [],
            'step': None,
            'times_right': 5.0,
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
            'secondary_right': [],
            'step': None,
            'times_right': 6.0,
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
            'secondary_right': [],
            'step': None,
            'times_right': 7.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 48, 55)},
           {'id': 383217L,
            'tag': 62L,
            'in_path': None,
            'name': 109L,
            'secondary_right': [],
            'step': None,
            'times_right': 7.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 26, 42),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 13, 58, 40)},
           {'id': 383109L,
            'tag': 63L,
            'in_path': None,
            'name': 109L,
            'secondary_right': [],
            'step': None,
            'times_right': 6.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 26, 21),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 45, 36)},
           {'id': 383234L,
            'tag': 66L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:15:26.002995',
                                '2014-03-20 01:20:07.213051'],
            'step': None,
            'times_right': 2.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 43, 27)},
           {'id': 383117L,
            'tag': 67L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:27:31.971359'],
            'step': None,
            'times_right': 2.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383108L,
            'tag': 68L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 00:41:36.541744'],
            'step': None,
            'times_right': 78.0,
            'times_wrong': 30.0,
            'tlast_right': datetime.datetime(2014, 3, 13, 20, 25, 8, 293723),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 45, 15)},
           {'id': 383543L,
            'tag': 69L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-17 22:29:32.526147',
                                '2014-03-20 01:13:10.801349'],
            'step': None,
            'times_right': 1.0,
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
            'secondary_right': ['2014-03-20 01:11:17.566601',
                                '2014-03-20 01:13:10.804879'],
            'step': None,
            'times_right': 4.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 28, 36),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 53, 45)},
           {'id': 383114L,
            'tag': 73L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-22 03:10:16.568678',
                                '2014-02-22 03:10:31.175847'],
            'step': None,
            'times_right': 2.0,
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
            'secondary_right': ['2014-02-25 01:11:45.086382',
                                '2014-03-20 01:20:07.227347'],
            'step': None,
            'times_right': 1002.0,
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
            'secondary_right': ['2014-03-20 01:22:45.999836'],
            'step': None,
            'times_right': 6.0,
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36)},
           {'id': 383220L,
            'tag': 82L,
            'in_path': None,
            'name': 109L,
            'secondary_right': [],
            'step': None,
            'times_right': 2.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 8, 27)},
           {'id': 383221L,
            'tag': 83L,
            'in_path': None,
            'name': 109L,
            'secondary_right': [],
            'step': None,
            'times_right': 6.0,
            'times_wrong': None,
            'tlast_right': datetime.datetime(2014, 2, 28, 20, 35, 41, 971118),
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
            'secondary_right': [],
            'step': None,
            'times_right': 2.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 3, 6, 26)},
           {'id': 383637L,
            'tag': 87L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-02-04 15:02:23.598612',
                                '2014-02-07 18:34:16.086847'],
            'step': None,
            'times_right': 7.0,
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 26),
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 12, 17)},
           {'id': 383118L,
            'tag': 88L,
            'in_path': None,
            'name': 109L,
            'secondary_right': ['2014-03-20 01:15:26.013721'],
            'step': None,
            'times_right': 4.0,
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
            'times_right': 2.0,
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'step': None,
            'in_path': None,
            'name': 109L,
            'secondary_right': []},
           {'name': 109L,
            'tag': 91L,
            'times_right': 5.0,
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 5, 35),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 18, 26),
            'step': None,
            'in_path': None,
            'id': 383218L,
            'secondary_right': ['2014-03-13 19:52:16.747902']},
           {'name': 109L,
            'tag': 92L,
            'times_right': 1001.0,
            'tlast_wrong': datetime.datetime(2013, 9, 27, 14, 50, 13),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 5, 4, 24, 12),
            'step': None,
            'in_path': None,
            'id': 383237L,
            'secondary_right': ['2014-03-10 19:14:58.914173']},
           {'name': 109L,
            'tag': 93L,
            'times_right': 2.0,
            'tlast_wrong': datetime.datetime(2013, 9, 30, 13, 39, 50),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 24, 41),
            'step': None,
            'in_path': None,
            'id': 383346L,
            'secondary_right': []},
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
            'times_right': 4.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 34, 49),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'step': None,
            'in_path': None,
            'id': 383545L,
            'secondary_right': ['2014-01-20 14:29:24.439739']},
           {'name': 109L,
            'tag': 115L,
            'times_right': 7.0,
            'tlast_wrong': datetime.datetime(2013, 9, 26, 20, 57, 36),
            'times_wrong': 0.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 27, 31),
            'step': None,
            'in_path': None,
            'id': 383120L,
            'secondary_right': ['2014-03-20 01:20:07.248791']},
           {'name': 109L,
            'tag': 116L,
            'times_right': 1001.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 10, 18, 58, 17),
            'step': None,
            'in_path': None,
            'id': 383412L,
            'secondary_right': []},
           {'name': 109L,
            'tag': 117L,
            'times_right': 3.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 8, 41),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 25, 25),
            'step': None,
            'in_path': None,
            'id': 383413L,
            'secondary_right': ['2014-03-20 00:45:07.186095']},
           {'name': 109L,
            'tag': 118L,
            'times_right': 2.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 19, 34),
            'times_wrong': 1.0,
            'tlast_right': datetime.datetime(2014, 3, 20, 1, 20, 7),
            'step': None,
            'in_path': None,
            'id': 383544L,
            'secondary_right': []},
           {'name': 109L,
            'tag': 119L,
            'times_right': 1007.0,
            'tlast_wrong': datetime.datetime(2013, 10, 3, 21, 13),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 2, 25, 21, 51, 13),
            'step': None,
            'in_path': None,
            'id': 383541L,
            'secondary_right': ['2014-03-20 01:15:26.017334']},
           {'name': 109L,
            'tag': 120L,
            'times_right': 1002.0,
            'tlast_wrong': datetime.datetime(2013, 10, 1, 21, 11, 43),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 7, 19, 29, 37),
            'step': None,
            'in_path': None,
            'id': 383415L,
            'secondary_right': ['2014-01-20 14:29:24.439739']},
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
            'times_right': 1001.0,
            'tlast_wrong': datetime.datetime(2013, 10, 5, 20, 7, 46),
            'times_wrong': 1000.0,
            'tlast_right': datetime.datetime(2014, 3, 17, 22, 29, 3),
            'step': None,
            'in_path': None,
            'id': 383636L,
            'secondary_right': []},
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
          '</tr></table></form>',
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
          '</tr></table></form>',
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
          '</tr></table></form>',
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
          '</label></td><td class="w2p_fw"><table class="generic-widget" '
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
          '<div>Congratulations, Homer! \n\n'  # prompt text
          'You have been promoted to these new badge levels:\r\n'
          '- apprentice alphabet basics\r\n'
          'and you&#x27;re ready to start working on some new badges:\r\n'
          '- beginner alphabet (intermediate)\r\n'
          'You can click on your name above to see details '
          'of your progress so far.</div>',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          {'new_tags': [62], 'promoted': {'cat2': [61]}},  # kwargs
          ),  # promoted, no new tags (for new badges)
         ('case3', 126,  # StepAwardBadges ------------------------------
          'synagogue',
          [31, 32],  # npcs here
          '<div>Congratulations, Homer! \n\n'  # prompt text
          'You have been promoted to these new badge levels:\r\n'
          '- apprentice alphabet basics\r\n'
          'You can click on your name above to see details '
          'of your progress so far.</div>',
          None,   # instructions
          None,   # slide decks
          None,   # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          {'promoted': {'cat2': [61]}},  # kwargs
          ),  # promoted, no new tags (for new badges)
         ('case2', 127,  # StepViewSlides ------------------------------
          'agora',
          [1, 14, 17, 21, 40, 41, 42],  # npcs here
          '<div>Take some time now to review these new slide '
          'sets. They will help with work on your new badges:\n'
          '<ul class="slide_list">'
          '<li><a data-w2p_disable_with="default" href="/paideia/'
          'listing/slides.html/3">The Alphabet II</a></li>'
          '<li><a data-w2p_disable_with="default" href="/paideia/'
          'listing/slides.html/8">Greek Words II</a></li></ul></div>',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map'],  # response buttons
          None,  # response form
          {'new_tags': [62]},  # kwargs
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
            assert re.match(rform, actual['response_form'].xml())
        elif rform:
            pprint(actual['response_form'])
            assert actual['response_form']
        assert actual['bugreporter'] == None
        assert actual['response_buttons'] == rbuttons
        assert actual['audio'] == None  # FIXME: add case with audio (path 380, step 445)
        assert actual['loc'] == alias

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize(('caseid', 'stepid'), [
        ('case1', 1),
        ('case2', 2),  # don't use steps 30, 125, 126, 127 (block)
        ('case2', 101)
    ])
    def test_step_make_replacements(self, caseid, db, stepid, mysteps, user_login):
        """Unit test for method Step._make_replacements()"""
        step, sdata = mystep(stepid, mysteps)
        case = mycases(caseid, user_login, db)
        oargs = {'raw_prompt': sdata['raw_prompt'],
                 'username': case['name'],
                 'next_loc': case['next_loc'],
                 'new_tags': case['new_badges'],
                 'promoted': case['promoted']
                 }
        ofinal = sdata['final_prompt']
        ofinal = ofinal.replace('[[user]]', oargs['username'])
        if isinstance(step, StepAwardBadges):
            oargs['new_badges'] = case['new_badges']
        elif isinstance(step, StepViewSlides):
            oargs['new_badges'] = case['new_badges']

        assert step._make_replacements(**oargs) == ofinal

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize(('caseid', 'stepid'), [
        ('case1', 1),
        ('case2', 2)
    ])
    def test_step_get_npc(self, caseid, stepid, db, mysteps,
                          user_login, npc_data):
        """Test for method Step.get_npc"""
        # TODO: make sure the npc really is randomized
        case = mycases(caseid, user_login, db)
        step, expected = mystep(stepid, mysteps)
        actual = step.get_npc(case['loc'])

        assert actual.get_id() in expected['npc_list']
        # make sure this npc has the right name for its id
        assert actual.get_name() == npc_data[actual.get_id()]['name']
        assert actual.get_image().xml() == IMG(_src=npc_data[actual.get_id()]['image']).xml()
        locs = actual.get_locations()
        # make sure there is common location shared by actual npc and step
        assert [l for l in locs
                if l in expected['locations']]
        for l in locs:
            assert isinstance(l, (int, long))
            assert l in npc_data[actual.get_id()]['location']

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('stepid', [1, 2])
    def test_step_get_instructions(self, stepid, mysteps):
        """Test for method Step._get_instructions"""
        step, expected = mystep(stepid, mysteps)
        actual = step._get_instructions()
        assert actual == expected['instructions']

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('stepid', [1, 2, 19])  # only StepText type
    def test_step_get_readable(self, stepid, mysteps):
        """Unit tests for StepText._get_readable() method"""
        step, expected = mystep(stepid, mysteps)
        assert step._get_readable() == expected['readable']

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('caseid,stepid',
                             [('case1', 1),
                              ('case2', 2),
                              ('case2', 101)
                              ])  # only StepText and StepMultiple types
    def test_step_get_reply(self, stepid, caseid, mysteps, user_login,
                            db, npc_data):
        """Unit tests for StepText._get_reply() method"""
        case = mycases(caseid, user_login, db)
        step, expected = mystep(stepid, mysteps)
        step.loc = case['loc']
        locnpcs = [int(n) for n in case['npcs_here']
                   if n in expected['npc_list']]
        step.npc = Npc(locnpcs[0], db)

        for x in [('correct', 1),
                  ('incorrect', 0)]:

            actual = step.get_reply(expected['user_responses'][x[0]])

            # assemble reply text (tricky)
            xtextraw = expected['reply_text'][x[0]]
            xtext = xtextraw.replace('[[resp]]',
                                     expected['user_responses'][x[0]])
            rdbl = ''
            print len(expected['readable']['readable_short'])
            if len(expected['readable']['readable_short']) > 1:  #
                for r in expected['readable']['readable_short']:
                    rdbl += '\n- {}'.format(r)
            elif x[1] != 1:
                rdbl += '\n- {}'.format(expected['readable']['readable_short'][0])
            xtext = xtext.replace('[[rdbl]]', rdbl)

            assert actual['sid'] == stepid
            assert actual['bg_image'] == case['loc'].get_bg()
            assert actual['prompt_text'] == xtext
            assert actual['readable_long'] == expected['readable']['readable_long']
            assert actual['npc_image']['_src'] == npc_data[locnpcs[0]]['image']
            assert actual['audio'] is None
            assert actual['widget_img'] is None
            assert actual['instructions'] == expected['instructions']
            assert actual['slidedecks'] == expected['slidedecks']
            assert actual['hints'] == expected['tips']

            assert actual['user_response'] == expected['user_responses'][x[0]]
            assert actual['score'] == x[1]
            assert actual['times_right'] == x[1]
            assert actual['times_wrong'] == abs(x[1] - 1)


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
    def test_path_get_id(self, pathid, db):
        """unit test for Path.get_id()"""
        path, pathsteps = mypath(pathid, db)
        assert path.get_id() == int(pathid)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('pathid,firststep,stepsleft',
                             [(3, 2, []),
                              (89, 101, []),
                              (19, 19, []),
                              (1, 71, []),
                              (63, 66, [67, 68])])
    def test_path_prepare_for_prompt(self, pathid, firststep, stepsleft, db):
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
                                      stepid, stepsleft, locs, db, mysteps):
        """
        Unit test for Path.get_step_for_prompt() where no redirect prompted.
        """
        # TODO: test edge cases with, e.g., repeat set
        # TODO: test middle of multi-step path
        path, pathsteps = mypath(pathid, db)
        actual, nextloc = path.get_step_for_prompt(Location(localias))

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

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'casenum,locid,localias,pathid,stepid,stepsleft,locs',
        [('case1', 6, 'shop_of_alexander', 3, 2, [], [3, 1, 13, 7, 8, 11]),
         ('case2', 8, 'agora', 89, 101, [], [7])
         ])
    def test_path_get_step_for_prompt_redirect(self, casenum, locid, localias,
                                               pathid, stepid, stepsleft, locs,
                                               db, mysteps):
        """
        Unit test for Path.get_step_for_prompt() in a case that prompts redirect.
        """
        # TODO: redirect can be caused by 2 situations: bad loc or wrong npcs
        # here
        path, pathsteps = mypath(pathid, db)
        actual, nextloc = path.get_step_for_prompt(Location(localias))

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

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'pathid,steps',
        [(3, [2]),
         (89, [101]),
         (19, [19]),
         (1, [71]),
         (63, [66, 67, 68])
         ])
    def test_path_get_steps(self, pathid, steps, mysteps, db):
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
         #(63, 66, [67, 68], [3, 1], 'domus_A')  # first step doesn't take reply
         ])
    def test_path_get_step_for_reply(self, pathid, stepid, stepsleft, locs,
                                     localias, db):
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

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('locid,completed,tpout,trecs,redirect,expected',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               [2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256, 40,
                                9, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                                419, 420, 421, 422, 423, 444, 445],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
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
                               False,
                               [1]  # only one left with tag
                               ),
                              (11,  # synagogue [all in loc 11 completed]
                               [1, 2, 3, 8, 95, 96, 97, 99, 102],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 20,
                                 'times_wrong': 10,
                                 'secondary_right': []}],
                                True,
                                [99, 97, 102, 2, 1, 3, 95, 8, 96]
                               ),
                              #(8,  # agora (no redirect, new here)
                               #[17, 98, 15, 208, 12, 16, 34, 11, 23, 4, 9, 18],
                               #{'latest_new': 2,
                                #'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                #'cat3': [], 'cat4': [],
                                #'rev1': [], 'rev2': [61],
                                #'rev3': [], 'rev4': []},
                                #False,
                               #[7, 14, 100, 35, 19, 103, 21, 97, 13, 261, 101]
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
    def test_user_get_path(self, locid, completed, tpout, trecs,
                           redirect, expected, db):
        """
        Unit testing method for User.get_path().
        """
        userdata = {'first_name': 'Homer',
                    'id': 1,
                    'time_zone': 'America/Toronto'}
        user = User(userdata, trecs, tpout)
        actual, acat, aredir, apastq = user.get_path(Location(db.locations(locid).loc_alias))
        assert actual.get_id() in expected
        assert isinstance(actual, Path)
        assert isinstance(actual.steps[0], Step)
        assert acat in range(1, 5)
        assert aredir is None
        assert apastq is None

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('tpin,rankout,tpout,trecs,counter,promoted,newtags',
        [({'latest_new': 1,  # tpin =========================================
           'cat1': [1], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          1,  # rank out
          {'latest_new': 1,  # tpout
           'cat1': [6, 29, 62, 82, 83], 'cat2': [],  # FIXME: this is wrong
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          4,
          None,
          [6, 29, 62, 82, 83]
          ),
         ({'latest_new': 1,  # tpin =========================================
           'cat1': [1], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          1,  # rank out
          {'latest_new': 1,  # tpout
           'cat1': [1], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          3,
          None,
          None
          )
         ])
    def test_user_get_categories(self, tpin, rankout, tpout, trecs, counter,
                                 promoted, newtags, user_login, db):
        """
        Unit test for User._get_categories() method.
        """
        user = User(user_login, trecs, tpin)
        user.cats_counter = counter
        try:
            db.tag_progress(db.tag_progress.name == user_login['id']).id
        except AttributeError:
            db.tag_progress.insert(name=user_login['id'])
        # set these to allow for retrieval if counter < 5
        user.tag_progress = tpin
        user.categories = {c: l for c, l in tpin.iteritems() if c[:3] == 'cat'}
        apromoted, anew_tags = user.get_categories()

        print 'user.tag_progress'
        print user.cats_counter
        print 'user.tag_progress'
        pprint(user.tag_progress)
        print 'user.categories'
        pprint(user.categories)

        for c, l in tpout.iteritems():
            assert user.tag_progress[c] == l
            if c in ['cat1', 'cat2', 'cat3', 'cat4']:
                assert user.categories[c] == l
        assert apromoted == promoted
        assert anew_tags == newtags

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

        assert user.complete_path()

        assert user.path is None
        assert user.completed_paths[-1] == pathid  # FIXME: store obj instead of just id?
        #assert isinstance(user.completed_paths[-1], Path)
        #assert user.completed_paths[-1].steps == []


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
                               mytagpros()['Simon Pan 2014-03-21'],
                               mytagrecs()['Simon Pan 2014-03-21'],
                               mytagrecs_with_secondary()['Simon Pan 2014-03-21'])
                              ])
    def test_categorizer_add_secondary_right(self, casename, rank, catsin,
                                             tagrecsin, tagrecsout, mytagpros,
                                             mytagrecs):
        """Unit test for the paideia.Categorizer._add_secondary_right method."""
        now = dt('2013-01-29')
        # 150 is random user id
        catzr = Categorizer(rank, catsin, tagrecsin, 150, utcnow=now)

        actual = catzr._add_secondary_right(tagrecsin)
        expected = tagrecsout

        for idx, a in enumerate(actual):
            e = expected[idx]
            esr = [parser.parse(d) for d in e['secondary_right']] \
                   if e['secondary_right'] else None
            print 'trying tag', a['tag']
            assert a['tag'] == e['tag']
            assert a['tlast_right'] == e['tlast_right']
            assert a['tlast_wrong'] == e['tlast_wrong']
            assert a['times_right'] == e['times_right']
            assert a['tlast_wrong'] == e['tlast_wrong']
            try:
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
                                'cat3': [], 'cat4': []},
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
                                'cat3': [], 'cat4': []},
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
                                'cat3': [], 'cat4': []},
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
                                'cat3': [], 'cat4': []},
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
                                'cat3': [], 'cat4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 20,
                                 'times_wrong': 10,
                                 'secondary_right': []}],
                               )
                              ])
    def test_categorizer_core_algorithm(self, casename, rank, catsin, catsout,
                                        tagrecs, db):
        """
        Unit test for the paideia.Categorizer._core_algorithm method

        Case numbers correspond to the cases (user performance scenarios) set
        out in the myrecords fixture.
        """
        now = dt('2013-01-29')
        # 150 is random user id
        catzr = Categorizer(rank, catsin, tagrecs, 150, utcnow=now)

        actual = catzr._core_algorithm()
        expected = catsout
        assert actual == expected

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecs,introduced',
                             [('case1',  # ???
                               1,
                               {'cat1': [1], 'cat2': [],
                                'cat3': [], 'cat4': []},
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
                                'cat3': [], 'cat4': []},
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

        assert actual == expected
        assert len(actual) == len(expected)
        assert catzr.rank == rank + 1

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecs,catsout',
                             [('case1', 1, {'cat1': [1], 'cat2': [],
                                            'cat3': [], 'cat4': []},
                               [{'name': 1,
                                 'tag': 1,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-29'),
                                 'times_right': 1,
                                 'times_wrong': 1,
                                 'secondary_right': None}],
                               {'cat1': [1, 61], 'cat2': [],
                                'cat3': [], 'cat4': []}
                               )
                              ])
    def test_categorizer_add_untried_tags(self,  casename, rank, catsin,
                                          tagrecs, catsout):
        """
            Unit test for the paideia.Categorizer._add_untried_tags method

            catsin is the output from _core_algorithm()
            catsout should have untried tags at the user's current rank added
            to cat1.

        """
        now = dt('2013-01-29')
        catzr = Categorizer(rank, catsin, tagrecs, 150, utcnow=now)

        actual = catzr._add_untried_tags(catsin)
        expected = catsout

        for cat, lst in actual.iteritems():
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
    @pytest.mark.parametrize('casename,rank,oldcats,catsin,tagrecs,'
                             'demoted,promoted',
                             [('case1',  # no prom or demot
                               1,
                               {'cat1': [1], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [61], 'cat2': [],
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
                               None,
                               None
                               ),
                              ('case2',  # promote 61 for ratio and time
                               1,
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'cat1': [62], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-29'),
                                 'tlast_wrong': dt('2013-01-28'),
                                 'times_right': 10,
                                 'times_wrong': 2,
                                 'secondary_right': []}],
                               None,
                               {'cat1': [], 'cat2': [61],
                                'cat3': [], 'cat4': []}
                               )
                              ])
    def test_categorizer_find_cat_changes(self, casename, rank, oldcats, catsin,
                                          tagrecs, demoted, promoted):
        """
            Unit test for the paideia.Categorizer._find_cat_changes method.

        """
        now = dt('2013-01-29')
        catzr = Categorizer(rank, oldcats, tagrecs, 150, utcnow=now)

        actual = catzr._find_cat_changes(catsin, oldcats)
        expected = {'categories': catsin,
                    'demoted': demoted,
                    'promoted': promoted}

        for cat, lst in actual['categories'].iteritems():
            assert lst == expected['categories'][cat]
        assert actual['demoted'] == expected['demoted']
        assert actual['promoted'] == expected['promoted']

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('casename,rank,catsin,tagrecsin,'
                             'rankout,catsout,tpout,'
                             'promoted,newtags',
                             [('case1',
                               1,
                               {'cat1': [1], 'cat2': [],
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
                               1,  # case1 out
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               None,
                               None
                               ),
                              ('case2',  # promote 61, introduce 62
                               1,
                               {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [{'name': 1,
                                 'tag': 61,
                                 'tlast_right': dt('2013-01-28'),
                                 'tlast_wrong': dt('2013-01-27'),
                                 'times_right': 20,
                                 'times_wrong': 1,
                                 'secondary_right': []}],
                               2,
                               {'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               {'cat1': [], 'cat2': [61],
                                'cat3': [], 'cat4': []},
                               [6, 29, 62, 82, 83]
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
        pprint(actual)

        for key, act in actual['categories'].iteritems():
            print key
            assert act == expected['cats'][key]

        for key, act in actual['tag_progress'].iteritems():
            assert act == expected['t_prog'][key]

        assert actual['new_tags'] == expected['nt']
        if actual['new_tags']:
            assert actual['tag_progress']['cat1'] == expected['nt']

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
            i = expected['locations'].index(m)
            assert actual['locations'][i]['loc_alias'] == m['loc_alias']
            assert actual['locations'][i]['bg_image'] == m['bg_image']
            assert actual['locations'][i]['id'] == m['id']
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
    def test_walk_get_user(self, alias, trecs, tpout, db):
        """Unit test for paideia.Walk._get_user()"""
        userdata = {'first_name': 'Homer', 'id': 1, 'time_zone': 'America/Toronto'}
        thiswalk = Walk(userdata=userdata,
                        tag_records=trecs,
                        tag_progress=tpout,
                        db=db)
        actual = thiswalk._get_user(userdata=userdata,
                                    tag_records=trecs,
                                    tag_progress=tpout)

        assert isinstance(actual, User)
        assert actual.get_id() == userdata['id']

    @pytest.mark.parametrize('pathid,stepid,alias,npcshere,trecs,tpout,redir,'
                             'promptext,instrs,slidedecks,widgimg,rbuttons,'
                             'rform,replystep',
        [(19,  # path # case3 ======================================================
          19,  # step
          'synagogue',  # alias
          [1],  # npcs here FIXME
          [{'name': 1,  # trecs
            'tag': 61,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-21'),
            'times_right': 10,
            'times_wrong': 10,
            'secondary_right': None},
           {'name': 1,
            'tag': 62,
            'tlast_right': dt('2013-01-10'),
            'tlast_wrong': dt('2013-01-1'),
            'times_right': 10,
            'times_wrong': 0,
            'secondary_right': None},
           {'name': 1,
            'tag': 63,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-21'),
            'times_right': 9,
            'times_wrong': 0,
            'secondary_right': None},
           {'name': 1,
            'tag': 66,
            'tlast_right': dt('2013-01-27'),
            'tlast_wrong': dt('2013-01-21'),
            'times_right': 10,
            'times_wrong': 0,
            'secondary_right': None}
           ],
          {'latest_new': 4,  # tpout
           'cat1': [62, 63, 68, 115, 72, 89, 36],
           'cat2': [61, 66],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
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
          '</tr></table></form>',
          True  # replystep
          ),
         (19,  # path # case2 ======================================================
          19,  # step
          'agora',  # alias
          [1],  # npcs here
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
          '</tr></table></form>',
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
          'Hi there. Sorry, I don\'t have anything for you to '  # prompt text
          'do here at the moment. I think someone was looking '
          'for you at somewhere else in town.',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          False  # replystep
          ),
         (2,  # path # case1======================================================
          1,  # step
          'shop_of_alexander',
          [2, 8, 17],  # npcs here (for step)
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          {'latest_new': 1,  # tpout
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          False,  # redirect?
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
          '</tr></table></form>',
          True  # replystep
          ),
         (3,  # path # case1======================================================
          2,  # step
          'shop_of_alexander',
          [2, 8, 17],  # npcs here FIXME
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          {'latest_new': 1,  # tpout
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          False,  # redirect?
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
          '</tr></table></form>',
          True  # replystep
          ),
         (89,  # path # case1======================================================
          101,  # step
          'shop_of_alexander',
          [2, 8, 14, 17, 31, 40, 41, 42],  # npcs here
          [{'name': 1,  # trecs
            'tag': 1,
            'tlast_right': dt('2013-01-29'),
            'tlast_wrong': dt('2013-01-29'),
            'times_right': 1,
            'times_wrong': 1,
            'secondary_right': None}],
          {'latest_new': 1,  # tpout
           'cat1': [61], 'cat2': [],
           'cat3': [], 'cat4': [],
           'rev1': [], 'rev2': [],
           'rev3': [], 'rev4': []},
          True,  # redirect?
          'Hi there. Sorry, I don\'t have anything for you to '  # prompt text
          'do here at the moment. I think someone was looking '
          'for you at somewhere else in town.',
          None,  # instructions
          None,  # slide decks
          None,  # widget image
          ['map', 'continue'],  # response buttons
          None,  # response form
          False  # replystep
          )
         ])
    def test_walk_ask(self, pathid, stepid, alias, npcshere, trecs, tpout, redir,
                      promptext, instrs, slidedecks, widgimg, rbuttons,
                      rform, replystep, npc_data, bg_imgs, db, user_login):
        thiswalk = Walk(userdata=user_login,
                        tag_records=trecs,
                        tag_progress=tpout,
                        db=db)
        loc = Location(alias)
        #path = Path(path_id=pathid, db=db)
        try:  # throws an error if user doesn't have a db.tag_progress row
            db.tag_progress(db.tag_progress.name == user_login['id']).id
        except AttributeError:
            db.tag_progress.insert(name=user_login['id'])
        actual = thiswalk.ask(alias, path=pathid)

        assert actual['sid'] == stepid
        assert actual['pid'] == pathid
        assert actual['completed_count'] == 1
        assert actual['category'] == None
        if not isinstance(actual['prompt_text'], str):
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
        #assert actual['npc_image']['_src'] == npc_data[npc.get_id()]['image']
        if actual['response_form']:
            assert re.match(rform, actual['response_form'].xml())
        elif rform:
            pprint(actual['response_form'])
            assert actual['response_form']
        assert actual['bugreporter'] == None
        assert actual['response_buttons'] == rbuttons
        assert actual['audio'] == None  # FIXME: add case with audio (path 380, step 445)
        assert actual['loc'] == alias
        assert thiswalk.user.path.steps == []  # because only step activated
        assert thiswalk.user.path.step_for_reply == replystep
        assert pathid == thiswalk.user.path.get_id()

    def test_walk_reply(self, mywalk):
        """Unit test for paideia.Walk.reply() method."""
        # TODO: make decorator for test methods to filter specific cases/steps
        # coming from the parameterized fixtures
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        c = case['casenum']
        step = mywalk['stepdata']
        s = step['id']
        combinations = {1: [1, 2],  # path 2, 3  # TODO: handle redirect steps?
                        2: [19],  # path 19
                        3: [19]}  # path 19

        if c in combinations.keys() and s in combinations[c]:
            # test for both a correct and an incorrect response
            path = step['paths'][0]
            for k, v in step['user_responses'].iteritems():
                thestring = re.compile(r'^Incorrect.*', re.U)
                result = thestring.search(step['reply_text'][k])
                if result:
                    score = 0
                    times_right = 0
                    times_wrong = 1
                else:
                    score = 1
                    times_right = 1
                    times_wrong = 0

                response_string = v

                expected = {'reply': step['reply_text'][k],
                            'score': score,
                            'times_right': times_right,
                            'times_wrong': times_wrong}
                            # TODO: put in safety in case of empty form

                thiswalk.ask(path)
                assert path == thiswalk.user.path.get_id()
                # make sure ask() prepared the step for reply
                assert thiswalk.user.path.step_for_reply.get_id() == s
                # TODO: parameterize when multi-step path is tested
                assert thiswalk.user.path.steps == []

                actual = thiswalk.start(response_string, path=path)
                assert actual['reply']['reply_text'] == expected['reply']
                assert actual['reply']['score'] == expected['score']
                assert actual['reply']['times_right'] == expected['times_right']
                assert actual['reply']['times_wrong'] == expected['times_wrong']
                response_string = response_string.decode("utf-8")
                print response_string
                bug_info = (response_string.encode('utf-8'),
                            case['loc'].get_alias(),
                            thiswalk.record_id,
                            thiswalk.user.path.get_id(),
                            expected['score'],
                            s)
                bug_reporter = '<a class="bug_reporter_link" '\
                               'href="/paideia/creating/bug.load?'\
                               'answer={}&amp;'\
                               'loc={}&amp;'\
                               'log_id={}&amp;'\
                               'path={}&amp;'\
                               'score={}&amp;'\
                               'step={}" '\
                               'id="bug_reporter">click here</a>'.format(*bug_info)
                assert actual['bug_reporter'].xml() == bug_reporter
                assert not thiswalk.user.path.step_for_reply
                assert not thiswalk.user.path.step_for_prompt
                assert s == thiswalk.user.path.completed_steps[-1].get_id()
        else:
            pass

    def test_walk_record_cats(self, mywalk, db):
        """
        Unit tests for Walk._record_cats() method.
        """
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        if case['casenum'] == 1:
            tag_progress = case['tag_progress_out']
            user_id = thiswalk._get_user().get_id()
            print 'USER ID'
            print user_id
            promoted = case['promoted']
            new_tags = case['new_badges']
            promoted['cat1'] = new_tags
            promoted = {k: v for k, v in promoted.iteritems() if v}
            expected_progress = copy(tag_progress)
            expected_progress['name'] = user_id
            if promoted:
                print promoted.values()
                expected_begun = {t: cat for cat, lst in promoted.iteritems()
                                for t in lst if lst}
            else:
                expected_begun = None
            # TODO: make sure there's a test that covers some promoted or new
            # tags

            # call the method and test its return value
            thiswalk._record_cats(tag_progress, promoted,
                                  new_tags, db)

            # test record insertion for db.tag_progress
            actual_select_tp = db(db.tag_progress.name == user_id).select()
            assert len(actual_select_tp) == 1

            actual_record_tp = actual_select_tp.first().as_dict()
            for k, v in actual_record_tp.iteritems():
                if k != 'id':
                    assert v == expected_progress[k]

            # test record insertion for db.badges_begun
            actual_select_bb = db(db.badges_begun.name == user_id).select()
            # one badges_begun row for each of user's tag_records rows
            user_tag_records = db(db.tag_records.name == user_id).select()
            assert len(actual_select_bb) == len(user_tag_records)
            # check that new values were entered
            now = datetime.datetime.utcnow()
            if expected_begun:
                print expected_begun
                for t, v in {tag: cat for tag, cat in expected_begun.iteritems()}:
                    actual_select_bb.find(lambda row: row.tag == t)
                    assert len(actual_select_bb) == 1
                    assert actual_select_bb.first()[v] == now
        else:
            print 'skipping combination'
            pass
        # TODO: make sure data is removed from db after test

    def test_walk_record_step(self, mywalk, db):
        """
        Unit test for Paideia.Walk._record_step()

        At present this only runs for case 1, assuming path 3 and step 1.
        """
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        if case['casenum'] == 1:
            user_id = thiswalk._get_user().get_id()
            step_id = 1
            path_id = 3
            score = 1.0
            loglength = len(db(db.attempt_log.name == user_id).select())
            step_tags = [61]  # FIXME: hard coded until I properly parameterize
            response_string = 'blabla'

            expected_tag_records = [t for t in case['tag_records'] if t in step_tags]

            # call the method and collect return value
            actual_log_id = thiswalk._record_step(user_id, path_id, step_id,
                                                  score,
                                                  expected_tag_records,
                                                  response_string)

            # test writing to attempt_log
            logs_out = db(db.attempt_log.name == user_id).select()
            last_log = logs_out.last()
            last_log_id = last_log.id

            assert len(logs_out) == loglength + 1
            assert actual_log_id == last_log_id

            # test writing to tag_records
            actual_tag_records = db(db.tag_records.name == user_id).select()
            assert len(actual_tag_records) == len(expected_tag_records)
            for l in expected_tag_records:
                for_this_tag = actual_tag_records.find(lambda row:
                                                       row.tag == l['tag'])
                assert len(for_this_tag) == 1

                for k in l.keys():
                    assert for_this_tag[k] == l[k]
        else:
            print 'skipping combination'
            pass
        # TODO make sure data is removed from db after test

    def test_walk_store_user(self, mywalk):
        """Unit test for Walk._store_user"""
        session = current.session
        case = mywalk['casedata']
        thiswalk = mywalk['walk']
        if case['casenum'] == 1:
            session.user = None  # empty session variable as a baseline
            user = thiswalk._get_user()
            user_id = user.get_id()

            actual = thiswalk._store_user(user)
            assert actual is True
            assert isinstance(session.user, User)
            assert session.user.get_id() == user_id

            # remove session user again
            session.user = None
        else:
            print 'skipping combination'
            pass


@pytest.mark.skipif('global_runall is False '
                    'and global_run_TestPathChooser is False')
class TestPathChooser():
    '''
    Unit testing class for the paideia.PathChooser class.
    '''
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('locid,completed,tpout,redirect,expected',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               [2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256, 40,
                                9, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                                419, 420, 421, 422, 423, 444, 445],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               False,
                               [1]  # only one left with tag
                               ),
                              (11,  # synagogue [all in loc 11 completed]
                               [1, 2, 3, 8, 95, 96, 97, 99, 102],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                                True,
                                [5, 63, 256, 409, 410, 411, 412, 413, 414,
                                 415, 416, 417, 418, 419, 420, 421, 422, 423,
                                 444, 445]  # tag 61, not loc 11, not completed
                               ),
                              (8,  # agora (no redirect, new here)
                               [17, 98, 15, 208, 12, 16, 34, 11, 23, 4, 9, 18],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                                False,
                               [7, 14, 100, 35, 19, 103, 21, 97, 13, 261, 101]
                               ),
                              (8,  # agora (all for tags completed, repeat here)
                               [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                19, 21, 22, 23, 34, 35, 45, 97, 98, 100, 101,
                                103, 120, 129, 139, 141, 149, 152, 161, 167,
                                176, 184, 190, 208, 222, 225, 228, 231, 236,
                                247, 255, 257, 261, 277, 333, 334, 366, 424,
                                425, 426, 427, 428, 429, 430, 431, 433, 434,
                                435, 436, 437, 439, 440, 441, 444, 445],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                                False,
                               [101, 35, 34, 23, 16, 261, 15, 21, 208, 100,
                                17, 14, 9, 7, 18, 11, 98, 12, 4, 19, 103, 13,
                                97]  # with tags already completed here (repeat)
                               ),
                              ])
    def test_pathchooser_choose(self, locid, completed, tpout, redirect,
                                expected, db):
        """
        Unit test for the paideia.Pathchooser.choose() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        actual, newloc, catnum = chooser.choose()

        #mycat = 'cat{}'.format(catnum)
        #allpaths = db(db.paths.id > 0).select()
        #tagids = tpout[mycat]
        #expected = [p.id for p in allpaths
                    #if any([t for t in tagids if t in p.tags])]
        print 'CHOSEN PATH', actual
        print 'EXPECTED PATHS', expected

        assert catnum in range(1, 5)
        if redirect:
            assert newloc
            firststep = actual['steps'][0]
            steplocs = db.steps(firststep).locations
            assert newloc in steplocs
            assert locid not in steplocs
        else:
            assert actual['id'] in expected
            assert newloc is None

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
        for num in range(1000):
            actual = chooser._order_cats()
            assert actual in expected
            result_count[actual[0]] += 1
        assert result_count[1] in range(740 - 20, 740 + 20)
        assert result_count[2] in range(160 - 20, 160 + 20)
        assert result_count[3] in range(90 - 20, 90 + 20)
        assert result_count[4] in range(10 - 20, 10 + 20)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('locid,completed,tpout,expected',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               [2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256, 40,
                                9, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                                419, 420, 421, 422, 423, 444, 445],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [1]  # only one left with tag
                               ),
                              (11,  # synagogue [all in loc 11 completed]
                               [1, 2, 3, 8, 95, 96, 97, 99, 102],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                                [5, 63, 256, 409, 410, 411, 412, 413, 414,
                                 415, 416, 417, 418, 419, 420, 421, 422, 423,
                                 444, 445]  # tag 61, not loc 11, not completed
                               ),
                              (8,  # agora (no redirect, new here)
                               [17, 98, 15, 208, 12, 16, 34, 11, 23, 4, 9, 18],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [7, 14, 100, 35, 19, 103, 21, 97, 13, 261, 101]
                               ),
                              (8,  # agora (all for tags completed, repeat here)
                               [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                19, 21, 22, 23, 34, 35, 45, 97, 98, 100, 101,
                                103, 120, 129, 139, 141, 149, 152, 161, 167,
                                176, 184, 190, 208, 222, 225, 228, 231, 236,
                                247, 255, 257, 261, 277, 333, 334, 366, 424,
                                425, 426, 427, 428, 429, 430, 431, 433, 434,
                                435, 436, 437, 439, 440, 441, 444, 445],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [101, 35, 34, 23, 16, 261, 15, 21, 208, 100,
                                17, 14, 9, 7, 18, 11, 98, 12, 4, 19, 103, 13,
                                97]  # with tags already completed here (repeat)
                               ),
                              ])
    def test_pathchooser_paths_by_category(self, locid, completed, tpout,
                                           expected):
        """
        Unit test for the paideia.Pathchooser._paths_by_category() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        cpaths, category = chooser._paths_by_category(1, tpout['latest_new'])
        assert all([row['id'] for row in cpaths if row['id'] in expected])

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('locid,completed,tpout,expected',
                             [(6,  # shop_of_alexander (only 1 untried here)
                               [2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256, 40,
                                9, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                                419, 420, 421, 422, 423, 444, 445],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                               [1]  # only one left with tag
                               ),
                              (11,  # synagogue [all in loc 11 completed]
                               [1, 2, 3, 8, 95, 96, 97, 99, 102],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                                [5, 63, 256, 409, 410, 411, 412, 413, 414,
                                 415, 416, 417, 418, 419, 420, 421, 422, 423,
                                 444, 445]  # tag 61, not loc 11, not completed
                               ),
                              (8,  # agora (no redirect, new here)
                               [17, 98, 15, 208, 12, 16, 34, 11, 23, 4, 9, 18],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [7, 14, 100, 35, 19, 103, 21, 97, 13, 261, 101]
                               ),
                              (8,  # agora (all for tags completed, repeat here)
                               [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                                19, 21, 22, 23, 34, 35, 45, 97, 98, 100, 101,
                                103, 120, 129, 139, 141, 149, 152, 161, 167,
                                176, 184, 190, 208, 222, 225, 228, 231, 236,
                                247, 255, 257, 261, 277, 333, 334, 366, 424,
                                425, 426, 427, 428, 429, 430, 431, 433, 434,
                                435, 436, 437, 439, 440, 441, 444, 445],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                               [101, 35, 34, 23, 16, 261, 15, 21, 208, 100,
                                17, 14, 9, 7, 18, 11, 98, 12, 4, 19, 103, 13,
                                97]  # with tags already completed here (repeat)
                               ),
                              ])
    def test_pathchooser_choose_from_cat(self, locid, completed, tpout,
                                         expected, db):
        """
        Unit test for the paideia.Pathchooser._choose_from_cats() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        catnum = 1
        expected_rows = db(db.paths.id.belongs(expected)).select()
        path, newloc, cat = chooser._choose_from_cat(expected_rows, catnum)
        assert path['id'] in expected
        if newloc:
            assert newloc in [l for l in db.steps(path['steps'][0]).locations]
        else:
            assert newloc is None
        assert cat == 1


class TestBugReporter():
    '''
    Unit testing class for the paideia.BugReporter class.
    '''

    def test_bugreporter_get_reporter(self):
        """
        Unit test for BugReporter.get_reporter() method.
        """
        data = {'record_id': 22,
                'path_id': 4,
                'step_id': 108,
                'score': 0.5,
                'response_string': 'hi',
                'loc_alias': 'agora'}
        expected = '<a class="bug_reporter_link" data-w2p_disable_with="default" ' \
                   'href="/paideia/creating/bug.load?' \
                   'answer=hi&amp;loc=agora&amp;log_id=22&amp;path=4&amp;' \
                   'score=0.5&amp;step=108" id="bug_reporter">click here</a>'

        actual = BugReporter().get_reporter(**data)

        assert actual.xml() == expected
