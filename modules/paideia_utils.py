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
import datetime

"""
def simple_obj_print(the_dict, title='No Title', indentation=0):
"""
"""
    Prints a simple thing
    Joseph Boakye jboakye@bwachi.com
"""
"""
    indentation_string = ' '*indentation
    if (None == the_dict):
        print indentation_string  + '{' + str(title) + ': '  + '-None-' +  '}'
        return
    while True:
        #dictionaries
        if ( (type(the_dict) == type({})) | isinstance(the_dict, Storage)):
            print indentation_string  + str(title) + '(dict):'
            for key in the_dict:
                simple_obj_print(the_dict[key],key,indentation+1)
            break
        #lists
        if ( (hasattr(the_dict, '__iter__')) |isinstance(the_dict, StorageList)) :
            print indentation_string  + str(title) + '(list):'
            count = 0
            try:
                for value in the_dict:
                    simple_obj_print(value, count,indentation+1)
                    count +=1
            except TypeError, te:
                simple_obj_print("list is not iterable",count,indentation+1)
            break
        #simple item
        while True:
            if type(the_dict) is datetime.datetime:
                print indentation_string  + '{' + str(title) + ': ' +  \
                     the_dict.strftime('%Y %m %d %H %M %S %f') +  '}'
                break
            print indentation_string  + '{' + str(title) + ': '  +  str(the_dict) +  '}'
            break
        break
"""
def simple_obj_print(the_dict, title='No Title', indentation=0):
    output_obj = {'data': ''}
    simple_obj_print_str(output_obj, the_dict, title, indentation)
    print output_obj['data']

def simple_obj_print_str(output_obj, the_dict, title='No Title', indentation=0, doing_what='S'):
    """
    Prints a simple thing ... same as simple_obj_print but print into string
    Joseph Boakye jboakye@bwachi.com
    """
    indentation_string = ' '*indentation
    scalar_beg = ''
    scalar_end = ''
    if doing_what in ('L', 'D' ):
        scalar_beg = '<li>'
        scalar_end = '</li>'
    if (None == the_dict):
        output_obj['data'] +=  indentation_string + scalar_beg + '<p>' + '{' + str(title) + ': '  + '-None-' +  '}' + '</p>' +  scalar_end
        return
    while True:
        #dictionaries
        if ( (type(the_dict) == type({})) | isinstance(the_dict, Storage)):
            output_obj['data'] +=  (indentation_string  + str(title) + '(dict:)' + '<ol title="dict">')
            for key in the_dict:
                #output_obj['data'] +=  (indentation_string  + '<li>')
                simple_obj_print_str(output_obj,the_dict[key],key,indentation+1,'D')
                #output_obj['data'] +=  (indentation_string  + '</li>')
            output_obj['data'] +=  (indentation_string  + '</ol>')
            break

        #lists
        if ( (hasattr(the_dict, '__iter__')) |isinstance(the_dict, StorageList)) :
            output_obj['data'] +=  (indentation_string  + str(title) + '(list:)' + '<ol title="list">')
            count = 0
            try:
                for value in the_dict:
                    #output_obj['data'] +=  (indentation_string  + '<li>')
                    simple_obj_print_str(output_obj,value, count,indentation+1,'L')
                    #output_obj['data'] +=  (indentation_string  + '</li>')
                    count +=1
            except TypeError, te:
                simple_obj_print_str(output_obj,"list is not iterable",count,indentation+1)
                output_obj['data'] +=  (indentation_string  + '</li>')
            output_obj['data'] +=  (indentation_string  + '</ol>')
            break
        #simple item
        while True:
            if type(the_dict) is datetime.datetime:
                output_obj['data'] +=   (indentation_string  + scalar_beg + '<p>' + '{' + str(title) + ': ' +  \
                     the_dict.strftime('%Y %m %d %H %M %S %f') +  '}' + '</p>' +  scalar_end)
                break
            output_obj['data'] +=  ( indentation_string + scalar_beg + '<p>' + '{' + str(title) + ': '  +  str(the_dict) +  '}' + '</p>' +  scalar_end)
            break
        break



class Paideia_Debug(object):
    """
    Carry debug information to the screen
    JOB ... oct 22, 2014
    """
    def __init__(self):
        """
        """
        self.data = 'Debug Enabled'

    def do_print(self, the_object,the_title):
        data_obj = dict(data='');
        simple_obj_print_str(data_obj, the_object, the_title, 0)
        self.data += data_obj['data']


def uprint(myobj):
    """
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
    #print prettystring
    return prettystring


def uprint_dict(mydict, lvl=0, html=False):
    """
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


def islist(dat):
    """
    Return the supplied object converted to a list if it is not already.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.islist(dat)


def sanitize_greek(strings):
    """
    Check for latin characters mixed with Greek.
    """
    try:
        newstrings = []
        for string in strings:
            string = makeutf8(string)
            rgx = makeutf8(r'(?P<a>[Α-Ωα-ω])?([a-z]|[A-Z]|\d)(?(a).*|[Α-Ωα-ω])')
            #print 'filterrgx ==============================='
            #print rgx
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
            #print 'newstring is ============================'
            #print newstring
            newstrings.append(newstring)
        return newstrings
    except Exception:
        print traceback.format_exc(12)


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


def makeutf8(rawstring):
    """
    Return the string decoded as utf8 if it wasn't already.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.makeutf8(rawstring)


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


def test_regex(regex, readables):
    """
    Return a re.match object for each given string, tested with the given regex.

    The "readables" argument should be a list of strings to be tested.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
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


def flatten(items, seqtypes=(list, tuple)):
    """
    Convert an arbitrarily deep nested list into a single flat list.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.flatten(items, seqtypes)


def send_error(myclass, mymethod, myrequest):
    """
    Send an email reporting error and including debug info.

    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    plugin_utils.send_error(myclass, mymethod, myrequest)


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


def normalize_accents(strings):
    """
    Return a polytonic Greek unicode string with accents removed.

    The one argument should be a list of strings to be normalized. It can
    also handle a single string.

    So far this function only handles lowercase strings.
    """
    if not isinstance(strings, list):
        strings = [strings]

    equivs = {'α': ['ά', 'ὰ', 'ᾶ'],
              'ἀ': ['ἄ', 'ἂ', 'ἆ'],
              'ἁ': ['ἅ', 'ἃ', 'ἇ'],
              'ᾳ': ['ᾷ', 'ᾲ', 'ᾴ'],
              'ᾀ': ['ᾄ', 'ᾂ', 'ᾆ'],
              'ᾁ': ['ᾅ', 'ᾃ', 'ᾇ'],
              'ε': ['έ', 'ὲ'],
              'ἐ': ['ἔ', 'ἒ'],
              'ἑ': ['ἕ', 'ἓ'],
              'η': ['ῆ', 'ή', 'ὴ'],
              'ἠ': ['ἤ', 'ἢ', 'ἦ'],
              'ἡ': ['ἥ', 'ἣ', 'ἧ'],
              'ῃ': ['ῇ', 'ῄ', 'ῂ'],
              'ᾐ': ['ᾔ', 'ᾒ', 'ᾖ'],
              'ᾑ': ['ᾕ', 'ᾓ', 'ᾗ'],
              'ι': ['ῖ', 'ϊ', 'ί', 'ὶ'],
              'ἰ': ['ἴ', 'ἲ', 'ἶ'],
              'ἱ': ['ἵ', 'ἳ', 'ἷ'],
              'ο': ['ό', 'ὸ'],
              'ὀ': ['ὄ', 'ὂ'],
              'ὁ': ['ὅ', 'ὃ'],
              'υ': ['ῦ', 'ϋ', 'ύ', 'ὺ'],
              'ὐ': ['ὔ', 'ὒ', 'ὖ'],
              'ὑ': ['ὕ', 'ὓ', 'ὗ'],
              'ω': ['ῶ', 'ώ', 'ὼ'],
              'ὠ': ['ὤ', 'ὢ', 'ὦ'],
              'ὡ': ['ὥ', 'ὣ', 'ὧ'],
              'ῳ': ['ῷ', 'ῴ', 'ῲ'],
              'ᾠ': ['ᾤ', 'ᾢ', 'ᾦ'],
              'ᾡ': ['ᾥ', 'ᾣ', 'ᾧ'],
              }
    accented = chain(*equivs.values())
    restr = '|'.join(accented)
    newstrings = []
    for mystring in strings:
        if mystring not in ['τίνος', 'τί', 'τίς', 'τίνα', 'τίνας', 'τίνι']:
            search = re.search(restr, mystring)
            if search:
                matching_letters = search.group()  # could be multiple
                # get relevant subset of equivs dictionary
                edict = {k: v for k, v in equivs.iteritems()
                        if [m for m in v if m in matching_letters]}
                # eliminate absent accented letters from values
                for k, v in edict.iteritems():
                    edict[k] = [l for l in v if l in matching_letters]
                    pairs = edict.items()
                    for idx, p in enumerate(pairs):
                        if len(p[1]) > 1:  # handle multiple matching values
                            newpairs = [(v, p[0]) for v in p[1][1:]]
                            pairs.extend(newpairs)
                        pairs[idx] = (p[1][0], p[0])
                newstrings.append(multiple_replace(mystring, *pairs))
            else:
                newstrings.append(mystring)
        else:
            newstrings.append(mystring)
        #myloc = locale.getdefaultlocale()
        # TODO: get alphabetical sorting working here
        #print 'default locale is', myloc
        #locale.setlocale(locale.LC_ALL, 'el_GR.UTF-8')
        newstrings = sorted(newstrings)
        #locale.setlocale(locale.LC_ALL, myloc)
    return newstrings


def gather_vocab():
    """
    Return a list of all Greek words used in steps.
    """
    db = current.db
    steps = db(db.steps.id > 0).select()

    words = []
    for s in steps:
        regex = re.compile(u'[^\w\.,\?!\"\'\-\*\s\|\<\>;\(\)\\\:\[\]\/]+')
        strings = ' '.join([s.prompt, s.readable_response])
        words.extend(regex.findall(strings))
    lower_words = [w.decode('utf-8').lower().encode('utf-8') for w in words]
    normal_words = normalize_accents(lower_words)
    unique_words = list(set(normal_words))
    x = ['πιλ', 'βοδυ', 'μειδ', 'νηλ', 'ἰλ', 'σαγγ', 'ἁμ', 'ἱτ', 'ἑλπ', 'ἑλω', 'ο',
         'βοτ', 'ὁλ', 'ὁγ', 'παθ', 'τιψ', 'β', 'σωλ', 'κορπ', 'ὡλ', 'κατς', 'γγς',
         'μωλτεγγ', 'δεκ', 'φιξ', 'βαλ', 'διλ', 'δαξ', 'δρομα', 'δακ', 'δαγ', 'ἁγ',
         'λοξ', 'δυδ', 'βωθ', 'ὐψ', 'καν', 'καβ', 'ὀτ', 'βαδ', 'μωστ', 'μοισδ',
         'μιλ', 'βελ', 'ἑδ', 'θοτ', 'κιλ', 'κρω', 'βοχ', 'ω', 'μεντ', 'ἁτ', 'νεατ',
         'σπηρ', 'βοδι', 'πιτ', 'βονδ', 'ἁρδ', 'δοκς', 'μελτ', 'βεδ', 'μαλ', 'δατς',
         'σωπ', 'α', 'πενσιλ', 'κς', 'δεκς', 'αριας', 'βαγγ', 'σετ', 'βρουμ', 'ἀδ',
         'πωλ', 'δατ', 'ἁγγ', 'πραυδ', 'αὐτης', 'νειλ', 'σογγ', 'ζαπ', 'κλαδ',
         'νιτ', 'φαξ', 'βολ', 'κεπτ', 'μοιστ', 'ἁμερ', 'τουνα', 'προγγ', 'τ',
         'κλυν', 'λοβ', 'πλειαρ', 'κροπ', 'βανδ', 'μωλτεν', 'υτ', 'κοτ', 'κοπ',
         'ἀτ', 'φυξ', 'ὡλι', 'μυτ', 'θατ', 'δοτ', 'βικς', 'ἁμαρ', 'λωφερ', 'δοκ',
         'ταπ', 'ἀβωδ', 'ὑτος', 'λωφρ', 'ἁμρ', 'ροκ', 'πς', 'βαδυ', 'οὐψ', 'πραγγ',
         'σπειρ', 'ἀγγλ', 'σλαψ', 'πλαυ', 'δραμα', 'φοξ', 'ἱτεδ', 'ὁτ', 'δογ',
         'δολ', 'ρω', 'δοξ', 'ὗτος', 'μιτ', 'αὑ', 'ἱτς', 'μωλτ', 'βατ', 'βαχ',
         'βικ', 'μιαλ', 'μολ', 'μιελ', 'κον', 'μωισδ', 'κραπ', 'καπ', 'ὑπ', 'ἀγκλ',
         'λιξ', 'ρωλ', 'λαβ', 'ὀδ', 'λαξ', 'δοτς', 'ἀνκλ', 'ρακ', 'πεγ', 'τυνα',
         'βρυμ', 'καρπ', 'βρεδ', 'κιπ', 'μηδ', 'δαλ', 'βετ', 'διπ', 'κλιν', 'πετ',
         'βαδι', 'λικς', 'δακς']
    mywords = [l for l in unique_words if not l in x]
    mywords_dict = {}
    dups_dict = {}
    for word in mywords:
        dup = db(db.word_forms.word_form == word).select()
        if dup:
            dups_dict[word] = dup[0].id
        else:
            newindex = db.word_forms.insert(word_form=word)
            mywords_dict[word] = newindex

    return mywords_dict, dups_dict


def multiple_replace(string, *key_values):
    """
    DEPRECATED IN FAVOUR OF PLUGIN_UTILS VERSION
    """
    return plugin_utils.multiple_replacer(string, *key_values)
