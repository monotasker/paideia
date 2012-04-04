
#!/usr/bin/python
"""
run test from the command line:
python web2py.py -S api -M -R applications/api/tests/test.py
where "api" = my app name
"""

import unittest

from gluon.globals import Request
# so that we can reset the Request object for each test
from gluon.contrib.test_helpers import form_postvars

execfile("applications/paideia/controllers/exploring.py", globals())
#executes the controller in the prepared web2py environment, 
#bringing all of the function declarations into the local 
#namespace. Passing globals() to the execfile() command lets
#your controllers see your database. 

#run code here to restore the standard database state
#any db interactions in a test must be followed by db.commit() 

class Paideia_exploringModule(unittest.TestCase):
	def setUp(self):
		"""establish conditions for desired test environment"""

		request = Request() #use a clean Request object
		session = Session() #use a clean Session object
