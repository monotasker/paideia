from gluon import current
from gluon import IMG, URL
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

    def choose(self, step, location, prev_npc, prev_loc):
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

class BugReporter(object):
    pass

class Step(object):
    def __init__(self, step_id, db=None):
        """docstring for __init__"""
        if db is None:
            db == current.db
        self.db = db
        self.data = db.steps[step_id]
        self.prompt = self.data.prompt
        self.locations = self.data.location
        self.npcs = self.data.npcs
        self.reply = None
        self.response = None
        self.score = None
        self.repeating = False
        self.instructions = self.data.instructions
        self.tips = self.data.tips
        self.record_id

    def get_prompt(self):
        """docstring for get_prompt"""
        return self.prompt

    def get_reply(self, response):
        """docstring for get_reply"""
        self.response = response
        # TODO: unfinished
        pass

    def get_npcs(self):
        """docstring for get_npcs"""
        pass

    def get_locations(self):
        """docstring for get_locations"""
        pass

    def get_instructions(self):
        """docstring for get_instructions"""
        pass

    def _eval_response(self):
        """docstring for eval_response"""
        # TODO: unfinished
        pass

    def _make_replacements(self):
        """docstring for eval_response"""
        # TODO: unfinished
        pass


class StepEvaluator(object):

    def __init__(self, step):
        """docstring for __init__"""
        pass

    def get_eval(self):
        """docstring for get_eval"""
        tips = self.get_tips()
        self.score = ???
        self._record()
        bug_reporter = BugReporter(record_id)
        return {'bug_reporter'=bug_reporter,
                'tips'=tips}

    def get_tips(self):
        """docstring for get_tips"""
        pass

    def _record(self):
        """docstring for _record"""
        pass



class Path(object):
    pass


class User(object):
    pass


class Block(object):
    pass
