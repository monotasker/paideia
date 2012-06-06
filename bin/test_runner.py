#!/usr/bin/python
"""
Copy or symlink this fileto web2py's bin directory before running.

Execute with:
>   python web2py.py -S app_name -M -R test_runner.py to run the doctests and unittests
>   python web2py.py -S app_name    -R test_runner.py to run the userinterface tests

o With -M it runs all tests that exist in the tests directories of 'app_name'.
o Also runs all doctests
o Without -M parameter run the UI tests using Selenium

Unittests
=========

Inside the unittest file the class should have a name based on the
file's path, like this:

FilenameDirectory -> DefaultTasksModel

for example:
applications/[app_name]/tests/controllers/default.py
is
class DefaultController(unittest.TestCase)

BEWARE that the name is NOT in plural (controllers->Controller)

depends on python modules unittest and selenium.

For documentation see slice 67 and 142 at http://www.web2pyslices.com

Original by
02/03/2009
Jon Vlachoyiannis
jon@emotionull.com

Changes and additions:
o app_name
o enable running on windows by using os.path
o moved db_test in from models
o added UI tests using Selenium

version 0.92
2012/05/07
Nico de Groot
ndegroot0@gmail.com
"""

from copy import copy
import doctest
import glob
import os
import sys
import traceback
import unittest
from uuid import uuid4

from gluon import current
from gluon.storage import Storage
from gluon.utils import web2py_uuid


DB_URI = 'sqlite:memory:'
DB_DIR = os.path.join(os.getcwd(), 'applications/paideia/databases')


def showfeedback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print '-'*60
    for line in traceback.format_exception(exc_type, exc_value,exc_traceback):
        print line[:-1]
    print '-'*60

def custom_execfile(test_file):
    if os.name == 'nt':
        errlist = (WindowsError,ValueError,SystemExit)
    else:
        errlist = (OSError,ValueError,SystemExit)

    try:
        file_dir = os.path.split(test_file)[0]
        if file_dir not in sys.path:
            sys.path.append(file_dir)   # to support imports from current folder in the testfiles
        # modules are applications/[app_name]/modules
        modules_path = os.path.join('applications', app_name, 'modules')
        if modules_path not in sys.path:
            sys.path.append(modules_path)       # to support imports from modules folder
        if 'site-packages' not in sys.path:
            sys.path.append('site-packages')    # support imports from web2py/site-packages
        g = copy(globals())
        execfile(test_file, g,)
    except errlist:
        pass # we know about the rotating logger error...
             # and SystemExit is not useful to detect
    except:
        showfeedback()
    return g

def copy_virtual_fields(db, test_db, table_name):
    '''
    Copy a table's virtual fields from the live database to the test database.

    The virtual fields for each table in the test database should all be empty
    so we just get whatever's in the live database.
    '''

    db_table = getattr(db, table_name)
    test_db_table = getattr(test_db, table_name)
    test_db_table.virtualfields.extend(db_table.virtualfields)

app_name= current.request.application

try:
    db
except NameError: w2p_models = False
else:
    w2p_models = True


# Create testing db, but only when necessary,
# maybe the app is already configured to use the testing db

if w2p_models:
    # Export the data from the live database
    # TODO: Put this in a seperate script sp that we don't have to do this
    # every time we run tests
    csv_file = os.path.join(
        'applications',
        app_name,
        'private/test_fixture.csv'
    )

    db.export_to_csv_file(open(csv_file, 'w'))

    if not db._uri == DB_URI:
        # create a test database by copying the original db
        print "Create testing db to replace current db..."

        test_db = DAL(DB_URI)
        if not test_db.tables:
            for table_name in db.tables:  # Copy tables
                table_copy = [copy(f) for f in db[table_name]]
                test_db.define_table(table_name, *table_copy)

                copy_virtual_fields(db, test_db, table_name)

            test_db.import_from_csv_file(open(csv_file, 'r'))

        db = test_db

        # Switch auth to the test db
        current.auth.db = db

    suite = unittest.TestSuite()

    # find unittests
    path = os.path.join('applications', app_name, 'tests', '*', '*.py')
    test_files = glob.glob(path)
    test_files = [x for x in test_files if not os.path.split(x)[0].endswith('userinterface')]

    print len(test_files), " unittest files found."

    ''' TODO: Are we going to use doctests?
    # find doctests in controller
    path = os.path.join('applications', app_name, 'controllers', '*.py')
    doc_test_files = glob.glob(path)
    print len(doc_test_files), " controller files with possible doctests found."

    if not test_files and not doc_test_files:
        print "No unittest and doctest test files found for application: " + app_name

    # Bring in all doc tests and submit them
    print "Adding doctests" if doc_test_files else "No doctests"
    for f in  doc_test_files:
        g = custom_execfile(f)
        suite.addTest(doctest.DocFileSuite(f, globs=g,module_relative=False))
    '''

    # Bring in all unit tests and their controllers/models/whatever
    print "Adding unittests" if test_files else "No unittests"

    for test_file in test_files:
        g = custom_execfile(test_file)
        # Create the appropriate class name based on filename and path
        components = os.path.split(test_file)
        filename = str.capitalize(components[-1][:-3]) # without .py
        directory = str.capitalize(os.path.split(components[-2])[-1])

        # Load the to-be-tested file
        to_be_tested_file = os.path.join("applications",
                                          app_name,
                                          directory.lower() ,
                                          filename.lower() + ".py")

        #send class name (attribute of g) to the suite
        suite.addTest(unittest.makeSuite(g[filename+directory[:-1]] )) # lose the s

    # lets get rolling (doc & unit)
    unittest.TextTestRunner(verbosity=2).run(suite)

''' TODO: Are we going to use selenium?
else: # no models, just the UI tests

    path = os.path.join('applications', app_name, 'tests', 'userinterface', 'case_*.py')
    selenium_test_files = glob.glob(path)
    print len(selenium_test_files), " userinterface testcases found."

    suite = unittest.TestSuite()

    # Bring in selenium tests and submit them to the suite
    print "Add external UI tests (Selenium)" if selenium_test_files else "No external UI tests"
    for test_file in  selenium_test_files:

        g = custom_execfile(test_file)
        # reconstruct the class name from filename
        components = os.path.split(test_file)
        filename = str.capitalize(components[-1][:-3]) # without .py
        classname = str.capitalize(filename.split("_")[1])

        #pass the classname to Suite
        suite.addTest(unittest.makeSuite(g[classname]))

    unittest.TextTestRunner(verbosity=2).run(suite)
    if os.getenv('WEB2PY_USE_DB_TESTING') == "TRUE":
        print "UI tests have used the Testing-Fixture database in the webapp %s" % app_name
        print "Reset environment variable WEB2PY_USE_DB_TESTING to switch to normal database"
'''

