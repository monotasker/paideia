# -*- coding: utf-8 -*-
# Unit tests for the paideia module

import pytest
from paideia import Npc, Location, User, Step, StepRedirect, StepText
from paideia import StepEvaluator, Path, PathChooser, Categorizer, Walk
from gluon import *
import datetime

# ===================================================================
# Test Fixtures
# ===================================================================

db = current.db
def dt(string):
    """Return datetime object parsed from the string argument supplied"""
    format = "%Y-%m-%d"
    return datetime.datetime.strptime(string, format)

@pytest.fixture(params=['case{}'.format(n) for n in range(1,2)])
def myrecords(request):
    """pytest fixture for providing user records."""
    case = request.param
    case1 = {'casenum': 1, 'mynow': dt('2013-01-29'),
            'attempt_log': [{'step': None, 'path': None, 'score': None,
                            'dt_attempted': None} ],
            'tag_records': [{'tag_id': 1,
                             'last_right': dt('2013-01-29'),
                             'last_wrong': dt('2013-01-29'),
                             'times_right': 1, 'times_wrong': 1}],
            'tag_progress': {'latest_new': 1,
                            'cat1': [], 'cat2': [], 'cat3': [], 'cat4': [],
                            'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}}

    case2 = {'casenum': 2, 'mynow': dt('2013-01-29'),
            'attempt_log': [{'step': None, 'path': None, 'score': None,
                            'dt_attempted': None} ],
            'tag_records': [{'tag_id': 1,
                             'last_right': dt('2013-01-29'),
                             'last_wrong': dt('2013-01-29'),
                             'times_right': 1, 'times_wrong': 1}],
            'tag_progress': {'latest_new': 1,
                            'cat1': [], 'cat2': [], 'cat3': [], 'cat4': [],
                            'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}}

    return locals()[case]

@pytest.fixture
def mycategorizer(myrecords, request):
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
    loc_alias = 'shop_of_alexander'
    tag_progress = myrecords['tag_progress']
    tag_records = myrecords['tag_records']
    return User(userdata, loc_alias, tag_records, tag_progress)

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

@pytest.fixture(params=['case{}'.format(p) for p in range(1,2)])
def mypath(request):
    """
    A pytest fixture providing a paideia.Path object for testing.
    """
    # StepText loc and prev_npc both work, no blocks, no prev_loc
    case = request.param
    case1 = {'args': [1, None, 8, None, 1],
            'kwargs': {'db': db}}
    # StepText loc and prev_npc both work, no blocks, no prev_loc
    case2 = {'args': [1, None, 8, None, 1],
            'kwargs': {'db': db}}
    casedict = locals()[case]
    return {'casenum': case[4:], 'path': Path(*casedict['args'], **casedict['kwargs'])}

@pytest.fixture
def mystep():
    """
    A pytest fixture providing a paideia.Step object for testing.
    - same npc and location as previous step
    TODO: write another fixture for a new location and for a new npc
    """
    loc = Location(8, db)
    prev_loc = Location(8, db)
    prev_npc_id = 1
    return Step(1, loc, prev_loc, prev_npc_id, db=db)

@pytest.fixture
def myStepRedirect():
    """
    A pytest fixture providing a paideia.StepRedirect object for testing.
    - same npc and location as previous step
    TODO: write another fixture for a new location and for a new npc
    """
    loc = Location(11, db) # synagogue
    prev_loc = Location(11, db)
    prev_npc_id = 31 # stephanos
    return StepRedirect(30, loc, prev_loc, prev_npc_id, db=db)

@pytest.fixture
def myStepText():
    """ """
    loc = Location(8, db)
    prev_loc = Location(8, db)
    prev_npc_id = 1
    return StepText(1, loc, prev_loc, prev_npc_id, db=db)

@pytest.fixture
def myStepEvaluator():
    """
    A pytest fixture providing a paideia.StepEvaluator object for testing.
    """
    step = db.steps[1]
    answers = [step.response1, step.response2, step.response3]
    tips = step.hints
    return StepEvaluator(answers, tips)

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
        assert mynpc.get_image().xml() == '<img src="/paideia/static/images/images.image.bb48641f0122d2b6.696d616765732e696d6167652e383136303330663934646664646561312e34343732363137373639366536373230333432653733373636372e737667.svg" />'

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
        assert mystep.get_id() == 1

    def test_step_get_tags(self, mystep):
        """Test for method Step.get_tags"""
        assert mystep.get_tags() == {'primary': [61], 'secondary': []}

    def test_step_get_prompt(self, mystep):
        """Test for method Step.get_prompt"""
        username = 'Ian'
        assert mystep.get_prompt(username)['prompt'] == 'How could you write the word "meet" using Greek letters?'
        assert mystep.get_prompt(username)['instructions'].xml() == '<ul class="step_instructions"><li>Focus on finding Greek letters that make the *sounds* of the English word. Don&#x27;t look for Greek &quot;equivalents&quot; for each English letter.</li></ul>'
        assert mystep.get_prompt(username)['npc_image'].xml() == '<img src="/paideia/static/images/images.image.bb48641f0122d2b6.696d616765732e696d6167652e383136303330663934646664646561312e34343732363137373639366536373230333432653733373636372e737667.svg" />'

    def test_step_make_replacements(self, mystep):
        """Unit test for method Step._make_replacements()"""
        raw_string = 'Hi [[user]]!'
        username = 'Ian'
        assert mystep._make_replacements(raw_string, username) == 'Hi Ian!'

    def test_step_get_responder(self, mystep):
        """Test for method Step.get_responder"""
        map_button = A("Map", _href=URL('walk'),
                        cid='page',
                        _class='button-yellow-grad back_to_map icon-location')
        assert mystep.get_responder().xml() == DIV(map_button).xml()

    def test_step_get_npc(self, mystep):
        """Test for method Step.get_npc"""
        # TODO: make sure the npc really is randomized
        assert mystep.get_npc().get_id() == 1

        locs = mystep.get_npc().get_locations()
        assert isinstance(locs[0], Location)
        assert locs[0].get_id() == 6
        assert isinstance(locs[1], Location)
        assert locs[1].get_id() == 8

    def test_step_get_instructions(self, mystep):
        """Test for method Step._get_instructions"""
        assert mystep._get_instructions().xml() == '<ul class="step_instructions"><li>Focus on finding Greek letters that make the *sounds* of the English word. Don&#x27;t look for Greek &quot;equivalents&quot; for each English letter.</li></ul>'

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
        assert myStepRedirect.get_prompt(username)['npc_image'].xml() == '<img src="/paideia/static/images/images.image.a59978facee731f0.44726177696e672031382e737667.svg" />'

    def test_stepredirect_make_replacements(self, myStepRedirect):
        """docstring for test_stepredirect_make_replacements"""
        string = 'Nothing to do here [[user]]. Try [[next_loc]].'
        next_step = 1
        kwargs = {'username': 'Ian', 'db': db, 'next_step': next_step}
        newstring = 'Nothing to do here Ian. Try somewhere else in town.'
        assert myStepRedirect._make_replacements(string, **kwargs) == newstring

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
        assert myStepRedirect.get_npc().get_id() == 31

        locs = myStepRedirect.get_npc().get_locations()
        assert isinstance(locs[0], Location)
        assert (locs[0].get_id() == 3) or (locs[0].get_id() == 11)

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
        assert myStepText.get_responder().xml() == resp

    def test_steptext_get_reply(self, myStepText):
        pass

class TestStepEvaluator():
    """Class for evaluating the submitted response string for a Step"""

    def test_stepevaluator_get_eval(self, myStepEvaluator):
        user_response = 'μιτ'
        assert myStepEvaluator.get_eval(user_response)['score'] == 1
        assert myStepEvaluator.get_eval(user_response)['times_wrong'] == 0
        assert myStepEvaluator.get_eval(user_response)['reply'] == 'Right. Κάλον.'
        assert myStepEvaluator.get_eval(user_response)['user_response'] == 'μιτ'
        assert myStepEvaluator.get_eval(user_response)['tips'] == []

class TestPath():
    """Unit testing class for the paideia.Path object"""

    def test_get_next_step(self, mypath):
        """docstring for test_get_next_step"""
        output = 'output{}'.format(mypath['casenum'])
        output1 = Step(71, 8, None, 1, db=db)
        output2 = Step(71, 8, None, 1, db=db)
        assert mypath['path'].get_next_step(8) == output


class TestPathChooser():
    pass

class TestUser():
    """unit testing class for the paideia.User class"""

    def test_user_get_id(self, myuser):
        assert myuser.get_id() == 1

class TestCategorizer():
    """Unit testing class for the paideia.Categorizer class"""

    def test_categorize(self, mycategorizer):
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
                        'demoted': {}},

            'case2': {'tag_progress': {'latest_new': 1,
                                'cat1': [61], 'cat2': [],
                                'cat3': [], 'cat4': [],
                                'rev1': [], 'rev2': [],
                                'rev3': [], 'rev4': []},
                        'new_tags': {'cat1': [61]},
                        'promoted': {'cat1': []},
                        'demoted': {}},
            }
        assert mycategorizer['categorizer'].categorize_tags() == output[case]

    def test_core_algorithm(self, mycategorizer):
        """
        Unit test for the paideia.Categorizer._core_algorithm method

        Case numbers correspond to the cases (user performance scenarios) set
        out in the myrecords fixture.
        """
        case = 'case{}'.format(mycategorizer['casenum'])
        output = {'case1': {'cat1': [1], 'cat2': [], 'cat3': [], 'cat4': []},
                'case2': {'cat1': [1], 'cat2': [], 'cat3': [], 'cat4': []}}

        assert mycategorizer['categorizer']._core_algorithm() == output[case]

    def test_introduce_tags(self):
        """Unit test for the paideia.Categorizer._introduce_tags method"""
        pass

    def test_add_untried_tags(self, mycategorizer):
        """Unit test for the paideia.Categorizer._add_untried_tags method"""
        input_cats = {'cat1': [1], 'cat2': [],
                        'cat3': [], 'cat4': []}
        output_cats = {'cat1': [1, 61], 'cat2': [],
                        'cat3': [], 'cat4': []}
        assert mycategorizer['categorizer']._add_untried_tags(input_cats) == \
                                                                output_cats

    def test_find_cat_changes(self):
        """docstring for test_"""
        pass

class TestWalk():
    pass
