#! /usr/bin/python
# -*-coding:utf8-*-

import re
import pytest
from plugin_1way_sync import OnewaySyncer

@pytest.fixture
def myfix():
    """docstring for myfix testing fixture."""
    pass


class TestOnewaySyncer():
    """
    """
    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('', [()])
    def test_get_form(self):
        actual = OnewaySyncer().get_form()
        expected = ['<form action="#" enctype="multipart/form-data" method="post">'
                    '<input name="data" type="file" />'
                    '<input type="submit" />'
                    '<div style="display:none;">'
                    '<input name="_formkey" type="hidden" '
                    'value="\n+" />'
                    '<input name="_formname" type="hidden" value="default" />'
                    '</div>'
                    '</form>']
        assert re.match(actual['form'].xml(), expected[0])
        assert actual['output'] == None

    @pytest.mark.skipif(False, reason='just because')
    @pytest.mark.parametrize('table,csvfile',
                             [()
                              ])
    def test_parse_csv_table(self, table, csvfile, db):
        # create and populate test table
        #if ['testing'] not in db.tables:
            #db.define_table('testing', Field('lemma'))
        #db.testing.truncate()
        #db.testing.insert(lemma='ποιεω')
        #db.testing.insert(lemma='ἀκουει')

        # test data
        headers = ['testing.id', 'testing.lemma']
        rows = {1: 'ποιεω',
                2: 'ἀκουω',
                3: 'εἱς'}

        # write test data to csv file
        writer = csv.writer(open('test_parse_csv_table.csv', 'wb'))
        writer.writerow(headers)
        for key, value in rows.items():
            writer.writerow([key, value])

        actual = OnewaySyncer().parse_csv_table('testing',
                                                'test_parse_csv_table.csv')

        assert actual == rows

