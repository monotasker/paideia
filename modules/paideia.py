from gluon import current


class Stance(object):
    '''Stores the current state of the game session.'''

    def __init__(self):
        """docstring for __init__"""
        pass

class Npc(object):
    '''
    Stores and provides information about one non-player character in the
    game
    '''

    def __init__(self, id_num, db=None):
        """
        initialize an npc object with database data for the character
        with the provided id
        """
        if db is None:
            db = current.db
        self.id_num = id_num
        self.data = db.npcs[id_num]

    def get_id(self):
        """return the database row id of the current npc"""
        return self.id_num

    def get_name(self):
        """return the name of the current npc"""
        return self.data.name

    def get_image(self):
        """docstring for get_image"""
        return self.data.npc_image

    def get_locations(self):
        """docstring for get_locations"""
        return self.data.location

    def get_notes(self):
        """docstring for get_locations"""
        return self.data.notes

    def choose(self, step, location, prev_npc):
        """choose a new npc for the step that has been selected"""
        pass
