# -*- coding: utf-8 -*-

if 0:
    from gluon import current, URL, SPAN, XML, A
    response, request, T = current.response, current.request, current.t
    auth = current.auth
from datetime import datetime

"""
This file includes the menu content along with other meta content and global
layout settings
"""

# Meta =====================================================================

# assemble page title
parts = [c.capitalize() for c in [response.title,
                                  request.controller,
                                  request.function]
         if c and c not in ['default', 'index']]
mytitle = ' | '.join(parts)
if request.args:
    mytitle = ' | '.join([', '.join(request.args), mytitle])

response.title = request.application
response.pagetitle = mytitle
response.mobiletitle = mytitle
response.subtitle = T('Learning New Testament Greek in Context')
response.homeurl = URL('default', 'index')

# http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Ian W. Scott'
response.meta.description = 'An online, interactive course in ' \
                            'New Testament Greek'
response.meta.keywords = 'Greek, koine, New Testament, language, ' \
                         'education, learning'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = XML('All content copyright &copy; 2011-{}, '
                              'Ian W. Scott. Source code available on '.format(datetime.now().year),
                              A('GitHub', _href="https://github.com/monotasker/paideia"))
response.meta.google_verify = 'MlxOzReGJ8Y2vVC_V7HK9TLNiUUIabrt_Mt_m0D8MSc'

# Layout ===================================================================

response.left_sidebar_enabled = 0
response.right_sidebar_enabled = 0
response.fluid_layout = True

# Menu =====================================================================

response.menu = [(SPAN(T(' Home'), _class='icon-home'),
                  False, URL('default', 'index'), []),
                 (SPAN(T(' Map'), _class='icon-map-marker'),
                  False, URL('exploring', 'index'), []),
                 (SPAN(T(' Slides'), _class='icon-picture'),
                  False, URL('listing', 'slides'), []),
                 (SPAN(T(' Vocabulary'), _class='icon-picture'),
                  False, URL('reporting', 'vocabulary.html'), [])
                 ]
m = response.menu

if auth.has_membership('administrators', auth.user_id) or auth.is_impersonating():
    m += [(SPAN(T(' Admin'), _class='icon-cog'), False, None,
           [(SPAN(T(' Create'), _class='icon-leaf'), False, None,
             [(SPAN(T(' Slide decks'), _class='icon-tasks'),
               False, URL('editing', 'listing.html', args=['plugin_slider_decks'])),
              (SPAN(T(' Slides'), _class='icon-film'),
               False, URL('editing', 'listing.html',
                          args=['plugin_slider_slides'],
                          vars={'orderby': 'slide_name'})),
              (SPAN(T(' Paths'), _class='icon-road'),
               False, URL('editing', 'listing.html',
                          args=['paths'])),
              (SPAN(T(' Steps'), _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['steps'])),
              (SPAN(T(' Lemmas'), _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['lemmas'],
                          vars={'orderby': 'lemma'})),
              (SPAN(T(' Constructions'), _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['constructions'],
                          vars={'orderby': 'construction_label'})),
              (SPAN(T(' Word forms'), _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['word_forms'],
                          vars={'orderby': 'word_form'})),
              (SPAN(T(' Tags'), _class='icon-tag'),
               False, URL('editing', 'listing.html',
                          args=['tags'],
                          vars={'orderby': 'tag'})),
              (SPAN(T(' Badges'), _class='icon-certificate'),
               False, URL('editing', 'listing.html',
                          args=['badges'],
                          vars={'orderby': 'badge_name'})),
              (SPAN(T(' Instructions'), _class='icon-check'),
               False, URL('editing', 'listing.html',
                          args=['step_instructions'])),
              (SPAN(T(' Hints'), _class='icon-question'),
               False, URL('editing', 'listing.html',
                          args=['step_hints'])),
              (SPAN(T(' NPCs'), _class='icon-group'),
               False, URL('editing', 'listing.html',
                          args=['npcs'])),
              (SPAN(T(' Locations'), _class='icon-screenshot'),
               False, URL('editing', 'listing.html',
                          args=['locations'])),
              (SPAN(T(' Classes'), _class='icon-group'),
               False, URL('editing', 'listing.html',
                          args=['classes'])),
              (SPAN(T(' Images'), _class='icon-picture'),
               False, URL('editing', 'listing.html',
                          args=['images'])),
              ]),

            (SPAN(T(' Reports'), _class='icon-bar-chart'), False, None,
             [(SPAN(T(' Users'), _class='icon-group'),
               False, URL('listing', 'user')),
              (SPAN(T(' Individual user'), _class='icon-group'),
               False, URL('reporting', 'user',
                          args=[0])),
              (SPAN(T(' New Bug reports'), _class='icon-warning-sign'),
               False, URL('editing', 'listing.html',
                          args=['bugs'],
                          vars={'restrictor': {'bug_status': 5}})),
              (SPAN(T(' Confirmed Bug reports'), _class='icon-stethoscope'),
               False, URL('editing', 'listing.html',
                          args=['bugs'],
                          vars={'restrictor': {'bug_status': 1}})),
              (SPAN(T(' All Bug reports'), _class='icon-frown'),
               False, URL('editing', 'listing.html',
                          args=['bugs'])),
              (SPAN(T(' Unparsed word forms'), _class='icon-warning-sign'),
               False, URL('editing', 'listing.html',
                          args=['word_forms'],
                          vars={'restrictor': {'construction': None}})),
              (SPAN(T(' Paths by tag'), _class='icon-tags'),
               False, URL('reporting', 'paths_by_tag')),
              (SPAN(T(' Attempt log'), _class='icon-list-alt'),
               False, URL('reporting', 'attempts')),
              (SPAN(T(' All Exceptions'), _class='icon-frown'),
               False, URL('editing', 'listing.html',
                          args=['exceptions'])),
             (SPAN(T(' Steps with Invld. Locs'), _class='icon-frown'),
               False, URL('editing', 'sil.html',
                          args=['stepsinvalidlocs'])),
             (SPAN(T(' Tags No Badges'), _class='icon-frown'),
               False, URL('editing', 'tnb.html',
                          args=['tagsnobadges'])),
             (SPAN(T(' Steps Problem Regexes'), _class='icon-frown'),
               False, URL('editing', 'pregex.html',
                          args=['stepsproblemregex'])),
              ]),

            (SPAN(T(' Utils'), _class='icon-cog'), False, None,
             [(SPAN(T(' Make paths'), _class='icon-cog'),
               False, URL('util', 'make_path')),
              (SPAN(T(' Test step regex'), _class='icon-cog'),
               False, URL('util', 'test_regex')),
              (SPAN(T(' Bulk update'), _class='icon-cog'),
               False, URL('util', 'bulk_update')),
              (SPAN(T(' Print Select'), _class='icon-cog'),
               False, URL('plugin_utils', 'util', args=['print_rows_as_dicts'])),
              (SPAN(T(' Impersonate'), _class='icon-cog'),
               False, URL('default', 'user', args=['impersonate'])),
              (SPAN(T(' Export DB'), _class='icon-cog'),
               False, URL('util', 'export_db')),
              (SPAN(T(' DB Backup'), _class='icon-cog'),
               False, URL('plugin_sqlite_backup', 'backup_db')),
              ]),
            (SPAN(T(' Web IDE'), _class='icon-code'),
             False, URL('admin', 'default', 'index')),
            (SPAN(T(' Error reports'), _class='icon-frown'),
             False, URL('admin', 'default', 'errors/paideia')),
            (SPAN(T(' Database'), _class='icon-sitemap'),
             False, URL('appadmin', 'index')),
            ])
          ]
