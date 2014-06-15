#! /usr/bin/python
# -*-coding:utf8-*-

import pytest

class TestOnewaySyncer():
    """
    """

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,stype', [(1, StepText)])
    def test_get_form(self):
        pass


    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,stype', [(1, StepText)])
    def test_parse_csv(self):
        pass

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,stype', [(1, StepText)])
    def test_parse_csv_table(self):
        """docstring for test_parse_csv_table"""
        pass

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,stype', [(1, StepText)])
    def test_copy_db():
        """
        """
        pass

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('stepid,stype', [(1, StepText)])
    def test_sync(self):
        """
        """
        pass
