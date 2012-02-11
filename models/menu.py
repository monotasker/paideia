# -*- coding: utf-8 -*-

if 0:
    from gluon import current, URL
    response, request, T = current.response, current.request, current.t

response.title = request.application
response.subtitle = T('An online space for learning New Testament Greek')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ian W. Scott'
response.meta.description = 'An online space for learning New Testament Greek'
response.meta.keywords = 'Greek, koine, New Testament, language, education, learning'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'


response.menu = [
    (T('Home'), False, URL('default','index'), [])
    ]

response.menu+=[(T('Admin'), False, None,
    [
    (T('Web IDE'), False, URL('admin', 'default', 'index')),
    (T('Database'), False, URL('appadmin', 'index')),   
    (T('Users'), False, URL('listing', 'user')),
    (T('Questions'), False, URL('plugin_listandedit', 'listing.html', args=['questions'])),
    (T('Quizzes'), False, URL('plugin_listandedit', 'listing.html', args=['quizzes'])),
    (T('Tags'), False, URL('plugin_listandedit', 'listing.html', args=['tags'])),
    (T('NPCs'), False, URL('plugin_listandedit', 'listing.html', args=['npcs'])),
    (T('locations'), False, URL('plugin_listandedit', 'listing.html', args=['locations'])),
    ]
   )]
