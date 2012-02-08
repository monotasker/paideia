from gluon import current, SPAN, A, DIV
from gluon.custom_import import track_changes
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget 
#TODO: add ListWidget as another option?

#TODO: Move the current calls to within the methods
session, request, response = current.session, current.request, current.response
response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.js'))

#TODO: set track changes to false when dev is finished
track_changes(True)

class AjaxSelect:
    """
    This plugin creates a select widget wrapped that can be refreshed via ajax 
    without resetting the entire form. It also provides an "add new" button 
    that allows users to add a new item to the table that populates the select 
    widget via ajax. The widget is then automatically refreshed via ajax so that 
    the new item is visible as a select option and can be chosen. All of this
    happens without a page or form refresh so that data entered in other fields 
    is not lost or submitted.

    Installation:
    1. download the plugin file;
    2. In the web2py online ide (design view for your app) scroll to the bottom section labeled "Plugins";
    3. At the bottom of that section is a widget to "upload plugin file". Click "Browse".
    4. In the file selection window that opens, navigate to the downloaded plugin file, select it, and
        click "open". The file selection window should close.
    5. Click the "upload" button.
    The plugin should now be installed and ready to use.

    Usage:
    In a web2py model file, import this class and then apply it as
    the widget-factory for one or more db fields. To do this for a field named
    'author' from a table named 'notes' you would add this line somewhere in
    the model file:

    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 'authors', {optional arguments}).widget()

    Note that the third argument passed to AjaxSelect should be the name of the
    table *referenced by the current field*. In this example, the field 'author'
    references the table 'authors'. So the third argument in this case is 'authors'.

    Optional arguments:
    refresher (True/False; defaults to True):a button to manually refresh the select
    widget via ajax.

    adder (True/False; defaults to True): a button to add a new record to the linked
    table that populates the select widget.

    restrictor ({form field name}): adds a dynamic constraint on the records displayed 
    in the named field's widget. When the specified form field (within the same form) 
    has its value changed, this select will be refreshed and its displayed records 
    filtered accordingly. Note that this is only useful if {fieldname} references 
    values shared with the linked table.

    e.g., to make the select constrain the widget for the 'works' table:
    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 'authors', restrictor='work').widget()

    multi (basic/False; defaults to False): Instead of displaying a single select 
    widget, the 'basic' value displays a standard multiselect widget (an html 
    select widget with a size greater than 1). This will only work properly if the 
    database field type is defined as "list:reference" in the model. 

    """
    #TODO: Get restriction to happen on initial widget creation, not just refresh 
    # maybe by moving all widget creation to the controller? but still have to get restrictor field val
    #TODO: allow for restrictor argument to take list and filter multiple other fields

    def __init__(self, field, value, linktable, refresher = False, adder = True,
                 restricted = "None", restrictor = "None", multi = False):
        self.field = field
        self.value = value
        self.linktable = linktable
        self.refresher = refresher
        self.adder = adder
        self.restricted = restricted
        self.restrictor = restrictor
        self.tablename = ""
        self.fieldname = ""
        self.wrappername = ""
        self.comp_url = ""
        self.add_url = ""
        self.adder_id = ""
        self.refresher_id = ""
        self.wrapper = ""
        self.w = ""
        self.classes = ""
        self.multi = multi
        self.clean_val = self.value
        #remove problematic pipe characters or commas from the field value 
        #in case of list:reference fields
        if self.multi and isinstance(self.value, list):
            self.clean_val = '-'.join(map(str, self.value))

    def get_fieldset(self):
        """get field and tablenames for the id's of the widget and associated elements"""
        #TODO: Why is this in a separate method? Move to _init_?
        fieldset = str(self.field).split('.')
        self.tablename = fieldset[0]
        self.fieldname = fieldset[1]

    def build_info(self):
        """Prepare information to be used in building widget and associated elements"""
        #build name for the span that will wrap the select widget
        self.wrappername = '%s_%s_loader' % (self.tablename, self.fieldname)

        #create ids for the "refresh" and "add new" buttons
        self.adder_id = '%s_add_trigger' % self.linktable
        self.refresher_id = '%s_refresh_trigger' % self.linktable

        #classes for wrapper span to indicate filtering relationships
        if self.restrictor == 'None':
            self.classes += ''
        else:
            self.classes += '%s restrictor for_%s' % (self.linktable, self.restrictor)

        #vars (params) for urls
        uvars = dict(multi = self.multi, fieldval = self.clean_val, linktable = self.linktable)
        #args for urls
        uargs = [self.tablename, self.fieldname, self.wrappername]

        #URL to refresh widget via ajax
        self.comp_url = URL('plugin_ajaxselect', 'set_widget.load', args = uargs, vars = uvars)
        #URL to load form for linking table via ajax
        self.add_url = URL('plugin_ajaxselect', 'set_form_wrapper.load', args = uargs, vars = uvars)



    #create the select widget
    def create_widget(self):
        
        #create either a single select widget or multiselect widget
        if self.multi == 'basic':
            self.w = MultipleOptionsWidget.widget(self.field, self.value)
        else:
            self.w = OptionsWidget.widget(self.field, self.value)

    def create_wrapper(self):
        """
        Create wrapper element and associated buttons, forms, etc. 
        Place the new widget inside.
        """
        #create the span wrapper and place the select widget inside
        span = SPAN(self.w, _id = self.wrappername, _class = self.classes)
        #prepare to hide 'refresh' button via CSS if necessary
        if self.refresher is False:
            rstyle = 'display:none'
        else:
            rstyle = ''
        #create 'add new' button
        refresh_a = A('refresh', _href = self.comp_url, 
                      _id = self.refresher_id, cid = self.wrappername, _style = rstyle)
        #create name for form to create new entry in linked table
        form_name = '%s_adder_form' % self.linktable
        #create 'add new' button to open form
        adder = A('add new', _href = self.add_url, _id = self.adder_id, 
                  _class = 'add_trigger', cid = form_name)       
        #create hidden div to hold form (to be displayed via modal dialog, 
        #dialog triggered in static/plugin_ajaxselect.js
        
        
        
        dialog = DIV('', _id = form_name)
        #assemble these newly created components of the widget set,
        #leave out 'add new' button if desired
        if not self.adder:
            self.wrapper = span, refresh_a, dialog
        else:
            self.wrapper = span, refresh_a, adder, dialog

    def widget(self):
        """
        Main method to create the ajaxselect widget. Calls helper methods and returns
        the wrapper element containing all associated elements. This method doesn't
        take any arguments since they are all provided at class instantiation.
        """

        self.get_fieldset()

        self.build_info()

        self.create_widget()

        self.create_wrapper()

        return self.wrapper
