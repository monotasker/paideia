# coding: utf8


def duplicateRow(tablename, rowid):
    orig = db(db[tablename].id=rowid).select().first()


def duplicateAndEdit(tablename, rowid):
    """
    Duplicate a database row and open up the new row for
    further editing.
    """
    pass
