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
from pprint import pprint
import traceback
from gluon import current, SQLFORM, Field, BEAUTIFY, IS_IN_DB, UL, LI
from gluon import CAT, H2
#from gluon import TABLE, TD, TR, LABEL, P, A, URL
import re
from random import randrange, shuffle
from itertools import product, chain
from paideia_utils import firstletter, capitalize, capitalize_first
from paideia_utils import sanitize_greek, flatten, multiple_replace


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
        pprint(flds)
        form = SQLFORM.factory(*flds)

        if form.process().accepted:
            print "form was processed"
            vv = request.vars
            stepsdata = []
            for n in ['one', 'two', 'three', 'four', 'five']:
                nkeys = [k for k in vv.keys() if re.match('{}.*'.format(n), k)]
                print 'nkeys'
                print nkeys
                filledfields = [k for k in nkeys if vv[k] not in ['', None]]
                if filledfields:
                    ndict = {k: vv[k] for k in nkeys}
                    stepsdata.append(ndict)

            paths = self.make_path(wordlists=[w.split('|') for w in vv['words']],
                                   label_template=vv.label_template,
                                   testing=vv.testing,
                                   avoid=vv.avoid,
                                   stepsdata=stepsdata)
            print 'got paths: ', len(paths)
            message, output = self.make_output(paths)

            print 'got output\nmessage is: ', message
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

        if testing:
            self.mock = True
        paths = []
        images_missing = []
        new_forms = []
        if len(wordlists) > 1:
            combos = list(product(*wordlists))
        else:
            combos = wordlists[0]
        if avoid:
            combos = [x for x in combos
                      if not any([set(y).issubset(set(x)) for y in avoid])]

        # loop to create one path for each combo
        for c in combos:
            label = label_template.format('-'.join([i.split('|')[0] for i in c]))
            mykeys = ['words{}'.format(n) for n in range(len(c))]
            combodict = dict(zip(mykeys, c))
            #print 'combos'
            #pprint(combodict)

            pathresult = {'steps': {}}
            pathsteps = []
            for i, s in enumerate(stepsdata):  # loop for each step in path
                print 'step', i
                pprint(s)
                # filter out step identifier prefixes from field names
                numstrings = ['one_', 'two_', 'three_', 'four_', 'five_']
                s = {k.replace(numstrings[i], ''): v for k, v in s.iteritems()}
                stepresult, newforms, imiss = self.make_step(combodict, s)
                pathsteps.append(stepresult[0])
                pathresult['steps'][stepresult[0]] = stepresult[1]
                new_forms.append(newforms)
                images_missing.extend(imiss)
            if all([isinstance(k, int) for k in pathresult['steps'].keys()]):
                pid = self.write_to_db(pathsteps, label)
            else:
                pid = 'path not written'
            paths.append(pid)
            pathresult['path id'] = pid
            pathresult['new_forms'] = new_forms
            pathresult['images_missing'] = images_missing
            paths.append(pathresult)

        return paths

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
        ptemp = sdata['prompt_template']
        ptemp = ptemp.split('|')
        ptemp = [ptemp] if not isinstance(ptemp, list) else ptemp
        xtemp = sdata['response_template']
        xtemp = [xtemp] if not isinstance(xtemp, list) else xtemp
        rtemp = sdata['readable_template']
        rtemp = rtemp.split('|')
        rtemp = [rtemp] if not isinstance(rtemp, list) else rtemp
        tags1 = sdata['tags']
        itemp = sdata['image_template']
        tags2 = sdata['tags_secondary']
        tags3 = sdata['tags_ahead'] if 'tags_ahead' in sdata.keys() else None
        npcs = sdata['npcs']
        locs = sdata['locations']
        points = sdata['points'] if 'points' in sdata.keys() else 1.0, 0.0, 0.0

        img = self.make_image(combodict, itemp) if itemp else None
        imgid = img[0] if img else None
        #ititle = img[1] if img else None
        images_missing = img[2] if img else None

        pros, rxs, rdbls, newfs = self.formatted(combodict, ptemp, xtemp, rtemp)
        tags = self.get_step_tags(tags1, tags2, tags3, pros, rdbls)
        kwargs = {'prompt': sanitize_greek(pros[randrange(len(pros))]),
                  'widget_type': mytype,
                  #'widget_audio': None,
                  'widget_image': imgid,
                  'response1': rxs[0],
                  'readable_response': '|'.join([sanitize_greek(r)
                                                 for r in rdbls]),
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
            mtch = self.test_regex(kwargs['response1'], rdbls)
            dups = self.check_for_duplicates(kwargs, rdbls, pros)
            if mtch and not self.mock and not dups[0]:
                stepresult = self.write_step_to_db(kwargs), kwargs
            elif mtch and not dups[0] and self.mock:
                stepresult = 'testing', kwargs
            elif mtch and dups[0]:
                stepresult = 'duplicate step', dups
            else:
                stepresult = 'failure', 'readable didn\'t match regex'
        except Exception:
            tracebk = traceback.format_exc(5)
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

    def formatted(self, combodict, ptemps, xtemps, rtemps):
        """
        Return a list of the template formatted with each of the words.

        The substitution format in each string looks like:
           {{wordsX}} for manual substitution (word forms unchanged)
           {{wordsY-wordsX}} or {{lemma-wordsX}}
                for automatic substitution (word parsed to agree with another
                being substituted elsewhere).
        """
        newforms = []  # collect any new word forms created in db along the way
        readables = []
        regexes = {}  # need keys to ensure proper priority
        prompts = []

        parts = {'prompt{}'.format(i): r for i, r in enumerate(ptemps) if r}
        print 'parts is: =================================='
        pprint(parts)
        xtemps = [xtemps] if type(xtemps) != list else xtemps
        regexes = {'regex{}'.format(i): r for i, r in enumerate(xtemps) if r}
        print 'regexes is: =================================='
        pprint(regexes)
        rdbls = {'rdbl{}'.format(i): r for i, r in enumerate(rtemps) if r}
        print 'rdbls is: =================================='
        pprint(rdbls)
        parts.update(regexes)
        parts.update(rdbls)
        print 'parts is: =================================='
        pprint(parts)

        # perform substitutions for each "part" to be returned
        for k, p in parts.iteritems():
            inflected = []
            print 'for part ', k, p, '------------------------------'
            fields = re.findall(r'(?<={{).*?(?=}})', p)
            print 'fields ==============================='
            pprint(fields)
            inflected_fields = [f for f in fields if len(f.split('-')) > 1]
            print 'inflected_fields ==============================='
            pprint(inflected_fields)

            # get inflected forms to substitute
            for f in fields:
                if f in inflected_fields:
                    myform, newform = self.get_inflected(f, combodict)
                    if newform:  # note any additions to db.word_forms
                        newforms.append(newform)
                else:
                    myform = combodict[f]
                # add case handling for fields in regex
                if re.match(r'regex', k):
                    lower, tail = firstletter(myform)
                    myform = '({}|{})?{}'.format(lower, capitalize(lower), tail)

                inflected.append(('{{{}}}'.format(f), myform))
                print 'myform is: =================================='
                print myform
                print 'f is: =================================='
                print f

            print 'inflected are: ==================================='
            pprint(inflected)
            formatted = multiple_replace(inflected, p)

            # add formatted string to appropriate collection for return
            if re.match(r'regex.*', k):
                idx = k.replace('regex', '')
                regexes[idx] = formatted
            elif re.match(r'rdbl.*', k):
                readables.append(capitalize_first(formatted))
            else:
                prompts.append(capitalize_first(formatted))

        return prompts, regexes, readables, newforms

    def get_inflected(self, field, combodict):
        """
        Get the properly inflected word form for the supplied field.
        """
        db = current.db
        lemma, mod = field.split('-')
        # if lemma is pointer to a word list
        lemma = combodict[lemma] if lemma in combodict.keys() else lemma
        # allow for passing inflected form instead of lemma
        if not db.lemmas(db.lemmas.lemma == lemma):
            myrow = db.word_forms(db.word_forms.word_form == lemma)
            lemma = myrow.lemma.lemma
        # inflect lemma to agree with its governing word
        modform = combodict[mod]
        myform, newform = self.make_form_agree(modform, lemma)

        return myform, newform

    def make_form_agree(self, mod_form, mylemma):
        """
        Return a form of the lemma "mylemma" agreeing with the supplied mod_form.

        This method is used only for nominals (nouns, pronouns, adjectives),
        excluding substantive participals. Verbs (including participles) are
        handled elsewhere.
        """
        db = current.db
        newform = None

        form = db(db.word_forms.word_form == mod_form).select().first()
        case = form.grammatical_case
        gender = form.gender
        number = form.number
        #else:
            #parsebits = mod_parse.split('_')
            #case = abbrevs[parsebits[1]]
            #gender = abbrevs[parsebits[2]]
            #number = abbrevs[parsebits[3]]
            #ref_lemma = parsebits[-1]
            #pos = parsebits[0]
            #ref_const = '{}_{}_{}_{}'.format(pos, parsebits[1],
                                             #parsebits[2],
                                             #parsebits[3])
            #ref_lemma_id = db(db.lemmas.lemma == ref_lemma).select().first().id
            #row = db((db.word_forms.source_lemma == ref_lemma_id) &
                     #(db.word_forms.grammatical_case == case) &
                     #(db.word_forms.gender == gender) &
                     #(db.word_forms.number == number)
                     #).select().first()
            #if not row:
                ## Add the modified word form to db.word_forms
                #ref_const_id = db(db.constructions.construction_label == ref_const
                                  #).select().first().id
                #new = {'word_form': mod_parts[0],
                       #'source_lemma': ref_lemma_id,
                       #'grammatical_case': case,
                       #'gender': gender,
                       #'number': number,
                       #'construction': ref_const_id}
                #db.word_forms.insert(**new)
                #newforms.append(new)
        # Retrieve correct form from db. If none, try to create it.
        try:
            mylemma_id = db(db.lemmas.lemma == mylemma).select().first().id
            # allow for ambiguous gender forms
            genders = [gender, 'undetermined']
            if gender in ['masculine', 'feminine']:
                genders.append('masculine or feminine')
            myrow = db((db.word_forms.source_lemma == mylemma_id) &
                       (db.word_forms.grammatical_case == case) &
                       (db.word_forms.gender.belongs(genders)) &
                       (db.word_forms.number == number)
                       ).select().first()
            myform = myrow.word_form
        except (AttributeError, IndexError):
            print traceback.format_exc(5)
            print 'no pre-made form in db for', mylemma, mod_form
            myform = None  # FIXME: try to create and save new declined form
            newform = 'I\'m new'

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
        allforms = chain(*words)
        allforms = list(set(allforms))

        # Get tags for all lemmas and forms in allforms
        # TODO: Should allforms include all words or only substitutions?
        formrows = db((db.word_forms.word_form.belongs(allforms)) &
                      (db.word_forms.construction == db.constructions.id)
                      ).select()
        constags = [f.constructions.tags for f in formrows]
        formtags = [f.word_forms.tags for f in formrows]
        firsttags = [f.word_forms.lemma.first_tag for f in formrows]
        xtags = [f.word_forms.lemma.extra_tags for f in formrows]

        newtags = chain(constags, formtags, firsttags, xtags)
        newtags = list(set(flatten(formtags)))
        # assume at first that all form tags are secondary
        tags2.extend(newtags)

        newtags1, newtags2, newtags3 = [], [], []
        alltags = chain(tags1, tags2, tags3)
        tagrows = db(db.tags.id.belongs(alltags)).select(db.tags.id,
                                                         db.tags.position)
        steplevel = max([t.position for t in tagrows])
        for t in tagrows:
            if t.position == steplevel:
                newtags1.append(t)
            elif t.position < steplevel:
                newtags2.append(t)
            else:
                newtags3.append(t)

        return (newtags1, newtags2, newtags3)

    def test_regex(self, regex, readables):
        """
        Return True if the supplied strings satisfy the supplied regex.
        """
        readables = readables if type(readables) == list else [readables]
        test_regex = re.compile(regex, re.X)
        mlist = [re.match(test_regex, rsp) for rsp in readables]
        if all(mlist):
            return True
        else:
            return False

    def write_step_to_db(self, kwargs):
        """ """
        db = current.db
        try:
            sid = db.steps.insert(**kwargs)
            return sid
        except Exception:
            print traceback.format_exc(5)
            return False

    def write_to_db(self, steps, label):
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
        opts = {'goodpaths': [p for p in paths if isinstance(p['path id'], int)],
                'badpaths': [p for p in paths if not isinstance(p['path id'], int)]}
        outs = {'goodpaths': UL(),
                'badpaths': UL()}
        newforms = []
        images = []

        for opt in ['goodpaths', 'badpaths']:
            badcount = 0

            for p in opts[opt]:
                if opt == 'badpaths':
                    badcount += 1

                successes = [s for s, v in p['steps']
                             if s[0] not in ['failure', 'duplicate step']]
                failures = [s for s, v in p['steps'] if s[0] == 'failure']
                duplicates = [s for s, v in p['steps'] if s[0] == 'duplicate step']

                pout = LI('Path {}'.format(p['path id']))
                pout.append(LI('steps succeeded: {}'.format(len(successes))))
                pout.append(LI('steps failed: {}'.format(len(failures))))
                pout.append(LI('steps were duplicates: {}'.format(len(duplicates))))
                steps = UL()
                for s in p['steps']:
                    steps.append(LI(BEAUTIFY(s)))
                pout.append(LI(steps))

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
        result = []
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
                    mtch = self.test_regex()
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
