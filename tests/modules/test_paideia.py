# -*- coding: utf-8 -*-
# Unit tests for the paideia module

import pytest
from paideia import Npc, Location, User, PathChooser, Path, Categorizer, Walk
from paideia import StepFactory, StepText, StepMultiple, NpcChooser  # Step
from paideia import StepRedirect, StepViewSlides, StepAwardBadges
from paideia import StepEvaluator, MultipleEvaluator, StepQuotaReached
from paideia import A, URL, DIV, LI, UL, SPAN
#from paideia import Block, BlockRedirect, BlockAwardBadges, BlockViewSlides
from gluon import current
request = current.request
# from gluon.dal import Rows
import datetime
# from pprint import pprint
import re
from random import randint

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


@pytest.fixture(params=[n for n in [1, 2, 30, 101, 125, 126, 127]])
def mysteps(request):
    """
    Test fixture providing step information for unit tests.
    This fixture is parameterized, so that tests can be run with each of the
    steps or with any sub-section (defined by a filtering expression in the
    test). This step fixture is also used in the mycases fixture.
    """
    the_step = request.param
    steps = {1: {'id': 1,
                 'type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1, 17],
                 'locations': [3, 1, 13, 7, 8, 11],
                 'raw_prompt': 'How could you write the word "meet" using '
                               'Greek letters?',
                 'final_prompt': 'How could you write the word "meet" using '
                                 'Greek letters?',
                 'instructions': ['Focus on finding Greek letters that make '
                                  'the *sounds* of the English word. Don\'t '
                                  'look for Greek "equivalents" for each '
                                  'English letter.'],
                 'tags': [61],
                 'tags_secondary': [],
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
                 'type': StepText,
                 'widget_type': 1,
                 'npc_list': [8, 2, 32, 1],
                 'locations': [3, 1, 13, 7, 8, 11],
                 'raw_prompt': 'How could you write the word "bought" using '
                               'Greek letters?',
                 'final_prompt': 'How could you write the word "bought" using '
                                 'Greek letters?',
                 'instructions': None,
                 'tags': [61],
                 'tags_secondary': [],
                 'responses': {'response1': '^β(α|ο)τ$'},
                 'readable': {'readable_short': [u'βατ', u'βοτ'],
                              'readable_long': [u'βατ', u'βοτ']},
                 'reply_text': {'correct': 'Right. Κάλον.',
                                'incorrect': 'Incorrect. Try again!'},
                 'tips': None,  # why is this None, but step 1 its []?
                 'user_responses': {'correct': 'βοτ',
                                    'incorrect': 'βλα'}
                 },
             30: {'id': 30,
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
                  'tags_secondary': []},
             101: {'id': 101,
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
                   'readable': {'readable_short': ['ναι'],
                                'readable_long': None},
                   'reply_text': {'correct': 'Right. Κάλον.',
                                  'incorrect': 'Incorrect. Try again!'},
                   'tips': []},
             125: {'id': 125,
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
                   'tags_secondary': []},
             126: {'id': 126,
                   'type': StepAwardBadges,
                   'widget_type': 8,
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'raw_prompt': 'Congratulations, [[user]]! You\'ve started'
                                 'work on these new badges! [[new_badge_list]]'
                                 'You can click on your name above to '
                                 'see details of your progress so far.',
                   'final_prompt': 'Congratulations, [[user]]![[new_badge_list]]'
                                   'You can click on your name above to '
                                   'see details of your progress so far.',
                   'instructions': None,
                   'tags': [81],
                   'tags_secondary': []},
             127: {'id': 127,
                   'type': StepViewSlides,
                   'widget_type': 6,
                   'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                   'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10],
                   'raw_prompt': 'Congratulations, [[user]]! You\'re ready to '
                                 'start working on some new badges:[[badge_list]]. Before'
                                 'you continue, take some time to view these slide sets:'
                                 '[[slides]]You\'ll find the slides by clicking on the '
                                 '"slides" menu item at top.',
                   'final_prompt': 'Congratulations, Ian! You\'re ready to '
                                   'start working on some new badges:'
                                   '[[badge_list]]. Beforeyou continue, take '
                                   'some time to view these slide sets:'
                                   '<ul class="slide_list">'
                                   '<li>The Alphabet III</li>'
                                   '<li>Case Basics</li>'
                                   '</ul>'
                                   'You\'ll find the slides by clicking on '
                                   'the "slides" menu item at top.',
                   'instructions': None,
                   'tags': [80],
                   'tags_secondary': []}
             }
    return steps[the_step]


@pytest.fixture(params=['case{}'.format(n) for n in range(1, 6)])
def mycases(request, mysteps):
    """
    Text fixture providing various cases for unit tests. For each step,
    several cases are specified, including:
    TODO: write another case to test with promotions present
    promoted_list = You\'ve reached a new level in these badges:
                <ul class="promoted_list"><li></li></ul>
    """
    the_case = request.param
    # same npc and location as previous step
    # replace tag too far ahead (1) with appropriate (61)
    cases = {'case1': {'casenum': 1,
                       'loc': Location(1, db),
                       'mynow': dt('2013-01-29'),
                       'name': 'Ian',
                       'uid': 1,
                       'prev_loc': Location(1, db),
                       'prev_npc_id': 2,
                       'npcs_here': [2, 8, 14, 17, 31, 40, 41, 42],
                       'pathid': 3,
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
                       'paths': {'cat1': [1, 2, 3, 5, 8, 63, 64, 70, 95, 96,
                                          97, 99, 102, 104, 256, 277],
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
                       'new_badges': [62],
                       'promoted': {'cat2': [61]},
                       'demoted': {},
                       'steps_here': [1, 2, 30, 125, 126, 127],
                       'completed': []}
             }
    return cases[the_case]


@pytest.fixture
def mynpcchooser(mysteps, mycases):
    if mysteps['id'] in mycases['steps_here']:
        if mycases['casenum'] == 1:
            step = StepFactory().get_instance(db=db,
                                              step_id=mysteps['id'],
                                              loc=mycases['loc'],
                                              prev_loc=mycases['prev_loc'],
                                              prev_npc_id=mycases['prev_npc_id'])
            location = mycases['loc']
            prev_npc = Npc(mycases['prev_npc_id'], db)
            prev_loc = mycases['prev_loc']
            return {'chooser': NpcChooser(step, location, prev_npc, prev_loc),
                    'stepdata': mysteps}


@pytest.fixture
def mywalk(mycases):
    """pytest fixture providing a paideia.Walk object for testing"""
    userdata = {'first_name': mycases['user'], 'id': 1}
    tag_progress = mycases['tag_progress']
    tag_records = mycases['tag_records']
    localias = mycases['loc'].get_alias()
    return Walk(localias,
                userdata=userdata,
                tag_records=tag_records,
                tag_progress=tag_progress,
                db=db)


@pytest.fixture
def mypathchooser(mycases):
    """pytest fixture providing a paideia.PathChooser object for testing"""
    klist = ['cat1', 'cat2', 'cat3', 'cat4', 'rev1', 'rev2', 'rev3']
    cats = {k: v for k, v in mycases['tag_progress'] if k in klist}
    pc = PathChooser(cats, mycases['loc'], mycases['completed'], db=db)
    return {'pathchooser': pc, 'paths': mycases['paths']}


@pytest.fixture
def mycategorizer(mycases):
    """A pytest fixture providing a paideia.Categorizer object for testing."""
    rank = mycases['tag_progress']['latest_new']
    cats_in = {k: v for k, v in mycases['tag_progress'].iteritems()
               if not k == 'latest_new'}
    cats_out = {k: v for k, v in mycases['tag_progress_out'].iteritems()
                if not k == 'latest_new'}
    tag_rs = mycases['tag_records']
    now = mycases['mynow']
    out = {'categorizer': Categorizer(rank, cats_in, tag_rs, utcnow=now),
           'categories_in': cats_in,
           'categories_out': cats_out,
           'tag_progress': mycases['tag_progress'],
           'tag_progress_out': mycases['tag_progress_out'],
           'core_out': mycases['core_out'],
           'promoted': mycases['promoted'],
           'demoted': mycases['demoted'],
           'new_tags': mycases['new_badges'],
           'introduced': mycases['introduced'],
           'untried_out': mycases['untried_out'],
           'tag_records': tag_rs}
    if 'tag_records_out' in mycases.keys():
        out['tag_records_out'] = mycases['tag_records_out']
    else:
        out['tag_records_out'] = mycases['tag_records']

    return out


@pytest.fixture
def myuser(mycases):
    """A pytest fixture providing a paideia.User object for testing."""
    userdata = db.auth_user(1).as_dict()
    tag_progress = mycases['tag_progress']
    tag_records = mycases['tag_records']
    localias = mycases['loc'].get_alias()
    return User(userdata, localias, tag_records, tag_progress)


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
    the_path = Path(path_id=mycases['pathid'],
                    blocks=mycases['blocks'],
                    loc=mycases['loc'],
                    prev_loc=mycases['prev_loc'],
                    prev_npc_id=mycases['prev_npc_id'],
                    db=db)
    return {'casenum': mycases['casenum'],
            'path': the_path}


@pytest.fixture
def mystep(mycases, mysteps):
    """
    A pytest fixture providing a paideia.Step object for testing.
    """
    stepdata = mysteps
    if (not mycases['loc'].get_id() in mysteps['locations']) or \
       (not [n for n in mycases['npcs_here'] if n in mysteps['npc_list']]):
        return None
    if mysteps['type'] == StepAwardBadges and mycases['casenum'] != 5:
        return None
    if mysteps['type'] == StepViewSlides and mycases['casenum'] != 5:
        return None
    if mysteps['type'] == StepRedirect and mycases['casenum'] != 5:
        return None
    else:
        return {'casenum': mycases['casenum'],
                'step': StepFactory().get_instance(db=db,
                                                   step_id=mysteps['id'],
                                                   loc=mycases['loc'],
                                                   prev_loc=mycases['prev_loc'],
                                                   prev_npc_id=mycases['prev_npc_id']),
                'stepdata': stepdata,
                'casedata': mycases}


@pytest.fixture
def myStepRedirect(mycases, mysteps):
    """
    A pytest fixture providing a paideia.StepRedirect object for testing.
    - same npc and location as previous step
    TODO: write another fixture for a new location and for a new npc
    """
    if mysteps['id'] == 30:
        stepdata = mysteps
        my_args = {'step_id': 30,
                   'loc': mycases['loc'],
                   'prev_loc': mycases['prev_loc'],
                   'prev_npc_id': mycases['prev_npc_id'],
                   'db': db}
        return {'step': StepRedirect(**my_args),
                'stepdata': stepdata}
    else:
        pass


@pytest.fixture
def myStepAwardBadges(mycases, mysteps):
    """
    A pytest fixture providing a paideia.StepAwardBadges object for testing.
    """
    if (mysteps['id'] == 126) and not (mycases['new_badges'] is None):
        kwargs = {'step_id': 126,
                  'loc': mycases['loc'],
                  'prev_loc': mycases['prev_loc'],
                  'prev_npc_id': mycases['prev_npc_id'],
                  'db': db}
        return {'casenum': mycases['casenum'],
                'step': StepAwardBadges(**kwargs),
                'stepdata': mysteps,
                'casedata': mycases}
    else:
        pass


@pytest.fixture
def myStepViewSlides(mycases, mysteps):
    """
    A pytest fixture providing a paideia.StepViewSlides object for testing.
    """
    if mysteps['id'] == 127:
        kwargs = {'step_id': 127,
                  'loc': mycases['loc'],
                  'prev_loc': mycases['prev_loc'],
                  'prev_npc_id': mycases['prev_npc_id'],
                  'db': db}
        return {'step': StepViewSlides(**kwargs),
                'stepdata': mysteps,
                'casedata': mycases}
    else:
        pass


@pytest.fixture
def myStepQuotaReached(mycases, mysteps):
    """
    A pytest fixture providing a paideia.StepQuota object for testing.
    """
    if mysteps['id'] == 125:
        kwargs = {'step_id': 125,
                  'loc': mycases['loc'],
                  'prev_loc': mycases['prev_loc'],
                  'prev_npc_id': mycases['prev_npc_id'],
                  'db': db}
        return {'step': StepFactory().get_instance(**kwargs),
                'stepdata': mysteps,
                'casedata': mycases}
    else:
        pass


@pytest.fixture
def myStepText(mycases, mysteps):
    """
    A pytest fixture providing a paideia.StepText object for testing.
    """
    if mysteps['widget_type'] == 1:
        # following switch alternates correct and incorrect answers
        # actual answers taken from mysteps data
        for n in [0, 1]:
            responses = ['incorrect', 'correct']
            s = StepFactory()
            step = s.get_instance(db=db,
                                  step_id=mysteps['id'],
                                  loc=mycases['loc'],
                                  prev_loc=mycases['prev_loc'],
                                  prev_npc_id=mycases['prev_npc_id'])
            return {'casenum': mycases['casenum'],
                    'step': step,
                    'stepdata': mysteps,
                    'casedata': mycases,
                    'user_response': mysteps['user_responses'][responses[n]],
                    'reply_text': mysteps['reply_text'][responses[n]],
                    'score': n,
                    'times_right': n,
                    'times_wrong': [1, 0][n]}
    else:
        pass


@pytest.fixture
def myStepMultiple(mycases, mysteps):
    """ """
    if mysteps['widget_type'] == 4:
        for n in [0, 1]:
            responses = ['incorrect', 'correct']
            options = mysteps['options']
            right_opt = mysteps['responses']['response1']
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

            kwargs = {'step_id': mysteps['id'],
                      'loc': mycases['loc'],
                      'prev_loc': mycases['prev_loc'],
                      'prev_npc_id': mycases['prev_npc_id'],
                      'db': db}
            return {'casenum': request.param,
                    'step': StepFactory().get_instance(**kwargs),
                    'casedata': mycases,
                    'stepdata': mysteps,
                    'resp_text': resp,
                    'user_response': user_responses[n],
                    'reply_text': mysteps['reply_text'][responses[n]],
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
def myMultipleEvaluator(request, mysteps):
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


# ===================================================================
# Test Classes
# ===================================================================


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

    def test_npcchooser_choose(self, mynpcchooser):
        if mynpcchooser:
            possible = mynpcchooser['stepdata']['npc_list']
            out = mynpcchooser['chooser'].choose()
            assert out.get_id() in possible


class TestStep():
    """
    Unit tests covering the Step class of the paideia module.
    """
    # TODO: parameterize to cover more locations

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


class TestAwardBadges():
    '''
    A subclass of Step. Handles the user interaction when the user is awarded
    new badges.
    '''

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
                      'new_badges': case['new_badges'],
                      'promoted': case['promoted'],
                      'db': db}
            print 'expected', case['new_badges']
            actual = myStepAwardBadges['step'].get_prompt(**kwargs)
            # assemble expected prompt string dynamically
            tags_badges = db(db.badges.tag == db.tags.id).select()
            new_records = tags_badges.find(lambda row:
                                           row.tags.id in case['new_badges'])
            print 'new_records', new_records
            expect_prompt = expect['raw_prompt'].replace('[[user]]',
                                                         case['name'])
            if new_records:
                new_badge_list = UL(_class='new_badge_list')
                for b in new_records:
                    new_badge_list.append(LI(SPAN(b.badges.badge_name,
                                                  _class='badge_name'),
                                             ' for ',
                                             b.badges.description))
                expect_prompt = expect_prompt.replace('[[new_badge_list]]',
                                                      new_badge_list.xml())
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

#class TestStepViewSlides():
    #'''
    #A subclass of Step. Handles the user interaction when the user is awarded
    #new badges.
    #'''

    #def test_awardbadges_get_id(self, myStepViewSlides):
        #"""Test for method Step.get_id"""
        #assert myStepViewSlides.get_id() == 127

    #def test_stepviewslides_get_prompt(self, myStepViewSlides):
        #"""
        #Test method for the get_prompt method of the StepRedirect class.
        #This test assumes that the selected npc is Stephanos. It also assumes
        #that the step is 30.
        #"""
        #sd = step_data_store[127]['case1']
        ## TODO: remove npc numbers that can't be at this
        #npcimgs = [n['image'] for k, n in npc_data.iteritems()
                        #if k in sd['npc_list']]
        #prompt = myStepViewSlides.get_prompt(username=sd['username'],
                                           #new_badges=sd['new_badges'])
        #print 'METHOD OUTPUT\n', sd['final_prompt']
        #print 'EXPECTED\n', prompt['prompt']
        #assert prompt['prompt'] == sd['final_prompt']
        #assert prompt['instructions'] == sd['instructions']
        #assert prompt['npc_image'] in npcimgs

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

    #def test_stepviewslides_get_tags(self, myStepViewSlides):
        #"""
        #Test for method StepViewSlides.get_tags

        #The one tag that should be returned for all steps of this class is tag
        #80.
        #"""
        #assert myStepViewSlides.get_tags() == {'primary': [80], 'secondary': []}

    #def test_stepviewslides_get_responder(self, myStepViewSlides):
        #"""Test for method StepViewSlides.get_responder"""
        #map_button = A("Map", _href=URL('walk'),
                        #cid='page',
                        #_class='button-yellow-grad back_to_map icon-location')
        #assert myStepViewSlides.get_responder().xml() == DIV(map_button).xml()

    #def test_stepviewslides_get_npc(self, myStepViewSlides):
        #"""Test for method StepViewSlides.get_npc"""
        #assert myStepViewSlides.get_npc().get_id() in [14, 8, 2, 40, 31,
                                                            #32, 41, 1, 17, 42]
        #locs = myStepViewSlides.get_npc().get_locations()
        #assert isinstance(locs[0], Location)


class TestStepText():
    '''
    Test class for paideia.StepText
    '''
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
    """Class for evaluating the submitted response string for a StepMultiple"""

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


#class TestPath():
    #"""Unit testing class for the paideia.Path object"""

    #def test_path_get_step_for_prompt(self, mypath):
        #"""docstring for test_get_next_step"""
        #output = 'output{}'.format(mypath['casenum'])
        ## for path 3, text, single step
        #output1 = StepFactory().get_instance(step_id=2, loc=Location(1, db),
                                        #prev_loc=1, prev_npc_id=2, db=db)
        ## for path 89, multiple, single step
        #output2 = StepFactory().get_instance(step_id=101, loc=Location(8, db),
                                        #prev_loc=None, prev_npc_id=1, db=db)
        #ready_path = mypath['path']
        ##ready_path._prepare_for_prompt()
        #pstep = ready_path.get_step_for_prompt()
        #ostep = locals()[output]
        #assert pstep.get_id() == ostep.get_id()
        #assert pstep.get_tags() == ostep.get_tags()
        #assert pstep.get_locations() == ostep.get_locations()
        #assert pstep.get_prompt(username='Joe') \
                                        #== ostep.get_prompt(username='Joe')

    #def test_path_prepare_for_answer(self, mypath):
        #"""Unit test for method paideia.Path.get_step_for_reply."""
        #casenum = mypath['casenum']
        #case = 'case{}'.format(casenum)
        ## path 3, text
        #case1 = {'step_for_reply_end': 2,
                #'step_for_prompt_start': 2,
                #'step_for_prompt_end': None,
                #'step_sent_id': 2}
        ## path 89, multiple
        #case2 = {'step_for_reply_end': 101,
                #'step_for_prompt_start': 101,
                #'step_for_prompt_end': None,
                #'step_sent_id': 101}
        #output = locals()[case]
        #sent_id = output['step_sent_id']
        #test_func = mypath['path'].prepare_for_answer(
                #step_for_prompt=StepFactory().get_instance(
                            #db=db, step_id=output['step_for_prompt_start']),
                #step_for_reply=None,
                #step_sent_id=output['step_sent_id'])
        #assert test_func['step_sent_id'] == output['step_sent_id']
        #assert test_func['step_for_prompt'] == output['step_for_prompt_end']
        #assert test_func['step_for_reply'] == output['step_for_reply_end']

    #def test_path_remove_block(self, mypath):
        #"""Unit test for method paideia.Path.remove_block."""
        #casenum = mypath['casenum']
        #if not casenum in [1, 2]:
            #case = 'case{}'.format(casenum)
            #case3 = {'block_done': Block(), 'blocks': []}
            #output = locals()[case]
            #assert mypath['path'].remove_block() == output

    #def test_path_get_step_for_reply(self, mypath):
        #"""Unit test for method paideia.Path.get_step_for_reply."""
        #out = {1: StepFactory().get_instance(step_id=2, loc=Location(1, db),
                                        #prev_loc=1, prev_npc_id=2, db=db),
              #2: StepFactory().get_instance(step_id=101,
                  #loc=Location(8, db), prev_loc=None, prev_npc_id=1, db=db)
              #}
        #path = mypath['path']
        #pstep = path.get_step_for_prompt()
        #path.prepare_for_answer(step_for_prompt=pstep, step_sent_id=pstep.get_id())
        #rstep = path.get_step_for_reply()

        #assert path.step_for_prompt is None
        #assert path.step_for_reply.get_id() is out[mypath['casenum']].get_id()
        #assert rstep.get_id() == out[mypath['casenum']].get_id()


#class TestUser():
    #"""unit testing class for the paideia.User class"""

    #def test_user_get_id(self, myuser):
        #assert myuser.get_id() == 1

    #def test_user_is_stale(self, myuser):
        #assert 0

    #def test_user_get_categories(self, myuser):
        #assert 0

    #def test_user_get_old_categories(self, myuser):
        #assert 0

    #def test_user_get_new_badges(self, myuser):
        #assert 0

    #def test_user_complete_path(self, myuser):
        #assert 0

    #def test_user_get_path(self, myuser):
        #assert 0


class TestCategorizer():
    """Unit testing class for the paideia.Categorizer class"""

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
        assert  core == output

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

#class TestWalk():
    #"""
    #A unit testing class for the paideia.Walk class.
    #"""

    #def test_walk_get_user(self, mywalk, myrecords, mysession):
        #"""docstring for _get_user"""
        #localias = mywalk.localias
        #userdata = {'first_name': 'Joe', 'id': 1}
        #tag_records = myrecords['tag_records']
        #tag_progress = myrecords['tag_progress']
        #assert mywalk._get_user(userdata=userdata, localias=localias,
                        #tag_records=tag_records, tag_progress=tag_progress)

    #def test_walk_map(self, mywalk):
        #mapdata = {'map_image': '/paideia/static/images/town_map.svg',
                    #'locations': [
                        #{'alias': 'None',
                        #'bg_image': 8,
                        #'id': 3},
                       #{'alias': 'domus_A',
                        #'bg_image': 8,
                        #'id': 1},
                       #{'alias': '',
                        #'bg_image': 8,
                        #'id': 2},
                       #{'alias': None,
                        #'bg_image': None,
                        #'id': 4},
                       #{'alias': None,
                        #'bg_image': None,
                        #'id': 12},
                       #{'alias': 'bath',
                        #'bg_image': 17,
                        #'id': 13},
                       #{'alias': 'gymnasion',
                        #'bg_image': 15,
                        #'id': 14},
                       #{'alias': 'shop_of_alexander',
                        #'bg_image': 16,
                        #'id': 6},
                       #{'alias': 'ne_stoa',
                        #'bg_image': 18,
                        #'id': 7},
                       #{'alias': 'agora',
                        #'bg_image': 16,
                        #'id': 8},
                       #{'alias': 'synagogue',
                        #'bg_image': 15,
                        #'id': 11},
                       #{'alias': None,
                        #'bg_image': None,
                        #'id': 5},
                       #{'alias': None,
                        #'bg_image': None,
                        #'id': 9},
                       #{'alias': None,
                        #'bg_image': None,
                        #'id': 10}
                       #]}
        #map = mywalk.map()
        #pprint(map)
        #for m in mapdata['locations']:
            #i = mapdata['locations'].index(m)
            #assert map['locations'][i]['alias'] == m['alias']
            #assert map['locations'][i]['bg_image'] == m['bg_image']
            #assert map['locations'][i]['id'] == m['id']
        #assert map['map_image'] == mapdata['map_image']

    #def test_walk_ask(self, mywalk):
        #prompt = 'How would you write the English word "head" using'\
                #' Greek letters?'
        #instructions = None
        #image = '/paideia/static/images/images.image.bb48641f0122d2b6.696d616765732e696d6167652e383136303330663934646664646561312e34343732363137373639366536373230333432653733373636372e737667.svg'
        #responder = '<form action="" autocomplete="off" enctype="multipart/form-data" method="post"><table><tr id="no_table_response__row"><td class="w2p_fl"><label for="no_table_response" id="no_table_response__label">Response: </label></td><td class="w2p_fw"><input class="string" id="no_table_response" name="response" type="text" value="" /></td><td class="w2p_fc"></td></tr><tr id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw"><input type="submit" value="Submit" /></td><td class="w2p_fc"></td></tr></table></form>'
        #ask = mywalk.ask()
        #assert ask['prompt']['prompt'] == prompt
        #assert ask['prompt']['instructions'] == instructions
        #assert ask['prompt']['npc_image'] == image
        #assert ask['responder'].xml() == responder

    #def test_walk_reply(self, mywalk):
        #response_string = ''
        #reply = ''
        #bug_reporter = ''
        ## TODO: put in safety in case of empty form
        #returning = mywalk.reply(response_string)
        #out_reply = returning['reply']
        #out_bug_reporter = returning['bug_reporter']

        #assert out_reply == reply
        #assert out_bug_reporter == bug_reporter

    #def test_walk_record_cats(self, mywalk):
        #"""
        #Unit tests for Walk._record_cats()
        #"""
        #tag_progress = {'tag': 61,
                        #'latest_new': 2,
                        #'cat1': [1, 2, 3],
                        #'cat2': [4],
                        #'cat3': [5, 6],
                        #'cat4': [7],
                        #'rev1': [1, 2, 3],
                        #'rev2': [4],
                        #'rev3': [5, 6],
                        #'rev4': [7],
                        #'secondary_right': []}

        #categories =   {'cat1': [1, 2, 3],
                        #'cat2': [4],
                        #'cat3': [5, 6],
                        #'cat4': [7],
                        #'rev1': [1, 2, 3],
                        #'rev2': [4],
                        #'rev3': [5, 6],
                        #'rev4': [7]}
        #new_tags = [1, 2, 3]
        #promoted = {'cat1': [1, 2, 3],
                    #'cat2': [4],
                    #'cat3': [5, 6],
                    #'cat4': [7],
                    #'rev1': [1, 2, 3],
                    #'rev2': [4],
                    #'rev3': [5, 6],
                    #'rev4': [7]}
        #demoted = {'rev1': [1, 2, 3],
                    #'rev2': [4],
                    #'rev3': [5, 6],
                    #'rev4': [7]}
        #assert 0

    #def test_walk_record_step(self, mywalk):
        #id = mywalk._get_user().get_id()
        #loglength = len(db(db.attempt_log.name == id).select())
        #tag_records = ''

        #rec = mywalk._record_step(tag_records, categories, new_tags)
        #assert len(db(db.attempt_log.name == id).select()) == loglenth + 1
        #assert 0

    #def test_walk_store_user(self, mywalk):
        #"""Unit test for Walk._store_user"""
        #session = current.session
        #assert mywalk._store_user() == True
        #assert isinstance(session.user, User)
        #assert session.user.get_id() == 1
        #assert 0

#class TestPathChooser():

    #def test_pathchooser_choose(self, mypathchooser):
        #newpath = mypathchooser['pathchooser'].choose()
        #assert newpath[0].id in [r for c in mypathchooser['paths'].values() for r in c if len(c) > 0]
        #assert newpath[2] in range(1,5)

    #def test_pathchooser_order_cats(self, mypathchooser):
        #pc = mypathchooser['pathchooser']._order_cats()
        #ind = pc.index(1)
        #if len(pc) >= (ind + 2):
            #assert pc[ind + 1] == 2
        #if len(pc) >= (ind + 3):
            #assert pc[ind + 2] == 3
        #if len(pc) >= (ind + 4):
            #assert pc[ind + 3] == 4
        #if ind != 0:
            #assert pc[ind - 1] == 4
        #assert len(pc) == 4
        #assert pc[0] in [1,2,3,4]
        #assert pc[1] in [1,2,3,4]
        #assert pc[2] in [1,2,3,4]
        #assert pc[3] in [1,2,3,4]

    #def test_pathchooser_paths_by_category(self, mypathchooser):
        #cpaths, category = mypathchooser['pathchooser']._paths_by_category('1')
        #allpaths = mypathchooser['paths']
        #pathids = allpaths['cat{}'.format(category)]
        #expected = db(db.paths).select()
        #expected = expected.find(lambda row: row.id in pathids)
        #assert len(cpaths) == len(expected)
        #for row in cpaths:
            #assert row.id in [r.id for r in expected]

    #def test_pathchooser_choose_from_cat(self, mypathchooser):
        #allpaths = mypathchooser['paths']
        #pathids = allpaths['cat{}'.format(1)]
        #expected = db(db.paths).select()
        #expected = expected.find(lambda row: row.id in pathids)
        #print expected

        #newpath = mypathchooser['pathchooser']._choose_from_cat(expected, 1)
        #assert newpath[0].id in mypathchooser['paths']['cat1']
        #assert newpath[1] in [l for l in db.steps(newpath[0].steps[0]).locations]
        #assert newpath[2] == 1
