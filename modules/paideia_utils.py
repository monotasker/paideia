#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright Ian W. Scott, 2013–2014

A collection of miscellaneous utility functions to be used in multiple modules.

Part of the Paideia platform built with web2py.

"""
import traceback
#import locale
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB
from gluon.storage import Storage
from gluon.storage import StorageList
#from plugin_ajaxselect import AjaxSelect
import re
from itertools import chain
#from pprint import pprint
#import datetime
#import json
import plugin_utils
from plugin_utils import makeutf8, encodeutf8
import datetime


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


def uprint(myobj):
    """
    Smart wrapper function to print simple unicode types in a readable form.

    Addresses the problem of print statements to stdout giving unicode code
    points instead of readable characters.

    """
    if type(myobj) == None:
        print 'None'
    calls = {dict: uprint_dict,
             list: uprint_list,
             tuple: uprint_tuple,
             unicode: makeutf8,
             int: makeutf8,
             long: makeutf8,
             float: makeutf8,
             str: makeutf8}
    printfunc = calls[type(myobj)]
    prettystring = printfunc(myobj)
    return prettystring


def uprint_dict(mydict, lvl=0, html=False):
    """
    Prints a unicode dictionary in readable form.

    """
    assert isinstance(mydict, dict)
    indent = '    ' * lvl if lvl > 0 else ''
    newdict = '\n' + indent + '{\n'
    for k, i in mydict.iteritems():
        if isinstance(i, dict):
            i = uprint_dict(i, lvl=lvl + 1)
        elif isinstance(i, list):
            i = uprint_list(i, lvl=lvl + 1)
        elif isinstance(i, tuple):
            i = uprint_tuple(i, lvl=lvl + 1)
        elif isinstance(i, (int, long, float, complex)):
            i = str(i)
        else:
            i = makeutf8(i)
        newdict += indent + ' ' + makeutf8(k) + ': ' + i + ',\n'
    newdict += '\n' + indent + ' }'
    return newdict


def uprint_list(mylist, lvl=0):
    """
    Prints a unicode list in readable form.

    """
    assert isinstance(mylist, list)
    indent = '    ' * lvl if lvl > 0 else ''
    newlist = '\n' + indent + '['
    for i in mylist:
        if isinstance(i, dict):
            i = uprint_dict(i, lvl=lvl + 1)
        elif isinstance(i, list):
            i = uprint_list(i, lvl=lvl + 1)
        elif isinstance(i, tuple):
            i = uprint_tuple(i, lvl=lvl + 1)
        elif isinstance(i, (int, long, float, complex)):
            i = str(i)
        else:
            i = makeutf8(i)
        newlist += indent + ' ' + i + ',\n'
    newlist += indent + ' ]'
    return newlist


def uprint_tuple(mytup, lvl=0):
    """
    Prints a unicode tuple in readable form.
    """
    assert isinstance(mytup, tuple)
    indent = '    ' * lvl if lvl > 0 else ''
    newtup = '\n' + indent + '('
    for i in mytup:
        if isinstance(i, dict):
            i = uprint_dict(i, lvl=lvl + 1)
        elif isinstance(i, list):
            i = uprint_list(i, lvl=lvl + 1)
        elif isinstance(i, tuple):
            i = uprint_tuple(i, lvl=lvl + 1)
        elif isinstance(i, (int, long, float, complex)):
            i = str(i)
        else:
            i = makeutf8(i)
        newtup += indent + ' ' + i + ',\n'
    newtup += indent + ' )'
    return newtup


def sanitize_greek(strings):
    """
    Check for latin similar characters mixed with Greek and convert them to
    Greek.

    """
    try:
        newstrings = []
        for string in strings:
            string = makeutf8(string)
            rgx = makeutf8(r'(?P<a>[Α-Ωα-ω])?([a-z]|[A-Z]|\d)(?(a).*|[Α-Ωα-ω])')
            latin = re.compile(rgx, re.U)
            mymatch = re.search(latin, string)
            if not mymatch:
                newstring = string
            else:
                subs = (('a', 'α'),
                        ('A', 'Α'),
                        ('d', 'δ'),
                        ('e', 'ε'),
                        ('E', 'Ε'),
                        ('Z', 'Ζ'),
                        ('H', 'Η'),
                        ('i', 'ι'),
                        ('I', 'Ι'),
                        ('k', 'κ'),
                        ('K', 'Κ'),
                        ('n', 'ν'),
                        ('N', 'Ν'),
                        ('o', 'ο'),
                        ('O', 'Ο'),
                        ('r', 'ρ'),
                        ('R', 'Ρ'),
                        ('t', 'τ'),
                        ('T', 'Τ'),
                        ('x', 'χ'),
                        ('X', 'Χ'),
                        ('w', 'ω'))
                print 'Latin character found in Greek string: '
                print mymatch.group(), 'in', string
                newstring = multiple_replace(string, *subs)
                print 'replaced with Greek characters:'
                print newstring
            newstrings.append(newstring)
        return newstrings
    except Exception:
        print traceback.format_exc(12)


def test_regex(regex, readables):
    """
    Return a re.match object for each given string, tested with the given regex.

    The "readables" argument should be a list of strings to be tested.

    """
    #TODO: DEPRECATE IN FAVOUR OF PLUGIN_UTILS VERSION
    readables = islist(readables)
    test_regex = re.compile(makeutf8(regex), re.I | re.U)
    rdict = {}
    for rsp in readables:
        match = re.match(test_regex, makeutf8(rsp))
        rdict[rsp] = True if match else False
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
        result = test_regex(row.response1, row.readable_response.split('|'))
        result = BEAUTIFY(result)
    elif form.errors:
        result = BEAUTIFY(form.errors)

    return form, result


def normalize_accents(string):
    """
    Return a polytonic Greek unicode string with accents removed.

    The one argument should be a list of strings to be normalized. It can
    also handle a single string.

    So far this function only handles lowercase strings.
    """
    strings = makeutf8(string).split(' ')

    equivs = {u'α': [u'ά', u'ὰ', u'ᾶ'],
              u'ἀ': [u'ἄ', u'ἂ', u'ἆ'],
              u'ἁ': [u'ἅ', u'ἃ', u'ἇ'],
              u'ᾳ': [u'ᾷ', u'ᾲ', u'ᾴ'],
              u'ᾀ': [u'ᾄ', u'ᾂ', u'ᾆ'],
              u'ᾁ': [u'ᾅ', u'ᾃ', u'ᾇ'],
              u'ε': [u'έ', u'ὲ'],
              u'ἐ': [u'ἔ', u'ἒ'],
              u'ἑ': [u'ἕ', u'ἓ'],
              u'η': [u'ῆ', u'ή', u'ὴ'],
              u'ἠ': [u'ἤ', u'ἢ', u'ἦ'],
              u'ἡ': [u'ἥ', u'ἣ', u'ἧ'],
              u'ῃ': [u'ῇ', u'ῄ', u'ῂ'],
              u'ᾐ': [u'ᾔ', u'ᾒ', u'ᾖ'],
              u'ᾑ': [u'ᾕ', u'ᾓ', u'ᾗ'],
              u'ι': [u'ῖ', u'ϊ', u'ί', u'ὶ', u'ί'],
              u'ἰ': [u'ἴ', u'ἲ', u'ἶ'],
              u'ἱ': [u'ἵ', u'ἳ', u'ἷ'],
              u'ο': [u'ό', u'ὸ'],
              u'ὀ': [u'ὄ', u'ὂ'],
              u'ὁ': [u'ὅ', u'ὃ'],
              u'υ': [u'ῦ', u'ϋ', u'ύ', u'ὺ'],
              u'ὐ': [u'ὔ', u'ὒ', u'ὖ'],
              u'ὑ': [u'ὕ', u'ὓ', u'ὗ'],
              u'ω': [u'ῶ', u'ώ', u'ὼ'],
              u'ὠ': [u'ὤ', u'ὢ', u'ὦ'],
              u'ὡ': [u'ὥ', u'ὣ', u'ὧ'],
              u'ῳ': [u'ῷ', u'ῴ', u'ῲ'],
              u'ᾠ': [u'ᾤ', u'ᾢ', u'ᾦ'],
              u'ᾡ': [u'ᾥ', u'ᾣ', u'ᾧ'],
              u'Ῥ': [u'῾Ρ'],  # also handle improperly formed marks
              u'Ἁ': [u'῾Α'],
              u'Ἑ': [u'῾Ε'],
              u'Ἱ': [u'῾Ι'],
              u'Ὑ': [u'῾Υ'],
              u'Ὁ': [u'῾Ο'],
              u'Ὡ': [u'῾Ω'],
              }
    accented = chain(*equivs.values())
    restr = '|'.join(accented)
    newstrings = []
    for mystring in strings:
        mystring = mystring.replace(u'ί', u'ί')  # avoid q-i iota on windows

        # this is ugly
        exempt = [u'τίνος', u'τί', u'τίς', u'τίνα', u'τίνας', u'τίνι',
                  u'Τίνος', u'Τί', u'Τίς', u'Τίνα', u'Τίνας', u'Τίνι']
        ex_period = [x + u'.' for x in exempt]
        ex_scolon = [x + u';' for x in exempt]
        ex_comma = [x + u',' for x in exempt]
        ex_qmark = [x + u'?' for x in exempt]
        ex_colon = [x + u':' for x in exempt]
        exempt = chain(exempt, ex_colon, ex_comma, ex_qmark, ex_scolon, ex_period)

        if mystring not in exempt:
            matching_letters = re.findall(makeutf8(restr), mystring,
                                          re.I | re.U)
            print 'matching_letters', uprint(matching_letters)
            if matching_letters:
                edict = {makeutf8(k): v for k, v in equivs.iteritems()
                        if [m for m in v if makeutf8(m) in matching_letters]}
                print 'edict', edict
                for k, v in edict.iteritems():
                    myval = [l for l in v if makeutf8(l) in matching_letters][0]
                    mystring = mystring.replace(myval, k)
            else:
                pass
        else:
            pass
        newstrings.append(mystring)
    newstring = ' '.join(newstrings)
    return encodeutf8(newstring)


"""""""""""""""""""""""""""""""""""""""""""""""""""
ALL BELOW ARE DEPRECATED, MOVED TO plugin_utils
"""""""""""""""""""""""""""""""""""""""""""""""""""


def multiple_replace(string, *key_values):
    """
    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.multiple_replacer(string, *key_values)


def islist(dat):
    """
    Return the supplied object converted to a list if it is not already.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.islist(dat)


def clr(string, mycol='white'):
    """
    Return a string surrounded by ansi colour escape sequences.

    This function is intended to simplify colourizing terminal output.
    The default color is white. The function can take any number of positional
    arguments as component strings, which will be joined (space delimited)
    before being colorized.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.clr(string, mycol)


def printutf(string):
    """
    Convert unicode string to readable characters for printing.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.printutf(string)


def capitalize(letter):
    """
    Convert string to upper case in utf-8 safe way.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.capitalize(letter)


def lowercase(letter):
    """
    Convert string to lower case in utf-8 safe way.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.lowercase(letter)


def firstletter(mystring):
    """
    Find the first letter of a byte-encoded unicode string.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.firstletter(mystring)


def capitalize_first(mystring):
    """
    Return the supplied string with its first letter capitalized.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.capitalize_first(mystring)


def flatten(items, seqtypes=(list, tuple)):
    """
    Convert an arbitrarily deep nested list into a single flat list.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.flatten(items, seqtypes)


def make_json(data):
    """
    Return json object representing the data provided in dictionary "data".

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.make_json(data)


def load_json(data):
    """
    Read a json object and return as a simple python type object.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.load_json(data)
