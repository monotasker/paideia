#!/usr/bin/python
#found when running python web2py.py -S paideia -M -R testRunner.py

import unittest
from gluon.globals import Request, Session, Storage, Response
from gluon.contrib.test_helpers import form_postvars

class ExploringController(unittest.TestCase):
    def __init__(self, p):
        global auth, session, request
        unittest.TestCase.__init__(self, p)
        self.session = pickle.dumps(current.session)
        current.request.application = 'welcome'
        current.request.controller = 'default'
        self.request = pickle.dumps(current.request)

	def setUp(self):
		pass

	def testIndex(self):
		#form_postvars()
		self.assertEquals(2,3)
		self.assertEquals(2,2)
