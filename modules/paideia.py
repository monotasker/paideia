# -*- coding: utf-8 -*-
from gluon import current, redirect
from gluon import IMG, URL, SQLFORM, SPAN, DIV, UL, LI, A, Field, P, TAG, HTML
from gluon import I
from gluon import IS_NOT_EMPTY, IS_IN_SET

from inspect import getargvalues, stack
from copy import copy
from itertools import chain
from random import randint, randrange
import re
import datetime
from dateutil import parser
import traceback
from pytz import timezone
from plugin_widgets import POPOVER, ROLE
import pickle
#from pprint import pprint
from paideia_utils import send_error

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
                 new_user=None, shadow=None):
        """Initialize a Walk object."""
        db = current.db if not db else db
        # TODO: fix redundant db call here
        self.response_string = response_string
        # TODO: move retrieval of data to user init so it's not duplicated when
        # just retrieving existing User.
        self.user = self._get_user(userdata=userdata,
                                   tag_records=tag_records,
                                   tag_progress=tag_progress,
                                   new_user=new_user,
                                   shadow=shadow)
        # TODO is record_id necessary?
        self.record_id = None  # stores step log row id after db update

    def _get_user(self, userdata=None, tag_records=None,
                  tag_progress=None, new_user=None, shadow=None):
        '''
        Initialize or re-activate User object.
        All named arguments are necessary.
        '''
        auth = current.auth
        db = current.db
        try:
            assert self.user and not new_user
            print 'walk.get_user: retrieved user in memory'
            pass
        except AttributeError:  # because no user yet on this Walk
            try:
                sd = db(db.session_data.name ==
                        auth.user_id).select().first()
                if sd:
                    self.user = pickle.loads(sd['other_data'])
                else:
                    self.user = None
                print 'walk.get_user: retrieved user from db'
                assert self.user.is_stale() is False
                print 'walk.get_user: new_user is', new_user
                assert not new_user
                assert not shadow
            except (AssertionError, AttributeError):
                uid = auth.user_id if not shadow else shadow
                userdata = db.auth_user[uid] if not userdata else userdata
                userdata = userdata.as_dict()

                # because no user yet in db, user is stale, or flags present
                # (new_user or shadow)
                if not tag_records:
                    tag_records = db(db.tag_records.name == uid).select().as_list()
                if not tag_progress:
                    tag_progress = db(db.tag_progress.name == uid).select().first()
                    if not tag_progress and not shadow:
                        db.tag_progress.insert(latest_new=1)
                        tag_progress = db(db.tag_progress.name == uid).select().first()
                    tag_progress = tag_progress.as_dict()

                print 'walk.get_user: creating new user'
                self.user = User(userdata, tag_records, tag_progress)
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
                                  response_string=response_string,
                                  set_blocks=set_blocks)
            else:
                return self.ask(localias=localias,
                                path=path,
                                repeat=repeat,
                                set_blocks=set_blocks,
                                recategorize=recategorize,
                                step=step)
        except Exception:
            print traceback.format_exc(5)
            self.clean_user()  # get rid of path data if that's the problem
            return self.ask(localias=localias, path=path, step=step)

    def clean_user(self):
        """
        In case of irrecoverable conflict in user data, remove all path/steps.
        """
        print '\n error, cleaning user--------------------------------------\n'
        user = self._get_user()
        user.path = None
        self._store_user(user)

    def ask(self, localias=None, path=None, repeat=None,
            step=None, set_blocks=None, recategorize=None,
            shadow=None):
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
        db = current.db
        user = self.user
        # allow artificial setting of blocks during interface testing
        if set_blocks:
            for c, v in set_blocks.iteritems():
                myargs = {n: a for n, a in v.iteritems()}
                user._set_block(c, kwargs=myargs)
        user.get_categories(user_id=user.get_id())

        # FIXME: fix redundant db call here by sending localias to Loc() instead of id
        loc_id = db(db.locations.loc_alias == localias).select().first().id
        loc = Location(loc_id)
        user.set_location(loc)  # called only in ask?

        p = user.get_path(path=path, repeat=repeat)
        print 'walk.ask: got path', p.get_id()
        s, newloc_id = p.get_step_for_prompt(repeat=repeat)
        print 'walk.ask: got step', s.get_id()
        if newloc_id:
            user._set_block('redirect', kwargs={'next_loc': newloc_id})

        # TODO: make sure 'new_tags' is returned before 'view_slides'
        block = user.check_for_blocks()
        if block:
            condition = block.get_condition()
            print 'walk.ask: activating block,', condition
            # FIXME: necessary because p.step_for_reply is lost in step
            # activation?
            #if s.get_id() not in p.steps:
                #p.steps.insert(0, copy(s))
            #print 'walk.ask: p.steps restored to', p.steps
            if condition in ['new_tags', 'view_slides']:
                if not block.kwargs['new_tags']:
                    block.kwargs['new_tags'] = user.new_tags
                if ('promoted' in block.kwargs.keys()) and \
                   (block.kwargs['promoted'] is None):
                    block.kwargs['promoted'] = user.promoted
            s = block.get_step(**{'prev_loc': user.prev_loc,
                                  'prev_npc': user.prev_npc,
                                  'loc': user.loc,
                                  'npc': user.npc})
            print 'walk.ask: got block step', s.get_id()
            try:
                print 'walk.ask: path.step_for_prompt is still', p.step_for_prompt.get_id()
            except AttributeError:
                print 'walk.ask: path.step_for_prompt is None'

        npc = s.get_npc(prev_npc=user.prev_npc, prev_loc=user.prev_loc)
        print 'walk.ask: got npc', npc.get_id()
        user.set_npc(npc)
        if user.prev_npc:
            print 'walk.ask: user.prev_npc is now', user.prev_npc.get_id()
        else:
            print 'no previous npc'

        # get data to send to view
        prompt = s.get_prompt()
        progress = 'This will make {} paths so far today.'.format(len(user.completed_paths) + 1)
        responder = s.get_responder()
        responder.append(SPAN(progress, _class='progress_text'))

        # info for admin and debugging
        try:
            editlinks = self._get_editlinks(p.get_id(), s.get_id())
            responder.append(editlinks)
        except Exception:
            pass

        # clean up before return
        if type(s) not in [StepRedirect, StepQuotaReached, StepAwardBadges, StepViewSlides]:
            # only move prompt step to reply step (or to steps completed) if
            # its a content step
            assert p.end_prompt()  # non-response steps end here
            print 'walk.ask: ended prompt'
        else:
            print 'walk.ask: info step, prompt doesn\'t need ending'
        self._store_user(user)

        print 'walk.ask: user.loc is', user.loc.get_id()
        try:
            print 'walk.ask: user.prev_loc is', user.prev_loc.get_id()
        except:
            pass

        #if p:
            #print 'walk.ask: final path is', p.get_id()
            #if p.step_for_reply:
                #print 'walk.ask: final step_for_reply is', p.step_for_reply.get_id()
            #else:
                #print 'walk.ask: final step_for_reply is None'
            #print 'walk.ask: final step_for_prompt is', p.step_for_prompt
        #else:
            #print 'walk.ask: no final path'
        #if hasattr(p, 'blocks'):
            #print 'walk.ask: final blocks on p is', [b for b in p.blocks]
        print 'END OF WALK.ASK'
        print '==============================\n'

        return {'npc': prompt, 'responder': responder}

    def reply(self, localias, response_string, path=None,
              step=None, set_blocks=None):
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
        db = current.db
        user = self._get_user()
        user_id = user.get_id()
        # allow manual setting of blocks for testing
        if set_blocks:
            for c, v in set_blocks.iteritems():
                myargs = {n: a for n, a in v.iteritems()}
                user._set_block(c, kwargs=myargs)

        #print 'walk.reply: localias is', localias
        loc_id = db(db.locations.loc_alias == localias).select().first().id
        if loc_id != user.loc.get_id():
            #print 'walk.reply: different id than for prompt, updating'
            loc = Location(loc_id)
            user.set_location(loc)
            #print 'walk.reply: set user.loc to', user.loc.get_id()

        p = user.get_path(reply=True)
        #print 'walk.reply: path is', p.get_id()
        #print 'walk.reply: p.step_for_reply is', p.step_for_reply.get_id()
        s = p.get_step_for_reply()
        #print 'walk.reply: step is', s.get_id()

        # make sure there's a response to evaluate
        if (not response_string) or re.match(response_string, r'\s+'):
            print 'walk.reply: no response string, re-prompting'
            return self.ask()  # TODO: will this actually re-prompt the same step?

        # TODO: should blocks be checked at all in reply()?
        # FIXME: find a way to recognize changed npc without losing previous
        # step's npc
        # separate method to set_prev_npc that in turn calls set_npc.
        # call the former in ask, but only the latter in reply.
        #user.set_npc(mynpc[0])  # since npc decision has to follow step choice

        reply = s.get_reply(response_string)  # evaluate user response

        # record data for this step in db
        assert self._record_cats(user.tag_progress, user.promoted, user.new_tags)
        self.record_id = self._record_step(user_id,
                                           p.get_id(),
                                           s.get_id(),
                                           reply['score'],
                                           reply['times_right'],
                                           reply['times_wrong'],
                                           user.tag_records,
                                           s.get_tags(),
                                           response_string)
        assert self.record_id

        bug_reporter = BugReporter().get_reporter(self.record_id, p.get_id(),
                                                  s.get_id(), reply['score'],
                                                  response_string,
                                                  user.loc.get_alias())
        responder = s.get_final_responder(localias=user.loc.get_alias(),
                                          bug_reporter=bug_reporter)
        progress = 'This will make {} paths ' \
                   'so far today.'.format(len(user.completed_paths) + 1)
        responder.append(SPAN(progress, _class='progress_text'))

        # info for admin and debugging
        try:
            editlinks = self._get_editlinks(p.get_id(), s.get_id())
            responder.append(editlinks)
        except Exception:
            pass

        p.complete_step()  # removes path.step_for_reply
        # Note: path is completed (moved to user.completed_paths) in following
        # cycle in user.get_path. This simplifies repeating steps/paths
        # considerably.
        self._store_user(user)

        return {'npc': reply, 'responder': responder}

    def _get_editlinks(self, pid, sid):
        """
        Return an html helper object with links to edit current path and step.
        """
        stepedit = A('step {}'.format(sid),
                     _href=URL('editing', 'listing', args=['steps', sid]),
                     _class='prompt-s-editlink'
                     )
        pathedit = A('path {}'.format(pid),
                     _href=URL('editing', 'listing', args=['paths', pid]),
                     _class='prompt-p-editlink'
                     )
        links = ROLE(SPAN(pathedit, ', ', stepedit, _class='prompt-editlinks'))
        return links

    def _record_cats(self, tag_progress, promoted,
                     new_tags, db=None):
        """
        Record changes to the user's working tags and their categorization.

        Changes recorded in the following db tables:
        - badges_begun: new and promoted tags
        - tag_progress: changes to categorization (only if changes made)
        """
        db = current.db if not db else db
        auth = current.auth
        user_id = self.user.get_id()
        if user_id == auth.user_id:
            now = datetime.datetime.utcnow()
            # TODO: make sure promoted and new_tags info is passed on correctly

            # combine promoted and new_tags for recording purposes
            if promoted:
                promoted['cat1'] = new_tags
            elif new_tags:
                promoted = {'cat1': new_tags}
            else:
                promoted is None

            # record awarding of promoted and new tags in table db.badges_begun
            if promoted:
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
                except Exception:
                    print traceback.format_exc(5)
                    return False

            # update tag_progress table with current categorization
            try:
                db.tag_progress.update_or_insert(db.tag_progress.name == user_id,
                                                **tag_progress)
                mycount = db(db.tag_progress.name == user_id).count()
                assert mycount == 1  # ensure there's never a duplicate
                # TODO: eliminate need for this check by making name field unique
            except Exception:
                print traceback.format_exc(5)
                return False
            return True
        else:  # auth.user_id != user_id because shadowing another user
            return False

    def _record_step(self, user_id, step_id, path_id, score, times_right,
                     times_wrong, old_trecs, taglist, response_string):
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
        #print 'walk.record_step: starting locals are', pprint(locals())
        db = current.db
        auth = current.auth
        if user_id != auth.user_id:  # shadowing another user
            return False
        else:
            now = datetime.datetime.utcnow()
            # TODO: should the threshold here be less than 1 for 'right'?
            got_right = True if ((score - 1) < 0.01) else False  # because of float inaccuracy
            for t in taglist['primary']:
                #print 'walk.record_step: recording tag', t
                oldrec = [r for r in old_trecs if r['tag'] == t] if old_trecs else None
                #print 'walk.record_step: old record is', pprint(oldrec)
                if oldrec:
                    tlast_wrong = oldrec[0]['tlast_wrong']
                    tlast_right = oldrec[0]['tlast_right']
                    try:  # in case oldrec is None, created for secondary right
                        times_right = oldrec[0]['times_right'] + times_right
                    except TypeError:
                        pass
                    try:  # in case oldrec is None, created for secondary right
                        times_wrong = oldrec[0]['times_wrong'] + times_wrong
                    except TypeError:
                        pass
                    if got_right:  # because of float inaccuracy
                        tlast_right = now
                    else:
                        tlast_wrong = now
                else:  # if no existing record, just set both to now as initial baseline
                    tlast_wrong = now
                    tlast_right = now
                #print 'walk.record_step: times right', times_right
                #print 'walk.record_step: times wrong', times_wrong
                #print 'walk.record_step: tlast_right', tlast_right
                #print 'walk.record_step: tlast_wrong', tlast_wrong

                condition = {'tag': t, 'name': user_id}
                db.tag_records.update_or_insert(condition,
                                                tag=t,
                                                times_right=times_right,
                                                times_wrong=times_wrong,
                                                tlast_right=tlast_right,
                                                tlast_wrong=tlast_wrong)

            if got_right and ('secondary' in taglist.keys()):
                for t in taglist['secondary']:
                    #print 'walk.record_step: appending sec right to tag', t
                    oldrec = [r for r in old_trecs if r['tag'] == t]
                    #print 'oldrec is ', pprint(oldrec)

                    sec_right = [now]  # default
                    if len(oldrec) and oldrec[0]:
                        sec_right = oldrec[0]['secondary_right']
                        #print 'secright is ', pprint(oldrec)
                        try:
                            sec_right.append(now)
                        except AttributeError:  # because secondary_right is None
                            pass  # use default set above

                    condition = {'tag': t, 'name': user_id}
                    db.tag_records.update_or_insert(condition,
                                                    tag=t,
                                                    secondary_right=sec_right)

            log_args = {'name': user_id,
                        'step': step_id,
                        'in_path': path_id,
                        'score': score}  # time recorded automatically in table
            log_record_id = db.attempt_log.insert(**log_args)

            return log_record_id

    def _store_user(self, user):
        """
        Store the current User object (from self.user) in session.user

        Returns a boolean value indicating whether the storing was
        successful or not.
        """
        auth = current.auth
        db = current.db

        if user.get_id() != auth.user_id:  # shadowing another user
            return False
        else:
            user = pickle.dumps(self.user)
            db.session_data.update_or_insert(db.session_data.name == auth.user_id,
                                            other_data=user)
            return True


class Location(object):
    """
    Represents a location in the game world.
    """

    def __init__(self, id_num, db=None):
        """Initialize a Location object."""
        db = current.db if not db else db
        self.id_num = id_num
        self.data = db.locations[id_num]

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
            url = URL('static/images', db.images[self.data['bg_image']].image)
            bg = IMG(_src=url)
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
        print 'npc.init: id_num is', id_num
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
        vardict = {'answer': response_string.encode('utf-8'),
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

        br = POPOVER().widget('Something wrong?', c,
                              id='bug_reporter',
                              placement='left')

        return br


class StepFactory(object):
    """
    A factory class allowing automatic generation of correct Step subclasses.

    This allows easy changing/extension of Step classes without having to
    make changes to other application code. At present the decision is made
    based on the "widget_type" field supplied in db.steps. But there is not a
    1:1 relationship between widget type and Step subclass.
    """
    #TODO: does this object need an __init__ method?

    def get_instance(self, db=None, **kwargs):
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
        args = util_get_args()  # get the args and kwargs submitted above
        db = current.db if not db else db
        data = db.steps[locals()['step_id']].as_dict()
        del(args[0]['self'])
        step_classes = {1: StepText,
                        2: StepMultiple,
                        3: Step,
                        4: StepText,
                        5: StepMultiple,
                        6: StepViewSlides,
                        7: StepQuotaReached,
                        8: StepAwardBadges,
                        9: StepRedirect}
        return step_classes[data['widget_type']](**args[0])


class Step(object):
    '''
    This class represents one step (a single question and response
    interaction) in the game.
    '''

    def __init__(self, step_id=None, loc=None, prev_loc=None, prev_npc=None,
                 username=None, promoted=None, new_tags=None, **kwargs):
        """Initialize a paideia.Step object"""
        # basic step data from db
        db = current.db
        self.data = db.steps[step_id].as_dict()

        # flag
        self.repeating = False  # set to true if step already done today

        # set by init args and used for prompt replacements
        self.username = username
        #print 'step.init: self.username is', self.username
        self.promoted = promoted
        #print 'step.init: self.promoted is', self.promoted
        self.new_tags = new_tags
        #print 'step.init: self.new_tags is', self.new_tags

        # set internally or later
        self.npc = None  # must wait since all steps in path init at once
        self.loc = loc
        self.prev_npc = prev_npc
        self.prev_loc = prev_loc
        self.redirect_loc_id = None

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
        print 'locations for step are', self.data['locations']
        return [l for l in self.data['locations']
                if db.locations[l].loc_active is True]

    def _get_slides(self):
        """
        Return a UL helper object listing the slide decks relevant to this step.
        If this step has no associated slides, return False.
        """
        db = current.db
        slide_query = db(db.tags.id.belongs(self.data['tags'])).select()
        if slide_query:
            slides_list = UL(_class='prompt_slides')
            for s in slide_query:
                if s.slides:
                    for d in s.slides:
                        slides_list.append(LI(A(d.deck_name,
                                                _href=URL('listing', 'slides.html',
                                                        args=[d.id]))))
            slides_args = {'classnames': 'btn btn-info slides-popover',
                           'title': 'Relevant slide decks',
                           'id': 'Slides_btn'}
            s_pop = POPOVER().widget('slides',
                                     slides_list,
                                     **slides_args)

            return s_pop
        else:
            return False

    def _get_widget_image(self):
        """
        Return an IMG helper to display the widget image for the current step.
        If this step requires no such image, return False.
        """
        if not self.data['widget_image'] in [9, None]:  # TODO: magic number here:
            db = current.db
            img_row = db.images[self.data['widget_image']]
            image = IMG(_src=URL('static/images/', img_row.image),
                        _title=img_row.title,
                        _alt=img_row.description,
                        _class='widget-image')
            return image
        else:
            return False

    def _get_prompt_audio(self):
        """
        """
        if not self.data['prompt_audio'] in [1, None]:  # TODO: magic number here:
            db = current.db
            aud_row = db.audio[self.data['prompt_audio']]
            audio = TAG.audio('Sorry, your browser doesn\'t support the audio element',
                              _controls='true',
                              _autoplay='true',
                              _id=aud_row['title'],
                              _class='prompt_audio')
            audio.append(TAG.source(_src=aud_row['clip'],
                                    _type='audio/mp3'))
            if aud_row['clip_ogg']:
                audio.append(TAG.source(_src=aud_row['clip_ogg'],
                             _type='audio/ogg'))
            return audio
        else:
            return False

    def get_prompt(self, username=None, raw_prompt=None, **kwargs):
        """
        Return the prompt information for the step. In the Step base class
        this is a simple string. Before returning, though, any necessary
        replacements or randomizations are made.

        If the step cannot be performed in this location, this method returns
        the string 'redirect' so that the Walk.ask() method that called it can
        set a redirect block.
        """
        if not raw_prompt:
            raw_prompt = self.data['prompt']

        prompt = self._make_replacements(raw_prompt=raw_prompt, **kwargs)

        npc_prompt = DIV(_class='npc prompt')

        audio = self._get_prompt_audio()
        if audio:
            npc_prompt.append(audio)

        widget_image = self._get_widget_image()
        if widget_image:
            npc_prompt.append(widget_image)

        npc_prompt.append(P(prompt, _class='prompt-text'))

        instructions = self._get_instructions()
        if instructions:
            npc_prompt.append(instructions)

        slides_list = self._get_slides()
        if slides_list:
            npc_prompt.append(slides_list)

        if isinstance(self.npc, tuple):
            self.npc = self.npc[0]  # TODO: this is a temporary hack for bad data
        npc_image = self.npc.get_image()
        bg_image = self.loc.get_bg()

        return {'npc': npc_prompt,
                'npc_image': npc_image,
                'bg_image': bg_image}

    def _make_replacements(self, raw_prompt=None, reps=None, appds=None):
        """
        Return the provided string with tokens replaced by personalized
        information for the current user.
        """
        if not reps:
            reps = {}
            reps['[[user]]'] = self.username

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

    def get_responder(self):
        """
        Return form providing navigation options after prompt that does not
        require any answer.
        """
        map_button = A("Back to map", _href=URL('walk'),
                       cid='page',
                       _class='btn btn-success icon-map-marker')
        responder = DIV(map_button, _class='responder')
        return responder

    def get_npc(self, prev_npc=None, prev_loc=None):
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
        loc_id = self.loc.get_id()
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
                print 'Step.get_npc: continuing with prev_npc', prev_npc
                self.npc = copy(prev_npc)
            else:
                npc_here_list = [n for n in npc_list if loc_id in db.npcs[n]['map_location']]
                print 'Step.get_npc:', len(npc_list), 'npcs available for step'

                try:
                    pick = npc_here_list[randrange(len(npc_here_list))]
                except ValueError:  # "empty range for randrange()" if no npcs here
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
                    print 'Step.get_npc: no valid npc here for chosen step'

                    pick = npc_list[randrange(len(npc_list))]

                    print 'Step.npc: using fallback npc', pick
                assert pick
                self.npc = Npc(pick)
        return self.npc

    def _get_instructions(self):
        """
        Return an html list containing the instructions for the current
        step. Value is returned as a web2py UL() object.
        """
        db = current.db
        ii = self.data['instructions']
        if ii:
            i_list = UL()
            for i in ii:
                i_text = db.step_instructions[i].instruction_text
                i_list.append(LI(i_text))
            i_args = {'classnames': 'btn btn-info instructions-popover',
                      'title': 'Instructions for this step',
                      'id': 'instructions_btn'}
            i_pop = POPOVER().widget('Instructions',
                                     i_list,
                                     **i_args)
            return i_pop
        else:
            return False


class StepContinue(Step):
    """
    An abstract subclass of Step that adds a 'continue' button to the responder.
    """
    def get_responder(self):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        responder = super(StepContinue, self).get_responder()

        continue_button = A("Continue", _href=URL('walk', args=['ask'],
                            vars={'loc': self.loc.get_alias()}),
                            cid='page',
                            _class='continue btn btn-success')
        responder.append(continue_button)

        return responder


class StepRedirect(Step):
    '''
    A subclass of Step. Handles the user interaction when the user needs to be
    sent to another location.

    This class works best if either the 'next_step_id' (int) or the 'next_loc'
    (int) are supplied. In that case the prompt will direct the user to a
    specific location. Otherwise, the user receives a generic instruction to
    try "another location in town".
    '''
    def __init__(self, step_id=None, step_data=None, loc=None, prev_loc=None,
                 prev_npc=None, username=None, next_step_id=None, next_loc=None,
                 db=None, **kwargs):
        """Initialize a StepRedirect object."""

        assert next_loc
        self.next_loc = next_loc if next_loc else "another location in town"
        # delegate common init tasks to Step superclass
        kwargs = locals()
        del(kwargs['self'])
        super(StepRedirect, self).__init__(**kwargs)

    def _make_replacements(self, raw_prompt=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        db = current.db
        next_loc_name = db.locations[self.next_loc]['readable']

        reps = {'[[next_loc]]': next_loc_name}
        new_string = super(StepRedirect, self)._make_replacements(
            raw_prompt=raw_prompt,
            reps=reps)
        return new_string


class StepQuotaReached(StepContinue, Step):
    '''
    A Step that tells the user s/he has completed the daily minimum # of steps.
    '''
    def _make_replacements(self, raw_prompt=None, username=None, quota=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        reps = None
        new_string = super(StepQuotaReached, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                reps=reps)
        return new_string


class StepAwardBadges(StepContinue, Step):
    '''
    A Step that informs the user when s/he has earned new badges.
    '''

    def _make_replacements(self, raw_prompt=None, db=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        db = current.db if not db else db
        appds = {}
        reps = {}

        prom_rep = ' '
        if self.promoted:
            flat_proms = [i for cat, lst in self.promoted.iteritems() for i in lst if lst]
            prom_records = db(db.badges.tag.belongs(flat_proms)
                              ).select(db.badges.tag,
                                       db.badges.badge_name).as_list()
            if prom_records:
                prom_rep = DIV('You have been promoted to these new badge '
                               'levels:')
                prom_rep.append(UL(_class='promoted_list'))
                ranks = ['beginner', 'apprentice', 'journeyman', 'master']
                for rank, lst in self.promoted.iteritems():
                    if lst:
                        rank = rank.replace('cat', '')
                        i = int(rank) - 1
                        label = ranks[i]
                        for l in lst:
                            bname = [row['badge_name'] for row in prom_records
                                    if row['tag'] == l][0]
                            line = LI(SPAN(label, ' ', bname, _class='badge_name'))
                            prom_rep[1].append(line)
                    else:
                        pass
        appds['[[promoted_list]]'] = prom_rep

        conj = 'You'
        nt_rep = ''
        if self.new_tags:
            conj = 'and you'
            nt_records = db(db.badges.tag.belongs(self.new_tags)
                            ).select(db.badges.tag, db.badges.badge_name).as_list()
            if nt_records:
                nt_rep = DIV('{}\'re ready to start working on some new '
                             'badges:'.format(conj))
                nt_rep.append(UL(_class='new_tags_list'))
                for p in self.new_tags:
                    bname = [row['badge_name'] for row in nt_records
                             if row['tag'] == p][0]
                    line = LI(SPAN('beginner {}'.format(bname),
                                   _class='badge_name'))
                    nt_rep[1].append(line)
        appds['[[new_tag_list]]'] = nt_rep

        new_string = super(StepAwardBadges, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                reps=reps, appds=appds)
        return new_string


class StepViewSlides(Step):
    '''
    A Step that informs the user when s/he needs to view more grammar slides.
    '''

    def _make_replacements(self, raw_prompt=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].

        new_tags value should be a list of tag id's as integers
        """
        db = current.db
        tags = db((db.tags.id == db.badges.tag) &
                  (db.tags.id.belongs(self.new_tags))).select().as_list()

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
        new_string = super(StepViewSlides, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                appds=appds)
        return new_string


class StepText(Step):
    """
    A subclass of Step that adds a form to receive user input and evaluation of
    that input. Handles only a single string response.
    """

    def get_responder(self):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        form = SQLFORM.factory(Field('response', 'string',
                                     requires=IS_NOT_EMPTY()),
                               _autocomplete='off'
                               )
        responder = DIV(form, _class='responder', _id='responder')
        return responder

    def get_final_responder(self, localias=None, bug_reporter=None):
        """
        Return the html for the user-response interface presented with a reply.
        """
        resp = DIV(A("Continue",
                     _href=URL('walk', args=['ask'],
                               vars={'loc': localias}),
                     cid='page',
                     _class='btn btn-success next_q'),
                   A("Try again",
                     _href=URL('walk', args=['repeat'],
                               vars={'loc': localias}),
                     cid='page',
                     _class='btn btn-warning retry'),
                   A("Map",
                     _href=URL('walk', args=['map'], vars={'loc': None}),
                     cid='page',
                     _class='btn btn-info back_to_map'),
                   bug_reporter,
                   _class='responder')

        return resp

    def get_reply(self, user_response=None, answers=None, tips=None):
        """
        Evaluate a user's response and return the resulting data and reply.
        """
        db = current.db
        readable = self._get_readable()

        try:
            tips = self.data['hints']
            rkeys = ['response1', 'response2', 'response3']
            responses = {k: v for k, v in self.data.iteritems()
                         if k and (k in rkeys)}
        except TypeError:
            tips = self.data['step'].data['hints']
            responses = {k: v for k, v in self.data['step'].data.iteritems()
                         if k and (k in rkeys)}
        if tips:
            tips_lst = db(db.step_hints.id.belongs(tips)).select(db.step_hints.hint_text).as_list()
            tips_txt = UL()
            tips_lst = [v for t in tips_lst for k, v in t.iteritems()]
            for t in tips_lst:
                tips_txt.append(LI(t))
        else:
            tips_txt = None

        result = StepEvaluator(responses, tips_txt).get_eval(user_response)

        bg_image = self.loc.get_bg()
        npc_image = self.npc.get_image()

        reply = DIV(P(result['reply'],
                      'You said ', UL(LI(user_response)),
                      'Correct answers would include ',
                      readable['readable_short']),
                    _class='npc prompt')

        if tips:
            hints_args = {'classnames': 'btn btn-info',
                          'id': 'instructions_btn'}
            reply.append(POPOVER().widget('Hints', tips_txt, **hints_args))

        if readable['readable_long']:
            readable_long_args = {'classnames': 'btn btn-info',
                                  'id': 'readable_btn'}
            reply.append(POPOVER().widget('More examples', readable['readable_long'],
                                 **readable_long_args))

        return {'bg_image': bg_image,
                'npc': reply,
                'npc_image': npc_image,
                'score': result['score'],
                'times_right': result['times_right'],
                'times_wrong': result['times_wrong'],
                'user_response': result['user_response']}

    def _get_readable(self):
        """
        Return two strings containing the shorter and the longer forms of the
        readable correct answer samples for this step.
        """
        try:
            readable = self.data['readable_response']
            assert isinstance(readable, str)
        except TypeError:
            readable = self.data['step'].data['readable_response']
            assert isinstance(readable, str)

        rdbl_short = UL(_class='readable_short')
        if '|' in readable:
            # show first two answers for short readable
            rsplit = readable.split('|')
            readable_short = rsplit[:3]
            if len(rsplit) <= 2:
                readable_long = None
            else:
                rl_raw = rsplit[2:]
                readable_long = UL(_class='readable_long')
                for r in rl_raw:
                    readable_long.append(LI(r))
            for r in readable_short:
                rdbl_short.append(LI(r))
        else:
            rdbl_short.append(LI(readable))
            readable_long = None

        return {'readable_short': rdbl_short,
                'readable_long': readable_long}


class StepMultiple(StepText):
    """
    A subclass of Step that adds a form to receive multiple-choice user input
    and evaluation of that input.
    """

    def get_responder(self):
        """
        Return an html radio form for responding to the current step prompt.

        The form is built and returned as a web2py html helper object produced
        by the SQLFORM.factory() method. This produces a SQLFORM object
        without setting up any connection to crud methods on form submission.
        """
        request = current.request
        session = current.session
        vals = self.data['step_options']
        form = SQLFORM.factory(Field('response', 'string',
                                     requires=IS_IN_SET(v for v in vals),
                                     widget=SQLFORM.widgets.radio.widget))
        if form.process().accepted:
            session.response = request.vars.response
        responder = DIV(form, _class='responder')

        return responder


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
        responses = self.responses
        # Compare the student's response to the regular expressions
        try:
            if re.match(responses['response1'], user_response, re.I):
                score = 1
                reply = "Right. Κάλον."
            elif len(responses) > 1 and re.match(responses['response2'],
                                                 user_response, re.I):
                score = 0.5
                #TODO: Get this score value from the db instead of hard
                #coding it here.
                reply = "Οὐ κάκον. You're close."
                #TODO: Vary the replies
            elif len(responses) > 2 and re.match(responses['response3'],
                                                 user_response, re.I):
                #TODO: Get this score value from the db instead of hard
                #coding it here.
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

    def __init__(self, path_id=None, loc=None, prev_loc=None,
                 completed_steps=None, last_step_id=None, step_sent_id=None,
                 step_for_prompt=None, step_for_reply=None, prev_npc=None,
                 db=None, username=None):
        """
        Initialize a paideia.Path object.

        The following arguments are required at init:
            path_id
            loc_id
        The others are for dependency injection in testing
        """
        # first set from init args
        self.loc = loc
        self.prev_loc = prev_loc
        self.prev_npc = prev_npc
        self.username = username

        # set later
        self.npc = None

        # basic path data
        db = current.db if not db else db
        self.path_dict = db(db.paths.id == path_id).select().first().as_dict()

        # controlling step progression through path
        self.steps = self.get_steps(username)
        self.completed_steps = completed_steps if completed_steps else []
        self.step_for_prompt = step_for_prompt
        self.step_for_reply = step_for_reply

    def get_id(self):
        """Return the id of the current Path object."""
        return self.path_dict['id']

    def _prepare_for_prompt(self):
        """ move next step in this path into the 'step_for_prompt' variable"""
        # to bounce back after cleaning
        if len(self.steps) == 0:
            self._reset_steps()
        try:
            # TODO: why is this if condition necessary?
            if len(self.steps) > 1:
                next_step = self.steps.pop(0)
            else:
                next_step = copy(self.steps[0])
                self.steps = []
            self.step_for_prompt = next_step
            return True
        except:
            return False

    def end_prompt(self):
        """
        End prompt cycle before sending prompt data to view.

        For 1-stage steps this is the end of the step. For 2-stage steps
        this prepares for the reply stage (processing of the user response).
        """
        step = self.step_for_prompt
        if type(step) in [StepText, StepMultiple]:
            self.step_for_reply = copy(self.step_for_prompt)
            self.step_for_prompt = None
        else:
            assert self.complete_step()
        return True

    def complete_step(self):
        """
        Deactivate current step.
        """
        if self.step_for_reply:
            self.completed_steps.append(copy(self.step_for_reply))
            # TODO: should we handle (remove) steps that shouldn't be there?
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

    def get_step_for_prompt(self, loc=None, step=None, repeat=None):
        """
        Find the next unanswered step in the current path and return it.
        If the selected step cannot be performed at this location, return a
        Block object instead.
        """
        loc = self.loc if not loc else loc  # for testing only

        if repeat:
            assert self._reset_steps()

        # make sure controller hasn't skipped processing an earlier step's reply
        if self.step_for_reply:
            self.step_for_prompt = copy(self.step_for_reply)
            self.step_for_reply = None

        # get step
        if not self.step_for_prompt:
            assert self._prepare_for_prompt()
        mystep = self.step_for_prompt
        print 'path.get_step_for_prompt: initial step choice', mystep.get_id()

        next_loc = None
        goodlocs = mystep.get_locations()
        if not loc.get_id() in goodlocs:
            print 'path.get_step_for_prompt: this loc is', loc.get_id()
            print 'path.get_step_for_prompt: good locs are', goodlocs
            next_loc = goodlocs[randrange(len(goodlocs))]
            print 'path.get_step_for_prompt: next step can\'t be done here'
            print 'path.get_step_for_prompt: redirecting to loc', next_loc
            # TODO: Putting redirect check here requires sane step data
        else:
            mystep.loc = self.loc  # update location on step
            mystep.prev_loc = self.prev_loc

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

    def get_steps(self, username):
        """
        Return a list containing all the steps of this path as Step objects.
        """
        static_args = {'loc': self.loc,
                       'prev_loc': self.prev_loc,
                       'prev_npc': self.prev_npc}
        steplist = [StepFactory().get_instance(step_id=i, **static_args)
                    for i in self.path_dict['steps']]

        return steplist

    def set_npc(self, npc):
        """
        Set the active location after initialization of the Path object.
        """
        self.prev_npc = copy(self.npc) if self.npc else copy(npc)
        self.npc = npc
        return True

    def set_location(self, loc):
        """
        Set the active location after initialization of the Path object.
        """
        if isinstance(self.loc, int):
            self.prev_loc = Location(self.loc)
        else:
            self.prev_loc = copy(self.loc)
        if self.prev_loc is None:
            self.prev_loc = copy(loc)
        self.loc = loc
        return True


class PathChooser(object):
    """
    Select a new path to begin when the user begins another interaction.
    """

    def __init__(self, tag_progress, loc_id, paths_completed, db=None):
        """Initialize a PathChooser object to select the user's next path."""
        self.categories = {k: v for k, v in tag_progress.iteritems()
                           if not k in ['name', 'latest_new']}
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

        if switch in range(1, 76):
            cat = 1
        elif switch in range(75, 91):
            cat = 2
        elif switch in range(90, 99):
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
        # TODO: include paths with tag as secondary, maybe in second list
        # TODO: cache the select below and just re-order randomly
        ps = db().select(db.paths.ALL, orderby='<random>')
        # filter by category, then
        # filter out paths with a step that's not set to "active"
        # avoid steps with right tag but no location
        taglist = self.categories['cat{}'.format(cat)]
        # TODO: make find below more efficient

        ps = ps.find(lambda row:
                     [t for t in row.tags
                      if taglist and (t in taglist)])
        ps = ps.find(lambda row:
                     [s for s in row.steps
                      if db.steps(s).status != 2])
        ps.exclude(lambda row:
                   [s for s in row.steps
                    if db.steps(s).locations is None])
        # TODO: why does this kill the select?
        #ps.exclude(lambda row:
                   #[t for t in row.tags
                    #if db.tags[t].tag_position > self.rank])

        return (ps, cat)

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

        # cpaths is already filtered by category
        p_new = cpaths.find(lambda row: row.id not in self.completed).as_list()
        # FIXME: p.steps[0] is yielding a long int
        # added 'if' condition to .find here for steps with no locations
        # assigned (legacy data)
        p_here = [p for p in cpaths.as_list()
                  if db.steps[int(p['steps'][0])].locations
                  and loc_id in db.steps[int(p['steps'][0])].locations]
        p_here_new = [p for p in p_here if p in p_new]

        path = None
        new_loc = None
        if p_here_new:
            print 'PathChooser._choose_from_cat: choosing untried path for this loc'
            path = p_here_new[randrange(0, len(p_here_new))]
        elif p_new:
            print 'PathChooser._choose_from_cat: choosing untried path for different loc'
            # While loop safeguards against looking for location for a step
            # that has no locations assigned.
            while path is None:
                try:
                    path = p_new[randrange(0, len(p_new))]
                    new_locs = db.steps(path['steps'][0]).locations
                    new_loc = new_locs[randrange(0, len(new_locs))]
                except TypeError:
                    path = None
        elif p_here:
            print 'PathChooser._choose_from_cat: choosing repeat path for this loc'
            path = p_here[randrange(0, len(p_here))]

        return (path, new_loc, category)

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
            [0] Path object chosen
            [1] location id where Path must be started (or None if current loc)
            [2] the category number for this new path (int in range 1-4)
        """
        db = current.db if not db else db

        cat_list = self._order_cats()

        # cycle through categories, starting with the one from _get_category()
        for cat in cat_list:
            catpaths = self._paths_by_category(cat, self.rank)
            if catpaths[0]:
                return self._choose_from_cat(catpaths[0], catpaths[1])
            else:
                pass

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
        - userdata: {'name': str, 'id': int, '}
        - localias: str
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
            self.rank = tag_progress['latest_new'] if tag_progress else None
            self.tag_progress = tag_progress
            self.promoted = None
            self.new_tags = None
            #self.get_categories(rank=self.rank,
                                #old_categories=self.old_categories,
                                #tag_records=tag_records)

            self.inventory = []
            self.session_start = datetime.datetime.utcnow()

            self.loc = None
            self.prev_loc = None
            self.npc = None
            self.prev_npc = None
            msel = db((db.auth_membership.user_id == self.user_id) &
                      (db.auth_membership.group_id == db.auth_group.id)).select()
            #pprint([m for m in msel.as_list()])
            # FIXME: Handle registered users without a class assignment
            # put everyone either in a class at registration or in (by default)
            # a generic 'class' with generic presets
            try:
                target = [m.auth_group.paths_per_day for m in msel
                          if m.auth_group.paths_per_day][0]
            except:
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
            #print 'user.check_for_blocks: now blocks are', [b.get_condition() for b in self.blocks]
            return myblock
        else:
            return None

    def _set_block(self, condition, kwargs=None, data=None):
        """ Set a blocking condition on this Path object. """
        myblocks = [b.get_condition() for b in self.blocks]
        kwargs.update({'username': self.name})
        if not condition in myblocks:
            #print 'path.set_block: that condition is already set'
        #else:
            #print 'path.set_block: new condition, adding block'
            self.blocks.append(Block(condition=condition,
                                     kwargs=kwargs,
                                     data=data))
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

        # get current local datetime
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
        return True

    def get_new_tags(self):
        """Return a list of tag ids newly introduced"""
        return self.new_tags

    def get_promoted(self):
        """Return a dictionary of tag ids newly promoted to categories 2-4."""
        return self.promoted

    def get_tag_records(self):
        """
        Return a list of dictionaries matching the fields of db.tag_records.

        Each dictionary contains the user's performance data for a single
        grammatical tag.
        """
        return self.tag_records

    def get_tag_progress(self):
        """
        Return a dictionary matching the fields of db.tag_progress.

        This dictionary contains the user's overall progress data.
        """
        return self.tag_progress

    def get_path(self, categories=None, reply=False, db=None, path=None, repeat=None):
        """
        Return the currently active Path object.

        None of the arguments is strictly necessary, but loc will usually be
        provided. The others are only used for dependency injection during
        testing.

        Note: redirect block is set here if the chosen path cannot be
        begun in this location
        """
        db = current.db if not db else db
        categories = self.categories if not categories else categories
        #print 'user.get_path: user.loc is', self.loc.get_id()
        #if self.prev_loc:
            #print 'user.get_path: user.prev_loc is', self.prev_loc.get_id()

        if path:
            if not self.prev_loc:  # FIXME: hack to handle error ticket
                self.prev_loc = copy(self.loc)
            self.path = Path(path_id=path,
                             loc=self.loc,
                             prev_loc=self.prev_loc,
                             username=self.name)
        if repeat:
            if self.path:
                print 'repeating path from self.path'
                self.path.set_location(self.loc)
                self.path.prev_loc = self.prev_loc
                self.path.prev_npc = self.prev_npc
            else:
                path_id = self.completed_paths.pop(-1)
                self.path = Path(path_id=path_id,
                                 loc=self.loc,
                                 prev_loc=self.prev_loc,
                                 prev_npc=self.prev_npc,
                                 username=self.name)
        elif self.path and self.path.step_for_reply:
            # there's a step waiting for a reply
            print 'user.get_path: path has step needing reply'
            self.path.set_location(self.loc)
            self.path.prev_npc = self.prev_npc
        elif self.path and len(self.path.steps):
            # there's still an unfinished step in self.path
            print 'user.get_path: path includes a further step, continuing'
            print 'user.get_path:', len(self.path.steps), 'more steps'
            self.path.set_location(self.loc)
            self.path.prev_npc = self.prev_npc
        else:
            if self.path:
                print 'user.get_path: completing path', self.path.get_id()
                self.complete_path()  # catch end-of-path and triggers new choice
            if not self.tag_progress:  # in case User was badly initialized
                self.get_categories()
            print 'user.get_path: choosing new path'
            # FIXME: For some reason PathChooser.choose() is returning None for
            # path sometimes
            choice = (None,)
            while not choice or not choice[0]:
                choice = PathChooser(self.tag_progress, self.loc.get_id(),
                                    self.completed_paths).choose()
                if not choice:
                    choice = (None,)
                    print 'sending error'
                    send_error('User', 'get_path', current.request)
                    print 'sent error'
                elif not choice[0]:
                    print 'sending error'
                    send_error('User', 'get_path', current.request)
                    print 'sent error'
                else:
                    pass

            path = Path(path_id=choice[0]['id'],
                        loc=self.loc,
                        prev_loc=self.prev_loc,
                        prev_npc=self.prev_npc,
                        username=self.name)
            if choice[1]:  # check for a redirect location
                self._set_block('redirect', kwargs={'next_loc': choice[1]})
            self.path = path

        if (len(self.completed_paths) == self.quota) and \
                (hasattr(self, 'past_quota')):
            if (not hasattr(self, 'past_quota')) or (self.past_quota is False):
                self._set_block('quota_reached', kwargs={'quota': self.quota})
                self.past_quota = True
        print 'user.get_path: no of initial path blocks is', len(self.blocks)
        if len(self.blocks) > 0:
            print 'user.get_path: type of blocks is', [b.get_condition() for b in self.blocks]
            # FIXME: This hack is to work around mysterious introduction of
            # redirect block after initial redirect has been triggered
            self.blocks = [b for b in self.blocks if not b.get_condition() is 'redirect']
            print 'user.get_path: now blocks is', [b.get_condition() for b in self.blocks]
        return self.path

    def get_categories(self, user_id=None, rank=None, old_categories=None,
                       tag_records=None, utcnow=None):
        """
        Return a categorized dictionary with four lists of tag id's.

        This method is important primarily to decide whether a new
        categorization is necessary before instantiating a Categorizer object

        # TODO: do we need to create new categorizer object each time?

        The method is intended to be called with no arguments
        """
        #print 'user.get_categories: starting'
        db = current.db
        user_id = self.user_id if not user_id else user_id
        tag_records = db(db.tag_records.name == user_id).select().as_list()
        self.tag_records = tag_records

        # only re-categorize every 10th evaluated step
        if (self.cats_counter in range(0, 4)) and hasattr(self, 'categories') and self.categories:
            self.cats_counter += 1
            print 'user.get_categories: no need for refresh yet - counter is', self.cats_counter
            return True
        else:
            print 'user.get_categories: need to recategorize'

            utcnow = datetime.datetime.utcnow() if not utcnow else utcnow

            # get tag_progress, rank, categories
            try:
                tag_progress_sel = db(db.tag_progress.name == user_id
                                      ).select()
                assert len(tag_progress_sel) == 1
                self.tag_progress = tag_progress_sel.first().as_dict()
                rank = self.tag_progress['latest_new']
                # TODO: below is 'magic' hack based on specific db field names
                categories = {k: v for k, v in self.tag_progress.iteritems()
                              if k[:4] in ['cat', 'rev']}
            except AttributeError:
                categories = None
            self.old_categories = copy(categories)

            # perform categorization
            c = Categorizer(rank, categories, tag_records, user_id,
                            utcnow=utcnow)
            cat_result = c.categorize_tags()

            # Set blocks for 'new_tags' (slides) and 'promoted' conditions
            nt = cat_result['new_tags']
            pr = cat_result['promoted']
            if nt:  # These blocks need to be on the User, not path
                if (not hasattr(self, 'viewed_slides')) or (self.viewed_slides
                                                            is False):
                    self._set_block('view_slides', kwargs={'new_tags': nt})
                    self.viewed_slides = True
                if (not hasattr(self, 'reported_badges')) or \
                        (self.reported_badges is False):
                    self._set_block('new_tags',
                                    kwargs={'new_tags': nt, 'promoted': pr})
                    self.reported_badges = True
            if pr:
                if (not hasattr(self, 'reported_badges')) or \
                        (self.reported_badges is False):
                    self._set_block('new_tags',
                                    kwargs={'new_tags': nt, 'promoted': pr})
                    self.viewed_slides = True

            self.tag_records = cat_result['tag_records']
            self.rank = cat_result['tag_progress']['latest_new']
            self.tag_progress = cat_result['tag_progress']
            self.categories = cat_result['categories']
            self.promoted = cat_result['promoted']
            self.new_tags = cat_result['new_tags']
            self.cats_counter = 0  # reset counter

            return True

    def _get_old_categories(self):
        if self.old_categories:
            return self.old_categories
        else:
            return None

    def complete_path(self):
        """
        Move the current path from the path variable to 'completed_paths' list.
        Set last_npc and prev_loc before removing the path.
        """
        # Only id of paths stored to converve memory.
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
        self.user_id = user_id
        self.rank = rank
        self.tag_records = tag_records
        self.old_categories = categories
        self.utcnow = utcnow
        self.secondary_right = secondary_right

    def _sanitize_recs(self, tag_records):
        """
        Remove any illegitimate tag_records data.
        """
        db = current.db

        null_tags = [r for r in tag_records if r['tag'] is None]
        if null_tags:
            db(db.tag_records.tag == None).delete()

        tag_records = db(db.tag_records.name == self.user_id).select().as_list()
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
        old_categories = self.old_categories if not old_categories else old_categories
        tag_records = self.tag_records if not tag_records else tag_records
        tag_records = self._sanitize_recs(tag_records)
        db = current.db if not db else db
        new_tags = None

        # if user has not tried any tags yet, start first set
        if len(tag_records) == 0:
            #print 'categorize_tags: no tag_records found'
            categories = {}
            categories['cat1'] = self._introduce_tags()
            tp = {'cat1': categories['cat1'],
                  'rev1': None,
                  'cat2': None,
                  'rev2': None,
                  'cat3': None,
                  'rev3': None,
                  'cat4': None,
                  'rev4': None,
                  'latest_new': rank}
            return {'tag_records': None,
                    'tag_progress': tp,
                    'new_tags': categories['cat1'],
                    'promoted': None,
                    'demoted': None,
                    'categories': categories}
        else:
            # otherwise, categorize tags that have been tried
            tag_records = self._add_secondary_right(tag_records)
            #print 'categorize_tags: after core algorithm, tag_records are', pprint(self.tag_records)
            categories = self._core_algorithm()
            #print '\ncategorize_tags: after core algorithm, cats are', pprint(categories)
            categories = self._add_untried_tags(categories)
            #print '\ncategorize_tags: after adding untried, cats are', pprint(categories)
            # Remove any duplicates and tags beyond the user's current ranking
            for k, v in categories.iteritems():
                if v:
                    rankv = [t for t in v if db.tags(t)
                            and (db.tags[t].tag_position <= rank)]
                    categories[k] = list(set(rankv))
            # 'rev' categories are reintroduced
            categories.update((c, []) for c in ['rev1', 'rev2', 'rev3', 'rev4'])
            # changes in categorization since last time
            cat_changes = self._find_cat_changes(categories, old_categories)
            promoted = cat_changes['promoted']
            demoted = cat_changes['demoted']
            tag_progress = copy(cat_changes['categories'])

            # If there are no tags left in category 1, introduce next set
            if not tag_progress['cat1']:
                newlist = self._introduce_tags()
                categories['cat1'] = newlist
                tag_progress['cat1'] = newlist
                new_tags = newlist

            # Re-insert 'latest new' to match tag_progress table in db
            tag_progress['latest_new'] = self.rank
            #print 'categorize_tags: returning tag_progress as', tag_progress

            return {'tag_records': tag_records,
                    'tag_progress': tag_progress,
                    'new_tags': new_tags,
                    'promoted': promoted,
                    'demoted': demoted,
                    'categories': categories}

    def _add_secondary_right(self, tag_records):
        """
        Finds tag records with secondary attempts and adjusts records.

        For every 3 secondary_right entries, add 1 to times_right and change
        tlast_right based on the average of those three attempt dates.
        """
        db = current.db
        try:
            for rec in tag_records:
                right2 = rec['secondary_right']

                # FIXME: sanitizing data where tuples stored instead of
                # datetimes strings also have to be parsed into datetime objects
                if right2:
                    for t in right2:
                        if isinstance(t, list):
                            vals = right2.pop(right2.index(t))
                            right2.extend(vals)
                        else:
                            pass
                    for t in right2:
                        if isinstance(t, tuple):
                            try:
                                right2[right2.index(t)] = parser.parse(t[1])
                            except TypeError:
                                right2.append(parser.parse(t[1]))
                        else:
                            pass
                    for t in right2:
                        if not isinstance(t, datetime.datetime):
                            right2[right2.index(t)] = parser.parse(t)

                    if right2 != rec['secondary_right']:
                        right2.sort()
                        db.tag_records[rec['id']].update(secondary_right=right2)
                    rlen = len(right2)
                    remainder2 = rlen % 3

                if right2 and (isinstance(right2, list)) and (rlen >= 3) \
                        and (remainder2 > 0):
                    rindex = tag_records.index(rec)
                    # increment times_right by 1 per 3 secondary_right
                    triplets2 = rlen / 3
                    if not rec['times_right']:
                        rec['times_right'] = 0
                    rec['times_right'] += triplets2

                    # move tlast_right forward based on mean of oldest 3 secondary_right
                    now = self.utcnow
                    if remainder2 or rlen > 3:
                        early3 = right2[: -(remainder2)]
                    else:
                        early3 = right2[:]
                    early3d = [now - s for s in early3]
                    avg_delta = sum(early3d, datetime.timedelta(0)) / len(early3d)
                    avg_date = now - avg_delta
                    # sanitize tlast_right in case db value is string
                    tlr = rec['tlast_right'] \
                        if isinstance(rec['tlast_right'], datetime.datetime) \
                        else parser.parse(rec['tlast_right'])
                    if avg_date > tlr:  #
                        rec['tlast_right'] = avg_date

                    # remove counted entries from secondary_right, leave remainder
                    if remainder2:
                        rec['secondary_right'] = right2[-(remainder2):]
                    else:
                        rec['secondary_right'] = []
                    tag_records[rindex] = rec
                else:
                    continue
        except Exception:
            print traceback.format_exc(5)

        return tag_records

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
        db = current.db
        categories = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        utcnow = self.utcnow
        if not utcnow:
            utcnow = datetime.datetime.utcnow()
        if not tag_records:
            tag_records = self.tag_records
        # TODO: Get secondary_right here

        for record in tag_records:

            # find average score for steps with this tag over past week
            week_ago = utcnow - datetime.timedelta(days=7)
            print 'for tag', record['tag']
            log_query = db((db.attempt_log.dt_attempted >= week_ago) &
                           (db.attempt_log.step == db.steps.id) &
                           (db.steps.tags.contains(record['tag']))).select()
            scores = [l.attempt_log.score for l in log_query]
            try:
                avg_score = sum(scores) / float(len(scores))
            except ZeroDivisionError:  # if tag not tried in past week
                avg_score = 0
                # FIXME: Will this not bring tags up too early?

            # get durations for spaced repetition calculations
            # arithmetic operations yield datetime.timedelta objects
            lastright = record['tlast_right']
            lastwrong = record['tlast_wrong']
            if isinstance(lastright, str):
                lastright = parser.parse(lastright)
            if isinstance(lastwrong, str):
                lastwrong = parser.parse(lastwrong)

            right_dur = utcnow - lastright
            right_wrong_dur = lastright - lastwrong

            # spaced repetition algorithm for promotion to
            # ======================================================
            # category 2
            if (((right_dur < right_wrong_dur) and
                 # don't allow promotion from cat1 within 1 day
                 (right_wrong_dur > datetime.timedelta(days=1)) and
                 # require at least 20 right answers
                 (record['times_right'] >= 20))
                or ((record['times_right'] >= 20) and
                    # require an average score of at least 8.0
                    # TODO: does float comparison inaccuracy matter here?
                    (avg_score >= 8.0) and
                    # require that tag has right answer within last 2 days
                    (right_dur <= datetime.timedelta(days=2)))):
                # ==================================================
                # for cat3
                if right_wrong_dur.days >= 14:
                    # ==============================================
                    # for cat4
                    if right_wrong_dur.days > 60:
                        # ==========================================
                        # for immediate review
                        if right_wrong_dur > datetime.timedelta(days=180):
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
        rank = self.rank if not rank else rank

        if rank in (None, 0):
            rank == 1
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
        #print 'add_untried_tags: rank is', rank

        #print 'add_untried_tags: level 1 cats are', categories['cat1']

        left_out = []
        for r in range(1, rank + 1):
            newtags = [t['id'] for t in
                       db(db.tags.tag_position == r).select().as_list()]
            alltags = list(chain(*categories.values()))
            left_out.extend([t for t in newtags if t not in alltags])
        if left_out:
            #print 'add_untried_tags: adding some untried tags'
            categories['cat1'].extend(left_out)
        else:
            pass
            #print 'add_untried_tags: no untried tags to add'

        #print 'add_untried_tags: level 1 cats are now', categories['cat1']

        return categories

    def _find_cat_changes(self, cats, old_cats):
        """
        Determine whether any of the categorized tags are promoted or demoted.
        """
        if old_cats:
            demoted = {}
            promoted = {}
            for c, lst in cats.iteritems():
                if lst:
                    cindex = cats.keys().index(c)

                    # was tag in a higher category before?
                    gt = {k: old_cats[k] for k in
                          ['cat1', 'cat2', 'cat3', 'cat4'][cindex + 1:]}
                    gt_flat = [v for l in gt.values() if l for v in l]
                    revc = c.replace('cat', 'rev')
                    for tag in [l for l in lst if l in gt_flat]:
                        # move to review category
                        cats[c].pop(tag)
                        try:
                            demoted[revc].append(tag)
                        except Exception:
                            print traceback.format_exc(5)
                            demoted[revc] = [tag]
                        # then re-insert tag in its old max level
                        oldc = [k for k, v in gt if tag in v]
                        if len(cats[oldc]):
                            cats[oldc].append(tag)
                        else:
                            cats[oldc] = [tag]

                    # was tag in a lower category?
                    lt = {k: old_cats[k] for k in
                          ['cat1', 'cat2', 'cat3', 'cat4'][:cindex]}
                    lt_flat = [v for l in lt.values() if l for v in l]
                    # add to dictionary of 'promoted' tags
                    if lt_flat:
                        promoted[c] = [t for t in cats[c] if t in lt_flat]

            return {'categories': cats,
                    'demoted': demoted,
                    'promoted': promoted}
        else:
            return {'categories': cats,
                    'demoted': None,
                    'promoted': None}

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

    def __init__(self, condition, kwargs=None, data=None):
        """
        Initialize a new Block object
        """
        self.condition = condition
        self.data = data
        self.kwargs = kwargs

    def make_step(self, condition, kwargs=None, data=None):
        """Create correct Step subclass and store as an instance variable."""
        db = current.db
        kwargs = self.kwargs if not kwargs else kwargs
        step_classes = {'view_slides': 6,
                        'quota_reached': 7,
                        'new_tags': 8,
                        'promoted': 8,
                        'redirect': 9}
        step = db(db.steps.widget_type ==
                  step_classes[condition]).select(orderby='<random>').first()
        kwargs.update({'step_id': step['id']})
        mystep = StepFactory().get_instance(**kwargs)
        return mystep

    def get_condition(self):
        """Return a string representing the condition causing this block."""
        if self.condition:
            return self.condition
        else:
            return False

    def get_step(self, loc=None, prev_loc=None, npc=None, prev_npc=None):
        """Return the appropriate step for the current blocking condition"""
        if isinstance(self.data, Step):
            step = self.data  # in some cases easiest to just pass existing step
        else:
            newargs = {'loc': loc,
                       'prev_loc': prev_loc,
                       'npc': npc,
                       'prev_npc': prev_npc}
            kwargs = self.kwargs.update(newargs)
            step = self.make_step(self.get_condition(), kwargs=kwargs, data=self.data)
        return step

    def get_data(self):
        """Return the secondary data, if any, belonging to this Block."""
        if self.data:
            return self.data
        else:
            return False
