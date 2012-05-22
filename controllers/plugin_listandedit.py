# coding: utf8
import ast, pprint

def listing():
    """
    This plugin creates a large widget to display, edit, and add entries
    to one database table.

    LIST FORMAT
    By default the table rows are listed using either the "format" property
    of the table definition in the db model (if their is one), or the contents
    of the first table field (after the auto-generated id).

    ARGUMENTS
    Takes one required argument, the name of the table to be listed.

    VARIABLES
    An optional variable "restrictor" can be used to filter the displayed
    records. This variable must be a dictionary in which the keys are the names
    of fields in the table and the values are the values to be allowed in those
    fields when generating the list.
    """
    response.files.append(URL('static',
            'plugin_listandedit/plugin_listandedit.css'))
    response.files.append(URL('static',
            'plugin_listandedit/plugin_listandedit.js'))

    #get table to be listed
    tablename = request.args[0]
    #pass that name on to be used as a title for the widget
    rname = tablename

    #get filtering values if any
    if 'restrictor' in request.vars:
        restr = request.vars['restrictor']
        # convert the string from the URL to a python dictionary object
        restrictor = ast.literal_eval(restr)
    else:
        restrictor = None
    session.restrictor = restrictor

    #check to make sure the required argument names a table in the db
    if not tablename in db.tables():
        response.flash = '''Sorry, you are trying to list
        entries from a table that does not exist in the database.'''
    else:
        tb = db[tablename]
        #select all rows in the table

        #filter that set based on any provided field-value pairs in request.vars.restrictor
        if restrictor:
            for k, v in restrictor.items():
                filter_select = db(tb[k] == v)._select(tb.id)
                rowlist = db(tb.id.belongs(filter_select)).select()
        else:
            rowlist = db(tb.id > 0).select()

    # build html list from the selected rows
    listset = []
    for r in rowlist:
        fieldname = db[tablename].fields[1]
        # use format string from db table definition to list entries (if available)
        if db[tablename]._format:
            try:
                listformat = db[tablename]._format % r
            except:
                listformat = db[tablename]._format(r)
        else:
            listformat = r[fieldname]

        i = A(listformat, _href=URL('plugin_listandedit', 'edit.load', args=[tablename, r.id]), _class='plugin_listandedit_list', cid='viewpane')
        listset.append(i)

    # create a link for adding a new row to the table
    adder = A('Add new', _href=URL('plugin_listandedit', 'edit.load', args=[tablename]), _class='plugin_listandedit_list', cid='viewpane')

    return dict(listset = listset, adder = adder, rname = rname)

def makeurl(tablename):
    if session.restrictor:
        rstring = '{'
        for k, v in session.restrictor:
            rstring += "'%s':'%s'" % k, v
        rstring += '}'
    else:
        rstring = ''
    the_url = URL('plugin_listandedit', 'listing.load', args=tablename, vars=rstring)
    return the_url

def edit():
    print '\n starting controllers/plugin_listandedit edit()'
    tablename = request.args[0]
    if len(request.args) > 1:
        rowid = request.args[1]
        formname = '%s/%s' % (tablename, rowid)
        print 'formname: ', formname

        #TODO: Set value of "project" field programatically
        #TODO: re-load listing component on form submit
        form = SQLFORM(db[tablename], rowid, separator='', showid=False)
        pprint.pprint(form.vars)
        if form.process(formname=formname).accepted:
            the_url = makeurl(tablename)
            response.js = "web2py_component('%s', 'listpane');" %  the_url
            response.flash = 'The changes were recorded successfully.'
            print form.vars
        elif form.errors:
            print form.vars
            print hi
            response.flash = 'Sorry, there was an error processing ' \
                             'the form. The changes have not been recorded.'
        else:
            #TODO: Why is this line being run when a record is first selected?
            print form.vars
            pass

    elif len(request.args) == 1:
        formname = '%s/create' % (tablename)

        form = SQLFORM(db[tablename], separator='', showid=False)
        if form.process(formname=formname).accepted:
            the_url = makeurl(tablename)
            response.js = "web2py_component('%s', 'listpane');" %  the_url
            response.flash = 'New record successfully created.'
        elif form.errors:
            print form.vars
            response.flash = 'Sorry, there was an error processing '\
                             'the form. The new record has not been created.'
        else:
            pass

    else:
        response.flash = 'Sorry, you need to specify a type of record before I can listing the records.'

    return dict(form = form)
