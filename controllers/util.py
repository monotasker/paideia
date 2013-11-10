# coding: utf-8
"""
Controller functions handling back-end utility tasks (mostly db maintenance).
"""

if 0:
    from gluon import current, SQLFORM, BEAUTIFY, Field, UL, LI, A, P, URL
    db = current.db
    auth = current.auth
    request = current.request
from ast import literal_eval
import paideia_utils
#from pprint import pprint


@auth.requires_membership('administrators')
def make_path():
    """
    Uses paideia_utils.PathFactory() class to programmatically create paths.
    """
    message = ''
    output = ''
    form, message, output = TranslatePath().make_form()

    return {'form': form, 'message': message, 'output': BEAUTIFY(output)}


@auth.requires_membership('administrators')
def migrate_field():
    fields = {'plugin_slider_slides': ('content', 'slide_content')}

    for t, f in fields.iteritems():
        table = t
        source_field = f[0]
        target_field = f[1]
        items = db(db[table].id > 0).select()
        c = 0
        for i in items:
            values = {target_field: i[source_field]}
            i.update_record(**values)
            c += 1

    return {'records_copied': c}


@auth.requires_membership('administrators')
def to_migrate_table():
    items = db(db.pages.id > 0).select()
    c = 0
    for i in items:
        db.journal_pages.insert(**{'journal_page': i.page})
        c += 1

    return dict(records_moved=c)


@auth.requires_membership('administrators')
def migrate_back():
    items = db(db.images_migrate.id > 0).select()
    c = 0
    for i in items:
        c += 1
        db.images[i.id] = i.as_dict()

    return dict(records_updated=c)
