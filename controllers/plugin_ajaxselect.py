if 0:
    from gluon import current, SELECT, OPTION, SQLFORM, URL, DAL
    db = DAL()
    request, response = current.request, current.response

from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget

def set_widget():
    """
    creates a replacement instance of the OptionsWidget class defined in 
    gluon.sqlhtml and returns the result to re-populate the ajax LOAD field
    """

    #get variables to build widget for the proper field, with proper current value
    table = request.args[0]
    field = request.args[1]
    linktable = request.args[2]
    #args[3] is the wrappername, but is not used in this function

    valstring = request.vars['fieldval']
    #restore value to list since it was converted to string for url
    if valstring:
        value = valstring.split('-')
    else:
        value = None

    #use multiple select widget if 'multi' variable is set
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

    #testing for the extra argument added by javascript in plugin_ajaxselect.js when refresh is triggered by change in another select value
    if len(request.args) > 5:
        #get the value from the restricting select box to use in filtering this one
        filter_val = request.args[5]
        #find the table behind the constraining widget
        filter_t = request.args[6]
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
        w = SELECT(_id = n, _class = 'generic-widget', _name = field, 
                   _multiple = mval, size = sval, 
                   *[OPTION(e[rep], _value = e.id) for e in rows])
    else:
        #refresh using ordinary widget if no filter constraints
        w = widg.widget(the_field, value)

    return dict(widget = w, linktable = linktable)

def set_form_wrapper():
    """
    Creates the LOAD helper to hold the modal form for creating a new item in the linked table
    """
    tablename = request.args[0]
    fieldname = request.args[1]
    linktable = request.args[2]
    wrappername = request.args[3]

    formwrapper = LOAD('plugin_ajaxselect', 'linked_create_form.load', 
                       args = [tablename, fieldname, linktable, wrappername], 
                       vars = request.vars, 
                       ajax = True)

    return dict(formwrapper = formwrapper)


def linked_create_form():
    """
    creates a form to insert a new entry into the linked table which populates the ajaxSelect widget
    """

    tablename = request.args[0]
    fieldname = request.args[1]
    linktable = request.args[2]
    wrappername = request.args[3]
    
    form = SQLFORM(db[linktable])

    comp_url = URL('plugin_ajaxselect', 'set_widget.load', 
                   args = [tablename, fieldname, linktable, wrappername], 
                   vars = request.vars)

    if form.process().accepted:
        response.flash = 'form accepted'
        response.js = "web2py_component('%s', '%s');" % (comp_url, wrappername)
    else:
        response.error = 'form was not processed'

    return dict(form = form)
