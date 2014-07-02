#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Developed by Paolo Caruccio ( paolo.caruccio66@gmail.com )
Released under web2py license
version 1 rev.201312222030

Description
-----------
This package applies to some standard elements of web2py the bootstrap3 theme.
Current version covers: the auth navbar, the menus and SQLFORM
Supported version of bootstrap framework: 3.0.2+
Working since Version 2.8.2-stable+timestamp.2013.12.17.16.49.17 of web2py
Tested with python 2.7.6 and the following browsers:
    - Chrome 31.0.1650.63
    - Firefox 26.0
    - Opera 12.16 Build 1860
    - IE 10
    - IE 9
    - IE 8

Package content and requirements
--------------------------------
The package includes:
    - bootstrap3.py
    - web2py-bootstrap3.css
    - web2py-bootstrap3.js
    - example of layout.html (inspired to web2py welcome application)

The bundle doesn't include the framework files. You must download them from
http://getbootstrap.com/

Moreover, bootstrap3 to work in IE8 requires the use of 'respond.js'.
In the example layout this file is linked to a CDN repository but if you
have to use the web2py app offline and your browser is IE8, please download
it from https://github.com/scottjehl/Respond and put it in
"static/js" folder of your application and follow the comment you find in the 
head section of the 'layout.html' example.
For more details on bootstrap3 browsers support you should check
http://getbootstrap.com/getting-started/#browsers

Installation and usage
----------------------
- put the python module in "modules" folder of your w2p-app (you should restart
  web2py to load the module)
- in "static" folder of your w2p-app put 'web2py-bootstrap3.css' in "css"
  sub-folder and 'web2py-bootstrap.js' in the "js" folder
- replace the 'layout.html' in views folder of your w2p-app
  with that in this package
- download and uncompress the framework files in the static folder
  of your w2p-app
- in a model add the following code lines:

    # bootstrap3 theme for web2py
    from gluon import current
    current.auth = auth
    import bootstrap3 as bs3

- code your views by using the bootstrap3 framework guidelines
 (see more at http://getbootstrap.com/getting-started/)
- call menu with "bs3.menu()" and auth_navbar with "bs3.navbar()",
  set the SQLFORM formstyle to "bs3.form()"

Auth navbar
-------------
The navbar is fully customizable: you can change the text and icon for auth
items, add dividers and add your own items, set the order of the items
to your need and taste.
You can call it in your view or controller simply with:

                            bs3.navbar()

Menu navigation
---------------
If you want a response.menu navbar use in your view or controller:

                            bs3.menu()

If instead you want a navbar with your custom items, you can pass a list (build
like response.menu) as 'menu_list' argument:

      my_nav = [['Home', True, URL('index')],['Page', False, URL('link')]]
      bs3.menu(menu_list=my_nav)

Sometimes you want a list of links displayed by tabs:

                  bs3.menu(menu_type='tabs', menu_list=my_nav)

or pills:

                  bs3.menu(menu_type='pills', menu_list=my_nav)

If you need to add bootstrap3 classes to the menu you can use the argument
'add_classes' of the function. For example:

      bs3.menu(menu_type='tabs',add_classes='justified',menu_list=my_nav)

returns a tabbed menu justified (tabs have equal widths of their parent), while

      bs3.menu('pills','nav-stacked pull-right',my_nav)

returns a pills navigation stacked and right floated.

Forms
-----
To render a SQLFORM as a bootstrap3 form you can set its formstyle argument to:

                            bs3.form()

In this case the label will be over the input:

                            label |
                            input

For a label and input on the same line you can pass 'horizontal' as
first argument:

                  bs3.form(layout='horizontal')

                         label | input

It's possible display an inline forms (the label is rendered as input's
placeholder) by passing "layout = 'inline'" to the function :

                     bs3.form('inline')

The function has a second argument for styling checkboxes and radio widgets
(default is 'inline'):

                  bs3.form(rc_mode='inline')
                 
           checkbox 1 | checkbox 2 | checkbox 3

                  bs3.form(rc_mode='stacked')

                       checkbox 1 |
                       checkbox 2 |
                       checkbox 3

for example:

                bs3.form('horizontal','stacked')

returns a form where the labels are inline with their control and 
checkboxex/radioboxes widget has inputs stacked.

To add buttons to the form in runtime, you should use the function:

                  bs3.add_button(form, value, url, _class)

The mandatory arguments of the above function are:
    - form (the form to which append the button)
    - value (the button text)
    - url (the action's url)

The last argument is optional. Set it if you need a different class
than 'btn btn-default' one.

If you need to insert dynamically into the form an extra row, you should use:
                
      bs3.build_row(id, label, control, comment, form, layout, rc_mode) 

The mandatory arguments of the above function are:
    - id (the row id)
    - label (the row label)
    - control (the row widget)
    - comment (the row comment)

'layout' and 'rc_mode' arguments are optional.

To apply the bootstrap3 formstyle to auth forms you should set:

            auth.settings.formstyle = bs3.form()

Form-horizontal bootstrap3 settings
-----------------------------------
The default settings are:

    - for the label "col-md-4"
    - for the control wrapper "col-md-8"

These settings can be changed in "bootstrap3.py" and in "web2py-bootstrap3.js"
by modifying the values of:

    - FH_CL_PREFIX
    - FH_LABEL_COLW
    - FH_CONTROL_COLW

License
-------
bootstrap3.py is released under web2py license 
(http://www.web2py.com/init/default/license), while
web2py-bootstrap3.css and web2py-bootstrap3.js are released under the MIT
license (a copy is included in the package).

"""


from gluon import *
from gluon.languages import lazyT
from numbers import Number


FH_CL_PREFIX = 'col-md-'
FH_LABEL_COLW = '4'
FH_CONTROL_COLW = '8'  # 12 - FH_LABEL_COLW


def navbar():
    ''' full customizable auth navbar
    
    '''

    bar = current.auth.navbar(mode='bare')
    [li_login, li_register, li_request_reset_password, li_retrieve_username,
     li_logout, li_profile, li_change_password] = [None for n in xrange(7)]

    # text and icons for auth items in the drop-down
    ## text for dropdown toggle
    default_text = current.T('Login')
    ## login
    ico_login = 'glyphicon glyphicon-off'
    txt_login = current.T('Login')
    ## register
    ico_register = 'glyphicon glyphicon-user'
    txt_register = current.T('Register')
    ## password reset
    ico_request_reset_password = 'glyphicon glyphicon-lock'
    txt_request_reset_password = current.T('Lost password?')
    ## username retrieve
    ico_retrieve_username = 'glyphicon glyphicon-lock'
    txt_retrieve_username = current.T('Forgot username?')
    ## logout
    ico_logout = 'glyphicon glyphicon-off'
    txt_logout = current.T('Logout')
    ## profile
    ico_profile = 'glyphicon glyphicon-user'
    txt_profile = current.T('Profile')
    ## password change
    ico_change_password = 'glyphicon glyphicon-lock'
    txt_change_password = current.T('Password')

    # divider
    li_divider = LI(_class='divider')

    # not auth items (add your own)
    ## below some examples
    ico0 = 'glyphicon glyphicon-info-sign'
    txt0 = current.T('About')
    href0 = URL(current.request.controller, 'about')
    li_about = LI(A(I(_class=ico0), ' ', txt0, _href=href0, _rel='nofollow'))
    ## ----------------
    ico1 = 'glyphicon glyphicon-book'
    txt1 = current.T('Help')
    href1 = URL(current.request.controller, 'help')
    li_help = LI(A(I(_class=ico1), ' ', txt1, _href=href1, _rel='nofollow'))

    # auth items builder
    for k, v in bar.iteritems():
        if k == 'user':
            welcome_text = '%s %s' % (bar['prefix'], bar['user'])
            toggletext = default_text if v is None else welcome_text
        elif k == 'login':
            ico = ico_login
            txt = txt_login
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_login = res
        elif k == 'register':
            ico = ico_register
            txt = txt_register
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_register = res
        elif k == 'request_reset_password':
            ico = ico_request_reset_password
            txt = txt_request_reset_password
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_request_reset_password = res
        elif k == 'retrieve_username':
            ico = ico_retrieve_username
            txt = txt_retrieve_username
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_retrieve_username = res
        elif k == 'logout':
            ico = ico_logout
            txt = txt_logout
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_logout = res
        elif k == 'profile':
            ico = ico_profile
            txt = txt_profile
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_profile = res
        elif k == 'change_password':
            ico = ico_change_password
            txt = txt_change_password
            res = LI(A(I(_class=ico), ' ', txt, _href=v, _rel='nofollow'))
            li_change_password = res

    # dropdown toggle
    toggle = A(toggletext, ' ', B('', _class='caret'),
               _href='#',
               _class='dropdown-toggle',
               _rel='nofollow',
               **{'_data-toggle': 'dropdown'})

    # set the order of items in the drop-down and add dividers
    ul = [li_register,
          li_profile,
          li_request_reset_password,
          li_change_password,
          li_retrieve_username,
          li_divider,
          li_login,
          li_logout,
          li_divider,
          li_about,
          li_help
          ]

    # dropdown
    dropdown = UL(*[li for li in ul if li is not None],
                  _class='dropdown-menu', _role='menu', _id='w2p-auth-bar')

    # navbar
    navbar = LI(toggle, dropdown, _class='dropdown',
                **{'_data-w2pmenulevel': 'l0'})

    return navbar


def menu(menu_type=None, add_classes=None, menu_list=None):
    ''' possible options:
    menu type
        - navbar (default)
        - pills
        - tabs

    additional classes
        - all the bootstrap 3 classes appliable to nav (for example
          "pull-right", "nav-stacked" and so on

    menu_list is a list of lists like response.menu

    '''

    menu_class = ('nav-%s' % menu_type if menu_type in ('pills', 'tabs')
                  else 'navbar-nav')

    if add_classes and isinstance(add_classes, basestring):
        menu_class += ' %s' % add_classes
    
    current_menu = current.response.menu if not menu_list else menu_list

    menu = MENU(current_menu,
                _class='nav %s' % menu_class,
                li_class='dropdown',
                ul_class='dropdown-menu')

    return menu


def add_button(form, value, url, _class='btn btn-default'):
    ''' add buttons to the bs3 form
        This function overrides that one in gluon/html.py

    '''

    REDIRECT_JS = 'window.location="%s";return false'
    submit = form.element(_type='submit')
    submit.parent.append(
        CAT(TAG['button'](value, _class=_class, _type='button',
                          _onclick=url if url.startswith('javascript:') else
                          REDIRECT_JS % url), XML('&nbsp;')))


def build_row(id, label, control, comment, form,
              layout=None, rc_mode='inline'):
    ''' form row builder
    
    '''

    fh_label_class = '%s%s' % (FH_CL_PREFIX, FH_LABEL_COLW)
    fh_offest_class = '%soffset-%s' % (FH_CL_PREFIX, FH_LABEL_COLW)
    fh_control_class = '%s%s' % (FH_CL_PREFIX, FH_CONTROL_COLW)

    if not id.startswith('submit_record'):
        # form controls
        if isinstance(label, (basestring, lazyT)):
            clabel = LABEL(label)
            if not label and layout != 'horizontal':
                clabel = CAT('')
            label = clabel

        if control is None:
            # make the control as an empty string
            control = ''

        if isinstance(control, (basestring, lazyT)):
            # string
            control = P(control, _class='form-control-static')
        elif isinstance(control, Number):
            # number
            control = P(str(control), _class='form-control-static')
        elif isinstance(control, INPUT):
            ctrl_cls = None
            control_type = control.attributes.get('_type')
            if control_type not in ('checkbox', 'radio', 'file'):
                ctrl_cls = 'form-control'
                if isinstance(control, TEXTAREA):
                    # textarea
                    control['_rows'] = '3'
            elif control_type == 'file':
                # file input
                if layout == 'horizontal':
                    ctrl_cls = 'form-control-static'
            elif control_type in ('checkbox', 'radio'):
                # checkbox/radio input
                if form.readonly:
                    control['_disabled'] = 'disabled'
                clabel = label[0]
                label = LABEL('') if layout == 'horizontal' else CAT('')
                control = DIV(LABEL(control, clabel),
                              _class=control['_type'])
            if ctrl_cls:
                control.add_class(ctrl_cls)
        elif isinstance(control, SPAN):
            # static text
            control = P(control[0])
            control.add_class('form-control-static')
        elif isinstance(control, A):
            # link
            if layout == 'horizontal':
                label = LABEL(label)
            control.add_class('btn btn-default')
            control['_role'] = 'button'
            if layout not in ('horizontal','inline'):
                control = P(control)
        elif isinstance(control[0], UL) and control[0]['_class'] == 'w2p_list':
            # listwidget
            control = control[0]
            for c in control:
                if isinstance(c[0], INPUT):
                    c[0].add_class('form-control')
            control.add_class('list-unstyled')
        elif (isinstance(control[0], INPUT)
              and control[0]['_autocomplete'] == 'off'
              and control[-1]['_id'].startswith('_autocomplete_')):
            # autocompletewidget
            control[0].add_class('form-control')
            control = P(control, _class='w2p-autocomplete-widget')
        elif (isinstance(control, (TABLE, DIV)) and
              control.attributes.get('_class') and
             ('web2py_radiowidget' in control['_class'] or
              'web2py_checkboxeswidget' in control['_class'])):
            # radiowidget/checkboxeswidget
            labels = [l for l in control.elements('label')]
            mode = rc_mode if rc_mode == 'stacked' else 'inline'
            group = []
            for n, input in enumerate(control.elements('input')):
                itype = input.attributes.get('_type')
                if itype in ('checkbox', 'radio'):
                    if form.readonly:
                        input['_disabled'] = 'disabled'
                    if mode == 'inline':
                        group_class = '%s-%s' % (itype, mode)
                        group_element = LABEL(input,
                                              labels[n][0],
                                              _class=group_class)
                    else:
                        group_element = LI(LABEL(input,
                                                 labels[n][0]),
                                           _class=itype)
                else:
                    group_element = input
                group.append(group_element)
            control = (UL(*group, _class='rc_container list-unstyled')
                       if mode != 'inline'
                       else CAT(DIV(*group, _class='rc_container')))
        elif (isinstance(control, DIV) and
              isinstance(control[0], INPUT) and
              '_type' in control[0].attributes and
              control[0]['_type'] == 'file' and
              isinstance(control[1], SPAN) and
              isinstance(control[1][1], A)):
              # UploadWidget
            file_inp = control[0]
            file_inp['_style'] = 'display:none;'
            file_link = control[1][1]
            delete_box = False
            has_image = False
            if control[1][2] == '|':
                delete_box = True
                del_inp = control[1][3]
                del_inp['_style'] = 'opacity:0;'
                delete_lbl = control[1][4]
            if isinstance(control[-1], IMG):
                has_image = True
                image_preview = control[-1]
            if has_image:
                file_repr = IMG(_src=image_preview['_src'],
                                _alt='thumbnail',
                                _id='image-thumb',
                                _class='img-thumbnail')
            else:
                file_repr = SPAN(file_link[0])
            file_link = CAT(A(file_repr,
                              _href=file_link['_href'],
                              _class='w2p-file-preview'),
                            SPAN(current.T('no file'),
                                 _id='no-file',
                                 _style='display:none;'))
            edit_btn_class = 'btn btn-default dropdown-toggle'
            edit_btn = TAG['button'](current.T('edit'), ' ',
                                     SPAN(_class='caret'),
                                     _type='button',
                                     _class=edit_btn_class,
                                     **{'_data-toggle': 'dropdown'})
            drop_down = UL(LI(A(current.T(delete_lbl[0]),
                                _href='#',
                                _id='delete-file-option')),
                           LI(A(current.T('change'),
                                _href='#',
                                _id='change-file-option')),
                           _class='dropdown-menu',
                           _role='menu')
            edit_btn_dd = DIV(edit_btn,
                              drop_down,
                              _id='edit-btn-dd',
                              _class='btn-group')
            file_reset_btn = TAG['button'](current.T('reset'),
                                           _id='file-reset-btn',
                                           _type='button',
                                           _class='btn btn-default',
                                           _style='display:none;')
            control = CAT(DIV(file_inp,
                              file_link,
                              del_inp,
                              edit_btn_dd,
                              file_reset_btn,
                              _class='w2p-uploaded-file'))
        else:
            # widget not implemented
            print "row '%s': widget not implemented" % id

        if layout == 'horizontal':
            label_bs3_class = '%s control-label' % fh_label_class
            comment_class = 'help-block %s %s' % (fh_offest_class,
                                                  fh_control_class)
            control = DIV(control, _class=fh_control_class)
        elif layout == 'inline':
            control['_placeholder'] = label[0]
            label_bs3_class = 'sr-only'
            comment_class = 'sr-only'
        else:
            label_bs3_class = 'control-label'
            comment_class = 'help-block'

        ### label
        if label:
            label.add_class(label_bs3_class)

        ### comment
        if comment:
            comment = SPAN(comment, _class=comment_class)

        form_row = DIV(label, control, comment, _id=id, _class='form-group')
    else:  # form buttons
        if not len(control):
            # if the buttons are not wrapped in a DIV
            # (i.e. form buttons attribute) then we have to wrap them
            control = CAT(control)
        inputs = []
        first_btn = True
        for n, input in enumerate(control):
            btn_class = 'btn-primary' if first_btn else 'btn-default'
            input_type = input.attributes.get('_type')
            if isinstance(input, INPUT):
                # input tag
                if input_type in('button', 'submit', 'reset'):
                    first_btn = False
                    btn_id = input.attributes.get('_id')
                    js_click = input.attributes.get('_onclick')
                    input.add_class('bs3-form-btn btn %s' % btn_class)
                    button = TAG['button'](input['_value'],
                                           _type=input_type,
                                           _onclick=js_click,
                                           _class=input['_class'],
                                           _id=btn_id)
                elif input_type == 'image':
                    first_btn = False
                    input.add_class('bs3-form-btn btn %s' % btn_class)
                    button = input
                else:
                    # it isn't a button
                    input.add_class('form-control')
                    button = input
            elif input_type in ('button', 'submit', 'reset'):
                # 'button' tag
                first_btn = False
                input.add_class('bs3-form-btn btn %s' % btn_class)
                button = input
            elif isinstance(input, A):
                # anchor tag as a button
                first_btn = False
                input.add_class('bs3-form-btn btn %s' % btn_class)
                input['_role'] = 'button'
                button = input
            else:
                button = input
            inputs.extend([button, XML('&nbsp;')])

        buttons = (CAT(*inputs)
                   if layout != 'horizontal'
                   else DIV(CAT(*inputs),
                            _class='%s %s' % (fh_offest_class,
                                              fh_control_class)))

        form_row = DIV(buttons, _class='form-group', _id=id)

    return form_row


def form(layout=None, rc_mode='inline'):
    ''' formstyle for SQLFORM

    '''

    def style(form, fields):

        parent = CAT()
        form_group = None

        for id, label, widget, comment in fields:
            form_group = build_row(id, label, widget, comment,
                                   form, layout, rc_mode)
            parent.append(form_group)

        form_classes = ('bs3-form form-%s' % layout if layout in ('horizontal',
                                                                  'inline')
                        else 'bs3-form')

        form.add_class(form_classes)
        form['_role'] = 'form'

        return parent

    return style
