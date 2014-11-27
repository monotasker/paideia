#! /usr/bin/python
# -*- coding: utf-8-*-
from gluon import current, redirect
from gluon import IMG, URL, SQLFORM, SPAN, DIV, UL, LI, A, Field, P, HTML
from gluon import I
from gluon import IS_NOT_EMPTY, IS_IN_SET

from inspect import getargvalues, stack
import traceback
from copy import copy
from copy import deepcopy
from itertools import chain
from random import randint, randrange
import re
import datetime
from dateutil import parser
from pytz import timezone
import pickle
from plugin_utils import flatten
from plugin_widgets import MODAL
from pprint import pprint
from paideia_utils import simple_obj_print
from paideia_utils import Paideia_Debug

#True = debug to screen, False is normal
#current.paideia_DEBUG_MODE is set in Walk::init
# TODO: move these notes elsewhere
"""
The following files exist outside the paideia app folder and so need to be
watched when upgrading web2py:
- web2py/routes.py
"""

"""
Changes by Joseph Boakye ... Sep 21, 2014
added self as first argument to this function
    def _clean_tag_records(self,record_list=None, db=None):
update_tag_record was completely redone
new standalone function simple_object_print  to#printsimple objects
"""


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
        #also uncomment  paideia_debug.do_print stmts
        #-----------------------------------------------
        self.DEBUG_MODE = False
        current.paideia_DEBUG_MODE = self.DEBUG_MODE
        current.paideia_debug = Paideia_Debug()
        current.sequence_counter = 0
        #-----------------------------------------------
        db = current.db if not db else db
        # TODO: fix redundant db call here
        self.response_string = response_string
        # TODO: move retrieval of data to user init so it's not duplicated when
        # just retrieving existing User.
        self.user = self._get_user(userdata=userdata,
                                   tag_records=tag_records,
                                   tag_progress=tag_progress,
                                   new_user=new_user)
        #JOB .... oct 24, 2014

        #let self carry Walk object so we can
        # TODO is record_id necessary?
        self.record_id = None  # stores step log row id after db update
        #JOB ... oct 22, 2014

    def _new_user(self, userdata, tag_records, tag_progress):
        '''Return a new User object for the currently logged in user.'''
        #current.paideia_debug.do_print({'userdata':userdata,
                                        #'tag_records':tag_records,
                                        #'tag_progress': tag_progress},"_new_user called:before")
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
        #current.paideia_debug.do_print({'userdata':userdata,
                                        #'tag_records':tag_records,
                                        #'tag_progress': tag_progress},"_new_user called:after")
        return User(userdata, tag_records, tag_progress,blocks=[]) #TODO: find out where the mysterious blocks are coming from

    def _get_user(self, userdata=None, tag_records=None,
                  tag_progress=None, new_user=None):
        '''
        Initialize or re-activate User object.
        All named arguments are necessary.
        '''
        #current.paideia_debug.do_print({'userdata':userdata,
                                        #'tag_records':tag_records,
                                        #'tag_progress': tag_progress,
                                        #'new_user': new_user}," Brisbane in _get_user")
        auth = current.auth
        db = current.db
        try:  # look for user object already on this Walk
            assert (self.user) and new_user is None
        except (AttributeError, AssertionError):  # because no user yet on this Walk
            try:
                #current.paideia_debug.do_print('sd = db(db.session_data.name'," Brisbane in _get_user trying to get sd")
                sd = db(db.session_data.name ==
                        auth.user_id).select().first()
                if sd:
                    self.user = pickle.loads(sd['other_data'])
                else:
                    self.user = None
                assert self.user
                assert self.user.is_stale() is False
                assert not new_user
            except (KeyError, TypeError):  # Problem with session data
                print traceback.format_exc(5)
                #current.paideia_debug.do_print({'trace': traceback.format_exc(5)}," Brisbane in exception for _get_user")
                self.user = self._new_user(userdata, tag_records, tag_progress)
            except (AssertionError, AttributeError):  # user stale or block
                #current.paideia_debug.do_print('self.user = self._new_user(userdata, tag_records, tag_progress)'," Brisbane in _get_user ")
                self.user = self._new_user(userdata, tag_records, tag_progress)
        if isinstance(self.user.quota, list):
            self.user.quota = self.user.quota[0]
        return self.user

    def start(self, localias, response_string=None, path=None, repeat=None,
              step=None, set_blocks=None, recategorize=None,pre_bug_step_id=None):
        """
        JOB ... oct 18, 2014 ... added bug_step_id to signature
        Issue the correct method for this interaction and return the result.
        This is the top-level interface for the Paideia module, to be called by
        the controller. The method decides whether we're starting a new step or
        responding to one in-process.
        """
        #print'\nIN START'
        #debug
        ####current.paideia_debug.do_print(localias,"localias")
        ####current.paideia_debug.do_print(response_string,"response_string")
        ####current.paideia_debug.do_print(path,"path")
        ####current.paideia_debug.do_print(repeat,"repeat")
        ####current.paideia_debug.do_print(set_blocks,"set_blocks")
        ####current.paideia_debug.do_print(recategorize,"recategorize")

        #JOB ... oct 22, 2014
        result = None

        try:
            while True:
                if response_string:
                    #debug
                    ####current.paideia_debug.do_print("response string is good","message")
                    ##current.paideia_debug.do_print("reply","calling Walk.reply")
                    result =  self.reply(localias=localias,
                                      response_string=response_string,
                                      pre_bug_step_id=pre_bug_step_id)
                if result: break
                #debug
                ##current.paideia_debug.do_print("ask 1","calling Walk.ask")
                result =  self.ask(localias=localias,
                                path=path,
                                repeat=repeat,
                                set_blocks=set_blocks,
                                recategorize=recategorize,
                                step=step)
                break
        except Exception:
            print traceback.format_exc(5)
            self.clean_user()  # get rid of any problem path data
            #debug
            ####current.paideia_debug.do_print("ask 2","message")
            result =  self.ask(localias=localias, path=path, step=step)
            ####current.paideia_debug.do_print("ask 2 finished","message")
            #return excp_ask
        if self.DEBUG_MODE:
            result['paideia_debug'] = '<div>' + current.paideia_debug.data + '</div>'
        else:
            #TODO: strip off html tags
            print current.paideia_debug.data
            result['paideia_debug'] = ''
        #debug
        #print result
        return result

    def clean_user(self):
        """
        In case of irrecoverable conflict in user data, remove all path/steps.
        """
        #print'\n error, cleaning user--------------------------------------\n'
        user = self._get_user()
        user.path = None
        self._store_user(user)

    def ask(self, localias, path=None, repeat=None,
            step=None, set_blocks=None, recategorize=None):
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
        p = category = redir = pastquota =  None
        loc = prev_loc = prev_npc = None
        s = newloc_id = error_string = None
        prompt = None
        while True:
            ##current.paideia_debug.do_print((set_blocks,self.user.name), "Marseilles-ask")
            #print'STARTING WALK.ASK---------------------------------------'
            user = self.user
            #current.paideia_debug.do_print({'user.blocks':[b.get_condition() for b in user.blocks]}, "Brisbane- the user of ask")
            #print'Tag progress is------------------'
            ##pprint(user.tag_progress)
            # allow artificial setting of blocks during interface testing
            if set_blocks:
                for c, v in set_blocks.iteritems():
                    myargs = {n: a for n, a in v.iteritems()}
                    #current.paideia_debug.do_print({c: v}, "+-+-+- already existing set_blocks")
                    ##current.paideia_debug.do_print(({'sc': current.sequence_counter},{'c':c},{'myargs': myargs}), "Marseilles- calling user.setblock in aask")
                    current.sequence_counter += 1
                    user.set_block(c, kwargs=myargs)
            username = user.get_name()
            tag_progress,promoted,new_tags,demoted = self._set_blocks()
            #current.paideia_debug.do_print({'promoted': promoted,'new_tags:': new_tags,'demoted':demoted}, "Brisbane- after calling set_blocks")
            #JOB ... moved from reply ... oct 23, 2014
            if (promoted or new_tags or demoted):
            #if (True):
                ##current.paideia_debug.do_print({'promoted': promoted,'new_tags:': new_tags,'demoted':demoted}, "Marseilles- calling _record_cats")
                assert self._record_cats(tag_progress,
                             promoted,
                             new_tags,demoted)
                #current.paideia_debug.do_print({'tag_progress': tag_progress}, "Brisbane-tag_progress after _record_cats")
                #current.paideia_debug.do_print({'user.tag_progress': user.tag_progress}, "Brisbane-user.tag_progress after _record_cats")
            loc = Location(localias)
            #current.paideia_debug.do_print({'loc':loc.get_name(), 'localias': localias}, "Brisbane- loc and localias in ask")
            prev_loc = user.set_location(loc)
            prev_npc = user.get_prev_npc()

            p, category, redir, pastquota = user.get_path(loc, pathid=path,
                                                          repeat=repeat)
            #current.paideia_debug.do_print({'p':p.get_id(), 'category': category, 'redir':redir, 'pastquota':pastquota}, "Brisbane-after user.getpath is called in ask")

            if (not p): break #no paths for this location for this category

            user.active_cat = category
            if redir:
                #current.paideia_debug.do_print(({'sc': current.sequence_counter},{'redir':redir}), "Brisbane- calling user.setblock for redir in aask")
                current.sequence_counter += 1
                user.set_block('redirect', kwargs={'next_loc': redir})
            if pastquota:
                #current.paideia_debug.do_print(({'sc': current.sequence_counter},{'user.quota': user.quota}), "Brisbane- calling user.setblock for quota in aask")
                current.sequence_counter += 1
                user.set_block('quota_reached', kwargs={'quota': user.quota})

            s, newloc_id,error_string = p.get_step_for_prompt(loc, repeat=repeat)



            if newloc_id:
                #current.paideia_debug.do_print(({'sc': current.sequence_counter},{'newloc_id':newloc_id}), "Brisbane- calling user.setblock for newloc_id in aask")
                current.sequence_counter += 1
                user.set_block('redirect', kwargs={'next_loc': newloc_id})

            # TODO: make sure 'new_tags' is returned before 'view_slides'
            #current.paideia_debug.do_print(({'sc': current.sequence_counter}), "Brisbane- checking for blocks in ask")
            current.sequence_counter += 1
            block = user.check_for_blocks()
            if block:
                s = block.get_step()

            npc = s.get_npc(loc, prev_npc, prev_loc)
            user.set_npc(npc)

            if not user.blocks:
                user.clear_block_records()
            prompt = s.get_prompt(loc, npc, username, user_blocks_left = True if user.blocks else False)
            #print'before sending to view------------------------'

            #debug
            ####current.paideia_debug.do_print(user.completed_paths,'user.completed_paths')
            extra_fields = {'completed_count': user.get_completed_paths_len(),
                            'category': category,
                            'pid': p.get_id()
                            }
            #debug
            ####current.paideia_debug.do_print(extra_fields,'extra_fields')

            prompt.update(extra_fields)

            p.end_prompt(s.get_id())  # send id to tell whether its a block step
            self._store_user(user)
            #debug
            ####current.paideia_debug.do_print('returning from ask','msg')
            break #from utility while loop


        #propagating errors and alerting user instead of crashing
        if(not p): # no path in this location for this category
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
                      'pid': 0
                      }
            return prompt
        if(error_string):
            Exception_Bug({'log_id':0,
                                                   'path_id':p.get_id(),
                                                   'step_id':s.get_id(),
                                                   'score':0,
                                                   'answer':error_string,
                                                   'loc':user.loc.get_alias()})
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
                      'pid': p.get_id()
                      }
            return prompt

        return prompt #good prompt

    def _set_blocks(self, user=None):
        """
        """
        user = self.user if not user else user
        tag_progress, promoted, new_tags, demoted = user.get_categories(user_id=user.get_id())
        #current.paideia_debug.do_print({'promoted':promoted,
                                        #'new_tags':new_tags,
                                        #'demoted': demoted},"-----_set_blocks called")

        if new_tags:
            #current.paideia_debug.do_print('new_tags in effect','_set_blocks')
            # setting order here should make new_tags step come up first
            user.set_block('new_tags', kwargs={'new_tags': new_tags,
                                               'promoted': promoted})
            user.set_block('view_slides', kwargs={'new_tags': new_tags})
        if promoted:
            #current.paideia_debug.do_print('promoted in effect','_set_blocks')
            user.set_block('new_tags', kwargs={'new_tags': new_tags,
                                               'promoted': promoted})
        return tag_progress, promoted, new_tags,demoted

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
        #print'\n================================'
        ##current.paideia_debug.do_print({'response_string':response_string}, "Marseilles- reply")
        print'\nSTART OF Walk.reply()'
        #debug
        ##current.paideia_debug.do_print((path,step), "orpington-reply called with path and step:")
        user = self._get_user()
        loc = user.get_location()
        p, cat = user.get_path(loc)[:2]

        #current.paideia_debug.do_print("ask 3","message")

        s = p.get_step_for_reply()
        #print'\n 00000001'
        if (not response_string) or re.match(response_string, r'\s+'):
            #debug
            ###cask(urrent.paideia_debug.do_print("ask 3","message")
            #return self.ask()  # TODO: will this actually re-prompt the same step?
            return None
        prompt = s.get_reply(response_string)  # loc and npc stored on step

        """ save inside get_categories ..  JOB ... oct 23, 2014
        assert self._record_cats(user.tag_progress,
                                 user.promoted,
                                 user.new_tags)
        """
        #current.paideia_debug.do_print({'user.tag_records':user.tag_records},"Brisbane - user.tag_records before calling _record_step")
        self.record_id = self._record_step(user.get_id(),
                                           p.get_id(),
                                           s.get_id(),
                                           prompt['score'],
                                           prompt['times_right'],
                                           prompt['times_wrong'],
                                           user.tag_records,
                                           s.get_tags(),
                                           response_string)
        ##current.paideia_debug.do_print(response_string, "halifax ----response string in reply ----")
        ##current.paideia_debug.do_print(prompt, "halifax ----prompt in reply ----")
        ##current.paideia_debug.do_print(pre_bug_step_id, "halifax ---- pre bug step id in reply ----")
        prompt['bugreporter'] = BugReporter().get_reporter(self.record_id,
                                                           p.get_id(),
                       pre_bug_step_id if pre_bug_step_id  else s.get_id(),
                                                           prompt['score'],
                                                           response_string,
                                                           user.loc.get_alias())
        prompt['completed_count'] = user.get_completed_paths_len()
        prompt['pid'] = p.get_id()
        prompt['category'] = cat
        prompt['loc'] = loc.get_alias()

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
        JOB: added db.commit() after db.badges_begun.update_or_insert
        """
        db = current.db
        now = datetime.datetime.utcnow()
        try:
            for cat, lst in promoted.iteritems():
                if lst:
                    for tag in lst:
                        data = {'name': user_id,
                                'tag': tag,
                                cat.replace('rev','cat'): now}
                        #current.paideia_debug.do_print(({'data': data}), "Marseilles- data being recorded in _record_promotion")
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
        #current.paideia_debug.do_print(({'tag_progress': tag_progress},{'promoted': promoted}, {'new_tags': new_tags},{'demoted': demoted}), "Marseilles- record_cats called")
        db = current.db if not db else db
        auth = current.auth
        uid = self.user.get_id()
        if uid == auth.user_id:
            # TODO: make sure promoted and new_tags info passed on correctly
            # combine promoted and new_tags for recording purposes

            #JOB ... oct 30, 2014... commenting out
            #if promoted:
            #    promoted['cat1'] = new_tags
            #elif new_tags:
            #    promoted = {'cat1': new_tags}

            #else:
            #    promoted is None
            if promoted:
                #debug dont forget to delete
                #promoted['cat1'].append(72)
                #promoted['cat3']= [18]
                #end debug
                ##current.paideia_debug.do_print(({'promoted before record': promoted}), "Marseilles- record_cats called")
                assert self._record_promotions(promoted, uid)
                ##current.paideia_debug.do_print(({'promoted_after record': promoted}), "Marseilles- record_cats called")
            if demoted:
                ##current.paideia_debug.do_print(({'demoted before record': demoted}), "Marseilles- record_cats called")
                assert self._record_demotions(demoted,uid)
                ##current.paideia_debug.do_print(({'demoted after record': demoted}), "Marseilles- record_cats called")
            if new_tags:
                #current.paideia_debug.do_print(({'new_tags': new_tags}), "Marseilles- recording new_tags")
                #assert self._record_promotions({'cat1':new_tags}, uid)
                assert self._record_promotions(new_tags, uid)
            try:
                tag_progress['name'] = uid
                condition = {'name': uid}
                #pprint(tag_progress)

                #debug ... dont forget to take this out!
                #tag_progress['cat2'].append(82)
                #debug
                #current.paideia_debug.do_print(({'tag_progres before update': tag_progress}), "Marseilles- tag_progress")
                db.tag_progress.update_or_insert(condition, **tag_progress)
                db.commit()
                mycount = db(db.tag_progress.name == uid).count()
                assert mycount == 1  # ensure there's never a duplicate
                # TODO: eliminate check by making name field unique
            except Exception:
                #current.paideia_debug.do_print(tag_progress, "el paso- this exception in _record_cats is not expected")
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
        #debug
        #print'in update_tag_secondary'
        #printdb._lastsql
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
        JOB (jboakye@bwachi.com) Sept 09, 2014
        Adding step_id as arg before now. Adds the last step id, may be a validation
        issue without a valid step_id
        """

        SQL_TEMPLATE_UPDATE_TAG_RECORDS = "\
        UPDATE tag_records \
        SET    %s = coalesce(%s,0) + %f \
              ,%s = '%s' \
        ,step = %d \
        WHERE  name = %d \
        AND    tag =  %d; "

        now = datetime.datetime.utcnow() if not now else now
        ###current.paideia_debug.do_print(oldrec,"oldrec d---------------------------")
        oldrec = oldrec if not isinstance(oldrec, list) else oldrec[0]  # FIXME
        #debug ... JOB
        #print'oldrec new ---------------------------'
        ###current.paideia_debug.do_print(oldrec,"oldrec new---------------------------")
        #printtype(oldrec)
        ###current.paideia_debug.do_print(got_right,"gotright")
        ###current.paideia_debug.do_print(tright,"tright")
        ###current.paideia_debug.do_print(twrong,"twrong")
        ###current.paideia_debug.do_print(score,"score")
        ###current.paideia_debug.do_print(tag,"tag")
        ###current.paideia_debug.do_print(user_id,"user_id")
        ###current.paideia_debug.do_print(step_id,"step_id")

        tlright = now
        tlwrong = now
        db = current.db

        #we are going to grab the old rec from the dbase until we find out
        #why it is not present here sometimes
        #always grab a new one anyway
        use_this_oldrec = None
        try:
            if not use_this_oldrec:
                #debug
                #print'houston, we have a null oldrec'
                use_this_oldrec = db((db.tag_records.tag == tag) &
                            (db.tag_records.name == user_id)
                            ).select().first().as_dict()
        except Exception:
            use_this_oldrec = None
        ###current.paideia_debug.do_print(use_this_oldrec,"use this oldrec beta")

        newdata = {'name': user_id,
                   'tag': tag,
                   'times_right': tright,
                   'times_wrong': twrong,
                   'tlast_right': tlright,
                   'tlast_wrong': tlwrong,
                    'step': step_id}
        if use_this_oldrec:
            sql_string = None
            if got_right:
                sql_string = SQL_TEMPLATE_UPDATE_TAG_RECORDS % ('times_right','times_right',
                                     tright, 'tlast_right', now, step_id,user_id,tag)
            else:
                sql_string = SQL_TEMPLATE_UPDATE_TAG_RECORDS % ('times_wrong','times_wrong',
                                     twrong, 'tlast_wrong', now, step_id,user_id,tag)
            #debug
            #print'sql string is:' + sql_string
            rslt = db.executesql(sql_string)
        else: #new one
            db.tag_records.insert(**newdata)
        db.commit()
        #debug
        #print'accra'
        #printdb._lastsql
        ###current.paideia_debug.do_print(db._timings,"db timings")
        #print'end accra'
        tagrec = db((db.tag_records.tag == tag) &
                    (db.tag_records.name == user_id)
                    ).select()
        tagrec = tagrec.first()
        return tagrec.id

    def _record_step(self, user_id, step_id, path_id, score, raw_tright,
                     raw_twrong, old_trecs, taglist, response_string,
                     now=None):
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
        mynow = datetime.datetime.utcnow() if not now else now
        db = current.db
        # TODO: Store and roll back db changes if impersonating
        # TODO: should the threshold here be less than 1 for 'right'?
        # made change JOB ... got_right seems to be sending the opposite of what it should be -sept 21 2014
        #fix: if it is make it slightly higher and change the comparison sign
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
                    'user_response': response_string}  # time automatic in db
        log_record_id = db.attempt_log.insert(**log_args)
        db.commit()
        #JOB ... oct 25, 2014 ... only add to completed paths if got right
        self.user.complete_path(got_right)
        return log_record_id

    def _store_user(self, user, db=None):
        """
        Store the current User object (from self.user) in session.user

        If successful, returns an integer representing the successfully
        added/updated db row. If unsuccessful, returns False.
        """
        db = current.db if not db else db

        # TODO: Store and roll back db changes if impersonating
        #  if auth.is_impersonating():  # shadowing another user
        #  return False  # don't record in db
        #  else:
        try:
            myuser = pickle.dumps(user)
            rownum = db.session_data.update_or_insert(db.session_data.name == user.get_id(),
                                                      name=user.get_id(),
                                                      other_data=myuser)
            db.commit()
            return rownum
        except Exception:
            print traceback.format_exc(5)
            return False


class Location(object):
    """
    Represents a location in the game world.
    """

    def __init__(self, alias, db=None):
        """Initialize a Location object."""
        db = current.db if not db else db
        self.data = db(db.locations.loc_alias == alias).select().first()

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
        self.data = db.npcs(id_num)
        # get image here so that db interaction stays in __init__ method
        self.image_id = self.data.npc_image
        self.image = db.images[self.image_id].image

    def get_id(self):
        """return the database row id of the current npc"""
        return self.id_num

    def get_name(self):
        """return the name of the current npc"""
        return self.data.name

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
        locs = [l for l in self.data.map_location
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
        return self.data.notes


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
                          if n == self.prev_npc.get_id()
                          and self.location.get_id() in n.get_locations()]
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

        #debug
        #print 'halifax ---- get_reporter called with step_id: ', step_id
        #print 'halifax ---- get_reporter called with response_string: ', response_string
        response_string = response_string.decode('utf-8')
        response_string = response_string.encode('utf-8')
        #changing bug_id field to bug_step_id ... JOB ... oct 03, 2014
        vardict = {'answer': response_string,
                   'loc_id': loc_id,
                   'log_id': record_id,
                   'path_id': path_id,
                   'score': score,
                   'bug_step_id': step_id}
        c = P('Think your answer should have been correct? ',
              A('click here',
                I(_class='icon-bug'),
                _class='bug_reporter_link btn btn-danger',
                _href=URL('paideia', 'creating', 'bug.load', vars=vardict),
                cid='bug_reporter'),
              ' to submit a bug report. You can find the instructor\'s ',
              'response in the "bug reports" tab of your user profile.')

        br = MODAL('Something wrong?',
                   'Did you run into a problem?',
                   c,
                   trigger_type='link',
                   trigger_classes='bug_reporter',
                   id='bug_reporter_modal')

        return br


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
        """
        db = current.db
        return [l for l in self.data['locations']
                if db.locations[l].loc_active is True]

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
        rslt = False;
        while True:
            if not self.is_valid:
                break
            if self.get_locations():
                rslt =  True
                break
            break
        #debug
        ##current.paideia_debug.do_print('step_id:' + str(self.get_id()) + ' result:' + ('True' if rslt else 'False'), "tewksbusy: has locations")
        return rslt



    def _get_slides(self):
        """
        Return a dictionary of info on slide decks relevant to this step.

        The keys are deck ids, while the values are the deck names (as
        strings). If this step has no associated slides, returns None.

        """
        db = current.db
        tags = db(db.tags.id.belongs(self.data['tags'])).select()
        if tags:
            try:
                decks = {d.id: d.deck_name
                        for t in tags
                        for d in t.slides
                        if t.slides}
                return decks
            except:
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
            db = current.db
            aud_row = db.audio(self.data['prompt_audio'])
            audio = {'title': aud_row['title'],
                     'mp3': aud_row['clip'],
                     'ogg': aud_row['clip_ogg'] if aud_row['clip_ogg'] else None}
            return audio
        else:
            return None

    def get_prompt(self, location, npc, username, raw_prompt=None,user_blocks_left=False):
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
                  'pre_bug_step_id':self.get_id()}
        # TODO: this is a temporary hack for bad data
        self.npc = npc if not isinstance(npc, tuple) else npc[0]
        prompt['npc_image'] = self.npc.get_image()

        return prompt

    def _make_replacements(self, raw_prompt, username, reps=None, appds=None):
        """
        Return the provided string with tokens replaced by personalized
        information for the current user.
        """
        #print'raw_prompt ======================================'
        #printraw_prompt
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

        #print'new string ====================================='
        #printnew_string
        return {'newstr':newstr}

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
                    #debug
                    current.paideia_debug.do_print("randrange error permitted", '-boston-')
                    #print traceback.format_exc(5)
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
                        current.paideia_debug.do_print("randrange error NOT permitted", '-new york-')
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


class StepContinue(Step):
    """
    An abstract subclass of Step that adds a 'continue' button to the responder.
    """
    def get_prompt(self, loc, npc, username,raw_prompt=None,user_blocks_left=True):
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
    def get_prompt(self, loc, npc, username, raw_prompt=None,user_blocks_left=True):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        prompt = super(StepRedirect, self).get_prompt(loc, npc, username)
        #JOB ... oct 23, 2014 ... be forced to go back to the map
        #if redirect is the only block
        #if you continue, bad things can happen in the background
        #err ok not sure
        #if this is the only block, popping it from User::blocks will leave
        #User::blocks empty
        ##current.paideia_debug.do_print({'user_blocks_left':user_blocks_left},"Message from StepRedirect::get_prompt")
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
        return {'newstr':newstr}


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
        return {'newstr':newstr}


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

        new_tags = kw['new_tags'] if ('new_tags' in kw.keys()
                                      and kw['new_tags']) else None
        promoted = kw['promoted'] if ('promoted' in kw.keys()
                                      and kw['promoted']) else None
        #print'new tags:', new_tags, 'promoted', promoted
        #current.paideia_debug.do_print({'kw':kw},"_make_replacements called")


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
                        if bname: bname =  bname[0]
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
                    ranknum = int(rank.replace('rev', ''))
                    label = ranks[ranknum - 1]
                    for l in lst:
                        bname = [row['badge_name'] for row in prom_records
                                if row['tag'] == l]
                        if bname: bname =  bname[0]
                        else: bname = 'tag {}(no name)'.format(l)
                        line = '- {} {}\r\n'.format(label, bname)
                        prom_rep += line
        appds['[[promoted_list]]'] = prom_rep


        #print'reps are ==================================================='
        #pprint(reps)
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
            deckurl = URL('listing', 'slides.html', args=[row['id']])
            slides.append('- [{} {}]'.format(row['deck_name'], deckurl))
        slides = '\n'.join(slides)

        # collect replacements
        appds = {'[[slide_list]]': slides}
        newstr = (super(StepViewSlides, self
                       )._make_replacements(raw_prompt, username, appds=appds))['newstr']
        return {'newstr': newstr}


class StepText(Step):
    """
    A subclass of Step that adds a form to receive user input and evaluation of
    that input. Handles only a single string response.
    """

    def get_prompt(self, location, npc, username, raw_prompt=None,user_blocks_left=True):
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
                               Field('pre_bug_step_id','string', readable=False, writable=False),
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

    def _regularize_greek(self, user_response):
        """
        Replaces identical looking Latin characters in Greek words with Greek.
        """
        equivs = {'A': 'Α',  # the keys here are latin characters and
                  'B': 'Β',  # the values are unicode Greek, even though
                  'E': 'Ε',  # they may (depending on the font) look the same.
                  'H': 'Η',
                  'I': 'Ι',
                  'i': 'ι',
                  'K': 'Κ',
                  'M': 'Μ',
                  'N': 'Ν',
                  'v': 'ν',
                  'O': 'Ο',
                  'o': 'ο',
                  'P': 'Ρ',
                  'T': 'Τ',
                  'u': 'υ',
                  'X': 'Χ'}
        user_response = user_response.decode('utf8')
        words = user_response.split(' ')
        Latinchars = re.compile(u'[\u0041-\u007a]|\d', re.U)
        Greekchars = re.compile(u'[\u1f00-\u1fff]|[\u0370-\u03ff]', re.U)
        for idx, word in enumerate(words):
            Gklts = [l for l in word if re.match(Greekchars, l)]
            Latlts = [l for l in word if re.match(Latinchars, l)]
            if Gklts and Latlts and len(Gklts) > len(Latlts):
                for ltr in word:
                    if ltr in equivs.keys():
                        words[idx] = word.replace(ltr, equivs[ltr].decode('utf8'))
        newresp = ' '.join(words)
        return newresp.encode('utf8')

    def _strip_spaces(self, user_response):
        """
        Remove leading, trailing, and multiple internal spaces from string.
        """
        while '  ' in user_response:  # remove multiple inner spaces
            user_response = user_response.replace('  ', ' ')
        user_response = user_response.strip()  # remove leading and trailing spaces
        return user_response

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
        user_response = self._strip_spaces(user_response)
        #user_response = self._regularize_greek(user_response)  FIXME: this isn't working on live site
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

            if re.match(regex1, makeutf8(user_response)):
                score = 1
                reply = "Right. Κάλον."
            elif re.match(responses['response1'], (user_response + '.'), re.I | re.U):
                score = 0.9
                reply = "Οὐ Κάκον. You're very close. Just remember to put a " \
                        "period on the end of a full clause."
            elif re.match(responses['response1'], (user_response + '?'), re.I | re.U):
                score = 0.9
                reply = "Οὐ Κάκον. You're very close. Just remember to put a " \
                        "question mark on the end of a question."
            elif user_response[-1] in ['.', ',', '!', '?', ';'] and \
                    re.match(responses['response1'], user_response[:-1], re.I | re.U):
                score = 0.9
                reply = "Ού κάκον. You're very close. Just remember not to put " \
                        "a final punctuation mark on your answer if it's not a " \
                        "complete clause"
            elif len(responses) > 1 and re.match(responses['response2'],
                                                 user_response, re.I | re.U):
                score = 0.5
                #  TODO: Get this score value from the db instead of hard
                #  coding it here.
                reply = "Οὐ κάκον. You're close."
                #  TODO: Vary the replies
            elif len(responses) > 2 and re.match(responses['response3'],
                                                 user_response, re.I | re.U):
                #  TODO: Get this score value from the db instead of hard
                #  coding it here.
                score = 0.3
                reply = "Οὐ κάκον. You're close."
            else:
                score = 0
                reply = "Incorrect. Try again!"

            # Set the increment value for times wrong, depending on score
            if score < 1:
                times_wrong = 1
                times_right = 0
            else:
                times_wrong = 0
                times_right = 1

        # Handle errors if the student's response cannot be evaluated
        except re.error:
            exception_msg = 'these are the responses for a step having errors in evaluation: ' + str(responses)  + 'user response is:' + user_response
            Exception_Bug({'log_id':0,
                                       'path_id':0,
                                       'step_id':0,
                                       'score':0,
                                       'answer':exception_msg,
                                       'loc':0})
            #current.paideia_debug.do_print({'user_response':user_response,
                                         #'responses':responses},"error in StepEvaluator::get_eval")
            # FIXME: is there still a view for this?
            #debug
            #redirect(URL('index', args=['error', 'regex']))
            reply = 'Oops! I seem to have encountered an error in this step.'

        tips = self.tips  # TODO: customize tips for specific errors

        return {'score': score,
                'times_wrong': times_wrong,
                'times_right': times_right,
                'reply': reply,
                'user_response': user_response,
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

    def get_id(self):
        """Return the id of the current Path object."""
        return self.path_dict['id']

    def   _prepare_for_prompt(self):
        """ move next step in this path into the 'step_for_prompt' variable"""
        try:
            stepcount = len(self.steps)
            if stepcount < 1:  # to bounce back after cleaning User
                # TODO: Does this cause problems?
                self._reset_steps()

                #added by JOB ... sept 22, 2014, step_for_prompt needs to be set after reset
                if self.steps:
                    next_step = self.steps.pop(0)
                    self.step_for_prompt = next_step
                ####current.paideia_debug.do_print("_prepare_for_prompt:stepcount < 1","message")
                ####current.paideia_debug.do_print(self.step_for_prompt, "step_for_promt in _prepare_for_prompt:stepcount < 1")
                return True
            else:
                ####current.paideia_debug.do_print(len(self.steps),"in _prepare_for_prompt: ', len(self.steps), 'steps remain'")
                #print'in _prepare_for_prompt: ', len(self.steps), 'steps remain'
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

    def  _reset_steps(self):
        """
        Return all completed steps to the self.steps list.

        Intended to prepare for repeating an already-completed step.
        """
        if self.completed_steps:
            self.steps = copy(self.completed_steps)
            self.completed_steps = []
        if len(self.steps) == 0:
            #changed by JOB ... sept 22, 2014 ... get_steps takes no args
            #self.steps = self.get_steps(self.username)
            self.steps = self.get_steps()
            assert len(self.steps) > 0
        ####current.paideia_debug.do_print(self.steps,"in _reset_steps, this is self.steps")
        return True

    def get_step_for_prompt(self, loc, repeat=None):
        """
        Find the next unanswered step in the current path and return it.
        If the selected step cannot be performed at this location, return a
        Block object instead.
        """
        if repeat:
            assert self._reset_steps()

        # make sure controller hasn't skipped processing an earlier step's reply
        # if self.step_for_reply:
        # self.step_for_prompt = copy(self.step_for_reply)
        # self.step_for_reply = None

        # get step if there isn't already one from redirect
        if not self.step_for_prompt:
            assert self._prepare_for_prompt()
        mystep = self.step_for_prompt
        #debug
        ####current.paideia_debug.do_print(mystep, "mystep")

        next_loc = None
        error_string = None
        this_step_id = None
        goodlocs = mystep.get_locations()
        ##current.paideia_debug.do_print(goodlocs, "philadelphia - goodlocs")
        if not loc.get_id() in goodlocs:
            try:
                this_step_id = mystep.get_id()
                next_loc = goodlocs[randrange(len(goodlocs))]
            except ValueError:
                error_string = 'Step: ' + (str(this_step_id) if this_step_id else  "can't get step id") + " possible empty location - tag:philadelphia"
                current.paideia_debug.do_print(error_string + "randrange error NOT permitted", '-philadelpha-')
                print traceback.format_exc(5)
        else:
            mystep.loc = loc  # update location on step

        return (mystep, next_loc, error_string)

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
        #debug
        ##current.paideia_debug.do_print(self.categories, "boise-- self.categories in PathChooser::__init__")
        self.rank = tag_progress['latest_new']
        db = current.db if not db else db
        self.loc_id = loc_id
        self.completed = paths_completed
        self.CONSTANT_MOD_CAT = 20
        self.CONSTANT_USE_CAT = 'cat1'
        self.CONSTANT_USE_REV = 'rev1'
        self.just_cats = tag_progress['just_cats']
        self.all_cat = tag_progress['all_cat1']   #all_cat1 in dbase => all_cat
        self.tag_progress = tag_progress
        #debug
        ##current.paideia_debug.do_print(self, "boise-- all of self  in PathChooser::__init__")
    def _set_pathchooser_rank(self,tag_progress=None,given_rank=0):
        if (tag_progress and 'latest_new' in tag_progress and tag_progress['latest_new']):
            self.rank = tag_progress['latest_new']
        else: self.rank = given_rank



    def _order_cats(self):
        """
        Choose a category to prefer in path selection and order categories
        beginning with that number.

        Returns a list with four members including the integers one-four.
        """
        # TODO: Look at replacing this method with scipy.stats.rv_discrete()

        """
        cat = randint(1, 10)
        cat = (cat%4) + 1
        """

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

        #debug
        ##current.paideia_debug.do_print(cat_list, "boise-- cat_list in PathChooser::_order_cats")
        return cat_list


    def _refine_cat_choice(self):
        """
        What's it going to be? rev1 or cat1
        """
        self.all_cat = self.all_cat%self.CONSTANT_MOD_CAT #reset after MOD_CAT1
        if (0 == self.all_cat): self.just_cats = 0
        amt_of_just_cats_needed = (self.CONSTANT_MOD_CAT/2) - self.just_cats
        amt_left_in_cycle  =  self.CONSTANT_MOD_CAT - self.all_cat
        cat1_deficit = True if (amt_of_just_cats_needed > amt_left_in_cycle) else False
        self.all_cat += 1
        rslt = self.CONSTANT_USE_CAT
        if cat1_deficit:
            self.just_cats += 1
            rslt =  self.CONSTANT_USE_CAT
        else:
            rslt =  self.CONSTANT_USE_REV
        #current.paideia_debug.do_print({ 'amt_of_just_cats_needed': amt_of_just_cats_needed,
                                         #'amt_left_in_cycle': amt_left_in_cycle,
                                         #'cat1_deficit':cat1_deficit,
                                         #'self.all_cat1':self.all_cat,
                                        #'self.just_cats':self.just_cats,
                                        #'rslt': rslt}, "bilbao in _decide_between_rev1_and_cat1")
        self.tag_progress['just_cats'] = self.just_cats
        self.tag_progress['all_cat1']  = self.all_cat
        return rslt


    def _paths_by_category(self, cat, rank):
        """
        Assemble list of paths tagged with tags in each category for this user.

        Returns a dictionary with categories as keys and corresponding lists
        as values.
        """
        #current.paideia_debug.do_print({'cat':cat,'rank': rank}, "vernon:paths by category called")

        pathset = None
        use_cat1 = self.CONSTANT_USE_CAT
        while True:
            db = current.db
            # TODO: set up computed field
            # if not db(db.paths).select().first().path_tags:
            # for row in db(db.paths.id > 0).select():
            # db(db.paths.id == row.id).update(steps=row.steps)
            # TODO: include paths with tag as secondary, maybe in second list
            # TODO: cache the select below and just re-order randomly

            #create a cleaner qeury to get the path ... JOB ..oct 08,2014
            #conditions: tags_for_steps in tag_progress[rev_cat](tags)
            taglist = []
            use_cat1 = self._refine_cat_choice()
            if(self.CONSTANT_USE_CAT == use_cat1):
                cat = 1
                tag_cats = self.categories[self.CONSTANT_USE_CAT]
                taglist = tag_cats
                #current.paideia_debug.do_print({'cat':cat, 'new ones':taglist}, "boise-- taglist in PathChooser::_paths_by_category")
            else:
                taglist = self.categories['rev{}'.format(cat)]
                #current.paideia_debug.do_print({'cat':cat, 'old ones':taglist}, "boise-- taglist in PathChooser::_paths_by_category")
            #current.paideia_debug.do_print({'taglist':taglist}, "boise-- taglist in PathChooser::_paths_by_category")

            #get all steps in this taglist
            stepslist_unhashable = db(db.step2tags.tag_id.belongs(taglist)).select(db.step2tags.step_id).as_list()
            ##current.paideia_debug.do_print(stepslist_unhashable, "boise-- stepslist_unhashable in PathChooser::_paths_by_category")
            if ( not stepslist_unhashable): break
            stepslist = [v['step_id'] for v in stepslist_unhashable]
            ##current.paideia_debug.do_print(stepslist, "boise-- stepslist in PathChooser::_paths_by_category")

            #status of steps != 2
            stepslist_unhashable = db( (db.steps.id.belongs(stepslist)) & (db.steps.status != 2) ).select(db.steps.id).as_list()
            ##current.paideia_debug.do_print(stepslist, "boise-- stepslist_unhashable cleared of status != 2 in PathChooser::_paths_by_category")
            stepslist = [v['id'] for v in stepslist_unhashable]
            ##current.paideia_debug.do_print(stepslist, "boise-- stepslist cleared of status != 2 in PathChooser::_paths_by_category")
            if ( not stepslist): break
            #pathset = pathset.find(lambda row: len(row.steps) > 0 and
            #                       all([s for s in row.steps
            #                            if (db.steps[s].status != 2)]))

            #all paths in steplist from taglist
            pathset_ids_unhashable = db(db.path2steps.step_id.belongs(stepslist)).select(db.path2steps.path_id).as_list()
            ##current.paideia_debug.do_print(pathset_ids_unhashable, "boise--  pathset_ids_unhasable fresh in PathChooser::_paths_by_category")
            pathset_ids = [v['path_id'] for v in pathset_ids_unhashable]
            ##current.paideia_debug.do_print(pathset_ids, "boise--  pathset_ids fresh in PathChooser::_paths_by_category")
            if ( not pathset_ids): break

            # pathset.exclude(lambda row: any([t for s in row.steps
            # for t in db.steps[s].tags
            # if db.tags[t].tag_position > rank]))
            pathset = db(db.paths.id.belongs(pathset_ids)).select()
            ##current.paideia_debug.do_print(pathset.as_list(), "boise-- pathset after we get entire thing in PathChooser::_paths_by_category")
            #debug

            pathset = pathset.find(lambda row: all([ Step(s).has_locations() for s in row.steps]))
            ##current.paideia_debug.do_print(pathset, "boise-- pathset after screening for locations in PathChooser::_paths_by_category")

            pathset = pathset.as_list()

            #debug
            ###current.paideia_debug.do_print(pathset, "boise-- pathset in PathChooser::_paths_by_category")
            ##current.paideia_debug.do_print(cat,     "boise-- cat in PathChooser::_paths_by_category")
            break;
        return (pathset, cat, use_cat1)


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

        JOB: Oct 12, 2014 : _paths_by_category is supposed to have filtered out
        all paths that have steps with no locations, so we can skip that step
        here and make sure that it is working in _paths_by_category if we have
        a problem here

        """

        path = None
        new_loc = None
        mode = None
        #current.paideia_debug.do_print({'raw self.completed': self.completed}, "vernon- raw self.completed in Pathchooser::_choose_from_cat")
        completed_list = [int(k) for k in self.completed['paths']]
        while True:
            loc_id = self.loc_id
            #current.paideia_debug.do_print({'loc_id':loc_id}, "vernon -current loc_id in Pathchooser::_choose_from_cat")
            db = current.db
            #current.paideia_debug.do_print({'self.completed': completed_list}, "vernon- self.completed in Pathchooser::_choose_from_cat")
            p_new = [p for p in cpaths if p['id'] not in completed_list]
            #current.paideia_debug.do_print({'p_new':[p['id'] for p in p_new] if p_new else []}, "vernon- pnew in Pathchooser::_choose_from_cat")
            p_here = [p for p in cpaths
                      if loc_id in db.steps[int(p['steps'][0])].locations]
            #current.paideia_debug.do_print({'p_here':[p['id'] for p in p_here] if p_here else []}, "vernon- p_here in Pathchooser::_choose_from_cat")
            p_here_new = [p for p in p_here if p in p_new]
            #current.paideia_debug.do_print({'p_here_new':[p['id'] for p in p_here_new] if p_here_new else []}, "vernon- p_here_new in Pathchooser::_choose_from_cat")
            p_all  = [p for p in cpaths]
            #current.paideia_debug.do_print({'p_all':[p['id'] for p in p_all] if p_all else []}, "vernon- p_all in Pathchooser::_choose_from_cat")
            if p_here_new:
                #current.paideia_debug.do_print({'p_here_new':[p['id'] for p in p_here_new]}, "vernon- attempting p_here_new in Pathchooser::_choose_from_cat")
                path = p_here_new[randrange(0, len(p_here_new))]
                mode = 'here_new'
            elif p_new:
                # While loop safeguards against looking for location for a step
                # that has no locations assigned.
                #JOB ... infinite loop danger here?? oct 12, 2014
                #    ... adding a safeguard against infinite looping ... wasnt happening
                #    ...because at this point all paths should only have steps with locations anyways
                #current.paideia_debug.do_print({'p_new':[p['id'] for p in p_new]}, "vernon- attempting p_new in Pathchooser::_choose_from_cat")
                loopmax = len(p_new)*5
                loopcount = 0
                while path is None:
                    try:
                        loopcount += 1
                        if (loopcount > loopmax): break
                        idx = randrange(0, len(p_new))
                        path = p_new[idx]
                        new_locs = db.steps(path['steps'][0]).locations
                        goodlocs = [l for l in new_locs if db.locations[l].loc_active is True]
                        new_loc = goodlocs[randrange(0, len(goodlocs))]
                        mode = 'new_elsewhere'
                    except TypeError:
                        path = None
                        current.paideia_debug.do_print("vernon- TypeError should NOT happen ... filtering for blank locations in _path_by_category is not working ", '-altoona-')
                    except ValueError:
                        current.paideia_debug.do_print("vernon-randrange error NOT permitted", '-altoona-')
                        print traceback.format_exc(5)
            elif p_here:
                #current.paideia_debug.do_print({'p_here':[p['id'] for p in p_here]}, "vernon- attempting p_here in Pathchooser::_choose_from_cat")
                try:
                    #now based on how many times step has been seen ... JOB oct 25, 2014
                    """
                    x = randrange(0, len(p_here))
                    ##current.paideia_debug.do_print({'random':x}, "vernon- random index for p_here in Pathchooser::_choose_from_cat")
                    path = p_here[randrange(0, len(p_here))]
                    path = p_here[x]
                    """
                    p_here_objs = {str(p['id']):p for p in p_here}
                    p_here_scores = {k:0 for k in p_here_objs}
                    #print p_here_objs
                    #print p_here_scores
                    #current.paideia_debug.do_print({'p_here_objs':p_here_objs}, "vernon- p_here_objs in Pathchooser::_choose_from_cat")
                    for k in completed_list:
                        k_str = str(k)
                        if ((k_str in  self.completed['paths']) and (k_str in p_here_scores)):
                            p_here_scores[k_str] = self.completed['paths'][k_str]
                    p_here_scores_sorted = sorted(p_here_scores, key = lambda k: p_here_scores[k])
                    #print {'p_here_scores_sorted':p_here_scores_sorted}
                    use_this_p_here = [ p_here_objs[k] for k in p_here_scores_sorted]
                    path = use_this_p_here[0]
                    #print {'use_this_p_here':use_this_p_here}
                    #print {'path':path}
                    mode = 'repeat_here'
                    #current.paideia_debug.do_print({'p_here_objs':p_here_objs,
                                                  #  'p_here_scores':p_here_scores,
                                                  #  'p_here_scores_sorted':p_here_scores_sorted,
                                                  #  'use_this_p_here':use_this_p_here},
                                     #"vernon- sorted pheres in Pathchooser::_choose_from_cat")

                except ValueError:
                    current.paideia_debug.do_print("weired exception NOT permitted", '-altoona-')
                    print traceback.format_exc(5)
            elif p_all:
                #current.paideia_debug.do_print({'p_all':[p['id'] for p in p_all]}, "vernon- attempting p_all in Pathchooser::_choose_from_cat")
                loopmax = len(p_all)*5
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
                        mode = 'all_oldelsewhere'
                    except TypeError:
                        path = None
                        current.paideia_debug.do_print("vernon- TypeError should NOT happen ... filtering for blank locations in _path_by_category is not working ", '-altoona-')
                    except ValueError:
                        current.paideia_debug.do_print("vernon-randrange error NOT permitted", '-banf-')
                        print traceback.format_exc(5)
            break #from main while True
        #debug
        #current.paideia_debug.do_print( ({'path':path}, {'new_loc':int(new_loc) if new_loc else None}, {'category':category}, {'mode':mode}), "vernon-- (path, new_loc, category, mode) in PathChooser::_choose_from_cat")
        return (path, new_loc, category, mode)

    def choose(self, db=None):
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

        """
        cat_list = self._order_cats()
        print {'cat_list':cat_list}
        rev_list = ['rev{}'.format(c) for c in range(1,5)]
        print {'rev_list':rev_list}
        good_rev_nums = [l[3:] for l in rev_list if self.categories[l]]
        print {'good_rev_nums':good_rev_nums}
        no_good_rev_nums = set(rev_list).difference(good_rev_nums)
        print {'no_good_rev_nums': no_good_rev_nums}
        for n in no_good_rev_nums:
            cat_list.remove(n)
        """

        cat_list = [c for c in self._order_cats()
                    if self.categories['rev{}'.format(c)]]
        #current.paideia_debug.do_print(cat_list, "boise-- catlist in PathChooser::choose")

        # cycle through categories, starting with the one from _get_category()
        for cat in cat_list:
            catpaths, category,use_cat1 = self._paths_by_category(cat, self.rank)
            #print 'catpaths -------------'
            #print [c['id'] for c in catpaths]
            #print 'category -------------'
            #print category
            if (catpaths and len(catpaths)):
                path, newloc, category, mode = self._choose_from_cat(catpaths,
                                                                     category)
                if (mode):
                    #current.paideia_debug.do_print({'path': path,
                                                    #'newloc': newloc,
                                                    #'category':category,
                                                    # 'mode': mode}, "Brisbane: returning from choose")
                    return path, newloc, category, mode
                else:
                    print 'bad mode trying another category'
            else:
                continue
        #debug
        #print current.paideia_debug.data
        return None,None,None,None

class User(object):
    """
    An object representing the current user, including his/her performance
    data and the paths completed and active in this session.

    """

    #debug
    def __init__(self, userdata, tag_records, tag_progress, blocks=[]):
    #def __init__(self, userdata, tag_records, tag_progress):
        """
        Initialize a paideia.User object.

        ## Argument types and structures
        - userdata: {'first_name': str, 'id': int, ..}
        - tag_progress: rows.as_dict()
        - tag_records: rows.as_dict
        """
        db = current.db
        try:
            self.time_zone = userdata['time_zone']
            #current.paideia_debug.do_print(({'blocks':[b.get_condition() for b in blocks] }), "Brisbane- creating user these are the blocks")
            self.blocks = blocks  # FIXME: somehow pass previous day's blocks in user._is_stale()?
            #current.paideia_debug.do_print(({'blocks':[b.get_condition() for b in self.blocks] }), "Brisbane- creating user these are the self.blocks")
            self.name = userdata['first_name']
            self.user_id = userdata['id']

            self.path = None
            #JOB ... oct 25, 2014, self.completed paths will now be a hash {'path_id': count}
            #point latest to some default path? ... used for repeat should be valid for repeats unless server gets reset somewhere in between takes
            self.completed_paths = {'latest': None, 'paths': {}}

            self.cats_counter = 0  # timing re-categorization in get_categories()

            self.old_categories = {}
            self.tag_records = tag_records
            self._set_user_rank(tag_progress,1)
            #self.rank = tag_progress['latest_new'] if tag_progress else 1
            self.tag_progress = tag_progress
            self.promoted = None
            self.new_tags = None

            self.inventory = []
            self.session_start = datetime.datetime.utcnow()

            self.loc = None
            self.prev_loc = None
            self.npc = None
            self.prev_npc = None
            msel = db((db.auth_membership.user_id == self.user_id) &
                      (db.auth_membership.group_id == db.auth_group.id)).select()
            # FIXME: Handle registered users without a class assignment
            # put everyone either in a class at registration or in (by default)
            # a generic 'class' with generic presets
            try:
                target = [m.auth_group.paths_per_day for m in msel
                          if m.auth_group.paths_per_day][0]
            except IndexError:
                print traceback.format_exc(5)
                target = 20
            self.quota = target

            self.past_quota = False
            self.viewed_slides = False
            self.reported_badges = False
            self.reported_promotions = False
            #self.just_cats = 0
            #self.all_cat1  = 0
            #debug ... dont forget to remove
            #raise Exception ("who called me?")
        except Exception:
            print traceback.format_exc(5)
            #debug ... dont forget to remove this
            #current.paideia_debug.do_print( traceback.format_exc(),'who called me')
            #current.paideia_debug.do_print( traceback.extract_stack(),'who called me')

    def _set_user_rank(self,tag_progress=None,given_rank=0):
        if (tag_progress and 'latest_new' in tag_progress and tag_progress['latest_new']):
            self.rank = tag_progress['latest_new']
        else: self.rank = given_rank


    def get_completed_paths_len(self):
        """
        returns length of completed paths
        adds up counts of each completed path ...essentially how
        many times did you get something right
        """
        p_len = 0
        for x in  self.completed_paths['paths']:
            #debug
            #print {'self.completed_paths':self.completed_paths}
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
        - Returns False
        """
        # TODO make sure that current loc and npc get set for self.prev_loc etc
        if self.blocks:
            blockset = []
            for b in self.blocks:
                if not b.get_condition() in [c.get_condition() for c in blockset]:
                    blockset.append(b)
                    #current.paideia_debug.do_print(({'sc': current.sequence_counter},{'b':b.get_condition()}), "Brisbane- in check for blocks, appending b")
            self.blocks = blockset
            ##current.paideia_debug.do_print(({'sc': current.sequence_counter},{'self.blocks':[x.condition for x in  self.blocks] if self.blocks else []}), "Marseilles- in check for blocks, these blocks where found")
            current.sequence_counter += 1
            myblock = self.blocks.pop(0)
            #current.paideia_debug.do_print(({'sc': current.sequence_counter},{'my block': myblock.condition if myblock  else 'Empty'},{'new self.blocks':[x.condition for x in  self.blocks] if self.blocks else None}), "Brisbane- in check_for_blocks, these are the blocks left")
            current.sequence_counter += 1
            return myblock
        else:
            return None

    def set_block(self, condition, kwargs=None):
        """ Set a blocking condition on this Path object. """
        myblocks = [b.get_condition() for b in self.blocks]
        ##current.paideia_debug.do_print(({'sc': current.sequence_counter}, {'condition':condition},{'kwargs':kwargs},{'self.blocks':[x.condition for x in  self.blocks] if self.blocks else []}), "Marseilles- in User::_set_block, these are the  blocks before")
        current.sequence_counter += 1
        def _inner_set_block():
            if condition not in myblocks:
                self.blocks.append(Block(condition, kwargs=kwargs))
                #current.paideia_debug.do_print(({'sc': current.sequence_counter}, {'condition':condition},{'kwargs':kwargs},{'self.blocks':[x.condition for x in  self.blocks] if self.blocks else None}), "Brisbane- in inner_set_block in User::_set_block, these are the  blocks before")

        if condition == 'view_slides':
            if not self.viewed_slides:
                _inner_set_block()
                self.viewed_slides = True
        elif condition == 'new_tags':
            if not self.reported_badges:
                _inner_set_block()
                self.reported_badges = True
            else:
                ##current.paideia_debug.do_print(({'sc': current.sequence_counter},{'self.reported_badges':self.reported_badges}, {'condition':condition},{'kwargs':kwargs},{'self.blocks':[x.condition for x in  self.blocks] if self.blocks else []}), "Marseilles- in User::_set_block, new_tags but reported_badges is true")
                current.sequence_counter += 1
        #elif condition == 'promoted':
        #    if not self.reported_promotions:
        #        _inner_set_block()
        #        self.reported_promotions = True
        else:
            _inner_set_block()

        ##current.paideia_debug.do_print(({'sc': current.sequence_counter},{'self.blocks':[x.condition for x in  self.blocks] if self.blocks else []}), "Marseilles- in User::_set_block, these blocks where found")
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
        #current.paideia_debug.do_print(({'sc': current.sequence_counter},{'self.blocks':[x.condition for x in  self.blocks] if self.blocks else None}), "Brisbanme- in User::is_stale ... end")
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

    def _make_path_choice(self, loc):
        """
        Instantiate PathChooser and return the result of its choose() method.
        """
        choice = None
        if self.path:  # TODO: do I want this catch here?
            #JOB ... oct 25, 2014 ... complete_path now occurs after user gets path right
            #   is only 1 step in the path being used?
            #self.complete_path()  # catch end-of-path and triggers new choice -- oct 25, 2014 ... self.path = None has been moved from self.complete_path as we are completing path as soon as a right result is recorded so may need to keep path around
            self.path = None
            pass
        if not self.tag_progress:  # in case User was badly initialized
            #debug
            print 'Atlanta: no tag-progress, so getting categories'
            self.get_categories()

        if 'just_cats' not in self.tag_progress:self.tag_progress['just_cats'] = 0
        if 'all_cat1' not in self.tag_progress:self.tag_progress['all_cat1'] = 0
        choice, redir, cat, mode = PathChooser(self.tag_progress,
                                                loc.get_id(),
                                                self.completed_paths).choose()

        #tag_progress gets updated in PathChooser and we need to update it for cat1 purposes
        #current.paideia_debug.do_print({'self.tag_progress':self.tag_progress}, "********************albany-saving tag_progres************")
        condition = {'name': self.get_id()}
        current.db.tag_progress.update_or_insert(condition, **self.tag_progress)
        current.db.commit()


            # FIXME: if no choice, send_error('User', 'get_path', current.request)
        if mode:
            path = Path(path_id=choice['id'])
            return path, redir, cat
        else: return None,None,None

    def get_path(self, loc, db=None, pathid=None, repeat=None):
        """
        Return the currently active Path object.

        Only the 'loc' argument is strictly necessary. The others are used for
        dependency injection during testing.

        """
        db = current.db if not db else db
        redir = None
        cat = None
        pastq = None
        while True:
            ##current.paideia_debug.do_print({'pathid':pathid, 'loc':loc.get_alias()}, "albany-User::get_path called ")
            if pathid:  # testing specific path
                self.path = Path(pathid)
            #--- is this the cause of the repitions???? -- no its not ---------
            if repeat and not self.path:  # repeating a step, path finished before
                #current.paideia_debug.do_print({'repeat':repeat}, "albany-User::get_path called - repeat and not self.path")
                #xxx --- this is important for repition problem
                #if we are using hash ... we dont know the latest one is in 'latest'
                #pathid = self.completed_paths.pop(-1)
                pathid = self.completed_paths['latest']
                self.path = Path(pathid)
                ##current.paideia_debug.do_print(pathid, "albany-User::get_path new path *popped*: ")
            # TODO: rationalize this series of conditions
                ##current.paideia_debug.do_print(self.path.step_for_reply if (self.path and self.path.step_for_reply) else None,
                #                  "albany-User::get_path new path *popped*: ")
            elif self.path and self.path.step_for_reply:
                #current.paideia_debug.do_print({'self.path':self.path.get_id(), 'self.path.step_for_reply': self.path.step_for_reply.get_id()}, "albany-User::get_path called - self.path and self.path.step_for_reply")
                pass
            elif self.path and repeat:  # repeating a step, path wasn't finished
                #current.paideia_debug.do_print({'self.path':self.path.get_id(), 'repeat': repeat}, "albany-User::get_path called - self.path and repeat")
                pass
            elif self.path and len(self.path.steps):  # unfinished step in self.path
                #current.paideia_debug.do_print({'self.path':self.path.get_id(), 'len(self.path.steps)': len(self.path.steps)}, "albany-User::get_path called - self.path and len(self.path.steps)")
                pass
            else:  # choosing a new path
                self.path, redir, cat = self._make_path_choice(loc)
                #current.paideia_debug.do_print({'self.path':self.path.get_id(), 'cat':cat}, "albany-User::get_path called ... after calling _make_path_choice ")
                if (not self.path): break # and return Nones
            #debug
            ##current.paideia_debug.do_print(self.completed_paths,"Atlanta-completed paths")
            #end debug
            if self.get_completed_paths_len() >= self.quota and self.past_quota is False:
                pastq = True
                self.past_quota = True
            if len(self.blocks) > 0:
                # FIXME: This hack is to work around mysterious introduction of
                # redirect block after initial redirect has been triggered
                self.blocks = [b for b in self.blocks
                               if not b.get_condition() is 'redirect']
            break
        return (self.path, cat, redir, pastq)

    def get_categories(self, user_id=None, rank=None, old_categories=None,
                       tag_records=None, utcnow=None):
        """
        Return a categorized dictionary with four lists of tag id's.

        This method is important primarily to decide whether a new
        categorization is necessary before instantiating a Categorizer object

        # TODO: do we need to create new categorizer object each time?

        The method is intended to be called with no arguments
        """
        just_cats = 0
        all_cat1  = 0

        ##current.paideia_debug.do_print(old_categories, "Categories called")
        db = current.db
        user_id = self.user_id if not user_id else user_id
        if not tag_records:
            tag_records = db(db.tag_records.name == user_id).select().as_list()
        self.tag_records = tag_records

        #debug
        ###current.paideia_debug.do_print(self.cats_counter, "self.cats_counter")
        #dont forget to remove the ff line
        #self.cats_counter = 5

        if (self.cats_counter in range(0, 4)) \
                and hasattr(self, 'categories') \
                and self.categories:
            self.cats_counter += 1
            return None, None, None,None
        else:
            #print 'Atlanta- get_categories called'
            utcnow = datetime.datetime.utcnow() if not utcnow else utcnow
            try:
                tag_progress_sel = db(db.tag_progress.name == user_id
                                      ).select()
                assert len(tag_progress_sel) == 1
                self.tag_progress = tag_progress_sel.first().as_dict()
                rank = self.tag_progress['latest_new']
                just_cats = self.tag_progress['just_cats']
                all_cat1 = self.tag_progress['all_cat1']

                # TODO: below is 'magic' hack based on specific db field names
                categories = {k: v for k, v in self.tag_progress.iteritems()
                              if k[:3] in ['cat', 'rev']}
            except (AttributeError, AssertionError):
                categories = None
            self.old_categories = copy(categories)

            c = Categorizer(rank, categories, tag_records, user_id,
                            utcnow=utcnow)
            cat_result = c.categorize_tags()

            #debug
            #current.paideia_debug.do_print(cat_result, "halifax cat_result")

            self._set_user_rank(cat_result['tag_progress'],0)
            #self.rank = cat_result['tag_progress']['latest_new']

            self.tag_records = cat_result['tag_records']  # FIXME: do changes get recorded?
            self.tag_progress = cat_result['tag_progress']
            self.tag_progress['just_cats'] = just_cats
            self.tag_progress['all_cat1'] = all_cat1
            self.categories = cat_result['categories']
            self.promoted = cat_result['promoted']
            self.new_tags = cat_result['new_tags']
            self.cats_counter = 0  # reset counter


            #debug
            ###current.paideia_debug.do_print(self.categories, "Marseilles-tag categories output in get categories")
            ###current.paideia_debug.do_print(self.tag_progress, "Marseilles-tag progress output in get categories")
            ##current.paideia_debug.do_print(self.promoted, "Marseilles-tag promoted output in get categories")
            ##current.paideia_debug.do_print(self.new_tags, "Marseilles-tag new tags output in get categories")



            return self.tag_progress, self.promoted, self.new_tags, cat_result['demoted']

    def complete_path(self,got_right):
        """
        Move the current path from the path variable to 'completed_paths' list.
        Set last_npc and prev_loc before removing the path.
        """
        # Only id of paths stored to conserve memory.
        # prev_loc and prev_user info not drawn from old paths but
        # carried on User.
        # Repeating path must be triggered before path is completed.
        #debug
        ##current.paideia_debug.do_print(self.completed_paths, 'Atlanta-complete_path called')
        #self.completed_paths.append(self.path.get_id())
        #JOB ... oct 25, 2014
        #we now using hash {'path_id':count} to keep track of completed_paths
        # {'latest' : path_id} gives path_id of the latest one
        if (str(self.path.get_id()) not in self.completed_paths['paths']):
            self.completed_paths['paths'][str(self.path.get_id())] = {'right': 0, 'wrong':0}
        if got_right:
            self.completed_paths['paths'][str(self.path.get_id())]['right'] += 1
        else:
            self.completed_paths['paths'][str(self.path.get_id())]['wrong'] += 1
        self.completed_paths['latest'] = self.path.get_id()
        #debug
        #print {'self.completed_paths':self.completed_paths}
        #self.path = None ... has been moved to _make_path_choice ... we are doing complete_path
        #earlier and self.path may need to hang around a bit longer
        #self.path = None
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
        #print'Categorizer __init__: categories ------------------'
        ##pprint(tag_progress)
        self.utcnow = utcnow if utcnow else datetime.datetime.utcnow()
        self.secondary_right = secondary_right

    def _set_categorizer_rank(self,tag_progress=None,given_rank=0):
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
        JOB 2014/09/28 :
            we get a fresh copy of tag_records every time. don't even bother to bring
            tag_records to this function because it will be ignored
        """
        rank = self.rank if not rank else rank
        if not rank:
            rank = 1
        old_categories = self.old_categories if not old_categories \
                         else old_categories
        #tag_records = self.tag_records if not tag_records else tag_records
        db = current.db if not db else db
        tagorder = db.tag_records.tag
        tag_records = db(db.tag_records.name == self.user_id).select(orderby=tagorder).as_list()
        ###current.paideia_debug.do_print(tag_records,"Minnedosa, this is what we got")

        #if tag_records:
        #    tag_records = self._sanitize_recs(tag_records)
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
                   'just_cats': 0, 'all_cat1':0}
            return {'tag_progress': tp,
                    'tag_records': tag_records,
                    'new_tags': {'rev1': categories['rev1'], 'rev2':[], 'rev3':[],'rev4':[]},
                    'promoted': None,
                    'demoted': None,
                    'categories': categories}
        else:
            # otherwise, categorize tags that have been tried
            # TODO:uncomment and do _add_secondary_right properly

            for idx, t in enumerate([t for t in tag_records
                                     if tag_records and t['secondary_right']]):
                self._add_secondary_right(t)
                ###current.paideia_debug.do_print(t, "***--halifax--*** t after add secondary right")
            categories = self._core_algorithm()

            #debug
            #current.paideia_debug.do_print({'categories':categories}, "Lisbon-categories after core algorithm---------------------")

            categories = self._add_untried_tags(categories)
            #debug
            #current.paideia_debug.do_print({'categories':categories}, "Lisbon-categories after add untried-------------------------")

            categories = self._remove_dups(categories, rank)

            #debug
            #current.paideia_debug.do_print({'categories':categories}, "Lisbon-categories after remove dups-------------------------")

            categories.update((c, []) for c in ['cat1', 'cat2', 'cat3', 'cat4'])
            cat_changes = self._find_cat_changes(categories, old_categories)

            #debug
            ###current.paideia_debug.do_print(categories, "categories after cat changes -------------------------")
            ##pprint(cat_changes)

            promoted = cat_changes['promoted']
            demoted = cat_changes['demoted']
            new_tags = cat_changes['new_tags']
            tag_progress = copy(cat_changes['categories'])

            #add cats for new tags
            for i in range(1,5):
                idx = 'rev{}'.format(i)
                if (new_tags and idx in new_tags and new_tags[idx]):
                    idxcat = 'cat{}'.format(i)
                    curr_cat = tag_progress[idxcat] if (idxcat in tag_progress and tag_progress[idxcat]) else []
                    tag_progress[idxcat] = list(set(curr_cat).union(new_tags[idx]))[:]


            # If there are no tags left in category 1, introduce next set
            #current.paideia_debug.do_print({'tag_progress':tag_progress,}, "demerara ... this is why introduce_tags may never be called")
            if self._check_if_cat1_needed(tag_progress):
                #current.paideia_debug.do_print('--cat1 needed ---', "demerara -- cat1 needed")
                while True:
                    newlist = self._introduce_tags(rank=rank)
                    if not newlist:
                        current.paideia_debug.do_print({'rank': rank}, "ERROR: failed to get tags for rank")
                        break
                    curr_rev1 = tag_progress['rev1'] if ('rev1' in tag_progress and tag_progress['rev1']) else []
                    curr_cat1 = tag_progress['cat1'] if ('cat1' in tag_progress and tag_progress['cat1'])else []
                    tag_progress['cat1'] = list(set(curr_cat1).union(newlist))[:]
                    tag_progress['rev1'] = list(set(curr_rev1).union(newlist))[:]
                    if not new_tags: new_tags = {'rev1':[]}
                    curr_new_tags_rev1 = new_tags['rev1'] if (new_tags and 'rev1' in new_tags and new_tags['rev1']) else []
                    new_tags['rev1'] = list(set(curr_new_tags_rev1).union(newlist))[:]

                    curr_rev1 = categories['rev1'] if ('rev1' in categories and categories['rev1']) else []
                    curr_cat1 = categories['cat1'] if ('cat1' in categories and categories['cat1']) else []
                    categories['cat1'] = list(set(curr_cat1).union(newlist))[:]
                    categories['rev1'] = list(set(curr_rev1).union(newlist))[:]
                    break
            # Re-insert 'latest new' to match tag_progress table in db
            tag_progress['latest_new'] = self.rank
            #current.paideia_debug.do_print({'categories':tag_progress}, "Lisbon-final cat progress-------------------------")

            return {'tag_progress': tag_progress,
                    'tag_records': self.tag_records,
                    'new_tags': new_tags,
                    'promoted': promoted,
                    'demoted': demoted,
                    'categories': categories}

    def _check_if_cat1_needed(self,cats):
        result = True
        while True:
            if not 'cat1' in  cats: return result
            if not cats['cat1']:    return result
            #all_cat2andup = list(chain.from_iterable([cats[c] for c
            #                          in ['cat2','cat3','cat4']
            #                          if (c in cats and cats[c])]))
            #rev1set = set(cats['rev1'] if ('rev1' in cats and cats['rev1']) else [])
            #cat1inrev1 = rev1set.difference(all_cat2andup)
            #if not cat1inrev1: return result
            break
        return False

    def _remove_dups(self, categories, rank):
        """
        Remove any duplicate tags and any tags beyond user's current rank.
        """
        db = current.db
        for k, v in categories.iteritems():
            if v:
                rankv = [t for t in v if db.tags(t)
                        and (db.tags[t].tag_position <= rank)]
                #debug -
                debug_delete = [t for t in v if db.tags(t)]
                #current.paideia_debug.do_print({'debug_delete':debug_delete, k: v}, "neepawa- in remove_dups, all tags")
                categories[k] = list(set(rankv))
        return categories

    def _add_secondary_right(self, rec):
        """
        Return the given tag record adjusted based on secondary_right data.

        For every CONST_SEC_RIGHT_MOD secondary_right entries, add 1 to times_right and change
        tlast_right based on the average of those three attempt dates.
        """
        CONST_SEC_RIGHT_MOD = 20
        db = current.db
        rec = rec[0] if isinstance(rec, list) else rec


        """ uncomment this to generate enough secondarys to test ... do this only in test server
        #Joseph Boakye <jboakye@bwachi.com>
        #testing ***** DONT FORGET TO REMOVE THIS!!! ****
        #we are going to create at least 20 secondary right as we dont have a lot in
        #the system, so we can test this
        rlen = len(rec['secondary_right'])
        if (rlen):
            for i in range(1,23):
                (rec['secondary_right']).append(rec['secondary_right'][0])
        #--------- end generating secondary rights for testing - dont forget to remove --------------
        """


        right2 = flatten(rec['secondary_right'])  # FIXME: sanitizing data
        ###current.paideia_debug.do_print(rec, "neepawa- origional rec in _add_secondary_right")
        ###current.paideia_debug.do_print(right2, "neepawa- right2 in _add_secondary_right")
        ###current.paideia_debug.do_print( rec['secondary_right'], "minnedosa - rec sec right in _add_secondary_right,right2")

        if right2 != rec['secondary_right']:  # FIXME: can remove when data clean
            right2.sort()
        ###current.paideia_debug.do_print(right2, "halifax - right2 sorted in _add_secondary_right,right2")

        rlen = len(right2)
        rem2 = rlen % CONST_SEC_RIGHT_MOD



        if rlen >= CONST_SEC_RIGHT_MOD:
            # increment times_right by 1 per CONST_SEC_RIGHT_MOD secondary_right
            # this var is called triplets because CONST_SEC_RIGHT_MOD used to be 3
            triplets2 = rlen / CONST_SEC_RIGHT_MOD
            if not rec['times_right']:
                rec['times_right'] = 0
            rec['times_right'] += triplets2

            ###current.paideia_debug.do_print(rlen, "halifax - rlen in _add_secondary_right")
            ###current.paideia_debug.do_print(triplets2, "halifax - triplets2 in _add_secondary_right")
            ###current.paideia_debug.do_print(rem2, "halifax - rem2 in _add_secondary_right")

            # move tlast_right forward based on mean of oldest 3 secondary_right
            early3 = right2[: -(rem2)] if rem2 else right2[:]
            ###current.paideia_debug.do_print(early3, "halifax - early3 in _add_secondary_right")
            early3d = [self.utcnow - datetime.datetime.strptime(s,'%Y-%m-%d %H:%M:%S.%f') for s in early3]
            ###current.paideia_debug.do_print(early3d, "halifax - early3d in _add_secondary_right")
            avg_delta = sum(early3d, datetime.timedelta(0)) / len(early3d)
            ###current.paideia_debug.do_print(avg_delta, "halifax - avg_delta in _add_secondary_right")
            avg_date = self.utcnow - avg_delta
            ###current.paideia_debug.do_print(avg_date, "halifax - avg_date in _add_secondary_right")

            #print'type is', type(rec['tlast_right'])
            # sanitize tlast_right in case db value is string
            if not isinstance(rec['tlast_right'], (datetime.datetime, tuple)):
                rec['tlast_right'] = parser.parse(rec['tlast_right'])

            # move tlast_right forward to reflect recent secondary success
            if avg_date > rec['tlast_right']:
                print "halifax, avg_date > rec['tlast_right'] "
                rec['tlast_right'] = avg_date

            rec['secondary_right'] = right2[-(rem2):] if rem2 else []
            ###current.paideia_debug.do_print(rec, "halifax new rec in _add_secondary_right")

            #test where we change the last_right of the rec
            test_rec = deepcopy(rec)
            test_rec['tlast_right'] = test_rec['tlast_right'] - datetime.timedelta(days=300)
            ###current.paideia_debug.do_print(test_rec,"halifax test rec after subtracting 300 days")
            if avg_date > test_rec['tlast_right']:
                print "halifax, avg_date > test_rec['tlast_right'] "
                test_rec['tlast_right'] = avg_date
                ###current.paideia_debug.do_print(test_rec,"halifax test rec after replacing with avg_date")
            #write new record to dbase
            condition = {'tag': rec['tag'], 'name': rec['name']}
            db.tag_records.update_or_insert(condition,
                                            times_right = rec['times_right'],
                                            tlast_right = rec['tlast_right'],
                                            secondary_right=rec['secondary_right'])
            db.commit()
        else:
            pass
        return rec

    def _get_avg(self, tag, mydays=7):
        """
        Return the user's average score on a given tag over the past N days.

        Always returns a float, since scores are floats between 0 and 1.
        """
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

    def _core_algorithm(self, tag_records=None):
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
        ##current.paideia_debug.do_print({'tag_records': tag_records}, "tyne - in _core_algorithm")
        categories = {'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}
        tag_records = tag_records if tag_records else self.tag_records
        #debug
        debug_toggle_delete_me = 0
        for record in tag_records:
            #print'halifax tag', record['tag'], '================================='
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
                (((rdur < rwdur)  # delta right < delta right/wrong
                  and (rwdur.days > 1)  # not within 1 day
                  )
                 or
                 ((self._get_ratio(record) < 0.2)  # less than 1w to 5r total
                  and (rdur.days <= 30)  # right in past 30 days
                  )
                 or
                 ((self._get_avg(record['tag']) >= 0.8)  # avg score for week >= 0.8
                  and (rdur.days <= 30)  # right in past 30 days
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
                        ##current.paideia_debug.do_print({'tag': record['tag']}, "cern- this is going to be cat3")
                        category = 'rev3'  # delta between 14 and 60 days
                else:
                    category = 'rev2'  # Not due but delta is 2 weeks or less
            else:
                category = 'rev1'  # Spaced repetition requires review
            #print'************** category is ', category
            #debug - dont forget to remove this
            #debug_x_delete_me = ['rev1','rev2']
            #category = debug_x_delete_me[debug_toggle_delete_me%2]
            #debug_toggle_delete_me +=1
            #end debug
            #current.paideia_debug.do_print({'category': 'rev1', 'tag': record['tag']}, "cern")

            categories[category].append(record['tag'])
            #categories.append({category: record['tag']})

        return categories

    def _introduce_tags(self, rank=None, db=None):
        """
        Add the next set of tags to cat1 in the user's tag_progress

        Returns a dictionary of categories identical to that returned by
        categorize_tags
        """
        db = current.db if not db else db
        rank = self.rank if rank is None else rank

        #current.paideia_debug.do_print({'begin rank': rank}, "in introduce tags")
        if rank in (None, 0):
            rank = 1
        else:
            rank += 1
        self.rank = rank
        #current.paideia_debug.do_print({'end rank': rank,'end self.rank':self.rank}, "in introduce tags")

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
        #current.paideia_debug.do_print({'oldcats':oldcats},"glasgow- just entered _find_cat_changes")
        #current.paideia_debug.do_print({'cats':cats},"glasgow- just entered _find_cat_changes")
        uid = self.user_id if not uid else uid
        if oldcats:
            demoted = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
            promoted = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
            oldcats = {k: v for k, v in oldcats.iteritems()
                       if k[:3] == 'cat'}  # facilitates demotion tasks
            #copy oldcats into new new 'cats'
            for k in oldcats:
                if (k in oldcats and oldcats[k]):
                    cats[k] = oldcats[k][:]
                else:
                    cats[k] = []
            #current.paideia_debug.do_print({'cats' : cats},"surrey cats after updating with oldcats in _find_cat_changes")

            #new_tags = []
            new_tags = {'rev1': [], 'rev2': [], 'rev3': [], 'rev4': []}
            cnms = ['rev1', 'rev2', 'rev3', 'rev4']
            oldkeys = ['cat1', 'cat2', 'cat3', 'cat4']
            # TODO: cleaning up bad data; deprecate after finished
            oldcats = self._fix_oldcats(oldcats, uid, bbrows=bbrows)
            #current.paideia_debug.do_print({'oldcats' : oldcats},"surrey oldcats in _find_cat_changes")




            for cat, taglist in cats.iteritems():
                oldkey = 'cat{}'.format(cat[-1:])
                #--revcat = cat.replace('cat', 'rev')
                #--cats[revcat] = taglist[:]  # copy bc demotion only changes one
                #JOB ... oct 20, 2014 ... par around "cat in cnms"
                if taglist and (cat in cnms):
                    # Is tag completely new to this user?
                    oldvals = [v for v in oldcats.values() if v]
                    #current.paideia_debug.do_print({'oldvals' : oldvals},"trieste oldvals in _find_cat_changes")

                    #debug
                    #print'trieste-oldvals', oldvals
                    all_old_tags = list(chain.from_iterable(oldvals))
                    new_tags[cat] = [t for t in cats[cat] if t not in all_old_tags]
                    #new_tags.extend([t for t in taglist if t not in all_old_tags])

                    # was tag in a lower category before?
                    idx = oldkeys.index(oldkey)
                    was_lower = list(chain.from_iterable([oldcats[c] for c
                                                          in oldkeys[:idx]
                                                          if oldcats[c]]))
                    #current.paideia_debug.do_print({'was_lower': was_lower}, "trieste- was lower ")
                    promoted[cat] = [t for t in cats[cat] if t in was_lower]
                    ##current.paideia_debug.do_print(promoted, "trieste- promoted")

                    # was tag in a higher category before?
                    was_higher = list(chain.from_iterable([oldcats[c] for c
                                                           in oldkeys[idx + 1:]
                                                           if oldcats[c]]))
                    demoted[cat] = [t for t in taglist if t in was_higher]


            #this should be done for promoted instead? ... JOB ... nov 05, 2014
            #now being done for promotion
            #removal
            if any([k for k, v in promoted.iteritems() if v]):
                for tag in list(chain.from_iterable(promoted.values())):  # then restore old max in cats
                    catidx = [k for k, v in oldcats.iteritems()
                                if v and tag in v][0]
                    revidx = [k.replace('rev','cat') for k, v in cats.iteritems()
                                if v and tag in v and k in cnms][0]
                    try:
                        cat_set = set(cats[catidx])
                        #print {'tag to remove': tag, 'catidx':catidx}
                        #print {'cat set': cat_set}
                        if tag in cat_set: cat_set.remove(tag)
                        #print {'cat set after tag removed': cat_set}
                        cats[catidx] = []
                        cats[catidx] = list(cat_set)[:]
                        #print{'cats[catidx] finally': cats[catidx]}

                        """
                        cat_set = set(cats[revidx])
                        print {'tag to add': tag, 'revidx':revidx}
                        print {'cat set': cat_set}
                        cat_set.add(tag)
                        print {'cat set after tag added': cat_set}
                        cats[revidx] = []
                        cats[revidx] = list(cat_set)[:]
                        print{'cats[revidx] finally': cats[revidx]}
                        """
                    except ValueError:
                        #current.paideia_debug.do_print(({'promoted': promoted,'cats': cats} ), "Arden- UNEXPECTED ERROR while working on demotions")
                        pass

            #add cats for promoted tags
            #addition
            for k in promoted:
                while True:
                    if (not('rev' == k[:3])) : break
                    if (not(promoted[k])): break
                    catidx = k.replace('rev','cat')
                    if (catidx in oldcats) :
                        cats[catidx] = []
                        cats[catidx] =  list((set(oldcats[catidx])).union(promoted[k]))[:]
                    else:
                        cats[catidx] = promoted[k][:]
                    #current.paideia_debug.do_print(({'k': k, 'catidx': catidx, 'cats[catidx]': cats[catidx]} ), "Arden- setting cats for promoted")
                    break

            """
            #add cats for new tags
            for k in new_tags:
                while True:
                    if (not('rev' == k[:3])) : break
                    if (not(new_tags[k])): break
                    catidx = k.replace('rev','cat')
                    if (catidx in oldcats) :
                        cats[catidx] = []
                        x = []
                        if (catidx in oldcats and oldcats[catidx]): x = oldcats[catidx][:]
                        #cats[catidx] =  list((set(oldcats[catidx])).union(new_tags[k]))[:]
                        cats[catidx] =  list((set(x)).union(new_tags[k]))[:]
                        #current.paideia_debug.do_print(({'k': k, 'catidx': catidx, 'cats[catidx]': cats[catidx]} ), "Arden- setting cats for new tags")
                    else:
                        cats[catidx] = new_tags[k][:]
                    break
            """
            #debug ... dont forget to remove
            #cats['cat1'] = []
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
            new_tags = {'rev1': cats['rev1'][:], 'rev2':[], 'rev3':[],'rev4':[]}
            return {'categories': cats,
                    'demoted': None,
                    'promoted': None,
                    'new_tags': new_tags}

    #added self as first argument ... JOB ... sept 21 2013
    def _clean_tag_records(self,record_list=None, db=None):
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
        ##current.paideia_debug.do_print(({'sc': current.sequence_counter},{'self.condition':self.condition},{'self.kwargs':self.kwargs}), "Marseilles- Block constructor called")
        current.sequence_counter += 1

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
        ##current.paideia_debug.do_print(({'sc': current.sequence_counter},{'condition':condition},{'mystep':mystep}), "Marseilles- Block::make_step called")
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
            #current.paideia_debug.do_print(exception_data, "couldn't insert this exception data")
