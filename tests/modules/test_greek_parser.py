#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the modulename module

 Configuration and some fixtures
 the file tests/conftest.py
 run with python2.7 -m pytest -xvs applications/paideia/tests/modules/test_greek_parser.py

"""

import pytest
#import re
#from pprint import pprint
import datetime
from greek_parser import Parser, NounPhrase, Noun, Art, tokenize
#from plugin_utils import makeutf8
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
        print 'actual form is', actual
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
                                'construction': 153L,
                                'id': 98L,
                                'modified_on': datetime.datetime(2014, 6, 17,
                                                                 14, 41, 6),
                                'part_of_speech': 'particle',
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
        print 'actual output is', actual
        assert actual == dictout

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
        print 'actual form is', actual
        assert actual == formout


class TestNoun():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,string,expected',
            [(ur'ἀρτον|λογον',  # nominal
              u'Τον ἀρτον ὁ ἀνηρ πωλει.',  # string
              (False,
               {},
               {0: [(u'Τον', {'index': 0}),
                     (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                     (u'ὁ', {'index': 2}),
                     (u'ἀνηρ', {'index': 3}),
                     (u'πωλει', {'index': 4})]
                }
               )
              ),
             (ur'ἀρτον|λογον',  # nominal
              u'ἀρτον',  # string
              (True,
               {0: [(u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 0})]},
               {}
               )
              )
             ])
    def test_validate(self, nominal, string, expected):
        """
        """
        tkns = tokenize(string)[0]
        print 'tokens ------------------------------------'
        print tkns
        with Noun(nominal, 'top') as myNoun:
            avalid, afailed = myNoun.validate(tkns, [])
            #print 'valid leaves --------------------------'
            #print Uprinter().uprint(avalid)
            #print 'failed leaves -------------------------'
            #print Uprinter().uprint(afailed)
            assert avalid == expected[1]
            assert afailed == expected[2]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,odin,validout,failedout',
            [(ur'ἀρτον|λογον',  # ------------------------------nominal
              {0: [(u'Τον', {'index': 0}),  # -----------------odin
                   (u'ἀρτον', {'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {0: [(u'Τον', {'index': 0}),  # -----------------validout
                   (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {}  # --------------------------------------------failedout
              ),
             (ur'ἀρτον|ἀνηρ',  # ------------------------------nominal
              {0: [(u'Τον', {'index': 0}),  # -----------------odin
                   (u'ἀρτον', {'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {0: [(u'Τον', {'index': 0}),  # -----------------validout
                   (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})],
               1: [(u'Τον', {'index': 0}),
                   (u'ἀρτον', {'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'current': 0, 'pos': 'Noun', 'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {}  # --------------------------------------------failedout
              ),
             (ur'οἰκος|ἀνδρος',  # ------------------------------nominal
              {0: [(u'Τον', {'index': 0}),  # -----------------odin
                   (u'ἀρτον', {'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {},  # ---------------------------------------------validout
              {0: [(u'Τον', {'index': 0}),  # -------------------failedout
                   (u'ἀρτον', {'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               }
              ),
             (ur'ἀρτον|ἀνδρος',  # ------------------------------nominal
              {0: [(u'Τον', {'index': 0}),  # -----------------odin
                   (u'ἀρτον', {'pos': 'Noun', 'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})],
               1: [(u'Τον', {'pos': 'Art', 'index': 0}),
                   (u'ἀρτον', {'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {1: [(u'Τον', {'pos': 'Art', 'index': 0}),  # ------------------validout
                   (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]},
              {0: [(u'Τον', {'index': 0}),  # -------------------failedout
                   (u'ἀρτον', {'pos': 'Noun', 'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               }
              ),
             ])
    def test_match_string(self, nominal, odin, validout, failedout):
        """
        """
        with Noun(nominal, 'top') as myNoun:
            avalid, afailed = myNoun.match_string(odin, [])
            print 'valid leaves --------------------------'
            print Uprinter().uprint(avalid)
            print 'failed leaves -------------------------'
            print Uprinter().uprint(afailed)
            assert avalid == validout
            assert afailed == failedout


class TestNounPhrase():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,article,odin,validout,failedout',
            [('ἀρτον',  # --------------------------------nominal
              'τον',  # ----------------------------------article
              {0: [(u'Τον', {'current': 0, 'pos': 'Art', 'index': 0}),  # -------------odin
                   (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              {0: [(u'Τον', {'current': 0,  # ---------validout
                             'pos': 'Art',
                             'index': 0,
                             'modifies': 1}),
                   (u'ἀρτον', {'current': 0,
                               'pos': 'Noun',
                               'index': 1}),
                   (u'ὁ', {'index': 2}),
                   (u'ἀνηρ', {'index': 3}),
                   (u'πωλει', {'index': 4})]
               },
              [],  # -------------------------------------------failedout
              ),
             ]
             )
    def test_test_order(self, nominal, article, odin, validout, failedout):
        """
        """
        with NounPhrase(None, Art(article), Noun(nominal), 'def', 'top') as myNP:
            avalid, afailed = myNP.test_order(odin, [])
            print 'valid leaves --------------------------'
            print Uprinter().uprint(avalid)
            print 'failed leaves -------------------------'
            print Uprinter().uprint(afailed)
            assert avalid == validout
            assert afailed == failedout

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,article,string,expected',
            [(u'ἀρτον',  # --------------------------------nominal
              u'τον',  # ----------------------------------article
              u'Τον ἀρτον ὁ ἀνηρ πωλει.',  # -------------string
              (False,
               [],
               [[(u'Τον', {'pos': 'Art',  # -------------------failedout
                           'modifies': 1,
                           'index': 0,
                           'current': 0}),
                 (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1}),
                 (u'ὁ', {'index': 2}),
                 (u'ἀνηρ', {'index': 3}),
                 (u'πωλει', {'index': 4})]]
               )
              ),
             ('ἀρτον',  # --------------------------------nominal
              'Τον',  # ----------------------------------article
              'Τον ἀρτον.',  # -------------string
              (True,
               [[(u'Τον', {'pos': 'Art',  # -------------------validout
                           'modifies': 1,
                           'index': 0,
                           'current': 0}),
                 (u'ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 1})]
                ],
               []  # -------------------failedout
               )
              ),
             ('ἀρτον',  # --------------------------------nominal
              'τον',  # ----------------------------------article
              'Ἀρτον τον ὁ ἀνηρ πωλει.',  # -------------string
              (False,
               [],  # -------------------validout
               [[(u'Ἀρτον', {'current': 0, 'pos': 'Noun', 'index': 0}),  # --------failedout
                 (u'τον', {'current': 0, 'pos': 'Art', 'index': 1}),
                 (u'ὁ', {'index': 2}),
                 (u'ἀνηρ', {'index': 3}),
                 (u'πωλει', {'index': 4})]]
               )
              ),
             ])
    def test_validate(self, nominal, article, string, expected):
        """
        """
        tkns = tokenize(string)[0]
        with NounPhrase(None, Art(article), Noun(nominal), 'def', 'top') as myNoun:
            avalid, afailed = myNoun.validate(tkns, [])
            #print 'actual result ------------------------'
            #print aresult
            #print 'valid leaves --------------------------'
            #print Uprinter().uprint(avalid)
            #print 'failed leaves -------------------------'
            #print Uprinter().uprint(afailed)
            assert avalid == expected[1]
            assert afailed == expected[2]


'''
    pattern = Clause(None,
                     Subject(None, Noun(r'ἀνηρ'), 'def'),
                     Verb(r'πωλει|ἀγοραζει'),
                     DirObject(None, Noun(r'ἀρτον'), 'def'),
                     'top')
'''
