# -*- coding: utf-8 -*-

if 0:
    from gluon import current, URL, SPAN
    response, request, T = current.response, current.request, current.t
    auth = current.auth

response.title = request.application
response.mobiletitle = request.application
response.subtitle = T('An online space for learning New Testament Greek')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ian W. Scott'
response.meta.description = 'An online space for learning New Testament Greek'
response.meta.keywords = \
                'Greek, koine, New Testament, language, education, learning'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011-2012, Ian W. Scott. Source' \
    'code available on <a href="https://github.com/monotasker/paideia">' \
    'GitHub</a>'


response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (SPAN(T('Map'), _class='icon-location'), False,
                                             URL('exploring', 'index'), []),
    (SPAN(T('Slides'), _class='icon-image'), False,
                                             URL('listing', 'slides'), [])
    ]

if auth.has_membership('administrators', auth.user_id):
    response.menu += [(SPAN(T('Admin'), _class='icon-gear'), False, None, [
            (T('Create'), False, None, [
                (T('Slide decks'), False, URL('editing',
                            'listing.html', args=['plugin_slider_decks'])),
                (T('Slides'), False, URL('editing',
                            'listing.html', args=['plugin_slider_slides'])),
                (T('Paths'), False, URL('editing',
                            'listing.html', args=['paths'])),
                (T('Steps'), False, URL('editing',
                            'listing.html', args=['steps'])),
                (T('Tags'), False, URL('editing',
                            'listing.html', args=['tags'])),
                (T('Badges'), False, URL('editing',
                            'listing.html', args=['badges'])),
                (T('Instructions'), False, URL('editing',
                            'listing.html', args=['step_instructions'])),
                (T('Hints'), False, URL('editing',
                            'listing.html', args=['step_hints'])),
                (T('NPCs'), False, URL('editing',
                            'listing.html', args=['npcs'])),
                (T('locations'), False, URL('editing',
                            'listing.html', args=['locations'])),
                (T('images'), False, URL('editing',
                            'listing.html', args=['images'])),
            ]),

            (T('Reports'), False, None, [
                (T('Users'), False, URL('listing', 'user')),
                (T('Bug reports'), False, URL('editing',
                                        'listing.html', args=['bugs'])),
                (T('Paths by tag'), False, URL('reporting',
                                        'paths_by_tag')),
                (T('Attempt log'), False, URL('reporting',
                                        'attempts')),
            ]),
            (T('Web IDE'), False, URL('admin', 'default', 'index')),
            (T('Database'), False, URL('appadmin', 'index')),
        ])
        ]
