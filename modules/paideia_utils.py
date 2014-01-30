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
#from plugin_ajaxselect import AjaxSelect
import re
from itertools import chain
#from pprint import pprint
import datetime
import json


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
    """
    if not isinstance(dat, list):
        dat = [dat]
    return dat


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
    """
    col = {'white': '\033[95m',
           'blue': '\033[94m',
           'green': '\033[92m',
           'orange': '\033[93m',
           'red': '\033[91m',
           'lightblue': '\033[1;34m',
           'lightgreen': '\033[1;32m',
           'lightcyan': '\033[1;36m',
           'lightred': '\033[1;31m',
           'lightpurple': '\033[1;35m',
           'white': '\033[1;37m',
           'endc': '\033[0m'
           }
    thecol = col[mycol]
    endc = col['endc']
    if isinstance(string, list):
        try:
            string = ' '.join(string)
        except TypeError:
            string = ' '.join([str(s) for s in string])

    newstring = '{}{}{}'.format(thecol, string, endc)
    return newstring


def printutf(string):
    """Convert unicode string to readable characters for printing."""
    string = makeutf8(string)
    return string


def capitalize(letter):
    """
    Convert string to upper case in utf-8 safe way.
    """
    letter = makeutf8(letter)
    newletter = letter.upper()
    return newletter


def lowercase(letter):
    """
    Convert string to lower case in utf-8 safe way.
    """
    letter = makeutf8(letter)
    newletter = letter.lower()
    return newletter


def makeutf8(rawstring):
    """Return the string decoded as utf8 if it wasn't already."""
    try:
        rawstring = rawstring.decode('utf8')
    except (UnicodeEncodeError, UnicodeDecodeError):  # if already decoded
        #try:
            #rawstring = rawstring.encode('utf8').decode('utf8')
        #except Exception:
            #print 'encountered unicode error in makeutf8'
        rawstring = rawstring
    except (AttributeError, TypeError):  # if rawstring is NoneType
        rawstring = 'None'
    return rawstring


def firstletter(mystring):
    """
    Find the first letter of a byte-encoded unicode string.
    """
    mystring = makeutf8(mystring)
    let, tail = mystring[:1], mystring[1:]
    #print 'in firstletter: ', mystring[:1], '||', mystring[1:]
    #let, tail = let.encode('utf8'), tail.encode('utf8')
    return let, tail


def capitalize_first(mystring):
    """
    Return the supplied string with its first letter capitalized.
    """
    first, rest = firstletter(mystring)
    first = capitalize(first)
    newstring = first + makeutf8(rest)
    return newstring


def test_regex(regex, readables):
    """
    Return a re.match object for each given string, tested with the given regex.

    The "readables" argument should be a list of strings to be tested.
    """
    print 'testing regex ====================================='
    uprint(regex)
    readables = islist(readables)
    test_regex = re.compile(makeutf8(regex), re.I | re.U)
    rdict = {}
    for rsp in readables:
        match = re.match(test_regex, makeutf8(rsp))
        #print 'string is--------------------------------------'
        #print rsp
        #print 'match is --------------------------------------'
        #print match
        #if match:
            #print 'if match:', True
        #else:
            #print 'if match:', False
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
    """
    for i, x in enumerate(items):
        try:
            while isinstance(items[i], seqtypes):
                items[i:i + 1] = items[i]
        except IndexError:
            continue
    return items


def send_error(myclass, mymethod, myrequest):
    """ Send an email reporting error and including debug info. """
    mail = current.mail
    msg = '<html>A user encountered an error in {myclass}.{mymethod}' \
          'report failed.\n\nTraceback: {tb}' \
          'Request:\n{rq}\n' \
          '</html>'.format(myclass=myclass,
                           mymethod=mymethod,
                           tb=traceback.format_exc(5),
                           rq=myrequest)
    title = 'Paideia error'
    mail.send(mail.settings.sender, title, msg)


def make_json(data):
    """
    Return json object representing the data provided in dictionary "data".
    """
    date_handler = lambda obj: obj.isoformat() \
        if isinstance(obj, datetime.datetime) else None
    myjson = json.dumps(data,
                        default=date_handler,
                        indent=4,
                        sort_keys=True)
    return myjson


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


def multiple_replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


def multiple_replace(string, *key_values):
    return multiple_replacer(*key_values)(string)
