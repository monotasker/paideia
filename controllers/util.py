#! /usr/bin/python
# _*_ coding: utf-8 _*_

"""
Controller functions handling back-end utility tasks (mostly db maintenance).
"""

if 0:
    from gluon import current, SQLFORM, Field, IS_IN_SET, BEAUTIFY
    db = current.db
    auth = current.auth
    request = current.request
    response = current.response
from paideia_utils import test_step_regex, GreekNormalizer
from plugin_utils import flatten, makeutf8
import paideia_path_factory
import re
import traceback
import StringIO
import uuid
from pprint import pprint


@auth.requires_membership('administrators')
def gather_word_forms():
    """
    Return a list of all strings satisfying the supplied regex.

    The fieldnames argument should be a list, so that multiple target fields
    can be searched at once.

    The optional 'unique' keyword argument determines whether duplicates will
    be removed from the list. (Defaults to True.)

    The optional 'filterfunc' keyword argument allows a function to be passed
    which which will be used to alter the gathered strings. This alteration will
    happen before duplicate values are removed. So, for example, the strings
    can be normalized for case or accent characters if those variations are
    not significant.
    """

    items = []
    db = current.db
    x = ['πιλ', 'βοδυ', 'μειδ', 'νηλ', 'ἰλ', 'σαγγ', 'ἁμ', 'ἱτ', 'ἑλπ', 'ἑλω', 'ο',
         'βοτ', 'ὁλ', 'ὁγ', 'παθ', 'τιψ', 'β', 'σωλ', 'κορπ', 'ὡλ', 'κατς', 'γγς',
         'μωλτεγγ', 'δεκ', 'φιξ', 'βαλ', 'διλ', 'δαξ', 'δρομα', 'δακ', 'δαγ', 'ἁγ',
         'λοξ', 'δυδ', 'βωθ', 'ὐψ', 'καν', 'καβ', 'ὀτ', 'βαδ', 'μωστ', 'μοισδ',
         'μιλ', 'βελ', 'ἑδ', 'θοτ', 'κιλ', 'κρω', 'βοχ', 'ω', 'μεντ', 'ἁτ', 'νεατ',
         'σπηρ', 'βοδι', 'πιτ', 'βονδ', 'ἁρδ', 'δοκς', 'μελτ', 'βεδ', 'μαλ', 'δατς',
         'σωπ', 'α', 'πενσιλ', 'κς', 'δεκς', 'αριας', 'βαγγ', 'σετ', 'βρουμ', 'ἀδ',
         'πωλ', 'δατ', 'ἁγγ', 'πραυδ', 'αὐτης', 'νειλ', 'σογγ', 'ζαπ', 'κλαδ',
         'νιτ', 'φαξ', 'βολ', 'κεπτ', 'μοιστ', 'ἁμερ', 'τουνα', 'προγγ', 'τ',
         'κλυν', 'λοβ', 'πλειαρ', 'κροπ', 'βανδ', 'μωλτεν', 'υτ', 'κοτ', 'κοπ',
         'ἀτ', 'φυξ', 'ὡλι', 'μυτ', 'θατ', 'δοτ', 'βικς', 'ἁμαρ', 'λωφερ', 'δοκ',
         'ταπ', 'ἀβωδ', 'ὑτος', 'λωφρ', 'ἁμρ', 'ροκ', 'πς', 'βαδυ', 'οὐψ', 'πραγγ',
         'σπειρ', 'ἀγγλ', 'σλαψ', 'πλαυ', 'δραμα', 'φοξ', 'ἱτεδ', 'ὁτ', 'δογ',
         'δολ', 'ρω', 'δοξ', 'ὗτος', 'μιτ', 'αὑ', 'ἱτς', 'μωλτ', 'βατ', 'βαχ',
         'βικ', 'μιαλ', 'μολ', 'μιελ', 'κον', 'μωισδ', 'κραπ', 'καπ', 'ὑπ', 'ἀγκλ',
         'λιξ', 'ρωλ', 'λαβ', 'ὀδ', 'λαξ', 'δοτς', 'ἀνκλ', 'ρακ', 'πεγ', 'τυνα',
         'βρυμ', 'καρπ', 'βρεδ', 'κιπ', 'μηδ', 'δαλ', 'βετ', 'διπ', 'κλιν', 'πετ',
         'βαδι', 'λικς', 'δακς', 'πς', 'ὑπ', 'κς', 'α', 'ος', 'μιτ', 'βρεδ', 'ί',
         'ο', 'νεατ', 'δι', 'Ω', 'τ', 'υτ', 'η', 'ον', 'β', 'α', 'δεξ', 'παι']
    x = [makeutf8(word) for word in x]

    form = SQLFORM.factory(Field('search_table', default='steps',
                                 writable=False),
                           Field('search_field',
                                 requires=IS_IN_SET(['prompt',
                                                     'readable_response'])),
                           Field('write_table', default='word_forms',
                                 writable=False),
                           Field('write_field', default='word_form',
                                 writable=False),
                           Field('unique', 'boolean', default=True),
                           Field('testing', 'boolean', default=True),
                           Field('new', 'boolean', default=True))
    form.vars.search_table = 'steps'
    form.vars.write_table = 'word_forms'
    form.vars.write_field = 'word_form'

    if form.process().accepted:
        vv = form.vars
        filter_func = eval(vv.filter_func) if vv.filter_func else None
        trans_func = eval(vv.trans_func) if vv.trans_func else None

        rows = db(db[vv.search_table].id > 0).select()
        for r in rows:
            items.append(r[vv['search_field']])

        ptrn = re.compile(u'[\u0370-\u03FF\u1F00-\u1FFF]+', flags=re.U)
        items = flatten([re.findall(ptrn, makeutf8(i)) for i in items])
        normalizer = GreekNormalizer()
        items = [normalizer.normalize(i) for i in items]
        if vv.unique:
            items = list(set(items))
        items = [i.lower() for i in items if i not in x]

        if vv.new:
            existing = [makeutf8(r['word_form']) for r in
                        db(db.word_forms.id > 0).select(db.word_forms.word_form)]
            items = [i for i in items if i not in existing
                     and i.capitalize() not in existing
                     and i.lower() not in existing]
        if vv.testing:
            pass
            response.flash = 'Success, but nothing written to database.'
        else:
            newdata = [{'word_form': item} for item in items]
            rowcount = db.word_forms.bulk_insert(newdata)
            response.flash = 'Success. Added', len(rowcount), 'new word forms.'

    elif form.errors:
        items = BEAUTIFY(form.errors)

    return {'form': form, 'items': items}


@auth.requires_membership('administrators')
def test_regex():
    """
    Test whether a step's regex is satisfied by all of its readable responses.
    """
    form, result = test_step_regex()
    return {'form': form, 'result': result}


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
    """
    ===========================================================
    items = db(db.auth_group.id > 0).select()
    for i in items:
        if i.end_date:
            db.classes.update_or_insert(**{'institution': i.institution,
                                           'academic_year': i.academic_year,
                                           'term': i.term,
                                           'course_section': i.course_section,
                                           'instructor': i.course_instructor,
                                           'start_date': i.start_date,
                                           'end_date': i.end_date,
                                           'paths_per_day': i.paths_per_day,
                                           'days_per_week': i.days_per_week
                                           })
        else:
            pass
    cc = db(db.classes.id > 0).select().as_dict()

    ===========================================================
    """
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

"""
@auth.requires_membership('administrators')
def set_timestamps():
    # Make sure that every record in the database has a uuid.

    retval = {}
    mytime = datetime.datetime(2014, 1, 1)
    for t in db.tables:
        #if t in ['lemmas', 'constructions', 'word_forms', 'badges', 'steps',
        #         'paths', 'plugin_slider_slides', 'plugin_slider_decks']
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
"""
