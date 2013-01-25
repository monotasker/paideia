# -*- coding: utf-8 -*-
from gluon import current
from gluon import IMG, URL, INPUT, FORM, SQLFORM, SPAN, DIV, UL, LI, A, Field
from gluon import IS_NOT_EMPTY
from random import randint
import re


class Stance(object):
    '''Stores the current state of the game session.'''

    def __init__(self):
        """Initialize a Stance object."""
        self.path = None
        self.user = None

    def get_path(self):
        pass

    def get_user(self):
        if self.user:
            return self.user
        else:
            pass

class Walk(object):

    def __init__(self, loc_alias):
        """docstring for __init__"""
        self.user = User(loc_alias)
        self.response_string = response_string

    def ask(self):
        """docstring for __ask__"""

        p = self.user.get_path()
        s = p.get_next_step()
        prompt = s.get_prompt()
        responder = s.get_responder()
        self.store_user()

        return {'prompt': prompt, 'responder': responder}

    def reply(self, response_string):
        """docstring for __reply__"""

        p = self.user.get_path()
        s = p.get_current_step()
        reply = s.get_reply(response_string)
        record_id = self._record_step()
        bug_reporter = BugReporter(record_id)
        p.complete_step()

        if p.check_for_end() is True:
            self.user._complete_path()

        self._store_user()

        return {'reply': reply, 'bug_reporter': bug_reporter}

    def _record_step(self):
        pass

    def _complete_path(self):
        pass


class PathChooser(object):
    pass


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
        image_id = self.data.npc_image
        self.image = db.images[image_id].image

    def get_id(self):
        """return the database row id of the current npc"""
        return self.id_num

    def get_name(self):
        """return the name of the current npc"""
        return self.data.name

    def get_image(self):
        """
        Return a web2py IMG helper object with the image for the current
        npc character.
        """
        url = URL('static/images', self.db.images[self.data.npc_image].image)
        img = IMG(_src=url)
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
        pass

    def choose(self):
        """
        Choose an npc for the selected step.
        If possible, continue with the same npc. Otherwise, select a different
        one that can engage in the selected step.
        """
        available = step.get_npcs()
        # TODO: step.get_npcs returns ids or Npc objects?

        if ((location.get_readable() == prev_loc.get_readable()) and
            (prev_npc.get_id() in available)):
            return prev_npc
        else:
            available2 = [n for n in available
                            if n.get_id() == prev_npc.get_id()
                            and location.get_id() in n.get_locations()]
            if len(available2) > 1:
                return available2[randint(0,len(available2) - 1)]
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


class Step(object):
    '''
    This class represents one step (a single question and response
    interaction) in the game.
    '''

    def __init__(self, step_id, loc, prev_loc, prev_npc_id,
                    next_step_id=None,
                    path=None,
                    db=None):
        """docstring for __init__"""
        if db is None:
            db == current.db
        self.db = db
        self.data = db.steps[step_id]
        self.repeating = False # set to true if step already done today
        self.loc = loc
        self.prev_loc = prev_loc
        self.prev_npc_id = prev_npc_id
        self.npc = None
        self.path = path
        self.next_step_id = next_step_id

    def get_id(self):
        """
        Return the id of the current step as an integer.
        """
        return self.data.id

    def get_path(self):
        """
        Return the id of the current path as an integer.
        """
        # TODO: This feels like it's reversing the execution flow in an awkward
        # way. It's only needed for StepRecorder.record(). So should that method
        # be called by the path instead?
        return self.path

    def get_tags(self):
        """
        Return a list of tag id's
        """
        primary = self.data.tags
        secondary = self.data.tags_secondary
        return {'primary': primary, 'secondary': secondary}

    def get_prompt(self, username=None):
        """
        Return the prompt information for the step. In the Step base class
        this is a simple string. Before returning, though, any necessary
        replacements or randomizations are made.
        """
        self._check_location()
        raw_prompt = self.data.prompt
        prompt = self._make_replacements(raw_prompt, username)
        # prompt no longer tagged or converted to markmin here, but in view

        instructions = self._get_instructions()

        npc = self.get_npc() # duplicate choice prevented in get_npc()
        npc_image = self.npc.get_image()

        return {'prompt': prompt,
                'instructions': instructions,
                'npc_image': npc_image}

    def _make_replacements(self, raw_string, username=None, reps=None):
        """
        Return the provided string with tokens replaced by personalized
        information for the current user.
        """
        if username is None:
            auth = current.auth
            uname = auth.user['first_name']

        if reps is None:
            reps = {}
        reps['[[user]]'] = username

        new_string = raw_string
        for k, v in reps.iteritems():
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
        """Return an Npc object representing an appropriate npc for this step"""
        if self.npc: # ensure choice is made only once for each step
            return self.npc
        else:
            npcs_for_step = self.data.npcs
            npc_list = [n for n in npcs_for_step
                        if self.loc.get_id() in self.db.npcs[n].location]
            if self.prev_npc_id in npc_list:
                self.npc = Npc(self.prev_npc_id)
                return self.npc
            else:
                pick = npc_list[randint(0,len(npc_list) - 1)]
                self.npc = Npc(pick)
                return self.npc

    def _get_instructions(self):
        """
        Return an html list containing the instructions for the current
        step. Value is returned as a web2py UL() object.
        """
        instructions = self.data.instructions
        if instructions is None or instructions == []:
            return None
        else:
            list = UL(_class='step_instructions')
            for item in instructions:
                item_row = self.db.step_instructions[item]
                item_text = item_row.text
                list.append(LI(item_text))

            return list

    def _check_location(self):
        """docstring for get_locations"""
        # TODO: no code
        pass


class StepRedirect(Step):
    '''
    A subclass of Step. Handles the user interaction when the user needs to be
    sent to another location.
    '''

    def _make_replacements(self, prompt_string, username=None,
                                                    db=None, next_step=None):
        """
        Return the string for the step prompt with context-based information
        substituted for tokens framed by [[]].
        """
        session = current.session
        if db is None:
            db = current.db

        next_loc = 'somewhere else in town' # generic default
        # if mid-way through a path, send to next viable location
        # TODO: find a way to set this value to another location with an
        # available path if the current step is the last in its path.
        if self.next_step_id:
            next_locids = db.steps[self.next_step_id].locations
            # find a location that actually has a readable name
            raw_locs = [db.locations[n].readable for n in next_locids]
            next_locs = [n for n in raw_locs if not n is None]
        elif next_step:
            next_locids = db.steps[next_step].locations
            # find a location that actually has a readable name
            raw_locs = [db.locations[n].readable for n in next_locids]
            next_locs = [n for n in raw_locs if not n is None]
        else:
            pass

        reps = {'[[next_loc]]': next_loc}
        new_string = super(StepRedirect, self)._make_replacements(prompt_string,
                                                            reps=reps,
                                                            username=username)

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
        form = SQLFORM.factory(
                    Field('response', 'string',
                            requires=IS_NOT_EMPTY()),
                            _autocomplete='off'
                )
        return form

    def get_reply(self, user_response=None):
        """docstring for get_reply"""
        if user_response == None:
            request = current.request
            user_response = request.vars['response']

        readable = self._get_readable()

        result = StepEvaluator(response)
        reply_text = result['reply']
        tips = result['tips']
        score = result['score']
        tr = result['times_right']
        tw = result['times_wrong']
        ur = result['user_response']
        tags = self.get_tags()
        sid = self.get_id()
        pid = self.get_path()
        # the following class/method both records the user's performance
        # on this step instance AND returns the BugReporter object
        bug_reporter = StepRecorder().record(sid, tags, score, tr, tw, ur)

        return {'response': user_response,
                'reply_text': reply_text,
                'bug_reporter': bug_reporter,
                'tips':tips,
                'readable_short': readable['readable_short'],
                'readable_long': readable['readable_long']}

    def _get_readable(step_data=None):
        """
        Return two strings containing the shorter and the longer forms of the
        readable correct answer samples for this step.
        """
        if step_data is None:
            step_data = self.step_data

        readable = self.step_data.readable_response
        if '|' in readable:
            i = len(readable)
            if i > 1: i = 2
            readable_short = readable.split('|')[:(i + 1)]
            readable_short = [unicode(r, 'utf-8') for r in readable_short]
            readable_long = readable.split('|')
            readable_long = [unicode(r, 'utf-8') for r in readable_long]
        else:
            readable_short = [readable]
            readable_long = None

        return {'readable_short': readable_short,
                'readable_long': readable_long}


class StepMultipleChoice(Step):
    """
    A subclass of Step that adds a form to receive multiple-choice user input
    and evaluation of that input.
    """
    pass


class StepEvaluator(object):
    '''
    This class evaluates the user's response to a single step interaction and
    handles the data that results.
    '''

    def __init__(self, answers, tips):
        """Initializes a StepEvaluator object"""
        self.answers = answers
        self.tips = tips

    def get_eval(self, user_response=None):
        """
        Return the user's score for this step attempt along with "tips" text
        to be displayed to the user in case of a wrong answer.
        """
        if user_response == None:
            request = current.request
            user_response = request.vars['response']
        user_response = user_response.strip()
        answers = self.answers

        # Compare the student's response to the regular expressions
        try:
            if re.match(answers[0], user_response, re.I):
                score = 1
                reply = "Right. Κάλον."
            elif len(answers) > 1 and re.match(answers[1], user_response, re.I):
                score = 0.5
                #TODO: Get this score value from the db instead of hard
                #coding it here.
                reply = "Οὐ κάκον. You're close."
                #TODO: Vary the replies
            elif len(answers) > 2 and re.match(answers[2], user_response, re.I):
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
            else:
                times_wrong = 0

        # Handle errors if the student's response cannot be evaluated
        except re.error:
            redirect(URL('index', args=['error', 'regex']))
            reply = 'Oops! I seem to have encountered an error in this step.'
            readable_short = None
            readable_long = None

        tips = self.tips # TODO: customize tips for specific errors

        return {'score': score,
                'times_wrong': times_wrong,
                'reply': reply,
                'user_response': user_response,
                'tips': tips}


class StepRecorder(object):
    """
    Record the user's performance on this step and return a BugReporter object
    containing information about the transaction required to reverse the
    transaction later if necessary.
    """

    def __init__(self):
        pass

    def _record(self, step_id, path_id, tags, score, tr, tw, user_response, db=None):
        """
        Record user performance data resulting from the current step
        evaluation. This method also returns some data so that the calling
        function can ensure that the recorded result is accurate.
        """
        score = self.score
        record_id = 0
        #TODO: unfinished
        return {'score':score,
                'record_id':record_id}


class Path(object):
    def __init__(self):
        """docstring for __init__"""
        self.completed_steps = []
        self.next_step_id = None

    def get_next_step(self, db=None):
        """docstring for get_next_step"""
        pass

class PathChooser(object):
    def __init__(self):
        """docstring for __init__"""
        pass

class User(object):
    def __init__(self, userdata=None):
        """docstring for __init__"""
        if userdata is None:
            userdata = current.Auth.user
        self.userdata = userdata
        self.path = None
        self.completed_paths = None
        self.categories = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        self.old_categories = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        self.new_badges = None
        self.blocks = None

    def get_id(self):
        """docstring"""
        pass

    def get_categories(self):
        """docstring for fname"""
        pass

    def get_new_badges(self):
        """docstring for fname"""
        pass

    def get_firstname(self):
        """docstring"""
        pass

    def get_path(self):
        """docstring"""
        pass

    def get_categories(self):
        """docstring"""
        pass

    def get_old_categories(self):
        """docstring"""
        pass

    def get_blocks(self):
        """docstring"""
        pass

class Categorizer(object):
    pass

class Block(object):
    """docstring"""
    pass


