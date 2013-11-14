#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
A collection of miscellaneous utility functions to be used in multiple modules.

Part of the Paideia platform built with web2py.

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
import traceback
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB, UL, LI, A, URL, P
#from plugin_ajaxselect import AjaxSelect
import re
from random import randrange, shuffle
from itertools import product


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
    print 'done sending '


MYWORDS = {u'πωλεω': {'glosses': ['sell'],
                      'constructions': [('pres_act_ind_2s', 'πωλεις'),
                                        ('pres_act_ind_3s', 'πωλει'),
                                        ('pres_act_ind_1p', 'πωλουμεν'),
                                        ('pres_act_ind_2p', 'πωλειτε'),
                                        ('pres_act_ind_3p', 'πωλουσι'),
                                        ('pres_act_imper_2s', 'πωλει'),
                                        ('pres_act_imper_2s', 'πωλειτε')
                                        ],
                      'xtags': [128, 121]},
           u'ὁραω': {'glosses': ['see', 'perceiv|e'],
                     'constructions': [('pres_act_inf', 'ὁρᾳν'),
                                       ('pres_act_ind_2s', 'ὁρᾳς'),
                                       ('pres_act_ind_3s', 'ὁρᾳ'),
                                       ('pres_act_ind_1p', 'ὁρωμεν'),
                                       ('pres_act_ind_2p', 'ὁρατε'),
                                       ('pres_act_ind_3p', 'ὁρωσι'),
                                       ('pres_act_imper_2s', 'ὁρα'),
                                       ('pres_act_imper_2p', 'ὁρατε'),
                                       ],
                     'xtags': [121]},
           u'βαινω': {'glosses': ['go', 'move'],
                      'constructions': [('pres_act_inf', None),
                                      ('pres_act_ind_2s', None),
                                      ('pres_act_ind_3s', None),
                                      ('pres_act_ind_1p', None),
                                      ('pres_act_ind_2p', None),
                                      ('pres_act_imper_2s', None),
                                      ('pres_act_imper_2p', None),
                                      ],
                      'xtags': [121]},
           u'σημαινω': {'glosses': ['mean', 'signify|ie'],
                        'constructions': [('pres_act_ind_1s', 'σημαινω'),
                                          ('pres_act_ind_2s', 'σημαινεις'),
                                          ('pres_act_ind_3s', 'σημαινει'),
                                          ('pres_act_ind_1p', 'σημαινομεν'),
                                          ('pres_act_ind_2p', 'σημαινετε'),
                                          ],
                        'xtags': [121]},
           u'ἀγοραζω': {'glosses': ['buy', 'shop|p'],
                        'constructions': [('pres_act_ind_1s', None),
                                          ('pres_act_ind_2s', 'ἀγοραζεις'),
                                          ('pres_act_ind_3s', 'ἀγοραζει'),
                                          ('pres_act_ind_1p', 'ἀγοραζομεν'),
                                          ('pres_act_ind_2p', 'ἀγοραζετε'),
                                          ('pres_act_imper_2s', None),
                                          ('pres_act_imper_2p', None),
                                          ],
                        'xtags': [121]},
           u'φερω': {'glosses': ['lift', 'carry', 'bear', 'tolerat|e',
                                 'endur|e'],
                     'constructions': [('pres_act_ind_2s',),
                                       ('pres_act_ind_3s',),
                                       ('pres_act_ind_1p',),
                                       ('pres_act_ind_2p',),
                                       ('pres_act_ind_3p',),
                                       ('pres_act_imper_2s', None),
                                       ('pres_act_imper_2p', None),
                                       ],
                     'xtags': [121]},
           u'θελω': {'glosses': ['want', 'wish', 'desir|e'],
                     'constructions': [('pres_act_inf', None),
                                       ('pres_act_ind_2s', None),
                                       ('pres_act_ind_3s', None),
                                       ('pres_act_ind_1p', None),
                                       ('pres_act_ind_2p', None),
                                       ('pres_act_ind_3p', None),
                                       ('pres_act_imper_2s', None),
                                       ('pres_act_imper_2p', None),
                                       ],
                     'xtags': [121]},
           u'λαμβανω': {'glosses': ['tak|e', 'get', 'receiv|e'],
                        'constructions': [('pres_act_inf', None),
                                        ('pres_act_ind_2s', None),
                                        ('pres_act_ind_3s', None),
                                        ('pres_act_ind_1p', None),
                                        ('pres_act_ind_2p', None),
                                        ('pres_act_ind_3p', None),
                                        ('pres_act_imper_2s', None),
                                        ('pres_act_imper_2p', None),
                                        ],
                        'xtags': [121]},
           u'ἀκουω': {'glosses': ['hear', 'listen', 'obey', 'perceiv|e'],
                      'constructions': [('pres_act_inf', None),
                                      ('pres_act_ind_2s', None),
                                      ('pres_act_ind_3s', None),
                                      ('pres_act_ind_1p', None),
                                      ('pres_act_ind_2p', None),
                                      ('pres_act_imper_2s', None),
                                      ('pres_act_imper_2p', None),
                                      ],
                      'xtags': [121]},
           u'ποιεω': {'glosses': ['do', 'mak|e'],
                      'constructions': [('pres_act_inf', None),
                                        ('pres_act_ind_1s', None),
                                        ('pres_act_ind_2s', 'ποιεις'),
                                        ('pres_act_ind_3s', 'ποιει'),
                                        ('pres_act_ind_1p', 'ποιουμεν'),
                                        ('pres_act_ind_2p', 'ποιειτε'),
                                        ('pres_act_ind_3p', 'ποιουσι'),
                                        ('pres_act_imper_2s', 'ποιει֚'),
                                        ('pres_act_imper_2p', 'ποιειτε'),
                                        ],
                      'xtags': [121]},
           u'διδωμι': {'glosses': ['give'],
                       'constructions': [('pres_act_ind_2s', 'διδως'),
                                         ('pres_act_ind_3s', 'διδωσι'),
                                         ('pres_act_ind_1p', 'διδομεν'),
                                         ('pres_act_ind_2p', 'διδοτε'),
                                         ('pres_act_ind_3p', 'διδοασι'),
                                         ('pres_act_imper_2s', 'διδου'),
                                         ('pres_act_imper_2p', 'διδοτε'),
                                         ],
                       'xtags': [121]}
           }

abbrevs = {'acc': 'accusative',
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

input = {'words1': ['καρπους|noun_acc_masc_plur_καρπος',
             'συκα|noun_acc_neut_plur_συκον',
             'ἰχθυας|noun_acc_masc_plur_ἰχθυς',
             'ἀρτους|noun_acc_masc_plur_ἀρτος'],
         'words2': ['δυο',
                 'τρεις',
                 'τεσσαρες',
                 'πεντα',
                 'ἑξα',
                 'ἑπτα',
                 'ὀκτω',
                 'ἐννεα',
                 'δεκα'],
         'words3': [],
         'prompt_template': ['{adj-ποσος} {words1} ἐχομεν?',
                             '{words1} {adj-ποσος} ἐχομεν?',
                             '{words1} ἐχομεν {adj-ποσος}?',
                             'Ἐχομεν {words1} {adj-ποσος}?'],
         'response_template': ['^(?P<a>Ἐχομεν\s)?(?P<b>{words2}\s)?(?(a)|(?P<c>ἐχομεν))?{words1}(?(a)|(?(c)|(?P<d>\sἐχομεν)))?(?(b)|\s{words2})(?(a)|(?(c)|(?(d)|(\sἐχομεν))))\.?'],
         'readable_template': ['Ἐχομεν {words2} {words1}.',
                             '{words2} ἐχομεν {words1}.',
                             '{words1} ἐχομεν {words2}.',
                             '{words1} {words2} ἐχομεν.',
                             '{words2} {words1} ἐχομεν.'],
         'image_template': 'food_{words2}_{words1}',
         'testing': True}

class PathFactory(object):

    u"""
    An abstract parent class to create paths (with steps) procedurally.

    """

    def __init__(self):
        """Initialize an object. """
        self.promptstrings = []

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
        form = SQLFORM.factory(Field('words1', 'list:string',
                                     default=input['words1']),
                               Field('words2', 'list:string',
                                     default=input['words2']),
                               Field('words3', 'list:string',
                                     default=input['words3']),
                               Field('prompt_template', 'list:string',
                                     default=input['prompt_template']),
                               Field('response_template', 'list:string',
                                     default=input['response_template']),
                               Field('readable_template', 'list:string',
                                     default=input['readable_template']),
                               Field('tags', 'list:reference ',
                                     requires=IS_IN_DB(db, 'tags.id',
                                                       '%(tag)s', multiple=True)),
                               Field('tags_secondary', 'list:reference tags',
                                     requires=IS_IN_DB(db, 'tags.id',
                                                       '%(tag)s', multiple=True)),
                               Field('tags_ahead', 'list:reference tags',
                                     requires=IS_IN_DB(db, 'tags.id',
                                                       '%(tag)s', multiple=True)),
                               Field('npcs', 'list:reference npcs',
                                     requires=IS_IN_DB(db, 'npcs.id',
                                                       '%(name)s', multiple=True)),
                               Field('locations', 'list:reference locations',
                                     requires=IS_IN_DB(db, 'locations.id',
                                                       '%(map_location)s', multiple=True)),
                               Field('step_type', 'list:reference step_types',
                                     requires=IS_IN_DB(db, 'step_types.id',
                                                       '%(step_type)s', multiple=True)),
                               Field('image_template',
                                     default=input['image_template']),
                               Field('avoid', 'list:string'),
                               Field('testing', type='boolean'))
        if form.process(dbio=False, keepvalues=True).accepted:
            vv = request.vars
            paths, result = self.make_path(words1=vv.words1,
                                           words2=vv.words2,
                                           words3=vv.words3,
                                           prompt_template=vv.prompt_template,
                                           response_template=vv.response_template,
                                           readable_template=vv.readable_template,
                                           tags=vv.tags,
                                           tags_secondary=vv.tags_secondary,
                                           tags_ahead=vv.tags_ahead,
                                           npcs=vv.npcs,
                                           locations=vv.locations,
                                           step_type=vv.step_type,
                                           image_template=vv.image_template,
                                           testing=vv.testing
                                           )
            message, output = self.make_output(paths, result)
        elif form.errors:
            message = BEAUTIFY(form.errors)

        return form, message, output

    def make_path(self, words1=None, words2=None, words3=None,
                  prompt_template=[], response_template=[],
                  readable_template=[],
                  tags=[],
                  tags_secondary=[],
                  tags_ahead=[],
                  npcs=[],
                  locations=[],
                  step_type=None,
                  image_template=None,
                  avoid=[],
                  testing=False):
        """
        Create a set of similar paths programmatically from provided variables.

        Required arguments
        ------------------

        :kwarg:widget_type (int)      -- the id of the widget-type appropriate
        to this step.

        :kwarg:prompt_template' (list) -- list of strings with {} marking fields
                                         for lemmas to be replaced.
        :kwarg:response_template' (list) -- string with {} marking fields for
                                         lemmas to be replaced.
        :kwarg:readable_template' (list) -- string with {} marking fields for
                                         lemmas to be replaced.
        :kwarg:words1 (list)          -- words (strings) to sub into the
                                         templates as {words1}.
        :kwarg:words2 (list)          -- words (strings) to sub into the
                                         templates as {words2}.
        :kwarg:words3 (list)          -- words (strings) to sub into the
                                         templates as {words3}.
        :kwarg:npcs (list)            -- npc id's (int) which are valid for
                                         the steps
        :kwarg:locs (list)            -- id's (int) for location in which the
                                         steps can be performed
        :kwargs:image_template (str)
        :kwargs:tags
        :kwargs:tags_secondary
        :kwargs:tags_ahead

        Optional arguments
        ------------------
        :kwarg:avoid (list of tuples) -- each tuple specifies an invalid
                                         combinations of lemmas which should
                                         be avoided in assembling step
                                         variations.

        """
        print "starting module======================================"
        db = current.db
        paths = []
        result = {}
        title_template = 'Counting fruit, {}'  # TODO: get from form
        images_missing = []

        wordlists = [l for l in [words1, words2, words3] if l]
        combos = product(*wordlists)
        print combos

        for c in combos:
            compname = title_template.format('-'.join(c))
            cdict = dict(zip(['words1', 'words2', 'words3'], c))
            img_title = image_template.format(**cdict) if image_template else 'none'
            img_row = db(db.images.title == img_title).select().first()
            if not img_row:
                db.images.insert(title=img_title)
                images_missing.append(img_title)
                img_row = db(db.images.title == img_title).select().first()
            img_id = img_row.id
            prompt, responses, readable, \
            xtags, new_forms = self.formatted(c,
                                              prompt_template,
                                              response_template,
                                              readable_template,
                                              testing
                                              )
            response1 = responses[0]
            response2 = responses[1] if len(responses) > 1 else None
            response3 = responses[2] if len(responses) > 2 else None
            outcome1 = 1.0
            outcome2 = 0.0
            outcome3 = 0.0
            tags = self.get_tags(tags, tags_secondary, tags_ahead, xtags)
            kwargs = {'prompt': prompt,
                      'widget_type': step_type,
                      'widget_audio': None,
                      'widget_image': img_id,
                      'response1': response1,
                      'readable_response': readable,
                      'outcome1': outcome1,
                      'response2': response2,
                      'outcome2': outcome2,
                      'response3': response3,
                      'outcome3': outcome3,
                      'tags': tags[0],
                      'tags_secondary': tags[1],
                      'tags_ahead': tags[2],
                      'npcs': npcs,  # [randrange(len(npcs))] if multiple
                      'locations': locations}  # [randrange(len(npcs))] if mult
            try:
                mtch = self.test_regex(kwargs)
                dups = self.check_for_duplicates(kwargs)
                roman = self.check_for_roman(kwargs)
                if mtch and not testing and not dups and not roman:
                    result[compname] = self.write_to_db(kwargs)
                elif mtch and not dups and not roman and testing:
                    result[compname] = ('testing', kwargs)
                elif mtch and dups:
                    result[compname] = ('duplicate', dups)
                elif mtch and roman:
                    result[compname] = ('roman characters', roman)
                else:
                    result[compname] = 'failure', 'readable didn\'t match regex'
            except Exception:
                tracebk = traceback.format_exc(5)
                result[compname] = ('failure', tracebk)
        result['new_forms'] = new_forms
        result['images_missing'] = images_missing
        return paths, result

    def formatted(self, words, prompts, resps, rdbls, testing):
        """
        Return a list of the template formatted with each of the words.
        """
        db = current.db
        parts = {'prompt': prompts[randrange(len(prompts))]}
        if type(resps) != list:
            resps = [resps]
        resps = {'resp{}'.format(i): r for i, r in enumerate(resps) if r}
        parts.update(resps)
        rdbl = {'rdbl{i}'.format(i=i): r for i, r in enumerate(rdbls)}
        parts.update(rdbl)
        print '--------------------------------------'
        print 'parts are:',
        for k, v in parts.iteritems():
            print k, ':', v
        newforms = []  # collect any new word forms created in db along the way
        mytags = []

        # perform substitutions for each "part" to be returned
        for k, p in parts.iteritems():
            print '--------------------------------------'
            print k
            print p

            # isolate fields for substitution, both automatic and manual
            fields = re.findall(r'(?<={).*?(?=})', p)
            auto_fields = [f for f in fields if f not in ['words1', 'words2',
                                                          'words3']]
            man_fields = [f for f in fields if f in ['words1', 'words2',
                                                     'words3']]
            # handle any automatic fields
            for f in auto_fields:
                mylemma = f.split('-')[1] if len(f.split('-')) > 1 else None
                mytags = db(db.lemmas.lemma == mylemma).select().first().extra_tags
                print 'mylemma:', mylemma
                if re.search(r'adj|noun|pronoun', f):
                    modifies = man_fields[0]  # FIXME: only works for single sub
                    print 'modifies:', modifies
                    mod_form = words[int(modifies[-1])-1]
                    print 'mod_form:', mod_form

                    myform, newform = self.make_form_agree(mod_form, mylemma,
                                                           testing)
                    print 'myform returned:', myform
                    print 'newform returned:', newform
                    if newform:
                        newforms.append(newform)
                    formtags = db((db.word_forms.word_form == myform) &
                                  (db.word_forms.construction == db.constructions.id)
                                  ).select()
                    if formtags:
                        for form in formtags:
                            if form.constructions.tags:
                                mytags.extend(form.constructions.tags)
                            if form.word_forms.tags:
                                mytags.extend(form.word_forms.tags)
                elif re.search(r'verb', p):  # how about participles?
                    pass
                # replace this automatically substituted field
                p = p.replace('{{{}}}'.format(f), myform)
                print f, myform
                print 'formatted A:', p

            # replace manually substituted fields
            wordlist = [w.split('|')[0] for w in words]
            man_args = zip(man_fields, wordlist)
            man_args = {a[0]: a[1] for a in man_args}
            print 'man_args', man_args
            parts[k] = p.format(**man_args)
            #first_letter = parts[k][:2].decode('utf-8').upper()
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
                    'υ': 'Υ',
                    'υ': 'Υ',
                    'φ': 'Φ',
                    'χ': 'Χ',
                    'ψ': 'Ψ',
                    'ω': 'Ω',
                    'ω': 'Ω',
                    'ω': 'Ω'}
            try:
                first_letter = caps[parts[k][:3]]
                parts[k] = first_letter + parts[k][3:]
            except KeyError:
                first_letter = caps[parts[k][:2]]
                parts[k] = first_letter + parts[k][2:]
            print 'final formatted:', parts[k]

        readables = [r for k, r in parts.iteritems() if re.match('rdbl', k)]
        resps = [r for k, r in parts.iteritems() if re.match('resp', k)]
        mytags = [t for t in mytags if not t is None]
        return parts['prompt'], resps, readables, mytags, newforms

    def make_form_agree(self, mod_form, mylemma, testing):
        """
        Return a form of the lemma "mylemma" agreeing with the supplied mod_form.

        This method is used only for nominals (nouns, pronouns, adjectives),
        excluding substantive participals. Verbs (including participles) are
        handled elsewhere.
        """
        db = current.db
        mod_parts = mod_form.split('|')
        mod_parse = mod_parts[1] if len(mod_parts) > 1 else None
        newforms = []
        if not mod_parse:
            form = db(db.word_forms.word_form == mod_form
                        ).select().first()
            case = form.grammatical_case
            print case
            gender = form.gender
            print gender
            number = form.number
            print number
        else:
            parsebits = mod_parse.split('_')
            case = abbrevs[parsebits[1]]
            print case
            gender = abbrevs[parsebits[2]]
            print gender
            number = abbrevs[parsebits[3]]
            print number
            ref_lemma = parsebits[-1]
            print ref_lemma
            pos = parsebits[0]
            print pos
            print 'newstuff111111111'
            ref_const = '{}_{}_{}_{}'.format(pos, parsebits[1],
                                                parsebits[2],
                                                parsebits[3])
            ref_lemma_id = db(db.lemmas.lemma == ref_lemma).select().first().id
            row = db((db.word_forms.source_lemma == ref_lemma_id) &
                     (db.word_forms.grammatical_case == case) &
                     (db.word_forms.gender == gender) &
                     (db.word_forms.number == number)
                     ).select().first()
            print 'row is:', row
            if not row:
                # Add the modified word form to db.word_forms
                ref_const_id = db(db.constructions.construction_label == ref_const
                                  ).select().first().id
                new = {'word_form': mod_parts[0],
                        'source_lemma': ref_lemma_id,
                        'grammatical_case': case,
                        'gender': gender,
                        'number': number,
                        'construction': ref_const_id}
                db.word_forms.insert(**new)
                newforms.append(new)
                print 'added new form ', mod_parts[0]
        # Retrieve correct form from db. If none, try to create it.
        try:
            mylemma_id = db(db.lemmas.lemma == mylemma).select().first().id
            genders = [gender, 'undetermined']
            if gender in ['masculine', 'feminine']:
                genders.append('masculine or feminine')
            for g in genders:
                print 'gender is', g
                myrow = db((db.word_forms.source_lemma == mylemma_id) &
                         (db.word_forms.grammatical_case == case) &
                         (db.word_forms.gender == g) &
                         (db.word_forms.number == number)
                         ).select().first()
                print 'row is', myrow
                if myrow:
                    print 'found row!!!!!'
                    break
            myform = myrow.word_form
        except (AttributeError, IndexError):
            print traceback.format_exc(5)
            print 'no pre-made form in db for', mylemma, mod_form
            myform = None  # FIXME: try to create and save new declined form

        return myform, newforms

    def check_for_duplicates(self, step):
        """
        Returns a 2-member tuple identifying whether there is a duplicate in db.

        tuple[0] is a boolean (True mean duplicate is present in db)
        tuple[1] is an integer (the row id of any duplicate step found)
        So negative return value is (False, 0).

        """
        db = current.db
        prompts = self.get_prompt_list(step)
        readables = self.get_readable_list(step)
        db_steps = db(db.steps.id > 0).select(db.steps.id,
                                              db.steps.prompt,
                                              db.steps.readable_response)
        for dbs in db_steps:
            db_readables = dbs.readable_response.split('|')
            if (dbs.prompt in [prompts]) and [r for d in db_readables
                                              for r in readables if r == d]:
                return (True, dbs.id)
            else:
                pass
        return (False, 0)

    def check_for_roman(self, word):
        """
        Check for roman characters mixed with Greek.
        """
        roman_chars = re.compile(r'[\u0041-\u007a]|\d')
        if not re.search(roman_chars, word):
            return False
        else:
            # TOdo: sub if necessary
            return True

    def flatten(self, items, seqtypes=(list, tuple)):
        for i, x in enumerate(items):
            while isinstance(items[i], seqtypes):
                items[i:i+1] = items[i]
        return items

    def get_tags(self, tags, tags2, tagsA, tags_extra):
        """
        Return a 3-member tuple of lists holding the tags for the current step.
        """
        # TODO: fix to separate out secondary etc.
        if tags and len(tags):
            if type(tags) == list:
                tags.extend(tags_extra)
            else:
                tags = tags_extra
            print 'tags are', tags
            tags = list(set(tags))
        else:
            tags = None
        if tags2:
            tags2 = list(set(tags2))
        else:
            tags2 = None
        if tagsA:
            tagsA = list(set(tagsA))
        else:
            tagsA = None
        return (tags, tags2, tagsA)

    def test_regex(self, regex, readables):
        """
        """
        test_regex = re.compile(regex, re.X)
        mlist = [re.match(test_regex, rsp) for rsp in readables]
        return mlist

    def write_to_db(self, step, compname):
        """ """
        db = current.db
        db.steps.insert(**step)
        sid = db(db.steps.id > 0).select().last().id
        db.paths.insert(label=self.path_label_template.format(compname),
                        steps=[sid])
        pid = db(db.paths.id > 0).select().last().id
        return (pid, sid)

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

    def make_output(self, paths, result):
        """
        Return formatted output for the make_path view after form submission.
        """
        newforms = result['new_forms']
        images = result['images_missing']
        del(result['new_forms'])
        del(result['images_missing'])
        successes = {r: v for r, v in result.iteritems() if r[0] != 'failure'}
        failures = {r: v for r, v in result.iteritems() if r[0] == 'failure'}
        message1 = ''
        message2 = ''
        if successes:
            message1 = 'Created {} new paths.\n'.format(len(successes.keys()))
        if failures:
            message2 = '{} paths failed\n'.format(len(failures.keys()))
        message = message1, message2
        output = UL()
        for s, v in successes.iteritems():
            output.append(LI(s,
                             A('path {}'.format(v[0]),
                             _href=URL('paideia', 'editing', 'listing.html',
                                     args=['paths', v[0]])),
                             A('step {}'.format(v[1]),
                             _href=URL('paideia', 'editing.html', 'listing.html',
                                     args=['steps', v[1]])),
                             _class='make_paths_success'))

        for f, v in failures.iteritems():
            output.append(LI(f, P(v[1]), _class='make_paths_failure'))

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
                               #widget=lambda f, v: AjaxSelect(f, v,
                                                            #indx=1,
                                                            #refresher=True,
                                                            #multi='basic',
                                                            #lister='simple',
                                                            #orderby='lemmas'
                                                            #).widget()
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


    def make_path(self, widget_type, lemmas, irregular):
        '''
        '''
        for lemma in lemmas:
            lemma['constructions'] = self.get_constructions(lemma)
            for idx, cst in enumerate(lemma['constructions']):  # each path
                compname = '{} {}'.format(lemma['lemma'], cst[0])
                crow = db(db.constructions.construction_label == cst
                             ).select().first()
                reg_str = crow['trans_regex_eng']
                glosses = self.make_glosses(lemma['lemma'], cst)
                rdbl = self.make_readable(glosses[:], crow['trans_templates'])
                tagset = self.get_tags(lemma, crow)
                word_form = self.get_word_form(lemma['lemma'], crow),
                try:
                    step = {'prompt': self.get_prompt(word_form, cst_row),
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
                    mtch = self.test_regex()
                    dups = self.check_for_duplicates(step)
                    if mtch and not testing and not dups:
                        self.write_to_db(step)
                        result[compname] = (pid, sid)
                    elif mtch and testing:
                        result[compname] = ('testing', pth)
                    else:
                        result[compname] = 'failure', 'readable didn\'t match'
                except Exception:
                    tbk = traceback.format_exc(5)
                    result[compname] = ('failure', tbk)
        return paths, result

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
            self.persons = ['_{}'.format(n) for n in range(1,4)]
            self.numbers = ['s', 'p']
            # TODO: this is very high loop complexity; move to db as fixed list
            self.verbcs = ['{}{}{}{}{}'.format(t, v, m, p, n)
                            for m in moods
                            for t in tenses
                            for v in voice
                            for p in persons
                            for n in numbers
                            if not (m == '_inf')
                            and not (m == '_imper' and p in ['_1', '_3'])]
            self.verbcs2 = ['{}{}{}'.format(t, v, m)
                            for m in moods
                            for t in tenses
                            for v in voice
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

    def get_tags(self, lemma, cst_row):
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
