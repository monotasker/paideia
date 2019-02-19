#! /etc/bin/python
# -*- coding:utf-8 -*-

"""
Paideia Path Factory.

Copyright 2013—2014, Ian W. Scott

Provides classes for the procedural creation of paths/steps for the Paideia
web-app.

PathFactory:class
: This is the base class that handles generic path creation.

TranslateWordPathFactory:class (extends PathFactory)
: A subclass that includes extra helper logic for simple translation paths.

"""
#from ast import literal_eval
#from copy import copy
# import datetime
import functools
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB, UL, LI, SPAN
from gluon import CAT, H3
from itertools import product, chain
from kitchen.text.converters import to_unicode, to_bytes
from paideia_utils import check_regex, Uprinter
from plugin_utils import flatten, makeutf8, islist, capitalize_first
# from pprint import pprint
from random import randrange, shuffle
import re
import traceback
# from paideia_utils import simple_obj_print


class ResultCollector(object):

    def __init__(self, func):
        """
        Decorator class that collects db insertion attempts on session.results.

        This decorator expects the final return value of the wrapped function
        to hold information on the update attempts. This information should be
        a list (even if only one member) of 4-member tuples of the form
        (dbtablename, insertval, newrowid, errormessage).
        """
        self.func = func

    def __call__(self, *args, **kwargs):
        """docstring for __call__"""
        session = locals()['session'] if 'session' in list(locals().keys()) else current.session
        if 'results' not in list(session.keys()):
            session.results = []
        retvals = self.func(*args, **kwargs)
        myval = retvals
        if myval:
            for m in myval:
                session.results.append(m)
        return retvals

    def __repr__(self):
        """
        Return the wrapped function's docstring.
        """
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """
        Support instance methods
        """
        return functools.partial(self.__call__, obj)


class Inflector(object):
    """
    """
    def __init__(self):
        """docstring for __"""
        self.wf = WordFactory()

    def _wordform_from_parsing(self, parsedict, lemma):
        """
        Return the inflected form of the supplied lemma for the given parsing.

        Returns a string if successful and None if unsuccessful.
        """
        db = current.db

        def _make_constraint_string(parsedict):
            """
            Return a constraint string matching the provided parsing dict.
            """
            cst_pairs = ['{}@{}'.format(k, v) for k, v in list(parsedict.items())]
            constraint = '_'.join(cst_pairs)
            return constraint

        # a lambda function is stored as a string in a db field
        myconst = db.constructions[parsedict['construction']]
        funcstring = myconst['form_function']
        try:
            formfunc = eval(funcstring)
            #formfunc  = lambda w: w + makeutf8('ς')
            myform = formfunc(makeutf8(lemma))
        except SyntaxError:  # if an empty string
            myform = lemma

        # add to db.word_forms here
        constraint = _make_constraint_string(parsedict)
        newfreturn = self.wf.add_new_wordform(myform, lemma, None, constraint)

        return newfreturn[0][1]

    def make_form_agree(self, modform, mylemma,
                        constraint=None, modconstraint=None, session=None):
        """
        Return a form of the lemma "mylemma" agreeing with the supplied modform.
        # FIXME: session kwarg only used by decorator
        """
        db = current.db
        newforms = {}

        def _add_to_newforms(returnval, tablelist):
            for table in tablelist:
                idx = table[1]
                val = returnval[idx] if returnval[idx] else returnval[idx + 1]
                newforms.setdefault(table[0], []).append(val)

        def _get_lemma(mylemma, constraint):
            """
            """
            lem = db.lemmas(db.lemmas.lemma == mylemma)
            lemform = db.word_forms(db.word_forms.word_form == mylemma)
            if not lem:  # add new lemma in db
                lemreturn = self.wf.add_new_lemma(mylemma, constraint)
                # returns: lemma, lemid, err, formid, formerr, cstid, csterr
                lem = db.lemmas(lemreturn[1])
                if lemreturn[3] and not lemform:
                    lemform = db.word_forms(lemreturn[3])
                _add_to_newforms(lemreturn, [('lemmas', 1), ('word_forms', 3),
                                            ('constructions', 5)])
            return lem, lemform

        def _get_ref(modform, constraint):
            """
            Return the db record matching the supplied word form.

            If that form is not in the db, try to create it.

            """
            ref = db.word_forms(db.word_forms.word_form == modform)
            if modform and not ref:  # add new word_form to db for modform
                refreturn = self.wf.add_new_wordform(modform, None,
                                                None, modconstraint)
                # returns: word_form, rowid, err, new_cst_id, csterr
                ref = db.word_forms(refreturn[1])
                _add_to_newforms(refreturn, [('word_forms', 1), ('constructions', 3)])
            return ref

        def _get_part_of_speech(cst, lem):
            """
            """
            pos = cst['part_of_speech'] if cst and 'part_of_speech' in list(cst.keys()) \
                else lem.part_of_speech
            return pos

        def _get_declension(pos, lemform):
            """
            """
            assert lemform
            if not lemform['declension']:
                declension = MorphParser().infer_declension(mylemma)
            else:
                declension = lemform['declension']
            return declension

        def _get_property(cst, lemform, ref, prop, part_of_speech):
            defaults = {'tense': 'present',
                        'voice': 'active',
                        'person': '3',
                        'mood': 'indicative'}
            if cst and prop in list(cst.keys()):
                propval = cst[prop]
            elif ref and (prop in list(ref.keys())) and \
                    ref[prop] not in ['none', None] and \
                    ((prop != 'gender') or
                     (part_of_speech in ['adjective', 'article', 'pronoun'])):
                propval = ref[prop]
            elif prop == 'gender':
                propval = lemform[prop]
            elif prop in list(defaults.keys()):
                propval = defaults[prop]
            else:
                propval = None
            return propval

        def _get_construction_label(parsing):
            """"""
            pos = parsing['part_of_speech']
            cl = WordFactory().make_construction_label(pos, parsing)
            construction = cl[1].id if cl[1] else None
            return construction

        # gather the 3 sources influencing the target form's inflection
        lem, lemform = _get_lemma(mylemma, constraint)
        assert lem
        assert lemform
        ref = _get_ref(modform, modconstraint)
        cst = self.wf.parse_constraint(constraint)

        # collect full parsing from those sources, giving priority to cst
        parsing = {}
        mykeys = []
        parsing['part_of_speech'] = _get_part_of_speech(cst, lem)
        if parsing['part_of_speech'] == 'verb':
            mykeys.extend(['mood', 'tense', 'voice', 'person', 'number'])
            if 'mood' in list(parsing.keys()) and parsing['mood'] == 'participle':
                mykeys.extend(['gender', 'grammatical_case'])
                mykeys.pop(mykeys.index('person'))
            if 'mood' in list(parsing.keys()) and parsing['mood'] != 'infinitive':
                mykeys.pop(mykeys.index('number'))
                mykeys.pop(mykeys.index('person'))
        elif parsing['part_of_speech'] in ['noun', 'pronoun',
                                           'adjective', 'article']:
            parsing['declension'] = _get_declension(parsing['part_of_speech'],
                                                    lemform)
            mykeys.extend(['grammatical_case', 'gender', 'number'])
        # FIXME: add tags field
        for k in mykeys:
            parsing[k] = _get_property(cst, lemform, ref, k,
                                       parsing['part_of_speech'])
        # parsing['construction'] = _get_construction_label(parsing)  # must be last
        parsing['source_lemma'] = lem.lemma

        # get the inflected form's row from the db
        myrow, parsing = self.get_db_form(parsing, lem.id)
        try:
            myform = myrow.word_form
        except AttributeError:  # if there isn't one try to make it
            try:
                myform = self._wordform_from_parsing(parsing, lem.lemma)
                result = None
            except Exception:  # if making new form fails
                traceback.print_exc(5)
                myform = None

        return myform

    def _fill_missing_fields(self, parsing):
        """"""
        db = current.db
        # find fields missing from parsing keys
        pos = parsing['part_of_speech']
        if pos == 'verb' and parsing['mood'] in ['infinitive', 'participle']:
            reqs = self.wf.wordform_reqs['verb-{}'.format(parsing['mood'])]
        else:
            reqs = self.wf.wordform_reqs[pos]
        # now fill missing fields with None
        extra_fields = [f for f in db.word_forms.fields
                        if f not in reqs
                        and f not in list(parsing.keys())]
        for f in extra_fields:
            parsing[f] = 'none'
        return parsing

    def get_db_form(self, parsing, lemid):
        """
        Retrieve the db row that matches the supplied parsing and lemma id.
        """
        db = current.db

        '''
        def _gender_cats(gender):
            """
            Return a list of gender categories for an item of this gender.
            """
            genders = [gender, 'undetermined']
            if parsing['gender'] in ['masculine', 'feminine']:
                genders.append('masculine or feminine')
            if parsing['gender'] in ['masculine', 'neuter']:
                genders.append('masculine or neuter')
            return genders
        '''
        if 'construction' in list(parsing.keys()) and parsing['construction']:
            myrow = db((db.word_forms.source_lemma == lemid) &
                       (db.word_forms.construction == parsing['construction'])
                       ).select().first()
        else:
            parsing = self._fill_missing_fields(parsing)
            myrow = db((db.word_forms.source_lemma == lemid) &
                       (db.word_forms.grammatical_case == parsing['grammatical_case']) &
                       (db.word_forms.tense == parsing['tense']) &
                       (db.word_forms.voice == parsing['voice']) &
                       (db.word_forms.mood == parsing['mood']) &
                       (db.word_forms.person == parsing['person']) &
                       (db.word_forms.gender == parsing['gender']) &
                       (db.word_forms.number == parsing['number'])
                       ).select().first()
        return myrow, parsing


class MorphParser(object):
    """
    """
    nom_endings = {'ος': {'sfx': ['ος', 'ου', 'ῳ', 'ον', 'ε',
                                   'οι', 'ων', 'οις', 'ους', '--'],
                           'declension': '2',
                           'gender': 'masculine'},
                   'ον': {'sfx': ['ον', 'ου', 'ῳ', 'ον', 'ε',
                                   'α', 'ων', 'οις', 'α', '--'],
                           'declension': '2',
                           'gender': 'neuter'},
                   '(η|α)': {'sfx': ['(η|α)', '[ηα]ς', '(ῃ|ᾳ)', '[ηα]ν', 'ε',
                                  'αι', 'ων', 'αις', 'ας', '--'],
                          'declension': '1',
                          'gender': 'feminine'},
                   'ρ': {'sfx': ['ρ', 'ρος', 'ρι', 'ρα', '--',
                                  'ρες', 'ρων', 'ρι.ι', 'ρας', '--'],
                          'declension': '3',
                          'gender': None},
                   'ις': {'sfx': ['[^ε]ις', '(εως|ος)', 'ι', '(ιν|α)',
                                   '--', 'ε[ι]?ς', 'ων', '[ιε].ι',
                                   '(εις|ας)', 'ε[ι]?ς'],
                          'declension': '3',
                          'gender': None},
                   'υς': {'sfx': ['υς', 'υως', 'υι', 'υν', 'υ',
                                   'υες', 'υων', '--', 'υας', 'υες'],
                          'declension': '3',
                          'gender': None},
                   }

    def __init__(self):
        """Initialize a new MorphParser object."""
        pass

    def infer_part_of_speech(self, word_form):
        """
        Return a string giving the likely part of speech of the supplied form.
        """

        word_form = makeutf8(word_form)
        if (word_form[-1] == 'ω') or (word_form[-2:] == 'μι'):
            ps = 'verb'
        elif (word_form[-2:] in ['ος', 'υς', 'ης', 'ον']) or \
             (word_form[-1] in ['η', 'α']):
            ps = 'noun'
        elif word_form[-2:] == 'ως':
            ps = 'adverb'
        else:
            ps = None

        return ps

    def infer_declension(self, wordform):
        """
        Return a string giving the declension of the supplied nom. sing. noun.
        """
        wordform = to_unicode(wordform, encoding='utf8')
        end = [e for e in list(self.nom_endings.keys())
               if re.match('.*{}$'.format(e), wordform)]
        if end:
            declension = self.nom_endings[end[0]]['declension']
        else:
            if wordform in ['ὁ', 'το']:
                declension = '2'
            elif wordform in ['ἡ']:
                declension = '2'
            else:
                declension = '3'
        return declension

    def infer_case(self, wordform, lemma):
        """docstring for _infer_case"""
        cases = ['nominative', 'genitive', 'dative', 'accusative', 'vocative',
                 'nominative', 'genitive', 'dative', 'accusative', 'vocative']
        pass

    def infer_gender(self, wordform, lemma):
        """
        """
        pass

    def infer_pattern(self, wordform, lemma):
        """
        """
        pass

    def infer_parsing(self, word_form, lemma):
        """
        """
        word_form = makeutf8(word_form)
        lemma = makeutf8(lemma)
        case = None
        gender = None
        declension = None
        number = None
        cases = ['nominative', 'genitive', 'dative', 'accusative', 'vocative',
                 'nominative', 'genitive', 'dative', 'accusative', 'vocative']
        for k, v in list(self.nom_endings.items()):
            if re.match('.*{}$'.format(k), lemma):
                ends = [i for i in v['sfx']
                        if re.match('.*{}$'.format(i), word_form)]
                if ends:
                    if len(ends) == 1:
                        idx = v['sfx'].index(ends[0])
                        case = cases[idx]
                        number = 'singular' if idx < 5 else 'plural'
                    else:
                        idxs = [v['sfx'].index(e) for e in ends]
                        if all(i > 4 for i in idxs):
                            number = 'plural'
                        elif all(i <= 4 for i in idxs):
                            number = 'singular'
                        else:
                            number = None
                declension = v['declension']
                gender = v['gender']

                break

        return {'grammatical_case': case,
                'gender': gender,
                'number': number,
                'declension': '{}decl'.format(declension)}


class WordFactory(object):
    """
    An abstract parent class to create paths (with steps) procedurally.

    """
    cst_eqs = {'masculine': ['masc', 'm'],
               'feminine': ['fem', 'f'],
               'neuter': ['neut', 'n'],
               'nominative': ['nom', 'nomin'],
               'genitive': ['gen', 'g'],
               'dative': ['dat', 'd'],
               'accusative': ['acc', 'a'],
               'singular': ['s', 'si', 'sing'],
               'plural': ['p', 'pl', 'plu', 'plur'],
               'present': ['pr', 'pres'],
               'future': ['fut', 'ftr'],
               'aorist1': ['aor1', 'a1', '1a', '1aor'],
               'aorist2': ['aor2', 'a2', '2a', '2aor'],
               'perfect1': ['pf1', 'prf1', 'perf1', '1pf', '1prf', '1perf'],
               'perfect2': ['pf2', 'prf2', 'perf2', '2pf', '2prf', '2perf'],
               'imperfect': ['imp', 'impf', 'imperf'],
               'active': ['act'],
               'middle': ['mid'],
               'passive': ['pass'],
               'middle/passive': ['mp', 'midpass', 'mid/pass', 'm/p'],
               'indicative': ['ind', 'indic'],
               'imperative': ['imper', 'impv'],
               'infinitive': ['inf', 'infin'],
               'subjunctive': ['sj', 'sjv', 'sub', 'subj', 'sbj'],
               'optative': ['o', 'opt', 'optat', 'optv', 'opttv'],
               'participle': ['pt', 'ptc', 'part'],
               'noun': ['nn'],
               'pronoun': ['pn', 'prn', 'pron', 'pnn'],
               'adjective': ['ad', 'aj', 'adj', 'adject', 'adjv'],
               'verb': ['v', 'vb'],
               'adverb': ['av', 'adv', 'avb', 'advb'],
               'particle': ['partic', 'ptcl', 'pcl'],
               'interjection': ['ij', 'ijn', 'intj', 'inter', 'interj',
                               'interjn', 'ijtn'],
               'idiom': ['id', 'idm'],
               'first': ['1', '1p', '1pers'],
               'second': ['2', '2p', '2pers'],
               'third': ['3', '3p', '3pers']
               }

    parsing_abbrevs = {'acc': 'accusative',
                       'dat': 'dative',
                       'nom': 'nominative',
                       'gen': 'genitive',
                       'masc': 'masculine',
                       'fem': 'feminine',
                       'neut': 'neuter',
                       'any': 'undetermined',
                       'masc-fem': 'masculine or feminine',
                       'sing': 'singular',
                       'plur': 'plural',
                       'pron': 'pronoun',
                       'noun': 'noun',
                       'adj': 'adjective',
                       'verb': 'verb',
                       'adv': 'adverb',
                       'conj': 'conjunction',
                       'ptc': 'participle',
                       'ind': 'indicative',
                       'imper': 'imperative',
                       'inf': 'infinitive',
                       'part': 'particle',
                       '1': 'first',
                       '2': 'second',
                       '3': 'third',
                       's': 'singular',
                       'p': 'plural',
                       'act': 'active',
                       'mid': 'middle',
                       'pass': 'passive',
                       'mid-pass': 'middle or passive',
                       'atheme': 'alpha thematic',
                       'athm': 'alpha thematic',
                       'aconst': 'alpha construct',
                       'acst': 'alpha construct',
                       'econst1': 'epsilon construct 1',
                       'ecst1': 'epsilon construct 1',
                       'econst2': 'epsilon construct 2',
                       'ecst2': 'epsilon construct 2',
                       'oconst': 'omicron construct',
                       'ocst': 'omicron construct'
                       }

    const_abbrevs = {'3 decl epsilon': '3e',
                     '3 decl upsilon': '3u',
                     'alpha thematic': 'atheme',
                     'alpha construct': 'aconst',
                     'epsilon construct 1': 'econst1',
                     'epsilon construct 2': 'econst2',
                     'omicron construct': 'oconst',
                     'adjective': 'adj',
                     'pronoun': 'pron',
                     'article': 'art',
                     'conjunction': 'conj',
                     'aorist1': 'aor1',
                     'aorist2': 'aor2',
                     'perfect1': 'perf1',
                     'perfect2': 'perf2',
                     'present': 'pres',
                     'future': 'fut',
                     'imperfect': 'imperf',
                     '1': '1decl',
                     'first': '1decl',
                     '1decl': '1decl',
                     '2': '2decl',
                     'second': '2decl',
                     '2decl': '2decl',
                     '3': '3decl',
                     'third': '3decl',
                     '3decl': '3decl',
                     'singular': 'sing',
                     'plural': 'plur',
                     'active': 'act',
                     'passive': 'pass',
                     'middle': 'mid',
                     'indicative': 'ind',
                     'subjunctive': 'subj',
                     'optative': 'opt',
                     'participle': 'ptc',
                     'infinitive': 'inf',
                     'imperative': 'imper',
                     'nominative': 'nom',
                     'genitive': 'gen',
                     'dative': 'dat',
                     'accusative': 'acc',
                     'vocative': 'voc',
                     'masculine': 'masc',
                     'feminine': 'fem'
                     }

    tagging_conditions = {'verb basics': (['verb']),
                          'noun basics': (['noun']),
                          'adjectives': (['adj']),
                          'nominative 1': (['noun', 'nom', '1decl'],
                                          ['adj', 'nom', '1decl'],
                                          ['pron', 'nom', '1decl']),
                          'nominative 2': (['noun', 'nom', '2decl'],
                                          ['adj', 'nom', '2decl'],
                                          ['pron', 'nom', '2decl']),
                          'nominative 3': (['noun', 'nom', '3decl'],
                                          ['adj', 'nom', '3decl'],
                                          ['pron', 'nom', '3decl']),
                          'dative 1': (['noun', 'dat', '1decl'],
                                      ['adj', 'dat', '1decl'],
                                      ['pron', 'dat', '1decl']),
                          'dative 2': (['noun', 'dat', '2decl'],
                                      ['adj', 'dat', '2decl'],
                                      ['pron', 'dat', '2decl']),
                          'dative 3': (['noun', 'dat', '3decl'],
                                      ['adj', 'dat', '3decl'],
                                      ['pron', 'dat', '3decl']),
                          'genitive 1': (['noun', 'gen', '1decl'],
                                        ['adj', 'gen', '1decl'],
                                        ['pron', 'gen', '1decl']),
                          'genitive 2': (['noun', 'gen', '2decl'],
                                        ['adj', 'gen', '2decl'],
                                        ['pron', 'gen', '2decl']),
                          'genitive 3': (['noun', 'gen', '3decl'],
                                        ['adj', 'gen', '3decl'],
                                        ['pron', 'gen', '3decl']),
                          'accusative 1': (['noun', 'acc', '1decl'],
                                          ['adj', 'acc', '1decl'],
                                          ['pron', 'acc', '1decl']),
                          'accusative 2': (['noun', 'acc', '2decl'],
                                          ['adj', 'acc', '2decl'],
                                          ['pron', 'acc', '2decl']),
                          'accusative 3': (['noun', 'acc', '3decl'],
                                          ['adj', 'acc', '3decl'],
                                          ['pron', 'acc', '3decl']),
                          'vocative 1': (['noun', 'voc', '1decl'],
                                        ['adj', 'voc', '1decl'],
                                        ['pron', 'voc', '1decl']),
                          'vocative 2': (['noun', 'voc', '2decl'],
                                        ['adj', 'voc', '2decl'],
                                        ['pron', 'voc', '2decl']),
                          'vocative 3': (['noun', 'voc', '3decl'],
                                        ['adj', 'voc', '3decl'],
                                        ['pron', 'voc', '3decl']),
                          'nominative plural nouns '
                          'and pronouns': (['noun', 'nom', 'plur'],
                                           ['adj', 'nom', 'plur'],
                                           ['pron', 'nom', 'plur']),
                          'genitive plural nouns '
                          'and pronouns': (['noun', 'gen', 'plur'],
                                           ['adj', 'gen', 'plur'],
                                           ['pron', 'gen', 'plur']),
                          'dative plural nouns '
                          'and pronouns': (['noun', 'gen', 'plur'],
                                           ['adj', 'gen', 'plur'],
                                           ['pron', 'gen', 'plur']),
                          'accusative plural nouns'
                          'and pronouns': (['noun', 'acc', 'plur'],
                                           ['adj', 'acc', 'plur'],
                                           ['pron', 'acc', 'plur']),
                          'vocative plural nouns '
                          'and pronouns': (['noun', 'voc', 'plur'],
                                           ['adj', 'voc', 'plur'],
                                           ['pron', 'voc', 'plur']),
                          'present active infinitive': (['verb', 'pres',
                                                         'act', 'inf']),
                          'present active imperative': (['verb', 'pres',
                                                         'act', 'imper']),
                          'present active indicative': (['verb', 'pres',
                                                         'act', 'ind']),
                          'present middle-passive '
                          'indicative': (['verb', 'pres', 'mid', 'ind'],
                                         ['verb', 'pres', 'pass', 'ind']),
                          'aorist active '
                          'indicative': (['verb', '1aor', 'act', 'ind'],
                                         ['verb', '2aor', 'act', 'ind']),
                          'aorist middle '
                          'indicative': (['verb', '1aor', 'mid', 'ind'],
                                         ['verb', '2aor', 'mid', 'ind']),
                          }

    wordform_reqs = {'noun': ['source_lemma', 'grammatical_case', 'gender',
                              'number', 'declension'],
                     'adjective': ['source_lemma', 'grammatical_case',
                                   'gender', 'number', 'declension'],
                     'pronoun': ['source_lemma', 'grammatical_case', 'gender',
                                 'number', 'declension'],
                     'verb': ['source_lemma', 'tense', 'voice', 'mood',
                              'person', 'number'],
                     'verb-participle': ['source_lemma', 'tense', 'voice',
                                         'mood', 'case', 'gender', 'number',
                                         'declension'],
                     'verb-infinitive': ['source_lemma', 'tense', 'voice',
                                         'mood'],
                     'adverb': ['source_lemma'],
                     'particle': ['source_lemma'],
                     'conjunction': ['source_lemma'],
                     'article': ['source_lemma', 'case', 'gender', 'number'],
                     'idiom': ['source_lemma']}

    def __init__(self):
        """Initialize a new WordFactory object."""
        self.parser = MorphParser()

    def make_construction_label(self, part_of_speech, parsedict):
        """
        """
        db = current.db
        # don't include lemma in construction label
        cstbits = [parsedict[k] for k in self.wordform_reqs[part_of_speech][1:]]
        shortbits = [self.const_abbrevs[i] for i in cstbits
                     if i not in ['none', None]]
        construction_label = '{}_{}'.format(part_of_speech, '_'.join(shortbits))
        # FIXME: below is hack to fix confusion over ordinal numbers
        if re.search('verb', construction_label):
            construction_label = construction_label.replace('decl', '')
        construction_row = db.constructions(db.constructions.construction_label
                                            == construction_label)
        return construction_label, construction_row, cstbits, shortbits

    @ResultCollector
    def _add_new_construction(self, pos, const_label, constbits, shortbits):
        """
        Insert new db.constructions record and return id info
        """
        db = current.db
        rdbl = '{}, {}'.format(pos, ' '.join(constbits))
        rdbl = rdbl.replace(' first', ', first person ')
        rdbl = rdbl.replace(' second', ', second person ')
        rdbl = rdbl.replace(' third', ', third person ')
        rdbl = rdbl.replace(' 1decl', ', 1st declension ')
        rdbl = rdbl.replace(' 2decl', ', 2nd declension ')
        rdbl = rdbl.replace(' 3decl', ', 3rd declension ')
        mytags = [k for k, v in list(self.tagging_conditions.items())
                    for lst in v if all(l in shortbits for l in lst)]
        mytags = [t.id for t in db(db.tags.tag.belongs(mytags)).select()]
        try:
            cst_id = db.constructions.insert(**{'construction_label': const_label,
                                                'readable_label': rdbl,
                                                'tags': mytags})
            db.commit()
            csterr = None
        except Exception:
            cst_id = None
            traceback.print_exc()
            csterr = 'Could not write new construction {} ' \
                        'to db.'.format(const_label)

        return [('constructions', const_label, cst_id, csterr)]

    @ResultCollector
    def add_new_wordform(self, word_form, lemma, modform, constraint):
        """
        Attempt to insert a new word form into the db based on supplied info.

        If the insertion is successful, return the word form and the id of the
        newly inserted row from db.word_forms. Otherwise return False.

        """
        db = current.db

        parsing = self.parse_constraint(constraint)
        if not parsing:
            parsing = {}

        # get lemma and part of speech
        lemmarow = db.lemmas(db.lemmas.lemma == lemma)
        parsing['source_lemma'] = lemmarow.id
        pos = lemmarow.part_of_speech
        if not pos:
            pos = self.parser.infer_part_of_speech(word_form)
            lemmarow.update_record(part_of_speech=pos)
            db.commit()
        # try to get missing info from modform or word form itself
        reqs = self.wordform_reqs[pos]
        if pos == 'verb' and parsing['mood'] in ['infinitive', 'participle']:
            reqs = self.wordform_reqs['verb-{}'.format(parsing['mood'])]
        modrow = db.word_forms(db.word_forms.word_form == modform)
        guesses = self.parser.infer_parsing(word_form, lemma)
        for r in [i for i in reqs if i not in list(parsing.keys()) or not parsing[i]]:
            try:
                parsing[r] = modrow[r]
                assert parsing[r]
            except (AssertionError, KeyError, TypeError):
                try:
                    parsing[r] = guesses[r]
                except (KeyError, TypeError):
                    parsing[r] = None

        # add construction
        clreturn = self.make_construction_label(pos, parsing)
        const_label, const_row, constbits, shortbits = clreturn
        if const_row:
            cst_id = const_row.id
            new_cst_id = None
            csterr = None
        else:  # create new construction entry if necessary
            new_cst_id, csterr = self._add_new_construction(const_label, pos,
                                                            constbits, shortbits)
            cst_id = new_cst_id
        parsing['construction'] = cst_id

        # collect and add tags
        parsing['tags'] = []
        parsing.setdefault('tags', []).append(lemmarow.first_tag)
        parsing.setdefault('tags', []).extend(db.constructions(cst_id).tags)
        parsing.setdefault('tags', []).extend(lemmarow.extra_tags)
        parsing['tags'] = list(set(parsing['tags']))

        parsing['word_form'] = word_form

        try:
            if 'on' in list(parsing.keys()):
                del(parsing['on'])  # FIXME: where does this come from?
                del(parsing['part_of_speech'])  # FIXME: where does this come from?
                del(parsing['id'])  # FIXME: where does this come from?
                del(parsing['uuid'])  # FIXME: where does this come from?
            rowid = db.word_forms.insert(**parsing)
            db.commit()
            err = None
        except Exception:
            traceback.print_exc()
            msg = makeutf8('Could not write word_form {} to db.')
            err = msg.format(word_form)

        return [('word_forms', word_form, rowid, err)]

    def add_new_lemma(self, lemma, constraint):
        """
        Attempt to insert a new lemma into the db based on supplied info.

        If the insertion is successful, return True. If the info is not
        sufficient, return False.
        """
        db = current.db
        cd = self.parse_constraint(constraint)
        lemma_reqs = ['lemma', 'glosses', 'part_of_speech', 'first_tag',
                      'extra_tags', 'first_tag']
        lemdata = {k: i for k, i in list(cd.items()) if k in lemma_reqs}
        lemma = makeutf8(lemma)

        # get lemma field
        lemdata['lemma'] = lemma
        # get part_of_speech field
        if 'part_of_speech' not in list(lemdata.keys()):
            lemdata['part_of_speech'] = self.parser.infer_part_of_speech(lemma)

        # add tags based on part of speech and ending
        tags = []
        if lemdata['part_of_speech'] == 'verb':
            tags.append('verb basics')
            if lemma[-2:] == 'μι':
                tags.append('μι verbs')
        elif lemdata['part_of_speech'] == 'noun':
            tags.append('noun basics')
            if lemma[-2:] in ['ος', 'ης', 'ον']:
                tags.append('nominative 2')
            elif lemma[-2:] in ['υς', 'ις', 'ων', 'ηρ']:
                tags.append('nominative 3')
            elif lemma[-1] in ['η', 'α']:
                tags.append('nominative 1')
        elif lemdata['part_of_speech'] in ['adjective', 'pronoun', 'adverb',
                                           'particle', 'conjunction']:
            tags.append('{}s'.lemdata['part_of_speech'])

        # handle any space placeholders in tag names
        lemdata['first_tag'] = lemdata['first_tag'].replace('#', ' ')
        tags = [t.replace('#', ' ') for t in tags]
        lemdata['first_tag'] = db.tags(db.tags.tag == lemdata['first_tag']).id

        # populate 'tags_extra' field with ids
        tagids = [t.id for t in db(db.tags.tag.belongs(tags)).select()]
        lemdata['extra_tags'] = tagids

        # get 'glosses' field
        if 'glosses' in list(lemdata.keys()):
            lemdata['glosses'] = lemdata['glosses'].split('|')
            lemdata['glosses'] = [g.replace('#', ' ') for g in lemdata['glosses']]

        try:
            lemid = db.lemmas.insert(**lemdata)
            db.commit()
            err = None
        except Exception:
            traceback.print_exc()
            err = 'Could not write new lemma {} to db.'.format(lemma)
            lemid = None

        # Add a word_forms entry for this dictionary form of the lemma
        try:
            myform = db.word_forms(db.word_forms.word_form == lemma).id
            formid = None
            formerr = None
            cstid = None
            csterr = None
        except Exception:
            traceback.print_exc()
            form, formid, formerr, cstid, csterr = self.add_new_wordform(lemma, lemma, None, constraint)

        return lemma, lemid, err, formid, formerr, cstid, csterr

    def parse_constraint(self, constraint):
        """
        Return a dictionary of grammatical features based on a constraint string.

        """
        try:
            cparsebits = [b for b in constraint.split('_')]
            cdict = {b.split('@')[0]: b.split('@')[1] for b in cparsebits
                     if len(b.split('@')) > 1}

            # FIXME: This hack is necessary because underscores are used as
            # delimiters and in field names. Find a different delimiter.
            expts = [('thematic', 'pattern'),
                     ('part', 'of', 'speech'),
                     ('word', 'form'),
                     ('source', 'lemma'),
                     ('grammatical', 'case')]
            for e in expts:
                for ex in e[:-1]:
                    if ex in list(cdict.keys()):
                        del(cdict[ex])
                full_label = '_'.join(e)
                try:
                    cdict[full_label] = cdict[e[-1]]
                    del(cdict[e[-1]])
                except KeyError:
                    pass

            key_eqs = {'num': 'number',
                       'n': 'number',
                       'gen': 'gender',
                       'gend': 'gender',
                       'g': 'gender',
                       'c': 'grammatical_case',
                       'case': 'grammatical_case',
                       't': 'tense',
                       'v': 'voice',
                       'm': 'mood',
                       'pers': 'person',
                       'ps': 'part_of_speech',
                       'pos': 'part_of_speech',
                       'gls': 'glosses',
                       'gloss': 'glosses',
                       'gl': 'glosses',
                       'ft': 'first_tag',
                       'first': 'first_tag'}
            for k, v in list(cdict.items()):  # handle key short forms
                if k in list(key_eqs.keys()):
                    cdict[key_eqs[k]] = v
                    del cdict[k]
            for k, v in list(cdict.items()):  # handle value short forms
                if v in list(chain.from_iterable(list(self.cst_eqs.values()))):
                    expandedv = [kk for kk, vv in list(self.cst_eqs.items())
                                 if v in vv][0]
                    cdict[k] = expandedv
            return cdict
        except AttributeError:  # constraint is NoneType
            traceback.print_exc(5)
            return False

    def get_wordform(self, field, combodict, db=None):
        """
        Get the properly inflected word form for the supplied field.

        The expected field format is {lemma-modform-constraint}. For example,
        {αὐτος-words1-case:nom}. This will inflect the lemma αὐτος to agree with
        the current words1 except that the case will be constrained as
        nominative. If no constraint is given the lemma will be inflected to
        agree with the modform in all relevant aspects.

        """
        db = db if db else current.db
        splits = field.split('-')
        lemma = splits[0]
        try:
            mod = splits[1]
        except IndexError:
            mod = None
        try:
            constraints = splits[2]
        except IndexError:
            constraints = None

        # if lemma is pointer to a word list
        lemma = combodict[lemma] if lemma in list(combodict.keys()) else lemma

        # allow for passing inflected form instead of lemma
        if not db.lemmas(db.lemmas.lemma == lemma):
            myrow = db.word_forms(db.word_forms.word_form == lemma)
            lemma = myrow.source_lemma.lemma
        # inflect lemma to agree with its governing word
        modform = combodict[mod] if mod and mod not in ['', 'none'] else None

        myform = Inflector().make_form_agree(modform, lemma, constraints)

        return myform


class StepFactory(object):
    """
    An abstract parent class to create paths (with steps) procedurally.

    """
    def __init__(self):
        """docstring for __"""
        pass

    def _step_to_db(self, kwargs):
        """ """
        db = current.db
        try:
            sid = db.steps.insert(**kwargs)
            db.commit()
            return sid
        except Exception:
            traceback.print_exc(5)
            return False

    def make_step(self, combodict, sdata, mock, stepindex):
        """
        Create one step with given data.

        Returns a 2-member tuple.
        The first member is itself a 2-member tuple
        consisting of:

        [0] stepresult      : a string indicating the result of the step-creation
                              attempt

        [1] content         : the content of that attempt. This content can be
                              - a step id (if success)
                              - a dict of step field values (if testing)
                              - a list of duplicate steps (duplicates)
                              - an error traceback (if failure)

        The second member of the top-level tuple is a boolean indicating
        whether the step image was newly created (and so an image file will
        need to be added to the new db row).

        """
        mytype = sdata['step_type']

        ptemp = [to_unicode(pt) for pt in islist(sdata['prompt_template'])]
        xtemp = [to_unicode(rt) for rt in islist(sdata['response_template'])]
        rtemp = [to_unicode(dt) for dt in islist(sdata['readable_template'])]

        tags1 = sdata['tags'] if 'tags' in list(sdata.keys()) else None
        itemp = sdata['image_template']
        tags2 = sdata['tags_secondary'] if 'tags_secondary' in list(sdata.keys()) \
            else None
        tags3 = sdata['tags_ahead'] if 'tags_ahead' in list(sdata.keys()) else None
        npcs = sdata['npcs']
        locs = sdata['locations']
        points = sdata['points'] if 'points' in list(sdata.keys()) and sdata['points'] \
            else 1.0, 0.0, 0.0
        instrs = sdata['instructions'] if 'instructions' in list(sdata.keys()) \
            else None
        hints = sdata['hints'] if 'hints' in list(sdata.keys()) else None
        img = self._make_image(combodict, itemp) if itemp else None
        imgid = img[0] if img else None
        # ititle = img[1] if img else None
        images_missing = img[2] if img else None

        pros, rxs, rdbls = self._format_strings(combodict, ptemp, xtemp, rtemp)
        rdbls = [r for r in islist(rdbls) if isinstance(r, str)]
        if len(rdbls) >= 1:
            rdbls = '|'.join(rdbls)
        else:
            rdbls = ['']
        tags = self.get_step_tags(tags1, tags2, tags3, pros, rdbls)
        kwargs = {'prompt': pros[randrange(len(pros))],  # sanitize_greek(pros[randrange(len(pros))]),
                  'widget_type': mytype,
                  # 'widget_audio': None,
                  'widget_image': imgid,
                  'response1': islist(rxs)[0],
                  'readable_response': rdbls,  # sanitize_greek(rdbls)]),
                  'outcome1': points[0],
                  'response2': rxs[1] if len(rxs) > 1 else None,
                  'outcome2': points[1],
                  'response3': rxs[2] if len(rxs) > 2 else None,
                  'outcome3': points[2],
                  'tags': tags[0],
                  'tags_secondary': tags[1],
                  'tags_ahead': tags[2],
                  'npcs': npcs,  # [randrange(len(npcs))] if multiple
                  'locations': locs,
                  'instructions': instrs,
                  'hints': hints}  # [randrange(len(npcs))] if mult

        try:
            # test readable responses against regexes
            matchdicts = []
            for x in rxs:
                my_rdbls = rdbls.split('|')
                results = []
                for m in my_rdbls:
                    results.append(check_regex(x, m))
                resultdict = {x: all(r for r in results)}
                matchdicts.append(resultdict)

            xfail = {}
            for idx, regex in enumerate(rxs):
                if mytype not in [3]:
                    mtch = all(matchdicts[idx].values())
                else:
                    mtch = True  # not expecting response to test
                if not mtch:
                    problems = [k for k, v in list(matchdicts[idx].items())
                                if not v]
                    xfail[regex] = problems
            dups = check_for_duplicates(kwargs, rdbls, pros)
            if mtch and not dups[0] and not mock:
                stepresult = self._step_to_db(kwargs), kwargs
            elif mtch and not dups[0] and mock:
                stepresult = 'testing{}'.format(stepindex), kwargs
            elif mtch and dups[0]:
                stepresult = 'duplicate step {}'.format(stepindex), dups
            else:
                stepresult = 'regex failure {}'.format(stepindex), xfail
        except Exception:
            traceback.print_exc(12)
            stepresult = ('failure')

        return stepresult, images_missing

    def _make_image(self, combodict, itemp):
        """
        Check for an image for the given combo and create if necessary.

        If a new image record is created, this method also adds its id and
        title directly to the instance variable images_missing.

        """
        db = current.db
        image_missing = False
        mytitle = itemp.format(**combodict)
        img_row = db(db.images.title == mytitle).select().first()
        if not img_row:
            myid = db.images.insert(title=mytitle)
            db.commit()
            image_missing = True
        else:
            myid = img_row.id

        return myid, mytitle, image_missing

    def _format_strings(self, combodict, ptemps, xtemps, rtemps):
        """
        Return a list of the template formatted with each of the words.

        The substitution format in each string looks like:
        {wordsX}        preset word form, simple string substitution
        {lemma-modform-constraint}  "lemma" parsed to agree with "modform" before
                                    substitution. The third term "constraint" is
                                    an optional limitation on the aspects of the
                                    lemma to be made to agree. The constraint
                                    should be formatted like "case:nom", in
                                    which case the case would be constrained
                                    as nominative, while all other aspects of
                                    the lemma would be brought into agreement
                                    with "modform".

        """
        prompts = [capitalize_first(self._do_substitution(p, combodict))
                   for p in ptemps]
        if xtemps not in ['', None]:
            rxs = []
            for x in xtemps:
                if re.search(r'{', x):
                    rxs.append(self._do_substitution(x, combodict, regex=True))
                else:
                    rxs.append(x)
        else:
            rxs = None
        if rtemps not in ['', None]:
            rdbls = []
            for r in rtemps:
                if re.search(r'{', r):
                    r = self._do_substitution(r, combodict)
                if re.match(r'.*[\.\?;\!]', r):
                    r = capitalize_first(r)
                rdbls.append(r)
        else:
            rdbls = None
        return prompts, rxs, rdbls

    def _add_caps_option(self, myform):
        """
        Reformat string to add regex syntax for the first letter to be capitalized.
        """
        myform = to_unicode(myform, encoding='utf8')
        first = myform[:1]
        cap = first.upper()
        rest = myform[1:]
        myform = '({}|{}){}'.format(first, cap, rest)
        myform = to_bytes(myform, encoding='utf8')
        return myform

    def _do_substitution(self, temp, combodict, regex=False):
        """
        Make the necessary replacements for the suplied template string.

        Returns a list of strings, one for each valid combination of words
        supplied in the combodict parameter.
        """
        ready_strings = []
        subpairs = {}

        fields = re.findall(r'(?<={).*?(?=})', temp)
        if not fields:
            return temp
        inflected_fields = [f for f in fields if len(f.split('-')) > 1]
        for f in fields:
            if f in inflected_fields:
                myform = to_unicode(WordFactory().get_wordform(f, combodict))
            else:
                myform = to_unicode(combodict[f])
            subpairs[f] = to_unicode(self._add_caps_option(myform) if regex else myform)
        ready_strings = temp.format(**subpairs)
        return ready_strings

    def get_step_tags(self, tags1, tags2, tags3, prompts, rdbls):
        """
        Return a 3-member tuple of lists holding the tags for the current step.
        """
        db = current.db
        tags1 = islist(tags1) if tags1 else []
        tags2 = islist(tags2) if tags2 else []
        tags3 = islist(tags3) if tags3 else []

        words = [p.split(' ') for p in prompts]
        try:
            words.extend([r[0].split(' ') for r in rdbls
                          if r[0] not in ['', None]])
        except IndexError:
            pass
        allforms = list(chain(*words))
        allforms = list(set(allforms))

        # Get tags for all lemmas and forms in allforms
        # TODO: Should allforms include all words or only substitutions?
        formrows = db((db.word_forms.word_form.belongs(allforms)) &
                      (db.word_forms.construction == db.constructions.id)
                      ).select()
        constags = [f.constructions.tags for f in formrows]
        formtags = [f.word_forms.tags for f in formrows]
        firsttags = [f.word_forms.source_lemma.first_tag for f in formrows]
        xtags = [f.word_forms.source_lemma.extra_tags for f in formrows]

        newtags = list(chain(constags, formtags, firsttags, xtags))
        newtags = list(set(flatten(newtags)))
        # assume at first that all form tags are secondary
        tags2.extend(newtags)

        newtags1, newtags2, newtags3 = [], [], []
        tagsets = [t for t in [tags1, tags2, tags3] if t]
        alltags = sorted(list(chain(*tagsets)))
        tagrows = db(db.tags.id.belongs(alltags)).select(db.tags.id,
                                                         db.tags.tag_position)
        steplevel = max([t.tag_position for t in tagrows if t.tag_position < 999])
        for t in tagrows:
            if t.tag_position == steplevel:
                newtags1.append(t.id)
            elif t.tag_position < steplevel:
                newtags2.append(t.id)
            else:
                newtags3.append(t.id)

        return (newtags1, newtags2, newtags3)


class PathFactory(object):
    """
    An abstract parent class to create paths (with steps) procedurally.

    """
    def __init__(self):
        """Initialize a paideia.PathFactory object."""
        self.promptstrings = []
        self.mock = True  # switch to activate testing mode with db clean-up
        self.parser = MorphParser()

    def make_create_form(self):
        """
        Returns a form to make a translate-word path and processes the form on
        submission.

        This form, when submitted, calls self.

        """
        request = current.request
        db = current.db
        message = ''
        output = ''
        flds = [Field('label_template', 'string'),
                Field('words', 'list:string'),
                Field('aligned', 'boolean'),
                Field('avoid', 'list:string'),
                Field('testing', 'boolean')]

        """
        myajax = lambda field, value: AjaxSelect(field, value, indx=1,
                                                 multi='basic',
                                                 lister='simple',
                                                 orderby='tag'
                                                 ).widget()
        """

        for n in ['one', 'two', 'three', 'four', 'five']:
            fbs = [Field('{}_prompt_template'.format(n), 'list:string'),
                   Field('{}_response_template'.format(n), 'list:string'),
                   Field('{}_readable_template'.format(n), 'list:string'),
                   Field('{}_tags'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True)),
                   Field('{}_tags_secondary'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True)),
                   Field('{}_tags_ahead'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True)),
                   Field('{}_npcs'.format(n), 'list:reference npcs',
                         requires=IS_IN_DB(db, 'npcs.id', '%(name)s',
                                           multiple=True)),
                   Field('{}_locations'.format(n), 'list:reference locations',
                         requires=IS_IN_DB(db, 'locations.id',
                                           '%(map_location)s',
                                           multiple=True)),
                   Field('{}_instructions'.format(n),
                         'list:reference step_instructions',
                         requires=IS_IN_DB(db, 'step_instructions.id',
                                           '%(instruction_label)s',
                                           multiple=True)),
                   Field('{}_hints'.format(n), 'list:reference step_hints',
                         requires=IS_IN_DB(db, 'step_hints.id',
                                           '%(hint_label)s',
                                           multiple=True)),
                   Field('{}_step_type'.format(n), 'list:reference step_types',
                         requires=IS_IN_DB(db, 'step_types.id',
                                           '%(step_type)s',
                                           multiple=True)),
                   Field('{}_image_template'.format(n), 'string')]
            flds.extend(fbs)
        form = SQLFORM.factory(*flds)

        if form.process(keepvalues=True).accepted:
            vv = request.vars
            stepsdata = []
            for n in ['one', 'two', 'three', 'four', 'five']:
                nkeys = [k for k in list(vv.keys()) if re.match('{}.*'.format(n), k)]
                filledfields = [k for k in nkeys if vv[k] not in ['', None]]
                if filledfields:
                    ndict = {k: vv[k] for k in nkeys}
                    stepsdata.append(ndict)
            if isinstance(vv['words'], list):
                wordlists = [to_unicode(w).split('|') for w in vv['words']]
            else:
                wordlists = [to_unicode(vv['words']).split('|')]
            paths = self.make_path(wordlists,
                                   label_template=vv.label_template,
                                   stepsdata=stepsdata,
                                   testing=vv.testing,
                                   avoid=vv.avoid,
                                   aligned=vv.aligned
                                   )
            message, output = self.make_output(paths)

        elif form.errors:
            message = BEAUTIFY(form.errors)

        return form, message, output

    def make_path(self, wordlists, label_template=None, stepsdata=None,
                  avoid=None, aligned=False, testing=False):
        """
        Create a set of similar paths programmatically from provided variables.

        Required positional argument
        ------------------

        wordlists (list of lists)   -- each of the contained lists is one set
                                        of replacement words (which can be
                                        substituted in the same field within
                                        any of the template strings).

        Required keyword arguments
        ------------------

        label_template (str)        -- a single string with substitution fields
                                        to be used for building the labels for
                                        each new path
        stepdata (list of dicts)    -- each dictionary

        Optional keyword arguments
        ------------------

        avoid (list of tuples)      -- each tuple specifies an invalid
                                        combinations of lemmas which should
                                        be avoided in assembling step
                                        variations.

        Required keys in stepdata dictionaries
        ------------------

        widget_type (int)           -- the id of the widget-type appropriate
                                        to this step.
        prompt_template (list)      -- list of strings with {} marking fields
                                        for lemmas to be replaced.
        response_template (str)     -- string with {} marking fields for
                                        lemmas to be replaced.
        readable_template (list)    -- string with {} marking fields for
                                        lemmas to be replaced.
        npcs (list)                 -- npc id's (int) which are valid for
                                        the steps
        locs (list)                 -- id's (int) for location in which the
                                        steps can be performed
        image_template (str)
        tags (list of ints)
        tags_secondary (list of ints)
        tags_ahead (list of ints)

        Optional keyword arguments
        ------------------
        points (tuple of doubles)   -- point value for each of the responses

        Return values
        --------------------
        The method returns a single list. Each member is a dictionary
        representing the result of the attempt to create a single path. Each
        of these dictionaries has the following keys:

        path id (int)           : id of the path created (or string indicating
                                why a path was not made: 'duplicate',
                                'failure', 'testing').
        steps (dict)            : keys are either path ids or a string
                                indicating why no step was created. The value
                                for each step is either a dict of the values
                                passed for step creation, a list of duplicate
                                step ids, or a string indicating failure.
        new_forms (dict)        : keys are the names of db tables, values are
                                each either a rowid (long) or an error
                                message (str).
                                added to db.word_forms during step creation.
        images_missing (list)   : A list of ids for newly created image records.
                                These will need to be populated with the actual
                                images manually.

        """
        session = current.session
        if testing is None:
            self.mock = False
        else:
            self.mock = True

        combos = self.make_combos(wordlists, aligned, avoid)
        paths = {}
        for idx, c in enumerate(combos):  # one path for each combo
            mykeys = ['words{}'.format(n + 1) for n in range(len(c))]
            combodict = dict(list(zip(mykeys, c)))  # keys are template placeholders
            label = to_unicode(label_template).format(**combodict)

            pdata = {'steps': {}, 'new_forms': {}, 'images_missing': []}
            for i, s in enumerate(stepsdata):  # each step in path
                # sanitize form response =============================="
                numstrings = ['one_', 'two_', 'three_', 'four_', 'five_']
                sdata = {k.replace(numstrings[i], ''): v for k, v in list(s.items())}
                # create steps ========================================"
                stepdata, imgs = StepFactory().make_step(combodict,
                                                         sdata,
                                                         self.mock,
                                                         i)
                # collect result ======================================"
                pdata['steps'][stepdata[0]] = stepdata[1]
                newforms = session.newforms if 'newforms' in list(session.keys()) \
                    else None
                if newforms:
                    for k, f in list(newforms.items()):
                        pdata['new_forms'].setdefault(k, []).append(f)
                if imgs:
                    pdata['images_missing'].append(imgs)
            pgood = [isinstance(k, int) for k in list(pdata['steps'].keys())]
            print('making paths', list(pdata['steps'].keys()))
            pid = self.path_to_db(list(pdata['steps'].keys()), label) \
                if all(pgood) and not self.mock else 'path not written {}'.format(idx)
            paths[pid] = pdata
        return paths

    def make_combos(self, wordlists, aligned, avoid):
        """
        Return a list of tuples holding all valid combinations of given words.

        If 'aligned' is True, the word lists will be combined with a simple
        zip. Otherwise, they are combined with product(). The 'avoid' parameter
        expects a list of tuples, each providing a combination to be excluded.

        """
        if len(wordlists) > 1 and aligned:
            combos = list(zip(*wordlists))
        elif len(wordlists) > 1:
            combos = list(product(*wordlists))
        else:
            combos = [(l,) for l in wordlists[0] if l]
            combos = [tup for tup in combos if tup]
        if avoid:
            combos = [x for x in combos
                      if not any([set(y).issubset(set(x)) for y in avoid])]
        return combos

    def path_to_db(self, steps, label):
        """ """
        db = current.db
        try:
            pid = db.paths.insert(label=label, steps=steps)
            db.commit()
            return pid
        except Exception:
            traceback.print_exc(5)
            return False

    def make_output(self, paths):
        """
        Return formatted output for the make_path view after form submission.

        """
        db = current.db
        opts = {'goodpaths': {p: v for p, v in list(paths.items())
                              if isinstance(p, int)},
                'badpaths': {p: v for p, v in list(paths.items())
                             if not isinstance(p, int)}}
        outs = {'goodpaths': UL(),
                'badpaths': UL()}
        newforms = []
        images = []

        for opt in ['goodpaths', 'badpaths']:
            badcount = 0

            for pk, pv in list(opts[opt].items()):
                if opt == 'badpaths':
                    badcount += 1

                successes = [s for s in list(pv['steps'].keys())
                             if s not in ['failure', 'duplicate step']]
                failures = [s for s in list(pv['steps'].keys()) if s == 'failure']
                duplicates = [s for s in list(pv['steps'].keys()) if s == 'duplicate step']

                pout = LI('Path: {}'.format(pk))

                psub = UL()
                psub.append(LI(SPAN('steps succeeded', _class='ppf_label'),
                               len(successes)))
                psub.append(LI(SPAN('steps failed', _class='ppf_label'),
                               len(failures)))
                psub.append(LI(SPAN('steps were duplicates', _class='ppf_label'),
                               len(duplicates)))
                content = pv['steps']

                mycontent = UL()
                UP = Uprinter()
                for key, c in list(content.items()):

                    mycontent.append(LI(key))
                    mystep = UL()

                    if isinstance(key, str) and re.match('regex failure', key):
                        mystep = UL()
                        mystep.append(LI(SPAN('regex: ', _class='regex_error'),
                                         list(c.keys())[0]))
                        mystep.append(LI(SPAN('readable: ', _class='regex_error'),
                                         ' '.join(list(c.values())[0])))
                    else:
                        wt = db.step_types(c['widget_type']).step_type \
                            if 'widget_type' in c else 'None'
                        mystep.append(LI(SPAN('widget_type', _class='ppf_label'),
                                        wt))
                        mystep.append(LI(SPAN('prompt', _class='ppf_label'),
                                        makeutf8(c['prompt'])))
                        mystep.append(LI(SPAN('readable_response', _class='ppf_label'),
                                        makeutf8(c['readable_response'])))
                        mystep.append(LI(SPAN('response1', _class='ppf_label'),
                                        makeutf8(c['response1'])))
                        mystep.append(LI(SPAN('outcome1', _class='ppf_label'),
                                        c['outcome1']))
                        mystep.append(LI(SPAN('response2', _class='ppf_label'),
                                        makeutf8(c['response2'])
                                    if c['response2'] else None))
                        mystep.append(LI(SPAN('outcome2', _class='ppf_label'),
                                        c['outcome2']))
                        mystep.append(LI(SPAN('response3', _class='ppf_label'),
                                        makeutf8(c['response3'])
                                        if c['response3'] else None))
                        mystep.append(LI(SPAN('outcome3', _class='ppf_label'),
                                        c['outcome3']))
                        tags = [t['tag'] for t in
                                db(db.tags.id.belongs(c['tags'])).select()]
                        mystep.append(LI(SPAN('tags', _class='ppf_label'),
                                        ', '.join(tags)))
                        tags_secondary = [t['tag'] for t in
                                          db(db.tags.id.belongs(c['tags_secondary'])
                                             ).select()]
                        mystep.append(SPAN(LI('tags_secondary', _class='ppf_label'),
                                        ', '.join(tags_secondary)))
                        tags_ahead = [t['tag'] for t in
                                      db(db.tags.id.belongs(islist(c['tags_ahead']))
                                         ).select()]
                        mystep.append(LI(SPAN('tags_ahead', _class='ppf_label'),
                                        ', '.join(tags_ahead)))
                        npcs = [makeutf8(t['name']) for t in
                                db(db.npcs.id.belongs(islist(c['npcs']))).select()]
                        mystep.append(LI(SPAN('npcs', _class='ppf_label'),
                                        ', '.join(npcs)))
                        # print 'locations:', islist(c['locations'])
                        locations = [makeutf8(t['map_location']) for t in
                                     db(db.locations.id.belongs(islist(c['locations']))
                                        ).select()
                                     ]
                        mystep.append(LI(SPAN('locations', _class='ppf_label'),
                                        ', '.join(locations)))
                        lemmas = [t['lemma'] for t in
                                db(db.lemmas.id.belongs(c['lemmas'])).select()] \
                            if 'lemmas' in list(c.keys()) else 'None'
                        mystep.append(LI(SPAN('lemmas', _class='ppf_label'),
                                        ', '.join(lemmas)
                                        if lemmas else 'None'))
                        mystep.append(LI(SPAN('status', _class='ppf_label'),
                                        db.step_status(c['status']).status_label
                                        if 'status' in list(c.keys()) else 'None'))
                        instructions = [t['instruction_label'] for t in
                                        db(db.step_instructions.id.belongs(c['instructions'])
                                           ).select()] if c['instructions'] else 'None'
                        mystep.append(LI(SPAN('instructions', _class='ppf_label'),
                                        ', '.join(instructions)
                                        if instructions else 'None'))
                        hints = [t['hint_label'] for t in
                                db(db.step_hints.id.belongs(c['hints'])).select()] \
                            if 'hints' in list(c.keys()) and c['hints'] else 'None'
                        mystep.append(LI(SPAN('hints', _class='ppf_label'),
                                        ', '.join(hints)))
                    mycontent.append(LI(mystep))

                psub.append(mycontent)
                pout.append(psub)

                outs[opt].append(pout)

        output = CAT(H3('successes'), outs['goodpaths'],
                     H3('failures'), outs['badpaths'])

        message1 = 'Created {} new paths.'.format(len(outs['goodpaths'])) \
                   if len(outs['goodpaths']) else 'No new paths'
        message2 = '{} paths failed'.format(len(outs['badpaths'])) \
                   if len(outs['badpaths']) else 'No paths failed'
        nf = 'new word forms entered in db:\n{}'.format(BEAUTIFY(newforms))
        imgs = 'images needed for db:\n{}'.format(BEAUTIFY(images))
        message = message1 + '\n' + message2 + '\n' + nf + '\n' + imgs

        return (message, output)


class TranslateWordPathFactory(PathFactory):

    """
    Factory class to create paths for translating a single word from Greek to
    English.

    """

    def __init__(self):
        """
        Initialise a TranslateWordPathFactory object.
        """
        self.path_label_template = 'Meaning? {}'
        self.irregular_forms = {}
        self.prompt_template = ['Τί σημαινει ὁ λογος οὑτος? {}',
                                'Ὁ λογος οὑτος τί σημαινει? {}',
                                'Σημαινει ὁ λογος οὑτος τί? {}',
                                'Οὑτος ὁ λογος τί σημαινει? {}',
                                'Σημαινει τί ὁ λογος οὑτος? {}']

    def get_templates(self, lemid, cst):
        """
        """
        db = current.db
        cstrow = db.constructions(cst)
        lemrow = db.lemmas(lemid)
        lemma = lemrow.lemma
        glosses = lemrow.glosses
        gstring = '|'.join(glosses)
        response_template = [cstrow.trans_regex_eng.replace('{}', gstring)]
        readable_template = [c.replace('{}', g) for g in glosses
                             for c in cstrow.trans_templates]
        prompt_template = [t.replace('{}', lemma) for t in self.prompt_template]
        return prompt_template, response_template, readable_template

    def make_create_form(self):
        """
        Returns a form to make a translate-word path and processes the form on
        submission.

        This form, when submitted, calls self.

        """
        request = current.request
        db = current.db
        message = ''
        output = ''
        form = SQLFORM.factory(Field('lemma', db.lemmas,
                                     requires=IS_IN_DB(db, 'lemmas.id',
                                                       '%(lemma)s'),
                                     ),
                               Field('irregular_forms', type='list:string'),
                               Field('testing', type='boolean'))
        if form.process(keepvalues=True).accepted:
            lemid = request.vars.lemma
            assert isinstance(lemid, int)
            irregs = request.vars.irregular_forms
            self.irregular_forms = {f.split('|')[0]: f.split('|')[1]
                                    for f in irregs}  # TODO: activate these
            stepdata = {'step_type': 1,
                        'npcs': self.pick_npcs,
                        'locations': self.pick_locations,
                        'instructions': None,
                        'hints': None}
            for c in self.get_constructions(lemid):
                assert isinstance(c, int)
                temps = self.get_templates(lemid, c)  # do substitutions already
                stepdata['prompt_template'] = to_unicode(temps[0])  # do substitutions already
                stepdata['response_template'] = to_unicode(temps[1])
                stepdata['readable_template'] = to_unicode(temps[2])
                paths, result = self.make_path([[request.vars.lemma]],
                                               label_template=self.label_template,
                                               stepdata=[stepdata])
            message, output = self.make_output(paths, result)
        elif form.errors:
            message = BEAUTIFY(form.errors)

        return form, message, output

    def make_combos(self, lemma):
        return [(lemma,)]

    def get_constructions(self, lemma):
        """
        Return a list of constructions that need a path for the given lemma.

        The returned value is a list of strings, each of which is the
        'construction_label' value for a db.constructions row.
        """
        if lemma['part_of_speech'] == 'verb':
            self.tenses = ['pres', 'aor', 'imperf', 'perf']
            self.voices = ['_act', '_mid', '_pass']
            self.moods = ['_ind', '_imper', '_inf']
            self.persons = ['_{}'.format(n) for n in range(1, 4)]
            self.numbers = ['s', 'p']
            # TODO: this is very high loop complexity; move to db as fixed list
            self.verbcs = ['{}{}{}{}{}'.format(t, v, m, p, n)
                           for m in self.moods
                           for t in self.tenses
                           for v in self.voice
                           for p in self.persons
                           for n in self.numbers
                           if not (m == '_inf')
                           and not (m == '_imper' and p in ['_1', '_3'])]
            self.verbcs2 = ['{}{}{}'.format(t, v, m)
                            for m in self.moods
                            for t in self.tenses
                            for v in self.voice
                            if (m == '_inf')]
            self.verbcs = self.verbcs.extend(self.verbcs2)
            return self.verbcs
        # TODO: add conditions for other parts of speech
        else:
            return False

    def get_prompt(self, word_form):
        """
        Return the specific prompt to be presented in the step.
        """
        pstrings = self.promptlist if self.promptlist else \
            self.get_prompt_list(word_form)
        pstring = pstrings[randrange(len(pstrings))]
        return pstring

    def get_prompt_list(self, word_form):
        """
        Return a list of all valid prompt strings for this step.
        """
        plist = [s.format(word_form) for s in self.promptstrings]
        self.promptlist = plist
        return plist

    def get_readable_list(self):
        """
        """
        pass

    def make_glosses(self, lemma, cst):
        """
        Return a list of valid glosses for the supplied lemma and construction.
        """
        pass

    def get_form(self, lemma, cst):
        db = current.db
        prefab = db((db.word_forms.lemma == lemma.id) &
                   (db.word_forms.construction == cst.id)).select()
        if prefab:
            return prefab[0]['word_form']
        else:
            return cst['form_function'](lemma)

    def get_step_tags(self, lemma, cst_row):
        """
        Return a 3-member tuple of lists holding the tags for the current step.
        """
        tags = cst_row['tags']
        if lemma.extra_tags:
            tags.extend(lemma.extra_tags)
        tags = list(set(tags))
        tags2 = list(set(tags))
        tagsA = list(set(tags))
        return (tags, tags2, tagsA)

    def make_readable(self, lemma, construction):
        """
        Return a list of readable glosses using the given template and a
        string of glosses separated by |.

        This includes removing or doubling the final letters of the gloss as
        needed (e.g., before -ing, -ed, -er).
        """
        readables = []
        glosses = lemma['glosses']
        templates = construction['trans_templates']
        for gloss in glosses:
            for tplt in templates:
                tplt_parts = tplt.split('{}')
                if len(tplt_parts) == 2:
                    suffix = re.match('^\(?(ing|ed|er)\)?', tplt_parts[1])
                    if suffix:
                        if re.match('e$', gloss):
                            gloss = gloss[:-1]
                        if re.match('p$', gloss) and (suffix.group() != 'ing'):
                            gloss = '{}p'.format(gloss)
                        if re.match('y$', gloss) and (suffix.group() != 'ing'):
                            gloss = '{}ie'.format(gloss[:-1])
                readables.append(tplt.format(gloss))
        shuffle(readables)
        readable_string = '|'.join(readables[:7])

        return (readables, readable_string)

    def make_regex(self, myglosses, raw):
        """
        Return the complete regex string based on a list of word myglosses and
        a template regex string.
        """
        for i, v in enumerate(myglosses):
            t = v.split('|')
            if len(t) > 1:
                myglosses[i] = '{}({})?'.format(t[0], t[1])
        gloss_string = '|'.join(myglosses)
        regex = raw.format(gloss_string)
        return regex


def check_for_duplicates(step, readables, prompt):
    """
    Returns a 2-member tuple identifying whether there is a duplicate in db.

    tuple[0] is a boolean (True mean duplicate is present in db)
    tuple[1] is an integer (the row id of any duplicate step found)
    So negative return value is (False, 0).

    """
    db = current.db
    db_steps = db(db.steps.id > 0).select(db.steps.id,
                                            db.steps.prompt,
                                            db.steps.readable_response)
    for dbs in db_steps:
        db_readables = dbs.readable_response.split('|')
        if dbs.prompt == prompt and [r for d in db_readables
                                        for r in readables if r == d]:
            return True, dbs.id
        else:
            pass
    return False, 0


"""

    εὐγε
    εἰ δοκει
    *ἀκουω
    *ποιεω
        Τί ποιεις Στεφανος?
    *διδωμι
        Τί αύτη διδει?
        Τίς διδει τουτον τον δωρον?

    *φερω
    *θελω
        θελεις συ πωλειν ἠ ἀγοραζειν?
        Ποσα θελεις ἀγοραζειν?
    *ζητεω
    *τιμαω
        τιμαω
    *λαμβανω
    *ἀγοραζω
        Βαινε και ἀγοραζε τρεις ἰχθυας.
    *πωλεω
        Τί πωλεις Ἀλεξανδρος?
    *βλεπω
    *βαινω
    *ἐχω
    *ὁραω
    *σημαινω
    *διδωμι

    ποσος, -η, -ον
    ὁ μισθος
    ἡ χαρις
    ἡ δραχμη
    το δηναριον
        Is this a gift or would you like a denarius?
    ὁ πωλης
        συ ὁ πωλης?
        βλεπει ὁ πωλης. θελω με ἠ Ἰασων ὁ υἱος μου?
    το πωλητηριον
        τίνος ἡ πωλητηριον?
    το ἐλαιοπωλιον
        ἀγοραζει τουτους του ἐλαιοπωλιου?
    οἰνοπωλιον
    ἀρτοπωλιον
    το δωρον
        τίνος το δωρον?
    το -φορος
"""
