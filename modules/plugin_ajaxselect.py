from gluon import current, SPAN, A, DIV, SQLFORM, INPUT, UL, LI
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget, MultipleOptionsWidget 
#TODO: add ListWidget as another option?

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
    2. In the web2py online ide (design view for your app) scroll to the bottom 
    section labeled "Plugins";
    3. At the bottom of that section is a widget to "upload plugin file". Click 
    "Browse".
    4. In the file selection window that opens, navigate to the downloaded 
    plugin file, select it, and click "open". The file selection window should 
    close.
    5. Click the "upload" button.
    The plugin should now be installed and ready to use.

    Usage:
    In a web2py model file, import this class and then apply it as
    the widget-factory for one or more db fields. To do this for a field named
    'author' from a table named 'notes' you would add this line somewhere in
    the model file:

    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 
    'authors', {optional arguments}).widget()

    Note that the third argument passed to AjaxSelect should be the name of the
    table *referenced by the current field*. In this example, the field 'author'
    references the table 'authors'. So the third argument in this case is 
    'authors'.

    Optional arguments:
    refresher (True/False; defaults to True):a button to manually refresh the 
    select widget via ajax.

    adder (True/False; defaults to True): a button to add a new record to the 
    linked table that populates the select widget.

    restrictor ({form field name}): adds a dynamic constraint on the records 
    displayed in the named field's widget. When the specified form field 
    (within the same form) has its value changed, this select will be refreshed 
    and its displayed records filtered accordingly. Note that this is only 
    useful if {fieldname} references values shared with the linked table.

    e.g., to make the select constrain the widget for the 'works' table:
    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 
    'authors', restrictor='work').widget()

    multi (basic/False; defaults to False): Instead of displaying a single 
    select widget, the 'basic' value displays a standard multiselect widget (an 
    html select widget with a size greater than 1). This will only work 
    properly if the database field type is defined as "list:reference" in the 
    model. 

    lister (False/'simple'/'editlinks'; defaults to False): 'normal' adds a 
    list of the widget's currently selected values below a multiselect widget. If 
    set to 'editlinks' these passive list items become links opening edit forms
    for the linked items in a modal window.

    """
    """TODO: Get restriction to happen on initial widget creation, not just 
    refresh maybe by moving all widget creation to the controller? but still 
    have to get restrictor field val
    TODO: allow for restrictor argument to take list and filter multiple other 
    fields"""

    def __init__(self, field, value, linktable, refresher = False, adder = True,
                 restricted = "None", restrictor = "None", multi = False, 
                 lister = False):
        
        session, request, response = current.session, current.request, current.response
        
        #arguments passed from instantiation in model
        self.field = field
        self.value = value
        #get name strings from field and value
        self.fieldset = str(self.field).split('.')
        
        #build name for the span that will wrap the select widget
        self.wrappername = '%s_%s_loader' % (self.fieldset[0], self.fieldset[1])

        self.linktable = linktable
        self.refresher = refresher
        self.adder = adder
        self.restricted = restricted
        self.restrictor = restrictor
        self.multi = multi
        self.lister = lister

        #use value stored in session if changes to widget haven't been sent to db
        if (self.wrappername in session) and (session[self.wrappername]):
            self.value = session[self.wrappername]
            print 'session value being used in module: '
            session[self.wrappername] = None
        else:
            print 'db value being used in module'
            session[self.wrappername] = None

        self.clean_val = self.value
        #remove problematic pipe characters or commas from the field value 
        #in case of list:reference fields
        if self.multi and isinstance(self.value, list):
            self.clean_val = '-'.join(map(str, self.value))
        print 'module self.value = ', self.value
        print 'module self.clean_val', self.clean_val


        #utility variables to pass information from one method to the next
        self.comp_url = ""
        self.add_url = ""
        self.adder_id = ""
        self.refresher_id = ""
        self.wrapper = ""
        self.w = ""
        self.classes = ""
        #vars (params) for urls
        self.uvars = dict(value = self.clean_val, 
                    linktable = self.linktable, 
                    wrappername = self.wrappername, 
                    refresher = self.refresher,
                    adder = self.adder,
                    restricted = self.restricted,
                    restrictor = self.restrictor,
                    multi = self.multi,
                    lister = self.lister
                    )
        #args for urls
        self.uargs = self.fieldset


    def build_info(self):
        """Prepare information to be used in building widget and associated 
        elements"""

        #create ids for the "refresh" and "add new" buttons
        self.adder_id = '%s_add_trigger' % self.linktable
        self.refresher_id = '%s_refresh_trigger' % self.linktable

        #classes for wrapper span to indicate filtering relationships
        if self.restrictor == 'None':
            self.classes += 'plugin_ajaxselect'
        else:
            self.classes += '%s restrictor for_%s' % (self.linktable, self.restrictor)

    def create_widget(self):       
        
        """create either a single select widget or multiselect widget"""
        if self.multi == 'basic':
            self.wrapper = [MultipleOptionsWidget.widget(self.field, self.value)]
        else:
            self.wrapper = [OptionsWidget.widget(self.field, self.value)]
        #hidden input to help send unsaved changes via ajax so that they're 
        #preserved through a widget refresh
        inputid = self.wrappername + '_input'
        self.wrapper.append(INPUT(_id = inputid, _name = inputid, _type = 'hidden', _value = ''))

    def add_taglist(self):

        self.wrapper.append(UL(self.add_tags(), _class = 'taglist'))

    def add_tags(self):
        db = current.db
        tags = []

        
        if self.lister == 'normal':
            for v in self.value:
                the_row = db(db[self.linktable].id == v).select().first()
                f = db[self.linktable]._format % the_row
                tags.append(LI(f, _class = 'tag'))

        elif self.lister == 'editlinks':
            try:
                form_name = '%s_editlist_form' % self.linktable
                print 'form_name is ', form_name

                for v in self.value:       
                    the_row = db(db[self.linktable].id == v).select().first()
                    f = db[self.linktable]._format % the_row
                    print 'formatstring is ', f
                    edit_trigger_id = '%s_editlist_trigger_%i' % (self.linktable, v)
                    print 'id is ', edit_trigger_id

                    tags.append(LI(A(f, _href=URL('plugin_ajaxselect', 'set_form_wrapper.load', 
                                                    args = self.uargs, vars = dict(id = str(v))),   
                                        _id = edit_trigger_id,
                                        _class = 'edit_trigger editlink tag', 
                                        cid = form_name), _class = 'editlink tag'))
                tags.append(DIV('', _id = form_name))
            except Exception, err:
                print 'error in module add_tags(): ', err

        return tags

    def add_extras(self):

        #prepare to hide 'refresh' button via CSS if necessary
        if self.refresher is False:
            rstyle = 'display:none'
        else:
            rstyle = ''

        #URL to refresh widget via ajax
        self.comp_url = URL('plugin_ajaxselect', 'set_widget.load', 
                            args = self.uargs, vars = self.uvars)
        #URL to load form for linking table via ajax
        self.add_url = URL('plugin_ajaxselect', 'set_form_wrapper.load',
                           args = self.uargs, vars = self.uvars)

        #create 'refresh' button
        refresh_a = A('r', _href = self.comp_url, 
                      _id = self.refresher_id, 
                      _class = 'refresh_trigger',
                      cid = self.wrappername, 
                      _style = rstyle)

        #append the 'refresh' button to the wrapper object
        self.wrapper.append(refresh_a)

        if self.adder:
            #create name for form to create new entry in linked table
            form_name = '%s_adder_form' % self.linktable
            #create 'add new' button to open form
            add_a = A('+', _href = self.add_url, _id = self.adder_id, 
                  _class = 'add_trigger', cid = form_name)       
            #create hidden div to hold form (to be displayed via modal dialog, 
            #dialog triggered in static/plugin_ajaxselect.js
            dialog = DIV('', _id = form_name)

            self.wrapper.append(add_a)
            self.wrapper.append(dialog)


    def widget(self):
        """
        Main method to create the ajaxselect widget. Calls helper methods and returns
        the wrapper element containing all associated elements. This method doesn't
        take any arguments since they are all provided at class instantiation.
        """

        self.build_info()

        self.create_widget()

        self.add_extras()

        if self.lister:
            self.add_taglist()
        else:
            print 'no list asked for'

        self.wrapper[0] = SPAN(self.wrapper[0], _id = self.wrappername, _class = self.classes)

        return self.wrapper

    def refresh(self):
        """
        Method to re-create widget (without ancillary buttons and dialogs) 
        on ajax refresh
        """

        self.create_widget()

        return self.wrapper
