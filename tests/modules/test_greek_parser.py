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
from greek_parser import NounPhrase, Noun, Art, tokenize
#from plugin_utils import makeutf8
from paideia_utils import Uprinter


class TestNoun():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,string,expected',
            [(ur'ἀρτον|λογον',  # nominal
              u'Τον ἀρτον ὁ ἀνηρ πωλει.',  # string
              (False,
               [],
               [[(u'Τον', {'index': 0}),
                 (u'ἀρτον', {'current': True, 'pos': 'Noun', 'index': 1}),
                 (u'ὁ', {'index': 2}),
                 (u'ἀνηρ', {'index': 3}),
                 (u'πωλει', {'index': 4})]]
               )
              ),
             (ur'ἀρτον|λογον',  # nominal
              u'ἀρτον',  # string
              (True,
               [[(u'ἀρτον', {'pos': 'Noun', 'index': 0})]],
               []
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
              [[(u'Τον', {'index': 0}),  # -----------------odin
                (u'ἀρτον', {'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]],
              [[(u'Τον', {'index': 0}),  # -----------------validout
                (u'ἀρτον', {'current': True, 'pos': 'Noun', 'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]],
              []  # --------------------------------------------failedout
              ),
             (ur'ἀρτον|ἀνηρ',  # ------------------------------nominal
              [[(u'Τον', {'index': 0}),  # -----------------odin
                (u'ἀρτον', {'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]],
              [[(u'Τον', {'index': 0}),  # -----------------validout
                (u'ἀρτον', {'current': True, 'pos': 'Noun', 'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})],
               [(u'Τον', {'index': 0}),
                (u'ἀρτον', {'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'current': True, 'pos': 'Noun', 'index': 3}),
                (u'πωλει', {'index': 4})]
               ],
              []  # --------------------------------------------failedout
              ),
             (ur'οἰκος|ἀνδρος',  # ------------------------------nominal
              [[(u'Τον', {'index': 0}),  # -----------------odin
               (u'ἀρτον', {'index': 1}),
               (u'ὁ', {'index': 2}),
               (u'ἀνηρ', {'index': 3}),
               (u'πωλει', {'index': 4})]],
              [],  # ---------------------------------------------validout
              [[(u'Τον', {'index': 0}),  # -------------------failedout
                (u'ἀρτον', {'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]]
              ),
             (ur'ἀρτον|ἀνδρος',  # ------------------------------nominal
              [[(u'Τον', {'index': 0}),  # -----------------odin
                (u'ἀρτον', {'pos': 'Noun', 'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})],
               [(u'Τον', {'pos': 'Art', 'index': 0}),
                (u'ἀρτον', {'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]
               ],
              [[(u'Τον', {'pos': 'Art', 'index': 0}),  # ------------------validout
                (u'ἀρτον', {'current': True, 'pos': 'Noun', 'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]],
              [[(u'Τον', {'index': 0}),  # -------------------failedout
                (u'ἀρτον', {'pos': 'Noun', 'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]]
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
              [[(u'Τον', {'current': True, 'pos': 'Art', 'index': 0}),  # -------------odin
                (u'ἀρτον', {'current': True, 'pos': 'Noun', 'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]],
              [[(u'Τον', {'current': True,  # ---------validout
                          'pos': 'Art',
                          'index': 0,
                          'modifies': 1}),
                (u'ἀρτον', {'current': True,
                            'pos': 'Noun',
                            'index': 1}),
                (u'ὁ', {'index': 2}),
                (u'ἀνηρ', {'index': 3}),
                (u'πωλει', {'index': 4})]],
              [],  # -------------------------------------------failedout
              ),
             ]
             )
    def test_test_order(self, nominal, article, odin, validout, failedout):
        """
        """
        with NounPhrase(None, Art(article), Noun(nominal), 'top') as myNP:
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
                           'index': 0}),
                 (u'ἀρτον', {'pos': 'Noun', 'index': 1}),
                 (u'ὁ', {'index': 2}),
                 (u'ἀνηρ', {'index': 3}),
                 (u'πωλει', {'index': 4})]]
               )
              ),
             ('ἀρτον',  # --------------------------------nominal
              'τον',  # ----------------------------------article
              'Τον ἀρτον.',  # -------------string
              (True,
               [[(u'Τον', {'pos': 'Art',  # -------------------validout
                           'modifies': 1,
                           'index': 0}),
                 (u'ἀρτον', {'pos': 'Noun', 'index': 1})]
                ],
               []  # -------------------failedout
               )
              ),
             ('ἀρτον',  # --------------------------------nominal
              'τον',  # ----------------------------------article
              'Ἀρτον τον ὁ ἀνηρ πωλει.',  # -------------string
              (False,
               [],  # -------------------validout
               [[(u'Ἀρτον', {'pos': 'Noun', 'index': 0}),  # --------failedout
                 (u'τον', {'pos': 'Art', 'index': 1}),
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
        with NounPhrase(None, Art(article), Noun(nominal), 'top') as myNoun:
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
