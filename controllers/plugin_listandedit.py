# coding: utf8
if 0:
    from gluon import current, URL, A
    from gluon.sqlhtml import SQLFORM
    response, request, db, session = current.response, current.request, current.db, current.session

def listing():
    """
    API: Takes two required arguments. The first is the name of the 
    table being listed, and the second is the id of the project.
    Takes one required variable in the URL request: a dictionary with at 
    least one item with the index 'fields'. The value of 
    request.vars[fields] provides the fields to be used to represent each 
    record in the listing.
    """
    response.files.append(URL('static', 
            'plugin_listandedit/plugin_listandedit.css'))
    response.files.append(URL('static', 
            'plugin_listandedit/plugin_listandedit.js'))

    tablename = request.args[0]
    if len(request.args) > 1:
        restrictor = request.args[1]
        session.restrictor = restrictor
        rname_row = db(db.projects.id == restrictor).select().first()
        rname = rname_row.projectname
    else:
        restrictor = None
        rname = None
    fieldnames = request.vars['fields']

    rowlist = ''
    if not tablename in db.tables():
        response.flash = '''Sorry, you are trying to list 
        entries from a table that does not exist in the database.'''
    else:
        tb = db[tablename]
        #TODO: Get tables and fields programmatically
        if restrictor:
            rowlist = db((tb.author == db.authors.id) & (tb.work == db.works.id) & (tb.project == restrictor)).select()
        else:
            rowlist = db(tb.id > 0).select()

    listset = []
    for r in rowlist:
        #FIXME: I need to get these values programmatically from vars['fields']
        fieldname = db[tablename].fields[1]
        listformat = r[fieldname]
        print r.id

        i = A(listformat, _href=URL('plugin_listandedit', 'edit.load', args=[tablename, r.id]), _class='plugin_listandedit_list', cid='viewpane')
        listset.append(i)

    adder = A('Add new', _href=URL('plugin_listandedit', 'edit.load', args=[tablename]), _class='plugin_listandedit_list', cid='viewpane')

    return dict(listset = listset, adder = adder, rname = rname)

def edit():
    tablename = request.args[0]
    if len(request.args) > 1:
        rowid = request.args[1]
        formname = '%s/%s' % (tablename, rowid)

        #TODO: Set value of "project" field programatically
        #TODO: Fix widget of "tags" field (adder and multi-select)
        #TODO: re-load listing component on form submit
        form = SQLFORM(db[tablename], rowid, separator='', showid=False)
        if form.process(formname=formname).accepted:
            response.flash = 'The changes were recorded successfully.'
        elif form.errors:
            print form.vars
            response.flash = 'Sorry, there was an error processing ' \
                             'the form. The changes have not been recorded.'
        else:
            #TODO: Why is this line being run when a record is first selected?
            pass

    elif len(request.args) == 1:
        formname = '%s/create' % (tablename)

        form = SQLFORM(db[tablename], separator='', showid=False)
        if form.process(formname=formname).accepted:
            arglist = [tablename]
            if session.restrictor:
                arglist.append(session.restrictor)
            the_url = URL('plugin_listandedit', 'list.load', args=arglist)
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