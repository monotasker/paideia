#! /usr/bin/python3.6
# -*- coding:utf-8 -*-

# import argparse
from copy import deepcopy, copy
from gluon import current
# from paideia_utils import Uprinter
from plugin_utils import clr, makeutf8
# from pprint import pprint
import re
# import traceback

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

LEAFINDEX = 0


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
        token_list = [(t, {'index': words.index(t)}) for t in words]
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
        self.restring = args[0] if args[0] else None
        self.structures = args[1:]
        try:
            self.top = True if self.structures[-1] == 'top' else False
            if self.top:
                self.structures = self.structures[:-1]
        except IndexError:  # because no substructures
            self.structures = None
            self.top = False
        print('self.structures', self.structures)
        print('self.top', self.top)
        self.matching_words = {}

        self.classname = type(self).__name__

    def __enter__(self):
        """ Necessary to use in 'with' condition."""
        return self

    def validate(self, validlfs, failedlfs={}):
        """
        compare ordered list of word tokens to definition of valid natural
        language expressions.

        clause should be Clause() object
        """
        matching_words = self.matching_words if self.matching_words else {}

        print('restring is', self.restring)
        # validate constituent structures recursively
        if self.structures:
            for s in self.structures:
                print('validating', s)
                validlfs, failedlfs, mw = s.validate(validlfs,
                                                     failedlfs=failedlfs)
                if len(validlfs) < 1:
                    print('failed while validating', s)
                    return validlfs, failedlfs, matching_words
                for k, wrd in mw.items():
                    if k in matching_words.keys():
                        matching_words[k].extend(wrd)
                    else:
                        matching_words[k] = wrd

        # find matching string for remaining viable leaves
        if self.restring:
            # need to compare with newly parsed to find newly added words
            old_validlfs = copy(validlfs)
            print('checking for restring', self.restring)
            validlfs, failedlfs, mw = self.match_string(validlfs, failedlfs)
            for k, wrd in mw.items():
                if k in matching_words.keys():
                    matching_words[k].extend(wrd)
                else:
                    matching_words[k] = wrd
            if len(validlfs) < 1:  # no valid leaves, validation fails
                return validlfs, failedlfs, matching_words

        # test sub-structure order for any viable leaves
        if self.structures:
            validlfs, failedlfs = self.test_agreement(validlfs,
                                                      failedlfs,
                                                      matching_words)
            validlfs, failedlfs = self.test_order(validlfs,
                                                  failedlfs,
                                                  matching_words)
            if len(validlfs) < 1:  # no valid leaves, validation fails
                return validlfs, failedlfs, matching_words

        # find any untagged words if this structure is top level
        # if found, validation fails
        if self.top:
            for v in list(validlfs.values()):
                for w in v:
                    print(w)
                print('')
            for idx, leaf in validlfs.items():
                untagged = [t for t in leaf if 'pos' not in list(t[1].keys())]
                if untagged:
                    failedlfs[idx] = validlfs[idx]
                    validlfs = {k: v for k, v in validlfs.items() if k != idx}
                    print(clr(['some extra words left over'], self.myc))
                    for w in untagged: print(w)
            if not validlfs:
                return validlfs, failedlfs, matching_words
            else:
                pass

        self.matching_words = matching_words

        return validlfs, failedlfs, matching_words

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

    def tag_token(self, matchindex, key, value, leafcopy, matching):
        '''
        Returns false if the value to be tagged for has already been tagged
        '''
        mydict = leafcopy[matchindex][1]
        if key not in list(mydict.keys()):  # only tag word if untagged
            mydict[key] = value

            if matching:
                myword = leafcopy[matchindex][0]
                for m in matching:
                    if m[0] == myword:
                        m[1][key] = value
        else:
            print('already tagged, leaf invalid')
            return False, None

        return leafcopy, matching

    def match_string(self, validleaves, failedleaves,
                     restring=None, classname=None):
        '''
        Identify token strings that match the current construction.

        This method finds matching tokens in the provided string and adds the
        suitable grammatical information to the analysis if a match is found.
        If more than one match is available in the string, the method creates
        separate "leaves" to pursue the analysis assuming each possibility in
        parallel. If multiple "leaves" are supplied, each is tagged in this
        way. If no matches are available in the string, all valid leaves are
        moved to the dictionary of failed leaves in the return value.

        validleaves
        : A dictionary with indices as keys and OrderedDict objects as values.
        Each OrderedDict represents one construal of the string being
        evaluated. Each one employs the words of the string as keys and
        dictionaries (or None) for values. The dictionaries may have the keys
        'pos' (str, classname for a part of speech) and 'modifies' (int, index
        of another word modified by this one).

        failedleaves
        : A dictionary with the same structure as `validleaves`. This one
        represents the construals of the string that do *not* satisfy the test.

        restring
        : An optional keyword argument allowing direct injection of the regular
        expression to be used for matching.

        classname
        : An optional keyword argument allowing direct injection of the
        classname to be used in tagging matched tokens.
        '''
        global LEAFINDEX
        matching_words = {}
        restring = self.restring if not restring else restring
        classname = self.classname if not classname else classname

        test = re.compile(restring, re.I)

        validstring = ' '.join([i[0] for i in validleaves[0]])
        print('validstring is')
        print(validstring)
        mymatch = test.findall(validstring)
        print('mymatch is')
        print(mymatch)
        for m in mymatch:
            print(m)

        newvalids = {}
        newfaileds = {}
        if mymatch:
            print('mymatch', mymatch)
            for key, leaf in validleaves.items():
                print('tagging leaf:', key, '=============================')
                for m in mymatch:
                    if m in [w[0] for w in leaf]:  # because findall and case
                        print('tagging leaf with', m)
                        matchindex = [l[1]['index'] for l in leaf
                                      if l[0] == m][0]
                        taggedleaf, match = self.tag_token(matchindex, 'pos',
                                                           classname,
                                                           deepcopy(leaf),
                                                           None)
                        if taggedleaf:
                            if key in list(newvalids.keys()):
                                LEAFINDEX += 1
                                key = copy(LEAFINDEX)
                            print('appending valid leaf', key)
                            newvalids[key] = taggedleaf
                            # add matching words (with index) directly to
                            # instance variable
                            new_word = (m, {'pos': classname,
                                            'index': matchindex})
                            if key in matching_words.keys():
                                matching_words[key].append(new_word)
                            else:
                                matching_words[key] = [new_word]
                            print('matching for leaf', key)
                        elif not taggedleaf:
                            if key in list(newfaileds.keys()):
                                LEAFINDEX += 1
                                key = copy(LEAFINDEX)
                            print('appending failed leaf', key)
                            newfaileds[key] = leaf
                        else:
                            print('leaf is duplicate')
                    else:
                        print('match', m, 'is not in string')
                        pass
        else:
            print('no match')
            print(validleaves)
            print(failedleaves)
            if validleaves:
                if failedleaves:
                    newfaileds = validleaves.update(failedleaves)
                else:
                    newfaileds = validleaves
            else:
                newfaileds = failedleaves
            newvalids = {}

        self.matching_words = matching_words

        return newvalids, newfaileds, matching_words

    def test_agreement(self, validleaves, failedleaves, matching_words):
        """ """
        return validleaves, failedleaves

    def test_order(self, validleaves, failedleaves, matching_words):
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
        between = [s for s, v in self.structs.items()
                   if v in range(p1 + 1, p2 - 1)]
        disallowed = [s for s in between
                      if (s not in allow) or (s in exclude)]
        missing = [s for s in require if s not in between]
        fit = False if (disallowed or missing) else True

        return fit

    def agree(self, w1, w2, criteria):
        """
        Return True if the words at the listed indexes in leaf agree.

        words is a list of the keys from one leaf of validleaves
        """
        print('Do {} and {} agree?'.format(w1, w2, end=' '))
        # FIXME: This is going to allow cases where they can agree but the
        # parsing is wrong for this context.
        # print(self.parseform(w1.lower()))
        # print(self.parseform(w2.lower()))
        parsed = [(f, s) for f in self.parseform(w1.lower())
                  for s in self.parseform(w2.lower())]
        conflicts = []
        for p in parsed:
            # for myp in p:
            #     print({i: v for i, v in myp.items() if i in ['grammatical_case', 'gender', 'number']})
            try:
                myconf = [c for c in criteria if p[0][c] != p[1][c]]
                if myconf:
                    conflicts.append(myconf)
                    print('conflict:', myconf)
            except KeyError:
                conflicts.append('incompatible')

        if len(conflicts) == len(parsed):
            agreement = False
        else:
            agreement = True
            conflicts = []

        return agreement, conflicts

    def find_agree(self, refword, pos=None, lemma=None):
        """
        Return the form of the specified lemma that agrees with the refword.
        """
        db = current.db
        if pos == 'article':
            parsing = self.parseform(refword)[0]
            print('parsing')
            print(parsing)
            artlemid = db(db.lemmas.lemma == 'ὁ'
                          ).select(db.lemmas.id).first().id
            print('artlemid', artlemid)
            argdict = {'source_lemma': artlemid,
                       'grammatical_case': parsing['grammatical_case'],
                       'gender': parsing['gender'],
                       'number': parsing['number']}
            print('argdict')
            print(argdict)
            myword = self.getform(argdict)
        return myword

    def parseform(self, token):
        """
        Return a dictionary holding the grammatical information for the token.
        """
        db = current.db
        try:
            formrows = db(db.word_forms.word_form == token
                          ).select().as_list()
        except AttributeError:
            formrows = db(db.word_forms.word_form == token.lower()
                          ).select().as_list()
        for row in formrows:
            lemmarow = db.lemmas(row['source_lemma'])
            row['part_of_speech'] = lemmarow['part_of_speech']
        return formrows

    def getform(self, kwargs, db=None):
        """
        Return a list of possible declined forms for the supplied parsing.
        """
        db = current.db if not db else db
        tbl = db['word_forms']
        query = tbl.id > 0
        for k, v in kwargs.items():
            query &= tbl[k] == v
        print('query in getform')
        print(query)
        myforms = db(query).select()
        forms = [row['word_form'] for row in myforms]
        if len(forms) == 1:
            forms = forms[0]
        elif not forms:
            forms = None
        print(forms)
        return forms

    def __exit__(self, type, value, traceback):
        """
        Necessary for use in 'with' condition.
        """
        print('destroying Parser instance')


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

    def test_agreement(self, validlfs, failedlfs, mw):
        """
        """
        newvalids = {}
        newfaileds = failedlfs
        conflict_list = {}

        for key, leaf in validlfs.items():
            match = mw[key]
            nouns = [m for m in match if m[1]['pos'] == 'Noun']
            arts = [m for m in match if m[1]['pos'] == 'Art']
            adjs = [m for m in match if m[1]['pos'] == 'Adj']

            leaf_conflicts = {}

            if len(nouns) > 1:
                print('phrase includes multiple nouns, checking agreement')
                for noun in nouns[1:]:
                    agree, conf = self.agree(nouns[0][0], noun[0],
                                             ['grammatical_case',
                                              'gender', 'number'])
                    if agree:
                        leaf, match = self.tag_token(noun[1]['index'],
                                                     'modifies',
                                                     nouns[0][1]['index'],
                                                     leaf, match)
                    else:
                        mykey = '{}_{}_{}'.format(noun[0], noun[1]['index'],
                                                  noun[1]['pos'])
                        leaf_conflicts[mykey] = ('no agreement', conf, noun,
                                                 nouns[0])
            if adjs:
                print('phrase includes adjective, checking agreement')
                for adj in adjs:
                    agree, conf = self.agree(nouns[0][0], adj[0],
                                             ['grammatical_case',
                                              'gender', 'number'])
                    if agree:
                        print(adj[1])
                        leaf, match = self.tag_token(adj[1]['index'],
                                                     'modifies',
                                                     nouns[0][1]['index'],
                                                     leaf, match)
                    else:
                        mykey = '{}_{}_{}'.format(adj[0], adj[1]['index'],
                                                  adj[1]['pos'])
                        leaf_conflicts[mykey] = ('no agreement', conf, adj,
                                                 nouns[0])
            if arts:
                print('phrase is definite, checking article agreement')
                for art in arts:
                    agree, conf = self.agree(nouns[0][0], art[0],
                                             ['grammatical_case',
                                              'gender', 'number'])
                    if agree:
                        leaf, match = self.tag_token(art[1]['index'],
                                                     'modifies',
                                                     nouns[0][1]['index'],
                                                     leaf, match)
                    else:
                        mykey = '{}_{}_{}'.format(art[0], art[1]['index'],
                                                  art[1]['pos'])
                        leaf_conflicts[mykey] = ('no agreement', conf, art,
                                                 nouns[0])
            mw[key] = match
            if leaf_conflicts:
                newfaileds[key] = leaf
                conflict_list[key] = leaf_conflicts
            else:
                newvalids[key] = leaf

        self.matching_words = mw

        return newvalids, newfaileds, mw, conflict_list

    def test_order(self, validlfs, failedlfs, matching_words):
        """
        """
        newvalids = {}
        newfaileds = {}

        # Does article precede its noun? If so mark as modifying that noun
        if self.definite:
            def fail_leaf(key, leaf):
                if leaf not in newfaileds:
                    newfaileds[key] = leaf

            def pass_leaf(key, leaf):
                if leaf not in newvalids:
                    newvalids[key] = leaf

            # FIXME: what about optional article?
            # now check article-noun order in successful leaves
            for key, leaf in validlfs.items():
                if self.before(art, mynoun, matching_words):
                    if newleaf not in newvalids:
                        newvalids[key] = newleaf

        # No other article intervening between matching article and noun?

        # Adjective in attributive position?

        # Adjectives agree with nominal? If so mark as modifying nominal

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


class Adj(Parser):
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
    parser.add_argument('pattern', help='the pattern against which to '
        'evaluate the string')
    args = parser.parse_args()
    main(args.string, args.pattern)
'''
