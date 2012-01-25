# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('An online space for learning New Testament Greek')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ian W. Scott'
response.meta.description = 'An online space for learning New Testament Greek'
response.meta.keywords = 'Greek, koine, New Testament, language, education, learning'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'


##########################################
## this is the main application menu
## add/remove items as required
##########################################

response.menu = [
    (T('Home'), False, URL('default','index'), [])
    ]

##########################################
## this is here to provide shortcuts
## during development. remove in production
##
## mind that plugins may also affect menu
##########################################

#########################################
## Make your own menus
##########################################

response.menu+=[(T('Admin'), False, None,
    [
    (T('Design'), False, URL('admin', 'default', 'index')),
    (T('Database'), False, URL('appadmin', 'index')),   
    (T('Users'), False, URL('listing', 'user')),
    (T('Questions'), False, URL('plugin_listandedit', 'list.html', args=['questions'])),
    (T('Quizzes'), False, URL('plugin_listandedit', 'list.html', args=['quizzes'])),
    (T('Tags'), False, URL('plugin_listandedit', 'list.html', args=['tags'])),
    ]
   )]
