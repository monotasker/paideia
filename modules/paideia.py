from gluon import current


class Stance(object):
    '''Stores the current state of the game session.'''

    def __init__(self, user_id, state=current):
        self.user == User(user_id)

class User(object):
    '''Represents a user record from the db'''
    def __init__(self):
        pass

class Npc(object):
    '''
    Stores and provides information about one non-player character in the
    game
    '''

    def __init__(self, id_num, state=current):
        """
        initialize an npc object with database data for the character
        with the provided id
        """
        db = current.db
        self.data = db.npcs(id_num)
        self.id = id

    def get_id(self):
        """return the database row id of the current npc"""
        return self.id

    def get_name(self):
        """return the name of the current npc"""

        return self.data

    def get_image(self):
        """docstring for get_image"""
        pass

    def get_locations(self):
        """docstring for get_locations"""
        pass
