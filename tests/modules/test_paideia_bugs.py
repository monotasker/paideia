#! /usr/bin/python
# -*- coding: UTF-8 -*-

"""
# Unit tests for the paideia_bugs module
#
# Configuration and some fixtures (client, web2py) declared in
# the file tests/conftest.py
# run with python2.7 -m pytest -xvs applications/paideia/tests/modules/
"""

import pytest


class TestBug():
    '''
    Unit testing class for the paideia_bugs.Bug class.
    '''
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('record_id,path_id,step_id,score,response_string,'
                             'loc_id',
                             [(22,  # record_id
                               4,  # 'path_id':
                               108,  # 'step_id':
                               0.5,  # 'score':
                               'hi',  # 'response_string':
                               8)  # 'loc_id':
                              ])
    def test_bug_undo(self, record_id, path_id, step_id, score,
                      response_string, loc_id):
        """
        Unit test for BugReporter.get_reporter() method.
        """

        mybug = Bug(step_id=step_id, path_id=path_id, loc_id=loc_id)
        result = mybug.undo(bug_id, log_id, score, bugstatus, user_id, comment,
                            user_response, user_comment, adjusted_score)
