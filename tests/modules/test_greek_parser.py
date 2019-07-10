#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the modulename module

 Configuration and some fixtures
 the file tests/conftest.py
 run with python2.7 -m pytest -xvs applications/paideia/tests/modules/
    test_greek_parser.py

"""

import pytest
# import re
# from pprint import pprint
import datetime
from greek_parser import Parser, NounPhrase, Noun, Art, tokenize
# from plugin_utils import makeutf8
from paideia_utils import Uprinter


class TestParser():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('dictin,formout',
                             [({'source_lemma': 50,  # dictin
                                'gender': 'feminine',
                                'number': 'singular',
                                'grammatical_case': 'accusative'},
                               'την'  # formout
                               ),
                              ])
    def test_getform(self, dictin, formout, db):
        """
        """
        actual = Parser(None).getform(dictin)
        print('actual form is', actual)
        assert actual == formout

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('dictout,formin',
                             [({'source_lemma': 50,  # dictin
                                'gender': 'feminine',
                                'number': 'singular',
                                'grammatical_case': 'accusative',
                                'person': 'none',
                                'tense': 'none',
                                'voice': 'none',
                                'mood': 'none',
                                'declension': '1',
                                'construction': 153,
                                'id': 98,
                                'modified_on': datetime.datetime(2014, 6, 17,
                                                                 14, 41, 6),
                                'part_of_speech': 'article',
                                'tags': [],
                                'thematic_pattern': '',
                                'uuid': 'd59c8c40-1d60-4da1-afaf-7f145323d693',
                                'word_form': '\xcf\x84\xce\xb7\xce\xbd'
                                },
                               'την'  # formout
                               ),
                              ])
    def test_parseform(self, dictout, formin):
        """
        """
        actual = Parser(None).parseform(formin)
        print('actual output is', actual)
        for k, val in actual.items():
            assert dictout[k] == val

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('formin,pos,formout',
                             [('ἀδελφην',
                               'article',
                               'την'  # formout
                               ),
                              ])
    def test_find_agree(self, formin, formout, pos):
        """
        """
        actual = Parser(None).find_agree(formin, pos)
        print('actual form is', actual)
        assert actual == formout


class TestNoun():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'nominal,string,expected,matching',
        [(r'ἀρτον|λογον',  # nominal
          'Τον ἀρτον ὁ ἀνηρ πωλει.',  # string
          (False,
           {},
           {0: [('Τον', {'index': 0}),
                ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                ('ὁ', {'index': 2}),
                ('ἀνηρ', {'index': 3}),
                ('πωλει', {'index': 4})]
            }
           ),
          {0: {'index': 1, 'word': 'ἀρτον'}}  # matching
          ),
         (r'ἀρτον|λογον',  # nominal
          'ἀρτον',  # string
          (True,
           {0: [('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 0})]},
           {}
           ),
          {0: {'index': 0, 'word': 'ἀρτον'}}  # matching
          )
         ])
    def test_validate(self, nominal, string, expected, matching):
        """
        """
        tkns = tokenize(string)[0]
        print('tokens ------------------------------------')
        print(tkns)
        with Noun(nominal, 'top') as myNoun:
            avalid, afailed = myNoun.validate(tkns, [])
            # print 'valid leaves --------------------------'
            # print Uprinter().uprint(avalid)
            # print 'failed leaves -------------------------'
            # print Uprinter().uprint(afailed)
            assert avalid == expected[1]
            assert afailed == expected[2]
            assert myNoun.matching_words == matching

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'nominal,odin,validout,failedout,matching',
        [(r'ἀρτον|λογον',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {0: [('Τον', {'index': 0}),  # -----------------validout
               ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {},  # --------------------------------------------failedout
          {0: {'index': 1, 'word': 'ἀρτον'}}  # ------------matching
          ),
         (r'ἀρτον|ἀνηρ',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {0: [('Τον', {'index': 0}),  # -----------------validout
               ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})],
           1: [('Τον', {'index': 0}),
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'current': 0, 'pos': 'Noun', 'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {},  # --------------------------------------------failedout
          {0: {'index': 1, 'word': 'ἀρτον'},
           1: {'index': 3, 'word': 'ἀνηρ'}}  # ------------matching
          ),
         (r'οἰκος|ἀνδρος',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {},  # ---------------------------------------------validout
          {0: [('Τον', {'index': 0}),  # -------------------failedout
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {}  # ---------------------------------------------matching
          ),
         (r'ἀρτον|ἀνδρος',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})],
           1: [('Τον', {'pos': 'Art', 'index': 0}),
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {1: [('Τον', {'pos': 'Art', 'index': 0}),  # -------- validout
               ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]},
          {0: [('Τον', {'index': 0}),  # -------------------failedout
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {1: {'index': 1, 'word': 'ἀρτον'}}  # ------------matching
          ),
         ])
    def test_match_string(self, nominal, odin, validout, failedout, matching):
        """
        """
        with Noun(nominal, 'top') as myNoun:
            avalid, afailed = myNoun.match_string(odin, [])
            print('valid leaves --------------------------')
            print(Uprinter().uprint(avalid))
            print('failed leaves -------------------------')
            print(Uprinter().uprint(afailed))
            assert avalid == validout
            assert afailed == failedout
            if myNoun.matching_words:
                for k, v in myNoun.matching_words.items():
                    assert matching[k] == v
            else:
                assert myNoun.matching_words == matching


class TestNounPhrase():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
            'nominal,article,odin,validout,failedout,'
            'art_matching,noun_matching',
            [('ἀρτον',  # --------------------------------nominal
              'τον',  # ----------------------------------article
              {0: [('Τον', {'current': 0, 'pos': 'Art', 'index': 0}),  # odin
                   ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {0: [('Τον', {'current': 0,  # ---------validout
                            'pos': 'Art',
                            'index': 0,
                            'modifies': 1}),
                   ('ἀρτον', {'current': 0,
                              'pos': 'Noun',
                              'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              [],  # -------------------------------------------failedout
              {0: {'index': 0, 'word': 'Τον'}},   # ------------art_matching
              {0: {'index': 1, 'word': 'ἀρτον'}}  # ------------noun_matching
              ),
             ]
             )
    def test_test_order(self, nominal, article, odin, validout, failedout,
                        art_matching, noun_matching):
        """
        """
        art = Art(article)
        art.matching_words == art_matching
        noun = Noun(nominal)
        noun.matching_words == noun_matching
        with NounPhrase(None, art, noun, 'def', 'top') as myNP:
            avalid, afailed = myNP.test_order(odin, [])
            print('valid leaves --------------------------')
            print(Uprinter().uprint(avalid))
            print('failed leaves -------------------------')
            print(Uprinter().uprint(afailed))
            assert avalid == validout
            assert afailed == failedout

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'nominal,article,string,expected',
        [('ἀρτον',  # --------------------------------nominal
          'τον',  # ----------------------------------article
          'Τον ἀρτον ὁ ἀνηρ πωλει.',  # -------------string
          (False,
           [],
           [[('Τον', {'pos': 'Art',  # -------------------failedout
                      'modifies': 1,
                      'index': 0,
                      'current': 0}),
             ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
             ('ὁ', {'index': 2}),
             ('ἀνηρ', {'index': 3}),
             ('πωλει', {'index': 4})]]
           )
          ),
         ('ἀρτον',  # --------------------------------nominal
          'Τον',  # ----------------------------------article
          'Τον ἀρτον.',  # -------------string
          (True,
           [[('Τον', {'pos': 'Art',  # -------------------validout
                      'modifies': 1,
                      'index': 0,
                      'current': 0}),
             ('ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1})]
            ],
           []  # -------------------failedout
           )
          ),
         ('ἀρτον',  # --------------------------------nominal
          'τον',  # ----------------------------------article
          'Ἀρτον τον ὁ ἀνηρ πωλει.',  # -------------string
          (False,
           [],  # -------------------validout
           [[('Ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 0}),  # flout
             ('τον', {'current': 0, 'pos': 'Art', 'index': 1}),
             ('ὁ', {'index': 2}),
             ('ἀνηρ', {'index': 3}),
             ('πωλει', {'index': 4})]]
           )
          ),
         ])
    def test_validate(self, nominal, article, string, expected):
        """
        """
        tkns = tokenize(string)[0]
        with NounPhrase(None, Art(article), Noun(nominal), 'def', 'top') \
                as myNoun:
            avalid, afailed = myNoun.validate(tkns, [])
            # print 'actual result ------------------------'
            # print aresult
            # print 'valid leaves --------------------------'
            # print Uprinter().uprint(avalid)
            # print 'failed leaves -------------------------'
            # print Uprinter().uprint(afailed)
            assert avalid == expected[1]
            assert afailed == expected[2]


'''
    pattern = Clause(None,
                     Subject(None, Noun(r'ἀνηρ'), 'def'),
                     Verb(r'πωλει|ἀγοραζει'),
                     DirObject(None, Noun(r'ἀρτον'), 'def'),
                     'top')
'''
