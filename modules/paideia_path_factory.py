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
import traceback
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB, UL, LI
from gluon import CAT, H2
import re
from random import randrange, shuffle
from itertools import product, chain
from paideia_utils import capitalize_first, test_regex, uprint
from paideia_utils import flatten, multiple_replace, islist  # sanitize_greek,
import datetime


class PathFactory(object):
    """
    An abstract parent class to create paths (with steps) procedurally.

    """

    def __init__(self):
        """Initialize an object. """
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
                Field('avoid', 'list:string'),
                Field('testing', 'boolean')]

        for n in ['one', 'two', 'three', 'four', 'five']:
            fbs = [Field('{}_prompt_template'.format(n), 'list:string'),
                   Field('{}_response_template'.format(n), 'list:string'),
                   Field('{}_readable_template'.format(n), 'list:string'),
                   Field('{}_tags'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True)),
                   Field('{}_tags_secondary'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id',
                                           '%(tag)s',
                                           multiple=True)),
                   Field('{}_tags_ahead'.format(n), 'list:reference tags',
                         requires=IS_IN_DB(db, 'tags.id', '%(tag)s',
                                           multiple=True)),
                   Field('{}_npcs'.format(n), 'list:reference npcs',
                         requires=IS_IN_DB(db, 'npcs.id', '%(name)s',
                                           multiple=True)),
                   Field('{}_locations'.format(n), 'list:reference locations',
                         requires=IS_IN_DB(db, 'locations.id', '%(map_location)s',
                                           multiple=True)),
                   Field('{}_step_type'.format(n), 'list:reference step_types',
                         requires=IS_IN_DB(db, 'step_types.id', '%(step_type)s',
                                           multiple=True)),
                   Field('{}_image_template'.format(n), 'string')]
            flds.extend(fbs)
        #pprint(flds)
        form = SQLFORM.factory(*flds)

        if form.process().accepted:
            #print "form was processed"
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
                                   testing=vv.testing,
                                   avoid=vv.avoid,
                                   stepsdata=stepsdata)
            #print 'got paths: ', len(paths)
            message, output = self.make_output(paths)

            #print 'got output\nmessage is: ', message
        elif form.errors:
            message = BEAUTIFY(form.errors)
            print 'form had errors:', message

        return form, message, output

    def make_path(self, wordlists, label_template=None, stepsdata=None,
                  avoid=None, testing=False):
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
        print "starting module======================================"
        print datetime.datetime.now()
        print "======================================"

        if testing:
            self.mock = True

        combos = self.make_combos(wordlists, avoid)
        #print 'for {} combos'.format(len(combos))
        paths = {}
        for idx, c in enumerate(combos):  # one path for each combo
            #print 'path for combo {}'.format(idx)
            #print '====================================================='
            label = label_template.format('-'.join([i.split('|')[0] for i in c]))
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
            pgood = [isinstance(k, int) for k in pdata['steps'].keys()]
            pid = self.path_to_db(pdata['steps'], label) \
                if all(pgood) and not self.mock else 'path not written {}'.format(idx)
            paths[pid] = pdata
            #uprint(pdata)
        #print 'paths ====================================================='
        #print paths.keys()

        return paths

    def make_combos(self, wordlists, avoid):
        """
        Return a list of tuples holding all valid combinations of given words.

        Avoid parameter allows exclusion of certain combinations.

        """
        if len(wordlists) > 1:
            combos = list(product(*wordlists))
        else:
            combos = [(l,) for l in wordlists[0] if l]
            combos = [tup for tup in combos if tup]
        if avoid:
            combos = [x for x in combos
                      if not any([set(y).issubset(set(x)) for y in avoid])]
        #print "combos ==================================="
        #uprint(combos)
        #pprint(combos)
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

        ptemp = islist(sdata['prompt_template'].split('|'))
        xtemp = islist(sdata['response_template'].split('||'))
        rtemp = islist(sdata['readable_template'].split('|'))

        tags1 = sdata['tags']
        #print 'tags received from form ======================================='
        #print tags1
        itemp = sdata['image_template']
        tags2 = sdata['tags_secondary']
        #print 'tags received from form ======================================='
        #print tags2
        tags3 = sdata['tags_ahead'] if 'tags_ahead' in sdata.keys() else None
        #print 'tags received from form ======================================='
        #print tags3
        npcs = sdata['npcs']
        locs = sdata['locations']
        points = sdata['points'] if 'points' in sdata.keys() and sdata['points'] \
            else 1.0, 0.0, 0.0

        img = self.make_image(combodict, itemp) if itemp else None
        imgid = img[0] if img else None
        #ititle = img[1] if img else None
        images_missing = img[2] if img else None

        pros, rxs, rdbls, newfs = self.format_strings(combodict, ptemp, xtemp, rtemp)
        tags = self.get_step_tags(tags1, tags2, tags3, pros, rdbls)
        #print 'pros returned from formatted ================================'
        #uprint(pros)
        #print 'rdbls returned from formatted ================================'
        #uprint(rdbls)
        #print 'rxs returned from formatted ================================'
        #uprint(rxs)
        kwargs = {'prompt': pros[randrange(len(pros))],  # sanitize_greek(pros[randrange(len(pros))]),
                  'widget_type': mytype,
                  #'widget_audio': None,
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
                  'locations': locs}  # [randrange(len(npcs))] if mult

        try:
            matchdicts = [test_regex(x, rdbls) for x in rxs]
            xfail = {}
            for idx, regex in enumerate(rxs):
                mtch = all(matchdicts[idx].values())
                if not mtch:
                    problems = [k for k, v in matchdicts[idx].iteritems() if not v]
                    xfail[regex] = problems
                    #print 'regex {} failed with string: {}'.format(idx, problems)
            dups = self.check_for_duplicates(kwargs, rdbls, pros)
            if mtch and not self.mock and not dups[0]:
                stepresult = self.step_to_db(kwargs), kwargs
            elif mtch and not dups[0] and self.mock:
                stepresult = 'testing', kwargs
            elif mtch and dups[0]:
                stepresult = 'duplicate step', dups
            else:
                stepresult = 'regex failure', xfail
        except Exception:
            tracebk = traceback.format_exc(12)
            stepresult = ('failure', tracebk)

        return stepresult, newfs, images_missing

    def make_image(self, combodict, itemp):
        """
        Check for an image for the given combo and create if necessary.

        If a new image record is created, this method also adds its id and
        title directly to the instance variable images_missing.

        """
        db = current.db
        images_missing = []
        mytitle = itemp.format(**combodict)
        img_row = db(db.images.title == mytitle).select().first()
        if not img_row:
            myid = db.images.insert(title=mytitle)
            images_missing.append((myid, mytitle))
        else:
            myid = img_row.id

        return myid, mytitle, images_missing

    def format_strings(self, combodict, ptemps, xtemps, rtemps):
        u"""
        Return a list of the template formatted with each of the words.

        The substitution format in each string looks like:
           {{wordsX}} for manual substitution (word forms unchanged)
           {{wordsY-wordsX}} or {{lemma-wordsX}}
                for automatic substitution (word parsed to agree with another
                being substituted elsewhere).
        """
        prompts = [self.do_substitution(p, combodict) for p in ptemps]
        #print 'got prompts'
        #uprint(prompts)
        p_new = [p[1] for p in prompts]
        prompts = [capitalize_first(p[0]) for p in prompts]
        rxs = [self.do_substitution(x, combodict) for x in xtemps]
        #print 'got regexes'
        #uprint(rxs)
        x_new = [x[1] for x in rxs]
        rxs = [x[0] for x in rxs]
        rdbls = [self.do_substitution(r, combodict) for r in rtemps]
        #print 'got readables'
        #uprint(rdbls)
        r_new = [r[1] for r in rdbls]
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
        subpairs = []
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
            subpairs.append(('{{{}}}'.format(f), myform))

        #print 'subpairs ==================================='
        #uprint(subpairs)
        ready_strings = multiple_replace(temp, subpairs[0])
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
        except KeyError:
            aspect = None
        # if lemma is pointer to a word list
        lemma = combodict[lemma] if lemma in combodict.keys() else lemma
        # allow for passing inflected form instead of lemma
        if not db.lemmas(db.lemmas.lemma == lemma):
            myrow = db.word_forms(db.word_forms.word_form == lemma)
            lemma = myrow.source_lemma.lemma
        # inflect lemma to agree with its governing word
        modform = combodict[mod]
        myform, newform = self.make_form_agree(modform, lemma, aspect)

        return myform, newform

    def make_form_agree(self, mod_form, mylemma, constraint=None):
        """
        Return a form of the lemma "mylemma" agreeing with the supplied mod_form.

        This method is used only for nominals (nouns, pronouns, adjectives),
        excluding substantive participals. Verbs (including participles) are
        handled elsewhere.
        """
        db = current.db
        newform = None
        lem = db(db.lemmas.lemma == mylemma).select.first()
        ref = db(db.word_forms.word_form == mod_form).select().first()
        # use provided constraints where present in field
        # allow for use of short forms
        cdict = {}
        if constraint:
            cparsebits = constraint.split('_')
            cparsing = [b.split(':') for b in cparsebits]
            cdict = {cp[0]: cp[1] for cp in cparsing}
        equivs = {'masc': 'masculine',
                  'fem': 'feminine',
                  'neut': 'neuter',
                  'nome': 'nominative',
                  'gen': 'genitive',
                  'dat': 'dative',
                  'acc': 'accusative',
                  'sing': 'singular',
                  'plu': 'plural',
                  'plur': 'plural'}
        case = cdict['case'] if 'case' in cdict.keys() else ref.grammatical_case
        gender = cdict['gender'] if 'gender' in cdict.keys() else ref.gender
        number = cdict['number'] if 'number' in cdict.keys() else ref.number
        for n in [case, gender, number]:
            n = equivs[n] if n in equivs.keys() else n
        # allow for ambiguously gendered forms
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
        myform = myrow.word_form
        # TODO: automatically create form if not in db
        #if not row:
            ## Add the modified word form to db.word_forms
            #ref_const_id = db(db.constructions.construction_label == ref_const
                                #).select().first().id
            #db.word_forms.insert(**new)
            #newforms.append(new)
                #'grammatical_case': case,
                #'gender': gender,
                #'number': number,
                #'construction': ref_const_id}
        #case = abbrevs[parsebits[1]]
        #gender = abbrevs[parsebits[2]]
        #number = abbrevs[parsebits[3]]
        #ref_lemma = parsebits[-1]
        #pos = parsebits[0]
        #ref_const = '{}_{}_{}_{}'.format(pos, parsebits[1],
                                            #parsebits[2],
                                            #parsebits[3])
        #ref_lemma_id = db(db.lemmas.lemma == ref_lemma).select().first().id
        #except (AttributeError, IndexError):
            #print traceback.format_exc(5)
            #uprint(('no pre-made form in db for', mylemma, mod_form))
            #myform = None  # FIXME: try to create and save new declined form
            #newform = 'I\'m new'
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
        tags1 = tags1 if tags1 else []
        tags2 = tags2 if tags2 else []
        tags3 = tags3 if tags3 else []

        words = [p.split(' ') for p in prompts]
        words.extend([r.split(' ') for r in rdbls])
        allforms = list(chain(*words))
        allforms = list(set(allforms))
        #print 'allforms================================================'
        #uprint(allforms)

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
        #print 'newtags ================================================'
        #print newtags
        newtags = list(set(flatten(newtags)))
        # assume at first that all form tags are secondary
        tags2.extend(newtags)

        newtags1, newtags2, newtags3 = [], [], []
        alltags = list(chain(tags1, tags2, tags3))
        #print 'alltags ================================================'
        #print alltags
        tagrows = db(db.tags.id.belongs(alltags)).select(db.tags.id,
                                                         db.tags.tag_position)
        steplevel = max([t.tag_position for t in tagrows])
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
            print traceback.format_exc(5)
            return False

    def path_to_db(self, steps, label):
        """ """
        db = current.db
        try:
            pid = db.paths.insert(label=label, steps=steps)
            return pid
        except Exception:
            print traceback.format_exc(5)
            return False

    def make_output(self, paths):
        """
        Return formatted output for the make_path view after form submission.

        """
        #print 'output keys =============================================='
        #print paths.values()[0]
        opts = {'goodpaths': {p: v for p, v in paths.iteritems()
                              if isinstance(p, int)},
                'badpaths': {p: v for p, v in paths.iteritems()
                             if not isinstance(p, int)}}
        #print len(opts['goodpaths'].keys())
        #print len(opts['badpaths'].keys())
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
                content = uprint(pv['steps'])
                #content = uprint(pformat(pv['steps']))
                psub.append(LI(content))
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
                    tbk = traceback.format_exc(5)
                    result[compname] = ('failure', tbk)
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
        #print 'step tags ==========================================='
        #print list(chain(tags, tags2, tagsA))
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
