#! /usr/bin/python3.6
# -*- coding:utf-8 -*-

# import argparse
from copy import deepcopy, copy
from gluon import current
# from paideia_utils import Uprinter
from plugin_utils import clr
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
        mw = {}
        conf = {}
        print('starting mw:', mw)

        print('restring is', self.restring)
        # validate constituent structures recursively
        if self.structures:
            # insert article if necessary
            if self.definite and not [s for s in self.structures
                                      if isinstance(s, Art)]:
                self.structures = (Art('?'), *self.structures)
            for s in self.structures:
                print('validating', s)
                validlfs, failedlfs, match, conf = s.validate(
                    validlfs, failedlfs=failedlfs)
                if len(validlfs) < 1:
                    print('failed while validating', s)
                    return validlfs, failedlfs, mw, conf
                # add this substructure's matching words to the parent
                # object's total matching words
                for k, wrd in match.items():
                    if k in mw.keys():
                        mw[k].extend(wrd)
                    else:
                        mw[k] = wrd
            print('after matching substructures, mw is:', mw)

        # find matching string for remaining viable leaves
        if self.restring:
            # need to compare with newly parsed to find newly added words
            old_validlfs = copy(validlfs)
            print('checking for restring', self.restring)
            validlfs, failedlfs, match, conf = self.match_string(validlfs,
                                                                 failedlfs)
            print('newly found match is:', match)
            # add parent's matching words to its total matching words
            for k, wrd in match.items():
                if k in mw.keys():
                    mw[k].extend(wrd)
                else:
                    mw[k] = wrd
            print('total', type(self).__name__, ' mw is now:', mw)

            if len(validlfs) < 1:  # no valid leaves, validation fails
                print('no valid leaves after matching!!!!!')
                return validlfs, failedlfs, mw, conf

        # test sub-structure agreements and order for any viable leaves
        if self.structures:
            validlfs, failedlfs, mw, conf = self.test_agreement(validlfs,
                                                                failedlfs,
                                                                mw,
                                                                conf)
            validlfs, failedlfs, mw, conf = self.test_order(validlfs,
                                                            failedlfs,
                                                            mw,
                                                            conf)
            if len(validlfs) < 1:  # no valid leaves, validation fails
                return validlfs, failedlfs, mw, conf

        # find any untagged words if this structure is top level
        # if found, validation fails
        if self.top:
            for v in list(validlfs.values()):
                for w in v:
                    print(w)
                print('')
            for idx, leaf in validlfs.items():
                untagged = [t for t in leaf if 'pos' not in t[1].keys()]
                if untagged:
                    failedlfs[idx] = validlfs[idx]
                    validlfs = {k: v for k, v in validlfs.items() if k != idx}
                    print(clr(['some extra words left over'], self.myc))
                    for w in untagged: print(w)
                    confkey = '_'.join([w[0] for w in untagged])
                    conf[idx] = {confkey: ('extra words present',
                                           [['extra words present']],
                                           untagged,
                                           failedlfs[idx])
                                 }
            if not validlfs:
                return validlfs, failedlfs, mw, conf
            else:
                pass

        self.matching_words = mw

        return validlfs, failedlfs, mw, conf

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
        print('mydict:', mydict)
        if key not in list(mydict.keys()):  # only tag word if untagged
            mydict[key] = value

            if matching:
                myword = leafcopy[matchindex][0]
                for m in matching:
                    if m[0] == myword:
                        m[1][key] = value
        else:
            print(key, 'already tagged, leaf invalid')
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
        if classname == 'Art' and restring == '?':
            restring = r'ὁ|του|τῳ|τον|το|ἡ|της|τῃ|την|οἱ|των|τοις|τους|τα|αἱ|ταις|τας'

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
        conflicts = {}
        if mymatch:
            print('mymatch', mymatch)
            print('matching_words:', matching_words)
            for key, leaf in validleaves.items():
                print('tagging leaf:', key, '=============================')
                for m in mymatch:
                    if m in [w[0] for w in leaf]:  # because findall and case
                        print('tagging leaf with', classname)
                        matchindex = [l[1]['index'] for l in leaf
                                      if l[0] == m][0]
                        taggedleaf, match = self.tag_token(matchindex, 'pos',
                                                           classname,
                                                           deepcopy(leaf),
                                                           None)
                        if taggedleaf and taggedleaf not in newvalids.values():
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
                            print(matching_words)
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

        for idx, leaf in newfaileds.items():
            confkey = "{}_{}".format(restring, classname)
            conflicts[idx] = {confkey: ('no match found',
                                        [['no match found']],
                                        restring,
                                        validstring
                                        )}
        print(matching_words)

        return newvalids, newfaileds, matching_words, conflicts

    def test_agreement(self, validleaves, failedleaves,
                       matching_words, conflicts):
        """ """
        return validleaves, failedleaves, matching_words, conflicts

    def test_order(self, validleaves, failedleaves,
                   matching_words, conflicts):
        """ """
        return validleaves, failedleaves, matching_words, conflicts

    def before(self, prior, latter):
        """
        Return True if prior tuple comes before latter in their leaf.
        """
        print(prior[1])
        print(latter[1])
        if prior[1]['index'] < latter[1]['index']:
            print('before')
            return True
        else:
            return False

    def after(self, latter, prior):
        """
        Return True if latter tuple comes after prior in their leaf.
        """
        if prior[1]['index'] > latter[1]['index']:
            return False
        else:
            return True

    def find_modified(self, modifier, mw):
        """
        Return the tuple for the word modified by the supplied modifier.
        """
        try:
            modindex = modifier[1]['modifies']
            modified = [w for w in mw if w[1]['index'] == modindex]
            if modified:
                return modified[0]
            else:
                return False
        except KeyError:
            return False

    def find_article(self, modified, mw):
        """
        Return the tuple for the article modifying the supplied word.
        """
        try:
            modindex = modified[1]['index']
            print(modindex)
            print(mw)
            modified = [w for w in mw if 'modifies' in w[1].keys() and
                        w[1]['modifies'] == modindex and
                        w[1]['pos'] == 'Art']
            print(modified)
            return modified[0] if modified else False
        except KeyError as e:
            print(e)
            return False

    def find_nonmod_between(self, modifier, modified, leaf):
        """
        Return any extraneous words between modifier and modified.

        These are judged to be extraneous if they are not tagged as also
        modifying the modified word.
        """
        moder_idx = modifier[1]['index']
        moded_idx = modified[1]['index']
        print([w for w in leaf if w[1]['index'] > moder_idx
                          and w[1]['index'] < moded_idx])
        nonmod_between = [w for w in leaf if w[1]['index'] > moder_idx
                          and w[1]['index'] < moded_idx
                          and ('modifies' not in w[1].keys()
                          or w[1]['modifies'] != moded_idx)]
        return nonmod_between

    def between(self, p1, p2, mw, allow=[], exclude=[], require=[]):
        """
        Test whether any intervening structures are appropriate.

        The keyword arguments allow, exclude, and require can be supplied with
        either word tuples (specifying specific words) or Parser subclasses (specifying kinds of constructions)
        """
        between = [m for m in mw
                   if m[1]['index'] in range(p1[1]['index'] + 1,
                                             p2[1]['index'])]
        # print('between:', between)
        allow_wds = [a for a in allow if not isinstance(a, Parser)]
        allow_tps = [a for a in allow if isinstance(a, Parser)]
        exclude_wds = [a for a in exclude if not isinstance(a, Parser)]
        exclude_tps = [a for a in exclude if isinstance(a, Parser)]
        require_wds = [a for a in require if not isinstance(a, Parser)]
        # print('require_wds:', require_wds)
        require_tps = [a for a in require if isinstance(a, Parser)]

        disallowed = [s for s in between
                      if (allow_tps and not isinstance(s, allow_tps))
                      or (allow_wds and s not in allow_wds)
                      if (allow_tps and not isinstance(s, allow_tps))
                      or (allow_wds and s not in allow_wds)
                      ]
        missing_wds = [s for s in require_wds if s not in between]
        missing_tps = [t for t in require_tps
                       if not [w for w in between if isinstance(w, t)]]
        missing_wds.extend(missing_tps)

        fit = False if (disallowed or missing_wds) else True

        return fit, disallowed, missing_wds

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
                    # print('conflict:', myconf)
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
            # print('parsing')
            # print(parsing)
            artlemid = db(db.lemmas.lemma == 'ὁ'
                          ).select(db.lemmas.id).first().id
            # print('artlemid', artlemid)
            argdict = {'source_lemma': artlemid,
                       'grammatical_case': parsing['grammatical_case'],
                       'gender': parsing['gender'],
                       'number': parsing['number']}
            # print('argdict')
            # print(argdict)
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
        # print('query in getform')
        # print(query)
        myforms = db(query).select()
        forms = [row['word_form'] for row in myforms]
        if len(forms) == 1:
            forms = forms[0]
        elif not forms:
            forms = None
        # print(forms)
        return forms

    def __exit__(self, type, value, traceback):
        """
        Necessary for use in 'with' condition.
        """
        # print('destroying Parser instance')


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

    def test_agreement(self, validlfs, failedlfs, mw, conflict_list):
        """
        """
        newvalids = {}
        newfaileds = failedlfs

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
                        # print(adj[1])
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
                if key not in conflict_list.keys():
                    conflict_list[key] = leaf_conflicts
                else:
                    conflict_list[key].update(leaf_conflicts)
            else:
                newvalids[key] = leaf

        self.matching_words = mw

        return newvalids, newfaileds, mw, conflict_list

    def test_order(self, validlfs, failedlfs, mw, conflict_list):
        """
        """
        newvalids = {}
        newfaileds = failedlfs

        def format_confkey(myterm):
            if isinstance(myterm, list):
                if len(myterm) > 1:
                    return '{}-{}_{}-{}'.format(myterm[0][0], myterm[-1][0],
                                                myterm[0][1]['index'],
                                                myterm[-1][1]['index'])
                else:
                    myterm = myterm[0]
            return '{}_{}_{}'.format(myterm[0], myterm[1]['index'],
                                     myterm[1]['pos'])

        for key, leaf in validlfs.items():
            match = mw[key]
            nouns = [m for m in match if m[1]['pos'] == 'Noun']
            arts = [m for m in match if m[1]['pos'] == 'Art']
            adjs = [m for m in match if m[1]['pos'] == 'Adj']

            leaf_conflicts = {}

            # FIXME: what about optional article?
            for art in arts:
                # print(art)
                print('Does each article have a unique substantive or adjective?')
                mymod = self.find_modified(art, match)
                print('mymod:', mymod)
                modpos = mymod[1]['pos'] if mymod else None
                if not mymod:
                    print('A')
                    leaf_conflicts[format_confkey(art)] = ('out of order',
                        [['dangling article']], art, None)

                if mymod:
                    print('Does each article precede its substantive or '
                          'adjective?')
                    if not self.before(art, mymod):
                        confstring = 'article follows its modified {}'.format(
                            mymod[1]['pos'])
                        leaf_conflicts[format_confkey(art)] = ('out of order',
                            [[confstring]], art, mymod)

                    # No extraneous words intervening between article and
                    # modified nominal/adj?
                    print('No extraneous words?')
                    extrawords = self.find_nonmod_between(art, mymod, leaf)
                    if extrawords:
                        confstring = 'extra words between article and modified {}' \
                                    ''.format(mymod[1]['pos'])
                        leaf_conflicts[format_confkey(extrawords)] = (
                            'out of order', [[confstring]], extrawords, [art, mymod])

                    print('definite adjective in attributive position?')
                    for adj in adjs:
                        print(adj)
                        amoded = self.find_modified(adj, match)
                        print('amoded:', amoded)
                        modedart = self.find_article(amoded, match)
                        print('modedaart:', modedart)
                        adjart = self.find_article(adj, match)
                        print('adjart:', adjart)
                        if modedart and self.before(adj, amoded):
                            print('K')
                            kwargs = {'exclude': adjart} if adjart else {}
                            betwn, disal, miss = self.between(modedart, amoded,
                                match, require=[adj], **kwargs)
                            # print('disal:', disal)
                            # print('miss:', miss)
                            if not betwn:
                                leaf_conflicts[format_confkey(adj)] = (
                                    'out of order',
                                    [['adjective not in attributive position 1']],
                                    adj, [modedart, amoded])
                        elif modedart and not adjart:
                            print('J')
                            leaf_conflicts[format_confkey(adj)] = ('out of order',
                                [['adjective not in attributive position 1']],
                                adj, [modedart, amoded])
                        elif adjart and not (self.before(adjart, adj) and
                                            self.after(adjart, amoded)):
                            print('L')
                            leaf_conflicts[format_confkey(adj)] = ('out of order',
                                [['adjective not in attributive position 2']],
                                adj, [modedart, amoded, adjart])

                    # definite attributive adjective follows nominal

            mw[key] = match
            if leaf_conflicts:
                newfaileds[key] = leaf
                if key not in conflict_list.keys():
                    conflict_list[key] = leaf_conflicts
                else:
                    conflict_list[key].update(leaf_conflicts)
            else:
                newvalids[key] = leaf

        self.matching_words = mw

        return newvalids, newfaileds, mw, conflict_list


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
