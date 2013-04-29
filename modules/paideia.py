# -*- coding: utf-8 -*-
from gluon import current, redirect
from gluon import IMG, URL, SQLFORM, SPAN, DIV, UL, LI, A, Field
from gluon import IS_NOT_EMPTY, IS_IN_SET
from random import randint, randrange
import re
import datetime
from itertools import chain
from inspect import getargvalues, stack
from copy import copy
#from pprint import pprint

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
        self.db = db
        if not db:
            self.db = current.db
        loc_id = db(db.locations.alias == localias).select().first().id
        self.loc = Location(loc_id, db)
        self.response_string = response_string
        if not userdata:
            auth = current.auth
            user_id = auth.user_id
            userdata = db.auth_user[user_id].as_dict()

        self.user = self._get_user(userdata=userdata,
                                   localias=localias,
                                   tag_records=tag_records,
                                   tag_progress=tag_progress)

    def _get_user(self, userdata=None, localias=None, tag_records=None,
                  tag_progress=None, db=None):
        # initialize or re-activate User object
        try:
            return self.user
        except AttributeError:  # because no user yet on this Walk
            try:
                session = current.session
                user = session.user
                assert user.is_stale() is False
                self.user = user
                return user
            # TODO: need error condition here for stale user
            except AttributeError:  # because no user yet in this session
                if not db:
                    db = self.db
                if not tag_records:
                    auth = current.auth
                    tag_records = db(db.tag_records.name == auth.user_id).select()
                    tag_records = tag_records.as_list()
                if not tag_progress:
                    auth = current.auth
                    tag_progress = db(db.tag_progress.name == auth.user_id).select()
                    #tag_progress_length = len(tag_progress)  # TODO log if > 1
                    tag_progress = tag_progress.first().as_dict()
                    # Handle first-time users, who won't have db row to fetch
                    if not tag_progress:
                        db.tag_progress.insert(latest_new=1)
                        tag_progress = db(db.tag_progress.name ==
                                          self.user.get_id()).select()
                        tag_progress = tag_progress.first().as_dict()

                self.user = User(userdata, localias, tag_records, tag_progress)
                return self.user

    def map(self, db=None):
        """
        Return the information necessary to present the paideia navigation
        map interface.
        """
        if not db:
            db = self.db
            cache = current.cache

        map_image = '/paideia/static/images/town_map.svg'
        # TODO: Review cache time
        locations = db().select(db.locations.ALL,
                                orderby=db.locations.location,
                                cache=(cache.ram, 60 * 60)).as_list()
        return {'map_image': map_image, 'locations': locations}

    def ask(self):
        """Return the information necessary to initiate a step interaction."""
        loc = self.loc
        # TODO: switch the localias argument below to the ful Location obj
        p = self.user.get_path(loc)
        s = p.get_step_for_prompt()
        prompt = s.get_prompt()
        responder = s.get_responder()
        p.prepare_for_answer()
        self._store_user(self.user)

        return {'prompt': prompt, 'responder': responder}

    def reply(self, response_string):
        """docstring for __reply__"""

        p = self.user.get_path(self.loc)
        path_id = p.get_id()

        s = p.get_step_for_reply(self.db)
        step_id = s.get_id()

        reply = s.get_reply(response_string)
        tags = reply['tags']
        score = reply['score']
        times_right = reply['times_right']
        times_wrong = reply['times_wrong']

        record_id = self._record_step(path_id, step_id, tags, score,
                                      times_right, times_wrong, response_string)

        bug_reporter = BugReporter(record_id, path_id, step_id,
                                   tags, score, response_string)
        p.complete_step(step_id)

        if p.check_for_end() is True:
            self.user._complete_path(path_id)

        self._store_user()

        return {'reply': reply, 'bug_reporter': bug_reporter}

    def _record_cats(self, tag_progress, categories, promoted,
                     demoted, new_tags, db=None):
        """
        Record changes to the user's working tags and their categorization.

        Changes recorded in the following db tables:
        - badges_begun: new and promoted tags
        - tag_progress: changes to categorization (only if changes made)
        """
        if not db:
            db = self.db
        user = self.user.get_id()
        now = datetime.datetime.utcnow()
        # record awarding of promoted and new tags in table db.badges_begun
        promoted['cat1'] = new_tags

        if promoted:
            for cat, lst in promoted.iteritems():
                if lst:
                    for tag in lst:
                        tag_record = db((db.badges_begun.name == user) &
                                        (db.badges_begun.tag == tag))
                        if not tag_record.count():
                            db.badges_begun.insert(**{'name': user,
                                                      'tag': tag,
                                                      cat: now})
                        else:
                            tag_record.update({cat: now})

        # update tag_progress table with current categorization
        db(db.tag_progress.name == user).update(**categories)

        return categories

    def _record_step(self, tag_records, categories, new_tags):
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
        ** if secondary_right is sufficient length, delete it and
                - add 1 to times_right
                - set tlast_right to now

        ** be sure not to log redirect and utility steps.
        """

        return True

    def _store_user(self, user=None):
        """
        Store the current User object (from self.user) in session.user

        Returns a boolean value indicating whether the storing was
        successful or not.
        """
        if not user:
            user = self.user
        session = current.session
        session.user = user
        return True


class Location(object):
    """
    Represents a location in the game world.
    """

    def __init__(self, id_num, db=None):
        """Initialize a Location object."""
        if db is None:
            db = current.db
        self.db = db
        self.id_num = id_num
        self.data = db.locations[id_num]

    def get_alias(self):
        """Return the alias of the current Location as a string."""
        return self.data.alias

    def get_name(self):
        """Return the name of the current Location as a string.
        This 'name' is used in the svg map to identify the location."""
        return self.data.location

    def get_readable(self):
        """
        Return the readable name of the current Location as a string.
        This is used to identify the location in communication with the user.
        """
        return self.data.readable

    def get_bg(self):
        """Return the background image of the current Location as a web2py
        IMG helper object."""
        url = URL('static/images', self.db.images[self.data.bg_image].image)
        bg = IMG(_src=url)
        return bg

    def get_id(self):
        """
        Return the id for the database row representing the current
        Location (as an int).
        """
        return self.data.id


class Npc(object):
    '''
    Represents one non-player character in the game
    '''

    def __init__(self, id_num, db=None):
        """
        initialize an npc object with database data for the character
        with the provided id
        """
        if db is None:
            db = current.db
        self.db = db
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
        img = URL('paideia', 'static', 'images/{}'.format(self.image))
        return img

    def get_locations(self):
        """docstring for get_locations"""
        locs = [Location(l) for l in self.data.location]
        return locs

    def get_description(self):
        """docstring for get_locations"""
        return self.data.notes


class NpcChooser(object):
    """
    Choose an npc to engage the user in the current step, based on the current
    location and the parameters of the step itself.
    """
    def __init__(self, step, location, prev_npc, prev_loc):
        """
        Initialize an NpcChooser object.
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
        location = self.location
        prev_npc = self.prev_npc
        prev_loc = self.prev_loc
        # TODO: step.get_npcs returns ids or Npc objects?

        if ((location.get_readable() == prev_loc.get_readable()) and
                (prev_npc.get_id() in available)):
            return prev_npc
        else:
            available2 = [n for n in available
                          if n.get_id() == prev_npc.get_id()
                          and location.get_id() in n.get_locations()]
            if len(available2) > 1:
                return available2[randint(0, len(available2) - 1)]
            else:
                return available2[0]


class BugReporter(object):
    """
    Class representing a bug-reporting widget to be presented along with the
    evaluation of the current step.
    """
    def __init__(step_id, user_response, record_id):
        """Initialize a BugReporter object"""
    pass


class StepFactory(object):
    """
    A factory class allowing automatic generation of correct Step subclasses.
    """
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
        if not db:
            db == current.db
        # TODO: read db data here and pass it forward as a dict
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

    def __init__(self, step_id=None, loc=None, prev_loc=None, prev_npc_id=None,
                 db=None, **kwargs):
        """Initialize a paideia.Step object"""
        if db is None:
            db == current.db
        self.db = db
        self.data = db.steps[step_id].as_dict()
        self.repeating = False  # set to true if step already done today
        self.loc = loc
        self.prev_loc = prev_loc
        self.prev_npc_id = prev_npc_id
        self.npc = None

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
        Return a list of tag id's
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
        if not raw_prompt:
            raw_prompt = self.data['prompt']

        prompt = self._make_replacements(username=username,
                                         raw_prompt=raw_prompt,
                                         **kwargs)

        instructions = self._get_instructions()
        npc = self.get_npc()  # duplicate choice prevented in get_npc()
        if npc is False:
            return 'redirect'
        npc_image = npc.get_image()
        # prompt no longer tagged or converted to markmin here, but in view

        return {'prompt': prompt,
                'instructions': instructions,
                'npc_image': npc_image}

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
            print 'k', k
            print 'v', v
            if not v:
                v = ''
            new_string = new_string.replace(k, v)

        return new_string

    def get_responder(self):
        """
        Return form providing navigation options after prompt that does not
        require any answer.
        """
        map_button = A("Map", _href=URL('walk'),
                       cid='page',
                       _class='button-yellow-grad back_to_map icon-location')
        responder = DIV(map_button)
        return responder

    def get_npc(self):
        """
        Return an Npc object appropriate for this step

        If there is no suitable npc available here, returns false.
        TODO: need to trigger redirect on false return
        """
        loc = self.loc.get_id()
        print 'loc is', loc

        if self.npc and (loc in self.npc.get_locations()):  # ensure choice is made only once for each step
            return self.npc
        else:
            npcs_for_step = self.data['npcs']
            npc_list = [int(n) for n in npcs_for_step
                        if loc in self.db.npcs[n].location]
            print 'npcs in loc:', npc_list

            if len(npc_list) < 1:
                print 'no npc to choose'
                return False
            elif self.prev_npc_id in npc_list:
                self.npc = Npc(self.prev_npc_id, db=self.db)
                print 'choosing npc', self.npc.get_id()
                return self.npc
            else:
                pick = npc_list[randint(1, len(npc_list)) - 1]
                self.npc = Npc(pick, db=self.db)
                print 'choosing npc', self.npc.get_id()
                return self.npc

    def _get_instructions(self):
        """
        Return an html list containing the instructions for the current
        step. Value is returned as a web2py UL() object.
        """
        instructions = self.data['instructions']
        if not instructions:
            return None
        else:
            list = []
            for item in instructions:
                item_row = self.db.step_instructions[item]
                item_text = item_row.text
                list.append(item_text)

            return list


class StepResponder(Step):
    """
    An abstract subclass of Step that adds a 'continue' button to the responder.
    """
    def get_responder(self):
        """
        Return the html form to allow the user to respond to the prompt for
        this step.
        """
        responder = super(StepResponder, self).get_responder()

        continue_button = A("Continue", _href=URL('walk', args=['ask'],
                            vars={'loc': self.loc.get_id()}),
                            cid='page',
                            _class='button-green-grad next_q')
        responder.append(continue_button)

        return responder


class StepRedirect(Step):
    '''
    A subclass of Step. Handles the user interaction when the user needs to be
    sent to another location.
    '''
    def __init__(self, step_id=None, step_data=None, loc=None, prev_loc=None,
                 prev_npc_id=None, username=None, next_step_id=None, db=None,
                 **kwargs):
        """docstring for __init__"""

        self.username = username
        self.next_step_id = next_step_id
        # delegate common init tasks to Step superclass
        kwargs = locals()
        del(kwargs['self'])
        super(StepRedirect, self).__init__(**kwargs)

    def _make_replacements(self, raw_prompt=None, username=None, db=None,
                           next_step_id=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        if not db:
            db = self.db
        if not username:
            username = self.username
        if not next_step_id:
            next_step_id = self.next_step_id
        next_loc = 'somewhere else in town'  # generic default
        # if mid-way through a path, send to next viable location
        # TODO: find a way to set this value to another location with an
        # available path if the current step is the last in its path.
        if next_step_id:
            next_locids = db.steps[next_step_id].locations
            # find a location that actually has a readable name
            raw_locs = [db.locations[n].readable for n in next_locids]
            next_locs = [n for n in raw_locs if not n is None]
            next_loc = next_locs[randrange(len(next_locs))]
        else:
            pass

        reps = {'[[next_loc]]': next_loc,
                '[[user]]': username}
        new_string = super(StepRedirect, self)._make_replacements(
            raw_prompt=raw_prompt,
            username=username,
            reps=reps)
        return new_string


class StepQuotaReached(StepResponder, Step):
    '''
    A Step that tells the user s/he has completed the daily minimum # of steps.
    '''
    def _make_replacements(self, raw_prompt=None, username=None):
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


class StepAwardBadges(StepResponder, Step):
    '''
    A Step that informs the user when s/he has earned new badges.
    '''

    def _make_replacements(self, raw_prompt=None, username=None,
                           new_badges=None, promoted=None, db=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        if not username:
            username = self.username
        if not db:
            db = self.db

        reps = {'[[user]]': username}

        flat_proms = [i for cat, lst in promoted.iteritems() for i in lst if lst]
        prom_records = db(db.badges.tag.belongs(flat_proms)
                          ).select(db.badges.tag,
                                   db.badges.badge_name).as_list()

        if prom_records:
            prom_list = UL(_class='promoted_list')
            ranks = ['beginner', 'apprentice', 'journeyman', 'master']
            for rank, lst in promoted.iteritems():
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
        else:
            prom_list = ''

        reps['[[promoted_list]]'] = prom_list

        new_string = super(StepAwardBadges, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                username=username,
                                                reps=reps)
        return new_string


class StepViewSlides(Step):
    '''
    A Step that informs the user when s/he needs to view more grammar slides.
    '''

    def _make_replacements(self, raw_prompt=None, username=None,
                           new_badges=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].

        new_badges value should be a list of tag id's as integers
        """
        db = self.db
        tags = db((db.tags.id == db.badges.tag) &
                  (db.tags.id.belongs(new_badges))).select().as_list()
        # get the relevant badges (id, name, and description)
        badges = [row['badges']['id'] for row in tags]
        if isinstance(badges[0], list):
            # anticipating possibility that badges could match multiple tags
            badges = [i for lst in badges for i in lst]
        else:
            pass

        # build list of badges
        badgerows = db(db.badges.id.belongs(badges)
                       ).select(db.badges.id,
                                db.badges.badge_name,
                                db.badges.description)

        badge_list = UL(_class='badge_list')
        for b in badgerows:
            badge_list.append(LI(SPAN(b.badge_name, _class='badge_name'),
                                 ' for ',
                                 b.description))

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
                                orderby=dtable.position)

        # build slide deck list
        slides = UL(_class='slide_list')
        for row in sliderows:
            slides.append(LI(A(row.deck_name,
                               _href=URL('listing', 'slides', args=[row.id]))))

        # collect replacements
        reps = {'[[badge_list]]': badge_list.xml(),
                '[[slides]]': slides.xml(),
                '[[user]]': username}
        new_string = super(StepViewSlides, self
                           )._make_replacements(raw_prompt=raw_prompt,
                                                username=username,
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
        return form

    def get_reply(self, user_response=None, answers=None, tips=None):
        """docstring for get_reply"""
        if not user_response:
            request = current.request
            user_response = request.vars['response']

        readable = self._get_readable()
        try:
            tips = self.data['hints']
            responses = {k: v for k, v in self.data.iteritems()
                         if k and (k in ['response1', 'response2', 'response3'])}
        except TypeError:
            tips = self.data['step'].data['hints']
            responses = {k: v for k, v in self.data['step'].data.iteritems()
                         if k and (k in ['response1', 'response2', 'response3'])}

        result = StepEvaluator(responses, tips).get_eval(user_response)

        return {'reply_text': result['reply'],
                'tips': tips,
                'readable_short': readable['readable_short'],
                'readable_long': readable['readable_long'],
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

        if '|' in readable:

            # show first two answers for short readable
            rsplit = readable.split('|')
            readable_short = rsplit[:3]
            if len(rsplit) <= 2:
                readable_long = None
            else:
                readable_long = rsplit
        else:
            readable_short = [readable]
            readable_long = None

        print 'readable_long:', readable_long
        print 'len readable:', len(readable)

        return {'readable_short': readable_short,
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
        vals = self.data['options']
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

    def __init__(self, path_id=None, blocks=None, loc=None, prev_loc=None,
                 completed_steps=None, last_step_id=None, step_for_prompt=None,
                 step_for_reply=None, prev_npc_id=None, db=None):
        """
        Initialize a paideia.Path object.

        The following arguments are required at init:
            path_id
            loc_id
        The others are for dependency injection in testing
        """
        if prev_loc:
            self.prev_loc_id = prev_loc.get_id()
        self.prev_npc_id = prev_npc_id
        self.loc = loc
        self.blocks = blocks
        if not db:
            db = current.db
        self.db = db
        self.path_dict = db.paths[path_id].as_dict()
        # assemble list of step objects for the whole path
        static_args = {'loc': self.loc, 'prev_loc': prev_loc,
                       'prev_npc_id': prev_npc_id, 'db': db}
        self.steps = [StepFactory().get_instance(step_id=i, **static_args)
                      for i in self.path_dict['steps']]
        # allow for insertion of these values by argument for testing
        if not completed_steps:
            self.completed_steps = []
        self.last_step_id = last_step_id
        self.step_for_prompt = step_for_prompt
        self.step_for_reply = step_for_reply

    def get_id(self):
        """Return the id of the current Path object."""
        return self.path_dict['id']

    def _prepare_for_prompt(self):
        """ move next step in this path into the 'step_for_prompt' variable"""
        if len(self.steps) > 1:
            next_step = self.steps.pop(0)
        else:
            next_step = copy(self.steps[0])
            self.steps = []
        self.step_for_prompt = next_step

        return self.step_for_prompt

    def get_step_for_prompt(self, loc=None):
        """Find the next unanswered step in the current path and return it.
        If the selected step cannot be performed at this location, set a
        Block on condition
        """
        # check for active step that hasn't been asked because of block
        if loc:
            self.loc = loc

        next_step = self._prepare_for_prompt()

        # check that next step can be asked here, else redirect
        locs = next_step.get_locations()
        if not (self.loc.get_id() in locs):
            new_block = Block().set_block(condition='redirect', kwargs=None,
                                          data=locs)
            if self.blocks:
                self.blocks.append(new_block)
            else:
                self.blocks = [new_block]

        # check for blocks
        if self.blocks:
            block_step = self.blocks.pop(0).get_step()
            if block_step:
                # TODO: make sure that the block step isn't added to completed
                # or step_to_answer or last_step_id
                # TODO: how will we remove the block?
                self.step_sent_id = block_step.get_id()
                return block_step

        self.step_sent_id = self.step_for_prompt.get_id()
        return next_step

    def prepare_for_answer(self, step_for_prompt=None, step_for_reply=None,
                           step_sent_id=None):
        """
        Prepare the class instance variables to receive the user's response.

        This method needs to be called before the step prompt is sent to the
        view. This includes:
        - resetting step_for_prompt to None
        - pop active step and either move to step_for_reply or simply delete
        """
        # TODO: make sure this doesn't run if the step was a block step
        # block steps are never set in self.step_for_prompt since should
        # not be re-activated
        # TODO: in Walk, provide id of actual step being sent to view

        if step_sent_id:
            self.step_sent_id = step_sent_id  # for testing purposes
        if not step_for_prompt:
            step_for_prompt = self.step_for_prompt
        if not step_for_reply:
            step_for_reply = self.step_for_reply

        if step_for_prompt.get_id() == step_sent_id:
            # this type check filters out block steps (subclasses of Block)
            if not isinstance(step_for_prompt, Block):
                self.step_for_reply = copy(step_for_prompt)
                self.step_for_prompt = None
            else:
                self.step_for_reply = None

        replynum = self.step_for_reply.get_id()
        try:
            promptnum = self.step_for_prompt.get_id()
        except:
            promptnum = None

        return {'step_for_reply': replynum,
                'step_for_prompt': promptnum,
                'step_sent_id': self.step_sent_id}

    def remove_block(self):
        """Remove an active block once its step has been sent to view."""
        # TODO: make sure that the block step isn't added to completed
        # or step_to_answer or last_step_id
        block_done = self.blocks.pop(0)
        return {'block_done': block_done, 'blocks': self.blocks}

    def get_step_for_reply(self, db=None):
        """Return the Step object that is currently active for this path."""
        reply_step = self.step_for_reply
        return reply_step


class PathChooser(object):
    """
    Select a new path to begin when the user begins another interaction.
    """

    def __init__(self, categories, loc_id, paths_completed, db=None):
        """Initialize a PathChooser object to select the user's next path."""
        self.categories = categories
        if not db:
            self.db = current.db
        self.db = db
        self.loc_id = loc_id
        self.completed = paths_completed

    def _order_cats(self):
        """
        Choose a category to prefer in path selection and order categories
        beginning with that number.

        Returns a list with four members including the integers one-four.
        """
        switch = randint(1, 101)

        if switch in range(1, 75):
            cat = 1
        elif switch in range(75, 90):
            cat = 2
        elif switch in range(90, 98):
            cat = 3
        else:
            cat = 4

        cat_range = range(1, 5)
        cat_list = cat_range[cat:5] + cat_range[0:cat]

        return cat_list

    def _paths_by_category(self, cat):
        """
        Assemble list of paths tagged with tags in each category for this user.

        Returns a dictionary with categories as keys and corresponding lists
        as values.
        """
        db = self.db

        ps = db().select(db.paths.ALL, orderby='<random>')
        # filter by category
        taglist = self.categories['cat{}'.format(cat)]
        ps = ps.find(lambda row: [t for t in row.tags
                                  if taglist and (t in taglist)])
        # filter out paths with a step that's not set to "active"
        ps = ps.find(lambda row: [s for s in row.steps
                                  if db.steps[s].status != 2])
        # avoid steps with right tag but no location
        ps.exclude(lambda row: db.steps[row.steps[0]].locations is None)

        # TODO: exclude paths whose steps have tags beyond user's active tags
        #if len(p_list) > 0:
            #maxp = db.tag_progress[auth.user_id].latest_new
            #p_list.exclude(lambda row:
                #[t for t in row.tags if db.tags[t].position > maxp])

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
        """
        loc_id = self.loc_id
        db = self.db

        # catpaths is already filtered by category
        p_new = cpaths.find(lambda row: row.id not in self.completed)
        p_here = cpaths.find(lambda p: loc_id in db.steps[p.steps[0]].locations)
        # TODO: or do I need db.steps[row.steps[0]].locations
        p_here_new = p_here.find(lambda p: p in p_new)

        path = None
        new_loc = None
        if p_here_new:
            path = p_here_new[randrange(0, len(p_here_new))]
        elif p_new:
            path = p_new[randrange(0, len(p_new))]
            new_locs = db.steps(path.steps[0]).locations
            # TODO: do we need db.steps[p_elsewhere.steps[0].locations
            new_loc = new_locs[randrange(0, len(new_locs))]
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
        """
        if not db:
            db = self.db
        # loc_id = self.loc_id
        cat_list = self._order_cats()

        # cycle through categories, starting with the one from _get_category()
        for cat in cat_list:
            catpaths = self._paths_by_category(cat)
            if catpaths[0]:
                return self._choose_from_cat(catpaths[0], catpaths[1])
            else:
                pass

        return None


class User(object):
    """
    An object representing the current user, including his/her performance
    data and the paths completed and active in this session.

    """

    def __init__(self, userdata, localias, tag_records, tag_progress, db=None):
        """
        Initialize a paideia.User object.

        ## Argument types and structures
        - userdata: {'name': str, 'id': int, '}
        - localias: str
        - tag_progress: rows.as_dict()
        - tag_records: rows.as_dict
        """
        if not db:
            db = current.db
        self.db = db
        self.tag_progress = tag_progress
        self.tag_records = tag_records
        self.rank = tag_progress['latest_new']
        self.name = userdata['first_name']
        self.user_id = userdata['id']
        self.path = None
        self.completed_paths = []
        self.cats_counter = 0
        self.old_categories = None
        self.categories = self._get_categories()
        self.new_badges = None
        self.blocks = []
        self.inventory = []
        self.session_start = datetime.datetime.utcnow()
        self.last_npc = None
        self.last_loc = None
        self.localias = localias
        self.loc_id = db(db.locations.alias == localias).select().first().id
        self.loc = Location(self.loc_id, db)
        self.redirect_loc = None

    def get_id(self):
        """Return the id (from db.auth_user) of the current user."""
        return self.user_id

    def is_stale(self):
        now = datetime.datetime.utcnow()
        start = self.session_start
        if now - start >= datetime.timedelta(days=1):
            return True
        else:
            return False

    def get_new_badges(self):
        """Return a dictionary of tag ids newly introduced or promoted"""
        return self.new_badges

    def get_path(self, loc, db=None):
        """
        Return the currently active Path object.

        Neither argument is strictly necessary, but localias will usually be
        provided. The db argument is only used for dependency injection during
        testing.
        """
        if not db:
            db = current.db
        # If the user has a multi-step path in progress, use that path
        if self.path:
            self.loc = loc
            self.path._set_loc(loc)
            return self.path
        # otherwise, select a new path
        else:
            self.loc = loc
            choice = PathChooser(self.categories, loc.get_id(),
                                 self.completed_paths, db=self.db).choose()
            path = Path(path_id=choice[0].id, loc=loc)

            # check for a redirect location to start the selected path
            if choice[1]:
                # TODO: get block logic working here
                self._set_block('redirect', choice[1])

            self.path = path
            return path

    def _get_categories(self, rank=None, categories=None, old_categories=None,
                        tag_records=None):
        """
        Return a categorized dictionary with four lists of tag id's.

        This method is important primarily to decide whether a new
        categorization is necessary before instantiating a Categorizer object
        # do we need to create new categorizer object each time?
        """
        if not rank:
            rank = self.rank
        if not tag_records:
            tag_records = self.tag_records
        cats_counter = self.cats_counter
        #old_categories = self.old_categories
        # only re-categorize every 10th evaluated step
        if cats_counter in range(1, 10):
            self.cats_counter = cats_counter + 1
            return self.categories
        else:
            try:
                self.old_categories = self.categories
            except AttributeError:
                self.old_categories = None
            c = Categorizer(rank, categories, tag_records)
            cat_result = c.categorize_tags()
            categories = cat_result['categories']
            self.categories = categories
            self.cats_counter = cats_counter + 1
            if cat_result['new_tags']:
                self.set_block('new_tags', cat_result['new_tags'])
            return categories

    def _get_blocks(self):
        """docstring"""
        return self.blocks

    def _set_block(self, condition, kwargs=None, data=None):
        """docstring for _set_block"""
        try:
            self.blocks.append(Block(condition=condition,
                                    kwargs=kwargs,
                                    data=data))
            return True
        except Exception:
            return False

    def _complete_path(self):
        """docstring"""
        self.completed_paths.append(self.path.get_id())
        self.last_npc = self.path.get_active_step().get_npc()['id']
        self.last_loc = self.path.get_active_step().get_npc()['id']
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
        if not db:
            db = current.db
        self.db = db

    def categorize_tags(self, rank=None, tag_records=None,
                        old_categories=None, db=None):
        """Return a categorized dictionary of tags"""
        if not rank:
            rank = self.rank
        if not old_categories:
            old_categories = self.old_categories
        if not tag_records:
            tag_records = self.tag_records
        if not db:
            db = current.db
        new_tags = None

        # if user has not tried any tags yet, start first set
        if len(tag_records) == 0:
            categories = {}
            categories['cat1'] = self._introduce_tags()
            return {'tag_progress': None,
                    'new_tags': None,
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
                            and (db.tags[t].position <= rank)]
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
        last_right based on the average of those three attempt dates.
        """
        db = self.db
        for rec in tag_records:
            # add new secondary_right attempts from attempt_log
            # (TODO: this is temporary)
            db_recs = db(
                        (db.attempt_log.name == rec['name']) &
                        (db.attempt_log.score == 1.0) &
                        (db.attempt_log.dt_attempted >= rec['last_right']) &
                        (db.attempt_log.step == db.steps.id) &
                        (db.steps.tags_secondary.contains(rec['tag_id']))
            ).select(db.attempt_log.dt_attempted).as_list()

            if db_recs:
                dates = [t for v in db_recs for t in v.iteritems()]
                try:
                    rec['secondary_right'].append(dates)
                except AttributeError:
                    rec['secondary_right'] = dates

            if rec['secondary_right'] and len(rec['secondary_right']) >= 3:
                rindex = tag_records.index(rec)
                rlen = len(rec['secondary_right'])
                # increment times_right by 1 per 3 secondary_right
                rnum = rlen / 3
                rmod = rlen % 3
                rec['times_right'] += rnum
                # move last_right forward based on mean of last 3 secondary_right
                now = self.utcnow
                if rlen > 3:
                    last3 = rec['secondary_right'][-(rmod + 3): -(rmod)]
                else:
                    last3 = rec['secondary_right'][:]
                last3_deltas = [now - s for s in last3]
                avg_delta = sum(last3_deltas, datetime.timedelta(0)) / 3
                avg_date = now - avg_delta
                if avg_date > rec['last_right']:
                    rec['last_right'] = avg_date

                # remove counted entries from secondary_right, leave remainder
                if rlen > 3:
                    rec['secondary_right'] = rec['secondary_right'][-(rmod):]
                else:
                    rec['secondary_right'] = []
                tag_records[rindex] = rec
            else:
                continue

        return tag_records

    def _core_algorithm(self, tag_records=None):
        """
        Return dict of the user's active tags categorized by past performance.

        The tag_records argument should be a list of dictionaries, each of
        which includes the following keys and value types:
            {'tag_id': <int>,
             'last_right': <datetime>,
             'last_wrong': <datetime>,
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
            right_dur = utcnow - record['last_right']
            right_wrong_dur = record['last_right'] - record['last_wrong']

            # spaced repetition algorithm for promotion to
            # ======================================================
            # category 2
            if ((right_dur < right_wrong_dur)
                    # don't allow promotion from cat1 within 1 day
                    and (right_wrong_dur > datetime.timedelta(days=1))
                    # require at least 10 right answers
                    and (record['times_right'] >= 10)) \
                or ((record['times_right'] >= 10)
                    # require ratio of at least 5 right to 1 wrong
                    and ((record['times_wrong'] / record['times_right'])
                         <= 0.2)
                    # require that tag has right answer within last 2 days
                    and (right_dur <= datetime.timedelta(days=14))): \
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

            categories[category].append(record['tag_id'])

        return categories

    def _introduce_tags(self, rank=None, db=None):
        """
        Add the next set of tags to cat1 in the user's tag_progress

        Returns a dictionary of categories identical to that returned by
        categorize_tags
        """
        if not db:
            db = current.db
        if not rank:
            rank = self.rank

        if rank in (None, 0):
            rank == 1
        else:
            rank += 1
        self.rank = rank

        newtags = [t['id'] for t in db(db.tags.position == rank).select()]

        return newtags

    def _add_untried_tags(self, categories, rank=None, db=None):
        """Return the categorized list with any untried tags added to cat1"""
        if not rank:
            rank = self.rank
        if not db:
            db = current.db

        left_out = []
        for r in range(1, rank + 1):
            newtags = [t.id for t in db(db.tags.position == r).select()]
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
                            print type(Exception), Exception
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
    """An object representing an interruption in the flow of the game."""

    def __init__(self):
        """Initialize a new Block object"""
        self.step = None
        self.condition = None
        self.data = None
        self.db = current.db

    def set_block(self, condition, kwargs={}, data=None):
        """Create correct Step subclass and store as an instance variable."""
        step_type = {'redirect': StepRedirect,
                     'award badges': StepAwardBadges,
                     'view slides': StepViewSlides,
                     'quota reached': StepQuotaReached}
        self.condition = condition
        if kwargs:
            kwargs['db'] = self.db
        else:
            kwargs = {'db': self.db}
        self.step = step_type[condition](**kwargs)
        return True

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
