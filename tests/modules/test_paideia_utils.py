#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the paideia_utils module

 Configuration and some fixtures
 the file tests/conftest.py
 run with py.test -xvs path/to/tests/dir

"""

import pytest
from paideia_utils import normalize_accents


@pytest.mark.skipif(False, reason='just because')
@pytest.mark.parametrize('string_in,string_out',
                            [('ἄγαπὴ', 'ἀγαπη'),  # handle multiple accents
                             ('“ἀγαπη”', '"ἀγαπη"'),  # handle curly quotes
                             ('‘ἀγαπη’', "'ἀγαπη'"),
                             (u'ἀγάπη', 'ἀγαπη'),  # handle unicode input
                             ('τίνος', 'τίνος'),  # words to be *kept* accented
                             ('τί', 'τί'),
                             ('τίς', 'τίς'),
                             ('τίνα', 'τίνα'),
                             ('τίνας', 'τίνας'),
                             ('τίνι', 'τίνι'),
                             ('Τίνος', 'Τίνος'),
                             ('Τί', 'Τί'),
                             ('Τίς', 'Τίς'),
                             ('Τίνα', 'Τίνα'),
                             ('Τίνας', 'Τίνας'),
                             ('Τίνι', 'Τίνι'),
                             ('τίς', 'τίς'),  # handle q-iota on windows
                             ('ἀγάπη', 'ἀγαπη'),  # alpha
                             ('ἀγὰπη', 'ἀγαπη'),
                             ('ἀγᾶπη', 'ἀγαπη'),
                             ('ἄν', 'ἀν'),  # alpha with smooth breathing
                             ('ἂν', 'ἀν'),
                             ('ἆν', 'ἀν'),
                             ('ἅν', 'ἁν'),  # alpha with rough breathing
                             ('ἃν', 'ἁν'),
                             ('ἇν', 'ἁν'),
                             ('πᾷν', 'πᾳν'),  # alpha with iota subscript
                             ('πᾲν', 'πᾳν'),
                             ('πᾴν', 'πᾳν'),
                             ('ᾄν', 'ᾀν'),  # alpha with iota subscript & smooth
                             ('ᾂν', 'ᾀν'),
                             ('ᾆν', 'ᾀν'),
                             ('ᾅν', 'ᾁν'),  # alpha with iota subscript & rough
                             ('ᾃν', 'ᾁν'),
                             ('ᾇν', 'ᾁν'),
                             ('πέν', 'πεν'),  # epsilon
                             ('πὲν', 'πεν'),
                             ('ἒν', 'ἐν'),  # epsilon with smooth
                             ('ἔν', 'ἐν'),
                             ('ἕν', 'ἑν'),  # epsilon with rough
                             ('ἓν', 'ἑν'),
                             ('πῆν', 'πην'),  # eta
                             ('πήν', 'πην'),
                             ('πὴν', 'πην'),
                             ('ἤν', 'ἠν'),  # eta with smooth
                             ('ἢν', 'ἠν'),
                             ('ἦν', 'ἠν'),
                             ('ἥν', 'ἡν'),  # eta with rough
                             ('ἣν', 'ἡν'),
                             ('ἧν', 'ἡν'),
                             ('πῇν', 'πῃν'),  # eta with iota subscript
                             ('πῄν', 'πῃν'),
                             ('πῂν', 'πῃν'),
                             ("ᾕν", "ᾑν"),  # eta with subsc and rough
                             ("ᾓν", "ᾑν"),
                             ("ᾗν", "ᾑν"),
                             ("ᾔν", "ᾐν"),  # eta with subsc and smooth
                             ("ᾒν", "ᾐν"),
                             ("ᾖν", "ᾐν"),
                             ("όν", "ον"),  # omicron
                             ("ὸν", "ον"),
                             ("ὅν", "ὁν"),  # omicron with rough
                             ("ὃν", "ὁν"),
                             ("ὄν", "ὀν"),  # omicron with smooth
                             ("ὂν", "ὀν"),
                             ("ῖν", "ιν"),  # iota
                             ("ϊν", "ιν"),
                             ("ίν", "ιν"),
                             ("ὶν", "ιν"),
                             ("ίν", "ιν"),
                             ("ἵν", "ἱν"),  # iota with rough
                             ("ἳν", "ἱν"),
                             ("ἷν", "ἱν"),
                             ("ἴν", "ἰν"),  # iota with smooth
                             ("ἲν", "ἰν"),
                             ("ἶν", "ἰν"),
                             ("ῦν", "υν"),  # upsilon
                             ("ϋν", "υν"),
                             ("ύν", "υν"),
                             ("ὺν", "υν"),
                             ("ὕν", "ὑν"),  # upsilon with rough
                             ("ὓν", "ὑν"),
                             ("ὗν", "ὑν"),
                             ("ὔν", "ὐν"),  # upsilon with smooth
                             ("ὒν", "ὐν"),
                             ("ὖν", "ὐν"),
                             ("ῶν", "ων"),  # omega
                             ("ών", "ων"),
                             ("ὼν", "ων"),
                             ("ὥν", "ὡν"),  # omega with rough
                             ("ὣν", "ὡν"),
                             ("ὧν", "ὡν"),
                             ("ὤν", "ὠν"),  # omega with smooth
                             ("ὢν", "ὠν"),
                             ("ὦν", "ὠν"),
                             ("ῷν", "ῳν"),  # omega with subsc
                             ("ῴν", "ῳν"),
                             ("ῲν", "ῳν"),
                             ("ᾥν", "ᾡν"),  # omega with subsc and rough
                             ("ᾣν", "ᾡν"),
                             ("ᾧν", "ᾡν"),
                             ("ᾤν", "ᾠν"),  # omega with subsc and smooth
                             ("ᾢν", "ᾠν"),
                             ("ᾦν", "ᾠν"),
                             ("῾Ων", "Ὡν"),  # improperly formed rough with caps
                             ("῾Ρν", "Ῥν"),
                             ("῾Υν", "Ὑν"),
                             ("῾Αν", "Ἁν"),
                             ("῾Ον", "Ὁν"),
                             ("῾Εν", "Ἑν"),
                             ("῾Ιν", "Ἱν"),
                             ("᾿Αν", "Ἀν"),  # improperly formed smooth with caps
                             ("᾿Ον", "Ὀν"),
                             ("᾿Ων", "Ὠν"),
                             ("᾿Ιν", "Ἰν"),
                             ("᾿Εν", "Ἐν"),
                             ('Άπη', 'Απη'),  # alpha caps
                             ('Ὰπη', 'Απη'),
                             ('Ἄπη', 'Ἀπη'),
                             ('Ἂπη', 'Ἀπη'),
                             ('Ἅπη', 'Ἁπη'),
                             ('Ἃπη', 'Ἁπη'),
                             ("Έν", "Εν"),  # epsilon caps
                             ("Ὲν", "Εν"),
                             ("Ἕν", "Ἑν"),
                             ("Ἓν", "Ἑν"),
                             ("Ἔν", "Ἐν"),
                             ("Ἒν", "Ἐν"),
                             ("Ἥν", "Ἡν"),  # eta caps
                             ("Ἣν", "Ἡν"),
                             ("Ἧν", "Ἡν"),
                             ("Ἤν", "Ἠν"),
                             ("Ἢν", "Ἠν"),
                             ("Ἦν", "Ἠν"),
                             ("Ήν", "Ην"),
                             ("Ὴν", "Ην"),
                             ("Ἵν", "Ἱν"),  # iota caps
                             ("Ἳν", "Ἱν"),
                             ("Ἷν", "Ἱν"),
                             ("Ϊν", "Ιν"),
                             ("Ίν", "Ιν"),
                             ("Ὶν", "Ιν"),
                             ("Ίν", "Ιν"),
                             ("Ὅν", "Ὁν"),  # omicron caps
                             ("Ὃν", "Ὁν"),
                             ("Όν", "Ον"),
                             ("Ὸν", "Ον"),
                             ("Ὕν", "Ὑν"),  # upsilon caps
                             ("Ὓν", "Ὑν"),
                             ("Ὗν", "Ὑν"),
                             ("Ϋν", "Υν"),
                             ("Ύν", "Υν"),
                             ("Ὺν", "Υν"),
                             ("Ών", "Ων"),  # omega caps
                             ("Ὼν", "Ων"),
                             ("Ὥν", "Ὡν"),
                             ("Ὣν", "Ὡν"),
                             ("Ὧν", "Ὡν"),
                             ])
def test_normalize_accents(string_in, string_out):
    """
    Unit testing function for paideia_utils.normalize_accents()

    """
    print 'string in', string_in
    print 'expected string out', string_out
    actual = normalize_accents(string_in)
    print 'actual string out', actual
    assert actual == string_out
