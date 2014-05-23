#! /usr/bin/python
# -*- coding: utf-8 -*-
from gluon import current, redirect
from gluon import IMG, URL, SQLFORM, SPAN, DIV, UL, LI, A, Field, P, HTML
from gluon import I
from gluon import IS_NOT_EMPTY, IS_IN_SET

from inspect import getargvalues, stack
import traceback
from copy import copy
from itertools import chain
from random import randint, randrange
import re
import datetime
from dateutil import parser
from pytz import timezone
import pickle
from plugin_utils import flatten
from plugin_widgets import MODAL
# from pprint import pprint

# TODO: move these notes elsewhere
"""
The following files exist outside the paideia app folder and so need to be
watched when upgrading web2py:
- web2py/routes.py
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
        db = current.db if not db else db
        # TODO: fix redundant db call here
        self.response_string = response_string
        # TODO: move retrieval of data to user init so it's not duplicated when
        # just retrieving existing User.
        self.user = self._get_user(userdata=userdata,
                                   tag_records=tag_records,
                                   tag_progress=tag_progress,
                                   new_user=new_user)
        # TODO is record_id necessary?
        self.record_id = None  # stores step log row id after db update

    def _new_user(self, userdata, tag_records, tag_progress):
        '''Return a new User object for the currently logged in user.'''
        auth = current.auth
        db = current.db
        uid = auth.user_id
        userdata = db.auth_user[uid].as_dict() if not userdata else userdata
        if not tag_records:
            tag_records = db(db.tag_records.name == uid).select().as_list()
        if not tag_progress:
            tag_progress = db(db.tag_progress.name == uid).select().first()
            if not tag_progress:
                db.tag_progress.insert(latest_new=1)
                tag_progress = db(db.tag_progress.name == uid).select().first()
            tag_progress = tag_progress.as_dict()
        return User(userdata, tag_records, tag_progress)

    def _get_user(self, userdata=None, tag_records=None,
                  tag_progress=None, new_user=None):
        '''
        Initialize or re-activate User object.
        All named arguments are necessary.
        '''
        auth = current.auth
        db = current.db
        try:  # look for user object already on this Walk
            assert (self.user) and new_user is None
        except (AttributeError, AssertionError):  # because no user yet on this Walk
            try:
                sd = db(db.session_data.name ==
                        auth.user_id).select().first()
                if sd:
                    self.user = pickle.loads(sd['other_data'])
                else:
                    self.user = None
                assert self.user.is_stale() is False
                assert not new_user
            except (KeyError, TypeError):  # Problem with session data
                print traceback.format_exc(5)
                self.user = self._new_user(userdata, tag_records, tag_progress)
            except (AssertionError, AttributeError):  # user stale or block
                self.user = self._new_user(userdata, tag_records, tag_progress)
        if isinstance(self.user.quota, list):
            self.user.quota = self.user.quota[0]
        return self.user

    def start(self, localias, response_string=None, path=None, repeat=None,
              step=None, set_blocks=None, recategorize=None):
        """
        Issue the correct method for this interaction and return the result.
        This is the top-level interface for the Paideia module, to be called by
        the controller. The method decides whether we're starting a new step or
        responding to one in-process.
        """
        print '\nIN START'
        try:
            if response_string:
                return self.reply(localias=localias,
                                  response_string=response_string)
            else:
                return self.ask(localias=localias,
                                path=path,
                                repeat=repeat,
                                set_blocks=set_blocks,
                                recategorize=recategorize,
                                step=step)
        except Exception:
            print traceback.format_exc(5)
            self.clean_user()  # get rid of any problem path data
            return self.ask(localias=localias, path=path, step=step)

    def clean_user(self):
        """
        In case of irrecoverable conflict in user data, remove all path/steps.
        """
        print '\n error, cleaning user--------------------------------------\n'
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

        print 'STARTING WALK.ASK---------------------------------------'
        user = self.user
        # allow artificial setting of blocks during interface testing
        if set_blocks:
            for c, v in set_blocks.iteritems():
                myargs = {n: a for n, a in v.iteritems()}
                user.set_block(c, kwargs=myargs)
        username = user.get_name()
        self._set_blocks()

        loc = Location(localias)
        prev_loc = user.set_location(loc)
        prev_npc = user.get_prev_npc()

        p, category, redir, pastquota = user.get_path(loc, pathid=path,
                                                      repeat=repeat)
        user.active_cat = category
        if redir:
            user.set_block('redirect', kwargs={'next_loc': redir})
        if pastquota:
            user.set_block('quota_reached', kwargs={'quota': user.quota})

        s, newloc_id = p.get_step_for_prompt(loc, repeat=repeat)
        if newloc_id:
            user.set_block('redirect', kwargs={'next_loc': newloc_id})

        # TODO: make sure 'new_tags' is returned before 'view_slides'
        block = user.check_for_blocks()
        if block:
            s = block.get_step()

        npc = s.get_npc(loc, prev_npc, prev_loc)
        user.set_npc(npc)

        prompt = s.get_prompt(loc, npc, username)
        extra_fields = {'completed_count': len(user.completed_paths),
                        'category': category,
                        'pid': p.get_id()}
        prompt.update(extra_fields)

        p.end_prompt(s.get_id())  # send id to tell whether its a block step
        self._store_user(user)
        return prompt

    def _set_blocks(self, user=None):
        """
        """
        user = self.user if not user else user
        promoted, new_tags = user.get_categories(user_id=user.get_id())
        if new_tags:
            # setting order here should make new_tags step come up first
            user.set_block('new_tags', kwargs={'new_tags': new_tags,
                                               'promoted': promoted})
            user.set_block('view_slides', kwargs={'new_tags': new_tags})
        if promoted:
            user.set_block('new_tags', kwargs={'new_tags': new_tags,
                                               'promoted': promoted})
        return True

    def reply(self, localias, response_string, path=None, step=None):
        """
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
        print '\n================================'
        print '\nSTART OF Walk.reply()'
        user = self._get_user()
        loc = user.get_location()
        p, cat = user.get_path(loc)[:2]
        s = p.get_step_for_reply()
        if (not response_string) or re.match(response_string, r'\s+'):
            return self.ask()  # TODO: will this actually re-prompt the same step?
        prompt = s.get_reply(response_string)  # loc and npc stored on step

        assert self._record_cats(user.tag_progress,
                                 user.promoted,
                                 user.new_tags)
        self.record_id = self._record_step(user.get_id(),
                                           p.get_id(),
                                           s.get_id(),
                                           prompt['score'],
                                           prompt['times_right'],
                                           prompt['times_wrong'],
                                           user.tag_records,
                                           s.get_tags(),
                                           response_string)
        prompt['bugreporter'] = BugReporter().get_reporter(self.record_id,
                                                           p.get_id(),
                                                           s.get_id(),
                                                           prompt['score'],
                                                           response_string,
                                                           user.loc.get_alias())
        prompt['completed_count'] = len(user.completed_paths)
        prompt['pid'] = p.get_id()
        prompt['category'] = cat
        prompt['loc'] = loc.get_alias()

        p.complete_step()  # removes path.step_for_reply; cf. (user.get_path)
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
                                cat: now}
                        db.badges_begun.update_or_insert(
                                (db.badges_begun.name == user_id) &
                                (db.badges_begun.tag == tag), **data)
            return True
        except Exception:
            print traceback.format_exc(5)
            return False

    def _record_cats(self, tag_progress, promoted, new_tags, db=None):
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
            # combine promoted and new_tags for recording purposes
            if promoted:
                promoted['cat1'] = new_tags
            elif new_tags:
                promoted = {'cat1': new_tags}
            else:
                promoted is None
            if promoted:
                assert self._record_promotions(promoted, uid)

            try:
                tag_progress['name'] = uid
                condition = {'name': uid}
                db.tag_progress.update_or_insert(condition, **tag_progress)
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
                           got_right, score, now=None):
        """
        """
        now = datetime.datetime.utcnow() if not now else now
        oldrec = oldrec if not isinstance(oldrec, list) else oldrec[0]  # FIXME
        tlright = now
        tlwrong = now
        db = current.db
        newdata = {'name': user_id,
                   'tag': tag,
                   'times_right': tright,
                   'times_wrong': twrong,
                   'tlast_right': tlright,
                   'tlast_wrong': tlwrong}
        try:
            if got_right:
                newdata['tlast_wrong'] = oldrec['tlast_wrong']
            else:
                newdata['tlast_right'] = oldrec['tlast_right']
            if not oldrec['times_right']:
                oldrec['times_right'] = 0
            if not oldrec['times_wrong']:
                oldrec['times_wrong'] = 0
            newdata['times_right'] += oldrec['times_right']
            newdata['times_wrong'] += oldrec['times_wrong']

            #  FIXME: temporary fix for bad tright/twrong data
            newdata = self._add_from_logs(tag, user_id, newdata, tright,
                                          twrong, got_right)
        except TypeError:  # because no oldrec
            pass

        db.tag_records.update_or_insert((db.tag_records.tag == tag) &
                                        (db.tag_records.name == user_id),
                                        **newdata)
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
        got_right = True if ((score - 1) < 0.01) else False  # float inaccuracy

        for t in taglist['primary']:
            oldrec = [r for r in old_trecs
                      if r['tag'] == t] if old_trecs else None
            self._update_tag_record(t, oldrec, user_id, raw_tright, raw_twrong,
                                    got_right, score, now=mynow)
        if got_right and ('secondary' in taglist.keys()):
            for t in taglist['secondary']:
                oldrec = [r for r in old_trecs
                          if r['tag'] == t] if old_trecs else None
                self._update_tag_secondary(t, oldrec, user_id, now=mynow)

        log_args = {'name': user_id,
                    'step': step_id,
                    'in_path': path_id,
                    'score': score,
                    'user_response': response_string}  # time automatic in db
        log_record_id = db.attempt_log.insert(**log_args)
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
        response_string = response_string.decode('utf-8')
        response_string = response_string.encode('utf-8')
        vardict = {'answer': response_string,
                   'loc_id': loc_id,
                   'log_id': record_id,
                   'path_id': path_id,
                   'score': score,
                   'step_id': step_id}
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
        """Return a list of the location id's for this step."""
        db = current.db
        return [l for l in self.data['locations']
                if db.locations[l].loc_active is True]

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

    def get_prompt(self, location, npc, username, raw_prompt=None):
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
        raw_prompt = self.data['prompt'] if not raw_prompt else raw_prompt
        prompt = {'sid': self.get_id(),
                  'prompt_text': self._make_replacements(raw_prompt, username),
                  'audio': self._get_prompt_audio(),
                  'widget_img': self._get_widget_image(),
                  'instructions': self._get_instructions(),
                  'slidedecks': self._get_slides(),
                  'bg_image': location.get_bg(),
                  'loc': location.get_alias(),
                  'response_buttons': ['map'],
                  'response_form': None,
                  'bugreporter': None}
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

        new_string = raw_prompt
        for k, v in reps.iteritems():
            if not v:
                v = ''
            new_string = new_string.replace(k, v)
        # FIXME: this is a bit of a hack to handle embedded html better
        if appds:
            new_string = DIV(new_string)
            for k, v in appds.iteritems():
                if not v:
                    v = ''
                new_string[0] = new_string[0].replace(k, '')
                new_string.append(v)

        return new_string

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
                    print traceback.format_exc(5)
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

                    pick = npc_list[randrange(len(npc_list))]

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
    def get_prompt(self, loc, npc, username):
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
    def get_prompt(self, loc, npc, username):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        prompt = super(StepRedirect, self).get_prompt(loc, npc, username)
        prompt['response_buttons'] = ['map', 'continue']
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
        new_string = super(StepRedirect, self)._make_replacements(raw_prompt,
                                                                  username,
                                                                  reps=reps)
        return new_string


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
        newstr = super(StepQuotaReached, self)._make_replacements(raw_prompt,
                                                                  username,
                                                                  reps=reps)
        return newstr


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
                    ranknum = int(rank.replace('cat', ''))
                    label = ranks[ranknum - 1]
                    for l in lst:
                        bname = [row['badge_name'] for row in prom_records
                                if row['tag'] == l][0]
                        line = '- {} {}\r\n'.format(label, bname)
                        prom_rep += line
        appds['[[promoted_list]]'] = prom_rep

        conj = 'You'
        nt_rep = ''
        if new_tags:
            conj = 'and you'
            nt_records = db(db.badges.tag.belongs(new_tags)
                            ).select(db.badges.tag, db.badges.badge_name).as_list()
            if nt_records:
                nt_rep = '{}\'re ready to start working on some new ' \
                         'badges:\r\n'.format(conj)
                for p in [t for t in new_tags if t]:
                    bname = [row['badge_name'] for row in nt_records
                             if row['tag'] == p][0]
                    line = '- beginner {}\r\n'.format(bname)
                    nt_rep += line
        nt_rep += 'You can click on your name above to see details ' \
                  'of your progress so far.'
        appds['[[new_tag_list]]'] = nt_rep
        newstr = super(StepAwardBadges, self
                       )._make_replacements(raw_prompt, username,
                                            reps=reps, appds=appds)
        return newstr


class StepViewSlides(Step):
    '''
    A Step that informs the user when s/he needs to view more grammar slides.
    '''

    def _make_replacements(self, raw_prompt, username):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].

        new_tags value should be a list of tag id's as integers
        """
        db = current.db
        new_tags = self.kwargs['new_tags']
        tags = db((db.tags.id == db.badges.tag) &
                (db.tags.id.belongs(new_tags))).select().as_list()

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
        slides = UL(_class='slide_list')
        for row in sliderows:
            slides.append(LI(A(row.deck_name,
                               _href=URL('listing', 'slides.html',
                                         args=[row['id']])
                               )))

        # collect replacements
        appds = {'[[slide_list]]': slides}
        newstr = super(StepViewSlides, self
                       )._make_replacements(raw_prompt, username, appds=appds)
        return newstr


class StepText(Step):
    """
    A subclass of Step that adds a form to receive user input and evaluation of
    that input. Handles only a single string response.
    """

    def get_prompt(self, location, npc, username):
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
        form = SQLFORM.factory(Field('response', 'string',
                                     requires=IS_NOT_EMPTY()),
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
        """
        if not user_response:
            request = current.request
            user_response = request.vars['response']
        user_response = user_response.strip()
        responses = {k: r for k, r in self.responses.iteritems()
                     if r and r != 'null'}
        # Compare the student's response to the regular expressions
        try:
            if re.match(responses['response1'], user_response, re.I | re.U):
                score = 1
                reply = "Right. Κάλον."
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
            # FIXME: is there still a view for this?
            redirect(URL('index', args=['error', 'regex']))
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
                return True
            else:
                print 'in _prepare_for_prompt: ', len(self.steps), 'steps remain'
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
        Return all completed steps to the self.steps list.

        Intended to prepare for repeating an already-completed step.
        """
        if self.completed_steps:
            self.steps = copy(self.completed_steps)
            self.completed_steps = []
        if len(self.steps) == 0:
            self.steps = self.get_steps(self.username)
            assert len(self.steps) > 0
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

        next_loc = None
        goodlocs = mystep.get_locations()
        if not loc.get_id() in goodlocs:
            next_loc = goodlocs[randrange(len(goodlocs))]
        else:
            mystep.loc = loc  # update location on step

        return (mystep, next_loc)

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
        self.rank = tag_progress['latest_new']
        db = current.db if not db else db
        self.loc_id = loc_id
        self.completed = paths_completed

    def _order_cats(self):
        """
        Choose a category to prefer in path selection and order categories
        beginning with that number.

        Returns a list with four members including the integers one-four.
        """
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

        return cat_list

    def _paths_by_category(self, cat, rank):
        """
        Assemble list of paths tagged with tags in each category for this user.

        Returns a dictionary with categories as keys and corresponding lists
        as values.
        """
        db = current.db
        # TODO: set up computed field
        # if not db(db.paths).select().first().path_tags:
        # for row in db(db.paths.id > 0).select():
        # db(db.paths.id == row.id).update(steps=row.steps)
        # TODO: include paths with tag as secondary, maybe in second list
        # TODO: cache the select below and just re-order randomly
        taglist = self.categories['rev{}'.format(cat)]

        allpaths = db(db.paths.id > 0).select()
        pathset = allpaths.find(lambda row: any([t for t in row.tags_for_steps
                                                 if t in taglist]))
        # pathset.exclude(lambda row: any([t for s in row.steps
        # for t in db.steps[s].tags
        # if db.tags[t].tag_position > rank]))
        pathset = pathset.find(lambda row: len(row.steps) > 0 and
                                           all([s for s in row.steps
                                                if (db.steps[s].status != 2)]))
        pathset = pathset.find(lambda row: all([db.steps[s].locations for s
                                                in row.steps]))
        pathset = pathset.as_list()

        return (pathset, cat)

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
        """
        loc_id = self.loc_id
        db = current.db

        p_new = [p for p in cpaths if p['id'] not in self.completed]
        p_here = [p for p in cpaths
                  if loc_id in db.steps[int(p['steps'][0])].locations]
        p_here_new = [p for p in p_here if p in p_new]

        path = None
        new_loc = None
        mode = None
        if p_here_new:
            # FIXME: does this loop make sense???
            for p in p_here_new:
                path = p_here_new[randrange(0, len(p_here_new))]
            mode = 'here_new'
        elif p_new:
            # While loop safeguards against looking for location for a step
            # that has no locations assigned.
            while path is None:
                try:
                    idx = randrange(0, len(p_new))
                    path = p_new[idx]
                    new_locs = db.steps(path['steps'][0]).locations
                    new_loc = new_locs[randrange(0, len(new_locs))]
                except TypeError:
                    path = None
            mode = 'new_elsewhere'
        elif p_here:
            path = p_here[randrange(0, len(p_here))]
            mode = 'repeat_here'

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

        cat_list = [c for c in self._order_cats()
                    if self.categories['rev{}'.format(c)]]

        # cycle through categories, starting with the one from _get_category()
        for cat in cat_list:
            catpaths, category = self._paths_by_category(cat, self.rank)
            if len(catpaths):
                path, newloc, category, mode = self._choose_from_cat(catpaths,
                                                                     category)
                return path, newloc, category, mode
            else:
                continue
        return False


class User(object):
    """
    An object representing the current user, including his/her performance
    data and the paths completed and active in this session.

    """

    def __init__(self, userdata, tag_records, tag_progress, blocks=[]):
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
            self.blocks = blocks  # FIXME: somehow pass previous day's blocks in user._is_stale()?
            self.name = userdata['first_name']
            self.user_id = userdata['id']

            self.path = None
            self.completed_paths = []

            self.cats_counter = 0  # timing re-categorization in get_categories()

            self.old_categories = {}
            self.categories = None
            self.tag_records = tag_records
            self.rank = tag_progress['latest_new'] if tag_progress else 1
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
            except Exception:
                print traceback.format_exc(5)
                target = 20
            self.quota = target

            self.past_quota = False
            self.viewed_slides = False
            self.reported_badges = False
        except Exception:
            print traceback.format_exc(5)

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
            self.blocks = blockset
            myblock = self.blocks.pop(0)
            return myblock
        else:
            return None

    def set_block(self, condition, kwargs=None):
        """ Set a blocking condition on this Path object. """
        myblocks = [b.get_condition() for b in self.blocks]

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
            _inner_set_block()

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

    def _make_path_choice(self, loc):
        """
        Instantiate PathChooser and return the result of its choose() method.
        """
        choice = None
        if self.path:  # TODO: do I want this catch here?
            self.complete_path()  # catch end-of-path and triggers new choice
        if not self.tag_progress:  # in case User was badly initialized
            self.get_categories()
        while not choice:
            choice, redir, cat, mode = PathChooser(self.tag_progress,
                                                   loc.get_id(),
                                                   self.completed_paths).choose()
            # FIXME: if no choice, send_error('User', 'get_path', current.request)
        path = Path(path_id=choice['id'])
        return path, redir, cat

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

        if pathid:  # testing specific path
            self.path = Path(pathid)
        if repeat and not self.path:  # repeating a step, path finished before
            pathid = self.completed_paths.pop(-1)
            self.path = Path(pathid)
        # TODO: rationalize this series of conditions
        elif self.path and self.path.step_for_reply:
            pass
        elif self.path and repeat:  # repeating a step, path wasn't finished
            pass
        elif self.path and len(self.path.steps):  # unfinished step in self.path
            pass
        else:  # choosing a new path
            self.path, redir, cat = self._make_path_choice(loc)

        if len(self.completed_paths) >= self.quota and self.past_quota is False:
            pastq = True
            self.past_quota = True
        if len(self.blocks) > 0:
            # FIXME: This hack is to work around mysterious introduction of
            # redirect block after initial redirect has been triggered
            self.blocks = [b for b in self.blocks
                           if not b.get_condition() is 'redirect']
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
        db = current.db
        user_id = self.user_id if not user_id else user_id
        if not tag_records:
            tag_records = db(db.tag_records.name == user_id).select().as_list()
        self.tag_records = tag_records

        if (self.cats_counter in range(0, 4)) \
                and hasattr(self, 'categories') \
                and self.categories:
            self.cats_counter += 1
            return None, None
        else:
            utcnow = datetime.datetime.utcnow() if not utcnow else utcnow
            try:
                tag_progress_sel = db(db.tag_progress.name == user_id
                                      ).select()
                assert len(tag_progress_sel) == 1
                self.tag_progress = tag_progress_sel.first().as_dict()
                rank = self.tag_progress['latest_new']
                # TODO: below is 'magic' hack based on specific db field names
                categories = {k: v for k, v in self.tag_progress.iteritems()
                              if k[:4] in ['cat', 'rev']}
            except (AttributeError, AssertionError):
                categories = None
            self.old_categories = copy(categories)

            c = Categorizer(rank, categories, tag_records, user_id,
                            utcnow=utcnow)
            cat_result = c.categorize_tags()
            self.rank = cat_result['tag_progress']['latest_new']
            self.tag_records = cat_result['tag_records']  # FIXME: do changes get recorded?
            self.tag_progress = cat_result['tag_progress']
            self.categories = cat_result['categories']
            self.promoted = cat_result['promoted']
            self.new_tags = cat_result['new_tags']
            self.cats_counter = 0  # reset counter

            return self.promoted, self.new_tags

    def complete_path(self):
        """
        Move the current path from the path variable to 'completed_paths' list.
        Set last_npc and prev_loc before removing the path.
        """
        # Only id of paths stored to conserve memory.
        # prev_loc and prev_user info not drawn from old paths but
        # carried on User.
        # Repeating path must be triggered before path is completed.
        self.completed_paths.append(self.path.get_id())
        self.path = None
        return True


class Categorizer(object):
    """
    A class that categorizes a user's active tags based on past performance.

    The categories range from 1 (need immediate review) to 4 (no review
    needed). Returns a dictionary with four keys corresponding to the four
    categories. The value for each key is a list holding the id's
    (integers) of the tags that are currently in the given category.
    """

    def __init__(self, rank, categories, tag_records, user_id,
                 secondary_right=None, utcnow=None, db=None):
        """Initialize a paideia.Categorizer object"""
        self.db = current.db if not db else db
        self.user_id = user_id
        self.rank = rank
        self.tag_records = tag_records
        self.old_categories = categories
        self.utcnow = utcnow if utcnow else datetime.datetime.utcnow()
        self.secondary_right = secondary_right

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
        tag_records = self.tag_records if not tag_records else tag_records
        tag_records = self._sanitize_recs(tag_records)
        db = current.db if not db else db
        new_tags = None

        # if user has not tried any tags yet, start first set
        if len(tag_records) == 0:
            categories = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
            categories['cat1'] = self._introduce_tags(rank=0)
            tp = {'cat1': categories['cat1'], 'rev1': categories['cat1'],
                  'cat2': [], 'rev2': [],
                  'cat3': [], 'rev3': [],
                  'cat4': [], 'rev4': [],
                  'latest_new': rank}
            return {'tag_progress': tp,
                    'tag_records': tag_records,
                    'new_tags': categories['cat1'],
                    'promoted': None,
                    'demoted': None,
                    'categories': categories}
        else:
            # otherwise, categorize tags that have been tried
            for idx, t in enumerate([t for t in tag_records
                                     if tag_records and t['secondary_right']]):
                tag_records[idx] = self._add_secondary_right(t)
            self.tag_records = tag_records
            categories = self._core_algorithm()
            categories = self._add_untried_tags(categories)
            categories = self._remove_dups(categories, rank)
            categories.update((c, []) for c in ['rev1', 'rev2', 'rev3', 'rev4'])
            cat_changes = self._find_cat_changes(categories, old_categories)
            promoted = cat_changes['promoted']
            demoted = cat_changes['demoted']
            new_tags = cat_changes['new_tags']
            tag_progress = copy(cat_changes['categories'])

            # If there are no tags left in category 1, introduce next set
            if not tag_progress['cat1']:
                newlist = self._introduce_tags()
                categories['cat1'] = categories['rev1'] = newlist
                tag_progress['cat1'] = tag_progress['rev1'] = newlist
                new_tags = newlist if not new_tags else new_tags.extend(newlist)

            # Re-insert 'latest new' to match tag_progress table in db
            tag_progress['latest_new'] = self.rank

            return {'tag_progress': tag_progress,
                    'tag_records': self.tag_records,
                    'new_tags': new_tags,
                    'promoted': promoted,
                    'demoted': demoted,
                    'categories': categories}

    def _remove_dups(self, categories, rank):
        """
        Remove any duplicate tags and any tags beyond user's current rank.
        """
        db = current.db
        for k, v in categories.iteritems():
            if v:
                rankv = [t for t in v if db.tags(t)
                        and (db.tags[t].tag_position <= rank)]
                categories[k] = list(set(rankv))
        return categories

    def _add_secondary_right(self, rec):
        """
        Finds tag records with secondary attempts and adjusts records.

        For every 3 secondary_right entries, add 1 to times_right and change
        tlast_right based on the average of those three attempt dates.
        """
        db = current.db
        rec = rec[0] if isinstance(rec, list) else rec
        right2 = flatten(rec['secondary_right'])  # FIXME: sanitizing data
        for t in right2:
            try:
                right2[right2.index(t)] = parser.parse(t)
            except TypeError:
                pass
        if right2 != rec['secondary_right']:  # FIXME: can remove when data clean
            right2.sort()
            db.tag_records[rec['id']].update(secondary_right=right2)

        rlen = len(right2)
        rem2 = rlen % 3

        if rlen >= 3:
            # increment times_right by 1 per 3 secondary_right
            triplets2 = rlen / 3
            if not rec['times_right']:
                rec['times_right'] = 0
            rec['times_right'] += triplets2

            # move tlast_right forward based on mean of oldest 3 secondary_right
            early3 = right2[: -(rem2)] if rem2 else right2[:]
            early3d = [self.utcnow - s for s in early3]
            avg_delta = sum(early3d, datetime.timedelta(0)) / len(early3d)
            avg_date = self.utcnow - avg_delta

            # sanitize tlast_right in case db value is string
            if not isinstance(rec['tlast_right'], datetime.datetime):
                rec['tlast_right'] = parser.parse(rec['tlast_right'])

            # move tlast_right forward to reflect recent secondary success
            if avg_date > rec['tlast_right']:
                rec['tlast_right'] = avg_date

            rec['secondary_right'] = right2[-(rem2):] if rem2 else []
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
        categories = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        tag_records = tag_records if tag_records else self.tag_records
        for record in tag_records:
            lrraw = record['tlast_right']
            lwraw = record['tlast_wrong']
            lr = lrraw if not isinstance(lrraw, str) else parser.parse(lrraw)
            lw = lwraw if not isinstance(lwraw, str) else parser.parse(lwraw)
            rdur = self.utcnow - lr
            rwdur = lr - lw

            # spaced repetition algorithm for promotion to
            # cat2? ======================================================
            if ((record['times_right'] >= 20) and  # at least 20 right
                (((rdur < rwdur)  # delta right < delta right/wrong
                  and (rwdur > datetime.timedelta(days=1))  # not within 1 day
                  )
                 or
                 ((self._get_ratio(record) < 0.2)  # less than 1w to 5r total
                  and (rdur <= datetime.timedelta(days=30))  # right in past 30 days
                  )
                 or
                 ((self._get_avg(record['tag']) >= 0.8)  # avg score for week >= 0.8
                  and (rdur <= datetime.timedelta(days=30))  # right in past 30 days
                  ))):
                # cat3? ==================================================
                if rwdur.days >= 14:
                    # cat4? ==============================================
                    if rwdur.days > 60:
                        # long-term review? ===================================
                        if rwdur > datetime.timedelta(days=180):
                            category = 'cat1'  # Not tried for 6 months
                        else:
                            category = 'cat4'  # Not due, delta > 60 days
                    else:
                        category = 'cat3'  # delta between 14 and 60 days
                else:
                    category = 'cat2'  # Not due but delta is 2 weeks or less
            else:
                category = 'cat1'  # Spaced repetition requires review

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
            categories['cat1'].extend(left_out)
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
                       if k[:3] == 'cat'}  # facilitates demotion tasks
            new_tags = []
            cnms = ['cat1', 'cat2', 'cat3', 'cat4']
            # TODO: cleaning up bad data; deprecate after finished
            oldcats = self._fix_oldcats(oldcats, uid, bbrows=bbrows)

            for cat, taglist in cats.iteritems():
                revcat = cat.replace('cat', 'rev')
                cats[revcat] = taglist[:]  # copy bc demotion only changes one
                if taglist and cat in cnms:
                    # Is tag completely new to this user?
                    all_old_tags = list(chain.from_iterable(oldcats.values()))
                    new_tags.extend([t for t in taglist if t not in all_old_tags])

                    # was tag in a lower category before?
                    idx = cnms.index(cat)
                    was_lower = list(chain.from_iterable([oldcats[c] for c
                                                          in cnms[:idx]
                                                          if oldcats[c]]))
                    promoted[cat] = [t for t in cats[cat] if t in was_lower]

                    # was tag in a higher category before?
                    was_higher = list(chain.from_iterable([oldcats[c] for c
                                                           in cnms[idx + 1:]
                                                           if oldcats[c]]))
                    demoted[cat] = [t for t in taglist if t in was_higher]

            if any([k for k, v in demoted.iteritems() if v]):
                for tag in list(chain.from_iterable(demoted.values())):  # then restore old max in cats
                    current = [k for k, v in demoted.iteritems()
                                if v and tag in v and k in cnms][0]
                    oldmax = [k for k, v in oldcats.iteritems()
                                if v and tag in v][0]
                    tagindex = cats[current].index(tag)
                    cats[current].pop(tagindex)
                    cats[oldmax].append(tag)
            return {'categories': cats,
                    'demoted': demoted if any([d for d in demoted.values()])
                               else None,
                    'promoted': promoted if any([p for p in promoted.values()])
                               else None,
                    'new_tags': new_tags}
        else:
            cats['rev1'] = cats['cat1'][:]
            new_tags = cats['cat1'][:]
            return {'categories': cats,
                    'demoted': None,
                    'promoted': None,
                    'new_tags': new_tags}

    def _clean_tag_records(record_list=None, db=None):
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
        return mystep

    def get_condition(self):
        """Return a string representing the condition causing this block."""
        return self.condition

    def get_step(self):
        """Return the appropriate step for the current blocking condition"""
        step = self.make_step(self.get_condition())
        return step
