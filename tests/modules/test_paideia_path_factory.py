#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the modulename module

 Configuration and some fixtures
 the file tests/conftest.py
 run with py.test -xvs path/to/tests/dir

"""

import pytest
import re
# from pprint import pprint
from paideia_path_factory import PathFactory


@pytest.fixture()
def mystepinfo():
    """docstring for mystepinfo"""

    stepinfo = [{'step_type': 4,
                 'prompt_template': ['Can you get some {words1} from the '
                                     '{words2}.'],
                 'response_template': ['Yes,\s(?P<a>I\s)?(?(a)|we\s)can\sget'
                                       '\ssome\s{words1}\sfrom\sthe\s{words2}.'],
                 'readable_template': ['Yes, I can get some {words1} from the '
                                       '{words2}.',
                                       'Yes, we can get some {words1} from the '
                                       '{words2}.'],
                 'npcs': [12, 6],
                 'locations': [1],
                 'image_template': 'foods_{words1}',
                 'tags': [2, 36, 48],
                 'tags_secondary': [3],
                 'tags_ahead': [4],
                 'instructions': [],
                 'hints': []
                 },
                ]
    return stepinfo


@pytest.fixture()
def create_form():
    form = [r'<form action="#" enctype="multipart/form-data" method="post">'
            '<table>'
            '<tr id="no_table_label_template__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_label_template" id="no_table_label_template__label">'
            'Label Template: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<input class="string" id="no_table_label_template" name="label_template" type="text" value="" />'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_words__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_words" id="no_table_words__label">Words: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<ul class="w2p_list" id="no_table_words_grow_input" style="list-style:none">'
            '<li><input class="string" id="no_table_words" name="words" type="text" value="" /></li>'
            '</ul>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_aligned__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_aligned" id="no_table_aligned__label">Aligned: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<input class="boolean" id="no_table_aligned" name="aligned" type="checkbox" value="on" />'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_avoid__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_avoid" id="no_table_avoid__label">Avoid: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<ul class="w2p_list" id="no_table_avoid_grow_input" style="list-style:none">'
            '<li>'
            '<input class="string" id="no_table_avoid" name="avoid" type="text" value="" />'
            '</li>'
            '</ul>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_testing__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_testing" id="no_table_testing__label">Testing: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<input class="boolean" id="no_table_testing" name="testing" type="checkbox" value="on" />'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_prompt_template__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_prompt_template" id="no_table_one_prompt_template__label">One Prompt Template: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<ul class="w2p_list" id="no_table_one_prompt_template_grow_input" style="list-style:none">'
            '<li><input class="string" id="no_table_one_prompt_template" name="one_prompt_template" type="text" value="" /></li>'
            '</ul>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_response_template__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_response_template" id="no_table_one_response_template__label">One Response Template: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<ul class="w2p_list" id="no_table_one_response_template_grow_input" style="list-style:none">'
            '<li>'
            '<input class="string" id="no_table_one_response_template" name="one_response_template" type="text" value="" />'
            '</li>'
            '</ul>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_readable_template__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_readable_template" id="no_table_one_readable_template__label">One Readable Template: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<ul class="w2p_list" id="no_table_one_readable_template_grow_input" style="list-style:none">'
            '<li>'
            '<input class="string" id="no_table_one_readable_template" name="one_readable_template" type="text" value="" /></li>'
            '</ul>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_tags__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_tags" id="no_table_one_tags__label">One Tags: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<select class="generic-widget" id="no_table_one_tags" multiple="multiple" name="one_tags" size="5">',
            '.*'
            '</select>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_tags_secondary__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_tags_secondary" id="no_table_one_tags_secondary__label">One Tags Secondary: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<select class="generic-widget" id="no_table_one_tags_secondary" multiple="multiple" name="one_tags_secondary" size="5">'
            '.*'
            '</select>'
            '</select>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_tags_ahead__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_tags_ahead" id="no_table_one_tags_ahead__label">One Tags Ahead: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<select class="generic-widget" id="no_table_one_tags_ahead" multiple="multiple" name="one_tags_ahead" size="5">'
            '.*'
            '</select>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_instructions__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_instructions" id="no_table_one_instructions__label">One Instructions: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<select class="generic-widget" id="no_table_one_instructions" multiple="multiple" name="one_instructions" size="5">'
            '.*'
            '</select>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_hints__row">'
            '<td class="w2p_fl"><label for="no_table_one_hints" id="no_table_one_hints__label">One Hints: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<select class="generic-widget" id="no_table_one_hints" multiple="multiple" name="one_hints" size="5">'
            '.*'
            '</select>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_step_type__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_step_type" id="no_table_one_step_type__label">One Step Type: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<select class="generic-widget" id="no_table_one_step_type" multiple="multiple" name="one_step_type" size="5">'
            '.*'
            '</select>'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '<tr id="no_table_one_image_template__row">'
            '<td class="w2p_fl">'
            '<label for="no_table_one_image_template" id="no_table_one_image_template__label">One Image Template: </label>'
            '</td>'
            '<td class="w2p_fw">'
            '<input class="string" id="no_table_one_image_template" name="one_image_template" type="text" value="" />'
            '</td>'
            '<td class="w2p_fc">'
            '</td>'
            '</tr>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '.*'
            '<tr id="submit_record__row">'
            '<td class="w2p_fl"></td>'
            '<td class="w2p_fw">'
            '<input type="submit" value="Submit" />'
            '</td>'
            '<td class="w2p_fc"></td>'
            '</tr>'
            '</table>'
            '<div style="display:none;">'
            '<input name="_formkey" type="hidden" value="'
            '.*'
            '" />'
            '<input name="_formname" type="hidden" value="no_table/create" />'
            '</div>'
            '</form>']
    return form[0]


class TestPathFactory():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('message,output',
        [('', '')
         ])
    def test_make_create_form(self, message, output, create_form):
        """
        Test method for the PathFactory.make_create_form() method.
        """
        f = PathFactory()
        actual = f.make_create_form()

        assert re.match(create_form, actual[0].xml())
        assert actual[1] == message
        assert actual[2] == output

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordlists,aligned,avoid,out',
        [([['hi', 'greetings'],  # wordlists ================================ 1
           ['there', 'again'],
           ['friend', 'buddy']
           ],
          False,  # aligned
          [('hi', 'again', 'buddy'),  # avoid
           ],
          [('hi', 'there', 'friend'),  # out
           ('hi', 'there', 'buddy'),
           ('hi', 'again', 'friend'),
           ('greetings', 'there', 'friend'),
           ('greetings', 'there', 'buddy'),
           ('greetings', 'again', 'friend'),
           ('greetings', 'again', 'buddy')]
          ),
         ([['hi', 'greetings'],  # wordlists ================================ 2
           ['there', 'again'],
           ['friend', 'buddy']
           ],
          True,  # aligned
          None,  # avoid
          [('hi', 'there', 'friend'),  # out
           ('greetings', 'again', 'buddy')
           ]
          )
         ])
    def test_make_combos(self, wordlists, aligned, avoid, out):
        """
        Test method for the PathFactory.make_combos method.

        wordlists arg is a list of lists
        avoid is a list of tuples
        aligned is a bool
        """
        f = PathFactory()
        actual = f.make_combos(wordlists, aligned, avoid)
        assert actual == out

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('combodict,out',
        [({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
           ('foods_ἀρτος',  # out
            True)  # this boolean indicates whether the image row is new
          ),
         ({'words1': 'βλαβλα',  # combodict: nonsense to test new img creation
            'words2': 'πωλιον'},
           ('foods_βλαβλα',  # out
            True)  # this boolean indicates whether the image row is new
          ),
         ])
    def test_make_image(self, combodict, out, mystepinfo, db):
        """
        Test method for PathFactory.make_image() method.
        """
        image_template = mystepinfo[0]['image_template']
        f = PathFactory()
        rowid, title, newrow = f.make_image(combodict, image_template)
        # clean up db
        if newrow:
            db(db.images.id == rowid).delete()
        assert isinstance(rowid, (long, int))
        assert title == out[0]
        assert newrow == out[1]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('constraint,out',
            [('c@g_g@m_n@pl',
              {'grammatical_case': 'genitive',
               'gender': 'masculine',
               'number': 'plural'}
              ),
             ('case@gen_gen@masc_num@plur',
              {'grammatical_case': 'genitive',
               'gender': 'masculine',
               'number': 'plural'}
              ),
             ('c@d_g@f_n@s_ps@nn',
              {'grammatical_case': 'dative',
               'gender': 'feminine',
               'number': 'singular',
               'part_of_speech': 'noun'}
              ),
             ('ps@vb_pers@1_n@s_t@pr_v@act_m@sbj',
              {'part_of_speech': 'verb',
               'person': 'first',
               'number': 'singular',
               'tense': 'present',
               'voice': 'active',
               'mood': 'subjunctive'}
              )
             ])
    def test_parse_constraint(self, constraint, out):
        """
        """
        f = PathFactory()
        actual = f._parse_constraint(constraint)
        for k, v in actual.iteritems():
            assert v == out[k]
        assert not [k for k in out.keys() if k not in actual.keys()]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordform,out',
            [('ἀρτος', 'noun'),
             ('λυω', 'verb'),
             ('ἀληθεια', 'noun'),
             ('ἰχθυς', 'noun'),
             ('ταχεως', 'adverb')
             ])
    def test_guess_part_of_speech(self, wordform, out):
        """
        """
        f = PathFactory()
        actual = f._guess_part_of_speech(wordform)
        assert actual == out

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordform,lemma,out',
            [(u'ἀρτοις', u'ἀρτος',
              {'grammatical_case': 'dative', 'gender': 'masculine',
               'number': 'plural', 'declension': '2decl'}
              ),
             (u'ἀληθειας', u'ἀληθεια',
              {'grammatical_case': None, 'gender': 'feminine',
               'number': None, 'declension': '1decl'}
              ),
             (u'ἰχθυας', u'ἰχθυς',
              {'grammatical_case': 'accusative', 'gender': None,
               'number': 'plural', 'declension': '3decl'}
              ),
             ])
    def test_guess_parsing(self, wordform, lemma, out):
        """
        """
        f = PathFactory()
        actual = f._guess_parsing(wordform, lemma)
        assert actual == out

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordform,mod_form,lemma,constraint,out',
            [('ἀρτος',
              None,
              'ἀρτος',
              'case@nom_g@m_num@s',
              {'word_form': 'ἀρτος',
               'source_lemma': 'ἀρτος',
               'grammatical_case': 'nominative',
               'gender': 'masculine',
               'number': 'singular',
               'construction': 'noun_nom_masc_sing_2decl',
               'tags': [1, 82, 117]}
              ),
             ('ἀρτῳ', None, 'ἀρτος', None,
              {'word_form': 'ἀρτῳ',
               'source_lemma': 'ἀρτος',
               'grammatical_case': 'dative',
               'gender': 'masculine',
               'number': 'singular',
               'construction': 'noun_dat_masc_sing_2decl',
               'tags': [1L, 82L, 117L]}
              ),
             # ('ἀληθεια', 'noun'),
             # ('ἰχθυς', 'noun'),
             # ('ταχεως', 'adverb')
             ])
    def test_add_new_wordform(self, wordform, mod_form, lemma, constraint,
                              out, db):
        """
        """
        f = PathFactory()
        actual, rowid, cst_id = f._add_new_wordform(wordform, lemma, mod_form,
                                                    constraint)
        # clean up db: value picked up by db fixture via introspection
        newrows = {'word_forms': 'rowid',
                   'constructions': 'cst_id'}
        assert actual == out['word_form']
        assert isinstance(rowid, (long, int))
        newrow = db.word_forms(rowid)
        myconstructions = db(db.constructions.construction_label ==
                             out['construction']).select()
        out['construction'] = myconstructions.first().id
        out['source_lemma'] = db.lemmas(db.lemmas.lemma == out['source_lemma']).id
        for k, v in out.iteritems():
            print 'testing', k
            assert newrow[k] == v

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('mod_form,lemma,constraints,out',
        [('ἀρτου',  # mod_form
          'ἀγορα',  # lemma
          None,  # constraints
          ('ἀγορας', None)  # out
          ),
         ('ἀρτοι',  # mod_form
          'ἀγορα',  # lemma
          'case@gen',  # constraints
          ('ἀγορων', None)  # out
          ),
         (None,  # modform
          'ἀγορα',  # lemma
          'case@gen_num@pl',  # constraints
          ('ἀγορων', None)  # out
          ),
         ])
    def test_make_form_agree(self, mod_form, lemma, constraints, out):
        """
        Test method for the PathFactory.format_strings() method.
        """
        f = PathFactory()
        wordform, newform = f.make_form_agree(mod_form, lemma,
                                              constraint=constraints)
        assert wordform == out[0]
        assert newform == out[1]

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('fieldstring,combodict,out',
        [('words2-words1',  # fieldstring
          {'words1': 'ἀρτου',  # combodict
           'words2': 'ἀγορα'},
          ('ἀγορας', None)  # out
          ),
         ('words2-words1-case@gen',
          {'words1': 'ἀρτοι',  # combodict
           'words2': 'ἀγορα'},
          ('ἀγορων', None)  # out
          ),
         ('ἀγορα-none-case@g_num@s',  # fieldstring
          {'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          ('ἀγορας', None)  # out
          ),
         ])
    def test_get_wordform(self, fieldstring, combodict, out):
        """
        Test method for the PathFactory.format_strings() method.
        """
        f = PathFactory()
        wordform, newform = f.get_wordform(fieldstring, combodict)
        assert wordform == out[0]
        assert newform == out[1]

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('combodict,temp,out',
        [({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'Can you get some {words1} from the {words2}.',  # temp
          ('Can you get some ἀρτος from the ἀγορα.',  # out
           [])
          ),
         ({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'Yes,\s(?P<a>I\s)?(?(a)|we\s)can\sget\ssome\s{words1}\sfrom\sthe'  # temp
          '\s{words2}.',
          ('Yes,\\s(?P<a>I\\s)?(?(a)|we\\s)can\\sget\\ssome\\s'  # out
           '\xe1\xbc\x80\xcf\x81\xcf\x84\xce\xbf\xcf\x82\\sfrom\\sthe\\s'
           '\xe1\xbc\x80\xce\xb3\xce\xbf\xcf\x81\xce\xb1.',
           [])
          ),
         ({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'Yes, I can get some {words1} from the {words2-words1-case@gen}.',  # temp
          ('Yes, I can get some ἀρτος from the ἀγορας.',  # out
           [])
          ),
         ])
    def test_do_substitution(self, combodict, temp, out):
        """
        Test method for the PathFactory.format_strings() method.
        """
        f = PathFactory()
        newstring, newforms = f.do_substitution(temp, combodict)
        assert newstring == out[0]
        assert newforms == out[1]

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('combodict,ptemps,xtemps,rtemps,stringsout',
        [({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          ['Can you get some {words1} from the {words2}.'],  # ptempts
          ['Yes,\s(?P<a>I\s)?(?(a)|we\s)can\sget\ssome\s{words1}\sfrom\sthe'  # xtempts
           '\s{words2}.'],
          ['Yes, I can get some {words1} from the {words2}.',  # rtemps
           'Yes, we can get some {words1} from the {words2}.'],
          {'prompts': ['Can you get some ἀρτος from the ἀγορα.'.decode('utf8')],
           'rxs': ['Yes,\\s(?P<a>I\\s)?(?(a)|we\\s)can\\sget\\ssome\\s'
                   '\xe1\xbc\x80\xcf\x81\xcf\x84\xce\xbf\xcf\x82\\s'
                   'from\\sthe\\s\xe1\xbc\x80\xce\xb3\xce\xbf\xcf\x81\xce\xb1.'],
           'rdbls': ['Yes, I can get some ἀρτος from the ἀγορα.'.decode('utf8'),
                     'Yes, we can get some ἀρτος from the ἀγορα.'.decode('utf8')],
           'newforms': []}
          ),
         ])
    def test_format_strings(self, combodict, ptemps, xtemps, rtemps, stringsout):
        """
        Test method for the PathFactory.format_strings() method.
        """
        f = PathFactory()
        prompts, rxs, rdbls, newforms = f.format_strings(combodict, ptemps,
                                                         xtemps, rtemps)
        assert prompts == stringsout['prompts']
        assert rxs == stringsout['rxs']
        assert rdbls == stringsout['rdbls']
        assert newforms == stringsout['newforms']

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('combodict,result,stepout',
        [({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'testing',  # result
          {'hints': [],  # stepout
           'instructions': [],
           'locations': [1],
           'npcs': [12, 6],
           'outcome1': 1.0,
           'outcome2': 0.0,
           'outcome3': 0.0,
           'prompt': u'Can you get some ἀρτος from the ἀγορα.',
           'readable_response': 'Yes, I can get some ἀρτος from the ἀγορα.|'
                                'Yes, we can get some ἀρτος from the '
                                'ἀγορα.'.decode('utf8'),
           'response1': 'Yes,\\s(?P<a>I\\s)?(?(a)|we\\s)can\\sget\\ssome\\s'
                        'ἀρτος\\sfrom\\sthe\\sἀγορα.',
           'response2': None,
           'response3': None,
           'tags': [2L],
           'tags_ahead': [1L],
           'tags_secondary': [4L, 36L, 48L, 82L, 117L],
           'widget_image': 116L,
           'widget_type': 4}),
         # ({'words1': 'καρπος',  # combodict
         # 'words2': 'πωλιον'},
         # 'testing',  # result
         # {}),  # stepout
         ])
    def test_make_step(self, combodict, result, stepout, mystepinfo):
        """
        Create one step with given data.

        Returns a 2-member tuple
        [0] stepresult      : A 2-member tuple consisting of a string[0]
                              indicating the result of the step-creation
                              attempt and a second member [1] which gives
                              the content of that attempt. This content can be
                              - a step id (if success)
                              - a dict of step field values (if testing)
                              - a list of duplicate steps (duplicates)
                              - an error traceback (if failure)
        [1] newfs           : A list of inflected word forms newly added to
                              db.word_forms in the course of step creation.
        """
        f = PathFactory()
        actual = f.make_step(combodict, mystepinfo[0])
        assert actual[0][0] == result
        assert actual[0][1] == stepout
        assert actual[1] == []

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('', [])
    def make_path(self):
        """
        """
        pass
