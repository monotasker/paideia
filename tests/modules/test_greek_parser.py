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
import re
from pprint import pprint
from greek_parser import main, Clause, NounPhrase, Subject, Noun, Verb, DirObject, tokenize

class TestNoun():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('nominal,string,expected',
            [('ἀρτον',  # nominal
              'Τον ἀρτον ὁ ἀνηρ πωλει.',  # string
             ([OrderedDict([('τον', None),
                            ('ἀρτον', ['Noun']),
                            ('ὁ', None),
                            ('ἀνηρ', None),
                            ('πωλει', None)])
               ],
              [])
              ),
             ])
    def test_find_article(self, nominal, string, expected):
        """
        """
        tkns = tokenize(string)[0]
        actual = Noun('ἀρτον|λογον', ['top']).match_string([tkns], [])
        print actual
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
