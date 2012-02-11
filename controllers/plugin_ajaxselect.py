if 0:
    from gluon import current, SELECT, OPTION, SQLFORM, URL, LOAD, SPAN
    request, response, db = current.request, current.response, current.db

from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget

def set_widget():
    """
    creates a replacement instance of the OptionsWidget class defined in 
    gluon.sqlhtml and returns the result to re-populate the ajax LOAD field
    """

    #get variables to build widget for the proper field
    #TODO: Can I get the table from db[field]._table or something like that?
    table = request.args[0]
    field = request.args[1]
    #args[2] is the wrappername, but is not used in this function

    #get name of table linked to this reference field
    linktable = request.vars['linktable']
    #get current value of field to be selected in refreshed widget
    if 'fieldval' in request.vars:
        valstring = request.vars['fieldval']
        #restore value to listing since it was converted to string for url
        if valstring:
            value = valstring.split('-')
        else:
            value = None
    else:
        value = None
        
    #find out whether widget should be single select widget or multiselect
    if 'multi' in request.vars:
        if request.vars['multi'] == 'basic':
            widg = MultipleOptionsWidget()
            mval = True;
            sval = '5'
    else:
        widg = OptionsWidget()
        mval = False;
        sval = '1'

    the_table = db[table]
    the_field = the_table[field]
    the_linktable = db[linktable]

    #build listing of current field values
    taglist = []
    #FIXME: Move these styles into a separate stylesheet
    #FIXME: Add this capacity to the initial loading of the widget 
    # (probably means having module class instantiate widget via this controller rather 
    # than having separate instantiation in the class code--easier db access). 
    tagstyle = 'display:inline-block; padding:3px; border-radius:0 6px 6px 0; background-color:#ccc;'
    
    if request.vars['multi'] == 'basic':
        fn = the_linktable.fields[1]
        if isinstance(value, list):
            print fn
            for v in value:
                itm = db(the_linktable.id == v).select(fn).first()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                taglist.append(SPAN(itm[fn], _class = 'selected_item', _style = tagstyle))
        else:
            itm = db(the_linktable.id == value).select(fn).first()
            taglist.append(SPAN(itm[fn], _class = 'selected_item', _style = tagstyle))
    print taglist

    #testing for the extra argument added by javascript in plugin_ajaxselect.js 
    #when refresh is triggered by change in another select value
    if 'rval' in request.vars:
        #get the value from the restricting select box to use in filtering this one
        filter_val = request.vars['rval']
        #find the table behind the constraining widget
        filter_t = request.vars['rtable']
        #find the corresponding field in this select's linked table
        ref = 'reference %s' % filter_t
        cf = [f for f in the_linktable.fields if the_linktable[f].type == ref][0]
        #filter the rows from the linked table accordingly
        rows = db(the_linktable[cf] == filter_val).select()
        #get the field name to represent values in the new select widget
        rep = the_linktable.fields[1]
        #build the name for the refreshed select widget
        n = table + '_' + field
               
        #create the widget with filtered options
        w = SELECT(_id = n, _class = 'generic-widget plugin_ajaxselect multi_basic', 
                   _name = field, _multiple = mval, size = sval, 
                   *[OPTION(e[rep], _value = e.id) for e in rows])
    else:
        #refresh using ordinary widget if no filter constraints
        w = widg.widget(the_field, value)

    return dict(widget = w, taglist = taglist, linktable = linktable)

def set_form_wrapper():
    """
    Creates the LOAD helper to hold the modal form for creating a new item in the linked table
    """
    tablename = request.args[0]
    fieldname = request.args[1]
    wrappername = request.args[2]
    
    formwrapper = LOAD('plugin_ajaxselect', 'linked_create_form.load', 
                       args = [tablename, fieldname, wrappername],
                       vars = request.vars, 
                       ajax = True)

    return dict(formwrapper = formwrapper)


def linked_create_form():
    """
    creates a form to insert a new entry into the linked table which populates the ajaxSelect widget
    """

    tablename = request.args[0]
    fieldname = request.args[1]
    wrappername = request.args[2]

    linktable = request.vars['linktable']
    form = SQLFORM(db[linktable])

    comp_url = URL('plugin_ajaxselect', 'set_widget.load', 
                   args = [tablename, fieldname, wrappername],
                   vars = request.vars)

    if form.process().accepted:
        response.flash = 'form accepted'
        response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
    else:
        response.error = 'form was not processed'

    return dict(form = form)
