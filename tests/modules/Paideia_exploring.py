
#!/usr/bin/python
#found when running python2.7 web2py.py -S paideia -M -R testRunner.py

import unittest
import cPickle as pickle
from gluon import * 
from gluon.contrib.test_helpers import form_postvars
from gluon import current

class Paideia_exploringModule(unittest.TestCase):

    def __init__(self, p):

        global auth, session, request
        unittest.TestCase.__init__(self, p)
        self.session = pickle.dumps(current.session)
        current.request.application = 'welcome'
        current.request.controller = 'default'
        self.request = pickle.dumps(current.request)

	def setUp(self):
		
        global response, session, request, auth
        current.session = pickle.loads(self.session)
        current.request = pickle.loads(self.request)
        auth = Auth(globals(), db)
        auth.define_tables()

	def testIndex(self):
		#form_postvars()
		self.assertEquals(2,3)
		self.assertEquals(2,2)
