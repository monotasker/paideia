#! /usr/bin/python
# -*- coding:utf-8 -*-

import re
from gluon import current
from collections import OrderedDict
#from pprint import pprint
from plugin_utils import clr, makeutf8
#import argparse
import traceback

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

    Returns a list of OrderedDicts, each of which represents one clause
    (or fragment). The keys in each dict are the tokens which make up the
    clause, ordered according to their appearance in the string.
    """
    clauses = re.split(r'[\.\?;:,]', str)
    tokenized = []
    for c in clauses:
        token_dict = OrderedDict((unicode(makeutf8(t)), None)
                                 for t in c.split(' '))
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
        self.restring = args[0].strip() if args[0] else None
        self.structures = args[1]
        try:
            self.top = True if self.structures[-1] == 'top' else False
            if self.top:
                self.structures = self.structures[:-1]
        except IndexError:  # because no substructures
            pass
        print 'self.structures', self.structures
        print 'self.top', self.top

        self.classname = type(self).__name__

    def validate(self, validlfs, failedlfs=[]):
        """
        compare list of word tokens to definition of valid natural language expressions.

        clause should be Clause() object
        """
        validlfs = [validlfs] if isinstance(validlfs, OrderedDict) else validlfs
        # validate constituent structures recursively
        if self.structures:
            for s in self.structures:
                validlfs, failedlfs = s.validate(validlfs, failedlfs)
                if len(validlfs) < 1:
                    return validlfs, failedlfs

        # test sub-structure order for any viable leaves
        for idx, leaf in enumerate(validlfs):
            leaf, match = self.test_order(leaf)
            if not match:
                failedlfs.append(validlfs.pop(idx))
            if len(validlfs) < 1:
                return validlfs, failedlfs

        # find matching string for remaining viable leaves
        if self.restring:
            validlfs, failedlfs = self.match_string(validlfs, failedlfs)
            if len(validlfs) < 1:
                return validlfs, failedlfs

        # find any untagged words if this structure is top level
        if self.top:
            for v in validlfs:
                for w in v: print w,
                print ''
            for idx, leaf in enumerate(validlfs):
                untagged = [t for t, v in leaf.iteritems() if not v]
                if untagged:
                    failedlfs.append(validlfs.pop(idx))
                    print clr(['some extra words left over'], self.myc)
                    for w in untagged: print w
            if not validlfs:
                return False, validlfs, failedlfs
            else:
                return True, validlfs, failedlfs

        return validlfs, failedlfs

    def match_string(self, validleaves, failedleaves,
                     restring=None, classname=None):
        '''
        Identify token strings that match the current construction.

        tokens
        : The ordered list of strings conaining the actual utterance.
        '''

        restring = self.restring if not restring else restring
        classname = self.classname if not classname else classname

        test = re.compile(restring, re.U | re.I)
        mymatch = test.findall(' '.join(validleaves[0]))

        # TODO: split into leaves if (b) match already tagged
        def tag_token(matchstring, leaf):
            for word in matchstring.split(' '):  # allows for multi-word match strings
                try:
                    leaf[word].append(classname)
                except AttributeError:
                    leaf[word] = [classname]
            return leaf

        if mymatch:
            validleaves = [tag_token(m, leaf)
                           for leaf in validleaves for m in mymatch]
            #print clr('now working with {} leaves in parsing '
            #          'tree'.format(len(validleaves)), self.myc)
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

    def getform(self, lemid, **kwargs):
        """
        Return a list of possible declined forms for the supplied parsing.
        """
        from paideia_path_factory import Inflector
        myform = Inflector().get_db_form(kwargs, lemid)
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
        gram, lemid = self.parseform(nominal)
        kwargs = {'gender': gram['gender'],
                  'case': gram['case'],
                  'number': gram['number'],
                  'part_of_speech': 'def_art'
                  }
        myart = self.getform(lemid, **kwargs)[0]  # TODO: What about multiple matches?
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
            nominals = [t for t, v in tokens.iteritems() if v and 'Noun' in v]
            for n in nominals:
                tokens = self.find_article(n, tokens)
            structs = self.get_struct_order(tokens)
            for k, v in structs.iteritems(): print clr([k, v, ';'], self.myc),

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
