# Unit tests for the paideia module

import sys
import pytest

sys.path.append('/home/ian/web/web2py/applications/paideia/modules')
sys.path.append('/home/ian/web/web2py')

from paideia import Npc
from gluon import *
from gluon.storage import Storage
from gluon.shell import exec_environment

#db = exec_environment('applications/paideia/models/paideia.py')

#db = DAL('sqlite://storage.sqlite')

db = Storage({'npcs': Storage({
            1: Storage({'id': 1, 'name': 'Alexander'}),
            2: Storage({'id': 2, 'name': 'Maria'}),
        })
})

@pytest.fixture
def mynpc():
    '''
    A pytest fixture providing a paideia.Npc object for testing.
    '''
    return Npc(1, db)

class TestNpc():
    '''
    Tests covering the Npc class of the paideia module.
    '''
    def test_npc_get_name(self, mynpc):
        """Test for method Npc.get_name()"""
        assert mynpc.get_name() == 'Alexander'

    def test_npc_get_id(self, mynpc):
        """Test for method Npc.get_id()"""
        assert mynpc.get_id() == 1

    def test_npc_get_image(self, mynpc):
        """Test for method Npc.get_image()"""
        pass

    def test_npc_get_locations(self, mynpc)
        """Test for method Npc.get_locations()"""
        pass

class TestStance():
    pass

#class StanceTest(unittest.TestCase):
    #def setUp(self):
        #self.stance = Stance()

    #def get_start_time_test(self):
        #time = self.stance.get_start_time()

    #def tearDown(self):
        #pass

#if __name__ == "main":
    #unittest.main()
