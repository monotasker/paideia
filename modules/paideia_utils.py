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
from gluon import SPAN
#from plugin_ajaxselect import AjaxSelect
import re
from itertools import chain
#from pprint import pprint
import datetime
import json

caps = {'α': 'Α',
        'ἀ': 'Ἀ',
        'ἁ': 'Ἁ',
        'β': 'Β',
        'γ': 'Γ',
        'δ': 'Δ',
        'ε': 'Ε',
        'ἐ': 'Ἐ',
        'ἑ': 'Ἑ',
        'ζ': 'Ζ',
        'η': 'Η',
        'ἠ': 'Ἠ',
        'ἡ': 'Ἡ',
        'θ': 'Θ',
        'ι': 'Ι',
        'ἰ': 'Ἰ',
        'ἱ': 'Ἱ',
        'κ': 'Κ',
        'λ': 'Λ',
        'μ': 'Μ',
        'ν': 'Ν',
        'ξ': 'Ξ',
        'ο': 'Ο',
        'ὀ': 'Ὀ',
        'ὁ': 'Ὁ',
        'π': 'Π',
        'ρ': 'Ρ',
        'σ': 'Σ',
        'τ': 'Τ',
        'υ': 'Υ',
        'ὐ': 'ὐ',
        'ὑ': 'Ὑ',
        'φ': 'Φ',
        'χ': 'Χ',
        'ψ': 'Ψ',
        'ω': 'Ω',
        'ὠ': 'Ὠ',
        'ὡ': 'Ὡ'}


def sanitize_greek(strings):
    """
    Check for latin characters mixed with Greek.
    """
    try:
        newstrings = []
        for string in strings:
            latin = re.compile(ur'(?P<a>[Α-Ωα-ω])?([a-z]|[A-Z]|\d)(?(a).*|[Α-Ωα-ω])')
            mymatch = re.search(latin, string.decode('utf-8'))
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
        print traceback.format_exc(5)


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
    string = string.decode('utf-8').encode('utf-8')
    return string


def capitalize(letter):
    """
    Convert string to upper case in utf-8 safe way.
    """
    #if letter in caps.values():
    newletter = letter.decode('utf-8').upper()
    return newletter.encode('utf-8')


def lowercase(letter):
    """
    Convert string to lower case in utf-8 safe way.
    """
    newletter = string.decode('utf-8').lower()
    return newletter.encode('utf-8')


def firstletter(mystring):
    """
    Find the first letter of a byte-encoded unicode string.
    """
    mystring = mystring.decode('utf-8')
    let, tail = mystring[:1], mystring[1:]
    #print 'in firstletter: ', mystring[:1], '||', mystring[1:]
    let, tail = let.encode('utf-8'), tail.encode('utf-8')
    return let, tail


def capitalize_first(mystring):
    """
    Return the supplied string with its first letter capitalized.
    """
    first, rest = firstletter(mystring)
    newstring = '{}{}'.format(capitalize(first), rest)
    return newstring


def test_regex(regex, readables):
    """
    Return a re.match object for each given string, tested with the given regex.

    The "readables" argument should be a list of strings to be tested.
    """
    readables = readables if type(readables) == list else [readables]
    test_regex = re.compile(regex, re.I | re.U)
    rdict = {}
    for rsp in readables:
        match = re.match(test_regex, rsp)
        rdict[rsp] = SPAN('PASSED', _class='success') if match \
            else SPAN('FAILED', _class='success')
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


def flatten(self, items, seqtypes=(list, tuple)):
    """
    Convert an arbitrarily deep nested list into a single flat list.
    """
    for i, x in enumerate(items):
        while isinstance(items[i], seqtypes):
            items[i:i + 1] = items[i]
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
