from gluon import current
from gluon import IMG, URL, INPUT, FORM, SPAN, DIV
from random import randint


class Stance(object):
    '''Stores the current state of the game session.'''

    def __init__(self):
        """Initialize a Stance object."""
        pass


class Walk(object):
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
    Choose an npc to engage the user in the current step, based on the current location and
    the parameters of the step itself.
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
        available = step.get_npcs() # TODO: step.get_npcs returns ids or Npc objects?
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


class BugReporter(object, step_id, user_response, record_id):
    """
    Class representing a bug-reporting widget to be presented along with the evaluation
    of the current step.
    """
    pass


class Step(object):
    '''
    This class represents one step (a single question and response interaction) in the game.
    '''

    def __init__(self, step_id, db=None):
        """docstring for __init__"""
        if db is None:
            db == current.db
        self.db = db
        self.data = db.steps[step_id]
        self.raw_prompt = self.data.prompt
        self.locations = self.data.location
        self.npcs = self.data.npcs
        self.reply = None
        self.response = None
        self.score = None
        self.repeating = False
        self.instructions = self.data.instructions
        self.tips = self.data.tips
        self.record_id

    def get_prompt(self, raw_prompt=None):
        """
        Return the prompt information for the step. In the Step base class this is a simple
        string. Before returning, though, any necessary replacements or randomizations
        are made.
        """
        if raw_prompt == None:
            raw_prompt = self.prompt
        prompt = self._make_replacements(raw_prompt)
        return {'prompt':prompt}

    def get_responder(self):
        """
        Return the html form to allow the user to respond to the prompt for this step.
        """

    def get_reply(self, user_response=None):
        """docstring for get_reply"""
        response = current.response
        if user_response == None:
            user_response = response.vars['response']
        bug_reporter = BugReporter(record_id)
        eval = StepEvaluator(response)
        reply_text = eval['reply']
        tips = eval['tips']


        # TODO: unfinished
        return {'response': user_response,
                'reply_text': reply_text,
                'bug_reporter': bug_reporter,
                'tips':tips}


    def get_npcs(self):
        """docstring for get_npcs"""
        pass

    def get_locations(self):
        """docstring for get_locations"""
        pass

    def get_instructions(self):
        """docstring for get_instructions"""
        pass

    def _make_replacements(self, raw_prompt=None):
        """docstring for eval_response"""
        if raw_prompt == None:
            raw_prompt == self.raw_prompt
        pass


class StepEvaluator(object):
    '''
    This class evaluates the user's response to a single step interaction and handles the
    data that results.
    '''

    def __init__(self, step_data, db=None):
        """Initializes a StepEvaluator object"""
        if db == None:
            db = current.db
        self.score = None
        self.step_data = step_data

    def get_eval(self, user_response=None):
        """
        The main public method that returns the evaluation result and triggers the
        handling of user-performance data. This method also returns the "tips" text
        to be displayed to the user in case of a wrong answer and the db id of the
        transaction that recorded the user performance data. This latter allows for
        reversing the transaction later.
        """
        if user_response == None:
            user_response =
        result = self._eval(user_response)
        score = result['score']
        tips = result['tips'] # get from _eval to allow for varying based on kind of error

        record = self._record(score)
        if record['score'] == score:
            pass
        else:
            pass # TODO: raise an error here



        return {'tips':tips,
                'record_id':record['record_id']}

    def _eval(self, response=None):
        """
        Evaluate the user response against the step's regular expression(s)
        """
        score == 0 # TODO: add actual business logic

        tips = self.step_data.tips  # TODO: customize tips for specific errors

        return {'score': score,
                'tips': tips}

    def _record(self):
        """
        Record user performance data resulting from the current step evaluation.
        This method also returns some data so that the calling function can ensure
        that the recorded result is accurate.
        """
        score = self.score
        record_id = 0
        #TODO: unfinished
        return {'score':score,
                'record_id':record_id}



class Path(object):
    pass


class User(object):
    pass


class Block(object):
    pass
