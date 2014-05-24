#! /usr/bin/python
# --coding:utf8--

"""
Part of the plugin plugin_1way_sync for the web2py framework.
"""

if 0:
    from plugins.plugin_1way_sync import OnewaySyncer


def oneway_csv_sync():
    """
    Perform a 1-way sync of data from the supplied csv file.
    """
    o = OnewaySyncer()
    form, output = o.get_form()
    return {'form': form, 'output': output}
