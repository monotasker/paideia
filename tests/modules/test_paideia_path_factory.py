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
from paideia_path_factory import PathFactory, MorphParser, Inflector
from paideia_path_factory import WordFactory, StepFactory
from plugin_utils import makeutf8


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


class TestMorphParser():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordform,expected',
            [('ἀρτος', '2'),
             ('τεκνον', '2'),
             ('ἰχθυς', '3'),
             ('ἀληθεια', '1'),
             ('παις', '3'),
             ('πολις', '3'),
             ('γυνη', '1'),
             ('μητηρ', '3'),
             ('παιδισκη', '1'),
             ('ναυτης', '2'),
             ])
    def test_infer_declension(self, wordform, expected):
        """
        """
        f = MorphParser()
        actual = f.infer_declension(wordform)
        actual == expected

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('wordform,lemma,expected',
            [('ἀρτος', 'ἀρτος', 'nominative'),
             ('ἀρτου', 'ἀρτος', 'genitive'),
             ('ἀρτῳ', 'ἀρτος', 'dative'),
             ('ἀρτον', 'ἀρτος', 'accusative'),
             ('ἀρτοι', 'ἀρτος', 'nominative'),
             ('ἀρτων', 'ἀρτος', 'genitive'),
             ('ἀρτοις', 'ἀρτος', 'dative'),
             ('ἀρτους', 'ἀρτος', 'accusative'),
             ('γυνη', 'γυνη', 'nominative'),
             ('γυνης', 'γυνη', 'genitive'),
             ('γυνῃ',  'γυνη', 'dative'),
             ('γυνην', 'γυνη', 'accusative'),
             ('γυναι', 'γυνη', 'nominative'),
             ('γυνων', 'γυνη', 'genitive'),
             ('γυναις', 'γυνη', 'dative'),
             ('γυνας', 'γυνη', 'accusative'),
             ('τεκνον', 'τεκνον', ['nominative', 'accusative']),
             ('τεκνα', 'τεκνα', ['nominative', 'accusative']),
             ('πολις', 'πολις', 'nominative'),
             ('πολεως', 'πολις', 'genitive'),
             ('πολει',  'πολις', 'dative'),
             ('πολιν', 'πολις', 'accusative'),
             ('πολεις', 'πολις', ['nominative', 'accusative']),
             ('πολεων', 'πολις', 'genitive'),
             ('πολεσι', 'πολις', 'dative'),
             ])
    def test_infer_case(self, wordform, lemma, expected):
        """
        """
        f = MorphParser()
        actual = f.infer_declension(wordform, lemma)
        actual == expected

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordform,out',
            [('ἀρτος', 'noun'),
             ('λυω', 'verb'),
             ('ἀληθεια', 'noun'),
             ('ἰχθυς', 'noun'),
             ('ταχεως', 'adverb')
             ])
    def test_infer_part_of_speech(self, wordform, out):
        """
        """
        f = MorphParser()
        actual = f.infer_part_of_speech(wordform)
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
    def test_infer_parsing(self, wordform, lemma, out):
        """
        """
        f = MorphParser()
        actual = f.infer_parsing(wordform, lemma)
        assert actual == out


class TestInflector():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('mod_form,lemma,constraints,out',
        [('ἀρτου',  # mod_form
          'ἀγορα',  # lemma
          'g@f_pattern@atheme',  # constraints
          ('ἀγορας',  # FIXME: thematic alpha not caught here
           [('word_forms', 'ἀγορας', 549L, None)])  # out
          ),
         ('ἀρτοι',  # mod_form
          'ἀγορα',  # lemma
          'case@gen',  # constraints
          ('ἀγορων',
           [('word_forms', 'ἀγορων', 550L, None)])  # out
          ),
         (None,  # modform
          'ἀγορα',  # lemma
          'case@gen_num@pl',  # constraints
          ('ἀγορων',
           [('word_forms', 'ἀγορων', 551L, None)])  # out
          ),
         ('γυναικες',  # modform
          'βαινω',  # lemma
          'pers@3',  # constraints
          ('βαινουσι',
           [('word_forms', 'βαινουσι', 552L, None)])  # out
          ),
         (None,  # modform
          'βαινω',  # lemma
          'pers@1_num@pl_ts@pres_v@act_m@ind',  # constraints
          ('βαινομεν',
           [('word_forms', 'βαινομεν', 553L, None)])  # out
          ),
         ])
    def test_make_form_agree(self, mod_form, lemma, constraints, out, web2py):
        """
        Test method for the PathFactory.format_strings() method.
        """
        session = web2py.current.session
        session.results = []
        i = Inflector()
        newform = i.make_form_agree(mod_form, lemma, constraint=constraints,
                                    session=session)
        print 'newform', newform
        assert newform == out[0] or newform == makeutf8(out[0])
        for idx, r in enumerate(session.results):
            for idx2, i in enumerate(r):
                print r, i
                print idx, idx2
                myi = out[1][idx][idx2]
                assert i == myi or i == makeutf8(myi)
        # TODO: are forms being re-created when in db? why can some not be
        # created?

    @pytest.mark.skipif(True, reason='just because')
    @pytest.mark.parametrize('',
        [(),
         ])
    def test_wordform_from_parsing(self):
        """
        """
        i = Inflector()
        pass


class TestWordFactory():
    """
    Class for manipulating inflected Greek word forms.
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('fieldstring,combodict,out',
        [('words2-words1',  # fieldstring
          {'words1': 'ἀρτου',  # combodict
           'words2': 'ἀγορα'},
          ('ἀγορας', {'constructions': [None], 'word_forms': [552L]})  # out
          ),
         ('words2-words1-case@gen',
          {'words1': 'ἀρτοι',  # combodict
           'words2': 'ἀγορα'},
          ('ἀγορων', {'constructions': [None], 'word_forms': [553L]})  # out
          ),
         ('ἀγορα-none-case@g_num@s',  # fieldstring
          {'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          ('ἀγορας', {'constructions': [None], 'word_forms': [554L]})  # out
          ),
         ])
    def test_get_wordform(self, fieldstring, combodict, out):
        """
        Test method for the WordFactory.get_wordform() method.
        """
        f = WordFactory()
        wordform = f.get_wordform(fieldstring, combodict)
        assert wordform == out[0] or makeutf8(out[0])

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordform,mod_form,lemma,constraint,out',
            [('ἀρτος',
              None,
              'ἀρτος',
              'case@nom_g@m_num@s',
              ('word_forms',
               'ἀρτος',  # word_form
               0,  # rowid
               None,  # err
               ),
              ),
             ('ἀρτῳ',
              None,
              'ἀρτος',
              None,
              ('word_forms',
               'ἀρτῳ',  # word_form
               0,  # rowid
               None,  # err
               ),
              ),
             # ('ἀληθεια', 'noun'),
             # ('ἰχθυς', 'noun'),
             # ('ταχεως', 'adverb')
             ])
    def test_add_new_wordform(self, wordform, mod_form, lemma, constraint,
                              out, db):
        """
        """
        f = WordFactory()
        actual = f.add_new_wordform(wordform, lemma, mod_form, constraint)

        # test method return values
        for idx, a in enumerate(actual[0]):
            if idx != 2:  # don't try to predict new db row ids
                assert a == out[idx]
            else:
                assert isinstance(actual[0][2], (long, int))
        # TODO: re-introduce tests for db io
        # test db row content
        #newrow = db.word_forms(actual[1])
        #myconstructions = db(db.constructions.construction_label ==
                             #forminfo['construction']).select()
        #forminfo['construction'] = myconstructions.first().id
        #forminfo['source_lemma'] = db.lemmas(db.lemmas.lemma ==
                                             #forminfo['source_lemma']).id
        #for k, v in forminfo.iteritems():
            #print 'testing', k
            #assert newrow[k] == v

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('lemma,constraint,out,leminfo',
            [('ἀρτος',
              'pos@nn_case@nom_g@m_num@s_gl@bread|food_ft@vocabulary#-#food',
              ('ἀρτος'.decode('utf8'),  # lemma
               0,  # lemid
               None,  # err
               0,  # formid
               None,  # formerr
               None,  # cstid,
               None,  # csterr
               ),
              {'lemma': 'ἀρτος',
               'part_of_speech': 'noun',
               'glosses': ['bread', 'food'],
               'first_tag': 'vocabulary - food',
               'extra_tags': ['nominative 2', 'noun basics']}
              ),
             # ('ἀληθεια', 'noun'),
             # ('ἰχθυς', 'noun'),
             # ('ταχεως', 'adverb')
             ])
    def test_add_new_lemma(self, lemma, constraint, out, leminfo, db):
        """
        """
        f = WordFactory()
        actual = f.add_new_lemma(lemma, constraint)
        for idx, a in enumerate(actual):
            if idx not in [1, 3, 5]:  # don't try to predict new db row ids
                assert a == out[idx]
            else:
                assert isinstance(actual[1], (long, int))
        self.newrows = {'word_forms': actual[1]}  # for db teardown
        newrow = db.lemmas(actual[1])
        leminfo['first_tag'] = db.tags(db.tags.tag == leminfo['first_tag']).id
        leminfo['extra_tags'] = [db.tags(db.tags.tag == t).id
                                 for t in leminfo['extra_tags']]
        for k, v in leminfo.iteritems():
            print 'testing', k
            assert newrow[k] == v

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
        f = WordFactory()
        actual = f.parse_constraint(constraint)
        for k, v in actual.iteritems():
            assert v == out[k]
        assert not [k for k in out.keys() if k not in actual.keys()]


class TestStepFactory():
    """
    Class to create steps for the Paideia web-app. (Unit tests)
    """
    @pytest.mark.skipif(False, reason='just because')
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
        f = StepFactory()
        rowid, title, newrow = f._make_image(combodict, image_template)
        # clean up db
        if newrow:
            db(db.images.id == rowid).delete()
        assert isinstance(rowid, (long, int))
        assert title == out[0]
        assert newrow == out[1]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('combodict,temp,out',
        [({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'Can you get some {words1} from the {words2}.',  # temp
          'Can you get some ἀρτος from the ἀγορα.',  # out
          ),
         ({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'Yes,\s(?P<a>I\s)?(?(a)|we\s)can\sget\ssome\s{words1}\sfrom\sthe'  # temp
          '\s{words2}.',
          'Yes,\\s(?P<a>I\\s)?(?(a)|we\\s)can\\sget\\ssome\\s'  # out
          '\xe1\xbc\x80\xcf\x81\xcf\x84\xce\xbf\xcf\x82\\sfrom\\sthe\\s'
          '\xe1\xbc\x80\xce\xb3\xce\xbf\xcf\x81\xce\xb1.',
          ),
         ({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          'Yes, I can get some {words1} from the {words2-words1-case@gen}.',  # temp
          'Yes, I can get some ἀρτος from the ἀγορας.',  # out
          ),
         ])
    def test_do_substitution(self, combodict, temp, out):
        """
        Test method for the PathFactory.format_strings() method.
        """
        f = StepFactory()
        newstring = f._do_substitution(temp, combodict)
        assert newstring == out or makeutf8(out)

    @pytest.mark.skipif(False, reason='just because')
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
        f = StepFactory()
        prompts, rxs, rdbls = f._format_strings(combodict, ptemps,
                                                xtemps, rtemps)
        assert prompts == [p.encode('utf8') for p in stringsout['prompts']]
        assert rxs == stringsout['rxs']
        assert rdbls == [r.encode('utf8') for r in stringsout['rdbls']]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('combodict,result,content,newimg',
        [({'words1': 'ἀρτος',  # combodict
           'words2': 'ἀγορα'},
          612L,  # result
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
           'widget_image': 124L,
           'widget_type': 4},
          True),
         # ({'words1': 'καρπος',  # combodict
         # 'words2': 'πωλιον'},
         # 'testing',  # result
         # {}),  # stepout
         ])
    def test_make_step(self, combodict, result, content, newimg, mystepinfo):
        """
        Create one step with given data.

        Returns a 2-member tuple
        [0]
        a tuple consisting of a string[0] indicating the
        result of the step-creation attempt and a second member [1]
        which gives the content of that attempt. This content can be
            - a step id (if success)
            - a dict of step field values (if testing)
            - a list of duplicate steps (duplicates)
            - an error traceback (if failure)
        [1]
        also returns images_missing list
        """
        f = StepFactory()
        actual = f.make_step(combodict, mystepinfo[0], False)  # third arg is 'mock'
        assert actual[0][0] == result
        for k, v in actual[0][1].iteritems():
            assert v == content[k] or makeutf8(v) == content[k]
        assert actual[1] == newimg


class TestPathFactory():
    """
    Class to create paths for the Paideia web-app. (Unit tests)
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

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('wordlists,label_template,stepdata,avoid,testing,'
                             'pathid,steps,new_forms,images_missing',
        [([(u'ἀνθρωπος', u'Ἰασων'),  # wordlists
           (u'ἀνηρ', u'Σιμων'),
           (u'γυνη', u'Μαρια')
           ],
         'mypath {words1} {words2}',  # label_template
         [{'id': 4,
           'widget_type': 1,         # stepdata
           'prompt_template': [u'Τίς {words1} ἐν τῃ στοᾳ?',
                               u'Ἐν τῃ στοᾳ τίς {words1}?'],
           'response_template': '',
           'readable_template': '',
           'npcs': [2],
           'locs': [1],
           'image_template': '',
           'tags': [],
           'tags_secondary': [],
           'tags_ahead': []},
          {'id': 5,
           'widget_type': 1,         # stepdata
           'prompt_template': [u'Βλεπεις {words2} ἐν τῃ στοᾳ.',
                               u'Ἐν τῃ στοᾳ βλεπεις {words2}.'],
           'response_template': '',
           'readable_template': '',
           'npcs': [8],
           'locs': [7],
           'image_template': '',
           'tags': [],
           'tags_secondary': [],
           'tags_ahead': []},
          {'id': 6,
           'widget_type': 1,         # stepdata
           'prompt_template': [u'Τίς οὐν {words1} ἐν τῃ στοᾳ?',
                               u'Ἐν τῃ στοᾳ οὐν τίς {words1}?'],
           'response_template': u'(?P<a>Βλεπω\s){words2}(?(a):\sβλεπω).',
           'readable_template': [u'Βλεπω {words2}'.
                                 u'{words2} βλεπω.'],
           'npcs': [2],
           'locs': [1],
           'image_template': '',
           'tags': [],
           'tags_secondary': [],
           'tags_ahead': []}],
          '',  # avoid
          '',  # testing
          1L,  # 'path_id' (int)
          {},  # 'steps' (dict)
          {},  # 'new_forms' (dict)
          []  #'images_missing' (list)
          )
        ])
    def make_path(self, wordlists, label_template, stepsdata, avoid, testing,
                  pathid, steps, new_forms, images_missing):
        """
        """
        actual = PathFactory.make_path(wordlists,
                                       label_template=label_template,
                                       stepsdata=stepsdata,
                                       avoid=avoid,
                                       aligned=aligned,
                                       testing=testing)
        assert actual[0] == pathid
        for k, step in actual[1].iteritems():
            for s, v in step.iteritems():
                assert v == steps[k][s] or makeutf8(steps[k][s])
        assert actual[2] == new_forms
        assert actual[3] == images_missing

