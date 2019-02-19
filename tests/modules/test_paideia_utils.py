#! /usr/bin/python
# -*- coding: UTF-8 -*-
"""
 Unit tests for the paideia_utils module

 Configuration and some fixtures
 the file tests/conftest.py
 run with py.test -xvs path/to/tests/dir

"""

from kitchen.text.converters import to_unicode
import pytest
from paideia_utils import GreekNormalizer, check_regex
from plugin_utils import makeutf8
from pprint import pprint
import re


class TestGreekNormalizer():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('ἄγαπὴ', 'ἀγαπη'),  # handle multiple accents
                                 ('“ἀγαπη”', '"ἀγαπη"'),  # handle curly quotes
                                 ('‘ἀγαπη’', "'ἀγαπη'"),
                                 ('ἀγάπη', 'ἀγαπη'),  # handle unicode input
                                 ('τίνος', 'τίνος'),  # words to be *kept* accented
                                 ('τί ἐστῖν', 'τί ἐστιν'),
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
                                 ("hi there?", "hi there?"),  # leave ? alone
                                 ])
    def test_normalize_accents(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.normalize_accents()

        """
        print('string in', string_in)
        print('expected string out', string_out)
        actual = GreekNormalizer().normalize_accents(string_in)
        print('actual string out', actual)
        assert actual == string_out
        assert isinstance(actual, str)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('Aγaπη', 'Αγαπη'),
                                 ('deλτα', 'δελτα'),
                                 ('ZEΔ', 'ΖΕΔ'),
                                 ('ΔH', 'ΔΗ'),
                                 ('τivα', 'τινα'),
                                 ('TIΣ', 'ΤΙΣ'),
                                 ('kαππα', 'καππα'),
                                 ('KΑΠΠΑ', 'ΚΑΠΠΑ'),
                                 ('ΑN', 'ΑΝ'),  # TODO: Why does ἘΝ fail here?
                                 ('ἀπo', 'ἀπο'),
                                 ('ἈΠO', 'ἈΠΟ'),
                                 ('ὡpα', 'ὡρα'),
                                 ('ὩPΑ', 'ὩΡΑ'),
                                 ('tε', 'τε'),
                                 ('ἐxω', 'ἐχω'),
                                 ('ἘXΩ', 'ἘΧΩ'),
                                 ('ἐγw', 'ἐγω'),
                                 ("ἀγαπη?", "ἀγαπη;"),
                                 ("hi bob?", "hi bob?")
                                 ])
    def test_convert_latin_chars(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.sanitize_greek()

        """
        print('string in', string_in)
        print('expected string out', string_out)
        actual = GreekNormalizer().convert_latin_chars(string_in)
        print('actual string out', actual)
        assert actual == string_out
        assert isinstance(actual, str)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out',
                                [('Aγaπη    Aγaπη ', 'Aγaπη Aγaπη'),
                                 ])
    def test_strip_extra_spaces(self, string_in, string_out):
        """
        Unit testing function for paideia_utils.sanitize_greek()

        """
        print('string in', string_in)
        print('expected string out', string_out)
        actual = GreekNormalizer().strip_extra_spaces(string_in)
        print('actual string out', actual)
        assert actual == string_out
        assert isinstance(actual, str)

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('string_in,string_out,regex',
                                [('῾Αγaπὴ    Aγaπη, τί ἐστιv “ἀγαπη.”',
                                  'Ἁγαπη Αγαπη, τί ἐστιν "ἀγαπη."',
                                  r'Ἁγαπη Αγαπη, τί ἐστιν "ἀγαπη."'),
                                  ('Pωμαιος', 'Ρωμαιος', r'Ρωμαιος'),
                                  ('παρά', 'παρα', r'παρα'),
                                  ('τίς', 'τίς', r'τίς'),  # q iota on windows
                                  ('πoιει', 'ποιει', r'ποιει'),
                                  ('Oὑτος', 'Οὑτος', r'Οὑτος'),
                                 ])
    def test_normalize(self, string_in, string_out, regex):
        """
        Unit testing function for paideia_utils.sanitize_greek()

        """
        print('string in', string_in)
        print('expected string out', string_out)
        actual = GreekNormalizer().normalize(string_in)
        print('actual string out', actual)
        assert actual == string_out
        assert isinstance(actual, str)
        regex1 = re.compile(to_unicode(regex), re.I | re.U)
        assert re.match(regex1, to_unicode(actual))

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
    actual = check_regex(regex, list(stringdict.keys()))
    pprint(actual)
    assert actual == stringdict
