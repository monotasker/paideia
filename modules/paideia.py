# -*- coding: utf-8 -*-
from gluon import current, redirect
from gluon import IMG, URL, SQLFORM, SPAN, DIV, UL, LI, A, Field, P
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
from plugin_widgets import POPOVER
import pickle

# TODO: move these notes elsewhere
"""
The following files exist outside the paideia app folder and so need to be
watched when upgrading web2py:
- web2py/routes.py
"""


def util_get_args():
    """
    Returns a collection of all the calling functionos arguments.

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


class Walk(object):
    """
    Main interface class for the paideia module, intended to be called by
    the controller.
    """

    def __init__(self, localias, tag_records=None,
                 tag_progress=None, response_string=None, userdata=None,
                 db=None):
        """Initialize a Walk object."""
        self.localias = localias
        db = current.db if not db else db
        loc_id = db(db.locations.loc_alias == localias).select().first().id
        self.loc = Location(loc_id)
        self.response_string = response_string
        userdata = db.auth_user[current.auth.user_id].as_dict() \
            if not userdata else userdata
        self.user = self._get_user(userdata=userdata,
                                   loc=self.loc,
                                   tag_records=tag_records,
                                   tag_progress=tag_progress)
        self.record_id = None  # stores step log row id after db update

    def _get_user(self, userdata=None, loc=None, tag_records=None,
                  tag_progress=None, db=None):
        ''' initialize or re-activate User object '''
        #session = current.session
        auth = current.auth
        db = current.db if not db else db
        try:
            return self.user
        except AttributeError:  # because no user yet on this Walk
            try:
                sd = db(db.session_data.name ==
                        auth.user_id).select().first()
                if sd:
                    user = pickle.loads(sd['other_data'])
                else:
                    user = None
                assert user.is_stale() is False
                self.user = user
                return user
            except Exception:  # (AttributeError, AssertionError)
                uid = auth.user_id
                # because no user yet in this session or user is stale
                if not tag_records:
                    tag_records = db(db.tag_records.name == uid).select().as_list()
                if not tag_progress:
                    tag_progress = db(db.tag_progress.name == uid).select().first()
                    if not tag_progress:
                        db.tag_progress.insert(latest_new=1)
                        tag_progress = db(db.tag_progress.name == uid).select().first()
                    tag_progress = tag_progress.as_dict()

                user = User(userdata, loc, tag_records, tag_progress)
                self.user = user
                return self.user

    def start(self, response_string=None, path=None, repeat=None):
        """
        Issue the correct method for this interaction and return the result.
        This is the top-level interface for the Paideia module, to be called by
        the controller. The method decides whether we're starting a new step or
        responding to one in-process.
        """
        print '\nIN START'
        print 'response:', response_string
        try:
            if response_string:
                return self.reply(response_string)
            else:
                return self.ask(path, repeat)
        except Exception:
            print traceback.format_exc(5)

    def map(self, mapnum=None, db=None):
        """
        Return data for the paideia navigation map interface.

        The mapnum argument is to facilitate future expansion to multiple
        levels of the map.
        """
        user = self._get_user()
        db = current.db if not db else db
        cache = current.cache

        map_image = '/paideia/static/images/town_map.svg'
        # TODO: Review cache time
        locations = db().select(db.locations.ALL,
                                orderby=db.locations.map_location,
                                cache=(cache.ram, 60 * 60)).as_list()
        # Store a user created at Walk instantiation, so it doesn't have to be
        # re-initialized at the next http request.
        self._store_user(user)

        return {'map_image': map_image, 'locations': locations}

    def ask(self, path=None, repeat=None):
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
        """
        user = self._get_user()
        loc = self.loc
        p = user.get_path(loc, path=path, repeat=repeat)  # call set_location here in get_path
        user.set_location(loc)  # must be set before step is retrieved
        user.last_response_text = None  # prevent using earlier response

        s = p.get_step_for_prompt(repeat=repeat)
        if isinstance(s, Block):
            condition = s.get_condition()
            print 'encountered Block', condition
            # a step needs to be finished (reply given or re-prompted)
            if condition == 'need_to_reply' and user.last_response_text:
                print 'found last response text'
                type(user.last_response_text)
                return self.reply(user.last_response_text)
            elif condition == 'need_to_reply':
                # TODO: this seems like a hack
                s = copy(p.step_for_reply)

        cur_npc = s.get_npc()
        if isinstance(cur_npc, Npc):
            cur_npc_id = cur_npc.get_id()
        else:
            # if no npc for chosen step, set random npc for this loc and send
            # user to another valid loc
            myargs = {'next_loc': cur_npc[0],
                      'username': user.name}
            p._set_block('redirect', kwargs=myargs)
            cur_npc_id = cur_npc[1]
        user.set_npc(cur_npc_id)

        prompt = s.get_prompt()
        responder = s.get_responder()
        self._store_user(user)
        # non-response steps end here
        print 'step_for_reply is', p.step_for_reply
        print 'END OF ASK IN MODULE'

        return {'npc': prompt, 'responder': responder}

    def reply(self, response_string, path=None):
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
        print 'START OF Walk.reply() IN MODULE'
        user = self._get_user()
        user_id = user.get_id()

        user.last_response_text = response_string  # in case need to recover step

        # evaluate user response and generate reply
        p = user.get_path(self.loc)
        # make sure there's a response to evaluate
        if not response_string or re.match(response_string, r'\s+'):
            p._set_block('empty_response')

        s = p.get_step_for_reply()
        print 'step is', s
        if isinstance(s, Block):
            print 'encountered block', s
            condition = s.get_condition()
            if condition == 'empty_response':
                return self.ask()
        reply = s.get_reply(response_string)

        # retrieve data from generated reply
        score = reply['score']
        tag_records = user.get_tag_records()
        tag_progress = user.get_tag_progress()
        promoted = user.get_promoted()
        new_tags = user.get_new_tags()

        # record data for this step in db
        assert self._record_cats(tag_progress, promoted, new_tags)
        record_id = self._record_step(user_id,
                                      p.get_id(),
                                      s.get_id(),
                                      score,
                                      tag_records,
                                      response_string)
        self.record_id = record_id
        assert record_id

        # create bug reporter
        bug_reporter = BugReporter().get_reporter(record_id,
                                                  p.get_id(),
                                                  s.get_id(),
                                                  score,
                                                  response_string,
                                                  self.loc.get_alias())

        responder = DIV(A("Continue",
                          _href=URL('walk', args=['ask'],
                                    vars={'loc': self.loc.get_alias()}),
                          cid='page',
                          _class='btn btn-success next_q'),
                        A("Try that again",
                          _href=URL('walk', args=['repeat'],
                                    vars={'loc': self.loc.get_alias()}),
                          cid='page',
                          _class='btn btn-warning retry'),
                        A("Go back to map",
                          _href=URL('walk', args=['map'], vars={'loc': None}),
                          cid='page',
                          _class='btn btn-info back_to_map'),
                        bug_reporter,
                        _class='responder')

        p.complete_step()  # removes path.step_for_reply
        self._store_user(user)

        return {'npc': reply, 'responder': responder}

    def _record_cats(self, tag_progress, promoted,
                     new_tags, db=None):
        """
        Record changes to the user's working tags and their categorization.

        Changes recorded in the following db tables:
        - badges_begun: new and promoted tags
        - tag_progress: changes to categorization (only if changes made)
        """
        db = current.db if not db else db
        user_id = self.user.get_id()
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
                                             name=user_id, **tag_progress)
            mycount = db(db.tag_progress.name == user_id).count()
            assert mycount == 1
        except Exception:
            print traceback.format_exc(5)
            return False
        return True

    def _record_step(self, user_id, step_id, path_id, score, tag_records,
                     response_string):
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
        db = current.db
        # TODO: add recording of response string
        # TODO: make sure record_dict is updated before this (by User)
        for record_dict in tag_records:
            # TODO: does record_dict include the right info?
            db.tag_records.update_or_insert(db.tag_records.name == user_id,
                                            **record_dict)

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
        #try:
            #print 'storing user in session'
            #session = current.session
            #session.user = None
            #session.user = copy(user)
            #print 'session.user is', session.user
        #except Exception:
            #print traceback.format_exc(5)
        #print 'storing user in db'
        db = current.db
        auth = current.auth
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
        self.id_num = id_num
        self.data = db.npcs[id_num]
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
        locs = [l for l in self.data.map_location]
        return locs

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
                     score, response_string, loc_alias):
        """
        Return a link to trigger submission of a bug report for current step.

        Returns a web2py A() html helper object, ready for embedding in a
        web2py view template. This is meant to be embedded in the reply UI
        which presents the user with an evaluation of the step input.
        """
        response_string = response_string.decode('utf-8')
        vardict = {'answer': response_string.encode('utf-8'),
                   'loc': loc_alias,
                   'log_id': record_id,
                   'path': path_id,
                   'score': score,
                   'step': step_id}
        c = P('Think your answer should have been correct? ',
              A('click here', _class='bug_reporter_link btn btn-danger',
                _href=URL('paideia', 'creating', 'bug.load', vars=vardict)),
              ' to submit a bug report. You can find the instructor\'s ',
              'response in the "bug reports" tab of your user profile.')

        br = POPOVER().widget('Something wrong?', c, id='bug_reporter')

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
        db = current.db
        self.data = db.steps[step_id].as_dict()
        self.repeating = False  # set to true if step already done today
        self.loc = loc
        print 'User.set_loc: loc is ', loc.get_id()
        self.prev_loc = prev_loc
        self.prev_npc = prev_npc
        self.npc = None
        self.username = username
        self.promoted = promoted
        self.new_tags = new_tags

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
        return self.data['locations']

    def get_prompt(self, username=None, raw_prompt=None, **kwargs):
        """
        Return the prompt information for the step. In the Step base class
        this is a simple string. Before returning, though, any necessary
        replacements or randomizations are made.

        If the step cannot be performed in this location, this method returns
        the string 'redirect' so that the Walk.ask() method that called it can
        set a redirect block.
        """
        db = current.db
        auth = current.auth

        if not raw_prompt:
            raw_prompt = self.data['prompt']

        prompt = self._make_replacements(raw_prompt=raw_prompt, **kwargs)

        npc_prompt = DIV(P(prompt, _class='prompt-text'), _class='npc prompt')

        instructions = self._get_instructions()
        if not instructions is None:
            instr_args = {'classnames': 'btn btn-info instructions-popover',
                          'title': 'Instructions for this step',
                          'id': 'instructions_btn'}
            npc_prompt.append(POPOVER().widget('Instructions', instructions,
                                             **instr_args))

        slide_query = db(db.tags.id.belongs(self.data['tags'])).select()
        if slide_query:
            slides_list = UL(_class='prompt_slides')
            for s in slide_query:
                if s.slides:
                    for d in s.slides:
                        slides_list.append(LI(A(d.deck_name,
                                                _href=URL('listing', 'slides',
                                                        args=[d.id]))))
            slides_args = {'classnames': 'btn btn-info slides-popover',
                           'title': 'Relevant slide decks',
                           'id': 'Slides_btn'}
            npc_prompt.append(POPOVER().widget('slides', slides_list,
                              **slides_args))

        npc = self.get_npc()  # duplicate choice prevented in get_npc()
        if not npc:
            locs = self.get_locations()
            kwargs = {'username': db.auth_user[auth.user_id]['first_name'],
                      'next_loc': locs[randrange(len(locs))]}
            return Block('redirect', kwargs=kwargs).get_step()
        try:
            npc_image = npc.get_image()
        except AttributeError:
            npc_image = Npc(npc[1]).get_image()
        bg_image = self.loc.get_bg()

        return {'npc': npc_prompt,
                'npc_image': npc_image,
                'bg_image': bg_image}

    def _make_replacements(self, raw_prompt=None, username=None, reps=None):
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

        return new_string

    def get_responder(self):
        """
        Return form providing navigation options after prompt that does not
        require any answer.
        """
        map_button = A("Back to map", _href=URL('walk'),
                       cid='page',
                       _class='back_to_map btn btn-success icon-map-marker')
        responder = DIV(map_button, _class='responder')
        return responder

    def get_npc(self):
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
        """
        loc = self.loc.get_id()
        db = current.db

        if self.npc and (loc in self.npc.get_locations()):  # ensure choice is made only once for each step
            return self.npc
        else:
            npcs_for_step = self.data['npcs']
            npc_list = [int(n) for n in npcs_for_step
                        if loc in db.npcs[n].map_location]

            if len(npc_list) < 1:
                # no npc for this step available in this location
                # choose an npc to redirect user elsewhere
                good_locs = self.get_locations()
                good_loc = good_locs[randrange(len(good_locs))]
                npcs_here = [n['id'] for n in db(db.npcs.id > 0).select()]
                if self.prev_npc and self.prev_npc.get_id() in npcs_here:
                    next_npc = self.prev_npc.get_id()
                else:
                    next_npc = npcs_here[randrange(len(npcs_here))]
                    self.npc = Npc(next_npc)
                return (good_loc, next_npc)
            elif self.prev_npc and self.prev_npc in npc_list:
                # previous npc here can continue with this step
                self.npc = Npc(self.prev_npc)
                return self.npc
            else:
                # pick a new npc at random
                pick = npc_list[randrange(len(npc_list))]
                self.npc = Npc(pick)
                return self.npc

    def _get_instructions(self):
        """
        Return an html list containing the instructions for the current
        step. Value is returned as a web2py UL() object.
        """
        db = current.db
        instructions = self.data['instructions']
        if not instructions:
            return None
        else:
            mylist = UL()
            for item in instructions:
                item_text = db.step_instructions[item].instruction_text
                mylist.append(LI(item_text))

            return mylist


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
                            vars={'loc': self.loc.get_id()}),
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

        self.next_loc = next_loc if next_loc else "another location in town"
        self.next_step_id = next_step_id
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

        # if mid-way through a path, send to next viable location
        if (not self.next_loc) and self.next_step_id:
            next_locids = db.steps[self.next_step_id].locations
            # find a location that actually has a readable name
            raw_locs = [db.locations[n].readable for n in next_locids]
            next_locs = [n for n in raw_locs if not n is None]
            self.next_loc = next_locs[randrange(len(next_locs))]

        next_loc_name = db.locations[self.next_loc]['readable']

        reps = {'[[next_loc]]': next_loc_name,
                '[[user]]': self.username}
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
                                                username=username,
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
        print 'promoted', self.promoted
        print 'new_tags', self.new_tags
        reps = {'[[user]]': self.username}

        conj = 'You'
        if self.new_tags:
            conj = 'and you'
            nt_records = db(db.badges.tag.belongs(self.new_tags)
                            ).select(db.badges.tag,
                                    db.badges.badge_name).as_list()

            if nt_records:
                nt_intro = P('You\'re ready to start working on some new badges:')
                nt_list = UL(_class='new_tags_list')
                for p in self.new_tags:
                    bname = [row['badge_name'] for row in nt_records
                             if row['tag'] == p]
                    line = LI(SPAN('beginner {}'.format(bname),
                                   _class='badge_name'))
                    nt_list.append(line)
                nt_rep = nt_intro.append(nt_list)
                nt_rep = nt_rep.xml()
            else:
                nt_rep = ''

            reps['[[new_tags_list]]'] = nt_rep

        if self.promoted:
            flat_proms = [i for cat, lst in self.promoted.iteritems() for i in lst if lst]
            prom_records = db(db.badges.tag.belongs(flat_proms)
                              ).select(db.badges.tag,
                                    db.badges.badge_name).as_list()

            if prom_records:
                prom_intro = P('{} have been promoted to these new badge '
                               'levels'.format(conj))
                prom_list = UL(_class='promoted_list')
                ranks = ['beginner', 'apprentice', 'journeyman', 'master']
                for rank, lst in self.promoted.iteritems():
                    if lst:
                        rank = rank.replace('cat', '')
                        i = int(rank) - 1
                        label = ranks[i]
                        for l in lst:
                            bname = [row['badge_name'] for row in prom_records
                                    if row['tag'] == l]
                            line = LI(SPAN(label, ' ', bname, _class='badge_name'))
                            prom_list.append(line)
                    else:
                        pass
                prom_list = prom_list.xml()
                prom_rep = prom_intro.append(prom_list)
            else:
                prom_rep = ''

            reps['[[promoted_list]]'] = prom_rep

        new_string = super(StepAwardBadges, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                reps=reps)
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
                               _href=URL('listing', 'slides', args=[row.id]))))

        # collect replacements
        reps = {'[[slide_list]]': slides.xml(),
                '[[user]]': self.username}
        new_string = super(StepViewSlides, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                reps=reps)
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

    def get_reply(self, user_response=None, answers=None, tips=None):
        """
        Evaluate a user's response and return the resulting data and reply.
        """
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

        result = StepEvaluator(responses, tips).get_eval(user_response)

        bg_image = self.loc.get_bg()

        npc = self.get_npc()  # duplicate choice prevented in get_npc()
        try:
            npc_image = npc.get_image()
        except AttributeError:
            npc_image = Npc(npc[1]).get_image()

        reply = DIV(P(result['reply'],
                      'You said ', UL(LI(user_response)),
                      'Correct answers would include ',
                      readable['readable_short']),
                    _class='npc prompt')

        if tips:
            hints_args = {'classnames': 'btn btn-info',
                          'id': 'instructions_btn'}
            reply.append(POPOVER().widget('Hints', tips, **hints_args))

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

    def __init__(self, path_id=None, blocks=[], loc=None, prev_loc=None,
                 completed_steps=None, last_step_id=None, step_sent_id=None,
                 step_for_prompt=None, step_for_reply=None, prev_npc=None,
                 db=None):
        """
        Initialize a paideia.Path object.

        The following arguments are required at init:
            path_id
            loc_id
        The others are for dependency injection in testing
        """
        self.prev_loc = prev_loc if prev_loc else None
        self.prev_npc = prev_npc if prev_npc else None
        self.loc = loc
        self.npc_id = None
        self.blocks = blocks
        db = current.db if not db else db
        self.path_dict = db.paths[path_id].as_dict()
        self.steps = self.get_steps()
        self.completed_steps = completed_steps if completed_steps else []
        self.last_step_id = last_step_id
        self.step_sent_id = step_sent_id
        self.step_for_prompt = step_for_prompt
        self.step_for_reply = step_for_reply

    def get_id(self):
        """Return the id of the current Path object."""
        return self.path_dict['id']

    def _prepare_for_prompt(self):
        """ move next step in this path into the 'step_for_prompt' variable"""
        try:
            if len(self.steps) > 1:
                next_step = self.steps.pop(0)
            else:
                next_step = copy(self.steps[0])
                self.steps = []

            self.step_for_prompt = next_step
            # not affected by Block, picked up again on next valid interaction

            self.step_sent_id = next_step.get_id()
            # step_sent_id may be overridden if Block found

            if len(self.completed_steps) > 0:
                last_step = self.completed_steps[-1]
                self.last_step_id = last_step.get_id()
                self.prev_npc = last_step.get_npc().get_id()
                # only updated here if mid-way through multi-step path
                # otherwise should have been set at Path init by
                # User.get_path()

            return True
        except:
            return False

    def _prepare_for_reply(self):
        """
        Move the active step from self.step_for_prompt to self.step_for_reply.
        This prepares a step for the evaluation of user-input.
        """
        if self.step_for_prompt:
            self.step_for_reply = copy(self.step_for_prompt)
            self.step_for_prompt = None
            assert not self.step_for_prompt
            return True
        else:
            return False

    def complete_step(self):
        """
        Deactivate current step.
        """
        if self.step_for_reply:
            self.step_for_reply = None
            assert not self.step_for_prompt
            return True
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
            'returning a Block: need_to_reply'
            return Block('need_to_reply', data=self.step_for_reply)

        if self.step_for_prompt:
            next_step = copy(self.step_for_prompt)
        elif self._prepare_for_prompt():
            next_step = copy(self.step_for_prompt)

        # all blocks triggered here, but can be set elsewhere
        active_block = self._check_for_blocks(next_step)
        if active_block:
            return active_block
        else:
            if isinstance(next_step, (StepText, StepMultiple)):
                assert self._prepare_for_reply()
                assert not self.step_for_prompt
            else:
                assert self.complete_step()
                assert not self.step_for_reply
                assert not self.step_for_prompt
            return next_step

    def _set_block(self, condition, kwargs=None, data=None):
        """ Set a blocking condition on this Path object. """
        newargs = {'prev_loc': self.prev_loc,
                   'prev_npc': self.prev_npc,
                   'loc': self.loc}
        if 'username' not in kwargs.keys():
            db = current.db
            auth = current.auth
            kwargs['username'] = db.auth_user[auth.user_id]['first_name']
        kwargs.update(newargs)
        self.blocks.append(Block(condition=condition,
                                 kwargs=kwargs,
                                 data=data))
        return True

    def _check_for_blocks(self, next_step, db=None):
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
        # check that next step can be asked here, else redirect
        locs = next_step.get_locations()
        if not (self.loc.get_id() in locs):
            kwargs = {'next_loc': locs[randrange(len(locs))]}
            self._set_block('redirect', kwargs=kwargs)
            print 'setting redirect block'

        if self.blocks:
            print 'blocks present'
            print 'types:', [b.get_condition() for b in self.blocks]
            block_step = self.blocks.pop(0).get_step()
            if block_step:
                # TODO: make sure that the block step isn't added to completed
                # or step_to_answer or last_step_id
                self.step_sent_id = block_step.get_id()
                return block_step
        else:
            return False

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
        reply_step = copy(self.step_for_reply)
        # TODO is this too early to append step to completed_steps?
        self.completed_steps.append(reply_step)
        # TODO: add step_sent_id check to unit test
        self.step_sent_id = reply_step.get_id() if reply_step else None

        return reply_step

    def get_steps(self):
        """
        Return a list containing all the steps of this path as Step objects.
        """
        db = current.db
        static_args = {'loc': self.loc,
                       'prev_loc': self.prev_loc,
                       'prev_npc': self.prev_npc,
                       'db': db}
        steplist = [StepFactory().get_instance(step_id=i, **static_args)
                    for i in self.path_dict['steps']]

        return steplist

    def set_location(self, loc):
        """
        Set the active location after initialization of the Path object.
        """
        old_loc_id = self.loc.get_id()
        if loc.get_id() == old_loc_id:
            pass
        else:
            self.prev_loc = old_loc_id
            self.loc = loc
        return True

    def set_npc(self, new_npc_id):
        """
        Set the currently active npc after initialization of the Path object.
        """
        old_npc_id = self.npc_id
        if new_npc_id == old_npc_id:
            pass
        else:
            self.prev_npc = old_npc_id
            self.npc_id = new_npc_id
        return True


class PathChooser(object):
    """
    Select a new path to begin when the user begins another interaction.
    """

    def __init__(self, tag_progress, loc_id, paths_completed, db=None):
        """Initialize a PathChooser object to select the user's next path."""
        self.categories = {k: v for k, v in tag_progress.iteritems()
                           if not k in ['name', 'latest_new']}
        print 'in pathchooser cats', self.categories
        self.rank = tag_progress['latest_new']
        print 'in pathchooser rank', self.rank
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
        print 'getting _paths_by_category for cat', cat
        # TODO: include paths with tag as secondary, maybe in second list
        # TODO: cache the select below and just re-order randomly
        ps = db().select(db.paths.ALL, orderby='<random>')
        print len(ps)
        # filter by category, then
        # filter out paths with a step that's not set to "active"
        # avoid steps with right tag but no location
        taglist = self.categories['cat{}'.format(cat)]
        # TODO: make find below more efficient

        ps = ps.find(lambda row:
                     [t for t in row.tags
                      if taglist and (t in taglist)])
        print len(ps)
        ps = ps.find(lambda row:
                     [s for s in row.steps
                      if db.steps(s).status != 2])
        print len(ps)
        ps.exclude(lambda row:
                   [s for s in row.steps
                    if db.steps(s).locations is None])
        print len(ps)
        # TODO: why does this kill the select?
        #ps.exclude(lambda row:
                   #[t for t in row.tags
                    #if db.tags[t].tag_position > self.rank])
        print len(ps)
        pathset = [p.id for p in ps]
        print len(pathset)

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

        # catpaths is already filtered by category
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
            path = p_here_new[randrange(0, len(p_here_new))]
        elif p_new:
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
        print 'starting choose'

        cat_list = self._order_cats()

        print 'cat_list', cat_list
        # cycle through categories, starting with the one from _get_category()
        for cat in cat_list:
            catpaths = self._paths_by_category(cat, self.rank)
            print 'catpaths', catpaths
            catpids = [p.id for p in catpaths[0]]
            catpids.sort()
            #cattags = [p.tags for p in catpaths[0]]
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

    def __init__(self, userdata, loc, tag_records, tag_progress, db=None):
        """
        Initialize a paideia.User object.

        ## Argument types and structures
        - userdata: {'name': str, 'id': int, '}
        - localias: str
        - tag_progress: rows.as_dict()
        - tag_records: rows.as_dict
        """
        try:
            self.time_zone = userdata['time_zone']
            db = current.db if not db else db
            # TODO: Update tag_records as steps proceed
            self.blocks = []
            self.name = userdata['first_name']
            self.user_id = userdata['id']
            self.path = None
            self.completed_paths = []
            self.last_response_text = None
            self.cats_counter = 0  # timing re-categorization in _get_categories()
            self.old_categories = {}
            self.tag_records = tag_records
            self.rank = tag_progress['latest_new'] if tag_progress else None
            self.tag_progress = tag_progress
            self.promoted = None
            self.new_tags = None
            self._get_categories(rank=self.rank,
                                 old_categories=self.old_categories,
                                 tag_records=tag_records)
            self.inventory = []
            self.session_start = datetime.datetime.utcnow()
            self.npc_id = None
            self.last_npc = None
            self.loc = loc
            self.last_loc = loc.get_id()
            self.loc_id = loc.get_id()
            self.redirect_loc = None
            self.quota = 40
        except Exception:
            print traceback.format_exc(5)

    def get_id(self):
        """Return the id (from db.auth_user) of the current user."""
        return self.user_id

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

    def set_location(self, loc):
        """
        Update the user's location after initialization of the User object.

        Includes setting of self.last_loc to the old location id and calling
        of path.set_location().

        Returns a boolean indicating success/failure.
        """
        if loc.get_id() == self.loc.get_id():
            pass
        else:
            self.last_loc = self.loc.get_id()
            self.loc = loc
            self.loc_id = loc.get_id()
            self.path.set_location(loc)
        return True

    def set_npc(self, npc_id):
        """
        Update the current npc after initialization of the User object.

        Includes setting of self.last_npc to the old npc id and calling
        of path.set_npc().

        Returns a boolean indicating success/failure.
        """
        if npc_id == self.npc_id:
            pass
        else:
            self.last_npc = self.npc_id
            self.npc_id = npc_id
            self.path.set_npc(npc_id)
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

    def get_path(self, loc, categories=None, db=None, path=None, repeat=None):
        """
        Return the currently active Path object.

        None of the arguments is strictly necessary, but loc will usually be
        provided. The others are only used for dependency injection during
        testing.

        Note: redirect block is set here if the chosen path cannot be
        begun in this location
        """
        db = current.db if not db else db
        categories = self._get_categories() if not categories else categories
        self.loc = loc

        if path:
            self.path = Path(path_id=path, loc=loc)
        if repeat:
            if self.path:
                pass  # do same path again
            else:
                self.path = self.completed_paths.pop(-1)
        elif self.path and (len(self.path.steps) or self.path.step_for_reply):
            pass  # continue with unfinished path, no new choice
        else:
            if self.path:
                self._complete_path()  # catch end-of-path and triggers new choice
            if not self.tag_progress:  # in case User was badly initialized
                self._get_categories()
            choice = PathChooser(self.tag_progress, loc.get_id(),
                                 self.completed_paths).choose()
            new_location = choice[1]
            path = Path(path_id=choice[0]['id'], loc=loc)
            # check for a redirect location to start the selected path
            if new_location:
                # TODO: get block logic working here
                kwargs = {'loc': self.loc,
                          'next_loc': new_location,
                          'username': self.name}
                path._set_block('redirect', kwargs=kwargs)
            self.path = path

        if len(self.completed_paths) > self.quota:
            kwargs = {'quota': self.quota}
            self.path._set_block('quota reached', kwargs=kwargs)

        return self.path

    def _get_categories(self, rank=None, old_categories=None,
                        tag_records=None, utcnow=None):
        """
        Return a categorized dictionary with four lists of tag id's.

        This method is important primarily to decide whether a new
        categorization is necessary before instantiating a Categorizer object

        # TODO: do we need to create new categorizer object each time?

        The method is intended to be called with no arguments.
        The rank, categories, and old_categories arguments are not needed,
        since the values can be drawn from the User class instance. They are
        provided to help in unit testing. The arguments tag_records and utcnow
        are required only for dependency injection during unit testing.
        """
        rank = self.rank if not rank else rank
        tag_records = self.tag_records if not tag_records else tag_records
        utcnow = datetime.datetime.utcnow() if not utcnow else utcnow
        old_categories = self.old_categories if not old_categories \
            else old_categories
        try:
            categories = self.categories
        except AttributeError:
            categories = None
        # only re-categorize every 10th evaluated step
        if self.cats_counter in range(1, 5) and self.tag_progress:
            self.cats_counter += 1
            return True
        else:
            c = Categorizer(rank, categories, tag_records, utcnow=utcnow)
            cat_result = c.categorize_tags()
            print 'cat_result is', cat_result
            # Set blocks for 'new_tags' (view_slides) and 'promoted' conditions

            nt = cat_result['new_tags']
            pr = cat_result['promoted']
            if nt and self.path:  # These blocks need to be on the User, not path
                self.path._set_block('new tags', kwargs={'new_tags': nt})
                self.path._set_block('view slides', kwargs={'new_tags': nt})
            if pr and self.path:
                self.path._set_block('promoted', kwargs={'promoted': pr, 'new_tags': nt})

            self.rank = cat_result['tag_progress']['latest_new']
            self.tag_progress = cat_result['tag_progress']
            self.promoted = cat_result['promoted']
            self.new_tags = cat_result['new_tags']
            self.cats_counter = 0  # reset counter

            return True

    def _get_old_categories(self):
        if self.old_categories:
            return self.old_categories
        else:
            return None

    def _complete_path(self):
        """
        Move the current path from the path variable to 'completed_paths' list.
        Set last_npc and last_loc before removing the path.
        """
        if self.path.completed_steps:
            last_step = self.path.completed_steps[-1]
            self.last_npc = last_step.get_npc()
            self.last_loc = last_step.loc
        # TODO: How much does storing whole path obj affect memory use?

        # TODO: Work out handling of the location in paths/steps
        self.completed_paths.append(copy(self.path))
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

    def __init__(self, rank, categories, tag_records,
                 secondary_right=None, utcnow=None, db=None):
        """Initialize a paideia.Categorizer object"""
        self.rank = rank
        self.tag_records = tag_records
        self.old_categories = categories
        self.utcnow = utcnow
        self.secondary_right = secondary_right

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
        old_categories = self.old_categories if not old_categories else old_categories
        tag_records = self.tag_records if not tag_records else tag_records
        db = current.db if not db else db
        new_tags = None
        # if user has not tried any tags yet, start first set
        if len(tag_records) == 0:
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
                  'latest_new': 1}
            return {'tag_progress': tp,
                    'new_tags': categories['cat1'],
                    'promoted': None,
                    'demoted': None,
                    'categories': categories}
        else:
            # otherwise, categorize tags that have been tried
            self.tag_records = self._add_secondary_right(tag_records)
            categories = self._core_algorithm()
            categories = self._add_untried_tags(categories)
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

            return {'tag_progress': tag_progress,
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
                # add new secondary_right attempts from attempt_log
                # (TODO: this is temporary)
                #db_recs = db(
                            #(db.attempt_log.name == rec['name']) &
                            #(db.attempt_log.score == 1.0) &
                            #(db.attempt_log.dt_attempted >= rec['tlast_right']) &
                            #(db.attempt_log.step == db.steps.id) &
                            #(db.steps.tags_secondary.contains(rec['tag']))
                #).select(db.attempt_log.dt_attempted).as_list()

                right2 = rec['secondary_right']

                #if db_recs:
                    #dates = [t for v in db_recs for t in v.iteritems()]
                    #try:
                        #right2.extend(dates)
                    #except AttributeError:
                        #right2 = dates

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
        categories = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        utcnow = self.utcnow
        if not utcnow:
            utcnow = datetime.datetime.utcnow()
        if not tag_records:
            tag_records = self.tag_records
        # TODO: Get secondary_right here

        for record in tag_records:
            #note: arithmetic operations yield datetime.timedelta objects
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
                 # require at least 10 right answers
                 (record['times_right'] >= 10))
                or ((record['times_right'] >= 10) and
                    # require ratio of at least 5 right to 1 wrong
                    ((record['times_wrong'] / record['times_right']) <= 0.2)
                    # require that tag has right answer within last 2 days
                    and (right_dur <= datetime.timedelta(days=14)))):
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

        left_out = []
        for r in range(1, rank + 1):
            newtags = [t['id'] for t in
                       db(db.tags.tag_position == r).select().as_list()]
            alltags = list(chain(*categories.values()))
            left_out.extend([t for t in newtags if t not in alltags])
        if left_out:
            categories['cat1'].extend(left_out)

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
        'new tags'
        'view slides'
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
        if isinstance(data, Step):
            self.step = data  # in some cases easiest to just pass existing step
        else:
            self.step = self.make_step(condition, kwargs=kwargs, data=data)

    def make_step(self, condition, kwargs=None, data=None):
        """Create correct Step subclass and store as an instance variable."""
        db = current.db
        kwargs = {} if not kwargs else kwargs
        step_classes = {'view slides': 6,
                        'quota reached': 7,
                        'new tags': 8,
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

    def get_step(self):
        """Return the appropriate step for the current blocking condition"""
        if self.step:
            return self.step
        else:
            return False

    def get_data(self):
        """Return the secondary data, if any, belonging to this Block."""
        if self.data:
            return self.data
        else:
            return False
