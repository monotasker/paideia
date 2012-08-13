# -*- coding: utf-8 -*-

if 0:
    from gluon import current, URL
    response, request, T = current.response, current.request, current.t

response.title = request.application
response.mobiletitle = request.application
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

if auth.has_membership('administrators', auth.user_id):
    response.menu+=[(T('Admin'), False, None,
        [
        (T('Reports'), False, None,
            (T('Users'), False, URL('listing', 'user')),
            (T('Paths'), False, URL('plugin_listandedit',
                                    'listing.html', args=['paths'])),
            (T('Steps'), False, URL('plugin_listandedit',
                                    'listing.html', args=['steps'])),
            (T('Quizzes'), False, URL('plugin_listandedit',
                                    'listing.html', args=['quizzes'])),
            (T('Tags'), False, URL('plugin_listandedit',
                                    'listing.html', args=['tags'])),
            (T('NPCs'), False, URL('plugin_listandedit',
                                    'listing.html', args=['npcs'])),
            (T('locations'), False, URL('plugin_listandedit',
                                    'listing.html', args=['locations'])),
            (T('images'), False, URL('plugin_listandedit',
                                    'listing.html', args=['images'])),
            (T('Bug reports'), False, URL('plugin_listandedit',
                                    'listing.html', args=['bugs'])),

        ),
        (T('Web IDE'), False, URL('admin', 'default', 'index')),
        (T('Database'), False, URL('appadmin', 'index')),
        ]
       )]
