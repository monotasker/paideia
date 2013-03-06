# -*- coding: utf-8 -*-
# Unit tests for the paideia module

import pytest
from paideia import Npc, Location, User, PathChooser, Path, Categorizer, Walk
from paideia import StepFactory, Step, StepText, StepMultiple
from paideia import StepRedirect, StepViewSlides, StepAwardBadges, StepQuotaReached
from paideia import StepEvaluator, MultipleEvaluator
from paideia import Block, BlockRedirect, BlockAwardBadges, BlockViewSlides
from gluon import *
import datetime
from pprint import pprint
import re

# ===================================================================
# Test Fixtures
# ===================================================================

def dt(string):
    """Return datetime object parsed from the string argument supplied"""
    format = "%Y-%m-%d"
    return datetime.datetime.strptime(string, format)

# Constant values from db
db = current.db
npc1_img = '/paideia/static/images/images.image.bb48641f0122d2b6.696d616765732e696d6167652e383136303330663934646664646561312e34343732363137373639366536373230333432653733373636372e737667.svg'
npc2_img = '/paideia/static/images/images.image.81e2d69e1aea4d99.44726177696e672031372e737667.svg'
npc3_img = '/paideia/static/images/images.image.81e2d69e1aea4d99.44726177696e672031372e737667.svg'
npc4_img = '/paideia/static/images/images.image.85a960241dc29f1b.776f6d616e312e706e67.png'
npc5_img = '/paideia/static/images/images.image.a4d5140b25f87749.44726177696e672031392e737667.svg'
npc6_img = '/paideia/static/images/images.image.a28124edf3480d82.696d616765732e696d6167652e383135323664663563326663623438302e343437323631373736393665363732303332333232653733373636372e737667.svg'
npc7_img = '/paideia/static/images/images.image.993274ee0076fd2f.696d616765732e696d6167652e393636636434346165663238613839652e343437323631373736393665363732303332333732653733373636372e737667.svg'
npc8_img = '/paideia/static/images/images.image.938be4c25c678bb5.323031322d30362d30352030335f35325f31312e706e67.png'
npc9_img = ''
npc10_img = '/paideia/static/images/images.image.961b44d8d322659c.323031322d30362d30372031345f34345f34302e706e67.png'
npc11_img = '/paideia/static/images/images.image.ac58c3e138964719.70686f6562652e706e67.png'
npc14_img = '/paideia/static/images/images.image.b5592e80d5fe4bb3.73796e61676f6775652e6a7067.jpg'
npc15_img = '/paideia/static/images/images.image.9a515ff664f03aa3.323031322d30372d32312032335f35315f31322e706e67.png'
npc16_img = '/paideia/static/images/images.image.8bb7c079634cf35a.44726177696e672033332e706e67.png'
npc17_img = '/paideia/static/images/images.image.95fcf253d4dd7abd.44726177696e6720352e706e67.png'

npc_data = {1: {'image': npc1_img,
                'name': 'Ἀλεξανδρος',
                'location': [6, 8],
                },
            2: {'image': npc4_img,
                'name': 'Μαρια',
                'location': [3, 1, 2, 4],
                },
            8: {'image': npc5_img,
                'name': 'Διοδωρος',
                'location': [1],
                },
            14: {'image': npc2_img,
                'name': 'Γεωργιος',
                'location': [3, 1, 2, 4, 7, 8, 9, 10],
                },
            17: {'image': npc7_img,
                'name': 'Ἰασων',
                'location': [3, 1, 2, 4, 7, 8],
                },
            21: {'image': npc7_img,
                'name': 'Νηρευς',
                'location': [7, 8],
                },
            31: {'image': npc3_img,
                'name': 'Σοφια',
                'location': [3, 1, 2, 4, 11],
                },
            32: {'image': npc10_img,
                'name': 'Στεφανος',
                'location': [11],
                },
            40: {'image': npc6_img,
                'name': 'Σιμων',
                'location': [3, 1, 2, 4, 7, 8],
                },
            41: {'image': npc11_img,
                'name': 'Φοιβη',
                'location': [3, 1, 4, 8],
                },
            42: {'image': npc9_img,
                'name': 'Ὑπατια',
                'location': [3, 1, 2, 4, 12, 8],
                }}

step_data_store = {
        # stepText
        1: {'case1':  # same npc and location as previous step
               {'loc': Location(8, db),
                'prev_loc': Location(8, db),
                'prev_npc_id': 1,
                'user': 'Ian',
                'new_badges': [],
                'npc_list': [],
                'instructions': None},
            'case2': {}
            },
        # stepText
        2: {'case1':  # same npc and location as previous step
                {'loc': Location(1, db),
                'prev_loc': Location(1, db),
                'prev_npc_id': 2}
            },
        # stepRedirect
        30: {'case1':
                {'user': 'Ian',
                'loc': Location(11, db), # synagogue
                'prev_loc': Location(11, db),
                'prev_npc_id': 31, # stephanos
                'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                'instructions': None},
            'case2': {}
            },
        # stepMultiple
        101: {'case1':  # same npc and location as previous step
                {'loc': Location(8, db),
                'prev_loc': Location(8, db),
                'prev_npc_id': 1,},
            'case2':
                {'loc': Location(8, db),
                'prev_loc': Location(7, db),
                'prev_npc_id': 1,
                }
            },
        # stepQuotaReached
        125: {'case1':  # same npc and location as previous step
                {'username': 'Ian',
                'loc': Location(8, db),
                'prev_loc': Location(8, db),
                'prev_npc_id': 1,
                'loc': Location(8, db),
                'prev_loc': Location(8, db),
                'prev_npc_id': 1,
                'raw_prompt': 'Well done, [[user]]. You\'ve finished enough '\
                        'paths for today. But if you would like to keep '\
                        'going, you\'re welcome to continue.',
                'final_prompt': 'Well done, Ian. You\'ve finished enough '\
                        'paths for today. But if you would like to keep '\
                        'going, you\'re welcome to continue.'
                }
            },
        # stepAwardBadges
        126: {'case1':  # new badges, no promoted
                {'username': 'Ian',
                'raw_prompt': 'Congratulations, [[user]]![[new_badge_list]]'\
                        '[[promoted_list]]You can click on your name above to '\
                        'see details of your progress so far.',
                'final_prompt': 'Congratulations, Ian! You\'ve earned a new '\
                        'badge! '\
                        '<ul class="new_badge_list">'\
                        '<li>'\
                        '<span class="badge_name">spaced out</span> '\
                        'for using spatial adverbs to talk about the '\
                        'location of events, people, places, or things'\
                        '</li>'\
                        '<li>'\
                        '<span class="badge_name">nominative 1</span> for '\
                        'the use of singular, first-declension nouns in the '\
                        'nominative case'\
                        '</li>'\
                        '</ul>'\
                        'You can click on your name above to '\
                        'see details of your progress so far.',
                'instructions': None,
                'loc': Location(12, db),
                'prev_loc': Location(12, db),
                'prev_npc_id': 2,
                'new_badges': [5, 6],
                'promoted': [],
                'widget_type': 8,
                'tags': [81],
                'tags_secondary': [],
                'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10]}
            },
            # TODO: write another case to test with promotions present
            #promoted_list = 'You\'ve reached a new level in these badges:'\
                        #'<ul class="promoted_list">'\
                        #'<li>'\
                        #'</li>'\
                        #'</ul>'
        # stepViewSlides
        127: {'case1':
                {'username': 'Ian',
                'loc': Location(3, db),
                'prev_loc': Location(3, db),
                'prev_npc_id': 1,
                'new_badges': [5,6],
                'raw_prompt': 'Congratulations, [[user]]! You\'re ready to start '\
                    'working on some new badges. Before you '\
                    'continue, take some time to view these slide sets:'\
                    '[[slides]]You\'ll find the slides by clicking on the '\
                    '"slides" menu item at top.',
                'final_prompt': 'Congratulations, Ian! You\'re ready to '\
                    'start working '\
                    'on some new badges. Before you continue, take some time '\
                    'to view these slide sets:'\
                        '<ul class="slide_list">'\
                        '<li>The Alphabet III</li>'\
                        '<li>Case Basics</li>'\
                        '</ul>'
                    'You\'ll find the slides by clicking on the "slides" menu '\
                    'item at top.',
                'instructions': None,
                'widget_type': 6,
                'tags': [80],
                'npc_list': [14, 8, 2, 40, 31, 32, 41, 1, 17, 42],
                'locations': [3, 1, 2, 4, 12, 13, 6, 7, 8, 11, 5, 9, 10]},
            'case2': {}
            }
        }

@pytest.fixture(params=['case{}'.format(n) for n in range(1,2)])
def myrecords(request):
    """pytest fixture for providing user records."""
    case = request.param
    case1 = {'casenum': 1, 'mynow': dt('2013-01-29'),
            'localias': 'shop_of_alexander',
            'attempt_log': [{'step': None, 'path': None, 'score': None,
                            'dt_attempted': None} ],
            'tag_records': [{'tag_id': 1,
                             'last_right': dt('2013-01-29'),
                             'last_wrong': dt('2013-01-29'),
                             'times_right': 1,
                             'times_wrong': 1,
                             'secondary_right': []}],
            'tag_progress': {'latest_new': 1,
                            'cat1': [], 'cat2': [], 'cat3': [], 'cat4': [],
                            'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}}

    case2 = {'casenum': 2, 'mynow': dt('2013-01-29'),
            'localias': 'domus_A',
            'attempt_log': [{'step': None, 'path': None, 'score': None,
                            'dt_attempted': None}],
            'tag_records': [{'tag_id': 1,
                             'last_right': dt('2013-01-29'),
                             'last_wrong': dt('2013-01-28'),
                             'times_right': 10,
                             'times_wrong': 2,
                             'secondary_right': []}],
            'tag_progress': {'latest_new': 1,
                            'cat1': [1], 'cat2': [], 'cat3': [], 'cat4': [],
                            'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}}
    return locals()[case]

@pytest.fixture(params=['case{}'.format(n) for n in range(1,2)])
def mysession(request):
    """pytest fixture for providing a mock session object."""
    case = request.param
    # no user in session
    case1 = {}
    # user already in session
    case2 = {'user': myuser}

    return locals()[case]

@pytest.fixture
def mywalk(myrecords):
    """pytest fixture providing a paideia.Walk object for testing"""
    userdata = {'first_name': 'Joe', 'id': 1}
    tag_progress = myrecords['tag_progress']
    tag_records = myrecords['tag_records']
    localias = myrecords['localias']
    return Walk(localias, userdata=userdata,
            tag_records=tag_records, tag_progress=tag_progress, db=db)

@pytest.fixture(params=['case{}'.format(n) for n in range(1,2)])
def mypathchooser(request, myloc):
    """pytest fixture providing a paideia.PathChooser object for testing"""
    case = request.param
    cases = {
    'case1':
        {'categories': {'cat1': [61], 'cat2': [], 'cat3': [], 'cat4': []},
        'loc': 'domus_A',
        'completed': [],
        'paths': [1, 2, 3, 5, 8, 63, 64, 70, 95, 96, 97, 99, 102, 104, 256, 277]},
    'case2':
        {'categories': {'cat1': [62], 'cat2': [61], 'cat3': [], 'cat4': []},
        'loc': 'domus_A',
        'completed': [],
        'paths': [4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22,
            23, 34, 35, 97, 98, 100, 101, 103, 257, 261, 277]},
    }
    c = cases[request.param]
    return {'pathchooser':
                PathChooser(c['categories'], c['loc'], c['completed'], db=db),
            'paths': c['paths']}

@pytest.fixture
def mycategorizer(myrecords):
    """A pytest fixture providing a paideia.Categorizer object for testing."""
    rank = myrecords['tag_progress']['latest_new']
    categories = myrecords['tag_progress']
    tag_records = myrecords['tag_records']
    return {'categorizer': Categorizer(rank, categories, tag_records),
            'casenum': myrecords['casenum']}

@pytest.fixture
def myuser(myrecords):
    """A pytest fixture providing a paideia.User object for testing."""
    userdata = db.auth_user(1).as_dict()
    tag_progress = myrecords['tag_progress']
    tag_records = myrecords['tag_records']
    localias = myrecords['localias']
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

@pytest.fixture(params=[p for p in range(1,2)])
def mypath(request):
    """
    A pytest fixture providing a paideia.Path object for testing.
    """
    # StepText loc and prev_npc both work, no blocks
    case = 'case{}'.format(request.param)
    case1args = {'path_id': 3, 'blocks': [], 'loc_id': 1,
            'prev_loc': Location(1, db), 'prev_npc_id': 2}
    case1 = Path(db=db, **case1args)
    # StepMultiple loc and prev_npc both work, no blocks
    case2args = {'path_id': 89, 'blocks': [], 'loc_id': 8,
            'prev_loc': Location(8, db), 'prev_npc_id': 1}
    case2 = Path(db=db, **case2args)
    return {'casenum': request.param,
            'path': locals()[case]}

@pytest.fixture(params=[s for s in range(1,3)])
def mystep(request):
    """
    A pytest fixture providing a paideia.Step object for testing.
    - same npc and location as previous step
    TODO: write another fixture for a new location and for a new npc
    """
    ind = request.param - 1
    cases = [(1, 'case1'),
            (2, 'case1'),
            (101, 'case2')]
    sid = cases[ind][0]
    case = cases[ind][1]
    sd = step_data_store[sid][case]
    out = {k:v for k, v in sd.iteritems()
                if k in ['loc', 'prev_loc', 'prev_npc_id']}
    return {'casenum': request.param,
            'step': StepFactory().get_instance(step_id=sid, db=db, **out)}

@pytest.fixture
def myStepRedirect():
    """
    A pytest fixture providing a paideia.StepRedirect object for testing.
    - same npc and location as previous step
    TODO: write another fixture for a new location and for a new npc
    """
    step_data = step_data_store[30]['case1']
    out = {'step_id': 30,
            'loc': step_data['loc'],
            'prev_loc': step_data['prev_loc'],
            'prev_npc_id': step_data['prev_npc_id']}
    return StepRedirect(db=db, **out)

@pytest.fixture
def myStepAwardBadges():
    """
    A pytest fixture providing a paideia.StepAwardBadges object for testing.
    """
    casenum = 1
    step_data = step_data_store[126]['case1']
    out = {'step_id': 126,
            'loc': step_data['loc'],
            'prev_loc': step_data['prev_loc'],
            'prev_npc_id': step_data['prev_npc_id']}
    return {'casenum': casenum, 'step': StepAwardBadges(db=db, **out)}

@pytest.fixture
def myStepViewSlides():
    """
    A pytest fixture providing a paideia.StepViewSlides object for testing.
    """
    step_data = step_data_store[127]['case1']
    out = {'step_id': 127,
            'loc': step_data['loc'],
            'prev_loc': step_data['prev_loc'],
            'prev_npc_id': step_data['prev_npc_id']}
    return StepViewSlides(db=db, **out)

@pytest.fixture
def myStepQuotaReached():
    """
    A pytest fixture providing a paideia.StepQuota object for testing.
    """
    step_data = step_data_store[125]['case1']
    out = {'step_id': 125,
            'loc': step_data['loc'],
            'prev_loc': step_data['prev_loc'],
            'prev_npc_id': step_data['prev_npc_id']}
    return  StepFactory().get_instance(**out)

@pytest.fixture(params=[s for s in range(1,2)])
def myStepText(request):
    """
    A pytest fixture providing a paideia.StepText object for testing.
    """
    ind = request.param - 1
    cases = [(1, 'case1'),
            (2, 'case1')]
    sid = cases[ind][0]
    case = cases[ind][1]
    sd = step_data_store[sid][case]
    out = {k:v for k, v in sd.iteritems() if k in ['loc', 'prev_loc', 'prev_npc_id']}
    return {'casenum': request.param,
            'step': StepFactory().get_instance(step_id=sid, db=db, **out)}

@pytest.fixture(params=[s for s in range(1,2)])
def myStepMultiple(request):
    """ """
    ind = request.param - 1
    cases = [(101, 'case1'),
            (101, 'case2')]
    sid = cases[ind][0]
    case = cases[ind][1]
    sd = step_data_store[sid][case]
    out = {k:v for k, v in sd.iteritems()
                if k in ['loc', 'prev_loc', 'prev_npc_id']}
    return {'casenum': request.param,
            'step': StepFactory().get_instance(step_id=sid, db=db, **out)}

@pytest.fixture(params=[s for s in range(1,2)])
def myStepEvaluator(request):
    """
    A pytest fixture providing a paideia.StepEvaluator object for testing.
    """
    case = 'case{}'.format(request.param)
    case1 = {'casenum': 1,
            'vals': {'step_id': 1,
                    'responses': {'response1': '^μιτ$'},
                    'tips': None}}
    case2 = {'casenum': 2,
            'vals': {'step_id': 2,
                    'responses': {'response1': '^β(α|ο)τ$'},
                    'tips': None}}
    out = locals()[case]
    return {'casenum': out['casenum'],
            'eval': StepEvaluator(responses=out['vals']['responses'],
                                    tips=out['vals']['tips'])}

@pytest.fixture(params=[s for s in range(1,2)])
def myMultipleEvaluator(request):
    """
    A pytest fixture providing a paideia.MultipleEvaluator object for testing.
    """
    case = 'case{}'.format(request.param)
    case1 = {'casenum': 1,
            'vals': {'step_id': 101,
                    'answers': ['ναι'],
                    'tips': None}}
    case2 = {'casenum': 2,
            'vals': {'step_id': 101,
                    'answers': ['ναι'],
                    'tips': None}}
    out = locals()[case]
    return {'casenum': out['casenum'],
            'eval': MultipleEvaluator(responses=out['vals']['answers'],
                                        tips=out['vals']['tips'])}

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

    def test_npc_choose(self, mynpc):
        """Test for method Npc.choose()"""
        pass # TODO: write this test

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

class TestStep():
    """
    Unit tests covering the Step class of the paideia module.
    """
    # TODO: parameterize to cover more locations

    def test_step_get_id(self, mystep):
        """Test for method Step.get_id"""
        casenum = mystep['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'id':1, 'type': StepText}
        case2 = {'id':2, 'type': StepText}
        case3 = {'id':101, 'type': StepMultiple}
        output = locals()[case]
        assert mystep['step'].get_id() == output['id']
        assert isinstance(mystep['step'], output['type']) == True

    def test_step_get_tags(self, mystep):
        """Test for method Step.get_tags"""
        casenum = mystep['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'primary': [61], 'secondary': []}
        case2 = {'primary': [61], 'secondary': []}
        case3 = {'primary': [36], 'secondary': []}
        output = locals()[case]
        assert mystep['step'].get_tags() == output

    def test_step_get_prompt(self, mystep):
        """Test for method Step.get_prompt"""
        username = 'Ian'
        casenum = mystep['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'prompt': 'How could you write the word "meet" using Greek letters?',
                'instructions': ['Focus on finding Greek letters that make the *sounds* of the English word. Don\'t look for Greek "equivalents" for each English letter.'],
                'npc_image': npc1_img}
        case2 = {'prompt': 'How could you write the word "bought" using Greek letters?',
                'instructions': None,
                'npc_image': npc4_img}
        case3 = {'prompt': 'Is this an English clause?\n\n"The cat sat."',
                'instructions': None,
                'npc_image': npc1_img}
        output = locals()[case]
        assert mystep['step'].get_prompt(username)['prompt'] == output['prompt']
        assert mystep['step'].get_prompt(username)['instructions'] == output['instructions']
        assert mystep['step'].get_prompt(username)['npc_image'] == output['npc_image']

    def test_step_make_replacements(self, mystep):
        """Unit test for method Step._make_replacements()"""
        casenum = mystep['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'raw_string': 'Hi [[user]]!', 'username': 'Ian', 'result': 'Hi Ian!'}
        case2 = {'raw_string': 'Hi there [[user]].', 'username': 'Ian', 'result': 'Hi there Ian.'}
        output = locals()[case]
        assert mystep['step']._make_replacements(raw_prompt=output['raw_string'],
                                                username=output['username']
                                                ) == output['result']

    def test_step_get_responder(self, mystep):
        """Test for method Step.get_responder"""
        the_type = mystep['step'].__class__.__name__
        # Step, StepRedirect, StepViewSlides steps
        map_button = A("Map", _href=URL('walk'),
                        cid='page',
                        _class='button-yellow-grad back_to_map icon-location')
        Step_output = StepRedirect_output = StepViewSlides_output = DIV(map_button).xml()
        # StepText steps
        resp = '<form action="" autocomplete="off" enctype="multipart/form-data" method="post">'
        resp += '<table>'
        resp += '<tr id="no_table_response__row">'
        resp += '<td class="w2p_fl">'
        resp += '<label for="no_table_response" id="no_table_response__label">Response: </label>'
        resp += '</td>'
        resp += '<td class="w2p_fw">'
        resp += '<input class="string" id="no_table_response" name="response" type="text" value="" />'
        resp += '</td>'
        resp += '<td class="w2p_fc"></td>'
        resp += '</tr>'
        resp += '<tr id="submit_record__row">'
        resp += '<td class="w2p_fl"></td>'
        resp += '<td class="w2p_fw"><input type="submit" value="Submit" /></td>'
        resp += '<td class="w2p_fc"></td></tr></table></form>'
        StepText_output = resp
        # StepMultiple steps #TODO: insert stepMultiple responder html here
        StepMultiple_output = None
        output = locals()['{}_output'.format(the_type)]

        assert mystep['step'].get_responder().xml() == output

    def test_step_get_npc(self, mystep):
        """Test for method Step.get_npc"""
        # TODO: make sure the npc really is randomized
        casenum = mystep['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'npc_id': [8, 2, 32, 1, 17],
                'name': ['Διοδωρος', 'Μαρια', 'Στεφανος', 'Ἀλεξανδρος', 'Ἱασων'],
                'locs': [3, 1, 2, 4, 6, 7, 8, 11]}
        case2 = {'npc_id': [8, 2, 32, 1],
                'name': ['Διοδωρος', 'Μαρια', 'Στεφανος', 'Ἀλεξανδρος'],
                'locs': [3, 1, 2, 4, 6, 7, 8, 11]}
        case3 = {'npc_id': [14],
                'name': ['Γεωργιος'],
                'locs': [3, 1, 2, 4, 7, 8, 9, 10]}
        output = locals()[case]
        assert mystep['step'].get_npc().get_id() in output['npc_id']
        assert mystep['step'].get_npc().get_name() in output['name']
        locs = mystep['step'].get_npc().get_locations()
        for l in locs:
            assert isinstance(l, Location)
            assert (l.get_id() in output['locs']) == True

    def test_step_get_instructions(self, mystep):
        """Test for method Step._get_instructions"""
        casenum = mystep['casenum']
        case = 'case{}'.format(casenum)
        case1 = ['Focus on finding Greek letters that make the *sounds* of the English word. Don\'t look for Greek "equivalents" for each English letter.']
        case2 = None
        case3 = None
        output = locals()[case]
        assert mystep['step']._get_instructions() == output

class TestStepRedirect():
    '''
    A subclass of Step. Handles the user interaction when the user needs to be
    sent to another location.
    '''

    def test_stepredirect_get_id(self, myStepRedirect):
        """Test for method Step.get_id"""
        assert myStepRedirect.get_id() == 30

    def test_stepredirect_get_prompt(self, myStepRedirect):
        """
        Test method for the get_prompt method of the StepRedirect class.
        This test assumes that the selected npc is Stephanos. It also assumes
        that the step is 30.
        """
        username = 'Ian'
        assert myStepRedirect.get_prompt(username)['prompt'] == "Hi there. Sorry, I don't have anything for you to do here at the moment. I think someone was looking for you at somewhere else in town."
        assert myStepRedirect.get_prompt(username)['instructions'] == None
        assert (myStepRedirect.get_prompt(username)['npc_image'] == '/paideia/static/images/images.image.a59978facee731f0.44726177696e672031382e737667.svg'
                or myStepRedirect.get_prompt(username)['npc_image'] == '/paideia/static/images/images.image.961b44d8d322659c.323031322d30362d30372031345f34345f34302e706e67.png')

    def test_stepredirect_make_replacements(self, myStepRedirect):
        """docstring for test_stepredirect_make_replacements"""
        string = 'Nothing to do here [[user]]. Try [[next_loc]].'
        next_step = 1
        kwargs = {'raw_prompt':string,
                'username': 'Ian',
                'db': db,
                'next_step_id': next_step}
        newstring = 'Nothing to do here Ian. Try somewhere else in town.'
        assert myStepRedirect._make_replacements(**kwargs) == newstring

    def test_stepredirect_get_tags(self, myStepRedirect):
        """
        Test for method StepRedirect.get_tags

        The one tag that should be returned for all steps of this class is tag
        70 ('default').
        """
        assert myStepRedirect.get_tags() == {'primary': [70], 'secondary': []}

    def test_stepredirect_get_responder(self, myStepRedirect):
        """Test for method Step.get_responder"""
        map_button = A("Map", _href=URL('walk'),
                        cid='page',
                        _class='button-yellow-grad back_to_map icon-location')
        assert myStepRedirect.get_responder().xml() == DIV(map_button).xml()

    def test_stepredirect_get_npc(self, myStepRedirect):
        """Test for method Step.get_npc"""
        # TODO: allow for alternate possibility of Sophia
        assert (myStepRedirect.get_npc().get_id() == 31
                    or myStepRedirect.get_npc().get_id() == 32)
        locs = myStepRedirect.get_npc().get_locations()
        assert isinstance(locs[0], Location)
        assert (locs[0].get_id() == 3) or (locs[0].get_id() == 11)

class TestAwardBadges():
    '''
    A subclass of Step. Handles the user interaction when the user is awarded
    new badges.
    '''

    def test_stepawardbadges_get_id(self, myStepAwardBadges):
        """Test for method Step.get_id"""
        assert myStepAwardBadges['step'].get_id() == 126

    def test_stepawardbadges_get_prompt(self, myStepAwardBadges):
        """
        Test method for the get_prompt method of the StepRedirect class.
        This test assumes that the selected npc is Stephanos. It also assumes
        that the step is 126.
        """
        sd = step_data_store[126]['case1']
        # TODO: remove npc numbers that can't be at this loc
        npcimgs = [n['image'] for k, n in npc_data.iteritems()
                        if k in sd['npc_list']]
        out = {'raw_prompt': sd['raw_prompt'],
                'username': sd['username'],
                'new_badges': sd['new_badges'],
                'db': db}
        prompt = myStepAwardBadges['step'].get_prompt(**out)
        assert prompt['prompt'] == sd['final_prompt']
        assert prompt['instructions'] == sd['instructions']
        assert prompt['npc_image'] in npcimgs

    def test_stepawardbadges_make_replacements(self, myStepAwardBadges):
        """docstring for test_step_stepawardbadges_make_replacements"""
        case = myStepAwardBadges['casenum']
        sd = step_data_store[126]['case{}'.format(case)]
        out = {k: v for k, v in sd.iteritems()
                if k in ['raw_prompt', 'username', 'new_badges', 'promoted']}
        actual = myStepAwardBadges['step']._make_replacements(**out)
        assert actual == sd['final_prompt']

    def test_stepawardbadges_get_tags(self, myStepAwardBadges):
        """
        Test for method StepRedirect.get_tags

        The one tag that should be returned for all steps of this class is 81
        """
        case = myStepAwardBadges['casenum']
        sd = step_data_store[126]['case{}'.format(case)]
        out = {'primary': sd['tags'], 'secondary': sd['tags_secondary']}
        assert myStepAwardBadges['step'].get_tags() == out

    def test_stepawardbadges_get_responder(self, myStepAwardBadges):
        """Test for method StepAwardBadges.get_responder"""
        request = current.request  # TODO: get loc below from self
        map_button = A("Map", _href=URL('walk'),
                        cid='page',
                        _class='button-yellow-grad back_to_map icon-location')
        continue_button = A("Continue", _href=URL('walk', args=['ask'],
                                        vars={'loc':12}),
                            cid='page',
                            _class='button-green-grad next_q')
        assert myStepAwardBadges['step'].get_responder().xml() == \
                                        DIV(map_button, continue_button).xml()

    def test_stepawardbadges_get_npc(self, myStepAwardBadges):
        """Test for method StepAwardBadges.get_npc"""
        assert myStepAwardBadges['step'].get_npc().get_id() in [14, 8, 2, 40, 31,
                                                            32, 41, 1, 17, 42]
        locs = myStepAwardBadges['step'].get_npc().get_locations()
        assert isinstance(locs[0], Location)


class TestStepViewSlides():
    '''
    A subclass of Step. Handles the user interaction when the user is awarded
    new badges.
    '''

    def test_awardbadges_get_id(self, myStepViewSlides):
        """Test for method Step.get_id"""
        assert myStepViewSlides.get_id() == 127

    def test_stepviewslides_get_prompt(self, myStepViewSlides):
        """
        Test method for the get_prompt method of the StepRedirect class.
        This test assumes that the selected npc is Stephanos. It also assumes
        that the step is 30.
        """
        sd = step_data_store[127]['case1']
        # TODO: remove npc numbers that can't be at this
        npcimgs = [n['image'] for k, n in npc_data.iteritems()
                        if k in sd['npc_list']]
        prompt = myStepViewSlides.get_prompt(username=sd['username'],
                                           new_badges=sd['new_badges'])
        assert prompt['prompt'] == sd['final_prompt']
        assert prompt['instructions'] == sd['instructions']
        assert prompt['npc_image'] in npcimgs

    def test_stepviewslides_make_replacements(self, myStepViewSlides):
        """
        docstring for test_step_stepviewslides_make_replacements

        """
        sd = step_data_store[127]['case1']
        prompt = myStepViewSlides._make_replacements(raw_prompt=sd['raw_prompt'],
                                                    username=sd['username'],
                                                    new_badges=[5, 6])
        print prompt, '\n'
        print sd['final_prompt']
        assert prompt == sd['final_prompt']

    def test_stepviewslides_get_tags(self, myStepViewSlides):
        """
        Test for method StepViewSlides.get_tags

        The one tag that should be returned for all steps of this class is tag
        80.
        """
        assert myStepViewSlides.get_tags() == {'primary': [80], 'secondary': []}

    def test_stepviewslides_get_responder(self, myStepViewSlides):
        """Test for method StepViewSlides.get_responder"""
        map_button = A("Map", _href=URL('walk'),
                        cid='page',
                        _class='button-yellow-grad back_to_map icon-location')
        assert myStepViewSlides.get_responder().xml() == DIV(map_button).xml()

    def test_stepviewslides_get_npc(self, myStepViewSlides):
        """Test for method StepViewSlides.get_npc"""
        assert myStepViewSlides.get_npc().get_id() in [14, 8, 2, 40, 31,
                                                            32, 41, 1, 17, 42]
        locs = myStepViewSlides.get_npc().get_locations()
        assert isinstance(locs[0], Location)


class TestStepText():
    '''
    Test class for paideia.StepText
    '''
    def test_steptext_get_responder(self, myStepText):
        resp = '<form action="" autocomplete="off" enctype="multipart/form-data" method="post">'
        resp += '<table>'
        resp += '<tr id="no_table_response__row">'
        resp += '<td class="w2p_fl">'
        resp += '<label for="no_table_response" id="no_table_response__label">Response: </label>'
        resp += '</td>'
        resp += '<td class="w2p_fw">'
        resp += '<input class="string" id="no_table_response" name="response" type="text" value="" />'
        resp += '</td>'
        resp += '<td class="w2p_fc"></td>'
        resp += '</tr>'
        resp += '<tr id="submit_record__row">'
        resp += '<td class="w2p_fl"></td>'
        resp += '<td class="w2p_fw"><input type="submit" value="Submit" /></td>'
        resp += '<td class="w2p_fc"></td></tr></table></form>'
        assert myStepText['step'].get_responder().xml() == resp

    def test_steptext_get_readable(self, myStepText):
        """Unit tests for StepText._get_readable() method"""
        casenum = myStepText['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'readable_long': None, 'readable_short': ['μιτ']}
        case2 = {'readable_long': None, 'readable_short': ['βατ|βοτ']}
        output = locals()[case]
        assert myStepText['step']._get_readable() == output

    def test_steptext_get_reply(self, myStepText):
        """Unit tests for StepText._get_reply() method"""
        casenum = myStepText['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'response': 'μιτ',
                'result': {'reply_text': 'Right. Κάλον.',
                            'tips': [],
                            'readable_short': ['μιτ'],
                            'readable_long': None,
                            'score': 1,
                            'times_right': 1,
                            'times_wrong': 0,
                            'user_response': 'μιτ'}}

        case2 = {'response': 'βλα',
                'result': {'reply_text': 'bla',
                            'tips': None,
                            'readable_short': ['bla'],
                            'readable_long': None,
                            'score': 0,
                            'times_right': 0,
                            'times_wrong': 1,
                            'user_response': 'βλα'}}
        out = locals()[case]
        func = myStepText['step'].get_reply(user_response=out['response'])
        for k, f in func.iteritems():
            assert  f == out['result'][k]

class TestStepMultiple():
    '''
    Test class for paideia.StepMultiple
    '''
    def test_stepmultiple_get_responder(self, myStepMultiple):
        """Unit testing for get_responder method of StepMultiple."""

        # value of _formkey input near end is variable, so matched with .*
        resp = '^<form action="" enctype="multipart/form-data" method="post">'
        resp += '<table>'
        resp += '<tr id="no_table_response__row">'
        resp += '<td class="w2p_fl">'
        resp += '<label for="no_table_response" id="no_table_response__label">Response: </label>'
        resp += '</td>'
        resp += '<td class="w2p_fw">'
        resp += '<table class="generic-widget" id="no_table_response" name="response">'
        resp += '<tr>'
        resp += '<td>'
        resp += '<input id="responseναι" name="response" type="radio" value="ναι" />'
        resp += '<label for="responseναι">ναι</label>'
        resp += '</td>'
        resp += '</tr>'
        resp += '<tr>'
        resp += '<td>'
        resp += '<input id="responseοὐ" name="response" type="radio" value="οὐ" />'
        resp += '<label for="responseοὐ">οὐ</label>'
        resp += '</td>'
        resp += '</tr>'
        resp += '</table>'
        resp += '</td>'
        resp += '<td class="w2p_fc"></td>'
        resp += '</tr>'
        resp += '<tr id="submit_record__row">'
        resp += '<td class="w2p_fl"></td>'
        resp += '<td class="w2p_fw">'
        resp += '<input type="submit" value="Submit" /></td>'
        resp += '<td class="w2p_fc"></td>'
        resp += '</tr>'
        resp += '</table>'
        resp += '<div class="hidden">'
        resp += '<input name="_formkey" type="hidden" value=".*" />'
        resp += '<input name="_formname" type="hidden" value="no_table/create" />'
        resp += '</div>'
        resp += '</form>$'

        testfunc = myStepMultiple['step'].get_responder().xml()
        assert re.match(resp, testfunc)

    def test_stepmultiple_get_reply(self, myStepMultiple):
        """Unit testing for get_reply method of StepMultiple."""
        casenum = myStepMultiple['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'reply_text': 'Right. Κάλον.',
                'tips': [],
                'readable_short': ['ναι'],
                'readable_long': None,
                'score': 1,
                'times_right': 1,
                'times_wrong': 0,
                'user_response': 'ναι'}
        case2 = {'reply_text': 'Incorrect. Try again!',
                'tips': [],
                'readable_short': ['οὐ'],
                'readable_long': None,
                'score': 0,
                'times_right': 0,
                'times_wrong': 1,
                'user_response': 'οὐ'}
        out = locals()[case]
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['reply_text'] == out['reply_text']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['tips'] == out['tips']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['readable_short'] == out['readable_short']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['readable_long'] == out['readable_long']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['score'] == out['score']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['times_right'] == out['times_right']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['times_wrong'] == out['times_wrong']
        assert myStepMultiple['step'].get_reply(out['user_response']
                                    )['user_response'] == out['user_response']


class TestStepEvaluator():
    """Class for evaluating the submitted response string for a Step"""

    def test_stepevaluator_get_eval(self, myStepEvaluator):
        """Unit tests for StepEvaluator.get_eval() method."""
        casenum = myStepEvaluator['casenum']
        case = 'case{}'.format(casenum)
        case1 = {'reply_text': 'Right. Κάλον.',
                'tips': None,
                'readable_short': ['μιτ'],
                'readable_long': None,
                'score': 1,
                'times_right': 1,
                'times_wrong': 0,
                'user_response': 'μιτ'}
        case2 = {'reply_text': 'Right. Κάλον.',
                'tips': None,
                'readable_short': ['ναι'],
                'readable_long': None,
                'score': 1,
                'times_right': 1,
                'times_wrong': 0,
                'user_response': 'βατ'}
        out = locals()[case]

        assert myStepEvaluator['eval'].get_eval(out['user_response']
                                        )['score'] == out['score']
        assert myStepEvaluator['eval'].get_eval(out['user_response']
                                        )['times_wrong'] == out['times_wrong']
        assert myStepEvaluator['eval'].get_eval(out['user_response']
                                        )['reply'] == out['reply_text']
        assert myStepEvaluator['eval'].get_eval(out['user_response']
                                        )['user_response'] == out['user_response']
        assert myStepEvaluator['eval'].get_eval(out['user_response']
                                        )['tips'] == out['tips']


class TestMultipleEvaluator():
    """Class for evaluating the submitted response string for a StepMultiple"""

    def test_multipleevaluator_get_eval(self, myMultipleEvaluator):
        """Unit tests for StepEvaluator.get_eval() method."""
        casenum = myMultipleEvaluator['casenum']
        case = 'case{}'.format(casenum)
        # step 101
        case1 = {'reply_text': 'Right. Κάλον.',
                'tips': None,
                'readable_short': ['ναι'],
                'readable_long': None,
                'score': 1,
                'times_right': 1,
                'times_wrong': 0,
                'user_response': 'ναι'}
        # step 101
        case2 = {'reply_text': 'Incorrect. Try again!',
                'tips': None,
                'readable_short': ['ναι'],
                'readable_long': None,
                'score': 1,
                'times_right': 1,
                'times_wrong': 0,
                'user_response': 'οὐ'}
        out = locals()[case]
        assert myMultipleEvaluator['eval'].get_eval(out['user_response']
                )['score'] == out['score']
        assert myMultipleEvaluator['eval'].get_eval(out['user_response']
                )['times_wrong'] == out['times_wrong']
        assert myMultipleEvaluator['eval'].get_eval(out['user_response']
                )['reply'] == out['reply_text']
        assert myMultipleEvaluator['eval'].get_eval(out['user_response']
                )['user_response'] == out['user_response']
        assert myMultipleEvaluator['eval'].get_eval(out['user_response']
                )['tips'] == out['tips']


class TestPath():
    """Unit testing class for the paideia.Path object"""

    def test_path_get_step_for_prompt(self, mypath):
        """docstring for test_get_next_step"""
        output = 'output{}'.format(mypath['casenum'])
        # for path 3, text, single step
        output1 = StepFactory().get_instance(step_id=2, loc=Location(1, db),
                                        prev_loc=1, prev_npc_id=2, db=db)
        # for path 89, multiple, single step
        output2 = StepFactory().get_instance(step_id=101, loc=Location(8, db),
                                        prev_loc=None, prev_npc_id=1, db=db)
        ready_path = mypath['path']
        ready_path._prepare_for_prompt()
        pstep = ready_path.get_step_for_prompt()
        ostep = locals()[output]
        assert pstep.get_id() == ostep.get_id()
        assert pstep.get_tags() == ostep.get_tags()
        assert pstep.get_locations() == ostep.get_locations()
        assert pstep.get_prompt(username='Joe') \
                                        == ostep.get_prompt(username='Joe')

    def test_path_prepare_for_answer(self, mypath):
        """Unit test for method paideia.Path.get_step_for_reply."""
        casenum = mypath['casenum']
        case = 'case{}'.format(casenum)
        # path 3, text
        case1 = {'step_for_reply_end': 2,
                'step_for_prompt_start': 2,
                'step_for_prompt_end': None,
                'step_sent_id': 2}
        # path 89, multiple
        case2 = {'step_for_reply_end': 101,
                'step_for_prompt_start': 101,
                'step_for_prompt_end': None,
                'step_sent_id': 101}
        output = locals()[case]
        sent_id = output['step_sent_id']
        test_func = mypath['path'].prepare_for_answer(
                step_for_prompt=StepFactory().get_instance(
                            db=db, step_id=output['step_for_prompt_start']),
                step_for_reply=None,
                step_sent_id=output['step_sent_id'])
        assert test_func['step_sent_id'] == output['step_sent_id']
        assert test_func['step_for_prompt'] == output['step_for_prompt_end']
        assert test_func['step_for_reply'] == output['step_for_reply_end']

    def test_path_remove_block(self, mypath):
        """Unit test for method paideia.Path.remove_block."""
        casenum = mypath['casenum']
        if not casenum in [1, 2]:
            case = 'case{}'.format(casenum)
            case3 = {'block_done': Block(), 'blocks': []}
            output = locals()[case]
            assert mypath['path'].remove_block() == output

    def test_path_get_step_for_reply(self, mypath):
        """Unit test for method paideia.Path.get_step_for_reply."""
        out = {1: StepFactory().get_instance(step_id=2, loc=Location(1, db),
                                        prev_loc=1, prev_npc_id=2, db=db),
              2: StepFactory().get_instance(step_id=101,
                  loc=Location(8, db), prev_loc=None, prev_npc_id=1, db=db)
              }
        path = mypath['path']
        path._prepare_for_prompt()
        pstep = path.get_step_for_prompt()
        path.prepare_for_answer(step_for_prompt=pstep, step_sent_id=pstep.get_id())
        rstep = path.get_step_for_reply()

        assert path.get_step_for_prompt() is None
        assert rstep.get_id() == out[mypath['casenum']].get_id()

class TestPathChooser():
    """Unit testing class for the paideia.PathChooser class."""
    pass

class TestUser():
    """unit testing class for the paideia.User class"""

    def test_user_get_id(self, myuser):
        assert myuser.get_id() == 1

    def test_user_is_stale(self, myuser):
        assert 1

    def test_user_get_categories(self, myuser):
        assert 1

    def test_user_get_old_categories(self, myuser):
        assert 1

    def test_user_get_new_badges(self, myuser):
        assert 1

    def test_user_complete_path(self, myuser):
        assert 1

    def test_user_get_path(self, myuser):
        assert 1


class TestCategorizer():
    """Unit testing class for the paideia.Categorizer class"""

    def test_categorizer_categorize(self, mycategorizer):
        """
        Unit test for the paideia.Categorizer.categorize method.

        Case numbers correspond to the cases (user performance scenarios) set
        out in the myrecords fixture.
        case 1: removes tag 1 (too early) and introduces untried tag 61
        """
        case = 'case{}'.format(mycategorizer['casenum'])
        output = {
            'case1': {'tag_progress': {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                        'new_tags': {'cat1': [61]},
                        'promoted': {'cat1': []},
                        'demoted': {},
                        'categories': {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': []}
                        },

            'case2': {'tag_progress': {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                        'new_tags': {'cat1': [61]},
                        'promoted': {'cat1': []},
                        'demoted': {},
                        'categories': {'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': []}
                        },
            }
        assert mycategorizer['categorizer'].categorize_tags() == output[case]

    def test_categorizer_core_algorithm(self, mycategorizer):
        """
        Unit test for the paideia.Categorizer._core_algorithm method

        Case numbers correspond to the cases (user performance scenarios) set
        out in the myrecords fixture.
        """
        case = 'case{}'.format(mycategorizer['casenum'])
        output = {'case1': {'cat1': [1], 'cat2': [], 'cat3': [], 'cat4': []},
                'case2': {'cat1': [1], 'cat2': [], 'cat3': [], 'cat4': []}}

        assert mycategorizer['categorizer']._core_algorithm() == output[case]

    def test_categorizer_introduce_tags(self):
        """Unit test for the paideia.Categorizer._introduce_tags method"""
        pass

    def test_categorizer_add_untried_tags(self, mycategorizer):
        """Unit test for the paideia.Categorizer._add_untried_tags method"""
        input_cats = {'cat1': [1], 'cat2': [],
                        'cat3': [], 'cat4': []}
        output_cats = {'cat1': [1, 61], 'cat2': [],
                        'cat3': [], 'cat4': []}
        assert mycategorizer['categorizer']._add_untried_tags(input_cats) == \
                                                                output_cats

    def test_categorizer_find_cat_changes(self):
        """docstring for test_"""
        pass

class TestWalk():
    """
    A unit testing class for the paideia.Walk class.
    """

    def test_walk_get_user(self, mywalk, myrecords, mysession):
        """docstring for _get_user"""
        localias = mywalk.localias
        userdata = {'first_name': 'Joe', 'id': 1}
        tag_records = myrecords['tag_records']
        tag_progress = myrecords['tag_progress']
        assert mywalk._get_user(userdata=userdata, localias=localias,
                        tag_records=tag_records, tag_progress=tag_progress)

    def test_walk_map(self, mywalk):
        mapdata = {'map_image': '/paideia/static/images/town_map.svg',
                    'locations': [
                        {'alias': 'None',
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
        map = mywalk.map()
        pprint(map)
        for m in mapdata['locations']:
            i = mapdata['locations'].index(m)
            assert map['locations'][i]['alias'] == m['alias']
            assert map['locations'][i]['bg_image'] == m['bg_image']
            assert map['locations'][i]['id'] == m['id']
        assert map['map_image'] == mapdata['map_image']

    def test_walk_ask(self, mywalk):
        prompt = ''
        responder = ''
        ask = mywalk.ask()
        assert ask['prompt'] == prompt
        assert ask['responder'] == responder

    def test_walk_reply(self, mywalk):
        assert 0

    def test_walk_record_step(self, mywalk):
        assert 0

    def test_walk_cache_user(self, mywalk):
        assert 0

    def test_pathchooser_choose(self, mypathchooser):
        newpath = mypathchooser['pathchooser'].choose()
        assert newpath.isinstance(Path)
        assert newpath.get_id() in mypathchooser['paths']

    def test_pathchooser_order_cats(self, mypathchooser):
        pc = mypathchooser['pathchooser']._order_cats()
        print pc
        ind = pc.index(1)
        if len(pc) >= (ind + 2):
            assert pc[ind + 1] == 2
        if len(pc) >= (ind + 3):
            assert pc[ind + 2] == 3
        if len(pc) >= (ind + 2):
            assert pc[ind + 3] == 4
        if ind != 0:
            assert pc[ind - 1] == 4
        assert len(pc) == 4
        assert pc[0] in [1,2,3,4]
        assert pc[1] in [1,2,3,4]
        assert pc[2] in [1,2,3,4]
        assert pc[3] in [1,2,3,4]

    def test_pathchooser_paths_by_category(self, mypathchooser):
        assert 0

    def test_pathchooser_choose_from_cat(self, mypathchooser):
        assert 0

