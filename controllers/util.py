# coding: utf-8

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
    form = SQLFORM.factory(Field('path_dicts', 'list:string'))
    if form.process(dbio=False, keepvalues=True).accepted:
        fact = paideia_utils.PathFactory()
        stringlist = request.vars.path_dicts
        for idx, strg in enumerate(stringlist):
            if strg[-1] == ',':
                stringlist[idx] = strg[:-1]
        rawstring = ','.join(stringlist)
        pd_string = '{{{}}}'.format(' '.join(rawstring.split()))
        mydict = literal_eval(pd_string)
        paths, result = fact.make_path(mydict)
        successes = {r: v for r, v in result.iteritems() if r[0] != 'failure'}
        failures = {r: v for r, v in result.iteritems() if r[0] == 'failure'}
        message = 'Created {} new paths.\n' \
                  '{} paths failed'.format(len(successes.keys()),
                                           len(failures.keys()))
        output = UL()
        for s, v in successes.iteritems():
            output.append(LI(s,
                             A('path {}'.format(v[0]),
                               _href=URL('paideia', 'editing', args=['paths', v[0]])),
                             A('step {}'.format(v[1]),
                               _href=URL('paideia', 'editing', args=['steps', v[1]])),
                            _class='make_paths_success'))

        for f, v in failures.iteritems():
            output.append(LI(f, P(v[1]), _class='make_paths_failure'))
    elif form.errors:
        message = BEAUTIFY(form.errors)

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
