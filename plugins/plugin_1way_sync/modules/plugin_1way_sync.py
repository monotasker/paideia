#! /usr/bin/python
# --coding:utf8--

"""
Part of the plugin plugin_1way_sync for the web2py framework.
"""

import csv
from gluon import FORM, INPUT, current
from plugin_sqlite_backup import copy_db
from pprint import pprint


class OnewaySyncer(object):
    """
    Sync data from the supplied csv file with the local app database.

    This is a very (dangerously) dumb sync. It does not pay any attention to
    which data is newer or check for duplicate table entries. It simply looks
    for differences between the csv data and the corresponding local table
    and either (a) adds a new row if there is no local row with the
    corresponding id or (b) updates the local row to conform to the csv
    data for the same row id.

    """

    def __init__(self):
        """docstring for __init__"""
        pass

    def get_form(self):
        """
        """
        db = current.db
        form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
        output = None
        if form.process().accepted:
            csvfile = db.parse_csv(form.vars.data.file)

            # for every table
            #for table in db.tables:
                ## for every uuid, delete all but the latest
                #items = db(db[table]).select(db[table].id,
                        #db[table].uuid,
                        #orderby=db[table].modified_on,
                        #groupby=db[table].uuid)
                #for item in items:
                    #db((db[table].uuid==item.uuid)&
                       #(db[table].id!=item.id)).delete()
            pprint(csvfile)
            output = pprint(csvfile)

        return {'form': form, 'output': output}

    def _parse_csv_table(self, tablename, csvfile):
        """
        Return a dictionary representing the csv data for the supplied table.

        The top-level dict keys are id numbers, one per row in the table.
        The top-level values are dictionaries whose keys are field names and
        values are the corresponding field values for the given row.
        """
        null = '<NULL>'
        unique = 'uuid'
        id_offset = {}

        reader = csv.reader(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL)
        first = True
        unique_idx = None
        colnames = None
        tdict = {}
        for lineno, line in enumerate(reader):
            if not line:
                break
            if not colnames:  # assume first line containing colnames
                colnames = [x.split('.',1)[-1] for x in line][:len(line)]
                cols, cid = [], None
                for i,colname in enumerate(colnames):
                    if is_id(colname):
                        cid = i
                    elif colname in self.fields:
                        cols.append((i,self[colname]))
                    if colname == unique:
                        unique_idx = i
            else:  # every other line contains data instead
                items = []
                for i, field in cols:
                    try:
                        items.append(fix(field, line[i], id_map, id_offset))
                    except ValueError:
                        raise RuntimeError("Unable to parse line:%s field:%s value:'%s'"
                                           % (lineno+1,field,line[i]))

                if not (id_map or cid is None or id_offset is None or unique_idx):
                    csv_id = long(line[cid])
                    curr_id = self.insert(**dict(items))
                    if first:
                        first = False
                        # First curr_id is bigger than csv_id,
                        # then we are not restoring but
                        # extending db table with csv db table
                        id_offset[self._tablename] = (curr_id-csv_id) \
                            if curr_id>csv_id else 0
                    # create new id until we get the same as old_id+offset
                    while curr_id<csv_id+id_offset[self._tablename]:
                        self._db(self._db[self][colnames[cid]] == curr_id).delete()
                        curr_id = self.insert(**dict(items))
                # Validation. Check for duplicate of 'unique' &,
                # if present, update instead of insert.
                elif not unique_idx:
                    new_id = self.insert(**dict(items))
                else:
                    unique_value = line[unique_idx]
                    query = self._db[self][unique] == unique_value
                    record = self._db(query).select().first()
                    if record:
                        record.update_record(**dict(items))
                        new_id = record[self._id.name]
                    else:
                        new_id = self.insert(**dict(items))
                if id_map and cid is not None:
                    id_map_self[long(line[cid])] = new_id

    def parse_csv(self, csvfile):
        """
        Parse csvfile and return a 2-level nested dictionary of the data.

        The top-level keys of the dict are table names. The second-level keys
        are field names within the table. The second-level values are the
        field contents.

        """
        db = current.db
        #csvdata = csv.reader(csvfile)
        dd = {}

        for line in csvfile:
            line = line.strip()
            if not line:  # ignore empty lines
                continue
            elif line == 'END':  # file is finished
                return
            elif not line.startswith('TABLE ') or \
                    not line[6:] in db.tables:
                raise SyntaxError('invalid file format')
            else:  # line parsing starts
                tablename = line[6:]
                if tablename is not None and tablename in db.tables:
                    dd[tablename] = self._parse_csv_table(tablename, csvfile)
                elif tablename is None or ignore_missing_tables:
                    # skip all non-empty lines
                    for line in ifile:
                        if not line.strip():
                            break
                else:
                    raise RuntimeError("Unable to import table that does not "
                                       "exist.\nTry db.import_from_csv_file(..."
                                       ", map_tablenames={'table':'othertable'}"
                                       ",ignore_missing_tables=True)")
            return dd


    def sync(self):
        """
        Sync data from the supplied csv file with the local app database.

        This is a very (dangerously) dumb sync. It does not pay any attention to
        which data is newer or check for duplicate table entries. It simply looks
        for differences between the csv data and the corresponding local table
        and either (a) adds a new row if there is no local row with the
        corresponding id or (b) updates the local row to conform to the csv
        data for the same row id.

        """
        assert copy_db()  # make sure db is backed up before the import happens

