#! /usr/bin/python
# -*- coding: UTF-8 -*-
# Unit tests for the paideia module
#
# Configuration and some fixtures (client, web2py) declared in
# the file tests/conftest.py

import pytest


class TestExploring(object):
    ''' Unit testing class for the exploring.py controller. '''

    def test_exploring_index(self, client, db):
        '''
        Unit test for the index() function of the exploring.py controller.
        '''
        assert db
        client.get('/exploring/index')
        print client.status
        assert 2

    def test_exploring_step(self):
        '''
        Unit test for the step() function of the exploring.py controller.
        '''
        pass

    def test_exploring_map(self):
        '''
        Unit test for the map() function of the exploring.py controller.
        '''
        pass
