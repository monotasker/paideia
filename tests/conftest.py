#!/usr/bin/env python

'''
py.test configuration and fixtures file.

This file is lightly adapted from the one by viniciusban;
Part of the web2py.test model app (https://github.com/viniciusban/web2py.test)

This file
- Tells application it's running in a test environment.
- Creates a complete web2py environment, similar to web2py shell.
- Creates a WebClient instance to browse your application, similar to a real
web browser.
- Propagates some application data to test cases via fixtures, like baseurl and
automatic appname discovery.

To run tests:
$ cd web2py (you must be in web2py root directory to run tests)
$ python web2py.py -a my_password --nogui &
$ py.test -x -v -s applications/my_app_name/tests
'''

import os
import pytest
import sys

sys.path.insert(0, '')


@pytest.fixture(scope='module')
def baseurl(appname):
    '''The base url to call your application.

    Change you port number as necessary.
    '''

    return 'http://localhost:8000/%s' % appname


@pytest.fixture(scope='module')
def appname():
    '''Discover application name.

    Your test scripts must be on applications/<your_app>/tests
    '''

    dirs = os.path.split(__file__)[0]
    appname = dirs.split(os.path.sep)[-2]
    return appname


@pytest.fixture(scope='module', autouse=True)
def fixture_create_testfile_for_application(request, appname):
    '''Creates a temp file to tell application she's running under a
    test environment.

    Usually you will want to create your database in memory to speed up
    your tests and not change your development database.

    This fixture is automatically run by py.test at module level. So, there's
    no overhad to test performance.
    '''

    # note: if you use Ubuntu, you can allocate your test database on ramdisk
    # simply using the /dev/shm directory.
    temp_dir = '/dev/shm/' + appname
    #temp_dir = '/tmp'

    # TODO: why import os and shutil below here and not at top?
    import os
    os.mkdir(temp_dir)

    # IMPORTANT: the temp_filename variable must have the same value as set in
    # your app/models/db.py file.
    temp_filename = '%s/tests_%s.tmp' % (temp_dir, appname)

    with open(temp_filename, 'w+') as tempfile:
        tempfile.write('application %s running in test mode' % appname)

    def _remove_temp_file_after_tests():
        import shutil
        shutil.rmtree(temp_dir)
        #os.remove(temp_filename)
    request.addfinalizer(_remove_temp_file_after_tests)


@pytest.fixture(autouse=True)
def fixture_cleanup_db(web2py):
    '''Truncate all database tables before every single test case.

    This can really slow down your tests. So, keep your test data small and try
    to allocate your database in memory.

    Automatically called by test.py due to decorator.
    '''

    web2py.db.rollback()
    for tab in web2py.db.tables:
        web2py.db[tab].truncate()
    web2py.db.commit()


@pytest.fixture(scope='module')
def client(baseurl, fixture_create_testfile_to_application):
    '''Create a new WebClient instance once per module.
    '''

    # TODO: why import here?
    from gluon.contrib.webclient import WebClient
    webclient = WebClient(baseurl)
    return webclient


@pytest.fixture()
def web2py(appname, fixture_create_testfile_for_application):
    '''Create a Web2py environment similar to that achieved by
    Web2py shell.

    It allows you to use global Web2py objects like db, request, response,
    session, etc.

    Concerning tests, it is usually used to check if your database is an
    expected state, avoiding creating controllers and functions to help
    tests.
    '''

    from gluon.shell import env
    from gluon.storage import Storage

    web2py_env = env(appname, import_models=True,
                     extra_request=dict(is_local=True))

    # Uncomment next 2 lines to allow using global Web2py objects directly
    # in your test scripts.
    # del web2py_env['__file__']  # avoid py.test import error
    # globals().update(web2py_env)

    return Storage(web2py_env)
