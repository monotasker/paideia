# -*- coding: utf-8 -*-
# Unit tests for the paideia module

import pytest
from paideia import Npc, Location, User, PathChooser, Path, Categorizer, Walk
from paideia import StepFactory, StepText, StepMultiple, NpcChooser, Step
from paideia import StepRedirect, StepViewSlides, StepAwardBadges
from paideia import StepEvaluator, MultipleEvaluator, StepQuotaReached
from paideia import A, URL, DIV, LI, UL, SPAN
from paideia import Block
from gluon import current
request = current.request
# from gluon.dal import Rows
import datetime
# from pprint import pprint
import re
from random import randint
from copy import copy

# web2py library for functional testing
from gluon.contrib.webclient import WebClient
client = WebClient('http://127.0.0.1:8000/paideia/default/', postbacks=True)
client.get('index')

#register
data = dict(first_name='Homer',
            last_name='Simpson',
            email='scottianw@gmail.com',
            password='test',
            password_two='test',
            _formname='register')
client.post('user/register', data=data)

# ===================================================================
# Controls governing which tests to run
# ===================================================================
global_runall = False
global_run_TestNpc = False
global_run_TestLocation = False
global_run_TestNpcChooser = False
global_run_TestStep = False
global_run_TestStepRedirect = False
global_run_TestStepAwardBadges = False
global_run_TestStepViewSlides = False
global_run_TestStepText = False
global_run_TestStepMultiple = False
global_run_TestStepEvaluator = False
global_run_TestMultipleEvaluator = False
global_run_TestPath = False
global_run_TestUser = False
global_run_TestCategorizer = False
global_run_TestWalk = 1
global_run_TestPathChooser = False

# ===================================================================
# Test Fixtures
# ===================================================================


def dt(string):
    """Return datetime object parsed from the string argument supplied"""
    format = "%Y-%m-%d"
    return datetime.datetime.strptime(string, format)

# Constant values from db
db = current.db
images = {'npc1_img': '/paideia/static/images/images.image.bb48641f0122d2b6.696d616765732e696d6167652e383136303330663934646664646561312e34343732363137373639366536373230333432653733373636372e737667.svg',
          'npc2_img': '/paideia/static/images/images.image.81e2d69e1aea4d99.44726177696e672031372e737667.svg',
          'npc3_img': '/paideia/static/images/images.image.a59978facee731f0.44726177696e672031382e737667.svg',
          'npc4_img': '/paideia/static/images/images.image.85a960241dc29f1b.776f6d616e312e706e67.png',
          'npc5_img': '/paideia/static/images/images.image.a4d5140b25f87749.44726177696e672031392e737667.svg',
          'npc6_img': '/paideia/static/images/images.image.a28124edf3480d82.696d616765732e696d6167652e383135323664663563326663623438302e343437323631373736393665363732303332333232653733373636372e737667.svg',
          'npc7_img': '/paideia/static/images/images.image.993274ee0076fd2f.696d616765732e696d6167652e393636636434346165663238613839652e343437323631373736393665363732303332333732653733373636372e737667.svg',
          'npc8_img': '/paideia/static/images/images.image.938be4c25c678bb5.323031322d30362d30352030335f35325f31312e706e67.png',
          'npc9_img': '/paideia/static/images//',
          'npc10_img': '/paideia/static/images/images.image.961b44d8d322659c.323031322d30362d30372031345f34345f34302e706e67.png',
          'npc11_img': '/paideia/static/images/images.image.ac58c3e138964719.70686f6562652e706e67.png',
          'npc14_img': '/paideia/static/images/images.image.b5592e80d5fe4bb3.73796e61676f6775652e6a7067.jpg',
          'npc15_img': '/paideia/static/images/images.image.9a515ff664f03aa3.323031322d30372d32312032335f35315f31322e706e67.png',
          'npc16_img': '/paideia/static/images/images.image.8bb7c079634cf35a.44726177696e672033332e706e67.png',
          'npc17_img': '/paideia/static/images/images.image.95fcf253d4dd7abd.44726177696e6720352e706e67.png'}

npc_data = {1: {'image': images['npc1_img'],
                'name': 'Ἀλεξανδρος',
                'location': [6, 8]},
            2: {'image': images['npc4_img'],
                'name': 'Μαρια',
                'location': [3, 1, 2, 4]},
            8: {'image': images['npc5_img'],
                'name': 'Διοδωρος',
                'location': [1]},
            14: {'image': images['npc2_img'],
                 'name': 'Γεωργιος',
                 'location': [3, 1, 2, 4, 7, 8, 9, 10]},
            17: {'image': images['npc7_img'],
                 'name': 'Ἰασων',
                 'location': [3, 1, 2, 4, 7, 8]},
            21: {'image': images['npc7_img'],
                 'name': 'Νηρευς',
                 'location': [7, 8]},
            31: {'image': images['npc3_img'],
                 'name': 'Σοφια',
                 'location': [3, 1, 2, 4, 11]},
            32: {'image': images['npc10_img'],
                 'name': 'Στεφανος',
                 'location': [11]},
            40: {'image': images['npc6_img'],
                 'name': 'Σίμων',
                 'location': [3, 1, 2, 4, 7, 8]},
            41: {'image': images['npc11_img'],
                 'name': 'Φοιβη',
                 'location': [3, 1, 4, 8]},
            42: {'image': images['npc9_img'],
                 'name': 'Ὑπατια',
                 'location': [3, 1, 2, 4, 12, 8]}
            }


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


@pytest.fixture(params=[n for n in [1, 2, 19, 30, 101, 125, 126, 127]])
def mysteps(request):
    """
    Test fixture providing step information for unit tests.
    This fixture is parameterized, so that tests can be run with each of the
    steps or with any sub-section (defined by a filtering expression in the
    test). This step fixture is also used in the mycases fixture.
    """
    the_step = request.param
    text_responder = '<form action="" autocomplete="off"' \
                     'enctype="multipart/form-data" method="post">' \
                     '<table>' \
                     '<tr id="no_table_response__row">' \
                     '<td class="w2p_fl">' \
                     '<label for="no_table_response" id="no_table_response__label">' \
                     'Response: </label>' \
                     '</td>' \
                     '<td class="w2p_fw">' \
                     '<input class="string" id="no_table_response" name="response" ' \
                     'type="text" value="" />' \
                     '</td>' \
                     '<td class="w2p_fc"></td>' \
                     '</tr>' \
                     '<tr id="submit_record__row">' \
                     '<td class="w2p_fl"></td>' \
                     '<td class="w2p_fw">' \
                     '<input type="submit" value="Submit" />' \
                     '</td>' \
                     '<td class="w2p_fc"></td>' \
                     '</tr>' \
                     '</table>' \
                     '</form>'
    multi_responder = text_responder
    stub_responder = ''
    continue_responder = ''

    steps = {1: {'id': 1,
                 'paths': [2],
                 'type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1, 17],
                 'locations': [3, 1, 13, 7, 8, 11],
                 'raw_prompt': 'How could you write the word "meet" using '
                               'Greek letters?',
                 'final_prompt': 'How could you write the word "meet" using '
                                 'Greek letters?',
                 'instructions': [],
                 'tags': [61],
                 'tags_secondary': [],
                 'responder': text_responder,
                 'responses': {'response1': '^μιτ$'},
                 'readable': {'readable_short': ['μιτ'],
                              'readable_long': None},
                 'tips': [],
                 'reply_text': {'correct': 'Right. Κάλον.',
                                'incorrect': 'Incorrect. Try again!'},
                 'user_responses': {'correct': 'μιτ',
                                    'incorrect': 'βλα'}
                 },
             2: {'id': 2,
                 'paths': [3],
                 'type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1],
                 'locations': [3, 1, 13, 7, 8, 11],
                 'raw_prompt': 'How could you write the word "bought" using '
                               'Greek letters?',
                 'final_prompt': 'How could you write the word "bought" using '
                                 'Greek letters?',
                 'instructions': ['Focus on finding Greek letters that make '
                                  'the *sounds* of the English word. Don\'t '
                                  'look for Greek "equivalents" for each '
                                  'English letter.'],
                 'tags': [61],
                 'tags_secondary': [],
                 'responder': text_responder,
                 'responses': {'response1': '^β(α|ο)τ$'},
                 'readable': {'readable_short': ['βατ', 'βοτ'],
                              'readable_long': None},
                 'reply_text': {'correct': 'Right. Κάλον.',
                                'incorrect': 'Incorrect. Try again!'},
                 'tips': None,  # why is this None, but elsewhere it's []?
                 'user_responses': {'correct': 'βοτ',
                                    'incorrect': 'βλα'}
                 },
             19: {'id': 19,
                 'paths': [19],
                 'type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1],
                 'locations': [3, 1, 13, 8, 11],
                 'raw_prompt': 'How could you spell the word "pole" with '
                               'Greek letters?',
                 'final_prompt': 'How could you spell the word "pole" with '
                                 'Greek letters?',
                 'instructions': ['Focus on finding Greek letters that make '
                                  'the *sounds* of the English word. Don\'t '
                                  'look for Greek "equivalents" for each '
                                  'English letter.'],
                 'tags': [62],
                 'tags_secondary': [61],
                 'responses': {'response1': '^πωλ$'},
                 'responder': text_responder,
                 'readable': {'readable_short': ['πωλ'],
                              'readable_long': None},
                 'reply_text': {'correct': 'Right. Κάλον.',
                                'incorrect': 'Incorrect. Try again!'},
                 'tips': [],
                 'user_responses': {'correct': 'πωλ',
                                    'incorrect': 'βλα'}
                  },
             30: {'id': 30,
                  'paths': [None],
                  'type': StepRedirect,
                  'widget_type': 9,
                  'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                  'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                  'raw_prompt': 'Hi there. Sorry, I don\'t have anything for '
                                'you to do here at the moment. I think '
                                'someone was looking for you at [[next_loc]].',
                  'final_prompt': 'Hi there. Sorry, I don\'t have anything '
                                  'for you to do here at the moment. I think '
                                  'someone was looking for you at '
                                  '[[next_loc]].',
                  'instructions': None,
                  'tags': [70],
                  'tags_secondary': [],
                  'responder': stub_responder},
             101: {'id': 101,
                   'paths': [89],
                   'type': StepMultiple,
                   'widget_type': 4,
                   'locations': [7],
                   'npc_list': [14],
                   'raw_prompt': 'Is this an English clause?\r\n\r\n"The '
                                 'cat sat."',
                   'final_prompt': 'Is this an English clause?\r\n\r\n"The '
                                   'cat sat."',
                   'instructions': None,
                   'tags': [36],
                   'tags_secondary': [],
                   'options': ['ναι', 'οὐ'],
                   'responses': {'response1': 'ναι'},
                   'responder': multi_responder,
                   'readable': {'readable_short': ['ναι'],
                                'readable_long': None},
                   'reply_text': {'correct': 'Right. Κάλον.',
                                  'incorrect': 'Incorrect. Try again!'},
                   'tips': []},
             125: {'id': 125,
                   'paths': [None],
                   'type': StepQuotaReached,
                   'widget_type': 7,
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'raw_prompt': 'Well done, [[user]]. You\'ve finished '
                                 'enough paths for today. But if you would '
                                 'like to keep going, you\'re welcome to '
                                 'continue.',
                   'final_prompt': 'Well done, [[user]]. You\'ve finished '
                                   'enough paths for today. But if you would '
                                   'like to keep going, you\'re welcome to '
                                   'continue.',
                   'instructions': None,
                   'tags': [79],
                   'tags_secondary': [],
                   'responder': continue_responder},
             126: {'id': 126,
                   'paths': [None],
                   'type': StepAwardBadges,
                   'widget_type': 8,
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'raw_prompt': 'Congratulations, [[user]]! You\'ve reached '
                                 'a new level with these badges:'
                                 '[[promoted_list]]You can click on your name '
                                 'above to see details of your progress '
                                 'so far.',
                   'final_prompt': 'Congratulations, [[user]]! You\'ve reached '
                                   'a new level with these badges:'
                                   '[[promoted_list]]You can click on your name '
                                   'above to see details of your progress '
                                   'so far.',
                   'instructions': None,
                   'tags': [81],
                   'tags_secondary': [],
                   'responder': continue_responder},
             127: {'id': 127,
                   'paths': [None],
                   'type': StepViewSlides,
                   'widget_type': 6,
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'raw_prompt': 'Congratulations, [[user]]! You\'re ready to '
                                 'start working on some new badges:'
                                 '[[badge_list]]Before you continue, take '
                                 'some time to view these slide sets:'
                                 '[[slides]]You\'ll find the slides by '
                                 'clicking on the "slides" menu item at top.',
                   'final_prompt': 'Congratulations, Ian! You\'re ready to '
                                   'start working on some new badges:'
                                   '[[badge_list]]Beforeyou continue, take '
                                   'some time to view these slide sets:'
                                   '<ul class="slide_list">'
                                   '<li>The Alphabet III</li>'
                                   '<li>Case Basics</li>'
                                   '</ul>'
                                   'You\'ll find the slides by clicking on '
                                   'the "slides" menu item at top.',
                   'instructions': None,
                   'tags': [80],
                   'tags_secondary': [],
                   'responder': stub_responder}
             }
    return steps[the_step]


@pytest.fixture(params=['case{}'.format(n) for n in range(1, 6)])
def mycases(request, mysteps):
    """
    Text fixture providing various cases for unit tests. For each step,
    several cases are specified.
    """
    the_case = request.param
    # same npc and location as previous step
    # replace tag too far ahead (1) with appropriate (61)
    cases = {'case1': {'casenum': 1,
                       'loc': Location(1, db),
                       'mynow': dt('2013-01-29'),
                       'name': 'Ian',
                       'uid': 1,
                       'prev_loc': Location(7, db),
                       'prev_npc_id': 2,
                       'npcs_here': [2, 8, 14, 17, 31, 40, 41, 42],
                       'pathid': 3,
                       'blocks_in': None,
                       'blocks_out': None,
                       'localias': 'shop_of_alexander',
                       'tag_records': [{'name': 1,
                                        'tag_id': 1,
                                        'last_right': dt('2013-01-29'),
                                        'last_wrong': dt('2013-01-29'),
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
                       'paths': {'cat1': [1, 2, 3, 5, 8, 63, 64, 70, 95, 96,
                                          97, 99, 102, 104, 256, 277],
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
                      {'casenum': 2,
                       'mynow': dt('2013-01-29'),
                       'loc': Location(8, db),
                       'name': 'Ian',
                       'uid': 1,
                       'prev_loc': Location(8, db),
                       'prev_npc_id': 1,
                       'npcs_here': [1, 14, 17, 21, 40, 41, 42],
                       'pathid': 89,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag_id': 61,
                                        'last_right': dt('2013-01-29'),
                                        'last_wrong': dt('2013-01-28'),
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
                       'tag_progress_out': {'latest_new': 1,
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
                       'paths': {'cat1': [1, 2, 3, 5, 8, 63, 64, 70, 95, 96,
                                          97, 99, 102, 104, 256, 277],
                                 'cat2': [],
                                 'cat3': [],
                                 'cat4': []},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': [],
                       'new_badges': [62],
                       'promoted': {'cat2': [61]},
                       'demoted': {}},
             'case3':  # same location as previous step, last npc stephanos
             # promote tag based on time (without ratio)
             # add several untried tags for current rank
                      {'casenum': 3,
                       'mynow': dt('2013-01-29'),
                       'name': 'Ian',
                       'uid': 1,
                       'loc': Location(11, db),  # synagogue
                       'prev_loc': Location(11, db),
                       'prev_npc_id': 31,  # stephanos
                       'npcs_here': [31, 32],
                       'pathid': 19,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag_id': 61,  # promote to 2 for time
                                        'last_right': dt('2013-01-27'),
                                        'last_wrong': dt('2013-01-21'),
                                        'times_right': 10,
                                        'times_wrong': 10,
                                        'secondary_right': None},
                                       # don't promote for time bc dw > dr
                                       {'name': 1,
                                        'tag_id': 62,
                                        'last_right': dt('2013-01-10'),
                                        'last_wrong': dt('2013-01-1'),
                                        'times_right': 10,
                                        'times_wrong': 0,
                                        'secondary_right': None},
                                       # don't promote for time bc t_r < 10
                                       {'name': 1,
                                        'tag_id': 63,
                                        'last_right': dt('2013-01-27'),
                                        'last_wrong': dt('2013-01-21'),
                                        'times_right': 9,
                                        'times_wrong': 0,
                                        'secondary_right': None},
                                       # promote for time bc t_r >= 10
                                       {'name': 1,
                                        'tag_id': 66,
                                        'last_right': dt('2013-01-27'),
                                        'last_wrong': dt('2013-01-21'),
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
                                        'cat1': [61, 62, 63, 66], 'cat2': [],
                                        'cat3': [], 'cat4': [],
                                        'rev1': [], 'rev2': [],
                                        'rev3': [], 'rev4': []},
                       'introduced': [9, 16, 48, 76, 93],
                       'tag_progress_out': {'latest_new': 4,
                                            'cat1': [62, 63, 68, 115, 72,
                                                     89, 36],
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
                       'paths': {'cat1': [1, 2, 3, 5, 8, 38, 39, 40, 41, 42,
                                          43, 44, 56, 57, 58, 59, 61, 62, 63,
                                          64, 70, 84, 86, 87, 88, 90, 95, 96,
                                          97, 99, 102, 104, 127, 256, 267, 270,
                                          277, 288, 289, 290, 301, 302],
                                 'cat2': [4, 7, 9, 10, 11, 12, 13, 14, 15, 16,
                                          17, 18, 19, 21, 22, 23, 34, 35, 97,
                                          98, 100, 101, 103, 257, 261, 277],
                                 'cat3': [],
                                 'cat4': []},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': [],
                       'untried': [68, 89, 72, 36, 115],
                       'new_badges': None,
                       'promoted': {'cat2': [61, 66]},
                       'demoted': {}},
             'case4':  # different location than previous step
             # secondary_right records override date and ratio to allow promot.
             # secondary_right list sliced accordingly
                      {'casenum': 4,
                       'mynow': dt('2013-01-29'),
                       'name': 'Ian',
                       'uid': 1,
                       'loc': Location(8, db),
                       'prev_loc': Location(7, db),
                       'prev_npc_id': 1,
                       'npcs_here': [1, 14, 17, 21, 40, 41, 42],
                       'pathid': 1,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag_id': 61,  # 2ndary overrides time
                                        'last_right': dt('2013-01-24'),
                                        'last_wrong': dt('2013-01-21'),
                                        'times_right': 9,
                                        'times_wrong': 10,
                                        'secondary_right': [dt('2013-01-28'),
                                                            dt('2013-01-28'),
                                                            dt('2013-01-28'),
                                                            dt('2013-01-29')]},
                                       {'name': 1,
                                        'tag_id': 62,  # 2ndary overrides ratio
                                        'last_right': dt('2013-01-29'),
                                        'last_wrong': dt('2013-01-28'),
                                        'times_right': 9,
                                        'times_wrong': 2,
                                        'secondary_right': [dt('2013-01-28'),
                                                            dt('2013-01-28'),
                                                            dt('2013-01-28')]}],
                       'tag_records_out': [{'name': 1,
                                            'tag_id': 61,  # 2ndary overrides time
                                            'last_right': dt('2013-01-28'),
                                            'last_wrong': dt('2013-01-21'),
                                            'times_right': 10,
                                            'times_wrong': 10,
                                            'secondary_right': [dt('2013-01-29')]
                                            },
                                           {'name': 1,
                                            'tag_id': 62,  # 2ndary overrides ratio
                                            'last_right': dt('2013-01-29'),
                                            'last_wrong': dt('2013-01-28'),
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
                       'paths': {'cat1': [6, 20, 24, 25, 27, 28, 33, 37, 64,
                                          65, 66, 67, 68, 69, 94, 103, 104,
                                          259, 260, 277, 278, 279, 280, 284,
                                          285, 286, 38, 39, 40, 41, 42, 43, 44,
                                          56, 57, 58, 59, 61, 62, 84, 86, 87,
                                          88, 90, 127, 267, 270, 288, 289, 290,
                                          301, 302, 45, 46, 47, 48, 49, 50, 51,
                                          52, 53, 54, 55, 56, 57, 58, 59, 60,
                                          61, 62, 84, 85, 86, 87, 88, 135, 206,
                                          262, 263, 264, 265, 266, 267, 268,
                                          269, 270, 308, 309],
                                 'cat2': [1, 2, 3, 5, 8, 63, 64, 70, 95, 96,
                                          97, 99, 102, 104, 256, 277, 4, 7, 9,
                                          10, 11, 12, 13, 14, 15, 16, 17, 18,
                                          19, 20, 21, 22, 23, 34, 35, 97, 98,
                                          100, 101, 103, 257, 261, 277],
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
                       'name': 'Ian',
                       'uid': 1,
                       'loc': Location(3, db),
                       'prev_loc': Location(3, db),
                       'prev_npc_id': 1,
                       'npcs_here': [2, 14, 17, 31, 40, 41, 42],
                       'pathid': 1,
                       'blocks_in': None,
                       'blocks_out': None,
                       'tag_records': [{'name': 1,
                                        'tag_id': 61,
                                        'last_right': dt('2013-01-29'),
                                        'last_wrong': dt('2013-01-28'),
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
                       'tag_progress_out': {'latest_new': 1,
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
                       'paths': {'cat1': [1, 2, 3, 5, 8, 63, 64, 70, 95, 96,
                                          97, 99, 102, 104, 256, 277],
                                 'cat2': [],
                                 'cat3': [],
                                 'cat4': []},
                       'new_badges': [62],
                       'promoted': {'cat2': [61]},
                       'demoted': {},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': []}
             }
    return {'casedata': cases[the_case],
            'stepdata': mysteps}


@pytest.fixture
def mynpcchooser(mycases):
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['id'] in case['steps_here']:
        if case['casenum'] == 1:
            step = StepFactory().get_instance(db=db,
                                              step_id=step['id'],
                                              loc=case['loc'],
                                              prev_loc=case['prev_loc'],
                                              prev_npc_id=case['prev_npc_id'])
            location = case['loc']
            prev_npc = Npc(case['prev_npc_id'], db)
            prev_loc = case['prev_loc']
            return {'chooser': NpcChooser(step, location, prev_npc, prev_loc),
                    'casedata': case,
                    'stepdata': step}


@pytest.fixture
def mywalk(mycases):
    """pytest fixture providing a paideia.Walk object for testing"""
    case = mycases['casedata']
    step = mycases['stepdata']
    userdata = {'first_name': case['name'], 'id': case['uid']}
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
def mypathchooser(mycases):
    """pytest fixture providing a paideia.PathChooser object for testing"""
    case = mycases['casedata']
    step = mycases['stepdata']
    klist = ['cat1', 'cat2', 'cat3', 'cat4', 'rev1', 'rev2', 'rev3']
    cats = {k: v for k, v in case['tag_progress'].iteritems() if k in klist}
    pc = PathChooser(cats, case['loc'], case['completed'], db=db)
    return {'pathchooser': pc,
            'paths': case['paths'],
            'casedata': case,
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


@pytest.fixture
def myuser(mycases):
    """A pytest fixture providing a paideia.User object for testing."""
    case = mycases['casedata']
    step = mycases['stepdata']
    uid = case['uid']
    userdata = db.auth_user(uid).as_dict()
    tag_progress = case['tag_progress']
    tag_records = case['tag_records']
    localias = case['loc'].get_alias()
    return {'user': User(userdata, localias, tag_records, tag_progress),
            'casedata': case,
            'stepdata': step}


@pytest.fixture
def mynpc():
    '''
    A pytest fixture providing a paideia.Npc object for testing.
    '''
    return Npc(1, db)


@pytest.fixture
def mynpc_stephanos():
    '''
    A pytest fixture providing a paideia.Npc object for testing.
    '''
    return Npc(32, db)


@pytest.fixture
def myloc():
    """
    A pytest fixture providing a paideia.Location object for testing.
    """
    return Location(6, db)


@pytest.fixture
def myloc_synagogue():
    """
    A pytest fixture providing a paideia.Location object for testing.
    """
    return Location(11, db)


@pytest.fixture
def mypath(mycases):
    """
    A pytest fixture providing a paideia.Path object for testing.
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    the_path = Path(path_id=case['pathid'],
                    blocks=case['blocks_in'],
                    loc=case['loc'],
                    prev_loc=case['prev_loc'],
                    prev_npc_id=case['prev_npc_id'],
                    db=db)
    pid = the_path.get_id()
    path_steps = db.paths[pid].steps
    return {'path': the_path,
            'id': pid,
            'casedata': case,
            'steps': path_steps,
            'stepdata': step}


@pytest.fixture
def mystep(mycases):
    """
    A pytest fixture providing a paideia.Step object for testing.
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    if (not case['loc'].get_id() in step['locations']) or \
       (not [n for n in case['npcs_here'] if n in step['npc_list']]):
        return None
    if step['type'] == StepAwardBadges and case['casenum'] != 5:
        return None
    if step['type'] == StepViewSlides and case['casenum'] != 5:
        return None
    if step['type'] == StepRedirect and case['casenum'] != 5:
        return None
    else:
        return {'casenum': case['casenum'],
                'step': StepFactory().get_instance(db=db,
                                                   step_id=step['id'],
                                                   loc=case['loc'],
                                                   prev_loc=case['prev_loc'],
                                                   prev_npc_id=case['prev_npc_id']),
                'stepdata': step,
                'casedata': case}


@pytest.fixture
def myStepRedirect(mycases):
    """
    A pytest fixture providing a paideia.StepRedirect object for testing.
    - same npc and location as previous step
    TODO: write another fixture for a new location and for a new npc
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['id'] == 30:
        my_args = {'step_id': 30,
                   'loc': case['loc'],
                   'prev_loc': case['prev_loc'],
                   'prev_npc_id': case['prev_npc_id'],
                   'db': db}
        return {'step': StepRedirect(**my_args),
                'stepdata': step}
    else:
        pass


@pytest.fixture
def myStepAwardBadges(mycases):
    """
    A pytest fixture providing a paideia.StepAwardBadges object for testing.
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    if (step['id'] == 126) and case['promoted']:
        kwargs = {'step_id': 126,
                  'loc': case['loc'],
                  'prev_loc': case['prev_loc'],
                  'prev_npc_id': case['prev_npc_id'],
                  'db': db}
        return {'step': StepAwardBadges(**kwargs),
                'stepdata': step,
                'casedata': case}
    else:
        pass


@pytest.fixture
def myStepViewSlides(mycases):
    """
    A pytest fixture providing a paideia.StepViewSlides object for testing.
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['id'] == 127 and case['new_badges']:
        kwargs = {'step_id': 127,
                  'loc': case['loc'],
                  'prev_loc': case['prev_loc'],
                  'prev_npc_id': case['prev_npc_id'],
                  'db': db}
        return {'step': StepViewSlides(**kwargs),
                'stepdata': step,
                'casedata': case}
    else:
        pass


@pytest.fixture
def myStepQuotaReached(mycases):
    """
    A pytest fixture providing a paideia.StepQuota object for testing.
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['id'] == 125:
        kwargs = {'step_id': 125,
                  'loc': case['loc'],
                  'prev_loc': case['prev_loc'],
                  'prev_npc_id': case['prev_npc_id'],
                  'db': db}
        return {'step': StepFactory().get_instance(**kwargs),
                'stepdata': step,
                'casedata': case}
    else:
        pass


@pytest.fixture
def myStepText(mycases):
    """
    A pytest fixture providing a paideia.StepText object for testing.
    """
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['widget_type'] == 1:
        # following switch alternates correct and incorrect answers
        # actual answers taken from step data
        for n in [0, 1]:
            responses = ['incorrect', 'correct']
            s = StepFactory()
            step_instance = s.get_instance(db=db,
                                           step_id=step['id'],
                                           loc=case['loc'],
                                           prev_loc=case['prev_loc'],
                                           prev_npc_id=case['prev_npc_id'])
            return {'casenum': case['casenum'],
                    'step': step_instance,
                    'stepdata': step,
                    'casedata': case,
                    'user_response': step['user_responses'][responses[n]],
                    'reply_text': step['reply_text'][responses[n]],
                    'score': n,
                    'times_right': n,
                    'times_wrong': [1, 0][n]}
    else:
        pass


@pytest.fixture
def myStepMultiple(mycases):
    """A pytest fixture providing a paideia.StepMultiple object for testing."""
    case = mycases['casedata']
    step = mycases['stepdata']
    if step['widget_type'] == 4:
        for n in [0, 1]:
            responses = ['incorrect', 'correct']
            options = step['options']
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
                      'prev_npc_id': case['prev_npc_id'],
                      'db': db}
            return {'casenum': request.param,
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


@pytest.fixture
def myStepEvaluator(mysteps):
    """
    A pytest fixture providing a paideia.StepEvaluator object for testing.
    """
    if mysteps['widget_type'] == 1:
        for n in [0, 1]:
            responses = ['incorrect', 'correct']
            user_responses = ['bla', mysteps['responses']['response1']]
            kwargs = {'responses': mysteps['responses'],
                      'tips': mysteps['tips']}
            return {'eval': StepEvaluator(**kwargs),
                    'tips': mysteps['tips'],
                    'reply_text': mysteps['reply_text'][responses[n]],
                    'score': n,
                    'times_right': n,
                    'times_wrong': [1, 0][n],
                    'user_response': user_responses[n]}
        else:
            pass
    else:
        pass


@pytest.fixture()
def myMultipleEvaluator(mysteps):
    """
    A pytest fixture providing a paideia.MultipleEvaluator object for testing.
    """
    if mysteps['widget_type'] == 4:
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
        else:
            pass
    else:
        pass


@pytest.fixture()
def myblock(myblocks):
    """
    A pytest fixture providing a paideia.Block object for testing.
    """
    return Block().set_block(**myblocks)

# ===================================================================
# Test Classes
# ===================================================================


class TestNpc():
    '''
    Tests covering the Npc class of the paideia module.
    '''
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestNpc')

    def test_npc_get_name(self, mynpc):
        """Test for method Npc.get_name()"""
        assert mynpc.get_name() == 'Ἀλεξανδρος'

    def test_npc_get_id(self, mynpc):
        """Test for method Npc.get_id()"""
        assert mynpc.get_id() == 1

    def test_npc_get_image(self, mynpc):
        """Test for method Npc.get_image()"""
        assert mynpc.get_image() == '/paideia/static/images/images.image.bb48641f0122d2b6.696d616765732e696d6167652e383136303330663934646664646561312e34343732363137373639366536373230333432653733373636372e737667.svg'

    def test_npc_get_locations(self, mynpc):
        """Test for method Npc.get_locations()"""
        locs = mynpc.get_locations()
        assert isinstance(locs[0], Location)
        assert locs[0].get_id() == 6
        assert isinstance(locs[1], Location)
        assert locs[1].get_id() == 8

    def test_npc_get_description(self, mynpc):
        """Test for method Npc.get_description()"""
        assert mynpc.get_description() == "Ἀλεξανδρος is a shop owner and good friend of Simon's household. His shop is in the agora."


class TestLocation():
    """
    Tests covering the Location class of the paideia module.
    """
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestLocation')

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
        assert myloc.get_bg().xml() == '<img src="/paideia/static/images/images.image.9a515ff664f03aa3.323031322d30372d32312032335f35315f31322e706e67.png" />'

    def test_location_get_id(self, myloc):
        """Test for method Location.get_id"""
        assert myloc.get_id() == 6


class TestNpcChooser():
    """
    Unit tests covering the NpcChooser class of the paideia module.
    """
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestNpcChooser')

    def test_npcchooser_choose(self, mynpcchooser):
        if mynpcchooser:
            possible = mynpcchooser['stepdata']['npc_list']
            out = mynpcchooser['chooser'].choose()
            assert out.get_id() in possible


class TestStep():
    """
    Unit tests covering the Step class of the paideia module.
    """
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestStep')

    def test_step_get_id(self, mystep):
        """Test for method Step.get_id

        mystep fixture will be None for invalid step/case combinations.
        """
        if mystep:
            sid = mystep['stepdata']['id']
            stype = mystep['stepdata']['type']
            assert mystep['step'].get_id() == sid
            assert isinstance(mystep['step'], stype) is True
        else:
            pass

    def test_step_get_tags(self, mystep):
        """Test for method Step.get_tags

        mystep fixture will be None for invalid step/case combinations.
        """
        if mystep:
            primary = mystep['stepdata']['tags']
            secondary = mystep['stepdata']['tags_secondary']
            out = {'primary': primary, 'secondary': secondary}
            assert mystep['step'].get_tags() == out

    def test_step_get_prompt(self, mystep):
        """Test for method Step.get_prompt"""
        if mystep:
            step = mystep['step']
            sdata = mystep['stepdata']
            case = mystep['casedata']
            if sdata['widget_type'] in [1, 4]:
                stepnpcs = sdata['npc_list']
                locnpcs = [int(n) for n in case['npcs_here'] if n in stepnpcs]
                username = case['name']
                if locnpcs:
                    oprompt = sdata['final_prompt']
                    oinstr = sdata['instructions']
                    onpc_image = [npc_data[n]['image'] for n in stepnpcs if n in locnpcs]
                    assert step.get_prompt(username)['prompt'] == oprompt
                    assert step.get_prompt(username)['instructions'] == oinstr
                    assert step.get_prompt(username)['npc_image'] in onpc_image
                else:
                    assert step.get_prompt(username) == 'redirect'
            else:
                pass
        else:
            pass

    def test_step_make_replacements(self, mystep):
        """Unit test for method Step._make_replacements()"""
        if mystep and mystep['stepdata']['id'] not in [30, 125, 126, 127]:
            step = mystep['step']
            sdata = mystep['stepdata']
            case = mystep['casedata']
            oargs = {'raw_prompt': sdata['raw_prompt'],
                     'username': case['name']}
            ofinal = sdata['final_prompt']
            ofinal = ofinal.replace('[[user]]', oargs['username'])
            if isinstance(step, StepAwardBadges):
                oargs['new_badges'] = case['new_badges']
            elif isinstance(step, StepViewSlides):
                oargs['new_badges'] = case['new_badges']

            assert step._make_replacements(**oargs) == ofinal
        else:
            pass

    def test_step_get_npc(self, mystep):
        """Test for method Step.get_npc"""
        # TODO: make sure the npc really is randomized
        if mystep:
            actual = mystep['step'].get_npc()
            expected = mystep['stepdata']

            assert actual.get_id() in expected['npc_list']
            # make sure this npc has the right name for its id
            assert actual.get_name() == npc_data[actual.get_id()]['name']
            assert actual.get_image() == npc_data[actual.get_id()]['image']
            locs = actual.get_locations()
            # make sure there is common location shared by actual npc and step
            assert [l.get_id() for l in locs
                    if l.get_id() in expected['locations']]
            for l in locs:
                assert isinstance(l, Location)
                assert l.get_id() in npc_data[actual.get_id()]['location']
        else:
            pass

    def test_step_get_instructions(self, mystep):
        """Test for method Step._get_instructions"""
        if mystep:
            # ['Focus on finding Greek letters that make the *sounds* of the
            # English word. Don\'t look for Greek "equivalents" for each
            # English letter.']
            expected = mystep['stepdata']['instructions']
            actual = mystep['step']._get_instructions()
            assert actual == expected
        else:
            pass


class TestStepRedirect():
    '''
    A subclass of Step. Handles the user interaction when the user needs to be
    sent to another location.
    '''
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestStepRedirect')

    def test_stepredirect_get_id(self, myStepRedirect):
        """Test for method Step.get_id"""
        if myStepRedirect:
            assert myStepRedirect['step'].get_id() == 30
        else:
            pass

    def test_stepredirect_get_prompt(self, myStepRedirect):
        """
        Test method for the get_prompt method of the StepRedirect class.
        This test assumes that the selected npc is Stephanos. It also assumes
        that the step is 30.
        """
        # TODO: parameterize this properly
        if myStepRedirect:
            username = 'Ian'
            actual = myStepRedirect['step'].get_prompt(username)
            step = myStepRedirect['stepdata']
            newstring = step['final_prompt'].replace('[[next_loc]]', '{}')
            # TODO: figure out how to get test step to supply next loc
            placenames = ['ἡ στοά', 'τὸ βαλανεῖον', 'ὁ οἰκος Σιμωνος',
                          'ἡ ἀγορά', 'somewhere else in town']
            expected_prompts = [newstring.format(p) for p in placenames]
            expected_instructions = step['instructions']
            expected_images = [npc_data[i]['image'] for i in step['npc_list']]

            assert actual['prompt'] in expected_prompts
            assert actual['instructions'] == expected_instructions
            assert actual['npc_image'] in expected_images
        else:
            pass

    def test_stepredirect_make_replacements(self, myStepRedirect):
        """docstring for test_stepredirect_make_replacements"""
        if myStepRedirect:
            string = 'Nothing to do here [[user]]. Try [[next_loc]].'
            next_step = 1
            kwargs = {'raw_prompt': string,
                      'username': 'Ian',
                      'db': db,
                      'next_step_id': next_step}
            newstring = 'Nothing to do here Ian. Try {}.'
            placenames = ['ἡ στοά', 'τὸ βαλανεῖον', 'ὁ οἰκος Σιμωνος',
                          'ἡ ἀγορά', 'ἡ συναγωγή']
            expecteds = [newstring.format(p) for p in placenames]
            assert myStepRedirect['step']._make_replacements(**kwargs) in \
                expecteds
        else:
            pass

    def test_stepredirect_get_tags(self, myStepRedirect):
        """
        Test for method StepRedirect.get_tags

        The one tag that should be returned for all steps of this class is tag
        70 ('default').
        """
        if myStepRedirect:
            step = myStepRedirect['step']
            assert step.get_tags() == {'primary': [70], 'secondary': []}
        else:
            pass

    def test_stepredirect_get_responder(self, myStepRedirect):
        """Test for method Step.get_responder"""
        # TODO: parameterize properly
        if myStepRedirect:
            map_button = A("Map", _href=URL('walk'),
                           cid='page',
                           _class='button-yellow-grad back_to_map icon-location')
            responder = myStepRedirect['step'].get_responder().xml()
            assert responder == DIV(map_button).xml()
        else:
            pass

    def test_stepredirect_get_npc(self, myStepRedirect):
        """Test for method Step.get_npc"""
        # TODO: parameterize properly
        if myStepRedirect:
            expected = myStepRedirect['stepdata']
            npc = myStepRedirect['step'].get_npc()
            assert npc.get_id() in expected['npc_list']
            assert npc.get_name() == npc_data[npc.get_id()]['name']
            assert npc.get_image() == npc_data[npc.get_id()]['image']
            locs = npc.get_locations()
            assert [l.get_id() for l in locs if l.get_id() in expected['locations']]
            for l in locs:
                assert isinstance(l, Location)
                assert l.get_id() in npc_data[npc.get_id()]['location']
        else:
            pass


class TestStepAwardBadges():
    '''
    A subclass of Step. Handles the user interaction when the user is awarded
    new badges.
    '''
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestStepAwardBadges')

    def test_stepawardbadges_get_id(self, myStepAwardBadges):
        """Test for method StepAwardBadges.get_id"""
        if myStepAwardBadges:
            expect_id = myStepAwardBadges['stepdata']['id']
            assert myStepAwardBadges['step'].get_id() == expect_id

    def test_stepawardbadges_get_prompt(self, myStepAwardBadges):
        """
        Test method for the get_prompt method of the StepAwardBadges class.
        """
        if myStepAwardBadges:
            expect = myStepAwardBadges['stepdata']
            case = myStepAwardBadges['casedata']
            # TODO: remove npc numbers that can't be at this loc
            npcimgs = [npc_data[n]['image'] for n in expect['npc_list']]
            kwargs = {'raw_prompt': expect['raw_prompt'],
                      'username': case['name'],
                      'promoted': case['promoted'],
                      'db': db}
            print 'expected', case['promoted']
            actual = myStepAwardBadges['step'].get_prompt(**kwargs)
            # assemble expected prompt string dynamically
            flat_proms = [i for cat, lst in case['promoted'].iteritems()
                          for i in lst if lst]
            prom_records = db(db.badges.tag.belongs(flat_proms)
                              ).select(db.badges.tag,
                                       db.badges.badge_name).as_list()
            print 'prom_records', prom_records
            expect_prompt = expect['raw_prompt'].replace('[[user]]',
                                                         case['name'])
            if prom_records:
                prom_list = UL(_class='promoted_list')
                ranks = ['beginner', 'apprentice', 'journeyman', 'master']
                for rank, lst in case['promoted'].iteritems():
                    if lst:
                        rank = rank.replace('cat', '')
                        i = int(rank) - 1
                        label = ranks[i]
                        for l in lst:
                            bname = [row['badge_name'] for row in prom_records
                                     if row['tag'] == l]
                            prom_list.append(LI(SPAN(label, ' ', bname,
                                                     _class='badge_name')))
                expect_prompt = expect_prompt.replace('[[promoted_list]]',
                                                      prom_list.xml())
            else:
                # don't let test pass if there are no new badges for prompt
                raise Exception
            assert actual['prompt'] == expect_prompt
            assert actual['instructions'] == expect['instructions']
            assert actual['npc_image'] in npcimgs
        else:
            pass

    # TODO: fix this test
    #def test_stepawardbadges_make_replacements(self, myStepAwardBadges):
        #"""docstring for test_step_stepawardbadges_make_replacements"""
        #case = myStepAwardBadges['casenum']
        #sd = step_data_store[126]['case{}'.format(case)]
        #out = {k: v for k, v in sd.iteritems()
                #if k in ['raw_prompt', 'username', 'new_badges', 'promoted']}
        #actual = myStepAwardBadges['step']._make_replacements(**out)
        #assert actual == sd['final_prompt']

    def test_stepawardbadges_get_tags(self, myStepAwardBadges):
        """
        Test for method StepRedirect.get_tags
        The one tag that should be returned for all steps of this class is 81
        """
        if myStepAwardBadges:
            step = myStepAwardBadges['stepdata']
            expected = {'primary': step['tags'],
                        'secondary': step['tags_secondary']}
            assert myStepAwardBadges['step'].get_tags() == expected
        else:
            pass

    def test_stepawardbadges_get_responder(self, myStepAwardBadges):
        """Test for method StepAwardBadges.get_responder"""

        if myStepAwardBadges:
            case = myStepAwardBadges['casedata']
            the_loc = case['loc'].get_id()

            map_button = A("Map", _href=URL('walk'),
                           cid='page',
                           _class='button-yellow-grad back_to_map icon-location')
            continue_button = A("Continue", _href=URL('walk', args=['ask'],
                                                      vars={'loc': the_loc}),
                                cid='page',
                                _class='button-green-grad next_q')
            expected = DIV(map_button, continue_button).xml()
            actual = myStepAwardBadges['step'].get_responder().xml()
            print 'actual\n', actual
            print 'expected\n', expected
            assert actual == expected
        else:
            pass

    def test_stepawardbadges_get_npc(self, myStepAwardBadges):
        """Test for method StepAwardBadges.get_npc"""
        if myStepAwardBadges:
            npc = myStepAwardBadges['step'].get_npc()
            step = myStepAwardBadges['stepdata']
            case = myStepAwardBadges['casedata']
            assert npc.get_id() in step['npc_list']
            assert npc.get_id() in case['npcs_here']
            assert isinstance(npc, Npc)
        else:
            pass


class TestStepViewSlides():
    '''
    A subclass of Step. Handles the user interaction when the user is awarded
    new badges.
    '''
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestStepViewSlides')

    def test_stepviewslides_get_id(self, myStepViewSlides):
        """Test for method Step.get_id"""
        if myStepViewSlides:
            step = myStepViewSlides['stepdata']
            assert myStepViewSlides['step'].get_id() == step['id']
        else:
            pass

    def test_stepviewslides_get_prompt(self, myStepViewSlides):
        """
        Test method for the get_prompt method of the StepRedirect class.
        This test assumes that the selected npc is Stephanos. It also assumes
        that the step is 30.
        """
        if myStepViewSlides:
            case = myStepViewSlides['casedata']
            step = myStepViewSlides['stepdata']
            # get actual prompt output
            actual = myStepViewSlides['step'].get_prompt(username=case['name'],
                                                 new_badges=case['new_badges'])
            # assemble expected prompt
            tags = db((db.tags.id == db.badges.tag) &
                    (db.tags.id.belongs(case['new_badges']))).select().as_list()

            # assemble the badge list
            badges = [row['badges']['id'] for row in tags]
            if isinstance(badges[0], list):
                # anticipating possibility that badges could match multiple tags
                badges = [i for lst in badges for i in lst]
            else:
                pass

            # build list of badges
            badgerows = db(db.badges.id.belongs(badges)
                           ).select(db.badges.id,
                                    db.badges.badge_name,
                                    db.badges.description)

            badge_list = UL(_class='badge_list')
            for b in badgerows:
                badge_list.append(LI(SPAN(b.badge_name, _class='badge_name'),
                                    ' for ',
                                    b.description))

            # assemble deck list
            deck_ids = [row['tags']['slides'] for row in tags]
            if isinstance(deck_ids[0], list):
                # anticipating possibility that decks could match multiple tags
                deck_ids = (i for lst in deck_ids for i in lst)
            deck_ids = list(set(deck_ids))

            deck_table = db.plugin_slider_decks
            deck_query = db(deck_table.id.belongs(deck_ids))
            decknames = deck_query.select(deck_table.id,
                                          deck_table.deck_name,
                                          orderby=deck_table.position)
            decklist = UL(_class='slide_list')
            for d in decknames:
                decklist.append(LI(A(d.deck_name, _href=URL('listing',
                                                            'slides',
                                                            args=[d.id]))))
            p = step['raw_prompt']
            expect_prompt = p.replace('[[user]]', case['name'])
            expect_prompt = expect_prompt.replace('[[badge_list]]',
                                                  badge_list.xml())
            expect_prompt = expect_prompt.replace('[[slides]]',
                                                  decklist.xml())
            # get list of expected npc images
            npc_images = [npc_data[n]['image'] for n in step['npc_list']
                          if n in case['npcs_here']]

            print 'METHOD OUTPUT\n', actual['prompt']
            print 'EXPECTED\n', expect_prompt
            assert actual['prompt'] == expect_prompt
            assert actual['instructions'] == step['instructions']
            assert actual['npc_image'] in npc_images

    #def test_stepviewslides_make_replacements(self, myStepViewSlides):
        #"""
        #docstring for test_step_stepviewslides_make_replacements

        #"""
        #sd = step_data_store[127]['case1']
        #prompt = myStepViewSlides._make_replacements(raw_prompt=sd['raw_prompt'],
                                                    #username=sd['username'],
                                                    #new_badges=[5, 6])
        #print prompt, '\n'
        #print sd['final_prompt']
        #assert prompt == sd['final_prompt']

    def test_stepviewslides_get_tags(self, myStepViewSlides):
        """
        Test for method StepViewSlides.get_tags

        The one tag that should be returned for all steps of this class is tag
        80.
        """
        if myStepViewSlides:
            actual = myStepViewSlides['step'].get_tags()
            expected = myStepViewSlides['stepdata']
            assert actual == {'primary': expected['tags'],
                              'secondary': expected['tags_secondary']}
            assert actual['primary'] == [80]
        else:
            pass

    def test_stepviewslides_get_responder(self, myStepViewSlides):
        """Test for method StepViewSlides.get_responder"""
        if myStepViewSlides:
            actual = myStepViewSlides['step'].get_responder().xml()
            map_button = A("Map", _href=URL('walk'),
                           cid='page',
                           _class='button-yellow-grad back_to_map '
                           'icon-location')
            expected = DIV(map_button).xml()
            assert actual == expected
        else:
            pass

    def test_stepviewslides_get_npc(self, myStepViewSlides):
        """Test for method StepViewSlides.get_npc"""
        if myStepViewSlides:
            actual = myStepViewSlides['step'].get_npc()
            expected = myStepViewSlides['stepdata']
            case = myStepViewSlides['casedata']
            assert isinstance(actual, Npc)
            assert actual.get_id() in expected['npc_list']
            assert actual.get_id() in case['npcs_here']
        else:
            pass


class TestStepText():
    '''
    Test class for paideia.StepText
    '''
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestStepText is False')

    def test_steptext_get_responder(self, myStepText):
        if myStepText:
            resp = '<form action="#" autocomplete="off" '\
                   'enctype="multipart/form-data" method="post">'\
                   '<table>'\
                   '<tr id="no_table_response__row">'\
                   '<td class="w2p_fl">'\
                   '<label for="no_table_response" '\
                   'id="no_table_response__label">Response: </label>'\
                   '</td>'\
                   '<td class="w2p_fw">'\
                   '<input class="string" id="no_table_response" '\
                   'name="response" type="text" value="" />'\
                   '</td>'\
                   '<td class="w2p_fc"></td>'\
                   '</tr>'\
                   '<tr id="submit_record__row">'\
                   '<td class="w2p_fl"></td>'\
                   '<td class="w2p_fw"><input type="submit" '\
                   'value="Submit" /></td>'\
                   '<td class="w2p_fc"></td></tr></table></form>'
            assert myStepText['step'].get_responder().xml() == resp
            assert isinstance(myStepText['step'], StepText)
        else:
            pass

    def test_steptext_get_readable(self, myStepText):
        """Unit tests for StepText._get_readable() method"""
        if myStepText:
            output = myStepText['stepdata']['readable']
            assert myStepText['step']._get_readable() == output
        else:
            pass

    def test_steptext_get_reply(self, myStepText):
        """Unit tests for StepText._get_reply() method"""
        if myStepText:
            step = myStepText['stepdata']
            response = myStepText['user_response']
            expected = {'reply_text': myStepText['reply_text'],
                        'tips': step['tips'],
                        'readable_short': step['readable']['readable_short'],
                        'readable_long': step['readable']['readable_long'],
                        'score': myStepText['score'],
                        'times_right': myStepText['times_right'],
                        'times_wrong': myStepText['times_wrong'],
                        'user_response': myStepText['user_response']}
            actual = myStepText['step'].get_reply(user_response=response)
            assert actual['reply_text'] == expected['reply_text']
            assert actual['readable_short'] == expected['readable_short']
            assert actual['readable_long'] == expected['readable_long']
            assert actual['tips'] == expected['tips']
            assert actual['times_right'] == expected['times_right']
            assert actual['times_wrong'] == expected['times_wrong']
            assert actual['user_response'] == expected['user_response']


class TestStepMultiple():
    '''
    Test class for paideia.StepMultiple
    '''
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestStepMultiple is False')

    def test_stepmultiple_get_responder(self, myStepMultiple):
        """Unit testing for get_responder method of StepMultiple."""
        if myStepMultiple:
            # value of _formkey input near end is variable, so matched with .*
            expected = myStepMultiple['resp_text']
            actual = myStepMultiple['step'].get_responder().xml()
            assert re.match(expected, actual)
        else:
            pass

    def test_stepmultiple_get_reply(self, myStepMultiple):
        """Unit testing for get_reply method of StepMultiple."""
        if myStepMultiple:
            step = myStepMultiple['stepdata']
            response = myStepMultiple['user_response']

            expected = {'reply_text': myStepMultiple['reply_text'],
                        'tips': step['tips'],
                        'readable_short': step['readable']['readable_short'],
                        'readable_long': step['readable']['readable_long'],
                        'score': myStepMultiple['score'],
                        'times_right': myStepMultiple['times_right'],
                        'times_wrong': myStepMultiple['times_wrong'],
                        'user_response': myStepMultiple['user_response']}
            actual = myStepMultiple['step'].get_reply(user_response=response)
            assert actual['reply_text'] == expected['reply_text']
            assert actual['readable_short'] == expected['readable_short']
            assert actual['readable_long'] == expected['readable_long']
            assert actual['tips'] == expected['tips']
            assert actual['times_right'] == expected['times_right']
            assert actual['times_wrong'] == expected['times_wrong']
            assert actual['user_response'] == expected['user_response']


class TestStepEvaluator():
    """Class for evaluating the submitted response string for a Step"""
    pytestmark = pytest.mark.skipif('not global_runall and '
                                    'not global_run_TestStepEvaluator')

    def test_stepevaluator_get_eval(self, myStepEvaluator):
        """Unit tests for StepEvaluator.get_eval() method."""
        if myStepEvaluator:
            evl = myStepEvaluator
            response = evl['user_response']
            expected = {'reply_text': evl['reply_text'],
                        'tips': evl['tips'],
                        'score': evl['score'],
                        'times_wrong': evl['times_wrong'],
                        'times_right': evl['times_right'],
                        'user_response': response}

            actual = myStepEvaluator['eval'].get_eval(response)
            assert actual['score'] == expected['score']
            assert actual['reply'] == expected['reply_text']
            assert actual['times_wrong'] == expected['times_wrong']
            assert actual['times_right'] == expected['times_right']
            assert actual['user_response'] == expected['user_response']
            assert actual['tips'] == expected['tips']
        else:
            pass


class TestMultipleEvaluator():
    """
    Unit testing class for paideia.MultipleEvaluator class.
    """
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestMultipleEvaluator '
                                    'is False')

    def test_multipleevaluator_get_eval(self, myMultipleEvaluator):
        """Unit tests for multipleevaluator.get_eval() method."""
        if myMultipleEvaluator:
            evl = myMultipleEvaluator
            response = evl['user_response']
            expected = {'reply_text': evl['reply_text'],
                        'tips': evl['tips'],
                        'score': evl['score'],
                        'times_wrong': evl['times_wrong'],
                        'times_right': evl['times_right'],
                        'user_response': response}

            actual = myMultipleEvaluator['eval'].get_eval(response)
            assert actual['score'] == expected['score']
            assert actual['reply'] == expected['reply_text']
            assert actual['times_wrong'] == expected['times_wrong']
            assert actual['times_right'] == expected['times_right']
            assert actual['user_response'] == expected['user_response']
            assert actual['tips'] == expected['tips']
        else:
            pass


class TestPath():
    """Unit testing class for the paideia.Path object"""
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestPath is False')

    def test_path_get_id(self, mypath):
        """unit test for Path.get_id()"""
        expected = mypath['id']
        actual = mypath['path'].get_id()
        assert actual == expected

    def test_path_prepare_for_prompt(self, mypath, mysteps):
        """unit test for Path._prepare_for_prompt()"""
        # TODO: add logic to test progression to subsequent step of multistep
        # path
        pid = mypath['id']
        sid = mypath['steps'][0]
        if mysteps['id'] == sid:
            #step = mysteps
            #case = mypath['casedata']
            expected = {'path_id': pid,
                        'step_id': sid}

            path = mypath['path']
            actual = path._prepare_for_prompt()

            assert actual is True
            assert path.step_for_prompt.get_id() == expected['step_id']
            assert path.steps == []
        else:
            pass

    def test_path_get_step_for_prompt(self, mypath, mysteps):
        """unit test for Path.get_step_for_prompt()"""
        # TODO: add logic to test progression to subsequent step of multistep
        # path
        # TODO: add logic to test block generation; returning block
        pid = mypath['id']
        sid = mypath['steps'][0]
        if mysteps['id'] == sid:
            step = mysteps
            case = mypath['casedata']
            expected = {'path_id': pid,
                        'step_id': sid,
                        'alternate_step_id': sid,
                        'locations': step['locations'],
                        'tags': {'primary': step['tags'],
                                'secondary': step['tags_secondary']},
                        'npc_list': [s for s in step['npc_list']
                                    if s in case['npcs_here']],
                        'loc': case['loc'].get_id(),
                        'steps': [],  # only step has been removed
                        'type': step['type']
                        }

            path = mypath['path']
            actual = mypath['path'].get_step_for_prompt()

            # redirect step id in cases where redirect Block is triggered
            if (case['casenum'] == 2) and (sid == 101):
                expected['tags'] = {'primary': [70],
                                    'secondary': []}
                expected['npc_list'] = [14, 8, 2, 40, 31, 32, 41, 1, 17, 42]
                expected['locations'] = [3, 1, 2, 4, 12, 13, 14, 6, 7, 8,
                                         11, 5, 9, 10]
                expected['type'] = StepRedirect

                assert path.step_for_reply is None
                assert path.step_for_prompt.get_id() == sid
                assert actual.get_id() == 30
            else:
                assert path.step_for_prompt is None
                assert path.step_for_reply.get_id() == sid
                assert actual.get_id() == sid

            assert path.get_id() == expected['path_id']
            assert actual.get_tags() == expected['tags']
            assert actual.get_locations() == expected['locations']
            assert case['loc'].get_id() in expected['locations']
            assert actual.get_npc().get_id() in expected['npc_list']
            assert actual.get_npc().get_id() in case['npcs_here']
            assert type(actual) == expected['type']
            assert isinstance(actual, expected['type'])
            assert path.steps == expected['steps']
        else:
            pass

    def test_path_check_for_blocks(self, mypath, mysteps):
        """
        unit test for Path.check_for_blocks()

        Since this method only checks for the presence of blocks on the current
        path, it will return a blocking step for each test case (even if that
        case would not normally have a block set.)
        """
        #pid = mypath['id']
        sid = mypath['steps'][0]
        if mysteps['id'] == sid:
            path = mypath['path']
            locs = [2, 3]

            kwargs = {'step_id': 30,
                      'loc': path.loc,
                      'prev_loc': path.prev_loc_id,
                      'prev_npc_id': path.prev_npc_id}
            expected = [Block('redirect', kwargs=kwargs, data=locs)]
            path.blocks = expected[:]
            path.step_for_prompt = sid

            actual = path.check_for_blocks(locs)

            print expected
            assert actual == expected[0].get_step()
            assert path.blocks == []
            assert path.step_for_prompt == sid
            assert path.step_sent_id == 30
        else:
            pass

    def test_path_redirect(self, mypath, mysteps):
        """
        unit test for Path.redirect().

        Since redirect() doesn't check any conditions before appending redirect
        Block, all cases tested should result in a Block (even if
        check_for_blocks() would not normally call redirect() for the case).
        """
        sid = mypath['steps'][0]
        if mysteps['id'] == sid:
            #step = mysteps
            path = mypath['path']
            locs = [2, 3]

            kwargs = {'step_id': 30,
                      'loc': path.loc,
                      'prev_loc': path.prev_loc_id,
                      'prev_npc_id': path.prev_npc_id}
            expected = [Block('redirect', kwargs=kwargs, data=locs)]

            actual = path.redirect(locs)
            actualblocks = path.blocks

            assert isinstance(path.blocks, list)
            assert len(actualblocks) == len(expected)
            for n in range(0, len(expected)):
                actualstep = path.blocks[n].get_step()
                expectedstep = expected[n].get_step()
                assert actualstep.get_id() == expectedstep.get_id()
                assert actualstep.get_id() == kwargs['step_id']
                assert isinstance(actualstep, StepRedirect)
            assert actual is None
        else:
            pass

    def test_path_get_step_for_reply(self, mypath, mysteps):
        """
        Unit test for method paideia.Path.get_step_for_reply.
        """
        sid = mypath['steps'][0]
        if mysteps['id'] == sid:
            path = mypath['path']
            case = mypath['casedata']
            kwargs = {'step_id': sid,
                      'loc': case['loc'],
                      'prev_loc': case['prev_loc'],
                      'prev_npc_id': case['prev_npc_id']}
            expected = StepFactory().get_instance(db=db, **kwargs)
            path.step_for_reply = copy(expected)

            actual = path.get_step_for_reply()

            assert path.step_for_prompt is None
            assert path.step_for_reply is None
            assert actual.get_id() == expected.get_id()
            assert path.step_sent_id == expected.get_id()
            assert not isinstance(actual, StepRedirect)
            assert not isinstance(actual, StepQuotaReached)
            assert not isinstance(actual, StepViewSlides)
            assert not isinstance(actual, StepAwardBadges)


class TestUser():
    """unit testing class for the paideia.User class"""
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestUser is False')

    def test_user_get_id(self, myuser):
        """
        Unit test for User.get_id() method.
        """
        #auth = current.auth
        uid = 1  # TODO: change to use auth.user_id
        assert myuser['user'].get_id() == uid

    def test_user_is_stale(self, myuser):
        """
        Unit test for User.is_stale() method.
        """
        now = datetime.datetime(2013, 01, 02, 14, 0, 0)
        tzn = 'America/Toronto'
        cases = [{'start': datetime.datetime(2013, 01, 02, 9, 0, 0),
                  'expected': False},
                 {'start': datetime.datetime(2013, 01, 02, 9, 0, 0),
                  'expected': False},
                 {'start': datetime.datetime(2013, 01, 02, 3, 0, 0),
                  'expected': True},
                 {'start': datetime.datetime(2012, 12, 29, 14, 0, 0),
                  'expected': True}]
        for c in cases:
            print 'start:', c['start']
            print 'expected:', c['expected']
            actual = myuser['user'].is_stale(now=now, start=c['start'],
                                     tz_name=tzn, db=db)
            assert actual == c['expected']

    def test_user_get_path(self, myuser):
        user = myuser['user']
        case = myuser['casedata']
        if user.cats_counter < 5:
            tags_due = [t for cat in case['categories_start'].values() for t in cat]
        elif user.cats_counter >= 5:
            tags_due = [t for cat in case['categories_out'].values() for t in cat]

        path_rows = db(db.paths.id > 0
                       ).select().find(lambda row:
                                       [t for t in row.tags if t in tags_due]
                                       and
                                       db.steps(row.steps[0]).status != 2
                                       and
                                       db.steps(row.steps[0]).locations
                                       and
                                       [l for l in db.steps(row.steps[0]).locations
                                        if l == case['loc'].get_id()])
        expected_paths = [p.id for p in path_rows]
        actual = user.get_path(case['loc'])
        assert actual.get_id() in expected_paths
        assert isinstance(actual, Path)
        assert isinstance(actual.steps[0], Step)

    def test_user_get_new_badges(self, myuser):
        """
        Unit test for User.get_new_badges().
        """
        user = myuser['user']
        user.new_badges = [1, 2, 3]
        expected = [1, 2, 3]
        actual = user.get_new_badges()

        assert actual == expected

    def test_user_get_promoted(self, myuser):
        """
        Unit test for User.get_promoted().
        """
        user = myuser['user']
        user.promoted = {'cat2': [1], 'cat3': [2], 'cat4': [3]}
        expected = {'cat2': [1], 'cat3': [2], 'cat4': [3]}
        actual = user.get_promoted()

        assert actual == expected

    def test_user_get_categories(self, myuser):
        """
        Unit test for User._get_categories() method.
        """
        user = myuser['user']
        case = myuser['casedata']
        print 'cats_counter:', user.cats_counter
        if user.cats_counter < 5:
            expected = case['categories_start']
        elif user.cats_counter >= 5:
            expected = case['categories_out']
        actual = user._get_categories(categories=case['tag_progress'],
                                      old_categories=None)
        print 'actual:\n', actual
        print 'expected:\n', expected

        # this avoids problem of lists being in different orders
        for c, l in expected.iteritems():
            assert len(actual[c]) == len([t for t in l if t in actual[c]])

    def test_user_get_old_categories(self, myuser):
        """
        TODO: at the moment this is only testing initial state in which there
        are no old categories yet.
        """
        #case = myuser['casedata']
        user = myuser['user']
        expected = None
        #expected = case['tag_progress']
        #del expected['latest_new']

        actual = user._get_old_categories()

        assert actual == expected
        #for c, l in actual.iteritems():
            #assert len([i for i in l if i in expected[c]]) == len(expected[c])
            #assert len(l) == len(expected[c])

    def test_user_complete_path(self, myuser):
        user = myuser['user']
        case = myuser['casedata']
        pathid = case['paths']['cat1'][0]
        path = Path(path_id=pathid, loc=case['loc'])
        path.completed_steps.append(path.steps.pop(0))
        user.path = copy(path)
        assert user._complete_path() is True
        assert user.path is None
        assert user.last_npc.get_id() in case['npcs_here']
        assert user.last_loc.get_id() == case['loc'].get_id()
        assert user.completed_paths[-1].get_id() == path.get_id()
        assert isinstance(user.completed_paths[-1], Path)


class TestCategorizer():
    """
    Unit testing class for the paideia.Categorizer class
    """
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestCategorizer is False')

    def test_categorizer_categorize(self, mycategorizer):
        """
        Unit test for the paideia.Categorizer.categorize method.

        Test case data provided (and parameterized) by mycases fixture via the
        mycategorizer fixture.
        """
        cat = mycategorizer
        out = {'cats': cat['categories_out'],
               't_prog': cat['tag_progress_out'],
               'nt': cat['new_tags'],
               'pro': cat['promoted'],
               'de': cat['demoted']}
        real = cat['categorizer'].categorize_tags()
        for c, l in out['t_prog'].iteritems():
            if isinstance(l, int):
                real['tag_progress'][c] == l
            else:
                for t in l:
                    assert t in real['tag_progress'][c]
        if out['nt']:
            for t in real['new_tags']:
                assert t in out['nt']
        for c, l in out['pro'].iteritems():
            for t in l:
                assert t in real['promoted'][c]
        for c, l in out['de'].iteritems():
            for t in l:
                assert t in real['demoted'][c]
        for c, l in out['cats'].iteritems():
            for t in l:
                assert t in real['categories'][c]

    def test_categorizer_core_algorithm(self, mycategorizer):
        """
        Unit test for the paideia.Categorizer._core_algorithm method

        Case numbers correspond to the cases (user performance scenarios) set
        out in the myrecords fixture.
        """
        cat = mycategorizer
        output = cat['core_out']
        core = cat['categorizer']._core_algorithm()
        assert core == output

    def test_categorizer_introduce_tags(self, mycategorizer):
        """Unit test for the paideia.Categorizer._introduce_tags method"""
        catzer = mycategorizer['categorizer']
        newlist = catzer._introduce_tags()
        if newlist:
            for n in newlist:
                assert n in mycategorizer['introduced']
        else:
            assert newlist is False
        assert len(newlist) == len(mycategorizer['introduced'])
        assert catzer.rank == mycategorizer['tag_progress']['latest_new'] + 1

    def test_categorizer_add_untried_tags(self, mycategorizer):
        """Unit test for the paideia.Categorizer._add_untried_tags method"""
        mz = mycategorizer
        catin = mz['core_out']
        catout = mz['untried_out']
        for cat, lst in mz['categorizer']._add_untried_tags(catin).iteritems():
            for tag in lst:
                assert tag in catout[cat]
            assert len(lst) == len(catout[cat])

    def test_categorizer_find_cat_changes(self, mycategorizer):
        """Unit test for the paideia.Categorizer._find_cat_changes method."""
        mz = mycategorizer
        actual = mz['categorizer']._find_cat_changes(mz['untried_out'],
                                                     mz['categorizer'
                                                        ].old_categories)
        for t in actual['categories']:
            if actual['categories']:
                assert t in mz['untried_out']
        for t in actual['demoted']:
            if actual['demoted']:
                assert t in mz['demoted']
        for t in actual['promoted']:
            if actual['promoted']:
                assert t in mz['promoted']

    def test_categorizer_add_secondary_right(self, mycategorizer):
        """Unit test for the paideia.Categorizer._add_secondary_right method."""
        mz = mycategorizer
        recsin = mz['tag_records']
        expected = mz['tag_records_out']
        realout = mz['categorizer']._add_secondary_right(recsin)
        for r in realout:
            ri = realout.index(r)
            assert r['tag_id'] == expected[ri]['tag_id']
            assert r['last_right'] == expected[ri]['last_right']
            assert r['last_wrong'] == expected[ri]['last_wrong']
            assert r['times_right'] == expected[ri]['times_right']
            assert r['last_wrong'] == expected[ri]['last_wrong']
            assert r['secondary_right'] == expected[ri]['secondary_right']


class TestWalk():
    """
    A unit testing class for the paideia.Walk class.
    """
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestWalk is False')

    def test_walk_get_user(self, mywalk):
        """Unit test for paideia.Walk._get_user()"""
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        if case['casenum'] == 1:
            localias = case['localias']
            userdata = {'first_name': 'Joe', 'id': 1}
            tag_records = case['tag_records']
            tag_progress = case['tag_progress']

            actual = thiswalk._get_user(userdata=userdata, localias=localias,
                                        tag_records=tag_records,
                                        tag_progress=tag_progress)
            assert isinstance(actual, User)
            assert actual.get_id() == userdata['id']
        else:
            pass

    def test_walk_map(self, mywalk):
        """Unit test for paideia.Walk._get_user()"""
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        if case['casenum'] == 1:
            expected = {'map_image': '/paideia/static/images/town_map.svg',
                        'locations': [{'alias': 'None',
                                    'bg_image': 8,
                                    'id': 3},
                                    {'alias': 'domus_A',
                                    'bg_image': 8,
                                    'id': 1},
                                    {'alias': '',
                                    'bg_image': 8,
                                    'id': 2},
                                    {'alias': None,
                                    'bg_image': None,
                                    'id': 4},
                                    {'alias': None,
                                    'bg_image': None,
                                    'id': 12},
                                    {'alias': 'bath',
                                    'bg_image': 17,
                                    'id': 13},
                                    {'alias': 'gymnasion',
                                    'bg_image': 15,
                                    'id': 14},
                                    {'alias': 'shop_of_alexander',
                                    'bg_image': 16,
                                    'id': 6},
                                    {'alias': 'ne_stoa',
                                    'bg_image': 18,
                                    'id': 7},
                                    {'alias': 'agora',
                                    'bg_image': 16,
                                    'id': 8},
                                    {'alias': 'synagogue',
                                    'bg_image': 15,
                                    'id': 11},
                                    {'alias': None,
                                    'bg_image': None,
                                    'id': 5},
                                    {'alias': None,
                                    'bg_image': None,
                                    'id': 9},
                                    {'alias': None,
                                    'bg_image': None,
                                    'id': 10}
                                    ]}
            actual = thiswalk.map()
            for m in expected['locations']:
                i = expected['locations'].index(m)
                assert actual['locations'][i]['alias'] == m['alias']
                assert actual['locations'][i]['bg_image'] == m['bg_image']
                assert actual['locations'][i]['id'] == m['id']
            assert actual['map_image'] == expected['map_image']
        else:
            pass

    def test_walk_ask(self, mywalk):
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        c = case['casenum']
        step = mywalk['stepdata']
        s = step['id']
        combinations = {1: 1,  # path 2
                        1: 2,  # path 3
                        1: 101,  # path 89, multiple
                        2: 101,  # path 89, redirect (step 30)
                        2: 19,  # path 19
                        3: 19}  # path 19
        if c in combinations.keys() and s == combinations[c]:
            expected = {'prompt': step['final_prompt'],
                        'instructions': step['instructions'],
                        'responder': step['responder']}
                        # TODO: check for image -- just hard to predict
                        #image : '/paideia/static/images/images.image.bb48641f0122d2b6.'
                        #'696d616765732e696d6167652e383136303330663934646664646561312e3'
                        #'4343732363137373639366536373230333432653733373636372e737667.svg'
            print 'PATHS', step['paths'][0]
            print 'RESPONDER: \n'
            print expected['responder']
            actual = thiswalk.ask(path=step['paths'][0])

            assert actual['prompt']['prompt'] == expected['prompt']
            assert actual['prompt']['instructions'] == expected['instructions']
            assert actual['prompt']['npc_image'] == expected['image']
            assert actual['responder'].xml() == expected['responder']
        else:
            pass

    def test_walk_reply(self, mywalk):
        """Unit test for paideia.Walk.reply() method."""
        # TODO: make decorator for test methods to filter specific cases/steps
        # coming from the parameterized fixtures
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        step = mywalk['stepdata']
        if case['casenum'] == 1:
            for k, v in step['user_responses'].iteritems():
                response_string = v
                expected = {'reply': step['reply_text'][k],
                            'bug_reporter': ''}
                            # TODO: add bug reporter string
                            # TODO: put in safety in case of empty form

                actual = thiswalk.reply(response_string),

                assert actual['reply'] == expected['reply']
                assert actual['bug_reporter'] == expected['bug_reporter']

    def test_walk_record_cats(self, mywalk):
        """
        Unit tests for Walk._record_cats()
        """
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        if case['casenum'] == 1:
            tag_progress = case['tag_progress_out']
            user_id = thiswalk._get_user().get_id()
            promoted = case['promoted']
            new_tags = case['new_badges']
            promoted['cat1'] = new_tags
            expected_progress = tag_progress
            expected_begun = {t: cat for cat in promoted for t in cat}

            # call the method and test its return value
            assert thiswalk._record_cats(tag_progress, promoted,
                                       new_tags, db) is True

            # test record insertion for db.tag_progress
            actual_select_tp = db(db.tag_progress.name == user_id).select()
            assert len(actual_select_tp) == 1

            actual_record_tp = actual_select_tp.first()
            for k, v in actual_record_tp.iteritems():
                assert v == expected_progress[k]

            # test record insertion for db.badges_begun
            actual_select_bb = db(db.badges_begun.name == user_id).select()
            # one badges_begun row for each of user's tag_records rows
            user_tag_records = db(db.tag_records.name == user_id).select()
            assert len(actual_select_bb) == len(user_tag_records)
            # check that new values were entered
            now = datetime.datetime.utcnow()
            for t, v in {tag: cat for tag, cat in expected_begun.iteritems()}:
                actual_select_bb.find(lambda row: row.tag_id == t)
                assert len(actual_select_bb) == 1
                assert actual_select_bb.first()[v] == now
        else:
            pass

    def test_walk_record_step(self, mywalk):
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

            expected_tag_records = [t for t in case['tag_records'] if t in step_tags]

            # call the method and collect return value
            actual_log_id = thiswalk._record_step(user_id, step_id, path_id,
                                                score, expected_tag_records)

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
                                                       row.tag == l['tag_id'])
                assert len(for_this_tag) == 1

                for k in l.keys():
                    assert for_this_tag[k] == l[k]
        else:
            pass

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
        else:
            pass


class TestPathChooser():
    '''
    Unit testing class for the paideia.PathChooser class.
    '''
    pytestmark = pytest.mark.skipif('global_runall is False '
                                    'and global_run_TestPathChooser is False')

    def test_pathchooser_choose(self, mypathchooser):
        newpath = mypathchooser['pathchooser'].choose()
        assert newpath[0].id in [r for c in mypathchooser['paths'].values() for r in c if len(c) > 0]
        assert newpath[2] in range(1, 5)

    def test_pathchooser_order_cats(self, mypathchooser):
        pc = mypathchooser['pathchooser']._order_cats()
        ind = pc.index(1)
        if len(pc) >= (ind + 2):
            assert pc[ind + 1] == 2
        if len(pc) >= (ind + 3):
            assert pc[ind + 2] == 3
        if len(pc) >= (ind + 4):
            assert pc[ind + 3] == 4
        if ind != 0:
            assert pc[ind - 1] == 4
        assert len(pc) == 4
        assert pc[0] in [1, 2, 3, 4]
        assert pc[1] in [1, 2, 3, 4]
        assert pc[2] in [1, 2, 3, 4]
        assert pc[3] in [1, 2, 3, 4]

    def test_pathchooser_paths_by_category(self, mypathchooser):
        cpaths, category = mypathchooser['pathchooser']._paths_by_category('1')
        allpaths = mypathchooser['paths']
        pathids = allpaths['cat{}'.format(category)]
        expected = db(db.paths).select()
        expected = expected.find(lambda row: row.id in pathids)
        assert len(cpaths) == len(expected)
        for row in cpaths:
            assert row.id in [r.id for r in expected]

    def test_pathchooser_choose_from_cat(self, mypathchooser):
        allpaths = mypathchooser['paths']
        pathids = allpaths['cat{}'.format(1)]
        expected = db(db.paths).select()
        expected = expected.find(lambda row: row.id in pathids)
        print expected

        newpath = mypathchooser['pathchooser']._choose_from_cat(expected, 1)
        assert newpath[0].id in mypathchooser['paths']['cat1']
        assert newpath[1] in [l for l in db.steps(newpath[0].steps[0]).locations]
        assert newpath[2] == 1
