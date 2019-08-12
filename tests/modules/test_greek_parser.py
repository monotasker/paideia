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
from greek_parser import Parser, NounPhrase, Noun, Art, Adj, tokenize


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
                             [([{'source_lemma': 50,  # dictout
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
                                 'uuid': 'd59c8c40-1d60-4da1-afaf-'
                                         '7f145323d693',
                                 'word_form': 'την'
                                 }],
                               'την'  # formin
                               ),
                              ([{'source_lemma': 42,  # dictout
                                 'gender': 'neuter',
                                 'number': 'singular',
                                 'grammatical_case': 'nominative',
                                 'person': 'none',
                                 'tense': 'none',
                                 'voice': 'none',
                                 'mood': 'none',
                                 'declension': '2',
                                 'construction': 12,
                                 'id': 849,
                                 'modified_on': datetime.datetime(2015, 5, 8,
                                                                  19, 29, 14),
                                 'part_of_speech': 'adjective',
                                 'tags': [],
                                 'thematic_pattern': '',
                                 'uuid': '65d2b869-6a5b-4272-a62f-'
                                         '67be60d0b0fc',
                                 'word_form': 'καλον'
                                 },
                                {'source_lemma': 42,  # dictout
                                 'gender': 'neuter',
                                 'number': 'singular',
                                 'grammatical_case': 'accusative',
                                 'person': 'none',
                                 'tense': 'none',
                                 'voice': 'none',
                                 'mood': 'none',
                                 'declension': '2',
                                 'construction': 13,
                                 'id': 1515,
                                 'modified_on': datetime.datetime(2015, 5, 8,
                                                                  19, 29, 14),
                                 'part_of_speech': 'adjective',
                                 'tags': [],
                                 'thematic_pattern': '',
                                 'uuid': '65d2b869-6a5b-4272-a62f-'
                                         '67be60d0b0fc',
                                 'word_form': 'καλον'
                                 },
                                {'source_lemma': 42,  # dictout
                                 'gender': 'neuter',
                                 'number': 'singular',
                                 'grammatical_case': 'vocative',
                                 'person': 'none',
                                 'tense': 'none',
                                 'voice': 'none',
                                 'mood': 'none',
                                 'declension': '2',
                                 'construction': 319,
                                 'id': 1516,
                                 'modified_on': datetime.datetime(2015, 5, 8,
                                                                  19, 29, 14),
                                 'part_of_speech': 'adjective',
                                 'tags': [],
                                 'thematic_pattern': '',
                                 'uuid': '65d2b869-6a5b-4272-a62f-'
                                         '67be60d0b0fc',
                                 'word_form': 'καλον'
                                 },
                                {'source_lemma': 42,  # dictout
                                 'gender': 'masculine',
                                 'number': 'singular',
                                 'grammatical_case': 'accusative',
                                 'person': 'none',
                                 'tense': 'none',
                                 'voice': 'none',
                                 'mood': 'none',
                                 'declension': '2',
                                 'construction': 19,
                                 'id': 1517,
                                 'modified_on': datetime.datetime(2015, 5, 8,
                                                                  19, 29, 14),
                                 'part_of_speech': 'adjective',
                                 'tags': [],
                                 'thematic_pattern': '',
                                 'uuid': '65d2b869-6a5b-4272-a62f-'
                                         '67be60d0b0fc',
                                 'word_form': 'καλον'
                                 }
                                ],
                               'καλον'  # formin
                               ),
                              ])
    def test_parseform(self, dictout, formin):
        """
        """
        actual = Parser(None).parseform(formin)
        print('actual output is', actual)
        for idx, p in enumerate(actual):
            for k, val in p.items():
                assert dictout[idx][k] == val

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
        print('looking for', pos, 'agreeing with', formin)
        print('expecting agreeing form', formout)
        print('actual agreeing form is', actual)
        assert actual == formout


class TestNoun():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'nominal,odin,validout,failedout,matching,conflicts',
        [(r'ἀρτον|λογον',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {0: [('Τον', {'index': 0}),  # -----------------validout
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {},  # --------------------------------------------failedout
          {0: [('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # ------------matching
          {}  # --------------------------------------------conflicts
          ),
         (r'ἀρτον|λογον',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3, 'pos': 'Noun'}),
               ('πωλει', {'index': 4})],
           1: [('Τον', {'index': 0}),
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4, 'pos': 'Verb'})]
           },
          {0: [('Τον', {'index': 0}),  # -----------------validout
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3, 'pos': 'Noun'}),
               ('πωλει', {'index': 4})],
           1: [('Τον', {'index': 0}),
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4, 'pos': 'Verb'})]
           },
          {},  # --------------------------------------------failedout
          {0: [('ἀρτον', {'index': 1, 'pos': 'Noun'})],
           1: [('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # ------------matching
          {}  # --------------------------------------------conflicts
          ),
         (r'ἀρτον|ἀνηρ',  # ------------------------------nominal
          {0: [('Τον', {'index': 0}),  # -----------------odin
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {0: [('Τον', {'index': 0}),  # -----------------validout
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})],
           1: [('Τον', {'index': 0}),
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'pos': 'Noun', 'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {},  # --------------------------------------------failedout
          {0: [('ἀρτον', {'index': 1, 'pos': 'Noun'})],
           1: [('ἀνηρ', {'index': 3, 'pos': 'Noun'})]}, # matching
          {}  # --------------------------------------------conflicts
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
          {}, # ---------------------------------------------matching
          {0: {'οἰκος|ἀνδρος_Noun': ('no match found',
                                     [['no match found']],
                                     'οἰκος|ἀνδρος',
                                     'Τον ἀρτον ὁ ἀνηρ πωλει')
               }
           }  # --------------------------------------------conflicts,
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
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]},
          {0: [('Τον', {'index': 0}),  # -------------------failedout
               ('ἀρτον', {'pos': 'Noun', 'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          {1: [('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # matching
          {0: {'ἀρτον|ἀνδρος_Noun': ('no match found', [['no match found']],
                                     'ἀρτον|ἀνδρος', 'Τον ἀρτον ὁ ἀνηρ πωλει')
               }
           }  # --------------------------------------------conflicts
          )  # fails: leaf 0 has already tagged the matching word
         ])
    def test_match_string(self, nominal, odin, validout, failedout, matching,
                          conflicts):
        """
        """
        with Noun(nominal, 'top') as myNoun:
            avalid, afailed, amatching, aconf = myNoun.match_string(odin, {})
            print('valid leaves --------------------------')
            print(avalid)
            print('failed leaves -------------------------')
            print(afailed)
            print('matching words -------------------------')
            print(amatching)
            print('conflicts -------------------------')
            print(aconf)
            assert avalid == validout
            assert afailed == failedout
            assert amatching == matching
            if myNoun.matching_words:
                print(myNoun.matching_words)
                for k, v in myNoun.matching_words.items():
                    assert matching[k] == v
            else:
                assert myNoun.matching_words == matching
            assert aconf == conflicts

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'nominal,string,tokens,expected,matching,conflicts',
        [(r'ἀρτον|λογον',  # nominal
          'Τον ἀρτον ὁ ἀνηρ πωλει.',  # string
          {0: [('Τον', {'index': 0}),  # tokens
               ('ἀρτον', {'index': 1}),
               ('ὁ', {'index': 2}),
               ('ἀνηρ', {'index': 3}),
               ('πωλει', {'index': 4})]
           },
          (False,
           {},
           {0: [('Τον', {'index': 0}),
                ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                ('ὁ', {'index': 2}),
                ('ἀνηρ', {'index': 3}),
                ('πωλει', {'index': 4})]
            }
           ),
          {0: [('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # matching
          {0: {'Τον_ὁ_ἀνηρ_πωλει': ('extra words present',
                                    [['extra words present']],
                                    [('Τον', {'index': 0}),
                                     ('ὁ', {'index': 2}),
                                     ('ἀνηρ', {'index': 3}),
                                     ('πωλει', {'index': 4})],
                                    [('Τον', {'index': 0}),
                                     ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                                     ('ὁ', {'index': 2}),
                                     ('ἀνηρ', {'index': 3}),
                                     ('πωλει', {'index': 4})]
                                    )
               }
           }  # conflicts
          ),  # fails: string includes other words and this is top-level structure
         (r'ἀρτον|λογον',  # nominal
          'ἀρτον',  # string
          {0: [('ἀρτον', {'index': 0})]},  # tokens
          (True,
           {0: [('ἀρτον', {'pos': 'Noun', 'index': 0})]},
           {}
           ),
          {0: [('ἀρτον', {'index': 0, 'pos': 'Noun'})]},  # matching
          {}  # conflicts
          )  # passes
         ])
    def test_validate(self, nominal, string, tokens, expected, matching, 
                      conflicts):
        """
        """
        tkns = tokenize(string)[0]
        assert tkns == tokens
        print('tokens ------------------------------------')
        print(tkns)
        with Noun(nominal, 'top') as myNoun:
            avalid, afailed, amatch, aconf = myNoun.validate(tkns, {})
            assert avalid == expected[1]
            assert afailed == expected[2]
            assert amatch == matching
            assert myNoun.matching_words == matching
            assert aconf == conflicts


class TestNounPhrase():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
            'nominal,article,adjective,odin,validout,failedout,match,matchout,'
            'conf',
            [('ἀρτον',  # --------------------------------nominal 0
              None,  # ----------------------------------article
              None,  # ----------------------------------adjective
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}),  # odin
                   ('ὁ', {'index': 1}),
                   ('ἀνηρ', {'index': 2}),
                   ('πωλει', {'index': 3})]
               },
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}),  # ---------validout
                   ('ὁ', {'index': 1}),
                   ('ἀνηρ', {'index': 2}),
                   ('πωλει', {'index': 3})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Ἀρτον', {'index': 0, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Ἀρτον', {'index': 0, 'pos': 'Noun'}),
                   ]},  # matchout
              {}  # conf
              ),  # no modifiers to agree
             ('ἀρτον',  # --------------------------------nominal 1
              None,  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Καλον', {'pos': 'Adj', 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {0: [('Καλον', {'pos': 'Adj', 'modifies': 1, 'index': 0}), # val
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Καλον', {'pos': 'Adj', 'index': 0}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Καλον', {'pos': 'Adj', 'modifies': 1, 'index': 0}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ]},  # matchout
              {}  # conf
              ),  # adjective but indefinite
             ('ἀρτον',  # --------------------------------nominal 2
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'modifies': 1,
                            'index': 0}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'modifies': 1, 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'index': 2, 'pos': 'Art'}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'index': 2, 'modifies': 1, 'pos': 'Art'}),
                   ]},  # matchout
              {}  # conf
              ),  # pass, even though too many articles without adjective
             ('ἀρτον',  # --------------------------------nominal 3
              'τον',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('καλον', {'pos': 'Adj', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'modifies': 1,
                            'index': 0}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('καλον', {'pos': 'Adj', 'index': 2}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ]},  # matchout
              {}  # conf
              ),  # agree despite predicate adj position (order not checked)
             ('ἀρτον',  # --------------------------------nominal 4
              'τον',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # odin
                   ('καλον', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'index': 0,
                            'modifies': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('καλον', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 2, 'pos': 'Art'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # matchout
              {}  # conf
              ),  # attributive adj position
             ('ἀρτον',  # --------------------------------nominal 5
              'τον',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'index': 2}),
                   ('καλον', {'pos': 'Adj', 'index': 3}),
                   ('ὁ', {'index': 4}),
                   ('ἀνηρ', {'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'index': 0,
                            'modifies': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'modifies': 1, 'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 3}),
                   ('ὁ', {'index': 4}),
                   ('ἀνηρ', {'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'pos': 'Art', 'index': 2}),
                   ('καλον', {'pos': 'Adj', 'index': 3}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'pos': 'Art', 'modifies': 1, 'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 3}),
                   ]},  # match
              {}  # conf
              ),  # second attributive adj position
             ('ἀρτον',  # --------------------------------nominal 6
              'την',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Την', {'pos': 'Art', 'index': 0}),  # odin
                   ('καλον', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------validout
              {0: [('Την', {'pos': 'Art',  # ---------failedout
                            'index': 0}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Την', {'index': 0, 'pos': 'Art'}),
                   ('καλον', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Την', {'index': 0, 'pos': 'Art'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # matchout
              {0: {'Την_0_Art': ('no agreement',
                                 [['gender']],
                                 ('Την', {'index': 0, 'pos': 'Art'}),
                                 ('ἀρτον', {'index': 2, 'pos': 'Noun'})
                                 )
                   }
               }  # conf
              ),  # attributive adj position (art conflicts)
             ('ἀρτον',  # --------------------------------nominal 7
              'τον',  # ----------------------------------article
              'καλαι',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # odin
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τον', {'pos': 'Art',  # ---------failedout
                            'modifies': 2,
                            'index': 0}),
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 2, 'pos': 'Art'}),
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # matchout
              {0: {'καλαι_1_Adj': ('no agreement',
                    [['grammatical_case', 'gender', 'number'],
                     ['grammatical_case', 'gender', 'number']],
                    ('καλαι', {'index': 1, 'pos': 'Adj'}),
                    ('ἀρτον', {'index': 2, 'pos': 'Noun'})
                    )
                   }
               }  # conf
              ),  # attributive adj position (adj conflicts)
             ('ἀρτον',  # --------------------------------nominal 8
              'τοις',  # ----------------------------------article
              'καλαι',  # --------------------------------adjective
              {0: [('Τοις', {'pos': 'Art', 'index': 0}),  # odin
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τοις', {'pos': 'Art',  # ---------failedout
                             'index': 0}),
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τοις', {'index': 0, 'pos': 'Art'}),
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Τοις', {'index': 0, 'pos': 'Art'}),
                   ('καλαι', {'pos': 'Adj', 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # matchout
              {0: {'Τοις_0_Art': ('no agreement',
                                  [['number', 'grammatical_case']],
                                  ('Τοις', {'index': 0, 'pos': 'Art'}),
                                  ('ἀρτον', {'index': 2, 'pos': 'Noun'})
                                  ),
                    'καλαι_1_Adj': ('no agreement',
                                    [['gender', 'number', 'grammatical_case'],
                                     ['gender', 'number', 'grammatical_case']],
                                    ('καλαι', {'index': 1, 'pos': 'Adj'}),
                                    ('ἀρτον', {'index': 2, 'pos': 'Noun'})
                                    )
                   }
               }  # conf
              ),  # attributive adj position (art conflicts)
             ('ἀρτον',  # --------------------------------nominal 9
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'index': 0,
                            'modifies': 1}),
                   ('ἀρτον', {'pos': 'Noun',
                              'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # matchout
              {}  # conf
              ),  # definite, no adjective
             ('ἀρτον',  # --------------------------------nominal 10
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'index': 0}),  # in
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'index': 0,
                            'modifies': 1}),
                   ('ἀρτον', {'pos': 'Noun',
                              'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'})]},  # matchout
              {}  # conf
              ),
             ]
             )
    def test_test_agreement(self, nominal, article, adjective, odin, validout,
                            failedout, match, matchout, conf):
        """
        """
        args = [Noun(nominal)]
        if adjective:
            args.append(Adj(adjective))
        if article:
            args.append('def')
        args.append('top')
        with NounPhrase(None, *args) as myNP:
            avalid, afailed, amatching, aconf = myNP.test_agreement(odin, {},
                                                                    match, {})
            print('valid leaves --------------------------')
            print(avalid)
            print('failed leaves -------------------------')
            print(afailed)
            print('conflicts -----------------------------')
            print(aconf)
            assert avalid == validout
            assert afailed == failedout
            assert amatching == matchout
            for k, val in aconf.items():
                for idx, c in val.items():
                    for x, i in enumerate(c):
                        if isinstance(i, list):
                            for myindex, l in enumerate(i):
                                assert sorted(l) == sorted(conf[k][idx][x][myindex])
                        else:
                            assert i == conf[k][idx][x]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
            'nominal,article,adjective,odin,validout,failedout,match,matchout,'
            'conf',
            [
             ('ἀρτον',  # --------------------------------nominal 0
              None,  # ----------------------------------article
              None,  # ----------------------------------adjective
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}),  # odin
                   ('ὁ', {'index': 1}),
                   ('ἀνηρ', {'index': 2}),
                   ('πωλει', {'index': 3})]
               },
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}),  # ---------validout
                   ('ὁ', {'index': 1}),
                   ('ἀνηρ', {'index': 2}),
                   ('πωλει', {'index': 3})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Ἀρτον', {'index': 0, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Ἀρτον', {'index': 0, 'pos': 'Noun'}),
                   ]},  # matchout
              {}  # conf
              ),  # no modifiers to order
             ('ἀρτον',  # --------------------------------nominal 1
              None,  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Καλον', {'pos': 'Adj', 'modifies': 1, 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {0: [('Καλον', {'pos': 'Adj', 'modifies': 1, 'index': 0}), # val
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Καλον', {'pos': 'Adj', 'modifies': 1, 'index': 0}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Καλον', {'pos': 'Adj', 'modifies': 1, 'index': 0}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ]},  # matchout
              {}  # conf
              ),  # adjective but indefinite
             ('ἀρτον',  # --------------------------------nominal 2
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'modifies': 1, 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τον', {'pos': 'Art',  # ---------failedout
                            'modifies': 1,
                            'index': 0}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'modifies': 1, 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'index': 2, 'modifies': 1, 'pos': 'Art'}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'index': 2, 'modifies': 1, 'pos': 'Art'}),
                   ]},  # matchout
              {0: {'τον_2_Art': ('out of order', 
                                 [['article follows its modified Noun']],
                                 ('τον', {'index': 2, 'modifies': 1,
                                  'pos': 'Art'}),
                                 ('ἀρτον', {'index': 1, 'pos': 'Noun'})
                                 )
                   }
               }  # conf
              ),  # fail because too many articles without adjective
             ('ἀρτον',  # --------------------------------nominal 3
              'τον',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τον', {'pos': 'Art',  # ---------failedout
                            'modifies': 1,
                            'index': 0}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ]},  # matchout
              {0: {'καλον_2_Adj': ('out of order', 
                                   [['adjective not in attributive position 1']
                                    ],
                                   ('καλον', {'index': 2, 'modifies': 1,
                                              'pos': 'Adj'}),
                                   [('Τον', {'index': 0, 'modifies': 1,
                                     'pos': 'Art'}),
                                   ('ἀρτον', {'index': 1, 'pos': 'Noun'})]
                                   )
                   }
               }  # conf
              ),  # fail because of predicate adj position 
             ('ἀρτον',  # --------------------------------nominal 4
              'τον',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 2, 'index': 0}),  # odin
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'index': 0,
                            'modifies': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 2}),
                   ('ὁ', {'index': 3}),
                   ('ἀνηρ', {'index': 4}),
                   ('πωλει', {'index': 5})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'modifies': 2, 'pos': 'Art'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 2, 'pos': 'Art'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 2, 'index': 1}),
                   ('ἀρτον', {'index': 2, 'pos': 'Noun'}),
                   ]},  # matchout
              {}  # conf
              ),  # attributive adj position
             ('ἀρτον',  # --------------------------------nominal 5
              'τον',  # ----------------------------------article
              'καλον',  # --------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),  # odin
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 3,
                            'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 3}),
                   ('ὁ', {'index': 4}),
                   ('ἀνηρ', {'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {0: [('Τον', {'pos': 'Art',  # ---------validout
                            'index': 0,
                            'modifies': 1}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 3,
                            'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 3}),
                   ('ὁ', {'index': 4}),
                   ('ἀνηρ', {'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {},  # -------------------------------------------failedout
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 3,
                            'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 3}),
                   ]},  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 3,
                    'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 3}),
                   ]},  # match
              {}  # conf
              ),  # second attributive adj position
             ('ἀρτον',  # --------------------------------nominal 6
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}),  # odin
                   ('τον', {'pos': 'Art', 'modifies': 0, 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {}, # ---------------------------------------------validout
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}), # ----failedout
                   ('τον', {'pos': 'Art', 'modifies': 0, 'index': 1}),
                   ('ὁ', {'index': 2}),
                   ('ἀνηρ', {'index': 3}),
                   ('πωλει', {'index': 4})]
               },  
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}), 
                   ('τον', {'pos': 'Art', 'modifies': 0, 'index': 1})
                   ]},  # match
              {0: [('Ἀρτον', {'pos': 'Noun', 'index': 0}), 
                   ('τον', {'pos': 'Art', 'modifies': 0, 'index': 1})
                   ]},  # matchout
              {0: {'τον_1_Art': ('out of order', 
                                   [['article follows its modified Noun']],
                                   ('τον', {'pos': 'Art', 'modifies': 0,
                                            'index': 1}),
                                   ('Ἀρτον', {'pos': 'Noun', 'index': 0})
                                   )
                   }
               }  # conf
              ),  # definite, no adjective
             ('ἀρτον',  # --------------------------------nominal 7
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),  # in
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 2,
                            'index': 3}),
                   ('ὁ', {'index': 4}),
                   ('ἀνηρ', {'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τον', {'pos': 'Art',  # ---------failedout
                            'index': 0,
                            'modifies': 1}),
                   ('ἀρτον', {'pos': 'Noun',
                              'index': 1}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 2,
                            'index': 3}),
                   ('ὁ', {'index': 4}),
                   ('ἀνηρ', {'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 2, 'index': 3})]
                   },  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 2}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 2,
                            'index': 3})]
                   },  # matchout
              {0: {'τον_3_Art': ('out of order', 
                                   [['article follows its modified Adj']],
                                   ('τον', {'pos': 'Art', 'modifies': 2, 'antecedent': 1, 'index': 3}),
                                   ('καλον', {'pos': 'Adj', 'modifies': 1,
                                              'index': 2})
                                   ),
                   'καλον_2_Adj': ('out of order', 
                                   [['adjective not in attributive position 2']
                                    ],
                                   ('καλον', {'pos': 'Adj', 'modifies': 1,
                                              'index': 2}),
                                   [('Τον', {'index': 0, 'modifies': 1, 'pos':
                                             'Art'}),
                                    ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                                    ('τον', {'pos': 'Art', 'antecedent': 1,
                                             'modifies': 2, 'index': 3})]
                                   )
                   }
               }  # conf
              ),  # second article following attributive adjective
             ('ἀρτον',  # --------------------------------nominal 8
              'τον',  # ----------------------------------article
              None,  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 3, 'index': 0}),  # in
                   ('ὁ', {'index': 1}),
                   ('ἀνηρ', {'index': 2}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τον', {'pos': 'Art',  # ---------failedout
                            'modifies': 3, 'index': 0}),
                   ('ὁ', {'index': 1}),
                   ('ἀνηρ', {'index': 2}),
                   ('ἀρτον', {'pos': 'Noun', 'index': 3}),
                   ('πωλει', {'index': 4})]
               },
              {0: [('Τον', {'index': 0, 'modifies': 3, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 3, 'pos': 'Noun'})]
                   },  # match
              {0: [('Τον', {'index': 0, 'modifies': 3, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 3, 'pos': 'Noun'})]
                   },  # matchout
              {0: {'ὁ-ἀνηρ_1-2': ('out of order', 
                                   [['extra words between article and '
                                     'modified Noun']],
                                   [('ὁ', {'index': 1}),
                                    ('ἀνηρ', {'index': 2})],
                                   [('Τον', {'pos': 'Art', 'modifies': 3,
                                     'index': 0}),
                                    ('ἀρτον', {'pos': 'Noun', 'index': 3})]
                                   )
                   }
               }  # conf
              ),  # fail: non-phrase words between article and its noun
             ('ἀρτον',  # --------------------------------nominal 9
              'τον',  # ----------------------------------article
              'καλον',  # -----------------------------------adjective
              {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),  # in
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 5,
                            'index': 2}),
                   ('ὁ', {'index': 3, 'pos': 'Art'}),
                   ('ἀνηρ', {'index': 4}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {},  # -------------------------------------------validout
              {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),  # fout
                   ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 5,
                            'index': 2}),
                   ('ὁ', {'index': 3, 'pos': 'Art'}),
                   ('ἀνηρ', {'index': 4}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 5}),
                   ('πωλει', {'index': 6})]
               },
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 5,
                            'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 5})
                   ]
               },  # match
              {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                   ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                   ('τον', {'pos': 'Art', 'antecedent': 1, 'modifies': 5,
                            'index': 2}),
                   ('καλον', {'pos': 'Adj', 'modifies': 1, 'index': 5})
                   ]
               },  # matchout
              {0: {'ὁ-ἀνηρ_3-4': ('out of order',
                                  [['extra words between article and modified '
                                    'Adj']],
                                  [('ὁ', {'index': 3, 'pos': 'Art'}),
                                   ('ἀνηρ', {'index': 4})],
                                  [('τον', {'pos': 'Art', 'modifies': 5,
                                    'antecedent': 1, 'index': 2}),
                                   ('καλον', {'pos': 'Adj', 'modifies': 1,
                                    'index': 5})],
                                  )
                   }
               }  # conf
              ),  # extra words between attributive2 adj and its article
             ]
             )
    def test_test_order(self, nominal, article, adjective, odin, validout,
                        failedout, match, matchout, conf):
        """
        """
        args = [Noun(nominal)]
        if adjective:
            args.append(Adj(adjective))
        if article:
            args.append('def')
        args.append('top')
        with NounPhrase(None, *args) as myNP:
            avalid, afailed, amatching, aconf = myNP.test_order(odin, {}, match, {})
            print('valid leaves --------------------------')
            print(avalid)
            print('failed leaves -------------------------')
            print(afailed)
            print('matching words-------------------------')
            print(amatching)
            print('conflicts------------------------------')
            print(aconf)
            assert avalid == validout
            assert afailed == failedout
            assert amatching == matchout
            for k, val in aconf.items():
                for idx, c in val.items():
                    for x, i in enumerate(c):
                        if isinstance(i, list) and isinstance(i[0], str):
                            for myindex, l in enumerate(i):
                              # print(l)
                              # print(conf[k][idx][x][myindex])
                              assert sorted(l) == sorted(
                                   conf[k][idx][x][myindex])
                        else:
                            assert i == conf[k][idx][x]

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize(
        'nominal,article,adjective,top,string,expected',
        [('ἀρτον',  # --------------------------------nominal
          'τον',  # ----------------------------------article
          None,  # -----------------------------------adjective
          True,  # -----------------------------------top
          'Τον ἀρτον ὁ ἀνηρ πωλει.',  # -------------string
          (False,
           {},  # -------------------------------------validout
           {0: [('Τον', {'pos': 'Art',  # -------------------failedout
                         'modifies': 1,
                         'index': 0,
                         }),
                ('ἀρτον', {'pos': 'Noun', 'index': 1}),
                ('ὁ', {'index': 2}),
                ('ἀνηρ', {'index': 3}),
                ('πωλει', {'index': 4})],
            2: [('Τον', {'index': 0}),
                ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                ('ὁ', {'index': 2, 'pos': 'Art'}),
                ('ἀνηρ', {'index': 3}),
                ('πωλει', {'index': 4})]
            },
           {0: [('Τον', {'index': 0, 'modifies': 1, 'pos': 'Art'}),
                ('ἀρτον', {'index': 1, 'pos': 'Noun'})],
            2: [('ὁ', {'index': 2, 'pos': 'Art'}),
                ('ἀρτον', {'index': 1, 'pos': 'Noun'})]
            },  # match
           {0: {'ὁ_ἀνηρ_πωλει': ('extra words present',
                                 [['extra words present']],
                                 [('ὁ', {'index': 2}),
                                  ('ἀνηρ', {'index': 3}),
                                  ('πωλει', {'index': 4})],
                                 [('Τον', {'index': 0, 'modifies': 1,
                                           'pos': 'Art'}),
                                  ('ἀρτον', {'index': 1, 'pos': 'Noun'}),
                                  ('ὁ', {'index': 2}),
                                  ('ἀνηρ', {'index': 3}),
                                  ('πωλει', {'index': 4})])},
            2: {'ὁ_2_Art': ('no agreement',
                            [['grammatical_case']],
                            ('ὁ', {'index': 2, 'pos': 'Art'}),
                            ('ἀρτον', {'index': 1, 'pos': 'Noun'}))}
            }  # conf
           )  # fails because extra words and top
          ),
         ('ἀρτον',  # --------------------------------nominal
          'Τον',  # ----------------------------------article
          None,  # -----------------------------------adjective
          True,  # -----------------------------------top
          'Τον ἀρτον.',  # -------------string
          (True,
           {0: [('Τον', {'pos': 'Art',  # -------------------validout
                         'modifies': 1,
                         'index': 0}),
                ('ἀρτον', {'pos': 'Noun', 'index': 1})]
            },
           {},  # -------------------failedout
           {0: [('Τον', {'pos': 'Art', 'modifies': 1, 'index': 0}),
                ('ἀρτον', {'pos': 'Noun', 'index': 1})]
            },   # match
           {}   # conf
           )  # passes
          ),
         ('ἀρτον',  # --------------------------------nominal
          'τον',  # ----------------------------------article
          None,  # -----------------------------------adjective
          False,  # -----------------------------------top
          'Ἀρτον τον ὁ ἀνηρ πωλει.',  # -------------string
          (False,
           {},  # -------------------validout
           {0: [('Ἀρτον', {'index': 0, 'pos': 'Noun'}),  # flout
                ('τον', {'index': 1, 'modifies': 0, 'pos': 'Art'}),
                ('ὁ', {'index': 2}),
                ('ἀνηρ', {'index': 3}),
                ('πωλει', {'index': 4})],
            3: [('Ἀρτον', {'index': 0, 'pos': 'Noun'}),
                ('τον', {'index': 1}),
                ('ὁ', {'index': 2, 'pos': 'Art'}),
                ('ἀνηρ', {'index': 3}),
                ('πωλει', {'index': 4})]},
           {0: [('τον', {'index': 1, 'modifies': 0, 'pos': 'Art'}),
                ('Ἀρτον', {'index': 0, 'pos': 'Noun'})],
            3: [('ὁ', {'index': 2, 'pos': 'Art'}),
                ('Ἀρτον', {'index': 0, 'pos': 'Noun'})]
           },  # -----------------------------------match
           {0: {'τον_1_Art': ('out of order',
                              [['article follows its modified Noun']],
                               ('τον', {'index': 1, 'modifies': 0,
                                        'pos': 'Art'}),
                               ('Ἀρτον', {'index': 0, 'pos': 'Noun'}))},
            3: {'ὁ_2_Art': ('no agreement',
                            [['grammatical_case']],
                            ('ὁ', {'index': 2, 'pos': 'Art'}),
                            ('Ἀρτον', {'index': 0, 'pos': 'Noun'}))}
            }  # ------------------------------------conf
           )  # fails because of article order
          ),
         ])
    def test_validate(self, nominal, article, adjective, top, string, expected):
        """
        """
        args = [Noun(nominal)]
        if adjective:
            args.append(Adj(adjective))
        if article:
            args.append('def')
        if top:
            args.append('top')
        tkns = tokenize(string)[0]
        with NounPhrase(None, *args) as myNoun:
            avalid, afailed, amatch, aconf = myNoun.validate(tkns, [])
            assert avalid == expected[1]
            assert afailed == expected[2]
            assert amatch == expected[3]
            assert aconf == expected[4]


'''
    pattern = Clause(None,
                     Subject(None, Noun(r'ἀνηρ'), 'def'),
                     Verb(r'πωλει|ἀγοραζει'),
                     DirObject(None, Noun(r'ἀρτον'), 'def'),
                     'top')
'''
