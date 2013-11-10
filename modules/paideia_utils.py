#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
A collection of miscellaneous utility functions to be used in multiple modules.

Part of the Paideia platform built with web2py.

"""
import traceback
from gluon import current, SQLFORM
import re
from random import randrange, shuffle


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


"""
εὐγε
εἰ δοκει
*ἀκουω
*ποιεω
    Τί ποιεις Στεφανος?
*διδωμι
    Τί αύτη διδει?
    Τίς διδει τουτον τον δωρον?

φερω
θελω
    θελεις συ πωλειν ἠ ἀγοραζειν?
    Ποσα θελεις ἀγοραζειν?
ζητεω
τιμαω
    τιμαω
λαμβανω
ἀγοραζω
    Βαινε και ἀγοραζε τρεις ἰχθυας.
πωλεω
    Τί πωλεις Ἀλεξανδρος?
βλεπω
βαινω
ἐχω
ὁραω
σημαινω
διδωμι
πωλεω

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

MYWORDS = {u'πωλεω': {'glosses': ['sell'],
                      'constructions': [('pres_act_ind_2s', 'πωλεις'),
                                        ('pres_act_ind_3s', 'πωλει'),
                                        ('pres_act_ind_1p', 'πωλουμεν'),
                                        ('pres_act_ind_2p', 'πωλειτε'),
                                        ('pres_act_ind_3p', 'πωλουσι'),
                                        ('pres_act_imper_2s', 'πωλει')
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
                                        ('pres_act_ind_3p', 'ποιουσι')
                                        ('pres_act_imper_2s', 'ποιει֚'),
                                        ('pres_act_imper_2p', 'ποιειτε'),
                                        ],
                      'xtags': [121]},
           u'διδωμι': {'glosses': ['give'],
                       'constructions': [('pres_act_ind_2s', 'διδως'),
                                         ('pres_act_ind_3s', 'διδωσι'),
                                         ('pres_act_ind_1p', 'διδομεν'),
                                         ('pres_act_ind_2p', 'διδοτε'),
                                         ('pres_act_ind_3p', 'διδοασι')
                                         ('pres_act_imper_2s', 'διδου'),
                                         ('pres_act_imper_2p', 'διδοτε'),
                                         ],
                       'xtags': [121]}
           }


class PathFactory(object):

    """ An abstract parent class to create paths (with steps) procedurally. """

    def __init__(self):
        """
        """
        self.promptstrings = []

    def make_create_form(self):
        """ """
        pass

    def make_path(self, lemmas, testing=False):
        """
        Create new paths asking the user the meaning (in English) of a single
        Greek word.
        """
        db = current.db
        paths = []
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
                tagset = self.get_tags(lemma, cst_row)
                word_form = self.get_word_form(lemma['lemma'], cst_row),
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
        A placeholder method to be overridden in child classes.
        """
        pass

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

    def check_for_duplicates(self, step):
        """
        Returns a 2-member tuple identifying whether there is a duplicate in db.

        tuple[0] is a boolean (True mean duplicate is present in db)
        tuple[1] is an integer (the row id of any duplicate step found)
        So negative return value is (False, 0).

        """
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

    def check_for_roman(self):
        """
        Check for roman characters mixed with Greek.
        """
        roman_chars = re.compile(r'[\u0041-\u007a]|\d')
        for idx, wrd in enumerate(self.lemmas):
            if not re.search(roman_chars, wrd):  # check for non-Greek
                pass
            else:
                # TOdo: sub if necessary
                pass
        return self.lemmas

    def make_glosses(self, lemma, cst):
        """
        Return a list of valid glosses for the supplied lemma and construction.
        """

    def get_form(self, lemma, cst):
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

    def test_regex(self, regex, readables):
        """
        """
        test_regex = re.compile(regex, re.X)
        mlist = [re.match(test_regex, rsp) for rsp in readables]
        return mlist

    def write_to_db(self, step):
        """ """
        sids = []
        for step in steplist:
            db.steps.insert(**step)
            sid = db(db.steps.id > 0).select().last().id
            sids.append(sid)
        db.paths.insert(label=self.path_label_template.format(compname),
                        steps=[sid])
        pid = db(db.paths.id > 0).select().last().id
        return (pid, sids)

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
        successes = {r: v for r, v in result.iteritems() if r[0] != 'failure'}
        failures = {r: v for r, v in result.iteritems() if r[0] == 'failure'}
        message = 'Created {} new paths.\n' \
                  '{} paths failed'.format(len(successes.keys()),
                                            len(failures.keys()))
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


    def make_form():
        """
        Returns a form to make a translate-word path and processes the form on
        submission.

        This form, when submitted, calls self.

        """
        message = ''
        output = ''
        form = SQLFORM.factory(Field('lemmas', 'list:reference lemmas'),
                               Field('irregular_forms', 'list:string'))
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
            pass
