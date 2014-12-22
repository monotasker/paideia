#! /usr/bin/python
# _*_ coding: utf-8 _*_

"""
Controller functions handling back-end utility tasks (mostly db maintenance).
"""

if 0:
    from gluon import current, SQLFORM, Field, IS_IN_SET
    db = current.db
    auth = current.auth
    request = current.request
    response = current.response
from paideia_utils import test_step_regex, gather_vocab
#from plugin_utils import capitalize
import paideia_path_factory
import traceback
import StringIO
import uuid
from pprint import pprint


@auth.requires_membership('administrators')
def test_regex():
    """
    Test whether a step's regex is satisfied by all of its readable responses.
    """
    form, result = test_step_regex()
    return {'form': form, 'result': result}


@auth.requires_membership('administrators')
def collect_step_vocab():
    vocab, dups = gather_vocab()
    return {'vocab': vocab, 'dups': dups}


@auth.requires_membership('administrators')
def make_path():
    """
    Uses paideia_utils.PathFactory classes to programmatically create paths.
    """
    print "Got controller==========================================="
    path_type = request.args[0] if request.args else 'default'
    factories = {'default': paideia_path_factory.PathFactory,
                 'translate_word': paideia_path_factory.TranslateWordPathFactory}
    message = ''
    output = ''
    form, message, output = factories[path_type]().make_create_form()
    print "Returning initial form"

    print 'returning result:'
    print 'message'

    return {'form': form, 'message': message, 'output': output}


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
    items = db(db.auth_membership.id > 0).select()
    for i in items:
        if i.group_id == 1:
            pass
        else:
            cls = db((db.auth_group.id == i.group_id) &
                     (db.auth_group.end_date == db.classes.end_date)
                     ).select().first()
            print i.user_id, ':', cls.classes.id
            db.class_membership.update_or_insert(**{'name': i.user_id,
                                                    'class_section': cls.classes.id})
    cc = db(db.class_membership.id > 0).select().as_dict()
    return {'result': pprint(cc)}


@auth.requires_membership('administrators')
def migrate_back():
    items = db(db.images_migrate.id > 0).select()
    c = 0
    for i in items:
        c += 1
        db.images[i.id] = i.as_dict()

    return dict(records_updated=c)


@auth.requires_membership('administrators')
def export_db():
    s = StringIO.StringIO()
    db.export_to_csv_file(s)
    response.headers['Content-Type'] = 'text/csv'
    return s.getvalue()


@auth.requires_membership('administrators')
def update_uuids():
    """
    Make sure that every record in the database has a uuid.
    """
    retval = {}
    for t in db.tables:
        print 'start table', t
        recs = db(db[t].id > 0).select()
        print 'found', len(recs), 'records'
        changed = 0
        dated = 0
        try:
            for r in recs:
                if r.uuid is None:
                    r.update_record(uuid=str(uuid.uuid4()))
                    changed += 1
                if r.modified_on is None:
                    r.update_record(modified_on=request.now)
                    dated += 1
            print 'changed', changed
        except:
            traceback.print_exc(5)
        retval[t] = ('changed {}'.format(changed),
                     'dated {}'.format(dated))

    return {'changes': retval}


@auth.requires_membership('administrators')
def set_timestamps():
    """
    Make sure that every record in the database has a uuid.
    """
    retval = {}
    mytime = datetime.datetime(2014, 1, 1)
    for t in db.tables:
        #if t in ['lemmas', 'constructions', 'word_forms', 'badges', 'steps',
                 #'paths', 'plugin_slider_slides', 'plugin_slider_decks']
        print 'start table'
        recs = db(db[t].id > 0).select()
        print 'found', len(recs), 'records'
        dated = 0
        try:
            for r in recs:
                r.update_record(modified_on=mytime)
                dated += 1
            print 're-dated', dated
        except:
            traceback.print_exec(5)
        retval[t] = ('changed {}'.format(changed),
                     'dated {}'.format(dated))

    return {'changes': retval}
