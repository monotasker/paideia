#! /usr/bin/python
# -*- coding:utf-8 -*-

#import argparse
from copy import deepcopy
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
        tokenized.append({0: token_list})
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
        self.matching_words = []

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

    def find_child_words(self):
        """
        """
        if self.structures:
            mywords = []
            for s in self.structures:
                myname = type(s).__name__
                struct_words = s.matching_words
                mywords.append([myname, struct_words])
            print 'finding child words'
            print mywords
            return mywords
        else:
            return None

    def find_current_parts(self, leaf):
        """
        Return a list of the leaf tuples belonging to the current construction.
        """
        parts = [p for p in leaf
                 if 'current' in p[1].keys() and p[1]['current'] == 0]
        return parts

    def validate(self, validlfs, failedlfs={}):
        """
        compare list of word tokens to definition of valid natural language expressions.

        clause should be Clause() object
        """
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
            for v in validlfs.values():
                for w in v: print w,
                print ''
            for idx, leaf in validlfs.iteritems():
                untagged = [t for t in leaf if 'pos' not in t[1].keys()]
                if untagged:
                    failedlfs[idx] = validlfs[idx]
                    validlfs = {k: v for k, v in validlfs.iteritems() if k != idx}
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

        validstring = ' '.join([i[0] for i in validleaves[0]])
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

        newvalids = {}
        newfaileds = {}
        if mymatch:
            print 'mymatch', mymatch
            for key, leaf in validleaves.iteritems():
                print 'tagging leaf:', leaf
                for m in mymatch:
                    if m in [w[0] for w in leaf]:  # because findall and case
                        print 'tagging leaf with', makeutf8(m), '==============='
                        taggedleaf = tag_token(m, deepcopy(leaf))
                        if taggedleaf and taggedleaf not in newvalids.values():
                            if key in newvalids.keys():
                                newkey = max(newvalids.keys()) + 1
                            else:
                                newkey = key
                            print 'appending valid leaf', newkey
                            newvalids[newkey] = taggedleaf
                            self.matching_words.append([classname, m, key])
                        elif not taggedleaf and leaf not in newfaileds.values():
                            if key in newfaileds.keys():
                                newkey = max(newfaileds.keys()) + 1
                            else:
                                newkey = key
                            print 'appending failed leaf', newkey
                            newfaileds[newkey] = leaf
                        else:
                            print 'leaf is duplicate'
                    else:
                        print 'match', m, 'is not in string'
                        pass
        else:
            print 'no match'
            newfaileds = deepcopy(validleaves)
            newvalids = {}

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

    def find_agree(self, refword, pos=None, lemma=None):
        """
        Return the form of the specified lemma that agrees with the refword.
        """
        db = current.db
        if pos == 'article':
            parsing = self.parseform(refword)
            print 'parsing'
            print parsing
            artlemid = db(db.lemmas.lemma == 'ὁ').select(db.lemmas.id).first().id
            print 'artlemid', artlemid
            argdict = {'source_lemma': artlemid,
                       'grammatical_case': parsing['grammatical_case'],
                       'gender': parsing['gender'],
                       'number': parsing['number']}
            print 'argdict'
            print argdict
            myword = self.getform(argdict)
        return myword

    def parseform(self, token):
        """
        Return a dictionary holding the grammatical information for the token.
        """
        db = current.db
        try:
            formrow = db.word_forms(db.word_forms.word_form == token).as_dict()
        except AttributeError:
            formrow = db.word_forms(db.word_forms.word_form == token.lower()).as_dict()

        lemmarow = db.lemmas(formrow['source_lemma'])
        formrow['part_of_speech'] = lemmarow['part_of_speech']
        return formrow

    def getform(self, kwargs, db=None):
        """
        Return a list of possible declined forms for the supplied parsing.
        """
        db = current.db if not db else db
        tbl = db['word_forms']
        query = tbl.id > 0
        for k, v in kwargs.iteritems():
            query &= tbl[k] == v
        print 'query in getform'
        print query
        myforms = db(query).select()
        forms = [row['word_form'] for row in myforms]
        if len(forms) == 1:
            forms = forms[0]
        elif not forms:
            forms = None
        print forms
        return forms

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
            args = [a for a in args if a != 'def']
        elif 'def?' in args:
            self.definite = 'maybe'
            args = [a for a in args if a != 'def?']
        else:
            self.definite = False

        super(NounPhrase, self).__init__(*args)

    def match_article(self, artform, leaf):
        """
        """
        tokenstring = ' '.join([w[0] for w in leaf])
        pattern = re.compile(artform, re.I | re.U)
        arts = pattern.findall(tokenstring)
        return arts

    def test_order(self, validlfs, failedlfs):
        """
        """
        newvalids = {}
        newfaileds = {}

        # Does article precede its noun? If so mark as modifying that noun
        if self.definite:
            child_words = self.find_child_words()
            # find and tag article in valid leaves
            print 'phrase is definite, checking order'
            for key, leaf in validlfs.iteritems():
                mynouns = [c for c in child_words if c[0] == 'Noun'][0]
                print 'mynouns'
                print mynouns
                mynoun = mynouns[0][1][key]
                artform = self.find_agree(mynoun, 'article')
                myarts = self.match_article(artform, leaf)
                # tag any valid articles
                if myarts:
                    for art in myarts:
                        validlfs, failedlfs = self.match_string(validlfs,
                                                                failedlfs,
                                                                restring=art)
            # FIXME: what about optional article?
            # now check article-noun order in successful leaves
            for key, leaf in validlfs.iteritems():
                newleaf = deepcopy(leaf)
                if self.before(art, mynoun):
                    # record modification link
                    newleaf = self.modifies(newleaf, art, mynoun)
                    if newleaf not in newvalids:
                        newkey = max(newvalids.keys()) + 1 \
                            if newvalids.keys() else 0
                        newvalids[key] = newleaf
                elif newleaf not in newfaileds:
                    newkey = max(newfaileds.keys()) + 1 \
                        if newfaileds.keys() else 0
                    newfaileds[key] = newleaf

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
