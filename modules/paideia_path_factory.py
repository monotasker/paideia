#! /etc/bin/python
# -*- coding:utf-8 -*-

u"""
Paideia Path Factory.

Copyright 2013—2014, Ian W. Scott

Provides classes for the procedural creation of paths/steps for the Paideia
web-app.

PathFactory:class
: This is the base class that handles generic path creation.

TranslateWordPathFactory:class (extends PathFactory)
: A subclass that includes extra helper logic for simple translation paths.

"""
# from pprint import pprint
import traceback
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB, UL, LI
from gluon import CAT, H2
import re
from random import randrange, shuffle
from itertools import product, chain
from paideia_utils import capitalize_first, test_regex, uprint
from paideia_utils import islist  # sanitize_greek,
from plugin_utils import flatten, makeutf8
# import datetime
# from plugin_ajaxselect import AjaxSelect


class PathFactory(object):
    """
    An abstract parent class to create paths (with steps) procedurally.

    """

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
                       'mid-pass': 'middle or passive'}

    const_abbrevs = {'adjective': 'adj',
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
                     'first': '1decl',
                     '1decl': '1decl',
                     'second': '2decl',
                     '2decl': '2decl',
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
                          'nominative1': (['noun', 'nom', '1decl'],
                                          ['adj', 'nom', '1decl'],
                                          ['pron', 'nom', '1decl']),
                          'nominative2': (['noun', 'nom', '2decl'],
                                          ['adj', 'nom', '2decl'],
                                          ['pron', 'nom', '2decl']),
                          'nominative3': (['noun', 'nom', '3decl'],
                                          ['adj', 'nom', '3decl'],
                                          ['pron', 'nom', '3decl']),
                          'dative1': (['noun', 'dat', '1decl'],
                                      ['adj', 'dat', '1decl'],
                                      ['pron', 'dat', '1decl']),
                          'dative2': (['noun', 'dat', '2decl'],
                                      ['adj', 'dat', '2decl'],
                                      ['pron', 'dat', '2decl']),
                          'dative3': (['noun', 'dat', '3decl'],
                                      ['adj', 'dat', '3decl'],
                                      ['pron', 'dat', '3decl']),
                          'genitive1': (['noun', 'gen', '1decl'],
                                        ['adj', 'gen', '1decl'],
                                        ['pron', 'gen', '1decl']),
                          'genitive2': (['noun', 'gen', '2decl'],
                                        ['adj', 'gen', '2decl'],
                                        ['pron', 'gen', '2decl']),
                          'genitive3': (['noun', 'gen', '3decl'],
                                        ['adj', 'gen', '3decl'],
                                        ['pron', 'gen', '3decl']),
                          'accusative1': (['noun', 'acc', '1decl'],
                                          ['adj', 'acc', '1decl'],
                                          ['pron', 'acc', '1decl']),
                          'accusative2': (['noun', 'acc', '2decl'],
                                          ['adj', 'acc', '2decl'],
                                          ['pron', 'acc', '2decl']),
                          'accusative3': (['noun', 'acc', '3decl'],
                                          ['adj', 'acc', '3decl'],
                                          ['pron', 'acc', '3decl']),
                          'vocative1': (['noun', 'voc', '1decl'],
                                        ['adj', 'voc', '1decl'],
                                        ['pron', 'voc', '1decl']),
                          'vocative2': (['noun', 'voc', '2decl'],
                                        ['adj', 'voc', '2decl'],
                                        ['pron', 'voc', '2decl']),
                          'vocative3': (['noun', 'voc', '3decl'],
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
                              'person', 'number', 'declension'],
                     'adverb': [],
                     'particle': [],
                     'conjunction': [],
                     'idiom': []}

    def __init__(self):
        """Initialize a paideia.PathFactory object."""
        self.promptstrings = []
        self.mock = True  # switch to activate testing mode with db clean-up

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

        for n in ['one', 'two', 'three', 'four', 'five']:
            fbs = [Field('{}_prompt_template'.format(n), 'list:string'),
                   Field('{}_response_template'.format(n), 'list:string'),
                   Field('{}_readable_template'.format(n), 'list:string'),
                   Field('{}_tags'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=1,
                         # multi='basic',
                         # lister='simple',
                         # orderby='tag'
                         # ).widget()
                         ),
                   Field('{}_tags_secondary'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id',
                                           '%(tag)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=2,
                         # multi='basic',
                         # lister='simple',
                         # orderby='tag'
                         # ).widget()
                         ),
                   Field('{}_tags_ahead'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=3,
                         # multi='basic',
                         # lister='simple',
                         # orderby='tag'
                         # ).widget()
                         ),
                   Field('{}_npcs'.format(n), 'list:reference npcs',
                         requires=IS_IN_DB(db, 'npcs.id', '%(name)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=1,
                         # multi='basic',
                         # lister='simple',
                         # orderby='name'
                         # ).widget()
                         ),
                   Field('{}_locations'.format(n), 'list:reference locations',
                         requires=IS_IN_DB(db, 'locations.id', '%(map_location)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=1,
                         # multi='basic',
                         # lister='simple',
                         # orderby='map_location'
                         # ).widget()
                         ),
                   Field('{}_instructions'.format(n), 'list:reference step_instructions',
                         requires=IS_IN_DB(db, 'step_instructions.id', '%(instruction_label)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=1,
                         # multi='basic',
                         # lister='simple',
                         # orderby='instruction_label'
                         # ).widget()
                         ),
                   Field('{}_hints'.format(n), 'list:reference step_hints',
                         requires=IS_IN_DB(db, 'step_hints.id', '%(hint_label)s',
                                           multiple=True),
                         # widget=lambda field, value: AjaxSelect(field, value,
                         # indx=1,
                         # multi='basic',
                         # lister='simple',
                         # orderby='hint_label'
                         # ).widget()
                         ),
                   Field('{}_step_type'.format(n), 'list:reference step_types',
                         requires=IS_IN_DB(db, 'step_types.id', '%(step_type)s',
                                           multiple=True)),
                   Field('{}_image_template'.format(n), 'string')]
            flds.extend(fbs)
        form = SQLFORM.factory(*flds)

        if form.process().accepted:
            vv = request.vars
            stepsdata = []
            for n in ['one', 'two', 'three', 'four', 'five']:
                nkeys = [k for k in vv.keys() if re.match('{}.*'.format(n), k)]
                filledfields = [k for k in nkeys if vv[k] not in ['', None]]
                if filledfields:
                    ndict = {k: vv[k] for k in nkeys}
                    stepsdata.append(ndict)
            if isinstance(vv['words'], list):
                wordlists = [w.split('|') for w in vv['words']]
            else:
                wordlists = [vv['words'].split('|')]
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
        new_forms (list)        : each member is a string, a word form newly
                                added to db.word_forms during step creation.
        images_missing (list)   : A list of ids for newly created image records.
                                These will need to be populated with the actual
                                images manually.

        """
        if testing is None:
            self.mock = False
        else:
            self.mock = True

        combos = self.make_combos(wordlists, aligned, avoid)
        paths = {}
        for idx, c in enumerate(combos):  # one path for each combo
            label = label_template.format('-'.join(c))
            mykeys = ['words{}'.format(n + 1) for n in range(len(c))]
            combodict = dict(zip(mykeys, c))  # keys are template placeholders

            pdata = {'steps': {}, 'new_forms': [], 'images_missing': []}
            for i, s in enumerate(stepsdata):  # each step in path
                # sanitize form response =============================="
                numstrings = ['one_', 'two_', 'three_', 'four_', 'five_']
                sdata = {k.replace(numstrings[i], ''): v for k, v in s.iteritems()}
                # create steps ========================================"
                stepdata, newforms, imgs = self.make_step(combodict, sdata)
                # collect result ======================================"
                pdata['steps'][stepdata[0]] = stepdata[1]
                if newforms:
                    pdata['new_forms'].append(newforms)
                if imgs:
                    pdata['images_missing'].append(imgs)
            pgood = [isinstance(k, (int, long)) for k in pdata['steps'].keys()]
            pid = self.path_to_db(pdata['steps'].keys(), label) \
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
        if len(wordlists) > 1 and aligned is True:
            combos = zip(*wordlists)
        elif len(wordlists) > 1:
            combos = list(product(*wordlists))
        else:
            combos = [(l,) for l in wordlists[0] if l]
            combos = [tup for tup in combos if tup]
        if avoid:
            combos = [x for x in combos
                      if not any([set(y).issubset(set(x)) for y in avoid])]
        return combos

    def make_step(self, combodict, sdata):
        """
        Create one step with given data.

        Returns a 2-member tuple
        [0] stepresult      : A 2-member tuple consisting of a string[0]
                              indicating the result of the step-creation
                              attempt and a second member [1] which gives
                              the content of that attempt. This content can be
                              - a step id (if success)
                              - a dict of step field values (if testing)
                              - a list of duplicate steps (duplicates)
                              - an error traceback (if failure)
        [1] newfs           : A list of inflected word forms newly added to
                              db.word_forms in the course of step creation.
        """
        mytype = sdata['step_type']

        ptemp = islist(sdata['prompt_template'])
        xtemp = islist(sdata['response_template'])
        rtemp = islist(sdata['readable_template'])

        tags1 = sdata['tags']
        itemp = sdata['image_template']
        tags2 = sdata['tags_secondary']
        tags3 = sdata['tags_ahead'] if 'tags_ahead' in sdata.keys() else None
        npcs = sdata['npcs']
        locs = sdata['locations']
        points = sdata['points'] if 'points' in sdata.keys() and sdata['points'] \
            else 1.0, 0.0, 0.0
        instrs = sdata['instructions']
        # FIXME: choking on the line below
        hints = sdata['hints']
        img = self.make_image(combodict, itemp) if itemp else None
        imgid = img[0] if img else None
        # ititle = img[1] if img else None
        images_missing = img[2] if img else None

        pros, rxs, rdbls, newfs = self.format_strings(combodict, ptemp, xtemp, rtemp)
        tags = self.get_step_tags(tags1, tags2, tags3, pros, rdbls)
        kwargs = {'prompt': pros[randrange(len(pros))],  # sanitize_greek(pros[randrange(len(pros))]),
                  'widget_type': mytype,
                  # 'widget_audio': None,
                  'widget_image': imgid,
                  'response1': islist(rxs)[0],
                  'readable_response': '|'.join([r for r in islist(rdbls)]),  # sanitize_greek(rdbls)]),
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
            matchdicts = [test_regex(x, rdbls) for x in rxs]
            xfail = {}
            for idx, regex in enumerate(rxs):
                mtch = all(matchdicts[idx].values())
                if not mtch:
                    problems = [k for k, v in matchdicts[idx].iteritems() if not v]
                    xfail[regex] = problems
            dups = self.check_for_duplicates(kwargs, rdbls, pros)
            if mtch and not self.mock and not dups[0]:
                stepresult = self.step_to_db(kwargs), kwargs
            elif mtch and not dups[0] and self.mock:
                stepresult = 'testing', kwargs
            elif mtch and dups[0]:
                stepresult = 'duplicate step', dups
            else:
                stepresult = 'regex failure', xfail
                # print 'regex failure-------------------------'
                # print xfail.keys()[0]
                # print xfail.values()[0][0]
        except Exception:
            # tracebk = traceback.format_exc(12)
            stepresult = ('failure')

        return stepresult, newfs, images_missing

    def make_image(self, combodict, itemp):
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
            image_missing = True
        else:
            myid = img_row.id

        return myid, mytitle, image_missing

    def format_strings(self, combodict, ptemps, xtemps, rtemps):
        u"""
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
        prompts = [self.do_substitution(p, combodict) for p in ptemps]
        p_new = chain.from_iterable([p[1] for p in prompts])
        prompts = [capitalize_first(p[0]) for p in prompts]

        rxs = [self.do_substitution(x, combodict) for x in xtemps]
        x_new = chain.from_iterable([x[1] for x in rxs])
        rxs = [x[0] for x in rxs]

        rdbls = [self.do_substitution(r, combodict) for r in rtemps]
        r_new = chain.from_iterable([r[1] for r in rdbls])
        rdbls = [capitalize_first(r[0]) for r in rdbls]

        newforms = list(chain(p_new, x_new, r_new))

        return prompts, rxs, rdbls, newforms

    def do_substitution(self, temp, combodict):
        """
        Make the necessary replacements for the suplied template string.

        Returns a list of strings, one for each valid combination of words
        supplied in the combodict parameter.
        """
        ready_strings = []
        subpairs = {}
        newforms = []

        fields = re.findall(r'(?<={).*?(?=})', temp)
        if not fields:
            return temp, None
        inflected_fields = [f for f in fields if len(f.split('-')) > 1]
        for f in fields:
            if f in inflected_fields:
                myform, newform = self.get_wordform(f, combodict)
                if newform:  # note any additions to db.word_forms
                    newforms.append(newform)
            else:
                myform = combodict[f]
            subpairs[f] = myform
        ready_strings = temp.format(**subpairs)
        return ready_strings, newforms

    def get_wordform(self, field, combodict):
        """
        Get the properly inflected word form for the supplied field.

        The expected field format is {lemma-modform-constraint}. For example,
        {αὐτος-words1-case:nom}. This will inflect the lemma αὐτος to agree with
        the current words1 except that the case will be constrained as
        nominative. If no constraint is given the lemma will be inflected to
        agree with the modform in all relevant aspects.

        """
        db = current.db
        splits = field.split('-')
        lemma = splits[0]
        mod = splits[1]
        try:
            aspect = splits[2]
        except IndexError:
            aspect = None
        # if lemma is pointer to a word list
        lemma = combodict[lemma] if lemma in combodict.keys() else lemma
        # allow for passing inflected form instead of lemma
        if not db.lemmas(db.lemmas.lemma == lemma):
            myrow = db.word_forms(db.word_forms.word_form == lemma)
            lemma = myrow.source_lemma.lemma
        # inflect lemma to agree with its governing word
        modform = combodict[mod] if mod != 'none' else None

        myform, newform = self.make_form_agree(modform, lemma, aspect)

        return myform, newform

    def _guess_part_of_speech(self, word_form):
        """docstring for _guess_part_of_speech"""

        word_form = makeutf8(word_form)
        if (word_form[-1] == u'ω') or (word_form[-2:] == u'μι'):
            ps = 'verb'
        elif (word_form[-2:] in [u'ος', u'υς', u'ης', u'ον']) or \
             (word_form[-1] in [u'η', u'α']):
            ps = 'noun'
        elif word_form[-2:] == u'ως':
            ps = 'adverb'
        else:
            ps = None

        return ps

    def _guess_parsing(self, word_form, lemma):
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
        endings = {u'ος': {'sfx': [u'ος', u'ου', u'ῳ', u'ον', u'ε',
                                   u'οι', u'ων', u'οις', u'ους', u'--'],
                           'declension': '2',
                           'gender': 'masculine'},
                   u'ον': {'sfx': [u'ον', u'ου', u'ῳ', u'ον', u'ε',
                                   u'α', u'ων', u'οις', u'α', u'--'],
                           'declension': '2',
                           'gender': 'neuter'},
                   u'(η|α)': {'sfx': [u'(η|α)', u'[ηα]ς', u'(ῃ|ᾳ)', u'[ηα]ν', u'ε',
                                  u'αι', u'ων', u'αις', u'ας', u'--'],
                          'declension': '1',
                          'gender': 'feminine'},
                   u'ρ': {'sfx': [u'ρ', u'ρος', u'ρι', u'ρα', u'--',
                                  u'ρες', u'ρων', u'ρι.ι', u'ρας', u'--'],
                          'declension': '3',
                          'gender': None},
                   u'ις': {'sfx': [u'[^ε]ις', u'(εως|ος)', u'ι', u'(ιν|α)',
                                   u'--', u'ε[ι]?ς', u'ων', u'[ιε].ι',
                                   u'(εις|ας)', u'ε[ι]?ς'],
                          'declension': '3',
                          'gender': None},
                   u'υς': {'sfx': [u'υς', u'υως', u'υι', u'υν', u'υ',
                                   u'υες', u'υων', u'--', u'υας', u'υες'],
                          'declension': '3',
                          'gender': None},
                   }
        for k, v in endings.iteritems():
            if re.match(u'.*{}$'.format(k), lemma):
                ends = [i for i in v['sfx']
                        if re.match(u'.*{}$'.format(i), word_form)]
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

    def _add_new_wordform(self, word_form, lemma, mod_form, constraint):
        """
        Attempt to insert a new word form into the db based on supplied info.

        If the insertion is successful, return the word form and the id of the
        newly inserted row from db.word_forms. Otherwise return False.

        """
        db = current.db

        # get initial dict from constraint if there is one
        cd = self._parse_constraint(constraint)
        if not cd:  # in case there was no constraint to parse
            cd = {}

        # get lemma and part of speech
        lemmarow = db.lemmas(db.lemmas.lemma == lemma)
        cd['source_lemma'] = lemmarow.id
        ps = lemmarow.part_of_speech
        if not ps:
            ps = self._guess_part_of_speech(word_form)
            #lemmarow.update(part_of_speech=ps)

        # identify expected info for this part of speech
        if ps == 'verb' and cd['mood'] == 'participle':
            self.self.wordform_reqs['verb'].pop(-2)
            num = self.self.wordform_reqs['verb'].pop(-1)
            self.wordform_reqs['verb'].extend(['grammatical_case', 'gender'])
            self.wordform_reqs['verb'].append(num)
        if ps == 'verb' and cd['mood'] == 'infinitive':
            self.wordform_reqs['verb'] = self.wordform_reqs['verb'][:-2]

        # try to get missing info from any modform (supposed to agree)
        if mod_form:
            modrow = db(db.word_forms.word_form == mod_form).select().first()
            if modrow:
                need = [i for i in self.wordform_reqs[ps]
                        if i not in cd.keys()]
                if need:
                    for n in need:
                        cd[n] = modrow[n]

        # try to get missing info from form itself and lemma
        need = [i for i in self.wordform_reqs[ps]
                if i not in cd.keys()]
        if need:
            guesses = self._guess_parsing(word_form, lemma)
            for n in need:
                if n in guesses.keys() and guesses[n]:
                    cd[n] = guesses[n]

        # remove any extraneous info
        for k in cd.keys():
            if k not in self.wordform_reqs[ps]:
                del cd[k]

        # build and add construction label
        cstbits = [cd[k] for k in self.wordform_reqs[ps][1:]]  # don't include lemma in construction label
        shortbits = [self.const_abbrevs[i] for i in cstbits]
        cst_label = '{}_{}'.format(ps, '_'.join(shortbits))
        cst_row = db.constructions(db.constructions.construction_label ==
                                   cst_label)
        if cst_row:
            cst_id = cst_row.id
            print 'found const', cst_id
        else:  # create new construction entry if necessary
            rdbl = '{}, {}'.format(ps, ' '.join(cstbits))
            rdbl = rdbl.replace(' first', ', first person ')
            rdbl = rdbl.replace(' second', ', second person ')
            rdbl = rdbl.replace(' third', ', third person ')
            rdbl = rdbl.replace(' 1decl', ', 1st declension ')
            rdbl = rdbl.replace(' 2decl', ', 2nd declension ')
            rdbl = rdbl.replace(' 3decl', ', 3rd declension ')
            mytags = [k for k, v in self.tagging_conditions.iteritems()
                      for lst in v if all(l in shortbits for l in lst)]
            mytags = [t.id for t in db(db.tags.tag.belongs(mytags)).select()]
            print 'inserting new construction:', cst_label
            cst_id = db.constructions.insert(**{'construction_label': cst_label,
                                                'readable_label': rdbl,
                                                'tags': mytags})
        if 'declension' in cd.keys():
            del cd['declension']  # only used for building construction
        cd['construction'] = cst_id

        # collect and add tags
        cd['tags'] = [] if 'tags' not in cd else cd['tags']
        cd['tags'].extend(db.constructions(cst_id).tags)
        mylem = db.lemmas(db.lemmas.lemma == lemma)
        cd['tags'].extend(mylem.extra_tags)
        cd['tags'].append(mylem.first_tag)
        cd['tags'] = list(set(cd['tags']))

        cd['word_form'] = word_form
        print cd['word_form']

        # write new form to db
        rowid = db.word_forms.insert(**cd)
        print 'inserted row', rowid

        return word_form, rowid, cst_id

    def _add_new_lemma(self, lemma, constraint):
        """
        Attempt to insert a new lemma into the db based on supplied info.

        If the insertion is successful, return True. If the info is not
        sufficient, return False.
        """
        db = current.db
        cd = self._parse_constraint(constraint)
        lemma_reqs = ['lemma', 'glosses', 'part_of_speech', 'first_tag',
                      'extra_tags']
        lemdata = {k: i for k, i in cd.iteritems() if k in lemma_reqs}
        lemma = makeutf8(lemma)

        # get lemma field
        lemdata['lemma'] = lemma
        # get part_of_speech field
        if 'part_of_speech' not in lemdata.keys():
            lemdata['part_of_speech'] = self._guess_part_of_speech(lemma)
        # get tags
        tags = []
        if lemdata['part_of_speech'] == 'verb':
            tags.append('verb basics')
            if lemma[-2:] == 'μι':
                tags.append('μι verbs')
        elif lemdata['part_of_speech'] == 'noun':
            tags.append('noun basics')
            if lemma[-2:] in ['ος', 'ης', 'ον']:
                tags.append('nominative2')
            elif lemma[-2:] in ['υς', 'ις', 'ων', 'ηρ']:
                tags.append('nominative3')
            elif lemma[-1] in ['η', 'α']:
                tags.append('nominative1')
        elif lemdata['part_of_speech'] in ['adjective', 'pronoun', 'adverb',
                                           'particle', 'conjunction']:
            tags.append('{}s'.lemdata['part_of_speech'])
        # populate 'tags_extra' field with ids
        tagids = [t.id for t in db(db.tags.tag.belongs(tags)).select()]
        lemdata['extra_tags'] = tagids

        # get 'glosses' field
        if 'glosses' in lemdata.keys():
            lemdata['glosses'] = lemdata['glosses'].split('|')

        lemid = db.lemmas.insert(**lemdata)

        return lemma, lemid

    def _parse_constraint(self, constraint):
        """
        Return a dictionary of grammatical features based on a constraint string.

        """
        try:
            cparsebits = constraint.split('_')
            cd = {b.split('@')[0]: b.split('@')[1] for b in cparsebits}
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
                       'gl': 'glosses'}
            for k, v in cd.iteritems():  # handle key short forms
                if k in key_eqs.keys():
                    cd[key_eqs[k]] = v
                    del cd[k]
            eq = {'masculine': ['masc', 'm'],
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
            for k, v in cd.iteritems():  # handle value short forms
                if v in list(chain.from_iterable(eq.values())):
                    expandedv = [kk for kk, vv in eq.iteritems() if v in vv][0]
                    cd[k] = expandedv
            return cd
        except AttributeError:  # constraint is NoneType
            return False

    def make_form_agree(self, mod_form, mylemma, constraint=None):
        """
        Return a form of the lemma "mylemma" agreeing with the supplied mod_form.

        This method is used only for nominals (nouns, pronouns, adjectives),
        excluding substantive participals. Verbs (including participles) are
        handled elsewhere.

        """
        db = current.db
        newform = None
        lem = db(db.lemmas.lemma == mylemma).select().first()
        if not lem:
            lem, rowid, formid = self._add_new_lemma(mylemma, mod_form,
                                                     constraint)
            lem = db.lemmas(rowid)
            if not lem:
                return (None, None, 'Could not create new lemma')
        lemform = db(db.word_forms.word_form == mylemma).select().first()
        if not lemform:
            myform, rowid = self._add_new_wordform(mylemma, mylemma,
                                                   mod_form, constraint)
            lemform = db.word_forms(rowid)
            newform = myform
            if not myform:
                return (None, None, 'Could not create new lemma')
        ref = db(db.word_forms.word_form == mod_form).select().first()
        if not ref:
            myform, rowid = self._add_new_wordform(mod_form, None, None, None)
            newform = myform
            if not lemform:
                return (None, None, 'Could not create new lemma')

        # use provided constraints where present in field
        cd = {}
        if constraint and constraint != 'none':
            cd = self._parse_constraint(constraint)
        case = ref.grammatical_case if 'case' not in cd.keys() else cd['case']
        number = ref.number if 'number' not in cd.keys() else cd['number']
        if () or (lem.part_of_speech == 'noun'):
            gender = lemform.gender
        else:
            gender = ref.gender
        # allow for ambiguously gendered forms in search for word form below
        if 'gender' in cd.keys():
            genders = [gender, 'undetermined']
            if gender in ['masculine', 'feminine']:
                genders.append('masculine or feminine')
            if gender in ['masculine', 'neuter']:
                genders.append('masculine or neuter')
        # get the inflected form from the db
        myrow = db((db.word_forms.source_lemma == lem.id) &
                   (db.word_forms.grammatical_case == case) &
                   (db.word_forms.gender.belongs(genders)) &
                   (db.word_forms.number == number)
                   ).select().first()
        try:
            myform = myrow.word_form
        except Exception:
            # print traceback.format_exc(5)
            myform = None  # FIXME: try to create and save new declined form

        return myform, newform

    def check_for_duplicates(self, step, readables, prompt):
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

    def get_step_tags(self, tags1, tags2, tags3, prompts, rdbls):
        """
        Return a 3-member tuple of lists holding the tags for the current step.
        """
        db = current.db
        tags1 = islist(tags1) if tags1 else []
        tags2 = islist(tags2) if tags2 else []
        tags3 = islist(tags3) if tags3 else []

        words = [p.split(' ') for p in prompts]
        words.extend([r.split(' ') for r in rdbls])
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

    def step_to_db(self, kwargs):
        """ """
        db = current.db
        try:
            sid = db.steps.insert(**kwargs)
            return sid
        except Exception:
            traceback.print_exc(5)
            return False

    def path_to_db(self, steps, label):
        """ """
        db = current.db
        try:
            pid = db.paths.insert(label=label, steps=steps)
            return pid
        except Exception:
            traceback.print_exc(5)
            return False

    def make_output(self, paths):
        """
        Return formatted output for the make_path view after form submission.

        """
        db = current.db
        opts = {'goodpaths': {p: v for p, v in paths.iteritems()
                              if isinstance(p, int)},
                'badpaths': {p: v for p, v in paths.iteritems()
                             if not isinstance(p, int)}}
        outs = {'goodpaths': UL(),
                'badpaths': UL()}
        newforms = []
        images = []

        for opt in ['goodpaths', 'badpaths']:
            badcount = 0

            for pk, pv in opts[opt].iteritems():
                if opt == 'badpaths':
                    badcount += 1

                successes = [s for s in pv['steps'].keys()
                             if s not in ['failure', 'duplicate step']]
                failures = [s for s in pv['steps'].keys() if s == 'failure']
                duplicates = [s for s in pv['steps'].keys() if s == 'duplicate step']

                pout = LI('Path: {}'.format(pk))

                psub = UL()
                psub.append(LI('steps succeeded: {}'.format(len(successes))))
                psub.append(LI('steps failed: {}'.format(len(failures))))
                psub.append(LI('steps were duplicates: {}'.format(len(duplicates))))
                content = pv['steps']
                mycontent = UL()
                for key, c in content.iteritems():
                    # print 'item', key
                    # pprint(c)
                    mycontent.append(LI(key))
                    mystep = UL()
                    mystep.append(LI('widget_type:', db.step_types(c['widget_type']).step_type))
                    mystep.append(LI('prompt:', uprint(c['prompt'])))
                    mystep.append(LI('readable_response:', uprint(c['readable_response'])))
                    mystep.append(LI('response1:', uprint(c['response1'])))
                    mystep.append(LI('outcome1:', c['outcome1']))
                    mystep.append(LI('response2:', uprint(c['response2'])
                                     if c['response2'] else None))
                    mystep.append(LI('outcome2:', c['outcome2']))
                    mystep.append(LI('response3:', uprint(c['response3'])
                                     if c['response3'] else None))
                    mystep.append(LI('outcome3:', c['outcome3']))
                    tags = [t['tag'] for t in
                            db(db.tags.id.belongs(c['tags'])).select()]
                    mystep.append(LI('tags:', tags))
                    tags_secondary = [t['tag'] for t in
                                      db(db.tags.id.belongs(c['tags_secondary'])
                                         ).select()]
                    mystep.append(LI('tags_secondary:', tags_secondary))
                    tags_ahead = [t['tag'] for t in
                                  db(db.tags.id.belongs(islist(c['tags_ahead']))
                                     ).select()]
                    mystep.append(LI('tags_ahead:', tags_ahead))
                    mycontent.append(LI(mystep))
                    npcs = [uprint(t['name']) for t in
                            db(db.npcs.id.belongs(islist(c['npcs']))).select()]
                    # print c['npcs']
                    mystep.append(LI('npcs:', npcs))
                    locations = [t['map_location'] for t in
                                 db(db.locations.id.belongs(c['locations'])
                                    ).select()
                                 ]
                    mystep.append(LI('locations:', uprint(locations)))
                    lemmas = [t['lemma'] for t in
                              db(db.lemmas.id.belongs(c['lemmas'])).select()] \
                        if 'lemmas' in c.keys() else None
                    mystep.append(LI('lemmas:', uprint(lemmas)
                                     if lemmas else None))
                    mystep.append(LI('status:',
                                     db.step_status(c['status']).status_label
                                     if 'status' in c.keys() else None))
                    instructions = [t['instruction_label'] for t in
                                    db(db.step_instructions.id.belongs(c['instructions'])
                                       ).select()]
                    mystep.append(LI('instructions:', instructions))
                    hints = [t['hint_label'] for t in
                             db(db.step_hints.id.belongs(c['hints'])
                                ).select()]
                    mystep.append(LI('hints:', hints))
                psub.append(mycontent)
                pout.append(psub)

                outs[opt].append(pout)

        output = CAT(H2('successes'), outs['goodpaths'],
                     H2('failures'), outs['badpaths'])

        message1 = 'Created {} new paths.\n'.format(len(outs['goodpaths'])) \
                   if len(outs['goodpaths']) else 'no'
        message2 = '{} paths failed\n'.format(len(outs['badpaths'])) \
                   if len(outs['badpaths']) else 'no'
        nf = 'new word forms entered in db:\n{}\n'.format(BEAUTIFY(newforms))
        imgs = 'images needed for db:\n{}\n'.format(BEAUTIFY(images))
        message = message1 + message2 + nf + imgs

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
        self.promptstrings = ['Τί σημαινει ὁ λογος οὑτος? {}',
                              'Ὁ λογος οὑτος τί σημαινει? {}',
                              'Σημαινει ὁ λογος οὑτος τί? {}',
                              'Οὑτος ὁ λογος τί σημαινει? {}',
                              'Σημαινει τί ὁ λογος οὑτος? {}']

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
        form = SQLFORM.factory(Field('lemmas',
                                     type='list:reference lemmas',
                                     requires=IS_IN_DB(db, 'lemmas.id', '%(lemma)s', multiple=True),
                                     ),
                               Field('irregular_forms', type='list:string'),
                               Field('testing', type='boolean'))
        # widget=lambda f, v: AjaxSelect(f, v,
        # indx=1,
        # refresher=True,
        # multi='basic',
        # lister='simple',
        # orderby='lemmas'
        # ).widget()
        if form.process(dbio=False, keepvalues=True).accepted:
            self.lemmaset = request.vars.lemmas
            irregs = request.vars.irregular_forms
            self.irregular_forms = {f.split('|')[0]: f.split('|')[1]
                                    for f in irregs}
            paths, result = self.make_path()
            message, output = self.make_output(paths, result)
        elif form.errors:
            message = BEAUTIFY(form.errors)

        return form, message, output

    def make_path(self, widget_type, lemmas, irregular, testing):
        '''
        '''
        db = current.db
        result = {}
        for lemma in lemmas:
            lemma['constructions'] = self.get_constructions(lemma)
            for idx, cst in enumerate(lemma['constructions']):  # each path
                compname = '{} {}'.format(lemma['lemma'], cst[0])
                crow = db(db.constructions.construction_label == cst
                          ).select().first()
                reg_str = crow['trans_regex_eng']
                glosses = self.make_glosses(lemma['lemma'], cst)
                rdbl = self.make_readable(glosses[:], crow['trans_templates'])
                tagset = self.get_step_tags(lemma, crow)
                word_form = self.get_word_form(lemma['lemma'], crow),
                try:
                    step = {'prompt': self.get_prompt(word_form, crow),
                            'response1': self.make_regex(glosses[:], reg_str),
                            'outcome1': 1.0,
                            'readable_response': rdbl,
                            'response2': self.make_glosslist(glosses),
                            'outcome2': 0.5,
                            'tags': tagset[0],
                            'tags_secondary': tagset[1],
                            'tags_ahead': tagset[2],
                            'npcs': [8],
                            'locations': [7]
                            }
                    # response3  # todo: build from groups in regex
                    # pth['outcome2'] = 0.4
                    mtch = test_regex()
                    dups = self.check_for_duplicates(step)
                    if mtch and not testing and not dups:
                        pid, sid = self.write_to_db(step)
                        result[compname] = (pid, sid)
                    elif mtch and testing:
                        result[compname] = ('testing', step)
                    else:
                        result[compname] = 'failure', 'readable didn\'t match'
                except Exception:
                    # tbk = traceback.format_exc(5)
                    result[compname] = ('failure')
        return result

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

