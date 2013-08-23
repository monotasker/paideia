# coding: utf-8

if 0:
    from gluon import current
    db = current.db


def migrate_field():
    fields = {'tags': ('position', 'tag_position')}

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


def to_migrate_table():
    items = db(db.pages.id > 0).select()
    c = 0
    for i in items:
        db.journal_pages.insert(**{'journal_page': i.page})
        c += 1

    return dict(records_moved=c)


def migrate_back():
    items = db(db.images_migrate.id > 0).select()
    c = 0
    for i in items:
        c += 1
        db.images[i.id] = i.as_dict()

    return dict(records_updated=c)
