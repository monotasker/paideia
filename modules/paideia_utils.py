#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright Ian W. Scott, 2013–2014

A collection of miscellaneous utility functions to be used in multiple modules.

Part of the Paideia platform built with web2py.

"""
from collections import OrderedDict
import datetime
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB
from gluon.storage import Storage
from gluon.storage import StorageList
from itertools import chain
from kitchen.text.converters import to_unicode, to_bytes
from plugin_utils import makeutf8, multiple_replace  # encodeutf8,
#from pprint import pprint
import re
import traceback


def simple_obj_print(the_dict, title='No Title', indentation=0):
    """
    Prints a simple thing
    Joseph Boakye jboakye@bwachi.com
    """
    output_obj = {'data': ''}
    simple_obj_print_str(output_obj, the_dict, title, indentation)
    print output_obj['data']


def simple_obj_print_str(output_obj, the_dict, title='No Title', indentation=0, doing_what='S'):
    """
    Prints a simple thing ... same as simple_obj_print but print into string
    Joseph Boakye jboakye@bwachi.com
    some reformatting by Ian W Scott scottianw@gmail.com
    """
    indentation_string = ' '*indentation
    scalar_beg = ''
    scalar_end = ''
    if doing_what in ('L', 'D'):
        scalar_beg = '<li>'
        scalar_end = '</li>'
    if (None == the_dict):
        output_obj['data'] = ''.join([indentation_string, scalar_beg, '<p>',
                                      '{', str(title), ': ', '-None-', '}',
                                      '</p>', scalar_end])
        return
    while True:
        #dictionaries
        if isinstance(the_dict, (Storage, dict)):
            output_obj['data'] = ''.join([indentation_string, str(title),
                                          '(dict:)', '<ol title="dict">'])
            for key in the_dict:
                simple_obj_print_str(output_obj, the_dict[key], key,
                                     indentation + 1, 'D')
            output_obj['data'] += (indentation_string + '</ol>')
            break

        #lists
        if hasattr(the_dict, '__iter__') or isinstance(the_dict, StorageList):
            output_obj['data'] = ''.join([indentation_string, str(title),
                                          '(list:)', '<ol title="list">'])
            count = 0
            try:
                for value in the_dict:
                    simple_obj_print_str(output_obj, value, count,
                                         indentation + 1, 'L')
                    count += 1
            except TypeError, te:
                simple_obj_print_str(output_obj, "list is not iterable",
                                     count, indentation + 1)
                output_obj['data'] += (indentation_string + '</li>')
            output_obj['data'] += (indentation_string + '</ol>')
            break
        #simple item
        while True:
            if type(the_dict) is datetime.datetime:
                strft = the_dict.strftime('%Y %m %d %H %M %S %f')
                output_obj['data'] = ''.join([indentation_string, scalar_beg,
                                              '<p>', '{', str(title), ': ',
                                              strft, '}', '</p>', scalar_end])
                break
            output_obj['data'] = ''.join([indentation_string, scalar_beg,
                                          '<p>', '{', str(title), ': ',
                                          str(the_dict), '}', '</p>',
                                          scalar_end])
            break
        break


class Paideia_Debug(object):
    """
    Carry debug information to the screen
    JOB ... oct 22, 2014
    """
    # TODO: Re-evaluate this
    def __init__(self):
        """
        """
        self.data = 'Debug Enabled'

    def do_print(self, the_object, the_title):
        data_obj = dict(data='')
        simple_obj_print_str(data_obj, the_object, the_title, 0)
        self.data += data_obj['data']


class Uprinter(object):
    """
    Class for printing simple unicode types in a readable (utf8 encoded) form.

    Addresses the problem of print statements to stdout giving unicode code
    points instead of readable characters.

    """
    def __init__(self):
        """
        """
        pass

    def uprint(self, myobj):
        """
        Smart wrapper function to print simple unicode types in a readable form.

        Addresses the problem of print statements to stdout giving unicode code
        points instead of readable characters.

        """
        if type(myobj) == None:
            print 'None'
        calls = {OrderedDict: self._uprint_ordered_dict,
                 dict: self._uprint_dict,
                 list: self._uprint_list,
                 tuple: self._uprint_tuple,
                 unicode: self._internal_print,
                 int: self._internal_print,
                 long: self._internal_print,
                 float: self._internal_print,
                 complex: self._internal_print,
                 str: self._internal_print}
        printfunc = calls[type(myobj)]
        return printfunc(myobj)

    def _internal_print(self, i, lvl=0):
        """
        """
        indent = '    ' * lvl if lvl > 0 else ''
        if isinstance(i, OrderedDict):
            i = self._uprint_ordered_dict(i, lvl=lvl + 1)
        if isinstance(i, dict):
            i = self._uprint_dict(i, lvl=lvl + 1)
        elif isinstance(i, list):
            i = self._uprint_list(i, lvl=lvl + 1)
        elif isinstance(i, tuple):
            i = self._uprint_tuple(i, lvl=lvl + 1)
        elif isinstance(i, (int, long, float, complex)):
            i = makeutf8(str(i))
        else:
            i = "'" + makeutf8(i) + "'"
        return i, lvl

    def _uprint_ordered_dict(self, myod, lvl=0, html=False):
        """
        Prints a unicode OrderedDict in readable form.

        """
        assert isinstance(myod, OrderedDict)
        indent = '    ' * lvl if lvl > 0 else ''
        newod = '\n' + indent + 'OrderedDict([\n'
        for k, i in myod.iteritems():
            i, lvl = self._internal_print(i, lvl)
            newod += indent + " ('" + makeutf8(k) + "', " + i + '),\n'
        newod += '\n' + indent + ' ])'
        return newod

    def _uprint_dict(self, mydict, lvl=0, html=False):
        """
        Prints a unicode dictionary in readable form.

        """
        assert isinstance(mydict, dict)
        indent = '    ' * lvl if lvl > 0 else ''
        newdict = '\n' + indent + '{\n'
        for k, i in mydict.iteritems():
            i, lvl = self._internal_print(i, lvl)
            newdict += indent + ' ' + makeutf8(k) + ': ' + i + ',\n'
        newdict += '\n' + indent + ' }'
        return newdict

    def _uprint_list(self, mylist, lvl=0):
        """
        Prints a unicode list in readable form.

        """
        assert isinstance(mylist, list)
        indent = '    ' * lvl if lvl > 0 else ''
        newlist = '\n' + indent + '['
        for i in mylist:
            i, lvl = self._internal_print(i, lvl)
            newlist += i + ',\n'
        newlist += indent + ' ]'
        return newlist

    def _uprint_tuple(self, mytup, lvl=0):
        """
        Prints a unicode tuple in readable form.
        """
        assert isinstance(mytup, tuple)
        indent = '    ' * lvl if lvl > 0 else ''
        newtup = '\n' + indent + '('
        for i in mytup:
            i, lvl = self._internal_print(i, lvl)
            newtup += indent + ' ' + i + ',\n'
        newtup += indent + ' )'
        return newtup


class GreekNormalizer(object):
    """
    """
    def __init__(self):
        """
        Initialize new GreekNormalizer instance.
        """
        self.isgreek = True

    def normalize(self, strings):
        """
        Primary normalization method that applies all of the other methods.

        This may be called with either a single string or a list of strings. It
        will return the same type as was supplied initially as the argument,
        except that any strings will be returned as unicode strings, regardless
        of their encoding or type when they were supplied.

        """
        debug = False
        if debug: print 'starting normalize'
        strings = [strings] if not isinstance(strings, list) else strings

        strings = self.convert_latin_chars(strings)
        if debug: print 'about to normalize accents'
        if debug: print 'sending strings ============================\n'
        if debug: for s in strings: print type(s), to_bytes(s)
        strings = self.normalize_accents(strings)
        strings = self.strip_extra_spaces(strings)

        if len(strings) == 1:
            strings = strings[0]
        return strings

    def convert_latin_chars(self, strings):
        """
        Check for latin similar characters mixed with Greek and convert them to
        Greek.

        """
        strings = [strings] if not isinstance(strings, list) else strings
        try:
            newstrings = []
            rgx = ur'(?P<a>[Α-Ωα-ω])?([a-z]|[A-Z]|\d|\?)(?(a).*|[Α-Ωα-ω])'
            latin = re.compile(rgx, re.U)
            for string in strings:
                string = unicode(makeutf8(string))
                mymatch = re.search(latin, string)
                if not mymatch:
                    newstring = string
                else:
                    subs = {u'a': u'α',  # y
                            u'A': u'Α',  # n
                            u'd': u'δ',  # y
                            u'e': u'ε',  # y
                            u'E': u'Ε',
                            u'Z': u'Ζ',
                            u'H': u'Η',
                            u'i': u'ι',  # y
                            u'I': u'Ι',
                            u'k': u'κ',
                            u'K': u'Κ',  # y
                            u'v': u'ν',  # y
                            u'N': u'Ν',
                            u'o': u'ο',  # y
                            u'O': u'Ο',  # ΝΝΝ
                            u'p': u'ρ',  # y
                            u'P': u'Ρ',
                            u't': u'τ',  # y
                            u'T': u'Τ',  # y
                            u'Y': u'Υ',
                            u'x': u'χ',
                            u'X': u'Χ',  # y
                            u'w': u'ω',  # y
                            u'?': u';'}
                    if debug: print 'Latin character found in Greek string: '
                    if debug: print mymatch.group(), 'in', string
                    newstring = multiple_replace(string, subs)
                    if debug: print 'replaced with Greek characters:'
                    if debug: print newstring
                newstrings.append(newstring)
            if len(newstrings) == 1:
                newstrings = newstrings[0]
            return newstrings
        except Exception:
            print traceback.format_exc(12)
            return False

    def strip_extra_spaces(self, strings):
        """
        Remove leading, trailing, and multiple internal spaces from string.
        """
        strings = [strings] if not isinstance(strings, list) else strings
        newstrings = []
        for string in strings:
            user_response = unicode(makeutf8(string))
            while '  ' in user_response:  # remove multiple inner spaces
                user_response = user_response.replace('  ', ' ')
            user_response = user_response.strip()  # remove leading and trailing spaces
            newstrings.append(user_response)
        if len(newstrings) == 1:
            newstrings = newstrings[0]
        return newstrings

    def normalize_accents(self, strings):
        """
        Return a polytonic Greek unicode string with accents removed.

        The one argument should be a list of strings to be normalized. It can
        also handle a single string.

        """
        debug = False
        instrings = [strings] if not isinstance(strings, list) else strings

        outstrings = []
        for string in instrings:
            substrs = to_unicode(string).split(' ')

            equivs = {u'α': [u'ά', u'ὰ', u'ᾶ'],
                      u'Α': [u'Ά', u'Ὰ'],  # caps
                      u'ἀ': [u'ἄ', u'ἂ', u'ἆ'],
                      u'Ἀ': [u'Ἄ', u'Ἂ', u'Ἆ', u'᾿Α'],  # caps (including combining )
                      u'ἁ': [u'ἅ', u'ἃ', u'ἇ'],
                      u'Ἁ': [u'Ἅ', u'Ἃ', u'Ἇ', u'῾Α'],  # caps (including combining)
                      u'ᾳ': [u'ᾷ', u'ᾲ', u'ᾴ'],
                      u'ᾀ': [u'ᾄ', u'ᾂ', u'ᾆ'],
                      u'ᾁ': [u'ᾅ', u'ᾃ', u'ᾇ'],
                      u'ε': [u'έ', u'ὲ'],
                      u'Ε': [u'Έ', u'Ὲ'],  # caps
                      u'ἐ': [u'ἔ', u'ἒ'],
                      u'Ἐ': [u'Ἔ', u'Ἒ', u'᾿Ε'],  # caps (including combining)
                      u'ἑ': [u'ἕ', u'ἓ'],
                      u'Ἑ': [u'Ἕ', u'Ἓ', u'῾Ε'],  # caps (including combining)
                      u'η': [u'ῆ', u'ή', u'ὴ'],
                      u'Η': [u'Ή', u'Ὴ'],  # caps
                      u'ἠ': [u'ἤ', u'ἢ', u'ἦ'],
                      u'Ἠ': [u'Ἤ', u'Ἢ', u'Ἦ', u'᾿Η'],  # caps (including combining)
                      u'ἡ': [u'ἥ', u'ἣ', u'ἧ'],
                      u'Ἡ': [u'Ἥ', u'Ἣ', u'Ἧ', u'῾Η'],  # caps (including combining)
                      u'ῃ': [u'ῇ', u'ῄ', u'ῂ'],
                      u'ᾐ': [u'ᾔ', u'ᾒ', u'ᾖ'],
                      u'ᾑ': [u'ᾕ', u'ᾓ', u'ᾗ'],
                      u'ι': [u'ῖ', u'ϊ', u'ί', u'ὶ', u'ί'],
                      u'ἰ': [u'ἴ', u'ἲ', u'ἶ'],
                      u'ἱ': [u'ἵ', u'ἳ', u'ἷ'],
                      u'Ι': [u'Ϊ', u'Ί', u'Ὶ', u'Ί'],  # caps
                      u'Ἰ': [u'Ἴ', u'Ἲ', u'Ἶ', u'᾿Ι'],  # caps (including combining)
                      u'Ἱ': [u'Ἵ', u'Ἳ', u'Ἷ', u'῾Ι'],  # caps (including combining)
                      u'ο': [u'ό', u'ὸ'],
                      u'ὀ': [u'ὄ', u'ὂ'],
                      u'ὁ': [u'ὅ', u'ὃ'],
                      u'Ο': [u'Ό', u'Ὸ'],  # caps
                      u'Ὀ': [u'Ὄ', u'Ὂ', u'᾿Ο'],  # caps (including combining)
                      u'Ὁ': [u'Ὅ', u'Ὃ', u'῾Ο'],  # caps (including combining)
                      u'υ': [u'ῦ', u'ϋ', u'ύ', u'ὺ'],
                      u'ὐ': [u'ὔ', u'ὒ', u'ὖ'],
                      u'ὑ': [u'ὕ', u'ὓ', u'ὗ'],
                      u'Υ': [u'Ϋ', u'Ύ', u'Ὺ'],  # caps TODO: no capital U with smooth?
                      u'Ὑ': [u'Ὕ', u'Ὓ', u'Ὗ', u'῾Υ'],  # caps (including combining)
                      u'ω': [u'ῶ', u'ώ', u'ὼ'],
                      u'ὠ': [u'ὤ', u'ὢ', u'ὦ'],
                      u'ὡ': [u'ὥ', u'ὣ', u'ὧ'],
                      u'Ω': [u'Ώ', u'Ὼ'],  # caps
                      u'Ὠ': [u'Ὤ', u'Ὢ', u'Ὦ', u'᾿Ω'],  # caps (including combining)
                      u'Ὡ': [u'Ὥ', u'Ὣ', u'Ὧ', u'῾Ω'],  # caps (including combining)
                      u'ῳ': [u'ῷ', u'ῴ', u'ῲ'],
                      u'ᾠ': [u'ᾤ', u'ᾢ', u'ᾦ'],
                      u'ᾡ': [u'ᾥ', u'ᾣ', u'ᾧ'],
                      u'Ῥ': [u'῾Ρ'],  # also handle improperly formed marks (rough)
                      u'"': [u'“', u'”', u'«', u'»'],  # handle curly quotes
                      u"'": [u'‘', u'’'],
                      }
            accented = chain(*equivs.values())
            restr = '|'.join(accented)
            newstrings = []
            # FIXME: this is ugly and conflicts with question mark conversion
            exempt = [u'τίνος', u'τί', u'τίς', u'τίνα', u'τίνας', u'τίνι',
                      u'Τίνος', u'Τί', u'Τίς', u'Τίνα', u'Τίνας', u'Τίνι']
            ex_period = [x + u'.' for x in exempt]
            ex_scolon = [x + u';' for x in exempt]
            ex_anotel = [x + u'·' for x in exempt]
            ex_comma = [x + u',' for x in exempt]
            ex_qmark = [x + u'\?' for x in exempt]
            ex_colon = [x + u':' for x in exempt]
            exempt = list(chain(exempt, ex_colon, ex_comma, ex_qmark, ex_scolon,
                          ex_period, ex_anotel))

            for mystring in substrs:
                latin_chars = re.compile(r'^[a-zA-Z\s\.,:;\'\"\?]+$', re.U)
                islatin = re.match(latin_chars, mystring)
                if debug: print 'substring:', to_bytes(mystring)
                if debug: print 'islatin:', islatin
                if not islatin:
                    mystring = mystring.strip()
                    if debug: print '1:', to_bytes(mystring)
                    mystring = mystring.replace(u'ί', u'ί')  # avoid q-i iota on windows
                    if debug: print '2:', to_bytes(mystring)

                    if mystring not in exempt:
                        # below print statement causes UnicodeEncodeError on live server
                        # print mystring, 'not exempt', type(mystring)
                        matching_letters = re.findall(to_unicode(restr), mystring,
                                                    re.I | re.U)
                        if debug: print 'matching letters:', to_bytes(matching_letters)
                        if matching_letters:

                            edict = {k: v for k, v in equivs.iteritems()
                                    if [m for m in v if m in matching_letters]}
                            key_vals = {ltr: k
                                        for ltr in list(chain(*edict.values()))
                                        for k in edict.keys()
                                        if ltr in edict[k]}
                            if debug: print key_vals
                            mystring = multiple_replace(mystring, key_vals)
                        else:
                            if debug: print 'no matching letters'
                    else:
                        if debug: print to_bytes(mystring), 'exempt'
                else:
                    if debug: print 'no Greek'
                newstrings.append(mystring)
            if debug: print '3'
            newstring = ' '.join(newstrings)
            if debug: print '4'
            outstrings.append(newstring)
            if debug: print '5'
        if len(outstrings) == 1:
            outstrings = outstrings[0]
        if debug: print 'returning', to_bytes(outstrings)
        return outstrings


def check_regex(rgx, readables):
    """
    Return a re.match object for each given string, tested with the given regex.

    The "readables" argument should be a list of strings to be tested.

    """
    readables = readables if isinstance(readables, list) else [readables]
    pattern = re.compile(to_unicode(rgx), re.I | re.U)
    rdict = {}
    for rsp in readables:
        # print 'pattern --------------------------------'
        # print rgx
        # print 'readable'
        # print rsp
        match = re.match(pattern, to_unicode(rsp))
        rdict[rsp] = True if match else False
        # if match:
        #   print 'they match!'
        # else:
        #   print 'no match ***'
        # print match
    return rdict


def test_step_regex():
    """
    Return a form that handles regex testing for individual steps.
    """
    db = current.db
    result = None
    form = SQLFORM.factory(Field('step_number', 'integer',
                                 requires=IS_IN_DB(db, 'steps.id')))

    if form.process(dbio=False, keepvalues=True).accepted:
        sid = form.vars.step_number
        row = db.steps(sid)
        result = check_regex(row.response1, row.readable_response.split('|'))
        result = BEAUTIFY(result)
    elif form.errors:
        result = BEAUTIFY(form.errors)

    return form, result
