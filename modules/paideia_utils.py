# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

"""
A collection of miscellaneous utility functions to be used in multiple modules.
"""
import traceback
#from gluon import current
import re
from random import randrange
from pprint import pprint


def send_error(myclass, mymethod, myrequest):
    """
    Send an email reporting error and including debug info.
    """
    #mail = current.mail
    #msg = '<html>A user encountered an error in {myclass}.{mymethod}' \
          #'report failed.\n\nTraceback: {tb}' \
          #'Request:\n{rq}\n' \
          #'</html>'.format(myclass=myclass,
                           #mymethod=mymethod,
                           #tb=traceback.format_exc(5),
                           #rq=myrequest)
    #title = 'Paideia error'
    #mail.send(mail.settings.sender, title, msg)
    #print 'done sending '


def make_definition_path():
    """
    Create a new path with the appropriate steps programmatically from a list
    of input terms
    """
    #db = current.db
    roman_chars = re.compile(u'[\u0041-\u007a]|\d')
    words = {'πωλεω':           {'translations': ['sell'],
                                 'constructions': [('pres_act_inf', 'πωλειν')],
                                 'extra_tags': [128, 121]
                                 },
             'ἀγοραζω':         {'translations': ['buy', 'shop'],
                                 'constructions': [('pres_act_inf', None)],
                                 'extra_tags': [121]
                                 },
             'φερω':            {'translations': ['lift', 'carry', 'bear', 'tolerat|e', 'endur|e'],
                                 'constructions': [('pres_act_inf', None)],
                                 'extra_tags': [121]
                                 }
             }

    # Constants for all definition steps
    consts = {'pres_act_inf':       {'raw_regex': '^(?P<a>to\s){}(ing)?$',
                                     'form_func': lambda w: w.replace(w[-1], 'ειν'),
                                     'trans_templates': ['to {}', '{}ing'],
                                     'instructions': [2, 12],
                                     'tags': [49, 2],
                                     'tags_secondary': [49, 2],
                                     'tags_ahead': None
                                     },
              'pres_act_ind_1s':    ('',
                                     lambda w: w,
                                     ['I am {}ing.',
                                      'I often {}.',
                                      'I usually {}.',
                                      'I {}.',
                                      'I {} over and over.'],
                                     [],  # instructions
                                     [2],  # tags
                                     []  # tags_secondary
                                     )
              }
    qstrings = ['Τί σημαινει ὁ λογος οὑτος? {}',
                'Ὁ λογος οὑτος τί σημαινει? {}',
                'Σημαινει ὁ λογος οὑτος τί? {}',
                'Οὑτος ὁ λογος τί σημαινει? {}',
                'Σημαινει τί ὁ λογος οὑτος? {}']

    # Start assembling list of path data
    paths = []
    for w, dct in words.iteritems():
        # TODO: test responses against regex
        for c in dct['constructions']:
            construction = c[0]
            form = c[1]

            # prompt
            if not form:
                form_func = consts[construction]['form_func']
                form = form_func(w)
            promptstring = qstrings[randrange(len(qstrings))]
            pathdict = {'prompt': promptstring.format(form)}

            # response1
            transs = []
            for v in dct['translations']:
                t = v.split('|')
                if len(t) > 1:
                    v = '{}({})?'.format(t[0], t[1])
                transs.append(v)
            verb_strings = '|'.join(transs)
            regex = consts[construction]['raw_regex']
            regex = regex.format(verb_strings)
            pathdict['response1'] = regex
            pathdict['outcome1'] = 1.0

            # readable response
            readables = []
            for v in dct['translations']:
                for t in consts[construction]['trans_templates']:
                    vv = v.split('|')
                    print vv
                    tt = t.split('\{\}')
                    print tt
                    if len(t) > 1:
                        if re.match('^ing', tt[-1]):
                            v = vv[0]
                            readables.append(t.format(v))
                        elif len(vv) > 1:
                            v = '{}{}'.format(vv[0], vv[1])
                            readables.append(t.format(v))
                        else:
                            v = vv[0]
                            readables.append(t.format(v))
                    else:
                        readables.append(t.format(v))
            # TODO: randomize and select fewer
            pathdict['readable_response'] = '|'.join(readables)

            # response2
            pathdict['response2'] = '|'.join(dct['translations'])
            pathdict['outcome2'] = 0.5

            # response3
            # TODO: build from groups in regex
            # pathdict['outcome2'] = 0.4

            # tags
            tags = consts[construction]['tags']
            if dct['extra_tags']:
                tags.extend(dct['extra_tags'])
            pathdict['tags'] = tags

            tags2 = consts[construction]['tags_secondary']
            pathdict['tags_secondary'] = tags2

            tagsA = consts[construction]['tags_ahead']
            pathdict['tags_ahead'] = tagsA

            #npcs
            pathdict['npcs'] = [8]

            # locations
            pathdict['locations'] = [7]

        # remove word from input dict
            if not re.search(roman_chars, w):  # check for non-Greek in the word
                paths.append(pathdict)
                dct['constructions'].pop(dct['constructions'].index(c))  # remove the word from the source dict
    for p in paths:
        test_regex = re.compile(p['response1'], re.X)
        m = None
        for r in p['readable_response'].split('|'):
            m = re.match(test_regex, r)
        if m:
            pprint(p)
        else:
            print '\nfailed regex test----------------------------------'
            pprint(p)
            print '\n---------------------------------------------------'
        #db.steps.insert()
