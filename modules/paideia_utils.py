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
from plugin_utils import multiple_replace
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
    print(output_obj['data'])


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
            except TypeError as te:
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
            print('None')
        calls = {OrderedDict: self._uprint_ordered_dict,
                 dict: self._uprint_dict,
                 list: self._uprint_list,
                 tuple: self._uprint_tuple,
                 str: self._internal_print,
                 int: self._internal_print,
                 int: self._internal_print,
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
        elif isinstance(i, (int, float, complex)):
            i = str(i)
        else:
            i = "'" + i + "'"
        return i, lvl

    def _uprint_ordered_dict(self, myod, lvl=0, html=False):
        """
        Prints a unicode OrderedDict in readable form.

        """
        assert isinstance(myod, OrderedDict)
        indent = '    ' * lvl if lvl > 0 else ''
        newod = '\n' + indent + 'OrderedDict([\n'
        for k, i in list(myod.items()):
            i, lvl = self._internal_print(i, lvl)
            newod += indent + " ('" + k + "', " + i + '),\n'
        newod += '\n' + indent + ' ])'
        return newod

    def _uprint_dict(self, mydict, lvl=0, html=False):
        """
        Prints a unicode dictionary in readable form.

        """
        assert isinstance(mydict, dict)
        indent = '    ' * lvl if lvl > 0 else ''
        newdict = '\n' + indent + '{\n'
        for k, i in list(mydict.items()):
            i, lvl = self._internal_print(i, lvl)
            newdict += indent + ' ' + k + ': ' + i + ',\n'
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
        debug = True
        if debug: print('starting normalize')
        strings = [strings] if not isinstance(strings, list) \
            else strings

        if debug: print('about to convert latin')
        strings = self.convert_latin_chars(strings)
        if debug: print('about to normalize accents')
        if debug: print('sending strings ============================\n')
        if debug:
            for s in strings:
                print(type(s), to_bytes(s))
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
        debug = True
        strings = [strings] if not isinstance(strings, list) else strings
        if debug: print(strings)
        try:
            newstrings = []
            rgx = r'(?P<a>[Α-Ωα-ω\u1F00-\u1FFF])?([a-z]|[A-Z]|\d|\?)+(?(a).*|[Α-Ωα-ω\u1F00-\u1FFF])'
            latin = re.compile(rgx)
            for string in strings:
                if debug: print('trying', string)
                mymatch = re.search(latin, string)
                if debug: print('match result:', mymatch)
                if not mymatch:
                    newstring = string
                else:
                    subs = {'a': 'α',  # y
                            'A': 'Α',  # y
                            'd': 'δ',  # y
                            'e': 'ε',  # y
                            'E': 'Ε',
                            'Z': 'Ζ',
                            'H': 'Η',
                            'i': 'ι',  # y
                            'I': 'Ι',
                            'k': 'κ',
                            'K': 'Κ',  # y
                            'v': 'ν',  # y
                            'N': 'Ν',
                            'o': 'ο',  # y
                            'O': 'Ο',  # y
                            'p': 'ρ',  # y
                            'P': 'Ρ',  # y
                            't': 'τ',  # y
                            'T': 'Τ',  # y
                            'Y': 'Υ',
                            'x': 'χ',
                            'X': 'Χ',  # y
                            'w': 'ω',  # y
                            '?': ';'}
                    if debug: print('Latin character found in Greek string: ')
                    if debug: print(mymatch.group(), 'in', string)
                    if debug: print(bytes(mymatch.group(), 'utf8'), 'in', bytes(string, 'utf8'))
                    newstring = multiple_replace(string, subs)
                    if debug: print('replaced with Greek characters:')
                    if debug: print(newstring)
                    if debug: print(bytes(newstring, 'utf8'))
                newstrings.append(newstring)
            if len(newstrings) == 1:
                newstrings = newstrings[0]
            return newstrings
        except Exception:
            print(traceback.format_exc(12))
            return False

    def strip_extra_spaces(self, strings):
        """
        Remove leading, trailing, and multiple internal spaces from string.
        """
        strings = [strings] if not isinstance(strings, list) else strings
        newstrings = []
        for string in strings:
            user_response = string
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
        debug = True
        instrings = [strings] if not isinstance(strings, list) else strings

        outstrings = []
        for string in instrings:
            substrs = string.split(' ')

            equivs = {'α': ['ά', 'ὰ', 'ᾶ'],
                      'Α': ['Ά', 'Ὰ'],  # caps
                      'ἀ': ['ἄ', 'ἂ', 'ἆ'],
                      'Ἀ': ['Ἄ', 'Ἂ', 'Ἆ', '᾿Α'],  # caps (including combining )
                      'ἁ': ['ἅ', 'ἃ', 'ἇ'],
                      'Ἁ': ['Ἅ', 'Ἃ', 'Ἇ', '῾Α'],  # caps (including combining)
                      'ᾳ': ['ᾷ', 'ᾲ', 'ᾴ'],
                      'ᾀ': ['ᾄ', 'ᾂ', 'ᾆ'],
                      'ᾁ': ['ᾅ', 'ᾃ', 'ᾇ'],
                      'ε': ['έ', 'ὲ'],
                      'Ε': ['Έ', 'Ὲ'],  # caps
                      'ἐ': ['ἔ', 'ἒ'],
                      'Ἐ': ['Ἔ', 'Ἒ', '᾿Ε'],  # caps (including combining)
                      'ἑ': ['ἕ', 'ἓ'],
                      'Ἑ': ['Ἕ', 'Ἓ', '῾Ε'],  # caps (including combining)
                      'η': ['ῆ', 'ή', 'ὴ'],
                      'Η': ['Ή', 'Ὴ'],  # caps
                      'ἠ': ['ἤ', 'ἢ', 'ἦ'],
                      'Ἠ': ['Ἤ', 'Ἢ', 'Ἦ', '᾿Η'],  # caps (including combining)
                      'ἡ': ['ἥ', 'ἣ', 'ἧ'],
                      'Ἡ': ['Ἥ', 'Ἣ', 'Ἧ', '῾Η'],  # caps (including combining)
                      'ῃ': ['ῇ', 'ῄ', 'ῂ'],
                      'ᾐ': ['ᾔ', 'ᾒ', 'ᾖ'],
                      'ᾑ': ['ᾕ', 'ᾓ', 'ᾗ'],
                      'ι': ['ῖ', 'ϊ', 'ί', 'ὶ', 'ί'],
                      'ἰ': ['ἴ', 'ἲ', 'ἶ'],
                      'ἱ': ['ἵ', 'ἳ', 'ἷ'],
                      'Ι': ['Ϊ', 'Ί', 'Ὶ', 'Ί'],  # caps
                      'Ἰ': ['Ἴ', 'Ἲ', 'Ἶ', '᾿Ι'],  # caps (including combining)
                      'Ἱ': ['Ἵ', 'Ἳ', 'Ἷ', '῾Ι'],  # caps (including combining)
                      'ο': ['ό', 'ὸ'],
                      'ὀ': ['ὄ', 'ὂ'],
                      'ὁ': ['ὅ', 'ὃ'],
                      'Ο': ['Ό', 'Ὸ'],  # caps
                      'Ὀ': ['Ὄ', 'Ὂ', '᾿Ο'],  # caps (including combining)
                      'Ὁ': ['Ὅ', 'Ὃ', '῾Ο'],  # caps (including combining)
                      'υ': ['ῦ', 'ϋ', 'ύ', 'ὺ'],
                      'ὐ': ['ὔ', 'ὒ', 'ὖ'],
                      'ὑ': ['ὕ', 'ὓ', 'ὗ'],
                      'Υ': ['Ϋ', 'Ύ', 'Ὺ'],  # caps TODO: no capital U with smooth?
                      'Ὑ': ['Ὕ', 'Ὓ', 'Ὗ', '῾Υ'],  # caps (including combining)
                      'ω': ['ῶ', 'ώ', 'ὼ'],
                      'ὠ': ['ὤ', 'ὢ', 'ὦ'],
                      'ὡ': ['ὥ', 'ὣ', 'ὧ'],
                      'Ω': ['Ώ', 'Ὼ'],  # caps (including combining)
                      'Ὠ': ['Ὤ', 'Ὢ', 'Ὦ', '᾿Ω'],  # caps (including combining)
                      'Ὡ': ['Ὥ', 'Ὣ', 'Ὧ', '῾Ω'],  # caps (including combining)
                      'ῳ': ['ῷ', 'ῴ', 'ῲ'],
                      'ᾠ': ['ᾤ', 'ᾢ', 'ᾦ'],
                      'ᾡ': ['ᾥ', 'ᾣ', 'ᾧ'],
                      'Ῥ': ['῾Ρ'],  # also handle improperly formed marks (rough)
                      '"': ['“', '”', '«', '»'],  # handle curly quotes
                      "'": ['‘', '’'],
                      }
            accented = chain(*list(equivs.values()))
            restr = '|'.join(accented)
            newstrings = []
            # FIXME: this is ugly and conflicts with question mark conversion
            exempt = ['τίνος', 'τί', 'τίς', 'τίνα', 'τίνας', 'τίνι',
                      'Τίνος', 'Τί', 'Τίς', 'Τίνα', 'Τίνας', 'Τίνι']
            ex_period = [x + '.' for x in exempt]
            ex_scolon = [x + ';' for x in exempt]
            ex_anotel = [x + '·' for x in exempt]
            ex_comma = [x + ',' for x in exempt]
            ex_qmark = [x + '?' for x in exempt]
            ex_colon = [x + ':' for x in exempt]
            exempt = list(chain(exempt, ex_colon, ex_comma, ex_qmark, ex_scolon,
                          ex_period, ex_anotel))

            for mystring in substrs:
                latin_chars = re.compile(r'^[a-zA-Z\s\.,:;\'\"\?]+$')
                islatin = re.match(latin_chars, mystring)
                if debug: print('substring:', mystring)
                if debug: print('islatin:', islatin)
                if not islatin:
                    mystring = mystring.strip()
                    if debug: print('1:', mystring)
                    mystring = mystring.replace('ί', 'ί')  # avoid q-i iota on windows
                    if debug: print('2:', mystring)

                    if mystring not in exempt:
                        # below print statement causes UnicodeEncodeError on live server
                        # print mystring, 'not exempt', type(mystring)
                        matching_letters = re.findall(restr, mystring,
                                                      re.I)
                        if debug: print('matching letters:', matching_letters)
                        if matching_letters:
                            edict = {k: v for k, v in list(equivs.items())
                                    if [m for m in v if m in matching_letters]}
                            key_vals = {ltr: k
                                        for ltr in list(chain(*list(edict.values())))
                                        for k in list(edict.keys())
                                        if ltr in edict[k]}
                            if debug: print(key_vals)
                            mystring = multiple_replace(mystring, key_vals)
                            if debug: print('after replacing:' + mystring)
                        else:
                            if debug: print('no matching letters')
                    else:
                        if debug: print(mystring, 'exempt')
                else:
                    if debug: print('no Greek')
                newstrings.append(mystring)
            if debug: print('3' + str(newstrings))
            newstring = ' '.join(newstrings)
            if debug: print('4' + newstring)
            outstrings.append(newstring)
            if debug: print('5' + str(outstrings))
        if len(outstrings) == 1:
            outstrings = outstrings[0]
        if debug: print('returning', outstrings)
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
