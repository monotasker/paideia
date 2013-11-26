# _*_ coding: utf-8 _*_

"""
Controller functions handling back-end utility tasks (mostly db maintenance).
"""

if 0:
    from gluon import current, BEAUTIFY
    db = current.db
    auth = current.auth
    request = current.request
import paideia_utils
import traceback
#from pprint import pprint


@auth.requires_membership('administrators')
def make_path():
    """
    Uses paideia_utils.PathFactory classes to programmatically create paths.
    """
    path_type = request.args[0] if request.args else 'default'
    factories = {'default': paideia_utils.PathFactory,
                 'translate_word': paideia_utils.TranslateWordPathFactory}
    message = ''
    output = ''
    form, message, output = factories[path_type]().make_create_form()

    return {'form': form, 'message': message, 'output': BEAUTIFY(output)}


@auth.requires_membership('administrators')
def bulk_update():
    """
    Controller function to perform a programmatic update to a field in one table.
    """
    myrecs = None
    form = SQLFORM.factory(
        Field('table', requires=IS_IN_SET(db.tables)),
        Field('field'),
        Field('query'),
        Field('new_value'))
    if form.process().accepted:
        query = eval(form.vars.query)
        try:
            recs = db(query)
            recs.update(**{form.vars.field: form.vars.new_value})
            myrecs = recs.select()
            response.flash = 'update succeeded'
        except Exception:
            print traceback.format_exc(5)
    elif form.errors:
        response.flash = 'form has errors'

    return dict(form=form, recs=myrecs)

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
