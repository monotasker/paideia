#! /usr/bin/python
# -*- coding:utf-8 -*-

import re
from collections import OrderedDict
#from pprint import pprint
from paideia_utils import clr
import traceback

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

    Returns a list of OrderedDicts, each of which represents one clause
    (or fragment). The keys in each dict are the tokens which make up the
    clause, ordered according to their appearance in the string.
    """
    clauses = re.split(r'[\.\?;:,]', str)
    tokenized = []
    for c in clauses:
       token_dict = OrderedDict((t.decode('utf-8').lower().encode('utf-8'), None) for t in c.split(' '))
       tokenized.append(token_dict)
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
        self.restring = args[0]
        if self.restring:
            self.restring = args[0].strip()
        self.structures = list(args[1:])
        self.top = False
        try:
            if self.structures[-1] == 'top':
                self.structures = self.structures[:-1]
                self.top = True
        except IndexError:  # because no sub-structures
            pass

        self.classname = type(self).__name__

    def validate(self, validleaves, failedleaves=[]):
        """
        compare list of word tokens to definition of valid natural language expressions.

        clause should be Clause() object
        """
        # TODO: to see eliminated parsing leaves, move them to a second list
        # instead of simply removing
        print clr('validating {}'.format(self.classname), self.myc)
        #print 'valid/failed:', clr([len(validleaves), '/', len(failedleaves)],
                                   #self.myc)

        # validate constituent structures first, recursively
        if self.structures:
            for s in self.structures:
                #print self.structures
                validleaves, failedleaves = s.validate(validleaves, failedleaves)
                if len(validleaves) < 1:
                    print clr('sub-structures didn\'t match', self.myc)
                    return validleaves, failedleaves
        else:  # if structure is at bottom level
            print clr('{} is bottom level, no '
                      'sub-structures'.format(self.classname), self.myc)

        # test sub-structure order for any viable parsing leaves returned
        for idx, leaf in enumerate(validleaves):
            leaf, match = self.test_order(leaf)
            if not match:
                failedleaves.append(validleaves.pop(idx))
            if len(validleaves) < 1:
                print clr(['order didn\'t match in', self.classname], self.myc)
                return validleaves, failedleaves
        #print 'valid/failed:', clr([len(validleaves), '/', len(failedleaves)],
                                   #self.myc)

        # find matching string in remaining viable leaves
        if self.restring:
            validleaves, failedleaves = self.match_string(validleaves, failedleaves)
            #print 'valid/failed:', clr([len(validleaves), '/',
                                        #len(failedleaves)], self.myc)
            if len(validleaves) < 1:
                print clr(['didn\'t find matching string for', self.classname],
                          self.myc)
                return validleaves, failedleaves

        # find any untagged words if this structure is top level
        if self.top:
            for v in validleaves:
                for w in v: print w,
                print ''
            for idx, leaf in enumerate(validleaves):
                untagged = [t for t, v in leaf.iteritems() if not v]
                if untagged:
                    failedleaves.append(validleaves.pop(idx))
                    print clr(['some extra words left over'], self.myc)
                    for w in untagged: print w
            if not validleaves:
                return validleaves, failedleaves

        #print clr('finished with {} valid leaves in parsing '
                  #'tree'.format(len(validleaves)), self.myc)
        if len(validleaves):
            print clr('{} is valid'.format(self.classname), self.myc)
            print 'valid/failed:', clr([len(validleaves), '/', len(failedleaves)],
                                        self.myc)
        return validleaves, failedleaves

    def match_string(self, validleaves, failedleaves,
                     restring=None, classname=None):
        '''
        Identify token strings that match the current construction.

        tokens
        : The ordered list of strings conaining the actual utterance.
        '''

        restring = self.restring if not restring else restring
        classname = self.classname if not classname else classname

        test = re.compile(restring, re.U|re.I)
        #print clr('looking for {}'.format(restring), self.myc)
        mymatch = test.findall(' '.join(validleaves[0]))
        #print clr('found {} matching strings in tokens'.format(len(mymatch)), self.myc)

        # TODO: split into leaves if (b) match already tagged
        def tag_token(matchstring, leaf):
            for word in matchstring.split(' '):  # allows for multi-word match strings
                print 'match:', clr(word, self.myc),
                try:
                    leaf[word].append(classname)
                except AttributeError:
                    leaf[word] = [classname]
            return leaf

        if mymatch:
            validleaves = [tag_token(m, leaf)
                           for leaf in validleaves for m in mymatch]
            #print clr('now working with {} leaves in parsing '
                      #'tree'.format(len(validleaves)), self.myc)
            print '\n',
        else:
            failedleaves.extend(validleaves[:])
            validleaves = []
        return (validleaves, failedleaves)

    def test_order(self, tokens):
        """ """
        match = True
        return tokens, match

    def get_struct_order(self, tokens):
        """
        Returns a dictionary of Parser subclass names and their index in tokens.

        This method also sets the self.structs class instance variable to the
        return value.
        """
        try:
            structs = {}
            for i, v in enumerate(tokens.values()):
                try:
                    structs[v] = i
                except TypeError:  # if the value is a list
                    for l in v:
                        structs[l] = i
            self.structs = structs
            return structs
        except Exception:
            print traceback.format_exc(5)

    def before(self, struct1, struct2, proximity=0, allow=[], exclude=[], require=[]):
        """
        Test whether struct1 appears before struct2 in the parsed tokens.

        Returns a boolean (True if struct1 comes before).

        proximity (int)
        :keyword argument, gives the maximum index places the two structures
        may stand apart in the token dictionary. The default value (0)
        indicates that proximity will not be considered.

        allow (list of strings)
        :keyword argument, lists the structures (type names) that may appear
        between struct1 and struct2.

        exclude (list of strings)
        :keyword argument, lists the structures (type names) that may not appear
        between struct1 and struct2.
        """
        structs = self.structs
        p1 = structs[struct1]
        p2 = structs[struct2]
        fit = True if p1 < p2 else False
        if fit and proximity > 0:
            fit = True if p2 - p1 <= proximity else False
        if fit and (allow or exclude or require):
            fit = self.between(p1, p2, allow, exclude, require)
        return p1, p2 if fit else False

    def after(self, struct1, struct2, proximity=0,
              allow=[], exclude=[], require=[]):
        """
        Test whether struct1 appears before struct2 in the parsed tokens.

        Returns a boolean (True if struct1 comes before).

        proximity (int)
        :keyword argument, gives the maximum index places the two structures
        may stand apart in the token dictionary. The default value (0)
        indicates that proximity will not be considered.

        allow (list of strings)
        :keyword argument, lists the structures (type names) that may appear
        between struct1 and struct2.

        exclude (list of strings)
        :keyword argument, lists the structures (type names) that may not appear
        between struct1 and struct2.
        """
        structs = self.structs
        p1 = structs[struct1]
        p2 = structs[struct2]
        fit = True if p2 < p1 else False
        if fit and proximity > 0:
            fit = True if p1 - p2 <= proximity else False
        if fit and (allow or exclude or require):
            fit = self.between(p2, p1, allow, exclude, require)
        return fit

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
        categories =  ['gender', 'number', 'case']
        conflicts = [c for c in categories if parsed[0][c] != parsed[1][c]]
        agreement = False if conflicts else True
        print agreement
        return agreement

    def parseform(self, token):
        """
        Return a dictionary holding the grammatical information for the token.
        """
        return wordforms[token]

    def getform(self, **kwargs):
        """
        Return a list of possible declined forms for the supplied parsing.
        """
        myform = list(set([w for w, p in wordforms.iteritems()
                           if not [k for k, v in kwargs.iteritems()
                                   if p[k] != v]
                           ]))
        return myform


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
        super(NounPhrase, self).__init__(*args)
        self.definite = False
        if 'def' in self.structures:
            self.definite = True
            self.structures.remove('def')

    def find_article(self, nominal, leaf):
        """
        Add the appropriate def article to the substructures of a noun phrase.
        """
        gram = self.parseform(nominal)
        kwargs = {'gender': gram['gender'],
                  'case': gram['case'],
                  'number': gram['number'],
                  'part_of_speech': 'def_art'
                  }
        myart = self.getform(**kwargs)[0]  # What about multiple matches?
        validleaves, failedleaves = self.match_string([leaf], [],
                                                      restring=myart,
                                                      classname='Art')
        return validleaves[0]

    def test_order(self, tokens):
        """
        """
        print 'testing order for', clr(self.classname, self.myc)
        match = False

        if self.definite:  # look for article(s) in valid configuration
            #print clr('{} is definite'.format(self.classname), self.myc)
            nominals = [t for t, v in tokens.iteritems() if v and 'Noun' in v]
            #print clr('nominals: {}'.format(nominals), self.myc)
            for n in nominals:
                print clr('getting article for {}'.format(n), self.myc),
                tokens = self.find_article(n, tokens)
            structs = self.get_struct_order(tokens)
            for k, v in structs.iteritems(): print clr([k, v, ';'], self.myc),
            print '\n',

            # TODO: check presence of non-agreeing art between agreeing art and
            # noun (or agreeing art without agreeing adj); also gen art
            # possible if gen modifier also there.
            matches = [self.before('Art', 'Noun', allow='Adj'),
                       self.before('Art', 'Noun', proximity=1)]
            match = list(set([m for m in matches if m]))
            if match:
                agreements = [m for m in match
                              if m and self.agree(m[0], m[1], tokens.keys())]
                match = True if agreements else False
        else:
            match = True

        return tokens, match


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
    Defniteness ambiguous.
    """
    myc = 'blue'
    pass


class Art(Parser):
    """
    """
    pass


class Adjective(Parser):
    pass

def main():
    """Take the  strings in 'strings' variable and validate them."""
    print clr('\n\nSTARTING VALIDATION', 'white')
    strings = {'Τον ἀρτον ὁ ἀνηρ πωλει.': 'pass',
               'Ὁ ἀνηρ πωλει τον ἀρτον.': 'pass',
               'Πωλει τον ἀρτον ὁ ἀνηρ.': 'pass',
               'τον πωλει ὁ ἀρτον ἀνηρ.': 'fail',  # should fail
               'ὁ ἀρτον πωλει τον ἀνηρ.': 'fail',  # should fail
               'ὁ τον ἀρτον πωλει ἀνηρ.': 'fail', # should fail
               'ὁ πωλει τον ἀρτον ἀνηρ.': 'fail'  # should fail
               }
    passed = []
    failed = []
    for idx, s in enumerate(strings.keys()):
        print clr('{} ----------------------------------------'
                  '----'.format(idx), 'white')
        tokenset = [token for token in tokenize(s)
                    if token.keys()[0] not in ['', ' ', None]]
        #print len(tokens), 'clauses to validate'
        for tokens in tokenset:
            c = Clause(None,
                       Subject(None, Noun(r'ἀνηρ'), 'def'),
                       Verb(r'πωλει|ἀγοραζει'),
                       DirObject(None, Noun(r'ἀρτον'), 'def'),
                       'top')
            # put tokens in list to prepare for parsing tree forking
            validleaves, failedleaves = c.validate([tokens])
            if validleaves:
                passed.append((s, idx))
            else:
                failed.append((s, idx))
            myc = 'green' if validleaves else 'red'
            resp = 'Success!' if validleaves else 'Failed'
            print clr([resp, '(', s ,')', '\n'], myc)
    print '{} of {} passed'.format(len(passed), len(passed) + len(failed))
    for p in passed:
        pclr = 'green' if strings[p[0]] == 'pass' else 'orange'
        print clr([p[1], ':', p[0]], pclr)
    for f in failed:
        fclr = 'red' if strings[f[0]] == 'fail' else 'purple'
        print clr([f[1], ':', f[0]], fclr)
    print '============================================================='

if __name__ == "__main__":
    main()
