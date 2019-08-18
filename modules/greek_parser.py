#! python3.6
# -*- coding:utf-8 -*-

import argparse
from copy import deepcopy, copy
from itertools import product, permutations
import os
from pprint import pprint
import re
import sys
import traceback
sys.path.append(os.path.abspath(
    '../../../gluon'))
from plugin_utils import clr
from gluon import current

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
    global LEAFINDEX
    LEAFINDEX = 0
    clauses = re.split(r'[\.\?;:,]', str)
    tokenized = []
    for c in clauses:
        words = c.split(' ')
        token_list = [(t, {'index': words.index(t)}) for t in words]
        tokenized.append({LEAFINDEX: token_list})
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
        global LEAFINDEX
        self.restring = args[0] if args[0] else None
        self.structures = args[1:]
        self.top = False
        self.optional = False
        try:
            self.top = True if self.structures[-1] == 'top' else False
            if self.top:
                self.structures = self.structures[:-1]
        except IndexError:  # because no substructures
            pass
        try:
            self.optional = True if self.structures[-1] == "opt" else False
            if self.optional:
                self.structures = self.structures[:-1]
        except IndexError:  # because no substructures
            pass
        # print('top?', self.top)
        # print('optional?', self.optional)
        # print('structures:', self.structures)
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
        global LEAFINDEX
        mw = {}
        conf = {}
        print(clr('Validating {}'.format(self.classname), self.myc))

        if self.structures:
            # insert article if necessary
            myarts = [s for s in self.structures if isinstance(s, Art)]
            mynoms = [s for s in self.structures if isinstance(s, (Noun, Adj))]
            lendiff = len(mynoms) - len(myarts)
            if self.definite and not myarts:
                self.structures = list(Art('?'), *self.structures)
            if self.definite and lendiff:
                for l in range(lendiff):
                    self.structures = list(Art('?', 'opt'), *self.structures)
            # validate constituent structures recursively
            for s in self.structures:
                #  TODO: pass structures back up in case nested substructures
                # were changed
                oldmw = deepcopy(mw)
                print(clr('Validating substructure {}'.format(s), self.myc))
                # print(oldmw)
                validlfs, failedlfs, match, conf = s.validate(
                    validlfs, failedlfs=failedlfs)
                if len(validlfs) < 1:
                    return validlfs, failedlfs, mw, conf
                # add this substructure's matching words to the parent
                # object's total matching words
                for k, wrd in match.items():
                    if k in mw.keys() and mw[k]:
                        mw[k].extend(wrd)
                    elif isinstance(k, str):  # handle match for newly split
                        # leaf because need pre-existing matching words
                        # from basis leaf too
                        k_new, k_old = k.split('-')
                        if int(k_old) in oldmw.keys() and oldmw[int(k_old)]:
                            print(k_old, '*****************************************')
                            print(oldmw[int(k_old)])
                            print(k_new)
                            print(wrd)
                            print(oldmw[int(k_old)] + wrd)
                            mw[int(k_new)] = oldmw[int(k_old)] + wrd
                        else:
                            mw[int(k_new)] = wrd
                    else:
                        mw[k] = wrd
                # print(mw)
            # remove matching words for any failed leaves
            mw = {k: v for k, v in mw.items() if k in validlfs.keys()
                  or k in failedlfs.keys()}
            # print(clr('cumulative mw with all structures: {}'.format(mw),
            #           self.myc))

        # find possible matching strings in viable leaves
        if self.restring:
            print(clr('checking for restring {}'.format(self.restring),
                      self.myc))
            validlfs, failedlfs, match, conf = self.match_string(validlfs,
                                                                 failedlfs)
            # print(clr('newly found match is: {}'.format(match),
            #           self.myc))
            # add this level's matching words to matching words of substructures
            for k, wrd in match.items():
                if k in mw.keys():
                    mw[k].extend(wrd)
                else:
                    mw[k] = wrd
            print(clr('total {} mw is now: {}'.format(type(self).__name__, mw),
                      self.myc))

            if len(validlfs) < 1:  # no valid leaves, validation fails
                print(clr('no valid leaves after matching!!!!!',
                          self.myc))
                return validlfs, failedlfs, mw, conf

        # test sub-structure agreements and order for any viable leaves
        if self.structures:
            #  first remove any duplicate leaves
            print('removing duplicate leaves ================================')
            print(len(failedlfs))
            print(len(validlfs))
            seen = []
            for k in list(validlfs.keys()):
                if validlfs[k] not in seen:
                    seen.append(validlfs[k])
                else:
                    del validlfs[k]
                    del mw[k]
            for k in list(failedlfs.keys()):
                if failedlfs[k] not in seen:
                    seen.append(failedlfs[k])
                else:
                    del failedlfs[k]
                    del mw[k]
            print(len(failedlfs), [l for l in failedlfs.keys()])
            print(len(validlfs), [l for l in validlfs.keys()])
            pprint(failedlfs)
            pprint(validlfs)

            print(clr('testing agreements', self.myc))
            validlfs, failedlfs, mw, conf = self.test_agreement(validlfs,
                                                                failedlfs,
                                                                mw,
                                                                conf)
            print(clr('testing order', self.myc))
            validlfs, failedlfs, mw, conf = self.test_order(validlfs,
                                                            failedlfs,
                                                            mw,
                                                            conf)
            if len(validlfs) < 1:  # no valid leaves, validation fails
                return validlfs, failedlfs, mw, conf

        # find any untagged words if this structure is top level
        # if found, validation fails
        if self.top:
            print(clr('top level structure', self.myc))
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
        # print('starting to tag', key, 'in', mydict)
        if key not in list(mydict.keys()):  # only tag word if untagged
            print(key, 'can be tagged')
            mydict[key] = value

            # print('matching:', matching)
            if matching:
                myword = leafcopy[matchindex][0]
                for m in matching:
                    if m[0] == myword:
                        m[1][key] = value
        else:
            print(key, 'already tagged, leaf invalid')
            print(leafcopy[matchindex])
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
        mymatch = test.findall(validstring)
        print(clr('match:'.format([m for m in mymatch]), self.myc))

        newvalids = {}
        newfaileds = {}
        conflicts = {}
        # if structure optional, preserve valid leaves without match tagged
        if self.optional:
            print(clr('optional: keeping leaves ', self.myc), end=' ')
            for key, leaf in validleaves.items():
                print(key)
                newvalids[key] = leaf
                matching_words[key] = []
            
        if mymatch:
            for key, leaf in validleaves.items():
                print(clr('matching leaf {}>>>>>>>>>>>>>>>>>>>>>>>'.format(key),
                          self.myc))
                failcount = 0
                for m in mymatch:
                    print(clr('trying {}=========================='.format(m),
                              self.myc))
                    if m in [w[0] for w in leaf]:  # because findall and case
                        print(clr('tagging {} with {}'.format(m, classname),
                                  self.myc))
                        matchindex = [l[1]['index'] for l in leaf
                                      if l[0] == m][0]
                        taggedleaf, match = self.tag_token(matchindex, 'pos',
                                                           classname,
                                                           deepcopy(leaf),
                                                           None)
                        if taggedleaf:
                            usekey = copy(key)
                            if len(newvalids) and usekey in list(newvalids.keys()):
                                LEAFINDEX += 1
                                usekey = copy(LEAFINDEX)
                            print(clr('appending valid leaf {}'.format(usekey),
                                      self.myc))
                            newvalids[usekey] = taggedleaf
                            # add matching words (with index) directly to
                            # instance variable
                            new_word = (m, {'pos': classname,
                                            'index': matchindex})
                            if usekey != key:  # send up basis for split leaf
                                usekey = '{}-{}'.format(usekey, key)
                            if usekey in matching_words.keys():
                                matching_words[usekey].append(new_word)
                            else:
                                matching_words[usekey] = [new_word]
                            # print(matching_words)
                        elif not taggedleaf:
                            failcount += 1
                            print('tagging failed')
                    else:
                        print('match', m, 'is not in string')
                        pass

                if failcount == len(mymatch):
                    print(clr('appending failed leaf {}'.format(key),
                                self.myc))
                    newfaileds[key] = leaf
                    
        else:
            print('no match')
            if validleaves:
                if newvalids:
                    print('no match, but optional')
                    pass
                elif failedleaves:
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
        # print(prior[1])
        # print(latter[1])
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
            print(mw)
            modindex = modifier[1]['modifies']
            modified = [w for w in mw if w[1]['index'] == modindex]
            if modified:
                return modified[0]
            else:
                return False
        except (TypeError, KeyError):
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

    def check_and_tag_agreement(self, validlfs, failedlfs, dimensions, parts,
                                 mode, tagging, mw, conflict_list):
        """
        Check specified parts of speech for agreement in specified dimensions.

        If only one part of speech is specified in `parts`, the members of that set are tested for global agreement among themselves. If two parts of speech are specified, the members of those two sets are tested for agreement across sets. This can be done in two ways. If `mode` is "pairwise", all possible cross-set pairs are checked for agreement. If `mode` is "setwise", this method looks at all combinations of pairings in which each member of set A is paired with a different member of set B.

        **For setwise comparison it's crucial that if one set will be shorter it is listed first in `parts`.**

        In the process of checking for agreement, the leaves are also tagged with information about which words modify other words in the same construction.

        Arguments:
            validlfs {dict} -- a dictionary of leaves that have passed prior
                              validation and are candidates for testing
                              agreement
            failedfs {dict} -- a dictionary of leaves that have aready failed
                               validation
            dimensions {list} -- A list of strings corresponding to the
                                 grammatical features that should agree.
            parts {list} -- A list of strings corresponding to the parts of
                            speech to be tested for agreement.
            mw {dict} -- A dictionary of the words in each leaf that match the
                         currently validating structure.
            tagging {dict} --   A dictionary of tags to be added to words that
                                agree. Keys are Parser types (str). Each value is a list of tuples, each of which includes a
                                tag string [0] and a part of speech that is the
                                target for the tagged relationship [1].
            conflict_list{dict} -- A dictionary containing the validation                              probems discovered so far in failed leaves.

        Returns:
            newvalids {dict}
            newfaileds {dict}
            mw {dict}
            conflict_list {dict}
        """
        global LEAFINDEX
        newvalids = {}
        newfaileds = failedlfs

        def handle_result(key, leaf, match, splitlfs, splitmatches,
                          leaf_conflicts):
            # handle both original leaf and any newly split children
            mw[key] = match
            for s, mymatch in splitmatches.items():
                mw[s] = mymatch

            result_leaves = {key: leaf}
            if splitlfs:
                result_leaves.update(splitlfs)
            for mykey, myleaf in result_leaves.items():
                if leaf_conflicts:
                    newfaileds[mykey] = myleaf
                    if mykey not in conflict_list.keys():
                        conflict_list[mykey] = leaf_conflicts
                    else:
                        conflict_list[mykey].update(leaf_conflicts)
                    if mykey in newvalids.keys():
                        del newvalids[mykey]
                else:
                    newvalids[mykey] = myleaf

        def makeleaf(newleaf, newmatch, splitlfs, splitmatches):
            global LEAFINDEX
            LEAFINDEX += 1
            usekey = copy(LEAFINDEX)
            print('adding split leaf {}'.format(usekey), '++++++++++++++++++')
            splitlfs[usekey] = newleaf
            splitmatches[usekey] = newmatch
            return splitlfs, splitmatches

        for key, leaf in validlfs.items():
            print(clr('checking leaf {}'.format(key), self.myc))
            splitlfs = {}
            splitmatches = {}
            leaf_conflicts = {}
            match = copy(mw[key])
            lists = [[m for m in match if m[1]['pos'] == p] for p in parts]

            # internal agreement among members of single set
            if len(parts) == 1:
                mytype = parts[0]
                if len(lists[0]) > 1:
                    print('phrase includes multiple {}s, checking '
                            'internal agreement'.format(mytype))
                    words = lists[0]
                    for word in words[1:]:
                        print(words[0][0], word[0], ': ', end='')
                        agree, conf = self.agree(words[0][0],
                                                 word[0], dimensions)
                        if agree and tagging:
                            mytag = [t[0] for t in tagging[mytype]
                                     if t[1] == mytype][0]
                            print('mytag:', mytag)
                            leaf, match = self.tag_token(
                                word[1]['index'], mytag,
                                words[0][1]['index'], leaf, match)
                            print('agree')
                        elif not agree:
                            mykey = '{}_{}_{}'.format(word[0], word[1]['index'],
                                                      word[1]['pos'])
                            leaf_conflicts[mykey] = ('no agreement', conf, word,
                                                    words[0])
                            print('fail***')

            # agreement between two sets

            def check_set(myset, valid_sets, invalid_sets):
                valid_pairs = []
                invalid_pairs = {}
                for pair in myset:
                    word1, word2 = pair[0], pair[1]
                    print(word1[0], word2[0], ': ', end="")
                    agree, conf = self.agree(word1[0], word2[0], dimensions)
                    if agree:
                        valid_pairs.append((word1, word2))
                    else:
                        mykey = '{}_{}_{}'.format(word1[0],
                                                    word1[1]['index'],
                                                    word1[1]['pos'])
                        invalid_pairs[mykey] = ('no agreement', conf, word1,
                                                word2)
                if len(valid_pairs) == len(list(myset)):
                    valid_sets.append(valid_pairs)
                else:
                    invalid_sets[str(myset)] = invalid_pairs

                return valid_sets, invalid_sets

            # ** make sure all the lists actually contain items **
            full_lists = [l for l in lists if l]
            if len(full_lists) > 1:
                word1type = parts[0]
                word2type = parts[1]
                print('construction includes {}, checking {} '
                      'agreement'.format(word1type, word2type))
                counter = 0
                valid_sets = []
                invalid_sets = {}

                if mode == 'pairwise' or [l for l in full_lists if len(l) == 1]:
                    print('using product')
                    myset = list(product(*full_lists))
                    # print('product:', myset)
                    valid_sets, invalid_sets = check_set(myset, valid_sets,
                                                         invalid_sets)
                else:
                    print('using permutations')
                    sets = [list(zip(full_lists[0]))
                            for p in permutations(full_lists[1])]
                    # print('permutations:', sets)
                    for myset in sets:
                        valid_sets, invalid_sets = check_set(myset, valid_sets,
                                                             invalid_sets)

                if valid_sets:
                    for myset in valid_sets:
                        for word1, word2 in myset:
                            newleaf = deepcopy(leaf)
                            newmatch = deepcopy(match)
                            if tagging and word1type in tagging.keys():
                                for t in tagging[word1type]:
                                    if t[0] == 'modifies' and t[1] == word2type:
                                        print('t:', t)
                                        newleaf, newmatch = self.tag_token(
                                            word1[1]['index'], t[0],
                                            word2[1]['index'], newleaf, newmatch
                                            )
                                    elif t[0] == 'antecedent':
                                        print('t:', t)
                                        word2mod = self.find_modified(
                                            word2, newmatch)
                                        if word2mod and \
                                              word2mod[1]['pos'] == t[1]:
                                            newleaf, newmatch = self.tag_token(
                                                word1[1]['index'],
                                                t[0],
                                                word2mod[1]['index'],
                                                newleaf, newmatch
                                                )
                            if tagging and word2type in tagging.keys():
                                for t in tagging[word2type]:
                                    newleaf, newmatch = self.tag_token(
                                        word2[1]['index'], t[0],
                                        word1[1]['index'], newleaf, newmatch
                                        )
                            print('agree')
                            if newleaf:
                                print('newleaf', newleaf)
                                if counter == 0:
                                    leaf, match = newleaf, newmatch
                                    counter += 1
                                else:
                                    splitlfs, splitmatches = makeleaf(
                                        newleaf, newmatch, splitlfs,
                                        splitmatches)
                else:
                    pprint(invalid_sets)
                    leaf_conflicts[invalid_sets.keys()] == invalid_sets

            handle_result(key, leaf, match, splitlfs, splitmatches,
                          leaf_conflicts)

        return newvalids, newfaileds, mw, conflict_list

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
    myc = 'lightgreen'

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
        newfaileds = deepcopy(failedlfs)
        mytests = [(['grammatical_case', 'gender', 'number'], 
                    ['Noun'],
                    'global',
                    None
                    ),
                   (['grammatical_case', 'gender', 'number'],
                    ['Adj', 'Noun'],
                    'pairwise',
                    {'Adj': [('modifies', 'Noun')]}
                    ),
                   (['grammatical_case', 'gender', 'number'],
                    ['Art', 'Noun'],
                    'setwise',
                    {'Art': [('modifies', 'Noun')]}
                    ),
                   (['grammatical_case', 'gender', 'number'],
                    ['Art', 'Adj'],
                    'setwise',
                    {'Art': [('modifies', 'Adj'), ('antecedent', 'Noun')]}
                    )
                   ]

        for test in mytests:
            myvalids = newvalids if newvalids else validlfs
            ret = self.check_and_tag_agreement(myvalids, failedlfs, *test, mw,
                                               conflict_list)
            newvalids = ret[0]
            newfaileds = ret[1]
            mw = ret[2]
            conflict_list = ret[3]

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
            print(clr('checking leaf {}'.format(key), self.myc))
            match = mw[key]
            nouns = [m for m in match if m[1]['pos'] == 'Noun']
            arts = [m for m in match if m[1]['pos'] == 'Art']
            adjs = [m for m in match if m[1]['pos'] == 'Adj']

            leaf_conflicts = {}

            # FIXME: what about optional article?
            for art in arts:
                # print(art)
                print('does', art, ': ')
                print('have a unique substantive or adjective? ', end='')
                mymod = self.find_modified(art, match)
                modpos = mymod[1]['pos'] if mymod else None
                if not mymod:
                    print('fail***')
                    leaf_conflicts[format_confkey(art)] = ('out of order',
                        [['dangling article']], art, None)
                else:
                    print('yes:', mymod)

                if mymod:
                    print('precede its substantive or adjective?', end='')
                    if not self.before(art, mymod):
                        confstring = 'article follows its modified {}'.format(
                            mymod[1]['pos'])
                        leaf_conflicts[format_confkey(art)] = ('out of order',
                            [[confstring]], art, mymod)
                        print('fail***')
                    else:
                        print('yes')

                    # No extraneous words intervening between article and
                    # modified nominal/adj?
                    print('have extraneous words before modified?', end='')
                    extrawords = self.find_nonmod_between(art, mymod, leaf)
                    if extrawords:
                        confstring = 'extra words between article and modified {}' \
                                    ''.format(mymod[1]['pos'])
                        leaf_conflicts[format_confkey(extrawords)] = (
                            'out of order', [[confstring]], extrawords, [art, mymod])
                        print('fail***')
                        print(extrawords)
                    else:
                        print('no')

                    for adj in adjs:
                        print('Is the adjective {} in attributive '
                              'position? '.format(adj), end='')
                        amoded = self.find_modified(adj, match)
                        # print('amoded:', amoded)
                        modedart = self.find_article(amoded, match)
                        # print('modedaart:', modedart)
                        adjart = self.find_article(adj, match)
                        # print('adjart:', adjart)
                        if modedart and self.before(adj, amoded):
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
                                print('fail (1)***')
                        elif modedart and not adjart:
                            leaf_conflicts[format_confkey(adj)] = ('out of order',
                                [['adjective not in attributive position 1']],
                                adj, [modedart, amoded])
                            print('fail (2)***')
                            print(leaf)
                        elif adjart and not (self.before(adjart, adj) and
                                            self.after(adjart, amoded)):
                            leaf_conflicts[format_confkey(adj)] = ('out of order',
                                [['adjective not in attributive position 2']],
                                adj, [modedart, amoded, adjart])
                            print('fail (3)***')

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
    myc = 'lightpurple'


class Noun(Parser):
    """
    Definiteness ambiguous.
    """
    myc = 'lightcyan'


class Art(Parser):
    """
    """
    myc = 'orange'


class Adj(Parser):
    myc = 'lightpurple'


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
        print(clr([resp, '(', string ,')', '\n'], myc))
    print('=============================================================')

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('string', help='the string to be evaluated')
    parser.add_argument('pattern', help='the pattern against which to '
        'evaluate the string')
    args = parser.parse_args()
    main(args.string, args.pattern)