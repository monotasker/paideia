#! /usr/bin/python
# -*- coding: utf-8-*-
from gluon import current, BEAUTIFY
from gluon import IMG, URL, SQLFORM, SPAN, UL, LI, Field, P, HTML
from gluon import IS_NOT_EMPTY, IS_IN_SET

from copy import copy
import datetime
from dateutil import parser
from inspect import getargvalues, stack
from itertools import chain
import os
from paideia_utils import Paideia_Debug, GreekNormalizer
import pickle
from plugin_utils import flatten, makeutf8, ErrorReport
from pprint import pprint
from pytz import timezone
from random import randint, randrange
import re
import sys
import traceback

"""
ABOUT
---------
This module holds the core game logic for the Paideia web-app for language
learning. It is designed to run in the context of the web2py framework and
relies heavily on the pydal database abstraction layer, developed as part of
web2py.

CREDITS AND COPYRIGHT
---------------------
Copyright Ian W. Scott, 2012-2015
Additional contributions by Joseph Boakye <jboakye@bwachi.com> (Fall 2014)

DEBUG MODE
------------
current.paideia_DEBUG_MODE is set in Walk.init

UPGRADING
-----------
The following files exist outside the paideia app folder and so need to be
watched when upgrading web2py:
- web2py/routes.py

"""


class MyPickler (pickle.Pickler):
    """Pickler subclass for debugging pickling problems."""
    def save(self, obj):
        try:
            pickle.Pickler.save(self, obj)
        except Exception, e:
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            print 'pickling object of type', type(obj)
            print obj
            print 'error ================'
            print e


def util_get_args():
    """
    Returns a collection of all the calling function's arguments.
    The returned collection is a tuple containing dictionary of calling
    function's named arguments and a list of calling function's unnamed
    positional arguments.
    By Kelly Yancey:
    kbyanc.blogspot.ca/2007/07/python-aggregating-function-arguments.html
    """
    posname, kwname, args = getargvalues(stack()[1][0])[-3:]
    posargs = args.pop(posname, [])
    args.update(args.pop(kwname, []))
    return args, posargs


class Map(object):
    def __init__(self):
        """
        """
        pass

    def show(self, mapnum=None, db=None):
        """
        Return data for the paideia navigation map interface.
        The mapnum argument is to facilitate future expansion to multiple
        levels of the map.
        """
        db = current.db if not db else db
        cache = current.cache

        map_image = '/paideia/static/images/town_map.svg'
        # TODO: Review cache time
        locations = db().select(db.locations.ALL,
                                orderby=db.locations.map_location,
                                cache=(cache.ram, 60 * 60)).as_list()
        return {'map_image': map_image, 'locations': locations}


class Walk(object):
    """
    Main interface class for the paideia module, intended to be called by
    the controller.
    """

    def __init__(self, tag_records=None, tag_progress=None,
                 response_string=None, userdata=None, db=None,
                 new_user=None):
        """Initialize a Walk object."""
        #set DEBUG_MODE to True to see debugging info on the screen
        #-----------------------------------------------
        self.DEBUG_MODE = False
        current.paideia_DEBUG_MODE = self.DEBUG_MODE
        current.paideia_debug = Paideia_Debug()
        current.sequence_counter = 0

        db = current.db if not db else db
        self.response_string = response_string
        self.user = self._get_user(userdata=userdata,
                                   tag_records=tag_records,
                                   tag_progress=tag_progress,
                                   new_user=new_user)
        self.record_id = None  # stores step log row id after db update

    def _new_user(self, userdata, tag_records, tag_progress):
        '''Return a new User object for the currently logged in user.'''
        auth = current.auth
        db = current.db
        uid = auth.user_id
        userdata = db.auth_user[uid].as_dict() if not userdata else userdata
        if not tag_records:
            tag_records = db(db.tag_records.name == uid).select()
            if tag_records: tag_records = tag_records.as_list()
        if not tag_progress:
            tag_progress = db(db.tag_progress.name == uid).select()
            if tag_progress:
                tag_progress = tag_progress.first()
            else:
                db.tag_progress.insert(latest_new=1)
                db.commit()
                tag_progress = db(db.tag_progress.name == uid).select().first()
            tag_progress = tag_progress.as_dict()
        return User(userdata, tag_records, tag_progress, blocks=[])  # TODO: find out where the mysterious blocks are coming from

    def _get_user(self, userdata=None, tag_records=None,
                  tag_progress=None, new_user=None):
        '''
        Initialize or re-activate User object.
        All named arguments are necessary.
        '''
        auth = current.auth
        db = current.db
        try:  # look for user object already on this Walk or new_user flag set
            assert (self.user) and new_user is None
        except (AttributeError, AssertionError):  # because no user yet on this Walk
            try:
                sd = db(db.session_data.name ==
                        auth.user_id).select().first()
                if sd:
                    sys.path.append(os.path.dirname(__file__))
                    self.user = pickle.loads(sd['other_data'])
                else:
                    self.user = None
                assert self.user
                assert self.user.is_stale() is False
                assert not new_user
                # FIXME: temporary sanitization of pickled session data
                # adjusting to new db field names - Apr 28, 2015
                tp = self.user.tag_progress
                tpkeys = tp.keys()
                for oldkey, newkey in {'just_cats': 'cat1_choices',
                                       'all_cats': 'all_choices'}.iteritems():
                    if oldkey in tpkeys:
                        current.paideia_debug.do_print('removing {} from stored '
                                                       'tag_progress'.format(oldkey),
                                                       'Walk.get_user')
                        tp[newkey] = copy(tp[oldkey])
                        del tp[oldkey]
                # FIXME: end of temporary sanitization
                current.paideia_debug.do_print('re-using user from '
                                               'db ------------',
                                               'Walk.get_user')

            except (KeyError, TypeError):  # Problem with session data
                print traceback.format_exc(5)
                self.user = self._new_user(userdata, tag_records, tag_progress)
            except (AssertionError, AttributeError):  # user stale or block
                self.user = self._new_user(userdata, tag_records, tag_progress)
                current.paideia_debug.do_print('creating new user from data '
                                               '------------',
                                               'Walk._get_user')
        if isinstance(self.user.quota, list):
            self.user.quota = self.user.quota[0]
        return self.user

    def start(self, localias, response_string=None, path=None, repeat=None,
              step=None, set_blocks=None, recategorize=None, pre_bug_step_id=None,
              set_review=None):
        """
        JOB ... oct 18, 2014 ... added bug_step_id to signature
        Issue the correct method for this interaction and return the result.
        This is the top-level interface for the Paideia module, to be called by
        the controller. The method decides whether we're starting a new step or
        responding to one in-process.
        """
        result = None
        try:
            while True:
                if response_string:
                    result = self.reply(localias=localias,
                                      response_string=response_string,
                                      pre_bug_step_id=pre_bug_step_id)
                if result: break
                result = self.ask(localias=localias,
                                path=path,
                                repeat=repeat,
                                set_blocks=set_blocks,
                                recategorize=recategorize,
                                step=step,
                                set_review=set_review)
                break
        except Exception:
            print traceback.format_exc(5)
            self.clean_user()  # get rid of any problem path data
            result = self.ask(localias=localias, path=path, step=step, set_review=set_review)
        if self.DEBUG_MODE:
            result['paideia_debug'] = '<div>' + current.paideia_debug.data + '</div>'
        else:
            #TODO: strip off html tags
            #print current.paideia_debug.data
            result['paideia_debug'] = ''
        return result

    def clean_user(self):
        """
        In case of irrecoverable conflict in user data, remove all path/steps.
        """
        user = self._get_user()
        user.path = None
        self._store_user(user)

    def ask(self, localias, path=None, repeat=None,
            step=None, set_blocks=None, recategorize=None, set_review=None):
        """
        Return the information necessary to initiate a step interaction.
        The "path" argument is used only for dependency injection during
        unit testing.
        In the returned dictionary, 'reply' item has the following dict as its
        value:
            'prompt':
            'instructions':
            'npc_image':
            'slides':
            'bg_image':
        The value of 'responder' is a web2py html helper object.
        The 'set_blocks' argument is used to set blocking conditions manually
            for testing purposes. It's value is a dictionary consisting of
                key: name of the blocking condition (str)
                value: dictionary of kwargs to be passed to the Block
        """
        debug = True
        p = category = redir = pastquota = None
        loc = prev_loc = prev_npc = None
        s = newloc_id = error_string = None
        prompt = None
        while True:
            user = self.user
            # allow artificial setting of blocks during interface testing
            if set_blocks:
                for c, v in set_blocks.iteritems():
                    myargs = {n: a for n, a in v.iteritems()}
                    current.sequence_counter += 1
                    user.set_block(c, kwargs=myargs)
            username = user.get_name()
            tag_progress, promoted, new_tags, demoted = self._set_blocks()
            if (promoted or new_tags or demoted):
                assert self._record_cats(tag_progress, promoted,
                                         new_tags, demoted)
            loc = Location(localias)
            prev_loc = user.set_location(loc)
            prev_npc = user.get_prev_npc()

            p, category, redir, pastquota, new_content = \
                user.get_path(loc, pathid=path,
                              repeat=repeat,
                              set_review=set_review)
            if repeat:
                user.repeating = True  # so that information available in reply
            if debug: print 'Walk::ask: path chosen is', p.get_id()
            if debug: print 'Walk::ask: redir is', redir

            if (not p): break  # no paths for this location for this category

            user.active_cat = category
            user.new_content = new_content
            if redir:
                current.sequence_counter += 1
                user.set_block('redirect', kwargs={'next_loc': redir})
            if pastquota:
                current.sequence_counter += 1
                user.set_block('quota_reached', kwargs={'quota': user.quota})
            if debug: print 'Walk::ask: user.path.steps num is', len(user.path.steps)

            s, newloc_id, error_string = p.get_step_for_prompt(loc, repeat=repeat)
            if debug: print 'Walk::ask: user.path.steps num is', len(user.path.steps)

            if newloc_id:
                current.sequence_counter += 1
                user.set_block('redirect', kwargs={'next_loc': newloc_id})

            # TODO: make sure 'new_tags' is returned before 'view_slides'
            current.sequence_counter += 1
            block = user.check_for_blocks()
            if block:
                s = block.get_step()

            npc = s.get_npc(loc, prev_npc, prev_loc)
            user.set_npc(npc)

            if not user.blocks:
                user.clear_block_records()
            prompt = s.get_prompt(loc, npc, username, user_blocks_left=True if user.blocks else False)

            if debug: print 'Walk::ask: user.path.steps num is', len(user.path.steps)
            extra_fields = {'completed_count': user.get_completed_paths_len(),
                            'category': category,
                            'pid': p.get_id(),
                            'new_content': new_content
                            }
            prompt.update(extra_fields)

            try:
                if debug: print 'Walk::ask: repeating?', user.repeating
            except AttributeError:
                if debug: print 'Walk::ask: user didn\'t have repeating attribute'
            p.end_prompt(s.get_id())  # send id to tell whether its a block step
            self._store_user(user)
            break  # from utility while loop

        # propagating errors and alerting user instead of crashing
        if(not p):  # no path in this location for this category
            prompt = {'sid': 0,
                      'prompt_text': "Please try another location for now",
                      'audio': None,
                      'widget_img': None,
                      'instructions': None,
                      'slidedecks': None,
                      'bg_image': None,
                      'loc': None,
                      'response_buttons': ['map'],
                      'response_form': None,
                      'npc_image': None,
                      'bugreporter': None,
                      'completed_count': user.get_completed_paths_len(),
                      'category': 0,
                      'pid': 0,
                      'new_content': new_content
                      }
            return prompt
        if(error_string):
            Exception_Bug({'log_id': 0,
                           'path_id': p.get_id(),
                           'step_id': s.get_id(),
                           'score':  0,
                           'answer': error_string,
                           'loc': user.loc.get_alias()})
            prompt = {'sid': s.get_id(),
                      'prompt_text': "Unexpected Error. A Bug Report with tag Philadelphia has been submitted",
                      'audio': None,
                      'widget_img': None,
                      'instructions': None,
                      'slidedecks': None,
                      'bg_image': None,
                      'loc': None,
                      'response_buttons': ['map'],
                      'response_form': None,
                      'npc_image': None,
                      'bugreporter': None,
                      'completed_count': 0,
                      'category': 0,
                      'pid': p.get_id(),
                      'new_content': new_content
                      }
            return prompt

        return prompt  # good prompt

    def _set_blocks(self, user=None):
        """
        """
        user = self.user if not user else user
        tag_progress, promoted, new_tags, demoted = user.get_categories(user_id=user.get_id())

        if new_tags:
            # setting order here should make new_tags step come up first
            user.set_block('new_tags', kwargs={'new_tags': new_tags,
                                               'promoted': promoted})
            user.set_block('view_slides', kwargs={'new_tags': new_tags})
        if promoted:
            user.set_block('new_tags', kwargs={'new_tags': new_tags,
                                               'promoted': promoted})
        return tag_progress, promoted, new_tags, demoted

    def reply(self, localias, response_string, path=None, step=None, pre_bug_step_id=None):
        """
        JOB ... oct 18, 2014, added bug_step_id to the signature
        Return the information necessary to complete a step interaction.
        This includes evaluation of the user's reply and presentation of
        the npc's response message.
        In the returned dictionary, the item 'reply' has as its value a
        dictionary with the following keys:
            'bg_image':
            'reply_text':
            'tips':
            'readable_short':
            'readable_long':
            'score':
            'times_right':
            'times_wrong':
            'user_response':
        """
        debug = True
        user = self._get_user()
        try:
            repeat = user.repeating
        except AttributeError:  # because user was initialized without attr
            repeat = False
        loc = user.get_location()
        p, cat = user.get_path(loc)[:2]
        if not cat:
            cat = user.active_cat
        if debug: print 'Walk::reply: category is', cat
        if debug: print 'Walk::reply: path is', p

        s = p.get_step_for_reply()
        if (not response_string) or re.match(response_string, r'\s+'):
            #return self.ask()  # TODO: will this actually re-prompt the same step?
            return None
        prompt = s.get_reply(response_string)  # loc and npc stored on step

        """ save inside get_categories ..  JOB ... oct 23, 2014
        assert self._record_cats(user.tag_progress,
                                 user.promoted,
                                 user.new_tags)
        """
        if repeat:
            user.repeating = False  # remove repeating flag now that step is over
            if debug: print 'Walk::reply: user is repeating, not recording step'
            self.record_id = None  # so there's a value to pass to the BugReporter
        else:
            if debug: print 'Walk::reply: cat being recorded is:', cat
            self.record_id = self._record_step(user.get_id(),
                                               s.get_id(),
                                               p.get_id(),
                                               prompt['score'],
                                               prompt['times_right'],
                                               prompt['times_wrong'],
                                               user.tag_records,
                                               s.get_tags(),
                                               response_string,
                                               cat,
                                               user.new_content)
        prompt['bugreporter'] = BugReporter().get_reporter(self.record_id,
                                                           p.get_id(),
                       pre_bug_step_id if pre_bug_step_id else s.get_id(),
                                                           prompt['score'],
                                                           response_string,
                                                           user.loc.get_alias())
        prompt['completed_count'] = user.get_completed_paths_len()
        prompt['pid'] = p.get_id()
        prompt['category'] = cat
        prompt['loc'] = loc.get_alias()
        prompt['new_content'] = user.new_content

        p.complete_step()  # removes path.step_for_reply; cf. (user.get_path)
        user._reset_for_walk()
        self._store_user(user)

        return prompt

    def _record_promotions(self, promoted, user_id):
        """
        Record awarding of new or promoted badges in db.badges_begun
        The 'promoted' argument is a dictionary with categories as keys and
        lists of tag id's as the values.
        Called by Walk._record_cats()

        """
        db = current.db
        now = datetime.datetime.utcnow()
        try:
            for cat, lst in promoted.iteritems():
                if lst:
                    for tag in lst:
                        data = {'name': user_id,
                                'tag': tag,
                                cat.replace('rev', 'cat'): now}
                        db.badges_begun.update_or_insert(
                                (db.badges_begun.name == user_id) &
                                (db.badges_begun.tag == tag), **data)
                        db.commit()
            return True
        except Exception:
            print traceback.format_exc(5)
            return False

    def _record_demotions(self, demoted, user_id):
        """
        Delete demoted badges from  db.badges_begun
        The 'demoted' argument is a dictionary with categories as keys and
        lists of tag id's as the values.
        Called by Walk._record_cats()
        JOB: added db.commit() after db.badges_begun.update_or_insert
        """
        return True

    def _record_cats(self, tag_progress, promoted, new_tags, demoted, db=None):
        """
        Record changes to the user's working tags and their categorization.
        Changes recorded in the following db tables:
        - badges_begun: new and promoted tags
        - tag_progress: changes to categorization (only if changes made)
        """
        db = current.db if not db else db
        auth = current.auth
        uid = self.user.get_id()
        if uid == auth.user_id:
            # TODO: make sure promoted and new_tags info passed on correctly

            if promoted:
                assert self._record_promotions(promoted, uid)
            if demoted:
                assert self._record_demotions(demoted, uid)
            if new_tags:
                assert self._record_promotions(new_tags, uid)
            try:
                tag_progress['name'] = uid
                condition = {'name': uid}

                db.tag_progress.update_or_insert(condition, **tag_progress)
                db.commit()
                mycount = db(db.tag_progress.name == uid).count()
                assert mycount == 1  # ensure there's never a duplicate
                # TODO: eliminate check by making name field unique
            except Exception:
                print traceback.format_exc(5)
                return False
            return True
        else:  # auth.user_id != uid because shadowing another user
            return False

    def _update_tag_secondary(self, tag, oldrec, user_id, now=None):
        """
        Update the 'secondary_right' field of a tag record.
        """
        mynow = datetime.datetime.utcnow() if not now else now
        db = current.db
        sec_right = [mynow]  # default
        if oldrec:
            oldrec = oldrec[0] if isinstance(oldrec, list) else oldrec  # FIXME
            sec_right = oldrec['secondary_right']
            try:
                sec_right.append(mynow)
            except AttributeError:  # because secondary_right is None
                sec_right = [mynow]  # default
        condition = {'tag': tag, 'name': user_id}
        tagrec = db.tag_records.update_or_insert(condition,
                                                 tag=tag,
                                                 secondary_right=sec_right)
        db.commit()
        return tagrec

    def _add_from_logs(self, tag, user_id, newdata, tright, twrong, got_right):
        """
        Temporary fix for lost tag records counts.
        """
        db = current.db
        tagsteps = [s['id'] for s
                    in db(db.steps.tags.contains(tag)).select().as_list()]
        logs = db((db.attempt_log.name == user_id) &
                  (db.attempt_log.step.belongs(tagsteps))
                  ).select().as_list()
        if logs:
            wronglogs = [l for l in logs if abs(l['score'] - 1) > 0.001]
            if len(wronglogs) != newdata['times_wrong']:
                newdata['times_wrong'] = len(wronglogs) + twrong
            if got_right:
                try:
                    wrongmax = max([l['dt_attempted'] for l in wronglogs])
                    newdata['tlast_wrong'] = wrongmax
                except ValueError:  # can't max() an empty list
                    pass

            rightlogs = [l for l in logs if abs(l['score'] - 1) <= 0.001]
            if len(rightlogs) != newdata['times_right']:
                newdata['times_right'] = len(rightlogs) + tright
            if not got_right:
                try:
                    rightmax = max([l['dt_attempted'] for l in rightlogs])
                    newdata['tlast_right'] = rightmax
                except ValueError:  # can't max() an empty list
                    pass
        return newdata

    def _update_tag_record(self, tag, oldrec, user_id, tright, twrong,
                           got_right, score, step_id=None, now=None):
        """
        Update the tag_records row for the selected tag for this attempt's.

        Creates a new tag_records entry if there is none already for the
        selected tag. Returns the id of the row that is updated/created.

        *Old approach by JOB* -------------------------------------------
        SQL_TEMPLATE_UPDATE_TAG_RECORDS = "\
                                          UPDATE tag_records \
                                          SET    %s = coalesce(%s,0) + %f \
                                              ,%s = '%s' \
                                          ,step = %d \
                                          WHERE  name = %d \
                                          AND    tag =  %d; "

        sql_string = None
        if got_right:
            sql_string = SQL_TEMPLATE_UPDATE_TAG_RECORDS % ('times_right',
                                'times_right', newdata['times_right'],
                                'tlast_right', newdata['tlast_right'],
                                newdata['step'], user_id, tag)
        else:
            sql_string = SQL_TEMPLATE_UPDATE_TAG_RECORDS % ('times_wrong',
                                'times_wrong', newdata['times_wrong'],
                                'tlast_wrong', newdata['tlast_wrong'],
                                newdata['step'], user_id, tag)
        rslt = db.executesql(sql_string)
        """

        now = datetime.datetime.utcnow() if not now else now
        oldrec = oldrec if not isinstance(oldrec, list) else oldrec[0]  # FIXME
        db = current.db

        # FIXME: oldrec not showing up here sometimes?
        if not oldrec:
            try:
                oldrec = db((db.tag_records.tag == tag) &
                            (db.tag_records.name == user_id)
                            ).select().first().as_dict()
            except:
                #print traceback.format_exc()
                oldrec = None

        newdata = {'times_right': tright,
                   'times_wrong': twrong,
                   'tlast_right': now,
                   'tlast_wrong': now,
                   'step': step_id,
                   'tag': tag,
                   'name': user_id}

        if oldrec:
            newdata['times_right'] = tright + oldrec['times_right'] \
                if oldrec['times_right'] else tright
            newdata['times_wrong'] = twrong + oldrec['times_wrong'] \
                if oldrec['times_wrong'] else twrong
            if got_right:
                newdata['tlast_wrong'] = oldrec['tlast_wrong']
            else:
                newdata['tlast_right'] = oldrec['tlast_right']

        # write updates to db here
        condition = {'name': user_id, 'tag': tag}
        myrec = db.tag_records.update_or_insert(condition, **newdata)
        db.commit()

        # double check insertion/update
        tagrecs = db((db.tag_records.tag == tag) &
                     (db.tag_records.name == user_id)).select()
        assert len(tagrecs) == 1
        tagrec = tagrecs.first()

        return tagrec.id

    def _record_step(self, user_id, step_id, path_id, score, raw_tright,
                     raw_twrong, old_trecs, taglist, response_string, category,
                     new_content, now=None):
        """
        Record this step attempt and its impact on user's performance record.
        Changes recorded in the following db tables:
        - attempt_log: log this attempt
        - tag_records: changes to
                            - times_right
                            - times_wrong
                            - tlast_wrong
                            - tlast_right
                            - secondary_right (add datetime to list)
        TODO: if secondary_right is sufficient length, delete it and
                - add 1 to times_right
                - set tlast_right to now
            but best done along the way, when first updating tag_records
        TODO: be sure not to log redirect and utility steps. (filter them out
        before calling _record_step())
        """
        debug = True
        mynow = datetime.datetime.utcnow() if not now else now
        db = current.db
        # TODO: Store and roll back db changes if impersonating
        # TODO: should the threshold here be less than 1 for 'right'?
        # made change JOB ... got_right seems to be sending the opposite of
        # what it should be -sept 21 2014
        # fix: if it is make it slightly higher and change the comparison
        # sign
        if debug: print 'Walk::_record_step: category is', category
        score_helper = score + 0.1
        got_right = True if ((score_helper - 1.0) > 0.00000001) else False  # float inaccuracy

        for t in taglist['primary']:
            oldrec = [r for r in old_trecs
                      if r['tag'] == t] if old_trecs else None
            if not oldrec:  # because list empty
                oldrec = None
            self._update_tag_record(t, oldrec, user_id, raw_tright, raw_twrong,
                                    got_right, score, step_id, now=mynow)
        if got_right and ('secondary' in taglist.keys()):
            for t in taglist['secondary']:
                oldrec = [r for r in old_trecs
                          if r['tag'] == t] if old_trecs else None
                if not oldrec:  # because list empty
                    oldrec = None
                self._update_tag_secondary(t, oldrec, user_id, now=mynow)

        log_args = {'name': user_id,
                    'step': step_id,
                    'in_path': path_id,
                    'score': score,
                    'user_response': makeutf8(response_string),
                    'selection_category': category,
                    'new_content': 'yes' if new_content else 'no'}  # time automatic in db
        #print 'log args ===================================='
        #print type(log_args['user_response'])
        #print log_args['user_response']  # FIXME: caused unicode error on live
        log_record_id = db.attempt_log.insert(**log_args)
        db.commit()
        self.user.complete_path(got_right)
        return log_record_id

    def _store_user(self, user, db=None):
        """
        Store the current User object (from self.user) in session.user
        If successful, returns an integer representing the successfully
        added/updated db row. If unsuccessful, returns False.
        """
        db = current.db if not db else db

        try:
            myuser = pickle.dumps(user)
            condition = {'name': user.get_id()}
            rownum = db.session_data.update_or_insert(condition,
                                                      name=user.get_id(),
                                                      other_data=myuser)
            db.commit()
            return rownum
        except Exception:
            print traceback.format_exc(5)
            #try:
            #    #with open('tempfile.txt', 'wb') as tempfile:
            #        #myuser = MyPickler(tempfile).dump(user)
            #        #os.remove('tempfile.txt')
            #except Exception:
            #    #print traceback.format_exc(5)
            #    #return False
            return False


class Location(object):
    """
    Represents a location in the game world.
    """

    def __init__(self, alias, db=None):
        """Initialize a Location object."""
        db = current.db if not db else db
        self.data = db(db.locations.loc_alias == alias).select().first().as_dict()

    def __str__(self):
        """Return string to represent a Location instance"""
        strout = 'Paideia Location Object -----------------------\n{}'
        mydata = self.data
        strout.format(mydata)
        return strout

    def get_alias(self):
        """Return the alias of the current Location as a string."""
        return self.data['loc_alias']

    def get_name(self):
        """Return the name of the current Location as a string.
        This 'name' is used in the svg map to identify the location."""
        return self.data['map_location']

    def get_readable(self):
        """
        Return the readable name of the current Location as a string.
        This is used to identify the location in communication with the user.
        """
        return self.data['readable']

    def get_bg(self):
        """Return the background image of the current Location as a web2py
        IMG helper object."""
        db = current.db
        try:
            bg = URL('static/images', db.images[self.data['bg_image']].image)
        except Exception:
            print traceback.format_exc(5)
            bg = SPAN('no image in db for location {}'.format(self.data['id']))
        return bg

    def get_id(self):
        """
        Return the id for the database row representing the current
        Location (as an int).
        """
        return self.data['id']


class Npc(object):
    '''
    Represents one non-player character in the game
    '''

    def __init__(self, id_num, db=None):
        """
        initialize an npc object with database data for the character
        with the provided id
        """
        db = current.db if not db else db
        # FIXME: this is a hack to handle being passed npc obj somewhere
        if isinstance(id_num, Npc):
            self.id_num = id_num.get_id()
        else:
            self.id_num = id_num
        self.data = db.npcs(id_num).as_dict()
        # get image here so that db interaction stays in __init__ method
        self.image_id = self.data['npc_image']
        self.image = db.images[self.image_id].image

    def __str__(self):
        """Return string to represent a Location instance"""
        strout = ['Paideia Npc Object ------------------------\n'
                  'id_num: {id_num}\n'
                  'image_id: {image_id}\n'
                  'image: {image}\n'
                  'data:\n{data}\n']
        return strout[0].format(id_num=self.id_num,
                                image_id=self.image_id,
                                image=self.image,
                                data=self.data)

    def get_id(self):
        """return the database row id of the current npc"""
        return self.id_num

    def get_name(self):
        """return the name of the current npc"""
        return self.data['name']

    def get_image(self, db=None):
        """
        Return a web2py IMG helper object with the image for the current
        npc character.
        """
        img = IMG(_src=URL('paideia', 'static', 'images/{}'.format(self.image)))
        return img

    def get_locations(self):
        """
        Npc.get_locations
        Return a list of ids (ints) for locations where this step can activate.
        """
        db = current.db
        locs = [l for l in self.data['map_location']
                if db.locations[l].loc_active is True]
        return locs

    def set_location(self, loc, prev_loc):
        """
        """
        self.loc = loc
        self.prev_loc = prev_loc
        return True

    def get_description(self):
        """docstring for Npc.get_description"""
        return self.data['notes']


class NpcChooser(object):
    """
    Choose an npc to engage the user in the current step, based on the current
    location and the parameters of the step itself.
    """
    def __init__(self, step, location, prev_npc, prev_loc):
        """
        Initialize an NpcChooser object.
        step: Step
        location: Location
        prev_npc: Npc
        prev_loc: Location
        """
        self.step = step
        self.location = location
        self.prev_npc = prev_npc
        self.prev_loc = prev_loc

    def choose(self):
        """
        Choose an npc for the selected step.
        If possible, continue with the same npc. Otherwise, select a different
        one that can engage in the selected step.
        """
        available = self.step.get_npcs()

        if ((self.location.get_readable() == self.prev_loc.get_readable()) and
                (self.prev_npc.get_id() in available)):
            return self.prev_npc
        else:
            # TODO: is the list below right???
            available2 = [n for n in available
                          if n == self.prev_npc.get_id() and
                          self.location.get_id() in n.get_locations()]
            if len(available2) > 1:
                return Npc(available2[randint(0, len(available2) - 1)])
            else:
                return Npc(available2[0])

            return False


class BugReporter(object):
    """
    Class representing a bug-reporting widget to be presented along with the
    evaluation of the current step.
    """
    def __init__(self):
        """Initialize a BugReporter object"""
        pass

    def get_reporter(self, record_id, path_id, step_id,
                     score, response_string, loc_id):
        """
        Return a link to trigger submission of a bug report for current step.
        Returns a web2py A() html helper object, ready for embedding in a
        web2py view template. This is meant to be embedded in the reply UI
        which presents the user with an evaluation of the step input.
        """
        debug = False

        response_string = response_string.decode('utf-8')
        response_string = response_string.encode('utf-8')

        vardict = {'answer': response_string,
                   'loc_id': loc_id,
                   'log_id': record_id,
                   'path_id': path_id,
                   'score': score,
                   'bug_step_id': step_id}
        if debug: print 'BugReporter::get_reporter: vardict is \n', pprint(vardict)

        return vardict


class StepFactory(object):
    """
    A factory class allowing automatic generation of correct Step subclasses.
    This allows easy changing/extension of Step classes without having to
    make changes to other application code. At present the decision is made
    based on the "widget_type" field supplied in db.steps. But there is not a
    1:1 relationship between widget type and Step subclass.
    """
    def get_instance(self, step_id, repeating=None, kwargs=None, db=None):
        """
        Return the correct subclass of Step based on record's 'widget_type'.
        The ids correspond to the following 'widget_type' labels:
        1. test response
        2. multiple choice (single option)
        3. stub
        4. image - text response DEPRECATED
        5. image - multichoice DEPRECATED
        6. send to view slides
        7. daily quota reached
        8. award badges
        9. redirect
        """
        db = current.db if not db else db
        mystep = db.steps[step_id]
        step_classes = {1: StepText,
                        2: StepMultiple,
                        3: Step,
                        4: StepText,
                        5: StepMultiple,
                        6: StepViewSlides,
                        7: StepQuotaReached,
                        8: StepAwardBadges,
                        9: StepRedirect}
        return step_classes[mystep['widget_type']](step_id,
                                                   repeating=repeating,
                                                   kwargs=kwargs,
                                                   stepdata=mystep.as_dict())


class Step(object):
    '''
    This class represents one step (a single question and response
    interaction) in the game.
    '''

    def __init__(self, step_id, repeating=False, kwargs=None, stepdata=None):
        """Initialize a paideia.Step object"""
        db = current.db
        self.data = db.steps[step_id].as_dict() if not stepdata else stepdata
        self.repeating = False  # set to true if step already done today
        self.npc = None  # must wait since all steps in path init at once
        self.redirect_loc_id = None  # TODO: is this used?
        self.kwargs = kwargs
        #JOB ...Nov 10,2014
        self.cat_tag = None

    def get_id(self):
        """
        Return the id of the current step as an integer.
        """
        return self.data['id']

    def get_npcs(self):
        """
        Return the ids of the npcs available for current step as a list.
        """
        return self.data['npcs']

    def get_tags(self):
        """
        Return a dictionary of tag id's associated with the current Step.
        Keys for the dictionary are 'primary' and 'secondary'. Values are lists
        of integers (db.tags row id's).
        """
        primary = self.data['tags']
        secondary = self.data['tags_secondary']
        return {'primary': primary, 'secondary': secondary}

    def get_locations(self):
        """
        Step.get_locations
        Return a list of the location id's for this step.

        Filters out locations which are not currently set as active.

        """
        db = current.db
        if self.data['locations']:
            locs = [l for l in self.data['locations']
                    if db.locations[l].loc_active is True]
        else:
            locs = None
            stepid = self.get_id()
            xtra_msg = 'Step {} has no assigned locations'.format(self.get_id())
            # FIXME: turning off to silence email spam during testing
            ErrorReport().send_report('Step', 'get_locations',
                                      subtitle='no locations for step',
                                      xtra=xtra_msg)
        return locs

    def is_valid(self):
        """
        Step.is_valid
        Returns true step has data
        """
        if self.data: return True
        return False

    def has_locations(self):
        """
        Step.has_locations
        Returns true if any of the location id's for this step is active.
        """
        rslt = False
        while True:
            if not self.is_valid:
                break
            if self.get_locations():
                rslt = True
                break
            break
        return rslt

    def _get_slides(self):
        """
        Return a dictionary of info on slide decks relevant to this step.
        The keys are deck ids, while the values are the deck names (as
        strings). If this step has no associated slides, returns None.
        """
        debug = False
        db = current.db
        tags = db(db.tags.id.belongs(self.data['tags'])).select()
        if debug: print 'Step::_get_slides: tags', [t['id'] for t in tags]
        if tags:
            if debug: print 'got some tags'
            try:
                decks = {d.id: d.deck_name
                        for t in tags
                        for d in t.slides
                        if t.slides}
                if debug: print 'decks:', decks
                return decks
            except Exception as e:
                print e
                print 'failed to return decks'
                pass
        else:
            return None

    def _get_widget_image(self):
        """
        Return a dictionary of information on the widget image for the step.
        If this step requires no such image, return None
        """
        if not self.data['widget_image'] in [9, None]:  # TODO: magic number here:
            db = current.db
            img_row = db.images[self.data['widget_image']]
            img = {'file': img_row.image,
                   'title': img_row.title,
                   'description': img_row.description}
            return img
        else:
            return None

    def _get_prompt_audio(self):
        """
        Return a dictionary of information on the audio clip for this step.

        If this step requires no such audio, return None
        """
        if not self.data['prompt_audio'] in [0, 1, None]:  # TODO: magic number
            while True:
                db = current.db
                aud_row = db.audio(self.data['prompt_audio'])
                if not aud_row['clip_m4a']: break
                audio = {'title': aud_row['title'],
                         'mp3': aud_row['clip'],
                         'ogg': aud_row['clip_ogg'] if aud_row['clip_ogg'] else None}
                audio_args_for_js = {'title': ''}
                media_supplied = ""
                if aud_row['clip_m4a']:
                    audio_args_for_js['m4a'] = "/paideia/default/download.load/" + aud_row['clip_m4a']
                    media_supplied = "m4a"
                """
                only doing m4a for now
                if aud_row['clip']:
                    audio_args_for_js['mp3'] = "/paideia/default/download.load/" + aud_row['clip']
                    if media_supplied: media_supplied += ",mp3"
                    else:media_supplied = "mp3"
                if aud_row['clip_ogg']:
                    audio_args_for_js['ogg'] = "/paideia/default/download.load/" + aud_row['clip_ogg']
                    if media_supplied: media_supplied += ",ogg"
                    else:media_supplied = "ogg"
                """
                audio['audio_args_for_js'] = str(audio_args_for_js)
                audio['media_supplied'] = media_supplied
                return audio
        else:
            return None

    def get_prompt(self, location, npc, username, raw_prompt=None, user_blocks_left=False):
        """
        Return the prompt information for the step. In the Step base class
        this is a simple string. Before returning, though, any necessary
        replacements or randomizations are made.
        If the step cannot be performed in this location, this method returns
        the string 'redirect' so that the Walk.ask() method that called it can
        set a redirect block.
        Extra data for block steps is passed via the 'kwargs' instance
        variable which in turn comes (via StepFactory) from the 'kwargs'
        argument at Block instantiation (called in turn by user.set_block).
        Since user.set_block is ONLY called in Walk.ask(), these values are
        always set in that top-level method.
        """
        #debug ... DONT FORGET TO TURN back on
        raw_prompt = self.data['prompt'] if not raw_prompt else raw_prompt
        #debug

        #raw_prompt = (self.data['prompt']  +  str(self.data['id']) + self.data['readable_response'])  if not raw_prompt else raw_prompt
        prompt_text_dict = self._make_replacements(raw_prompt, username)
        prompt = {'sid': self.get_id(),
                  'prompt_text': prompt_text_dict['newstr'] if ('newstr' in prompt_text_dict) else '',
                  'audio': self._get_prompt_audio(),
                  'widget_img': self._get_widget_image(),
                  'instructions': self._get_instructions(),
                  'slidedecks': self._get_slides(),
                  'bg_image': location.get_bg(),
                  'loc': location.get_alias(),
                  'response_buttons': ['map'],
                  'response_form': None,
                  'bugreporter': None,
                  'pre_bug_step_id': self.get_id()}
        # TODO: this is a temporary hack for bad data
        self.npc = npc if not isinstance(npc, tuple) else npc[0]
        prompt['npc_image'] = self.npc.get_image()

        return prompt

    def _make_replacements(self, raw_prompt, username, reps=None, appds=None):
        """
        Return the provided string with tokens replaced by personalized
        information for the current user.
        """
        if not reps:
            reps = {}
            reps['[[user]]'] = username
        newstr = raw_prompt
        # FIXME: this is a bit of a hack to handle embedded html better
        if appds:
            #new_string = DIV(new_string)
            #for k, v in appds.iteritems():
                #if not v:
                    #v = ''
                #new_string[0] = new_string[0].replace(k, '')
                #new_string.append(v)
            for k, v in appds.iteritems():
                if v:
                    newstr = newstr.replace(k, v)
                else:
                    newstr = newstr.replace(k, '')
                    #new_string += v
        for k, v in reps.iteritems():
            if not v:
                v = ''
            newstr = newstr.replace(k, v)

        return {'newstr': newstr}

    def get_npc(self, loc, prev_npc=None, prev_loc=None):
        """
        Return an Npc object appropriate for this step
        If there is no suitable npc available here, returns a tuple containing
            - the id of another suitable location [0]
            - the id of an npc at this location who will deliver a redirect
              message [1]
        If possible, the redirect message will be given by the same npc as in
        the last step.
        Because the redirect block must be set on the Path object, to which
        the Step has no access, the actual block is set by the Walk object
        after this method's value is returned.
        This method is also where all checking is done for compatibility between
        the chosen step, location, and npc.
        """
        loc_id = loc.get_id()
        db = current.db
        npc_list = self.get_npcs()

        if self.npc:  # keep pre-chosen npc
            if isinstance(self.npc, tuple):
                self.npc = self.npc[0]
            else:
                pass
        else:
            if prev_npc and (prev_loc.get_id() == loc_id) \
                    and (prev_npc.get_id() in npc_list):
                # previous npc was in this loc and is valid for this step
                self.npc = copy(prev_npc)
            else:
                npc_here_list = [n for n in npc_list if loc_id in db.npcs[n]['map_location']]

                try:
                    pick = npc_here_list[randrange(len(npc_here_list))]
                except ValueError:  # "empty range for randrange()" if no npcs here
                    #current.paideia_debug.do_print("randrange error permitted",
                    #                               'Step.get_npc')
                    mail = current.mail
                    msg = HTML(P('In selecting an npc there were none found for'
                                 'the combination:',
                                 UL(LI('step =', self.get_id()),
                                    LI('location =', loc_id)),
                                 'The full list of npcs for the step is',
                                 self.get_npcs()
                                 )
                               )
                    mail.send(mail.settings.sender,
                              'No valid npc was available',
                              msg.xml())
                    try:
                        pick = npc_list[randrange(len(npc_list))]
                    except ValueError:
                        current.paideia_debug.do_print("randrange error NOT "
                                                       "permitted",
                                                       'Step.get_npc')
                        print traceback.format_exc(5)
                assert pick
                self.npc = Npc(pick)
        return self.npc

    def _get_instructions(self):
        """
        Return a list of relevant step instructions as strings.
        If no instructions available, return None.
        """
        db = current.db
        if self.data['instructions']:
            instructions = [db.step_instructions[i].instruction_text
                            for i in self.data['instructions']]
            return instructions
        else:
            return None

    def __str__(self):
        """
        print a step object
        """
        strout = 'Paideia Step object -----------\n{}'
        info = {'Class': 'Step',
                'data': str(self.data),
                'repeating': self.repeating,
                'npc': self.npc,
                'redirect_loc_id': self.redirect_loc_id,
                'kwargs': str(self.kwargs),
                'cat_tag': self.cat_tag}
        return strout.format(str(info))


class StepContinue(Step):
    """
    An abstract subclass of Step that adds a 'continue' button to the responder.
    """
    def get_prompt(self, loc, npc, username, raw_prompt=None,
                   user_blocks_left=True):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        prompt = super(StepContinue, self).get_prompt(loc, npc, username)
        prompt['response_buttons'] = ['map', 'continue']
        return prompt


class StepRedirect(Step):
    '''
    A subclass of Step. Handles the user interaction when the user needs to be
    sent to another location.
    This class works best if either the 'next_step_id' (int) or the 'next_loc'
    (int) are supplied. In that case the prompt will direct the user to a
    specific location. Otherwise, the user receives a generic instruction to
    try "another location in town".
    '''
    def get_prompt(self, loc, npc, username, raw_prompt=None,
                   user_blocks_left=True):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        prompt = super(StepRedirect, self).get_prompt(loc, npc, username)
        if user_blocks_left:
            prompt['response_buttons'] = ['map', 'continue']
        else:
            prompt['response_buttons'] = ['map']
        return prompt

    def _make_replacements(self, raw_prompt, username):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        db = current.db
        kw = self.kwargs
        next_loc = kw['next_loc'] if (kw and 'next_loc' in kw) else None
        if next_loc:
            next_loc_name = db.locations[next_loc]['readable']
        else:
            next_loc_name = "somewhere else in town"
        reps = {'[[next_loc]]': next_loc_name}
        newstr = (super(StepRedirect, self)._make_replacements(raw_prompt,
                                                                  username,
                                                                  reps=reps))['newstr']
        return {'newstr': newstr}


class StepQuotaReached(StepContinue, Step):
    '''
    A Step that tells the user s/he has completed the daily minimum # of steps.
    '''
    def _make_replacements(self, raw_prompt, username):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        #  if self.kwargs:
        #  quota = self.kwargs['quota']  #  TODO: actually put value in prompt
        reps = None
        newstr = (super(StepQuotaReached, self)._make_replacements(raw_prompt,
                                                                  username,
                                                                  reps=reps))['newstr']
        return {'newstr': newstr}


class StepAwardBadges(StepContinue, Step):
    '''
    A Step that informs the user when s/he has earned new badges.
    '''

    def _make_replacements(self, raw_prompt, username):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        db = current.db
        appds = {}
        reps = {}
        kw = self.kwargs

        new_tags = kw['new_tags'] if ('new_tags' in kw.keys() and
                                      kw['new_tags']) else None
        promoted = kw['promoted'] if ('promoted' in kw.keys() and
                                      kw['promoted']) else None

        conj = " and you're" if promoted else "You are"
        nt_rep = ''
        if new_tags:
            flat_nts = [i for cat, lst in new_tags.iteritems() for i in lst if lst]
            nt_records = db(db.badges.tag.belongs(flat_nts)
                            ).select(db.badges.tag,
                                     db.badges.badge_name).as_list()
            if nt_records:
                nt_rep = '{} ready to start working on some new ' \
                         'badges:\r\n'.format(conj)
                ranks = ['beginner', 'apprentice', 'journeyman', 'master']
                nt_clean = {k: v for k, v in new_tags.iteritems() if v}
                for rank, lst in nt_clean.iteritems():
                    ranknum = int(rank.replace('rev', ''))
                    label = ranks[ranknum - 1]
                    for l in lst:
                        bname = [row['badge_name'] for row in nt_records
                                if row['tag'] == l]
                        if bname: bname = bname[0]
                        else: bname = 'tag {}(no name)'.format(l)
                        line = '- {} {}\r\n'.format(label, bname)
                        nt_rep += line
        nt_rep += 'You can click on your name above to see details ' \
                  'of your progress so far.'
        appds['[[new_tag_list]]'] = nt_rep

        prom_rep = ' '
        if promoted:
            flat_proms = [i for cat, lst in promoted.iteritems() for i in lst if lst]
            prom_records = db(db.badges.tag.belongs(flat_proms)
                              ).select(db.badges.tag,
                                       db.badges.badge_name).as_list()
            if prom_records:
                prom_rep = 'You have been promoted to these new badge levels:\r\n'
                ranks = ['beginner', 'apprentice', 'journeyman', 'master']
                prom_clean = {k: v for k, v in promoted.iteritems() if v}
                for rank, lst in prom_clean.iteritems():
                    # FIXME: why is this sometimes getting 'cat' instead of
                    # 'rev'?  Apr 28, 2015
                    try:
                        ranknum = int(rank.replace('rev', ''))
                    except ValueError:  # because getting 'cat' instead of 'rev'
                        ranknum = int(rank.replace('cat', ''))
                    # end of hack ------------------------------------------
                    label = ranks[ranknum - 1]
                    for l in lst:
                        bname = [row['badge_name'] for row in prom_records
                                if row['tag'] == l]
                        if bname: bname = bname[0]
                        else: bname = 'tag {}(no name)'.format(l)
                        line = '- {} {}\r\n'.format(label, bname)
                        prom_rep += line
        appds['[[promoted_list]]'] = prom_rep

        newstr = (super(StepAwardBadges, self
                        )._make_replacements(raw_prompt, username,
                                             reps=reps, appds=appds))['newstr']
        return {'newstr': newstr,
                'promoted': True if promoted else False,
                'new_tags': True if new_tags else False
                }


class StepViewSlides(Step):
    '''
    A Step that informs the user when s/he needs to view more grammar slides.
    '''

    def _make_replacements(self, raw_prompt, username):
        """
        TODO:brasil-look here to solve the slides problem ... JOB nov 2, 2014
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        new_tags value should be a list of tag id's as integers
        """
        db = current.db
        new_tags = self.kwargs['new_tags']
        flat_nts = [i for cat, lst in new_tags.iteritems() for i in lst if lst]
        tags = db((db.tags.id == db.badges.tag) &
                (db.tags.id.belongs(flat_nts))).select().as_list()

        # get the relevant slide sets (id and name)
        decks = [row['tags']['slides'] for row in tags]
        if isinstance(decks[0], list):
            # anticipating possibility that decks could match multiple tags
            decks = [i for lst in decks for i in lst]
        decks = list(set(decks))

        dtable = db.plugin_slider_decks
        sliderows = db(dtable.id.belongs(decks)
                       ).select(dtable.id,
                                dtable.deck_name,
                                orderby=dtable.deck_position)

        # build slide deck list
        slides = []
        for row in sliderows:
            baseurl = 'http://ianwscott.webfactional.com/paideia/listing/slides.html/'
            deckurl = baseurl + str(int(row['id']))
            slides.append('- [{} {}]'.format(row['deck_name'], deckurl))
        slides = '\n'.join(slides)

        # collect replacements
        appds = {'[[slide_list]]': slides}
        newstr = (super(StepViewSlides, self
                        )._make_replacements(raw_prompt, username,
                                             appds=appds))['newstr']
        return {'newstr': newstr}


class StepText(Step):
    """
    A subclass of Step that adds a form to receive user input and evaluation of
    that input. Handles only a single string response.
    """

    def get_prompt(self, location, npc, username, raw_prompt=None,
                   user_blocks_left=True):
        """x"""
        prompt = super(StepText, self).get_prompt(location, npc, username)
        prompt['response_form'] = self._get_response_form()
        prompt['response_buttons'] = []
        return prompt

    def _get_response_form(self):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        # TODO: needs test
        #JOB ... added step id for bug tracing ... oct 18, 2014
        form = SQLFORM.factory(Field('response', 'string',
                                     requires=IS_NOT_EMPTY()),
                               #Field('pre_bug_step_id', 'string'),
                               Field('pre_bug_step_id', 'string', readable=False, writable=False),
                               hidden=dict(pre_bug_step_id=self.get_id()),
                               _autocomplete='off')
        return form

    def get_reply(self, user_response=None):
        """
        Evaluate a user's response and return the resulting data and reply.
        """
        loc = self.loc
        npc = self.npc
        db = current.db
        readable = self._get_readable()
        tips = self.data['hints']
        responses = {k: v for k, v in self.data.iteritems()
                     if k and (k in ['response1', 'response2', 'response3'])}
        #  except TypeError:
        #  tips = self.data['step'].data['hints']
        #  responses = {k: v for k, v in self.data['step'].data.iteritems() if k and (k in rkeys)}

        if tips:
            tips_lst = db(db.step_hints.id.belongs(tips)
                          ).select(db.step_hints.hint_text).as_list()
            tips_lst = [v for t in tips_lst for k, v in t.iteritems()]
        else:
            tips_lst = None

        result = StepEvaluator(responses, tips_lst).get_eval(user_response)

        reply_text = '{}\nYou said\n- {}'.format(result['reply'], user_response)
        if len(readable['readable_short']) > 1:
            reply_text += '\nCorrect responses would include'
            for r in readable['readable_short']:
                reply_text += '\n- {}'.format(r)
        elif abs(result['score'] - 1) > 0.001:
            reply_text += '\nThe correct response ' \
                          'is\n- {}'.format(readable['readable_short'][0])

        reply = {'sid': self.get_id(),
                 'bg_image': loc.get_bg(),
                 'prompt_text': reply_text,
                 'readable_long': readable['readable_long'],
                 'npc_image': npc.get_image(),
                 'audio': None,


                 'widget_img': None,
                 'instructions': self._get_instructions(),
                 'slidedecks': self._get_slides(),
                 'hints': tips_lst,
                 'response_buttons': ['map', 'retry', 'continue'],
                 # below are for internal use in Walk.reply(), not for display
                 'score': result['score'],
                 'times_right': result['times_right'],
                 'times_wrong': result['times_wrong'],
                 'user_response': result['user_response']}
        return reply

    def _get_readable(self):
        """
        Return two strings containing the shorter and the longer forms of the
        readable correct answer samples for this step.
        """
        try:
            readable = self.data['readable_response']
        except TypeError:
            readable = self.data['step'].data['readable_response']

        rsplit = readable.split('|')
        readable_short = rsplit[:3]
        readable_long = rsplit[3:]  # [] will fail "if readable_long:" check

        return {'readable_short': readable_short,
                'readable_long': readable_long}


class StepMultiple(StepText):
    """
    A subclass of Step that adds a form to receive multiple-choice user input
    and evaluation of that input.
    """

    def _get_response_form(self):
        """Return an html form for responding to the current prompt."""
        request = current.request
        session = current.session
        vals = self.data['step_options']
        form = SQLFORM.factory(Field('response', 'string',
                                     requires=IS_IN_SET(v for v in vals),
                                     widget=SQLFORM.widgets.radio.widget))
        if form.process().accepted:
            session.response = request.vars.response
        return form


class StepEvaluator(object):
    '''
    This class evaluates the user's response to a single step interaction and
    handles the data that results.
    '''
    def __init__(self, responses, tips):
        """Initializes a StepEvaluator object"""
        self.responses = responses
        self.tips = tips

    def get_eval(self, user_response=None):
        """
        Return the user's score for this step attempt along with "tips" text
        to be displayed to the user in case of a wrong answer.
        Allowance is made for multiple internal spaces, leading or trailing
        spaces, and for identical-looking Lating characters being used in place
        of their Greek counterparts.
        Special responses (and a score of 0.9) are also given if the only error
        is the presence or absence of appropriate final punctuation.
        """
        if not user_response:
            request = current.request
            user_response = request.vars['response']
        clean_user_response = GreekNormalizer().normalize(user_response)
        #print 'in get_eval user_response is', type(user_response)
        clean_user_response = makeutf8(clean_user_response)
        responses = {k: r for k, r in self.responses.iteritems()
                     if r and r != 'null'}
        # Compare the student's response to the regular expressions
        times_wrong = 1
        times_right = 0
        score = 0

        try:
            regex1 = re.compile(makeutf8(responses['response1']), re.I | re.U)
            if 'response2' in responses.keys():
                regex2 = re.compile(makeutf8(responses['response2']), re.I | re.U)
            else:
                regex2 = None
            if 'response3' in responses.keys():
                regex3 = re.compile(makeutf8(responses['response3']), re.I | re.U)
            else:
                regex3 = None

            if re.match(regex1, makeutf8(clean_user_response)):
                score = 1
                reply = "Right. Κάλον."
            elif re.match(regex1, makeutf8(clean_user_response + '.')):
                score = 0.9
                reply = "Οὐ Κάκον. You're very close. Just remember to put a " \
                        "period on the end of a full clause."
            elif re.match(regex1, makeutf8(clean_user_response + '?')):
                score = 0.9
                reply = "Οὐ Κάκον. You're very close. Just remember to put a " \
                        "question mark on the end of a question."
            elif re.match(regex1, makeutf8(clean_user_response + ';')):
                score = 0.9
                reply = "Οὐ Κάκον. You're very close. Just remember to put a " \
                        "question mark on the end of a question."
            elif user_response[-1] in ['.', ',', '!', '?', ';'] and \
                    re.match(regex1, makeutf8(clean_user_response[:-1])):
                score = 0.9
                reply = "Ού κάκον. You're very close. Just remember not to put " \
                        "a final punctuation mark on your answer if it's not a " \
                        "complete clause"
            elif 'response2' in responses.keys() and \
                    re.match(regex2, makeutf8(clean_user_response)):
                score = 0.5
                #  TODO: Get this score value from the db instead of hard
                #  coding it here.
                reply = "Οὐ κάκον. You're close."
                #  TODO: Vary the replies

            elif 'response3' in responses.keys() and \
                    re.match(regex3, makeutf8(clean_user_response)):
                #  TODO: Get this score value from the db instead of hard
                #  coding it here.
                score = 0.3
                reply = "Οὐ κάκον. You're close."
            else:
                score = 0
                reply = "Incorrect. Try again!"

            # Set the increment value for times wrong, depending on score
            if score < 0.8:
                times_wrong = 1
                times_right = 0
            else:
                times_wrong = 0
                times_right = 1

        # Handle errors if the student's response cannot be evaluated
        except re.error:
            traceback.print_exc()
            exception_msg = ['these are the responses for a step having '
                             'errors in evaluation: ' + str(responses) +
                             'user response is:' + user_response][0]
            ErrorReport.send_report('StepEvaluator', 'get_eval',
                                    traceback=traceback.format_exc(),
                                    callingRequest=BEAUTIFY(current.request),
                                    xtra=exception_msg
                                    )
            Exception_Bug({'log_id': 0,
                           'path_id': 0,
                           'step_id': 0,
                           'score': 0,
                           'answer': exception_msg,
                           'loc': 0})
            # FIXME: is there still a view for this?
            reply = 'Oops! I seem to have encountered an error in this step.'

        tips = self.tips  # TODO: customize tips for specific errors

        return {'score': score,
                'times_wrong': times_wrong,
                'times_right': times_right,
                'reply': reply,
                'user_response': clean_user_response,
                'tips': tips}


class MultipleEvaluator(StepEvaluator):
    """
    Evaluates a user response to a multiple choice step prompt.
    """

    def __init__(self, responses, tips):
        """Initializes a StepEvaluator object"""
        keys = ['response1', 'response2', 'response3']
        self.responses = {r[0]: r[1] for r in zip(keys, responses)}
        self.tips = tips


class Path(object):
    """
    A class representing one 'path' in the game.
    Following the metaphor of 'walking' around the game environment, a 'path'
    is one discrete chain of user interactions with one or more npcs. A 'path'
    may include as little as one question-answer pair (one 'step') or may
    include any number of inter-dependent interactions ('steps') in a set
    linear sequence.
    So far there is no infrastructure for paths without a set sequence.
    """

    def __init__(self, path_id=None, db=None):
        """
        Initialize a paideia.Path object.
        The following arguments are required at init:
            path_id
            loc_id
        The others are for dependency injection in testing
        """
        db = current.db if not db else db
        self.path_dict = db(db.paths.id == path_id).select().first().as_dict()

        # for _reset_steps only
        auth = current.auth
        self.username = db.auth_user(auth.user_id).first_name

        # controlling step progression through path
        self.steps = self.get_steps()
        self.completed_steps = []
        self.step_for_prompt = None
        self.step_for_reply = None
        self.cat_tag = None

    def get_dict(self):
        return self.path_dict

    def get_id(self):
        """Return the id of the current Path object."""
        return self.path_dict['id']

    def _prepare_for_prompt(self):
        """ move next step in this path into the 'step_for_prompt' variable"""
        try:
            stepcount = len(self.steps)
            if stepcount < 1:  # to bounce back after cleaning User
                # TODO: Does this cause problems?
                self._reset_steps()

                # added by JOB ... sept 22, 2014, step_for_prompt needs to be
                # set after reset
                if self.steps:
                    next_step = self.steps.pop(0)
                    self.step_for_prompt = next_step
                return True
            else:
                next_step = self.steps.pop(0)
                self.step_for_prompt = next_step
                return True
        except:
            print traceback.format_exc(5)
            return False

    def end_prompt(self, stepid):
        """
        End prompt cycle before sending prompt data to view.
        For 1-stage steps this is the end of the step. For 2-stage steps
        this prepares for the reply stage (processing of the user response).
        """
        step = self.step_for_prompt
        # check if id is same so that block steps don't remove step_for_prompt
        if stepid == step.get_id():  # and isinstance(step, (StepText, StepMultiple)):
            self.step_for_reply = copy(self.step_for_prompt)
            self.step_for_prompt = None
        return True

    def complete_step(self):
        """
        Deactivate current step.
        """
        if self.step_for_reply:
            self.completed_steps.append(copy(self.step_for_reply))
            self.step_for_reply = None
            assert not self.step_for_reply
            assert not self.step_for_prompt
        else:
            self.step_for_prompt = None
            assert not self.step_for_reply
        return True

    def _reset_steps(self):
        """
        Return the last completed step to the self.steps list.
        Intended to prepare for repeating an already-completed step.
        """
        debug = False
        if self.completed_steps:
            laststep = self.completed_steps.pop()
            if debug: print 'laststep is', laststep.get_id()
            self.steps.insert(0, laststep)
            if debug: print 'self.steps is', [s.get_id() for s in self.steps]
            # self.steps = copy(self.completed_steps)
            # self.completed_steps = []
        if len(self.steps) == 0:
            self.steps = self.get_steps()
            assert len(self.steps) > 0
        return True

    def get_step_for_prompt(self, loc, repeat=None):
        """
        Find the next unanswered step in the current path and return it.
        If the selected step cannot be performed at this location, return a
        Block object instead.
        """
        debug = False
        if repeat:
            assert self._reset_steps()

        # get step if there isn't already one from redirect
        if not self.step_for_prompt:
            assert self._prepare_for_prompt()
        mystep = self.step_for_prompt

        next_loc = None
        error_string = None
        this_step_id = None
        goodlocs = mystep.get_locations()
        if not loc.get_id() in goodlocs:
            try:
                this_step_id = mystep.get_id()
                next_loc = goodlocs[randrange(len(goodlocs))]
            except ValueError:
                this_step_id = (str(this_step_id) if this_step_id
                                else "can't get step id")
                rawstring = 'Step: {} possible empty location - tag:philadelphia'
                error_string = rawstring.format(this_step_id)
                current.paideia_debug.do_print(error_string + "randrange error "
                                               "NOT permitted",
                                               'Path.get_step_for_prompt')
                print traceback.format_exc(5)
        else:
            mystep.loc = loc  # update location on step
        if debug: print 'Path::get_step_for_prompt: mystep is', mystep

        return mystep, next_loc, error_string

    def get_step_for_reply(self):
        """
        Return the Step object that is currently active for this path.
        This should be the path whose prompt has already been viewed by the user
        and to which the user has submitted a response. This method should only
        be called for steps which allow a user response, i.e. not for:
            StepRedirect
            StepQuotaReached
            StepViewSlides
            StepAwardBadges
            or a bare Step instance
        """
        return self.step_for_reply

    def get_steps(self):
        """
        Return a list containing all the steps of this path as Step objects.
        """
        """
        steplist = [StepFactory().get_instance(step_id=i)
                    for i in [446,448,451,452,453,454,455,456,457,459,445,447]]
        """
        # TODO dont forget to uncomment this

        steplist = [StepFactory().get_instance(step_id=i)
                    for i in self.path_dict['steps']]

        return steplist


class PathChooser(object):
    """
    Select a new path to begin when the user begins another interaction.
    """

    def __init__(self, tag_progress, loc_id, paths_completed, db=None):
        """Initialize a PathChooser object to select the user's next path."""
        self.categories = {k: v for k, v in tag_progress.iteritems()
                           if k not in ['name', 'latest_new']}
        self.rank = tag_progress['latest_new']
        db = current.db if not db else db
        self.loc_id = loc_id
        self.completed = paths_completed
        self.CYCLE_LENGTH = 20  # number of path selections per cycle
        self.CONSTANT_USE_CAT = 'cat1'
        self.CONSTANT_USE_REV = 'rev1'
        self.cat1_choices = tag_progress['cat1_choices'] \
            if 'cat1_choices' in tag_progress.keys() \
            and tag_progress['cat1_choices'] else 0  # counts cat1 choices
        self.all_choices = tag_progress['all_choices'] \
            if 'all_choices' in tag_progress.keys() \
            and tag_progress['all_choices'] else 0  # counts total choices
        self.tag_progress = tag_progress
        self.force_new = self._check_force_new()

    def _set_pathchooser_rank(self, tag_progress=None, given_rank=0):
        if (tag_progress and 'latest_new' in tag_progress and
                tag_progress['latest_new']):
            self.rank = tag_progress['latest_new']
        else:
            self.rank = given_rank

    def _order_cats(self):
        """
        Choose a category to prefer in path selection and order categories
        beginning with that number.
        Returns a list with four members including the integers one-four.
        """
        debug = True
        # TODO: Look at replacing this method with scipy.stats.rv_discrete()

        switch = randint(1, 100)

        if switch in range(1, 75):
            cat = 1
        elif switch in range(75, 91):
            cat = 2
        elif switch in range(91, 99):
            cat = 3
        else:
            cat = 4

        cat_list = range(1, 5)[(cat - 1):4] + range(1, 5)[0:(cat - 1)]
        if debug: print "PathChooser::_order_cats: categories prioritized in order:", cat_list
        return cat_list

    def _check_force_new(self):
        """
        Determines whether to select from categories normally or force cat1.

        The point here is to ensure that at least X proportion of every Y paths
        chosen are genuinely new material for the user (i.e., have tags in cat1)
        rather than being drawn from other tags that are simply up for review
        (which are also included in rev1).

        Returns 'True' if we are forcing the choice of new
        material. Otherwise returns False.
        """
        debug = True
        # reset choice counter at end of each cycle
        self.all_choices = self.all_choices % self.CYCLE_LENGTH
        if self.all_choices == 0:
            self.cat1_choices = 0

        # cat1 choices still needed this cycle to make up quota
        cat1_still_needed = (self.CYCLE_LENGTH/2) - self.cat1_choices
        left_in_cycle = self.CYCLE_LENGTH - self.all_choices

        # do we need all remaining choices in this cycle to make up cat1 quota?
        cat1_deficit = True if (cat1_still_needed >= left_in_cycle) else False
        if cat1_deficit:
            self.cat1_choices += 1  # FIXME: what about regular cat1 choices?
            rslt = True
            if debug: print 'PathChooser::_check_force_new: forcing new'
        else:
            rslt = False

        self.all_choices += 1
        self.tag_progress['cat1_choices'] = self.cat1_choices
        self.tag_progress['all_choices'] = self.all_choices
        return rslt

    def _paths_by_category(self, cat, rank):
        """
        Assemble list of paths tagged with tags in the chosen category.

        Return a dictionary with categories as keys and corresponding lists
        pathset :: list of dictionaries holding the data for selected paths
        cat :: integer representing the category from which choice was made
        force_cat1 :: boolean indicating whether or not cat1 selection was forced

        """
        debug = True
        db = current.db
        pathset = None
        force_cat1 = False
        while True:
            # TODO: set up computed field
            # if not db(db.paths).select().first().path_tags:
            # for row in db(db.paths.id > 0).select():
            # db(db.paths.id == row.id).update(steps=row.steps)
            # TODO: include paths with tag as secondary, maybe in second list?
            # TODO: cache the select below and just re-order randomly

            taglist = []

            def get_stepslist(taglist):
                if debug: print 'PathChooser::_paths_by_cateogry: using taglist', taglist
                myrows = db(db.steps.tags.contains(taglist)).select()
                myrows = myrows.find(lambda row: row.status != 2)
                mylist = [v.id for v in myrows]
                return mylist

            taglist = self.categories['rev{}'.format(cat)]
            taglist_cat1 = self.categories['cat1']
            if debug: print 'PathChooser::_paths_by_category: cat1_choices', self.cat1_choices
            if debug: print 'PathChooser::_paths_by_category: all_choices', self.all_choices
            if self.force_new:
                if debug: print 'PathChooser::_paths_by_category: forcing new'
                cat = 1
                force_cat1 = True
                stepslist = get_stepslist(taglist_cat1)
                if not stepslist:  # In case no steps in db for cat1 tags
                    # FIXME: send an error report here?
                    stepslist = get_stepslist(taglist)
            else:
                stepslist = get_stepslist(taglist)
                # find out whether
                if cat == 1:
                    new_stepslist = get_stepslist(taglist_cat1)

            if not stepslist:
                break

            """
            TODO: Why did JOB do it this way?
            # get id's for all steps marked with tags in taglist
            #stepslist_unhashable = db(db.step2tags.tag_id.belongs(taglist)
                                      #).select(db.step2tags.step_id).as_list()
            #if not stepslist_unhashable:
                #break
            #stepslist = [v['step_id'] for v in stepslist_unhashable]

            # remove steps with status 2 (deactivated)
            #stepslist_unhashable = db((db.steps.id.belongs(stepslist)) &
                                      #(db.steps.status != 2)
                                      #).select(db.steps.id).as_list()
            #stepslist = [v['id'] for v in stepslist_unhashable]
            """

            """
            # find all paths with a step in steplist
            #pathset_ids_unhashable = db(db.path2steps.step_id.belongs(stepslist)
                                        #).select(db.path2steps.path_id
                                                 #).as_list()
            #pathset_ids = [v['path_id'] for v in pathset_ids_unhashable]
            #if not pathset_ids:
                #break
            """

            #pathset = db(db.paths.steps.contains(stepslist)).select()
            pathset_all = db(db.paths.id > 0).select()
            pathset = pathset_all.find(lambda row: any(s for s in row.steps
                                                   if s in stepslist))

            # filter out any paths whose steps don't have a location
            pathset = pathset.find(lambda row: all([Step(s).has_locations()
                                                    for s in row.steps]))

            # figure out whether actually new material
            pathset_new = []
            if cat == 1 and not force_cat1:
                pathset_new = pathset_all.find(lambda row: any(s for s in row.steps
                                                   if s in new_stepslist))
                pathset_new = pathset_new.as_list()

            pathset = pathset.as_list()
            break
        return pathset, cat, force_cat1, pathset_new

    def _choose_from_cat(self, cpaths, category):
        """
        Select a path from the category supplied as an argument.
        Returns a 3-member tuple. The first value is the chosen path, and the
        second is a location id. If the location id is None, it means that the
        path can be begun in the current location. If that second member is an
        integer then the user should be redirected to that location. The third
        member is an integer between 1 and 4 corresponding to the category from
        which the path was chosen.

        Note: This method is *not* intended to handle categories with no
        available paths for this user. If such a category is supplied the
        method will raise an error.

        _paths_by_category is supposed to have filtered out
        all paths that have steps with no locations

        """
        debug = True
        path = None
        new_loc = None
        mode = None
        completed_list = [int(k) for k in self.completed['paths'].keys()]

        # print 'in _choose_from_cat ---------------------------------'
        while True:
            loc_id = self.loc_id
            db = current.db
            p_new = [p for p in cpaths if p['id'] not in completed_list]
            # print 'p_new:', [p['id'] for p in p_new]
            p_here = [p for p in cpaths
                      if loc_id in db.steps[int(p['steps'][0])].locations]
            # print 'p_here:', [p['id'] for p in p_here]
            p_here_new = [p for p in p_here if p in p_new]
            print 'p_here_new:', [p['id'] for p in p_here_new]
            p_all = [p for p in cpaths]
            p_tried_ids = list(set([p['id'] for p in cpaths]
                                   ).intersection(completed_list))
            # print 'p_tried:', p_tried_ids
            p_tried = [p for p in cpaths if p['id'] in p_tried_ids]

            # print 'self.completed:', self.completed['paths']
            # untried path available here
            if p_here_new:
                path = p_here_new[randrange(0, len(p_here_new))]
                mode = 'here_new'
                break
            # untried path available elsewhere
            if p_new:
                loopmax = len(p_new)*5  # prevent infinite loop
                loopcount = 0
                while path is None:
                    try:
                        loopcount += 1  # prevent infinite loop
                        if (loopcount > loopmax):
                            break

                        # choose randomly from untried paths
                        idx = randrange(0, len(p_new))
                        path = p_new[idx]

                        # find location for new path to be started
                        new_locs = db.steps(path['steps'][0]).locations
                        goodlocs = [l for l in new_locs
                                    if db.locations[l].loc_active is True]
                        new_loc = goodlocs[randrange(0, len(goodlocs))]
                        mode = 'new_elsewhere'
                    except TypeError:
                        path = None
                    except ValueError:
                        print traceback.format_exc(5)
                break
            if p_tried:
                try:
                    repeats = [{'id': str(p['id']), 'count': 0, 'path': p}
                                   for p in p_tried]
                    # get number of attempts for each path visited
                    for prep in repeats:
                        pid = int(prep['id'])
                        try:
                            comp_rec = self.completed['paths'][str(pid)]
                        except KeyError:
                            comp_rec = self.completed['paths'][pid]

                        prep['count'] = comp_rec['wrong'] + comp_rec['right']

                    mode = 'repeated'
                    new_loc = None

                    while True:  # find an available repeat path
                        if not repeats:  # prevent infinite loop
                            break
                        # repeat all once before repeating another twice, etc.
                        # TODO: randomize order of paths with equal counts
                        repeats_sorted = sorted(repeats,
                                                    key=lambda k: k['count'])
                        path = repeats_sorted[0]['path']

                        # find loc for repeat path
                        path_locs = db.steps(path['steps'][0]).locations
                        goodlocs = [l for l in path_locs
                                    if db.locations[l].loc_active is True]
                        # repeat path can be done here
                        if self.loc_id in goodlocs:
                            new_loc = self.loc_id
                            break
                        # need to start repeat path elsewhere
                        new_loc = goodlocs[randrange(0, len(goodlocs))] \
                                           if len(goodlocs) else None
                        if new_loc:
                            break
                        repeats.pop(0)  # if no viable loc for path, try another
                except ValueError:
                    print traceback.format_exc(5)
            if new_loc:
                if self.loc_id == new_loc:
                    new_loc = None  # new_loc = None means keep curr_loc
                    break
            # else choose from category paths at random
            if p_all:  # redundant ... shouldn't get to this point
                loopmax = len(p_all)*5  # ensure no infinite loop
                loopcount = 0
                while path is None:
                    try:
                        loopcount += 1
                        if (loopcount > loopmax): break
                        idx = randrange(0, len(p_all))
                        path = p_all[idx]
                        new_locs = db.steps(path['steps'][0]).locations
                        goodlocs = [l for l in new_locs if db.locations[l].loc_active is True]
                        new_loc = goodlocs[randrange(0, len(goodlocs))]
                        mode = 'any from category'
                    except TypeError:
                        path = None
                    except ValueError:
                        print traceback.format_exc(5)
                break  # redundant at the moment
            break  # from main while True

        return (path, new_loc, category, mode)

    def choose(self, set_review=None, db=None):
        """
        Choose a path for the current user based on performance record.
        The algorithm looks for paths using the following tests, in this order:
        - has a due tag & can be started in current location & untried today
        - has a due tag & untried today
        - has a due tag & already tried today
        - has a tag that's not due & untried today
        - any random path
        Returns a 3-member tuple:
            [0] Path chosen (as a row object as_dict)
            [1] location id where Path must be started (or None if current loc)
            [2] the category number for this new path (int in range 1-4)
        """
        db = current.db if not db else db
        debug = True
        new_material = False
        if set_review:  # select randomly from the supplied badge set (review and demo)
            myset = set_review
            set_tags = db(db.tags.tag_position == myset).select()
            taglist = [t['id'] for t in set_tags]
            set_steps = db(db.steps.tags.contains(taglist)).select()
            steplist = [s['id'] for s in set_steps]
            set_paths = db(db.paths.steps.contains(steplist)).select()
            path = set_paths[randrange(0, len(set_paths))]
            first_step = db.steps[path['steps'][0]]
            if debug: print 'PathChooser::choose: first_step is', first_step.id
            if self.loc_id in first_step['locations']:
                new_loc = None
            else:
                new_loc = [l for l in first_step['locations'] if db.locations[l].loc_active][0]
            category = None  # using badge set, not categories
            mode = "reviewing set {}".format(myset)
            new_material = False
            return path, new_loc, category, mode, new_material, self.tag_progress

        else:  # regular category based selection (default)
            cat_list = [c for c in self._order_cats()
                        if self.categories['rev{}'.format(c)]]
            # 'if' guarantees that no categories are attempted for which no tags
            # due

            # cycle through categories, prioritised in _order_cats()
            for cat in cat_list:
                if debug: print 'PathChooser::choose: checking in cat', cat
                catpaths, category, use_cat1, pathset_new = \
                    self._paths_by_category(cat, self.rank)
                #print 'forcing cat1?', use_cat1
                #print 'catpaths:', [c['id'] for c in catpaths]
                if catpaths and len(catpaths):
                    if debug: print 'PathChooser::choose: using category', category
                    path, newloc, category, mode = self._choose_from_cat(catpaths,
                                                                         category)
                    if mode:
                        # catch unforced choices of new material for this user
                        # and pass back whether or not the path is new material
                        if pathset_new:
                            if path['id'] in [p['id'] for p in pathset_new]:
                                new_material = True
                                self.cat1_choices += 1
                                self.tag_progress['cat1_choices'] = self.cat1_choices
                        elif self.force_new:
                            new_material = True
                        if debug: print 'PathChooser::choose: new_material =', new_material
                        return path, newloc, category, mode, new_material, self.tag_progress
                    else:
                        if debug: print 'bad mode trying another category'
                else:
                    continue
            return None, None, None, None, None, None


class User(object):
    """
    An object representing the current user, including his/her performance
    data and the paths completed and active in this session.
    """

    def __init__(self, userdata, tag_records, tag_progress, db=None, blocks=[]):
        """
        Initialize a paideia.User object.
        ## Argument types and structures
        - userdata: {'first_name': str, 'id': int, ..}
        - tag_progress: rows.as_dict()
        - tag_records: rows.as_dict
        """
        debug = False
        db = db if db else current.db
        # TODO: this 'if' is for testing and not functionally necessary
        if 'sequence_counter' not in dir(current):
            current.sequence_counter = 0
        try:
            self.time_zone = userdata['time_zone']
            self.blocks = blocks
            if debug: print 'User::init: self.blocks', self.blocks
            # FIXME: somehow pass previous day's blocks in user._is_stale()?
            self.name = userdata['first_name']
            self.user_id = userdata['id']

            self.path = None
            #each path in self.completed['paths'] will now be a hash {'path_id': {'right': int, 'wrong': int}}
            self.completed_paths = {'latest': None, 'paths': {}}

            self.cats_counter = 0  # timing re-categorization in get_categories()

            self.old_categories = {}
            self.tag_records = tag_records
            self._set_user_rank(tag_progress, 1)  # FIXME: return, don't set in method?
            #self.rank = tag_progress['latest_new'] if tag_progress else 1
            self.tag_progress = tag_progress
            self.promoted = None
            self.demoted = None
            self.new_tags = None

            self.inventory = []
            self.session_start = datetime.datetime.utcnow()

            self.loc = None
            self.prev_loc = None
            self.npc = None
            self.prev_npc = None
            self.quota = self._get_paths_quota(self.user_id)

            self.past_quota = False
            self.viewed_slides = False
            self.reported_badges = False
            self.reported_promotions = False

            self.repeating = False
            self.new_content = False
            self.active_cat = None
        except Exception:
            print traceback.format_exc(5)

    def __str__(self):
        strout = ['---------------------------------\n'
                  'Paideia User Object--------------\n'
                  '---------------------------------\n'
                  'USER DATA\n'
                  '---------------------------------\n'
                  'name: {name}\n'
                  'user_id: {user_id}\n'
                  'time_zone: {time_zone}\n'
                  'quota: {quota}\n'
                  '---------------------------------\n'
                  'CURRENT PATH\n'
                  '---------------------------------\n'
                  '{path}\n'
                  '\n---------------------------------\n'
                  'CURRENT STATE\n'
                  'session_start: {session_start}\n'
                  'blocks: {blocks}\n'
                  'completed_paths: {completed_paths}\n'
                  'cats_counter: {cats_counter}\n'
                  'inventory: {inventory}\n'
                  '---------------------------------\n'
                  'PROMOTION AND RANKING\n'
                  '---------------------------------\n'
                  'old_categories----------\n'
                  '{old_categories}\n'
                  'tag_progress------------\n'
                  '{tag_progress}\n'
                  'tag_records-------------\n'
                  '{tag_records}\n'
                  'promoted----------------\n'
                  '{promoted}\n'
                  'demoted-----------------\n'
                  '{demoted}\n'
                  'new_tags----------------\n'
                  '{new_tags}\n'
                  '---------------------------------\n'
                  'LOCATION AND NPC\n'
                  '---------------------------------\n'
                  'loc: {loc}\n'
                  'prev_loc: {prev_loc}\n'
                  'npc: {npc}\n'
                  'prev_npc: {prev_npc}\n'
                  '---------------------------------\n'
                  'FLAGS\n'
                  '---------------------------------\n'
                  'past_quota: {past_quota}\n'
                  'viewed_slides: {viewed_slides}\n'
                  'reported_badges: {reported_badges}\n'
                  'reported_promotions: {reported_promotions}\n'
                  '---------------------------------\n']
        return strout[0].format(name=self.name,
                                user_id=self.user_id,
                                time_zone=self.time_zone,
                                quota=self.quota,
                                path=self.path,
                                session_start=self.session_start,
                                blocks=self.blocks,
                                completed_paths=self.completed_paths,
                                cats_counter=self.cats_counter,
                                inventory=self.inventory,
                                old_categories=self.old_categories,
                                tag_progress=self.tag_progress,
                                tag_records=self.tag_records,
                                promoted=self.promoted,
                                demoted=self.demoted,
                                new_tags=self.new_tags,
                                loc=self.loc,
                                prev_loc=self.prev_loc,
                                npc=self.npc,
                                prev_npc=self.prev_npc,
                                past_quota=self.past_quota,
                                viewed_slides=self.viewed_slides,
                                reported_badges=self.reported_badges,
                                reported_promotions=self.reported_promotions)

    def _get_paths_quota(self, user_id):
        """Return the daily path quota (int) for the user's class section."""
        db = current.db
        msel = db((db.class_membership.name == self.user_id) &
                  (db.class_membership.class_section == db.classes.id)
                  ).select()
        try:
            target = [m.classes.paths_per_day for m in msel
                      if m.classes.paths_per_day][0]
        except IndexError:
            print 'user not a member of any class, defaulting to 20 quota'
            target = 20
        return target

    def _set_user_rank(self, tag_progress=None, given_rank=0):
        if (tag_progress and
                'latest_new' in tag_progress and
                tag_progress['latest_new']):
            self.rank = tag_progress['latest_new']
        else: self.rank = given_rank

    def get_completed_paths_len(self):
        """
        returns length of completed paths
        adds up counts of each completed path ...essentially how
        many times did you get something right
        """
        p_len = 0
        for x in self.completed_paths['paths']:
            p_len += self.completed_paths['paths'][x]['right']
            p_len += self.completed_paths['paths'][x]['wrong']
        return p_len

    def get_id(self):
        """Return the id (from db.auth_user) of the current user."""
        return self.user_id

    def get_name(self):
        """Return the first name (from db.auth_user) of the current user."""
        return self.name

    def get_prev_npc(self):
        """Return the id (from db.npcs) of the previously active npc."""
        return self.prev_npc

    def check_for_blocks(self):
        """
        Check whether new block needed, then activate first block (if any).
        If a block is found:
        - Returns a step subclass instance (StepRedirect, StepQuotaReached,
            StepAwardBadges, or StepViewSlides)
        - also sets self.step_sent_id
        If a block is not found:
        - Returns None
        """
        # TODO make sure that current loc and npc get set for self.prev_loc etc
        debug = False
        if self.blocks:
            if debug: print 'User::check_for_blocks: blocks present'
            blockset = []
            for b in self.blocks:
                if not b.get_condition() in [c.get_condition() for c in blockset]:
                    blockset.append(b)
            self.blocks = blockset
            if debug: print 'User::check_for_blocks: blockset', blockset
            current.sequence_counter += 1  # TODO: why increment twice here?
            myblock = self.blocks.pop(0)
            if debug: print 'User::check_for_blocks: myblock', blockset
            current.sequence_counter += 1  # TODO: why increment twice here?
            return myblock
        else:
            if debug: print 'User::check_for_blocks: no blocks present'
            return None

    def set_block(self, condition, kwargs=None):
        """ Set a blocking condition on this Path object. """
        myblocks = [b.get_condition() for b in self.blocks]
        current.sequence_counter += 1

        def _inner_set_block():
            if condition not in myblocks:
                self.blocks.append(Block(condition, kwargs=kwargs))

        if condition == 'view_slides':
            if not self.viewed_slides:
                _inner_set_block()
                self.viewed_slides = True
        elif condition == 'new_tags':
            if not self.reported_badges:
                _inner_set_block()
                self.reported_badges = True
            else:
                current.sequence_counter += 1
        #elif condition == 'promoted':
        #    if not self.reported_promotions:
        #        _inner_set_block()
        #        self.reported_promotions = True
        else:
            _inner_set_block()

        current.sequence_counter += 1
        return True

    def is_stale(self, now=None, start=None, time_zone=None, db=None):
        """
        Return true if the currently stored User should be discarded.
        User should be discarded (and a new one generated) at midnight local
        time.
        The arguments 'now', 'start', and 'tzone' are only used for dependency
        injection in unit testing.
        """
        db = current.db if not db else db
        now = datetime.datetime.utcnow() if not now else now
        time_zone = self.time_zone if not time_zone else time_zone
        tz = timezone(time_zone)
        local_now = tz.fromutc(now)
        # adjust start for local time
        start = self.session_start if not start else start
        lstart = tz.fromutc(start)
        daystart = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        if lstart < daystart:
            return True
        elif lstart > local_now:
            return False
        else:
            return False

    def set_npc(self, npc):
        """
        """
        self.prev_npc = copy(self.npc)
        self.npc = npc
        return True

    def set_location(self, loc):
        """
        Update the user's location after initialization of the User object.
        Includes setting of self.prev_loc to the old location id and calling
        of path.set_location().
        Returns a boolean indicating success/failure.
        """
        if isinstance(self.prev_loc, int):
            self.prev_loc = Location(self.prev_loc)
        else:
            self.prev_loc = copy(self.loc)
        self.loc = loc
        return self.prev_loc

    def get_location(self):
        """
        Return a Location object for the user's current location.
        """
        return self.loc

    def _make_path_choice(self, loc, set_review=None):
        """
        Instantiate PathChooser and return the result of its choose() method.
        """
        debug = False
        choice = None
        if self.path:  # TODO: do I want this catch here?
            self.path = None
        if not self.tag_progress:  # in case User was badly initialized
            #print 'no tag-progress, so getting categories'
            self.get_categories()

        if 'cat1_choices' not in self.tag_progress:
            self.tag_progress['cat1_choices'] = 0
        if 'all_choices' not in self.tag_progress:
            self.tag_progress['all_choices'] = 0
        choice, redir, cat, mode, new_content, tag_progress = \
            PathChooser(self.tag_progress,
                        loc.get_id(),
                        self.completed_paths).choose(set_review=set_review)
        self.tag_progress = tag_progress  # to keep counts made in PathChooser
        if debug: print 'User::_make_path_choice: mode is', mode
        #print 'in _make_path_choice ----------------------------------------'
        #print 'choice:', choice
        #print 'redir:', redir
        #print 'cat:', cat
        #print 'mode:', mode
        #print '-------------------------------------------------------------'
        condition = {'name': self.get_id()}
        current.db.tag_progress.update_or_insert(condition, **self.tag_progress)
        current.db.commit()

        if debug: 'User::_make_path_choice: mode is', mode
        # FIXME: if no choice, send_error('User', 'get_path', current.request)
        if mode:
            path = Path(path_id=choice['id'])
            if re.match(r'reviewing.*', mode, re.I):  # show mode if not regular choice
                cat = mode
                if debug: 'User::_make_path_choice: reviewing, cat is: ', cat
            if debug: print 'User::_make_path_choice: num of path.steps is', len(path.steps)
            return path, redir, cat, new_content
        else: return None, None, None, None

    def get_path(self, loc, db=None, pathid=None, repeat=None, set_review=None):
        """
        Return the currently active Path object.
        Only the 'loc' argument is strictly necessary. The others are used for
        dependency injection during testing (db and pathid) or for special
        selection modes (repeat, set_review).
        """
        debug = False
        db = current.db if not db else db
        redir = None
        cat = self.active_cat  # preserve previous val in multi-step paths
        pastq = None
        new_content = self.new_content   # preserve previous val in multi-step paths
        if debug: print 'User::get_path: starting self.path is', self.path
        if self.path:
            if debug: print 'User::get_path: self.path id is', self.path.get_id()
            if debug: print 'User::get_path:', len(self.path.steps), 'steps left in path'
        while True:
            if pathid:  # testing specific path
                self.path = Path(pathid)
                if debug: print 'con 1'

            if repeat and not self.path:  # repeating a step, path finished before
                if debug: print 'User::get_path: repeating a finished path'
                pathid = self.completed_paths['latest']
                self.path = Path(pathid)
            elif self.path and self.path.step_for_prompt:
                pass
            elif self.path and self.path.step_for_reply:
                pass
            elif self.path and repeat:  # repeating a step, path wasn't finished
                pass
            elif self.path and len(self.path.steps):  # unfinished step in self.path
                pass
            else:  # choosing a new path
                self.path, redir, cat, new_content = \
                    self._make_path_choice(loc, set_review=set_review)
                #print 'path chosen:', self.path.get_id()
                if (not self.path):
                    break  # and return Nones

            if self.get_completed_paths_len() >= self.quota and \
                    self.past_quota is False:
                pastq = True
                self.past_quota = True
            if len(self.blocks) > 0:
                # FIXME: This hack is to work around mysterious introduction of
                # redirect block after initial redirect has been triggered
                self.blocks = [b for b in self.blocks
                               if not b.get_condition() is 'redirect']
            break
        return (self.path, cat, redir, pastq, new_content)

    def get_categories(self, user_id=None, rank=None, old_categories=None,
                       tag_records=None, utcnow=None):
        """
        Return a categorized dictionary with four lists of tag id's.
        This method is important primarily to decide whether a new
        categorization is necessary before instantiating a Categorizer object
        # TODO: do we need to create new categorizer object each time?
        The method is intended to be called with no arguments unless values
        are being provided for testing.
        """
        cat1_choices = 0
        all_choices = 0

        db = current.db
        user_id = self.user_id if not user_id else user_id
        if not tag_records:
            tag_records = db(db.tag_records.name == user_id).select().as_list()
        self.tag_records = tag_records

        if (self.cats_counter in range(0, 4)) \
                and hasattr(self, 'categories') \
                and self.tag_progress \
                and self.categories:
            self.cats_counter += 1
            return self.tag_progress, None, None, None
        else:
            utcnow = datetime.datetime.utcnow() if not utcnow else utcnow
            try:
                if old_categories:
                    tpdict = old_categories
                else:
                    tp_sel = db(db.tag_progress.name == user_id).select()
                    assert len(tp_sel) == 1
                    tpdict = tp_sel.first().as_dict()
                self.tag_progress = tpdict
                rank = tpdict['latest_new']
                cat1_choices = tpdict['cat1_choices'] if 'cat1_choices' in tpdict.keys() else 0
                all_choices = tpdict['all_choices'] if 'all_choices' in tpdict.keys() else 0
                # TODO: below is 'magic' hack based on specific db field names
                categories = {k: v for k, v in tpdict.iteritems()
                              if k[:3] in ['cat', 'rev']}
            except (AttributeError, AssertionError):
                print traceback.format_exc()
                categories = None
            self.old_categories = copy(categories)

            c = Categorizer(rank, categories, tag_records, user_id,
                            utcnow=utcnow)
            cat_result = c.categorize_tags(old_categories=old_categories)
            # passing 'old_categories' allows it to be passed on in testing

            self._set_user_rank(cat_result['tag_progress'], 0)

            self.tag_records = cat_result['tag_records']
            self.tag_progress = cat_result['tag_progress']
            self.tag_progress['cat1_choices'] = cat1_choices
            self.tag_progress['all_choices'] = all_choices
            self.categories = cat_result['categories']
            self.promoted = cat_result['promoted']
            self.new_tags = cat_result['new_tags']
            self.demoted = cat_result['demoted']
            self.cats_counter = 0  # reset counter

            return (self.tag_progress, self.promoted,
                    self.new_tags, cat_result['demoted'])

    def complete_path(self, got_right):
        """
        Move the current path from the path variable to 'completed_paths' list.
        Set last_npc and prev_loc before removing the path.

        Argument 'got_right' is a boolean indicating success or failure in this
        path attempt.

        # Only id of paths stored to conserve memory.
        # prev_loc and prev_user info not drawn from old paths but
        # carried on User.
        # Repeating path must be triggered before path is completed.

        #we now using hash {'path_id':count} to keep track of completed_paths
        # {'latest' : path_id} gives path_id of the latest one
        """
        # FIXME: I think this is firing for every recorded step, not just at the
        # end of every path. The current behaviour is right, but the method is
        # misnamed and I'm not sure the implications for recording completed
        # paths.
        if (str(self.path.get_id()) not in self.completed_paths['paths']):
            pdict = {'right': 0, 'wrong': 0, 'path_dict': self.path.get_dict()}
            self.completed_paths['paths'][str(self.path.get_id())] = pdict
        if got_right:
            self.completed_paths['paths'][str(self.path.get_id())]['right'] += 1
        else:
            self.completed_paths['paths'][str(self.path.get_id())]['wrong'] += 1
        self.completed_paths['latest'] = self.path.get_id()

        return True

    def _reset_for_walk(self):
        """
        reset certain parameters after a walk
        """
        self.viewed_slides = False
        self.reported_badges = False
        self.reported_promotions = False

    def clear_block_records(self):
        """
        reset certain parameters after a walk
        """
        self.new_tags = None
        self.promoted = None


class Categorizer(object):
    """
    A class that categorizes a user's active tags based on past performance.
    The categories range from 1 (need immediate review) to 4 (no review
    needed). Returns a dictionary with four keys corresponding to the four
    categories. The value for each key is a list holding the id's
    (integers) of the tags that are currently in the given category.
    """

    def __init__(self, rank, tag_progress, tag_records, user_id,
                 secondary_right=None, utcnow=None, db=None):
        """Initialize a paideia.Categorizer object"""
        self.db = current.db if not db else db
        self.user_id = user_id
        self.rank = rank
        self.tag_records = tag_records
        self.old_categories = tag_progress
        self.utcnow = utcnow if utcnow else datetime.datetime.utcnow()
        self.secondary_right = secondary_right

    def _set_categorizer_rank(self, tag_progress=None, given_rank=0):
        if (tag_progress and 'latest_new' in tag_progress and tag_progress['latest_new']):
            self.rank = tag_progress['latest_new']
        else: self.rank = given_rank

    def _sanitize_recs(self, tag_records):
        """
        Remove any illegitimate tag_records data.
        """
        null_tags = [r for r in tag_records if r['tag'] is None]
        if null_tags:
            db = current.db
            db(db.tag_records.tag == None).delete()
            tag_records = db(db.tag_records.name == self.user_id
                             ).select().as_list()
            self.tag_records = tag_records

        return tag_records

    def categorize_tags(self, rank=None, tag_records=None,
                        old_categories=None, db=None):
        """
        Return a categorized dictionary of grammatical tags.
        The keys are the four categories used in the path selection algorithm,
        and the values are lists of integers (representing the tags to be
        placed in each category). The categorization is based on user
        performance (drawn from tag_records) and timing (spaced repetition).
        """
        rank = self.rank if not rank else rank
        if not rank:
            rank = 1
        old_categories = self.old_categories if not old_categories \
                         else old_categories

        if not tag_records:  # allows passing trecs for testing
            db = current.db if not db else db
            tagorder = db.tag_records.tag
            tag_records = db(db.tag_records.name == self.user_id
                             ).select(orderby=tagorder).as_list()

        self.tag_records = tag_records
        new_tags = None

        # if user has not tried any tags yet, start first set
        if len(tag_records) == 0:
            categories = {'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}
            categories['rev1'] = self._introduce_tags(rank=0)
            tp = {'cat1': categories['rev1'], 'rev1': categories['rev1'],
                  'cat2': [], 'rev2': [],
                  'cat3': [], 'rev3': [],
                  'cat4': [], 'rev4': [],
                  'latest_new': self.rank,
                  'cat1_choices': 0, 'all_choices': 0}
            return {'tag_progress': tp,
                    'tag_records': tag_records,
                    'new_tags': {'rev1': categories['rev1'], 'rev2': [],
                                 'rev3': [], 'rev4': []},
                    'promoted': None,
                    'demoted': None,
                    'categories': categories}
        else:
            # otherwise, categorize tags that have been tried

            for idx, t in enumerate([t for t in tag_records
                                     if tag_records and t['secondary_right']]):
                self._add_secondary_right(t)
            categories = self._core_algorithm()
            categories = self._add_untried_tags(categories)
            categories = self._remove_dups(categories, rank)
            categories.update((c, []) for c in ['cat1', 'cat2', 'cat3', 'cat4'])
            cat_changes = self._find_cat_changes(categories, old_categories)

            promoted = cat_changes['promoted']
            demoted = cat_changes['demoted']
            new_tags = cat_changes['new_tags']
            tag_progress = copy(cat_changes['categories'])

            #add cats for new tags
            for i in range(1, 5):
                idx = 'rev{}'.format(i)
                if (new_tags and idx in new_tags and new_tags[idx]):
                    idxcat = 'cat{}'.format(i)
                    curr_cat = tag_progress[idxcat] if (idxcat in tag_progress and tag_progress[idxcat]) else []
                    tag_progress[idxcat] = list(set(curr_cat).union(new_tags[idx]))[:]

            # If there are no tags left in category 1, introduce next set
            if self._check_if_cat1_needed(tag_progress):
                while True:
                    newlist = self._introduce_tags(rank=rank)
                    if not newlist:
                        current.paideia_debug.do_print("ERROR: failed to get "
                                                       "tags for rank {}"
                                                       "".format(rank),
                                                       'Categorizer.categorize_tags')
                        break
                    curr_rev1 = tag_progress['rev1'] if ('rev1' in tag_progress and tag_progress['rev1']) else []
                    curr_cat1 = tag_progress['cat1'] if ('cat1' in tag_progress and tag_progress['cat1'])else []
                    tag_progress['cat1'] = list(set(curr_cat1).union(newlist))[:]
                    tag_progress['rev1'] = list(set(curr_rev1).union(newlist))[:]
                    if not new_tags: new_tags = {'rev1': []}
                    curr_new_tags_rev1 = new_tags['rev1'] if (new_tags and 'rev1' in new_tags and new_tags['rev1']) else []
                    new_tags['rev1'] = list(set(curr_new_tags_rev1).union(newlist))[:]

                    curr_rev1 = categories['rev1'] if ('rev1' in categories and categories['rev1']) else []
                    curr_cat1 = categories['cat1'] if ('cat1' in categories and categories['cat1']) else []
                    categories['cat1'] = list(set(curr_cat1).union(newlist))[:]
                    categories['rev1'] = list(set(curr_rev1).union(newlist))[:]
                    break
            # Re-insert 'latest new' to match tag_progress table in db
            tag_progress['latest_new'] = self.rank

            return {'tag_progress': tag_progress,
                    'tag_records': self.tag_records,
                    'new_tags': new_tags,
                    'promoted': promoted,
                    'demoted': demoted,
                    'categories': categories}

    def _check_if_cat1_needed(self, cats):
        if 'cat1' not in cats or not cats['cat1']:
            return True
        else:
            return False

    def _remove_dups(self, categories, rank):
        """
        Remove any duplicate tags and any tags beyond user's current rank.
        """
        db = current.db
        for k, v in categories.iteritems():
            if v:
                rankv = [t for t in v if db.tags(t) and
                         (db.tags[t].tag_position <= rank)]
                rankv = list(set(rankv))
                rankv.sort()
                categories[k] = rankv
        return categories

    def _add_secondary_right(self, rec):
        """
        Return the given tag record adjusted based on secondary_right data.
        For every CONST_SEC_RIGHT_MOD secondary_right entries, add 1 to
        times_right and change tlast_right based on the average of those
        attempt dates.
        """
        CONST_SEC_RIGHT_MOD = 20
        db = current.db
        rec = rec[0] if isinstance(rec, list) else rec

        right2 = flatten(rec['secondary_right'])  # FIXME: sanitizing data
        if right2 != rec['secondary_right']:  # FIXME: can remove when data clean
            right2.sort()

        rlen = len(right2)
        rem2 = rlen % CONST_SEC_RIGHT_MOD

        if rlen >= CONST_SEC_RIGHT_MOD:
            # increment times_right by 1 per CONST_SEC_RIGHT_MOD secondary_right
            # this var is called triplets because CONST_SEC_RIGHT_MOD used to be 3
            triplets2 = rlen / CONST_SEC_RIGHT_MOD
            rec['times_right'] = triplets2 if not rec['times_right'] \
                else rec['times_right'] + triplets2

            # move tlast_right forward based on mean of oldest
            # CONST_SEC_RIGHT_MOD secondary_right dates
            early3 = right2[: -(rem2)] if rem2 else right2[:]
            early3d = [self.utcnow - parser.parse(s) for s in early3]
            #          datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
            avg_delta = sum(early3d, datetime.timedelta(0)) / len(early3d)
            avg_date = self.utcnow - avg_delta

            # sanitize tlast_right in case db value is string
            if not isinstance(rec['tlast_right'], (datetime.datetime, tuple)):
                rec['tlast_right'] = parser.parse(rec['tlast_right'])

            # move tlast_right forward to reflect recent secondary success
            if avg_date > rec['tlast_right']:
                rec['tlast_right'] = avg_date

            rec['secondary_right'] = right2[-(rem2):] if rem2 else []

            #write new record to dbase
            condition = {'tag': rec['tag'], 'name': rec['name']}
            db.tag_records.update_or_insert(condition,
                                            times_right=rec['times_right'],
                                            tlast_right=rec['tlast_right'],
                                            secondary_right=rec['secondary_right'])
            db.commit()
        else:
            pass
        return rec

    def _get_avg(self, tag, mydays=5):
        """
        Return the user's average score on a given tag over the past N days.
        Always returns a float, since scores are floats between 0 and 1.
        """
        # print 'user', self.user_id
        db = current.db
        startdt = self.utcnow - datetime.timedelta(days=mydays)
        log_query = db((db.attempt_log.name == self.user_id) &
                       (db.attempt_log.dt_attempted >= startdt) &
                       (db.attempt_log.step == db.steps.id) &
                       (db.steps.tags.contains(tag))).select()
        scores = [l.attempt_log.score for l in log_query]
        try:
            avg_score = sum(scores) / float(len(scores))
        except ZeroDivisionError:  # if tag not tried at all since startdt
            avg_score = 0
            # FIXME: Will this not bring tags up too early?
        return avg_score

    def _get_ratio(self, record):
        """
        Return the user's ratio of right to wrong answers for a given tag.
        Called by _core_algorithm()
        """
        try:
            ratio = record['times_wrong'] / record['times_right']
        except ZeroDivisionError:
            ratio = record['times_wrong']
        except TypeError:  #
            if not record['times_right']:
                ratio = 1
            else:
                ratio = 0
        return ratio

    def _core_algorithm(self, tag_records=None, db=None):
        """
        Return dict of the user's active tags categorized by past performance.
        The tag_records argument should be a list of dictionaries, each of
        which includes the following keys and value types:
            {'tag': <int>,
             'tlast_right': <datetime>,
             'tlast_wrong': <datetime>,
             'times_right': <float>,
             'times_wrong': <float>}
        The return value is a dict with the following keys and value types:
            {'cat1': [int, int ...],
             'cat2': [],
             'cat3': [],
             'cat4': []}
        TODO: Could this be done by a cron job or separate background process?
        TODO: Factor in how many times a tag has been successful or not
        TODO: Require that a certain number of successes are recent
        TODO: Look at secondary tags as well
        """
        db = db if db else current.db
        categories = {'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}
        tag_records = tag_records if tag_records else self.tag_records

        for record in tag_records:
            if not db.tags[record['tag']]:
                # TODO: send error email here
                continue
            lrraw = record['tlast_right']
            lwraw = record['tlast_wrong']
            lr = lrraw if not isinstance(lrraw, str) else parser.parse(lrraw)
            lw = lwraw if not isinstance(lwraw, str) else parser.parse(lwraw)
            rdur = self.utcnow - lr
            rwdur = lr - lw
            #print'cat2 if:'
            #print"record['times_right'] ", record['times_right'], '>= 20 (', record['times_right'] >= 20, ')'
            #print'and'
            #print'-------------------------------------------------------'
            #print'rdur.days ', rdur.days, '<', 'rwdur.days', rwdur.days, '> 1 (', rdur.days < rwdur.days > 1, ')'
            #print'or-----------------------------------------------------'
            #print'ratio ', self._get_ratio(record), '< 0.2 (', self._get_ratio(record) < 0.2, ')'
            #print'and'
            #printrdur.days, '<= 30 days (', rdur.days <= 30, ')'
            #print'or-----------------------------------------------------'
            #printself._get_avg(record['tag']), '>= 0.8 (', self._get_avg(record['tag']) >= 0.8, ')'
            #print'and'
            #print'rdur.days', rdur.days, '<= 30 days (', rdur.days <= 30, ')'

            # spaced repetition algorithm for promotion to
            # cat2? ======================================================
            if ((record['times_right'] >= 20) and  # at least 20 right
                (((rdur < rwdur) and  # delta right < delta right/wrong
                  (rwdur.days > 1)  # not within 1 day
                  ) or
                 ((self._get_ratio(record) < 0.2) and  # less than 1w to 5r total
                  (rdur.days <= 30)  # right in past 30 days
                  ) or
                 ((self._get_avg(record['tag']) >= 0.7) and  # avg score for week >= 0.7
                  (rdur.days <= 30)  # right in past 30 days
                  ))):
                #print'************** got to cat2'
                # cat3? ==================================================
                if rwdur.days >= 14:
                    # cat4? ==============================================
                    if rwdur.days > 60:
                        # long-term review? ===================================
                        if rdur > datetime.timedelta(days=180):
                            category = 'rev1'  # Not tried for 6 months
                        else:
                            category = 'rev4'  # Not due, delta > 60 days
                    else:
                        category = 'rev3'  # delta between 14 and 60 days
                else:
                    category = 'rev2'  # Not due but delta is 2 weeks or less
            else:
                category = 'rev1'  # Spaced repetition requires review

            categories[category].append(record['tag'])

        return categories

    def _introduce_tags(self, rank=None, db=None):
        """
        Add the next set of tags to cat1 in the user's tag_progress
        Returns a dictionary of categories identical to that returned by
        categorize_tags
        """
        db = current.db if not db else db
        rank = self.rank if rank is None else rank

        if rank in (None, 0):
            rank = 1
        else:
            rank += 1
        self.rank = rank

        newtags = [t['id'] for t in
                   db(db.tags.tag_position == rank).select().as_list()]
        #debug ... dont forget to take this out
        #newtags.append(82)
        #end of debug
        return newtags

    def _add_untried_tags(self, categories, rank=None, db=None):
        """Return the categorized list with any untried tags added to cat1"""
        db = current.db if not db else db
        rank = self.rank if not rank else rank

        left_out = []
        for r in range(1, rank + 1):
            newtags = [t['id'] for t in
                       db(db.tags.tag_position == r).select().as_list()]
            alltags = list(chain(*categories.values()))
            left_out.extend([t for t in newtags if t not in alltags])
        if left_out:
            categories['rev1'].extend(left_out)
        else:
            pass
        return categories

    def _fix_oldcats(self, oldcats, uid, bbrows=None):
        """
        Return categories with max levels fixed based on badges_begun rows.
        """
        db = self.db
        cnms = ['cat1', 'cat2', 'cat3', 'cat4']
        bbrows = bbrows if bbrows else db(db.badges_begun.name == uid
                                          ).select().as_list()
        bmax = {}
        for b in bbrows:
            mymax = len([k for k, v in b.iteritems() if k in cnms and v])
            bmax[b['tag']] = mymax
        for c, l in oldcats.iteritems():
            try:
                for tag in l:
                    if c in cnms and \
                            l in bmax.keys() and \
                            c[-1] != bmax[tag]:
                        oldcats[c].pop(l.index(tag))
                        oldcats['cat'.format(bmax[tag])].append(tag)
            except TypeError:  # because no list for that cat in oldcats
                pass
        return oldcats

    def _find_cat_changes(self, cats, oldcats, bbrows=None, uid=None):
        """
        Determine whether any of the categorized tags are promoted or demoted.
        """
        uid = self.user_id if not uid else uid
        if oldcats:
            demoted = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
            promoted = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
            oldcats = {k: v for k, v in oldcats.iteritems()
                       if k[:3] == 'cat' and k != 'cat1_choices'}  # facilitates demotion tasks
            oldcats = self._remove_dups(oldcats, self.rank)

            #copy oldcats into new new 'cats'
            # in preparation for finding diffs from rev1-4 and updating as
            # appropriate
            for k in oldcats:
                if (k in oldcats and oldcats[k]):
                    cats[k] = oldcats[k][:]
                else:
                    cats[k] = []

            new_tags = {'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}
            cnms = ['rev1', 'rev2', 'rev3', 'rev4']
            oldkeys = ['cat1', 'cat2', 'cat3', 'cat4']
            # TODO: cleaning up bad data; deprecate after finished
            oldcats = self._fix_oldcats(oldcats, uid, bbrows=bbrows)

            for cat, taglist in cats.iteritems():
                oldkey = 'cat{}'.format(cat[-1:])
                if taglist and (cat in cnms):
                    # Is tag completely new to this user?
                    oldvals = [v for v in oldcats.values() if v]
                    all_old_tags = list(chain.from_iterable(oldvals))
                    new_tags[cat] = [t for t in cats[cat] if t not in all_old_tags]

                    # was tag in a lower category before?
                    idx = oldkeys.index(oldkey)
                    was_lower = list(chain.from_iterable([oldcats[c] for c
                                                          in oldkeys[:idx]
                                                          if oldcats[c]]))
                    promoted[oldkey] = [t for t in cats[cat] if t in was_lower]

                    # was tag in a higher category before?
                    was_higher = list(chain.from_iterable([oldcats[c] for c
                                                           in oldkeys[idx + 1:]
                                                           if oldcats[c]]))
                    demoted[oldkey] = [t for t in taglist if t in was_higher]

            # remove promoted from old cat list and insert into higher cat list
            if any([k for k, v in promoted.iteritems() if v]):
                for tag in list(chain.from_iterable(promoted.values())):
                    catidx = [k for k, v in oldcats.iteritems()
                                if v and tag in v][0]
                    revidx = [k.replace('rev', 'cat') for k, v
                              in cats.iteritems()
                              if v and tag in v and k in cnms][0]
                    try:
                        if tag in cats[catidx]:
                            cats[catidx].remove(tag)
                            cats[revidx].append(tag)
                    except ValueError:
                        print traceback.format_exc()

            #add cats for new tags
            for k, v in new_tags.iteritems():
                if v and k in cnms:
                    catidx = k.replace('rev', 'cat')
                    cats[catidx].extend(v)

            return {'categories': cats,
                    'demoted': demoted if any([d for d in demoted.values()])
                               else None,
                    'promoted': promoted if any([p for p in promoted.values()])
                               else None,
                    'new_tags': new_tags if any([n for n in new_tags.values()])
                               else None}
        else:
            cats['cat1'] = cats['rev1'][:]
            #new_tags = cats['cat1'][:]
            new_tags = {'rev1': cats['rev1'][:], 'rev2': [], 'rev3': [],
                        'rev4': []}
            return {'categories': cats,
                    'demoted': None,
                    'promoted': None,
                    'new_tags': new_tags}

    def _clean_tag_records(self, record_list=None, db=None):
        """
        Find and remove any duplicate entries in record_list.
        This method is really safeguarding against faulty db updating in Walk.
        It should probably be deprecated, or should simply log a silent error
        when a duplicate is detected.
        """
        discrete_tags = set([t['tag'] for t in record_list])
        kept = []
        if len(record_list) > len(discrete_tags):
            for tag in discrete_tags:
                shortlist = record_list.find(lambda row: row.tag == tag)
                kept.append(shortlist[0].id)
                if len(shortlist) > 1:
                    for row in shortlist[1:]:
                        row.delete_record()
            record_list = record_list.find(lambda row: row.id in kept)


class Block(object):
    """
    An object representing a pending interruption in the flow of the game.
    The possible Block conditions are of two kinds. The first simply yield a
    step that can be returned by Path.get_step_for_prompt in lieu of the
    normally slated step:
        'redirect'
        'promoted'
        'new_tags'
        'slides'
        'quota_reached'
    The second category requires that the Block object be returned to Walk.ask()
    or Walk.reply() for a more involved response:
        'need to reply'
        'empty response'
    """

    def __init__(self, condition, kwargs=None):
        """
        Initialize a new Block object
        """
        self.condition = condition
        self.kwargs = kwargs
        # condition necessary for unit test
        try:
            current.sequence_counter += 1
        except AttributeError:
            current.sequence_counter = 1

    def make_step(self, condition):
        """Create correct Step subclass and store as an instance variable."""
        db = current.db
        step_classes = {'view_slides': 6,
                        'quota_reached': 7,
                        'new_tags': 8,
                        'promoted': 8,
                        'redirect': 9}
        step = db(db.steps.widget_type ==
                  step_classes[condition]).select(orderby='<random>').first()
        mystep = StepFactory().get_instance(step_id=step['id'],
                                            kwargs=self.kwargs)
        current.sequence_counter += 1
        return mystep

    def get_condition(self):
        """Return a string representing the condition causing this block."""
        return self.condition

    def get_step(self):
        """Return the appropriate step for the current blocking condition"""
        step = self.make_step(self.get_condition())
        return step


class Exception_Bug(object):
    """
    Handles the creation of exception
    reports for paideia.
    Joseph Boakye <jboakye@bwachi.com> Oct 12, 2014
    """
    def __init__(self, exception_data):
        """
        Initialize a Bug object for generating bug reports on specific user
        interactions.
        """
        db = current.db
        try:
            db.exceptions.insert(step=exception_data['step_id'],
                           in_path=exception_data['path_id'],
                           map_location=exception_data['loc'],
                           user_response=exception_data['answer'],
                           log_id=exception_data['log_id'],
                           score=exception_data['score'])
            db.commit()
        except Exception:
            print traceback.format_exc(5)
