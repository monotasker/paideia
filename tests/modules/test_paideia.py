# Unit tests for the paideia module

import pytest
from gluon import *
from paideia import *

class TestNpc():

    @pytest.fixture
    def npc(id=1):
        return Npc(id)

    def test_npc_get_name(self, npc):
        """docstring for test_npc_get_name"""
        assert npc.get_name == 'Alexander'

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
