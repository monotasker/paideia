#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
A collection of miscellaneous utility functions to be used in multiple modules.
"""
import traceback
from gluon import current
import re
from random import randrange, shuffle
from pprint import pprint


def send_error(myclass, mymethod, myrequest):
    """
    Send an email reporting error and including debug info.
    """
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
                      'constructions': [('pres_act_inf', 'πωλειν')],
                      'xtags': [128, 121]},
           u'ἀγοραζω': {'glosses': ['buy', 'shop|p'],
                       'constructions': [('pres_act_inf', None)],
                       'xtags': [121]},
           u'φερω': {'glosses': ['lift', 'carry', 'bear', 'tolerat|e', 'endur|e'],
                   'constructions': [('pres_act_inf', None)],
                   'xtags': [121]}
           }


CONSTRUCTIONS = {'pres_act_inf': {'raw_regex': r'^(?P<a>to\s)?({})(?(a)|ing)$',
                                  'form_func': lambda w: ('{}{}').format(w[:-2],
                                                                         'ειν'),
                                  'trans_templates': ['to {}', '{}ing'],
                                  'instructions': [2, 12],
                                  'tags': [49, 2],
                                  'tags_secondary': [],
                                  'tags_ahead': None
                                  },
                 'pres_act_ind_1s': {'raw_regex': '',
                                     'form_func': lambda w: w,
                                     'trans_templates': ['I am {}ing.',
                                                         'I often {}.',
                                                         'I usually {}.',
                                                         'I {}.',
                                                         'I {} over and over.'
                                                         ],
                                     'instructions': [],
                                     'tags': [2],
                                     'tags_secondary': [],
                                     'tags_ahead': None
                                     }
                 }


class PathFactory(object):
    """
    A class to create paths (with constituent steps) procedurally.
    """

    def make_path(self, words=MYWORDS, consts=CONSTRUCTIONS):
        """
        Create new paths asking the user the meaning (in English) of a single
        Greek word.
        """
        #db = current.db
        # Constants for all definition steps
        roman_chars = re.compile(r'[\u0041-\u007a]|\d')

        paths = []
        result = {}
        db = current.db
        for wrd, dct in words.iteritems():
            for idx, cst in enumerate(dct['constructions']):  # loop each path
                try:
                    glosses = dct['glosses']
                    mycst = consts[cst[0]]
                    pth = {'prompt': self.choose_form(cst, mycst['form_func'], wrd)}
                    # FIXME: why do I need to copy glosses?
                    pth['response1'] = self.make_regex(glosses[:], mycst['raw_regex'])
                    pth['outcome1'] = 1.0
                    rdbl = self.make_readable(glosses, mycst['trans_templates'])
                    pth['readable_response'] = rdbl
                    pth['response2'] = self.make_glosslist(glosses)
                    pth['outcome2'] = 0.5
                    # response3  # TODO: build from groups in regex
                    # pth['outcome2'] = 0.4
                    tags = consts[cst[0]]['tags']
                    if dct['xtags']:
                        tags.extend(dct['xtags'])
                    pth['tags'] = list(set(tags))
                    pth['tags_secondary'] = mycst['tags_secondary']
                    pth['tags_ahead'] = mycst['tags_ahead']
                    pth['npcs'] = [8]
                    pth['locations'] = [7]

                    # remove word from input dict
                    if not re.search(roman_chars, wrd):  # check for non-Greek
                        paths.append(pth)
                    test_regex = re.compile(pth['response1'], re.X)
                    mtch = None
                    for rsp in pth['readable_response'].split('|'):
                        mtch = re.match(test_regex, rsp)
                    if mtch:
                        #pprint(pth)
                        compname = '{} {}'.format(wrd, cst[0])
                        db.steps.insert(**pth)
                        sid = db(db.steps.id > 0).select().last().id
                        db.paths.insert(label='Meaning? {}'.format(compname),
                                        steps=[sid])
                        pid = db(db.paths.id > 0).select().last().id
                        result[compname] = (pid, sid)
                    else:
                        result[compname] = 'failure', 'readable didn\'t match'
                        print '\nfailed regex test----------------------------------'
                        pprint(pth)
                        print '\n---------------------------------------------------'
                except Exception:
                    compname = '{} {}'.format(wrd, cst[0])
                    tbk = traceback.format_exc(5)
                    result[compname] = ('failure', tbk)
        return paths, result

    def choose_form(self, const_tpl, func, word):
        """
        Return the correct inflected form of the current word.

        :arg:   func: A lambda function to inflect the base form of the word
        :arg:   word: The base form (first-person singular) of the word to be
                      inflected.
        """

        form = const_tpl[1]

        print '=============================================='
        print word
        print word[:-1]
        print word[:-3]
        myform = func(word) if not form else form
        print myform
        print '=============================================='

        qstrings = ['Τί σημαινει ὁ λογος οὑτος? {}',
                    'Ὁ λογος οὑτος τί σημαινει? {}',
                    'Σημαινει ὁ λογος οὑτος τί? {}',
                    'Οὑτος ὁ λογος τί σημαινει? {}',
                    'Σημαινει τί ὁ λογος οὑτος? {}']

        promptstring = qstrings[randrange(len(qstrings))]
        mystring = promptstring.format(myform)

        return mystring

    def make_glosslist(self, glossbits):
        """
        Return a bar-separated list of glosses as a single string.
        """
        glossbits = [g.split('|')[0] for g in glossbits]
        gss = '|'.join(glossbits)
        return gss

    def make_readable(self, glosses, templates):
        """
        Return a list of readable glosses using the given template and a
        string of glosses separated by |.

        This includes removing or doubling the final letters of the gloss as
        needed (e.g., before -ing).
        """
        readables = []
        for val in glosses:
            for templt in templates:
                vvs = val.split('|')
                tts = templt.split('{}')
                if len(tts) > 1:
                    if re.match('^(ing|ed)', tts[-1]):
                        if len(vvs) > 1 and vvs[1] == 'e':
                            val = vvs[0]
                        elif len(vvs) > 1 and vvs[1] == 'p':
                            val = '{}{}'.format(vvs[0], vvs[1])
                        readables.append(templt.format(val))
                    elif len(vvs) > 1:
                        val = '{}{}'.format(vvs[0], vvs[1])
                        readables.append(templt.format(val))
                    else:
                        val = vvs[0]
                        readables.append(templt.format(val))
                else:
                    readables.append(templt.format(val))
        shuffle(readables)
        readable_string = '|'.join(readables[:7])
        return readable_string

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
