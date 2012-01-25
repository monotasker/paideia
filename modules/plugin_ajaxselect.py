from gluon import sqlhtml, current, SPAN, A, DIV
from gluon.custom_import import track_changes
from gluon.html import URL
from gluon.sqlhtml import OptionsWidget

session, request, response = current.session, current.request, current.response

response.files.append(URL('static','plugin_ajaxselect/plugin_ajaxselect.js'))

#TODO: set track changes to false when dev is finished
track_changes(True)

class AjaxSelect:
    """
    This plugin creates a select widget wrapped that can be refreshed via ajax without resetting
    the entire form. It also provides an "add new" button that allows users to add a new item to
    the table that populates the select widget via ajax. The widget is then automatically refreshed
    via ajax so that the new item is visible as a select option and can be chosen. All of this
    happens without a page or form refresh so that data entered in other fields is not lost or submitted.

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

    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 'authors', {optional argument}).widget()

    Note that the third argument passed to AjaxSelect should be the name of the
    table *referenced by the current field*. In this example, the field 'author'
    references the table 'authors'. So the third argument in this case is 'authors'.

    Optional arguments:
    refresher (True/False; defaults to True):a button to manually refresh the select
    widget via ajax.

    adder (True/False; defaults to True): a button to add a new record to the linked
        table that populates the select widget.

    restrictor ({form field name}): adds a dynamic constraint on the records displayed in the
    select widget. When the specified form field (within the same form) has its value
    changed, this select will be refreshed and its displayed records filtered
    accordingly. Note that this is only useful if {fieldname} references values shared
    with the linked table.
    
    e.g., to make the select constrain the widget for the 'works' table:
    db.notes.author.widget = lambda field, value: AjaxSelect(field, value, 'authors', restrictor='work').widget()

    """
    #TODO: Implement boolean adder switch
    #TODO: Change refresher hiding so that it is style based
    #TODO: allow for restrictor argument to take list and filter multiple other fields

    def __init__(self, field, value, linktable, refresher = True, restricted = "None", restrictor = "None"):
        self.field = field
        self.value = value
        self.linktable = linktable
        self.refresher = refresher
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

    def get_fieldset(self):
        #get field and tablenames for element id's
        fieldset = str(self.field).split('.')
        self.tablename = fieldset[0]
        self.fieldname = fieldset[1]

    def build_info(self):
        #build name for the span that will wrap the select widget
        self.wrappername = '%s_%s_loader' %(self.tablename, self.fieldname)

        #classes for wrapper span to indicate filtering relationships
        if self.restrictor == 'None':
            self.classes += ''
        else:
            self.classes += '%s restrictor for_%s' % (self.linktable, self.restrictor)

        #URL to reload widget via ajax
        self.comp_url = URL('plugin_ajaxselect', 'set_widget.load', args=[self.tablename, self.fieldname, self.value, self.linktable, self.wrappername])

        #URL to load form for linking table via ajax
        self.add_url = URL('plugin_ajaxselect', 'set_form_wrapper.load', args=[self.tablename, self.fieldname, self.value, self.linktable, self.wrappername])

    def create_widget(self):
        #create the select widget
        self.adder_id = '%s_add_trigger' % self.linktable
        self.refresher_id = '%s_refresh_trigger' % self.linktable
        self.w = OptionsWidget.widget(self.field, self.value)

    def create_wrapper(self):
        #create the span wrapper and place the select widget inside, along with buttons to add and refresh if necessary
        span = SPAN(self.w, _id=self.wrappername, _class = self.classes)
        refresher = A('refresh', _href=self.comp_url, _id=self.refresher_id, cid=self.wrappername)
        form_name= '%s_adder_form' % self.linktable
        adder = A('add new', _href=self.add_url, _id=self.adder_id, _class='add_trigger', cid=form_name)
        dialog = DIV('', _id=form_name)

        if not self.refresher:
            self.wrapper = span, adder, dialog
        else:
            self.wrapper = span, refresher, adder, dialog

    def widget(self):
        """
        Returns a select widget that can be refreshed (via Ajax) by clicking the
        accompanying button. This allows updating of the select's contents without
        refreshing the whole form.
        """

        self.get_fieldset()

        self.build_info()

        self.create_widget()

        self.create_wrapper()

        return self.wrapper
