#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the paideia_utils module

 Configuration and some fixtures
 the file tests/conftest.py
 run with py.test -xvs path/to/tests/dir

"""

import pytest
from paideia_utils import GreekNormalizer, check_regex
from pprint import pprint


class TestGreekNormalizer():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('ἄγαπὴ', u'ἀγαπη'),  # handle multiple accents
                                 ('“ἀγαπη”', u'"ἀγαπη"'),  # handle curly quotes
                                 ('‘ἀγαπη’', u"'ἀγαπη'"),
                                 (u'ἀγάπη', u'ἀγαπη'),  # handle unicode input
                                 ('τίνος', u'τίνος'),  # words to be *kept* accented
                                 ('τί ἐστῖν', u'τί ἐστιν'),
                                 ('τίς', u'τίς'),
                                 ('τίνα', u'τίνα'),
                                 ('τίνας', u'τίνας'),
                                 ('τίνι', u'τίνι'),
                                 ('Τίνος', u'Τίνος'),
                                 ('Τί', u'Τί'),
                                 ('Τίς', u'Τίς'),
                                 ('Τίνα', u'Τίνα'),
                                 ('Τίνας', u'Τίνας'),
                                 ('Τίνι', u'Τίνι'),
                                 ('τίς', u'τίς'),  # handle q-iota on windows
                                 ('ἀγάπη', u'ἀγαπη'),  # alpha
                                 ('ἀγὰπη', u'ἀγαπη'),
                                 ('ἀγᾶπη', u'ἀγαπη'),
                                 ('ἄν', u'ἀν'),  # alpha with smooth breathing
                                 ('ἂν', u'ἀν'),
                                 ('ἆν', u'ἀν'),
                                 ('ἅν', u'ἁν'),  # alpha with rough breathing
                                 ('ἃν', u'ἁν'),
                                 ('ἇν', u'ἁν'),
                                 ('πᾷν', u'πᾳν'),  # alpha with iota subscript
                                 ('πᾲν', u'πᾳν'),
                                 ('πᾴν', u'πᾳν'),
                                 ('ᾄν', u'ᾀν'),  # alpha with iota subscript & smooth
                                 ('ᾂν', u'ᾀν'),
                                 ('ᾆν', u'ᾀν'),
                                 ('ᾅν', u'ᾁν'),  # alpha with iota subscript & rough
                                 ('ᾃν', u'ᾁν'),
                                 ('ᾇν', u'ᾁν'),
                                 ('πέν', u'πεν'),  # epsilon
                                 ('πὲν', u'πεν'),
                                 ('ἒν', u'ἐν'),  # epsilon with smooth
                                 ('ἔν', u'ἐν'),
                                 ('ἕν', u'ἑν'),  # epsilon with rough
                                 ('ἓν', u'ἑν'),
                                 ('πῆν', u'πην'),  # eta
                                 ('πήν', u'πην'),
                                 ('πὴν', u'πην'),
                                 ('ἤν', u'ἠν'),  # eta with smooth
                                 ('ἢν', u'ἠν'),
                                 ('ἦν', u'ἠν'),
                                 ('ἥν', u'ἡν'),  # eta with rough
                                 ('ἣν', u'ἡν'),
                                 ('ἧν', u'ἡν'),
                                 ('πῇν', u'πῃν'),  # eta with iota subscript
                                 ('πῄν', u'πῃν'),
                                 ('πῂν', u'πῃν'),
                                 ("ᾕν", u"ᾑν"),  # eta with subsc and rough
                                 ("ᾓν", u"ᾑν"),
                                 ("ᾗν", u"ᾑν"),
                                 ("ᾔν", u"ᾐν"),  # eta with subsc and smooth
                                 ("ᾒν", u"ᾐν"),
                                 ("ᾖν", u"ᾐν"),
                                 ("όν", u"ον"),  # omicron
                                 ("ὸν", u"ον"),
                                 ("ὅν", u"ὁν"),  # omicron with rough
                                 ("ὃν", u"ὁν"),
                                 ("ὄν", u"ὀν"),  # omicron with smooth
                                 ("ὂν", u"ὀν"),
                                 ("ῖν", u"ιν"),  # iota
                                 ("ϊν", u"ιν"),
                                 ("ίν", u"ιν"),
                                 ("ὶν", u"ιν"),
                                 ("ίν", u"ιν"),
                                 ("ἵν", u"ἱν"),  # iota with rough
                                 ("ἳν", u"ἱν"),
                                 ("ἷν", u"ἱν"),
                                 ("ἴν", u"ἰν"),  # iota with smooth
                                 ("ἲν", u"ἰν"),
                                 ("ἶν", u"ἰν"),
                                 ("ῦν", u"υν"),  # upsilon
                                 ("ϋν", u"υν"),
                                 ("ύν", u"υν"),
                                 ("ὺν", u"υν"),
                                 ("ὕν", u"ὑν"),  # upsilon with rough
                                 ("ὓν", u"ὑν"),
                                 ("ὗν", u"ὑν"),
                                 ("ὔν", u"ὐν"),  # upsilon with smooth
                                 ("ὒν", u"ὐν"),
                                 ("ὖν", u"ὐν"),
                                 ("ῶν", u"ων"),  # omega
                                 ("ών", u"ων"),
                                 ("ὼν", u"ων"),
                                 ("ὥν", u"ὡν"),  # omega with rough
                                 ("ὣν", u"ὡν"),
                                 ("ὧν", u"ὡν"),
                                 ("ὤν", u"ὠν"),  # omega with smooth
                                 ("ὢν", u"ὠν"),
                                 ("ὦν", u"ὠν"),
                                 ("ῷν", u"ῳν"),  # omega with subsc
                                 ("ῴν", u"ῳν"),
                                 ("ῲν", u"ῳν"),
                                 ("ᾥν", u"ᾡν"),  # omega with subsc and rough
                                 ("ᾣν", u"ᾡν"),
                                 ("ᾧν", u"ᾡν"),
                                 ("ᾤν", u"ᾠν"),  # omega with subsc and smooth
                                 ("ᾢν", u"ᾠν"),
                                 ("ᾦν", u"ᾠν"),
                                 ("῾Ων", u"Ὡν"),  # improperly formed rough with caps
                                 ("῾Ρν", u"Ῥν"),
                                 ("῾Υν", u"Ὑν"),
                                 ("῾Αν", u"Ἁν"),
                                 ("῾Ον", u"Ὁν"),
                                 ("῾Εν", u"Ἑν"),
                                 ("῾Ιν", u"Ἱν"),
                                 ("᾿Αν", u"Ἀν"),  # improperly formed smooth with caps
                                 ("᾿Ον", u"Ὀν"),
                                 ("᾿Ων", u"Ὠν"),
                                 ("᾿Ιν", u"Ἰν"),
                                 ("᾿Εν", u"Ἐν"),
                                 ('Άπη', u'Απη'),  # alpha caps
                                 ('Ὰπη', u'Απη'),
                                 ('Ἄπη', u'Ἀπη'),
                                 ('Ἂπη', u'Ἀπη'),
                                 ('Ἅπη', u'Ἁπη'),
                                 ('Ἃπη', u'Ἁπη'),
                                 ("Έν", u"Εν"),  # epsilon caps
                                 ("Ὲν", u"Εν"),
                                 ("Ἕν", u"Ἑν"),
                                 ("Ἓν", u"Ἑν"),
                                 ("Ἔν", u"Ἐν"),
                                 ("Ἒν", u"Ἐν"),
                                 ("Ἥν", u"Ἡν"),  # eta caps
                                 ("Ἣν", u"Ἡν"),
                                 ("Ἧν", u"Ἡν"),
                                 ("Ἤν", u"Ἠν"),
                                 ("Ἢν", u"Ἠν"),
                                 ("Ἦν", u"Ἠν"),
                                 ("Ήν", u"Ην"),
                                 ("Ὴν", u"Ην"),
                                 ("Ἵν", u"Ἱν"),  # iota caps
                                 ("Ἳν", u"Ἱν"),
                                 ("Ἷν", u"Ἱν"),
                                 ("Ϊν", u"Ιν"),
                                 ("Ίν", u"Ιν"),
                                 ("Ὶν", u"Ιν"),
                                 ("Ίν", u"Ιν"),
                                 ("Ὅν", u"Ὁν"),  # omicron caps
                                 ("Ὃν", u"Ὁν"),
                                 ("Όν", u"Ον"),
                                 ("Ὸν", u"Ον"),
                                 ("Ὕν", u"Ὑν"),  # upsilon caps
                                 ("Ὓν", u"Ὑν"),
                                 ("Ὗν", u"Ὑν"),
                                 ("Ϋν", u"Υν"),
                                 ("Ύν", u"Υν"),
                                 ("Ὺν", u"Υν"),
                                 ("Ών", u"Ων"),  # omega caps
                                 ("Ὼν", u"Ων"),
                                 ("Ὥν", u"Ὡν"),
                                 ("Ὣν", u"Ὡν"),
                                 ("Ὧν", u"Ὡν"),
                                 (u"hi there?", u"hi there?"),  # leave ? alone
                                 ])
    def test_normalize_accents(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.normalize_accents()

        """
        print 'string in', string_in
        print 'expected string out', string_out
        actual = GreekNormalizer().normalize_accents(string_in)
        print 'actual string out', actual
        assert actual == string_out
        assert isinstance(actual, unicode)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('Aγaπη', u'Αγαπη'),
                                 ('deλτα', u'δελτα'),
                                 ('ZEΔ', u'ΖΕΔ'),
                                 ('ΔH', u'ΔΗ'),
                                 ('τivα', u'τινα'),
                                 ('TIΣ', u'ΤΙΣ'),
                                 ('kαππα', u'καππα'),
                                 ('KΑΠΠΑ', u'ΚΑΠΠΑ'),
                                 ('ΑN', u'ΑΝ'),  # TODO: Why does ἘΝ fail here?
                                 ('ἀπo', u'ἀπο'),
                                 ('ἈΠO', u'ἈΠΟ'),
                                 ('ὡpα', u'ὡρα'),
                                 ('ὩPΑ', u'ὩΡΑ'),
                                 ('tε', u'τε'),
                                 ('ἐxω', u'ἐχω'),
                                 ('ἘXΩ', u'ἘΧΩ'),
                                 ('ἐγw', u'ἐγω')
                                 ])
    def test_convert_latin_chars(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.sanitize_greek()

        """
        print 'string in', string_in
        print 'expected string out', string_out
        actual = GreekNormalizer().convert_latin_chars(string_in)
        print 'actual string out', actual
        assert actual == string_out
        assert isinstance(actual, unicode)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('Aγaπη    Aγaπη ', u'Aγaπη Aγaπη'),
                                 ])
    def test_strip_extra_spaces(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.sanitize_greek()

        """
        print 'string in', string_in
        print 'expected string out', string_out
        actual = GreekNormalizer().strip_extra_spaces(string_in)
        print 'actual string out', actual
        assert actual == string_out
        assert isinstance(actual, unicode)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('῾Αγaπὴ    Aγaπη, τί ἐστιv “ἀγαπη.”',
                                  u'Ἁγαπη Αγαπη, τί ἐστιν "ἀγαπη."'),
                                 ])
    def test_normalize(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.sanitize_greek()

        """
        print 'string in', string_in
        print 'expected string out', string_out
        actual = GreekNormalizer().normalize(string_in)
        print 'actual string out', actual
        assert actual == string_out
        assert isinstance(actual, unicode)

@pytest.mark.skipif(False, reason='just because')
@pytest.mark.parametrize('regex,stringdict',
                            [('^(?P<a>ἀγαπη )?ἐγω ἐστιν(?(a)| ἀγαπη)\.$',
                             {'ἀγαπη ἐγω ἐστιν.': True,
                              'ἐγω ἐστιν ἀγαπη.': True,
                              'ἀγαπη ἐγω ἐστιν ἀγαπη.': False,
                              'ἐγω ἐστιν ἀγαπη': False
                              }
                              )
                             ])
def test_check_regex(regex, stringdict):
    """
    """
    actual = check_regex(regex, stringdict.keys())
    pprint(actual)
    assert actual == stringdict

