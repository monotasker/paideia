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
from paideia import Block, BugReporter
from gluon import current, IMG

import datetime
from pprint import pprint
import re
from random import randint
from copy import copy


# ===================================================================
# Switches governing which tests to run
# ===================================================================
global_runall = False
global_run_TestNpc = False
global_run_TestLocation = False
global_run_TestStep = False
global_run_TestStepEvaluator = False
global_run_TestMultipleEvaluator = False
global_run_TestPath = False
global_run_TestUser = False
global_run_TestCategorizer = False
global_run_TestWalk = False
global_run_TestPathChooser = 1

# ===================================================================
# Test Fixtures
# ===================================================================


def dt(string):
    """Return datetime object parsed from the string argument supplied"""
    format = "%Y-%m-%d"
    return datetime.datetime.strptime(string, format)


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


def mystep(stepid, mysteps):
    """
    A pytest fixture providing a paideia.Step object for testing.
    """
    try:
        stepdata = mysteps[stepid]
    except KeyError:
        stepdata = None  # FIXME: some test steps not in stepdata dict
    step = StepFactory().get_instance(stepid)
    return step, stepdata


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


@pytest.fixture
def myStepEvaluator(mysteps):
    """
    A pytest fixture providing a paideia.StepEvaluator object for testing.
    """
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

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('stepid', [1])
    def test_step_get_id(self, stepid, mysteps):
        """Test for method Step.get_id """
        step, expected = mystep(stepid, mysteps)
        assert step.get_id() == expected['id']
        assert isinstance(step, expected['step_type']) is True

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize("stepid", [1, 2])
    def test_step_get_tags(self, stepid, mysteps):
        """Test for method Step.get_tags """
        step, expected = mystep(stepid, mysteps)
        actual = step.get_tags()
        assert actual == {'primary': expected['tags'],
                          'secondary': expected['tags_secondary']}

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('caseid,stepid', [
        #('case1', 1),
        #('case2', 2),
        #('case2', 19),  # will redirect (currently no case works for step 19)
        #('case1', 30),  # redirect step
        #('case1', 101),
        #('case2', 125),  # FIXME: no slide decks being found here
        #('case2', 126),  # promoted, no new tags (for new badges)
        #('case3', 126),  # promoted, no new tags (for new badges)
        #('case2', 127),  # new tags and promoted (for view slides)
    ])
    def test_step_get_prompt(self, caseid, stepid, db, mysteps,
                             user_login, npc_data, bg_imgs):
        """Test for method Step.get_prompt"""
        case = mycases(caseid, user_login, db)
        step, expected = mystep(stepid, mysteps)
        locnpcs = [int(n) for n in case['npcs_here']
                   if n in expected['npc_list']]
        if locnpcs:
            npc = Npc(locnpcs[0], db)
            actual = step.get_prompt(case['loc'], npc, case['name'],
                                     case['next_loc'],
                                     case['new_badges'],
                                     case['promoted'])
            print 'actual -------'
            try:
                print actual['prompt'].xml()
            except Exception:
                print(actual['prompt'])
            print 'expected -------'
            print expected['final_prompt']

            assert (actual['prompt'] == expected['final_prompt']) or \
                   (actual['prompt'].xml() == expected['final_prompt']) or \
                   (actual['prompt'].xml() == expected['final_prompt'][case['casenum']])
            assert actual['instructions'] == expected['instructions']
            if expected['slidedecks']:
                for k, v in actual['slidedecks'].iteritems():
                    assert v == expected['slidedecks'][k]
            if expected['widget_image']:
                assert actual['widget_image']['title'] == expected['widget_image']['title']
                assert actual['widget_image']['file'] == expected['widget_image']['file']
                assert actual['widget_image']['description'] == expected['widget_image']['description']
            assert actual['bg_image'] == bg_imgs[case['loc'].get_id()]
            assert actual['npc_image'].attributes['_src'] == npc_data[npc.get_id()]['image']
        else:
            assert step.get_prompt(case['loc'], npc, case['name'],
                                   None, None, None) == expected['redirect']

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

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('stepid', [1, 2, 19])
    def test_stepevaluator_get_eval(self, stepid, mysteps, myStepEvaluator):
        """Unit tests for StepEvaluator.get_eval() method."""
        step, expected = mystep(stepid, mysteps)
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


@pytest.mark.skipif('global_runall is False and global_run_TestMultipleEvaluator '
                    'is False', reason='Global skip settings')
class TestMultipleEvaluator():
    """
    Unit testing class for paideia.MultipleEvaluator class.
    """

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('stepid', [101])
    def test_multipleevaluator_get_eval(self, stepid, mysteps, myMultipleEvaluator):
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
        expected = [mystep(sid, mysteps)[0] for sid in steps]
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
                                     localias, mysteps, db):
        """
        Unit test for method paideia.Path.get_step_for_reply.
        """
        path, pathsteps = mypath(pathid, db)
        step, expected = mystep(stepid, mysteps)
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

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('casenum', ['case1'])
    def test_user_get_id(self, casenum, user_login, db):
        """
        Unit test for User.get_id() method.
        """
        case = mycases(casenum, user_login, db)
        tag_progress = case['tag_progress']
        tag_records = case['tag_records']
        actualuser = myuser(tag_progress, tag_records, user_login, db)

        actualid = actualuser.get_id()
        expected = db((db.auth_user.first_name == 'Homer') &
                      (db.auth_user.last_name == 'Simpson')).select()
        assert len(expected) == 1
        assert actualid == expected.first().id

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('condition,casenum,viewedslides,reportedbadges',
                             [('redirect', 'case1', 0, 0),
                              ('view_slides', 'case1', 0, 0),
                              ('view_slides', 'case1', 1, 0),
                              ('new_tags', 'case1', 0, 0),
                              ('new_tags', 'case1', 0, 1),
                              ('promoted', 'case1', 0, 0),
                              ('promoted', 'case1', 0, 1),
                              ('quota_reached', 'case1', 0, 0)])
    def test_user_set_block(self, condition, casenum, viewedslides,
                            reportedbadges, user_login, db):
        """
        Unit test for User.set_block() method.
        """
        case = mycases(casenum, user_login, db)
        user = myuser(case['tag_progress'], case['tag_records'],
                             user_login, db)
        user.viewed_slides = viewedslides
        user.reported_badges = reportedbadges
        user.quota_reached = 0
        startlen = len(user.blocks)
        startconditions = [u.get_condition() for u in user.blocks]
        assert user.set_block(condition)
        newlen = len(user.blocks)
        if (viewedslides and condition == 'view_slides') or \
           (reportedbadges and condition == 'new_tags') or \
           (reportedbadges and condition == 'promoted'):
            print 'blocks are', user.blocks
            assert startlen == newlen
            assert [u.get_condition() for u in user.blocks] == startconditions
        else:
            print 'blocks are', user.blocks
            assert all([isinstance(b, Block) for b in user.blocks])
            assert startlen == newlen - 1
            assert user.blocks[-1].get_condition() == condition

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('casenum,theblocks',
                             [('case3', ['new_tags']),
                              ('case3', []),
                              ('case3', ['new_tags', 'redirect']),
                              ])
    def test_user_check_for_blocks(self, casenum, theblocks, user_login, db):
        """
        unit test for Path._check_for_blocks()

        Since this method only checks for the presence of blocks on the current
        path, it will return a blocking step for each test case (even if that
        case would not normally have a block set.)
        """
        # TODO: there's now some block-checking logic in the method. Ideally
        # that should be isolated in its own method.
        case = mycases(casenum, user_login, db)
        user = myuser(case['tag_progress'], case['tag_records'],
                             user_login, db)
        user.blocks = [Block(c) for c in theblocks]
        startlen = len(theblocks)

        actual_return = user.check_for_blocks()
        actual_property = user.blocks
        if theblocks:
            assert len(actual_property) == startlen - 1
            assert all(isinstance(b, Block) for b in actual_property)
            assert isinstance(actual_return, Block)
        else:
            assert len(actual_property) == 0
            assert actual_property == []
            assert actual_return is None

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('start,expected',
                             [(datetime.datetime(2013, 01, 02, 9, 0, 0), False),
                              (datetime.datetime(2013, 01, 02, 9, 0, 0), False),
                              (datetime.datetime(2013, 01, 02, 3, 0, 0), True),
                              (datetime.datetime(2012, 12, 29, 14, 0, 0), True)
                              ])
    def test_user_is_stale(self, start, expected, user_login, db):
        """
        Unit test for User.is_stale() method.
        """
        now = datetime.datetime(2013, 01, 02, 14, 0, 0)
        tzn = 'America/Toronto'
        case = mycases('case1', user_login, db)
        user = myuser(case['tag_progress'], case['tag_records'], user_login, db)
        actual = user.is_stale(now=now, start=start, time_zone=tzn, db=db)
        assert actual == expected

    @pytest.mark.skipif(True, reason='just because')
    def test_user_get_path(self, myuser, db):
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

    @pytest.mark.skipif(True, reason='just because')
    def test_user_get_categories(self, myuser):
        """
        Unit test for User._get_categories() method.
        """
        user = myuser['user']
        case = myuser['casedata']
        if user.cats_counter < 5:
            expected = case['categories_start']
        elif user.cats_counter >= 5:
            expected = case['categories_out']
        actual = user._get_categories()
        # this avoids problem of lists being in different orders
        for c, l in expected.iteritems():
            assert len(actual['categories'][c]) == len([t for t in l])

    @pytest.mark.skipif(True, reason='just because')
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

    @pytest.mark.skipif(True, reason='just because')
    def test_user_complete_path(self, myuser):
        user = myuser['user']
        case = myuser['casedata']
        pathid = case['paths']['cat1'][0]
        path = Path(path_id=pathid, loc=case['loc'])
        path.completed_steps.append(path.steps.pop(0))

        user.path = copy(path)
        assert user._complete_path() is True
        assert user.path is None
        if case['casenum'] == 3:
            print user.last_npc
            assert not user.last_npc
        else:
            assert user.last_npc.get_id() in case['npcs_here']
        assert user.last_loc.get_id() == case['loc'].get_id()
        assert user.completed_paths[-1].get_id() == path.get_id()
        assert isinstance(user.completed_paths[-1], Path)


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
                               )
                              ])
    def test_categorizer_add_secondary_right(self, casename, rank, catsin,
                                             tagrecsin, tagrecsout):
        """Unit test for the paideia.Categorizer._add_secondary_right method."""
        now = dt('2013-01-29')
        # 150 is random user id
        catzr = Categorizer(rank, catsin, tagrecsin, 150, utcnow=now)

        actual = catzr._add_secondary_right(tagrecsin)
        expected = tagrecsout

        for idx, a in enumerate(actual):
            assert a['tag'] == expected[idx]['tag']
            assert a['tlast_right'] == expected[idx]['tlast_right']
            assert a['tlast_wrong'] == expected[idx]['tlast_wrong']
            assert a['times_right'] == expected[idx]['times_right']
            assert a['tlast_wrong'] == expected[idx]['tlast_wrong']
            assert a['secondary_right'] == expected[idx]['secondary_right']

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
                               1, {'cat1': [1], 'cat2': [],
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
                    'and not global_run_TestWalk')
class TestWalk():
    """
    A unit testing class for the paideia.Walk class.
    """

    def test_walk_get_user(self, mywalk):
        """Unit test for paideia.Walk._get_user()"""
        thiswalk = mywalk['walk']
        case = mywalk['casedata']
        if case['casenum'] == 1:
            localias = case['localias']
            userdata = {'first_name': 'Homer',
                        'last_name': 'Simpson',
                        'id': current.auth.user.id}
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
                                    'bg_image': 15,
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
            actual = thiswalk.map()
            for m in expected['locations']:
                i = expected['locations'].index(m)
                assert actual['locations'][i]['loc_alias'] == m['loc_alias']
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

        combinations = {1: [1, 2, 101],  # paths 2, 3, 89 (multi, redir(step 30))
                        2: [101, 19],  # paths 89 (multiple), 19
                        3: [19]}  # path 19
        if c in combinations.keys() and s in combinations[c]:
            redirects = {1: [101],
                         2: [101]}  # TODO: why does case 2 redirect step 101?
            if c in redirects and s in redirects[c]:
                print 'redirecting'
                expected = {'prompt': step['redirect_prompt'],
                            'instructions': None,
                            'responder': step['redirect_responder'],
                            'reply_step': False}
            else:
                expected = {'prompt': step['final_prompt'],
                            'instructions': step['instructions'],
                            'responder': step['responder'],
                            'reply_step': False}
                if step['step_type'] in (StepText, StepMultiple):
                    # expect a reply step prepared for these step types
                    expected['reply_step'] = True

            path = step['paths'][0]
            print 'in test_walk_ask———————————————————————————–'
            print 'asking path', path
            actual = thiswalk.ask(path)
            # TODO: add the following new assertions to test for
            # path.get_step_for_prompt
            # check that right number of steps left in path.steps
            # TODO: parameterize this when we add multi-step path tests
            assert thiswalk.user.path.steps == []
            # check that a step is prepared for reply when necessary
            if expected['reply_step'] is True:
                assert thiswalk.user.path.step_for_reply
                print 'step_for_reply is', thiswalk.user.path.step_for_reply.get_id()
            else:
                assert not thiswalk.user.path.step_for_reply
                print 'no step prepared for reply'
            # check that correct path is active on user
            assert path == thiswalk.user.path.get_id()
            assert actual['prompt']['prompt'] == expected['prompt']
            assert actual['prompt']['instructions'] == expected['instructions']
            # TODO: check for image -- just hard to predict
            #assert actual['prompt']['npc_image'] == expected['image']
            assert actual['responder'].xml() == expected['responder']
        else:
            print 'skipping combination'
            pass

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
    @pytest.mark.parametrize('locid,completed,tpout,redirect',
                             [(6,  # shop_of_alexander
                               [2, 3, 5, 8, 63, 95, 96, 97, 99, 102, 256, 40,
                                9, 410, 411, 412, 413, 414, 415, 416, 417, 418,
                                419, 420, 421, 422, 423, 444, 445],
                               #[1],
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                                False
                               ),
                              (11,  # synagogue
                               [2, 3, 99],  # forcing redirect, these are in loc 11
                               {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [61], 'rev2': [],
                                'rev3': [], 'rev4': []},
                                True
                               ),
                              (8,  # agora
                               [],
                               {'latest_new': 2,
                                'cat1': [6, 29, 62, 82, 83], 'cat2': [61],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [61],
                                'rev3': [], 'rev4': []},
                                False
                               ),
                              ])
    def test_pathchooser_choose(self, locid, completed, tpout, redirect, db):
        """
        Unit test for the paideia.Pathchooser.choose() method.
        """
        chooser = PathChooser(tpout, locid, completed)
        actual, newloc, catnum = chooser.choose()

        mycat = 'cat{}'.format(catnum)
        allpaths = db(db.paths.id > 0).select()
        tagids = tpout[mycat]
        expected = [p.id for p in allpaths
                    if any([t for t in tagids if t in p.tags])]
        #{'cat1': [1, 2, 3, 5, 8, 63, 95, 96, 99, 102, 256],  # removed 64, 70, 97, 104, 277

        print 'CHOSEN PATH', actual
        print 'EXPECTED PATHS', expected

        assert catnum in range(1, 5)
        assert actual['id'] in expected
        firststep = actual['steps'][0]
        if redirect:
            assert newloc
            steplocs = db.steps(firststep).locations
            assert newloc in steplocs
            assert locid not in steplocs
        else:
            assert newloc is None

    def test_pathchooser_order_cats(self, mypathchooser):
        """
        Unit test for the paideia.Pathchooser._order_cats() method.
        """
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

    def test_pathchooser_paths_by_category(self, mypathchooser, db):
        """
        Unit test for the paideia.Pathchooser._paths_by_category() method.
        """
        tp = mypathchooser['casedata']['tag_progress_out']
        rank = tp['latest_new']
        cpaths, category = mypathchooser['pathchooser']._paths_by_category(1, rank)
        tagids = tp['cat{}'.format(category)]
        x = db(db.paths).select()
        x = x.find(lambda row: [t for t in tagids
                                if t in db.paths[row.id].tags])
        x = x.find(lambda row: [s for s in row.steps if db.steps(s).status != 2])
        x.exclude(lambda row: [s for s in row.steps
                               if db.steps(s).locations is None])
        x.exclude(lambda row: [t for t in row.tags
                               if db.tags[t].tag_position > rank])
        assert len(cpaths) == len(x)
        for row in cpaths:
            assert row.id in [r.id for r in x]

    def test_pathchooser_choose_from_cat(self, mypathchooser, db):
        """
        Unit test for the paideia.Pathchooser._choose_from_cats() method.
        """
        catnum = 1
        paths = mypathchooser['casedata']['paths']
        pathids = paths['cat{}'.format(catnum)]
        expected = db(db.paths).select()
        expected = expected.find(lambda row: row.id in pathids)

        newpath = mypathchooser['pathchooser']._choose_from_cat(expected, catnum)
        assert newpath[0]['id'] in paths['cat{}'.format(catnum)]
        assert newpath[1] in [l for l in db.steps(newpath[0]['steps'][0]).locations]
        assert newpath[2] == 1


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
