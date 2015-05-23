#! /usr/bin/python
# -*- coding:utf-8 -*-

#import argparse
from copy import copy, deepcopy
from gluon import current
#from paideia_utils import Uprinter
from plugin_utils import clr, makeutf8
#from pprint import pprint
import re
#import traceback

"""

Interface:

To set up a grammatical pattern to test against, instantiate one of the Parser
child classes.

NounPhrase(None, Article(), Noun())

"""

wordforms = {'ἀνηρ': {'gender': 'masc',
                      'part_of_speech': 'noun',
                      'number': 'sing',
                      'case': 'nominative'},
             'ἀρτον': {'gender': 'masc',
                       'part_of_speech': 'noun',
                       'number': 'sing',
                       'case': 'accusative'},
             'ὁ': {'part_of_speech': 'def_art',
                   'gender': 'masc',
                   'number': 'sing',
                   'case': 'nominative'},
             'τον': {'part_of_speech': 'def_art',
                     'gender': 'masc',
                     'number': 'sing',
                     'case': 'accusative'}
             }


def tokenize(str):
    """
    Divide a string into clauses and each clause into word tokens.

    Returns a list of lists, each of which represents one clause
    (or fragment). The members of each list are 2-member tuples including [0] a
    word from the clause, and [1] a dictionary. Each dictionary contains the
    key 'index' with an integer giving the position of the word in the clause.
    These tuples are ordered according to the appearance of the words in the
    original string.

    """
    clauses = re.split(r'[\.\?;:,]', str)
    tokenized = []
    for c in clauses:
        words = c.split(' ')
        token_list = [(unicode(makeutf8(t)), {'index': words.index(t)})
                      for t in words]
        tokenized.append(token_list)
    return tokenized


class Parser(object):
    """
    Abstract class defining basic recursive parsing behaviour.
    """
    myc = 'white'

    def __init__(self, *args):
        """
        Initialize a Parser object.

        restring
        : Test string to be used in regex comparisons for evaluating this
        construction

        structures
        : A list of Parser sub-class objects representing the grammatical
        constructions expected as constituents of this parent construction.
        """
        self.restring = args[0].strip() if args[0] else None
        self.structures = args[1:]
        try:
            self.top = True if self.structures[-1] == 'top' else False
            if self.top:
                self.structures = self.structures[:-1]
        except IndexError:  # because no substructures
            self.structures = None
            self.top = False
        print 'self.structures', self.structures
        print 'self.top', self.top

        self.classname = type(self).__name__

    def filter_pos(self, parts, pos):
        """
        Return a list of leaf tuples filtered based on the desired part of speech.
        """
        mytuples = [p for p in parts if p[1]['pos'] == pos]
        return mytuples

    def modifies(self, leaf, modifier, modified):
        """
        """
        modindex = modifier[1]['index']
        leaf[modindex][1]['modifies'] = modified[1]['index']
        return leaf

    def __enter__(self):
        """ Necessary to use in 'with' condition."""
        return self

    def find_current_parts(self, leaf):
        """
        Return a list of the leaf tuples belonging to the current construction.
        """
        parts = [p for p in leaf
                 if 'current' in p[1].keys() and p[1]['current'] == 0]
        return parts

    def validate(self, validlfs, failedlfs=[]):
        """
        compare list of word tokens to definition of valid natural language expressions.

        clause should be Clause() object
        """
        #print 'in validate: failedlfs in'
        #print Uprinter().uprint(failedlfs)
        #print 'in validate: validlfs in'
        #print Uprinter().uprint(validlfs)
        validlfs = [validlfs] if isinstance(validlfs[0], tuple) else validlfs
        # validate constituent structures recursively
        if self.structures:
            for s in self.structures:
                print 'validating', s
                validlfs, failedlfs = s.validate(validlfs, failedlfs)
                if len(validlfs) < 1:
                    print 'failed while validating', s
                    return validlfs, failedlfs

        # find matching string for remaining viable leaves
        if self.restring:
            print 'checking for restring', makeutf8(self.restring)
            validlfs, failedlfs = self.match_string(validlfs, failedlfs)
            if len(validlfs) < 1:  # no valid leaves, validation fails
                return validlfs, failedlfs

        # test sub-structure order for any viable leaves
        if self.structures:
            validlfs, failedlfs = self.test_order(validlfs, failedlfs)
            if len(validlfs) < 1:  # no valid leaves, validation fails
                return validlfs, failedlfs

        # find any untagged words if this structure is top level
        # if found, validation fails
        if self.top:
            for v in validlfs:
                for w in v: print w,
                print ''
            for idx, leaf in enumerate(validlfs):
                untagged = [t for t in leaf if 'pos' not in t[1].keys()]
                if untagged:
                    failedlfs.append(validlfs.pop(idx))
                    print clr(['some extra words left over'], self.myc)
                    for w in untagged: print w
            if not validlfs:
                return validlfs, failedlfs
            else:
                pass

        return validlfs, failedlfs

    '''
    def strip_current_flags(self, validlfs, failedlfs):
        """
        """
        newvalids = []
        newfaileds = []
        for v in validlfs:
            for idx, part in enumerate(v):
                try:
                    del v[idx][1]['current']
                except KeyError:
                    pass
            newvalids.append(copy(v))
        for f in failedlfs:
            for idx, part in enumerate(v):
                try:
                    del f[idx][1]['current']
                except KeyError:
                    pass
            newfaileds.append(copy(f))
        return newvalids, newfaileds
    '''

    def match_string(self, validleaves, failedleaves,
                     restring=None, classname=None):
        '''
        Identify token strings that match the current construction.

        validleaves
        : An OrderedDict with the words as keys and dictionaries (or None) for
        values. The dictionaries may have the keys 'pos' (str, classname for
        a part of speech) and 'modifies' (int, index of another word modified
        by this one).
        '''
        restring = unicode(makeutf8(self.restring)) if not restring \
            else unicode(makeutf8(restring))
        classname = self.classname if not classname else classname

        test = re.compile(restring, re.U | re.I)
        print 'restring is', restring, type(restring)
        validleaves = validleaves if isinstance(validleaves[0], list) \
            else [validleaves]
        validstring = ' '.join([i[0] for i in validleaves[0]])
        print 'validstring is', validstring, type(validstring)
        mymatch = test.findall(validstring)
        print 'mymatch is'
        for m in mymatch:
            print makeutf8(m)

        def tag_token(matchstring, leafcopy):
            print 'in tag_token---------------------------'
            print 'matchstring:', matchstring
            matchindex = [l[1]['index'] for l in leafcopy
                          if l[0] == matchstring][0]
            print 'matchindex:', matchindex
            mydict = leafcopy[matchindex][1]
            if 'pos' not in mydict.keys():  # only tag word if currently untagged
                mydict['pos'] = classname
                if 'current' in mydict.keys():
                    mydict['current'] += 1
                else:
                    mydict['current'] = 0
                print 'tagged as:', classname
                print leafcopy
            else:
                print 'already tagged, leaf invalid'
                return False
            return leafcopy

        newvalids = []
        newfaileds = []
        if mymatch:
            print 'mymatch', mymatch
            for leaf in validleaves:
                print 'tagging leaf:', leaf
                for m in mymatch:
                    if m in [w[0] for w in leaf]:  # because findall and case
                        print 'tagging leaf with', makeutf8(m), '==============='
                        taggedleaf = tag_token(m, deepcopy(leaf))
                        if taggedleaf and taggedleaf not in newvalids:
                            print 'appending valid leaf'
                            newvalids.append(taggedleaf)
                        elif not taggedleaf and leaf not in newfaileds:
                            print 'appending failed leaf'
                            newfaileds.append(leaf)
                        else:
                            print 'leaf is duplicate'
                    else:
                        print 'match', m, 'is not in string'
                        pass
        else:
            print 'no match'
            newfaileds.extend(validleaves[:])

        return newvalids, newfaileds

    def test_order(self, validleaves, failedleaves):
        """ """
        return validleaves, failedleaves

    def before(self, prior, latter):
        """
        Return True if prior tuple comes before latter in their leaf.
        """
        if prior[1]['index'] < latter[1]['index']:
            return True
        else:
            return False

    def after(self, latter, prior):
        """
        Return True if latter tuple comes after prior in their leaf.
        """
        if prior[1]['index'] < latter[1]['index']:
            return False
        else:
            return True

    def between(self, p1, p2, allow=[], exclude=[], require=[]):
        """
        Test whether any intervening structures are appropriate.
        """
        between = [s for s, v in self.structs.iteritems()
                   if v in range(p1 + 1, p2 - 1)]
        disallowed = [s for s in between
                      if (s not in allow) or (s in exclude)]
        missing = [s for s in require if s not in between]
        fit = False if (disallowed or missing) else True

        return fit

    def agree(self, p1, p2, words):
        """
        Return True if the words at the listed indexes in leaf agree.

        words is a list of the keys from one leaf of validleaves
        """
        print 'Do {} and {} agree?'.format(words[p1], words[p2]),
        parsed = [self.parseform(words[p1]),
                  self.parseform(words[p2])]
        categories = ['gender', 'number', 'case']
        conflicts = [c for c in categories if parsed[0][c] != parsed[1][c]]
        agreement = False if conflicts else True

    def parseform(self, token):
        """
        Return a dictionary holding the grammatical information for the token.
        """
        db = current.db
        formrow = db.word_forms(db.word_forms.word_form == token).as_dict()
        lemmarow = db.lemmas(formrow.source_lemma)
        formrow['part_of_speech'] = lemmarow['part_of_speech']
        return formrow, lemmarow.id

    def getform(self, **kwargs):
        """
        Return a list of possible declined forms for the supplied parsing.
        """
        db = current.db
        myform = db().select(**kwargs)
        return myform.as_dict()

    def __exit__(self, type, value, traceback):
        """
        Necessary for use in 'with' condition.
        """
        print 'destroying instance'


class Clause(Parser):
    """ """
    reqs = ['Verb']


class VerblessClause(Parser):
    """ """
    reqs = ['Subject', 'Complement']


class Verb(Parser):
    myc = 'orange'
    """
    """
    reqs = []


class NounPhrase(Parser):
    myc = 'lightcyan'

    def __init__(self, *args):
        """
        """
        if 'def' in args:
            self.definite = True
        elif 'def?' in args:
            self.definite = 'maybe'

    def find_agree(self, refword, pos):
        """
        """
        db = current.db
        if pos == 'article':
            parsing, lemid = self.parseform(refword)
            artlemid = db(db.lemmas.lemma == 'ὁ').select(db.lemmas.id)
            argdict = {'lemma': artlemid.id,
                       'grammatical_case': parsing['grammatical_case'],
                       'gender': parsing['gender'],
                       'number': parsing['number']}
            artform = self.getform(argdict)
            myword = artform['word_form']
        return myword

    def test_order(self, validlfs, failedlfs):
        """
        """
        newvalids = []
        newfaileds = []

        # Does article precede its noun? If so mark as modifying that noun
        if self.definite:
            print 'phrase is definite, checking order'
            for leaf in validlfs:
                parts = self.find_current_parts(leaf)
                mynoun = self.filter_pos(parts, 'Noun')[0]
                artform = self.find_agree(mynoun, 'article')

                print 'parts', parts  # problem is 'current' stripped
                myarts = self.filter_pos(parts, 'Art')
                for art in myarts:
                    newleaf = copy(leaf)
                    if self.before(art, mynoun):
                        # record modification link
                        newleaf = self.modifies(newleaf, art, mynoun)
                        if newleaf not in newvalids:
                            newvalids.append(newleaf)
                    elif newleaf not in newfaileds:
                        newfaileds.append(newleaf)

        return newvalids, newfaileds


class DirObject(NounPhrase):
    myc = 'lightred'
    """
    """
    pass


class IndirObject(NounPhrase):
    """
    """
    pass


class Subject(NounPhrase):
    """
    """
    pass


class DatPhrase(NounPhrase):
    """
    """


class Noun(Parser):
    """
    Definiteness ambiguous.
    """
    pass


class Art(Parser):
    """
    """
    pass


class Adjective(Parser):
    pass

'''
def main(string, pattern):
    """Take the  strings in 'strings' variable and validate them."""
    result = None
    tokenset = [token for token in tokenize(string)
                if token.keys()[0] not in ['', ' ', None]]
    for tokens in tokenset:
        p = eval(pattern) if not isinstance(pattern, Clause) else pattern
        # put tokens in list to prepare for parsing tree forking
        validleaves, failedleaves = p.validate([tokens])
        if validleaves:
            result = 'pass'
        else:
            result = 'fail'
        myc = 'green' if validleaves else 'red'
        resp = 'Success!' if validleaves else 'Failed'
        print clr([resp, '(', string ,')', '\n'], myc)
    print '============================================================='

    return result
'''

'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('string', help='the string to be evaluated')
    parser.add_argument('pattern', help='the pattern against which to evaluate the string')
    args = parser.parse_args()
    main(args.string, args.pattern)
'''
