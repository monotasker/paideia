# Unit tests for the paideia module

import unittest
from paideia import Stance

class StanceTest(unittest.TestCase):
    def setUp(self):
        self.stance = Stance()

    def get_start_time_test(self):
        time = self.stance.get_start_time()

    def tearDown(self):
        pass

if __name__ == "main":
    unittest.main()
