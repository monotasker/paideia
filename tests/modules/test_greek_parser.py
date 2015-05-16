#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the modulename module

 Configuration and some fixtures
 the file tests/conftest.py
 run with py.test -xvs path/to/tests/dir

"""

import pytest
from collections import OrderedDict
#import re
from pprint import pprint
from greek_parser import NounPhrase, Noun, tokenize
#from plugin_utils import makeutf8
from paideia_utils import Uprinter


class TestNoun():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,string,expected',
            [(ur'ἀρτον|λογον',  # nominal
              u'Τον ἀρτον ὁ ἀνηρ πωλει.',  # string
             (False, [], [OrderedDict([(u'τον', None),
                                       (u'ἀρτον', ['Noun']),
                                       (u'ὁ', None),
                                       (u'ἀνηρ', None),
                                       (u'πωλει', None)])
               ],
              [])
              ),
             ])
    def test_validate(self, nominal, string, expected):
        """
        """
        tkns = tokenize(string)[0]
        aresult, avalid, afailed = Noun(nominal, ['top']).validate(tkns)
        print 'actual result ------------------------'
        print aresult
        print 'valid leaves --------------------------'
        print Uprinter().uprint(avalid)
        print 'failed leaves -------------------------'
        print Uprinter().uprint(afailed)
        print type(afailed[0])
        assert actual == expected


class TestNounPhrase():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,string,expected',
            [('ἀρτον', 'Τον ἀρτον ὁ ἀνηρ πωλει.', 'pass'),
             ])
    def test_find_article(self, nominal, string, expected):
        """
        """
        tkns = tokenize(string)[0]
        actual = NounPhrase([tkns]).find_article()


'''
@pytest.mark.skipif(False, reason='just because')
@pytest.mark.parametrize('string,expected',
        [('Τον ἀρτον ὁ ἀνηρ πωλει.', 'pass'),
         ('Ὁ ἀνηρ πωλει τον ἀρτον.', 'pass'),
         ('Πωλει τον ἀρτον ὁ ἀνηρ.', 'pass'),
         ('τον πωλει ὁ ἀρτον ἀνηρ.', 'fail'),
         ('ὁ ἀρτον πωλει τον ἀνηρ.', 'fail'),
         ('ὁ τον ἀρτον πωλει ἀνηρ.', 'fail'),
         ('ὁ πωλει τον ἀρτον ἀνηρ.', 'fail')
         ])
def test_main(string, expected):
    """
    """
    pattern = Clause(None,
                     Subject(None, Noun(r'ἀνηρ'), 'def'),
                     Verb(r'πωλει|ἀγοραζει'),
                     DirObject(None, Noun(r'ἀρτον'), 'def'),
                     'top')
    actual = main(string, pattern)
    assert actual == expected
'''
