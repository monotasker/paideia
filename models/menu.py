# -*- coding: utf-8 -*-

from datetime import datetime
import os
# import traceback
if 0:
    from gluon import current, URL, SPAN, XML, A, I
    response, request, T = current.response, current.request, current.t
    auth = current.auth

"""
This file includes the menu content along with other meta content and global
layout settings
"""


# Versioning for updated static files ======================================
def version_file(filestring):
    '''
    Return a file path with an added version number in the file name.

    This is to help force browsers to re-download new versions of cached static
    files. It does not actually change the name of the referenced file. It
    simply returns a path with an alias for the filename. This must be paired
    with a rewriting script that serves the real file instead of the
    (non-existent) aliased file.
    '''
    am_on = False
    if am_on:
        filepath = os.path.join(request.env.web2py_path,
                                'applications/',
                                request.application,
                                'static/',
                                filestring)
        try:
            mtime = str(int(os.path.getmtime(filepath)))
            mypath, myname = filestring.split('/')
            namebase, namext = myname.split('.')
            newpath = os.path.join(mypath,
                                   '{}.{}.{}'.format(namebase, mtime, namext))
        except OSError, e:
            print e
            newpath = 'none'
    else:
        newpath = filestring
    return newpath


imports = {'d3': URL('static', 'js/d3.min.js'),
           'd3_infocharts': URL('static', 'js/info_chart1.js'),
           'datatables': 'https://cdn.datatables.net/v/bs/jszip-2.5.0/'
                         'dt-1.10.16/b-1.4.2/b-colvis-1.4.2/b-html5-1.4.2/'
                         'b-print-1.4.2/fc-3.2.3/fh-3.1.3/r-2.2.0/'
                         'datatables.min.js',
           'datatables_css': 'https://cdn.datatables.net/v/bs/jszip-2.5.0/'
                             'dt-1.10.16/b-1.4.2/b-colvis-1.4.2/b-html5-1.4.2/'
                             'b-print-1.4.2/fc-3.2.3/fh-3.1.3/r-2.2.0/'
                             'datatables.min.css',
           'pdfmake': 'https://cdnjs.cloudflare.com/ajax/libs/pdfmake/'
                      '0.1.32/pdfmake.min.js',
           'pdfmake_vfsfonts': 'https://cdnjs.cloudflare.com/ajax/libs/'
                               'pdfmake/0.1.32/vfs_fonts.js',
           }


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
                              'Ian W. Scott. Source code available on '
                              ''.format(datetime.now().year),
                              A('GitHub',
                                _href="https://github.com/monotasker/paideia"))
response.meta.google_verify = 'MlxOzReGJ8Y2vVC_V7HK9TLNiUUIabrt_Mt_m0D8MSc'

# Layout ===================================================================

response.left_sidebar_enabled = 0
response.right_sidebar_enabled = 0
response.fluid_layout = True

# Menu =====================================================================

response.menu = [(SPAN(I(_class='fa fa-home'),
                       SPAN('Home', _class='hidden-sm')),
                  False, URL('default', 'index'), []),
                 (SPAN(I(_class='fa fa-map-marker'),
                       SPAN('Map', _class='hidden-sm')),
                  False, URL('exploring', 'index'), []),
                 (SPAN(I(_class='fa fa-film'),
                       SPAN('Videos', _class='hidden-sm')),
                  False, URL('listing', 'slides'), []),
                 (SPAN(I(_class='fa fa-filter'),
                       SPAN('Vocabulary', _class='hidden-sm')),
                  False, URL('reporting', 'vocabulary.html'), [])
                 ]
m = response.menu

if auth.has_membership('administrators', auth.user_id) or \
        auth.is_impersonating():
    m += [(SPAN(I(_class='fa fa-cog'),
                SPAN('Admin', _class='hidden-sm')), False, None,
           [(SPAN(I(_class='fa fa-leaf fa-fw'), T(' Create'),
            _class='icon-leaf'), False, None,
             [(SPAN(I(_class='fa fa-film fa-fw'), T('Slide decks'),
               _class='icon-tasks'),
               False, URL('editing', 'listing.html',
                          args=['plugin_slider_decks'])),
              (SPAN(I(_class='fa fa-film fa-fw'), T('Slides'),
               _class='icon-film'),
               False, URL('editing', 'listing.html',
                          args=['plugin_slider_slides'],
                          vars={'orderby': 'slide_name'})),
              (SPAN(I(_class='fa fa-road fa-fw'), T('Paths'),
               _class='icon-road'),
               False, URL('editing', 'listing.html',
                          args=['paths'])),
              (SPAN(I(_class='fa fa-paw fa-fw'), T('Steps'),
               _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['steps'])),
              (SPAN(I(_class='fa fa-font fa-fw'), T('Lemmas'),
               _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['lemmas'],
                          vars={'orderby': 'lemma',
                                'collation': 'el'})),
              (SPAN(T(' Constructions'), _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['constructions'],
                          vars={'orderby': 'construction_label'})),
              (SPAN(I(_class='fa fa-comment fa-fw'), T('Word forms'),
               _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['word_forms'],
                          vars={'orderby': 'word_form',
                                'collation': 'el'})),
              (SPAN(I(_class='fa fa-tags fa-fw'), T('Tags'),
               _class='icon-tag'),
               False, URL('editing', 'listing.html',
                          args=['tags'],
                          vars={'orderby': 'tag'})),
              (SPAN(I(_class='fa fa-certificate fa-fw'), T('Badges'),
               _class='icon-certificate'),
               False, URL('editing', 'listing.html',
                          args=['badges'],
                          vars={'orderby': 'badge_name'})),
              (SPAN(I(_class='fa fa-info-circle fa-fw'), T('Instructions'),
               _class='icon-check'),
               False, URL('editing', 'listing.html',
                          args=['step_instructions'])),
              (SPAN(I(_class='fa fa-question-circle fa-fw'), T('Hints'),
               _class='icon-question'),
               False, URL('editing', 'listing.html',
                          args=['step_hints'])),
              (SPAN(I(_class='fa fa-user fa-fw'), T('NPCs'),
               _class='icon-group'),
               False, URL('editing', 'listing.html',
                          args=['npcs'])),
              (SPAN(I(_class='fa fa-map-marker fa-fw'), T('Locations'),
               _class='icon-screenshot'),
               False, URL('editing', 'listing.html',
                          args=['locations'])),
              (SPAN(I(_class='fa fa-users fa-fw'), T('Classes'),
               _class='icon-group'),
               False, URL('editing', 'listing.html',
                          args=['classes'])),
              (SPAN(I(_class='fa fa-picture-o fa-fw'), T('Images'),
               _class='icon-picture'),
               False, URL('editing', 'listing.html',
                          args=['images'])),
              ]),

            (SPAN(I(_class='fa fa-bar-chart fa-fw'), T('Reports')), False,
             None,
             [(SPAN(I(_class='fa fa-users fa-fw'), T('Users'),
              _class='icon-group'),
               False, URL('listing', 'user')),
              (SPAN(I(_class='fa fa-user fa-fw'), T('Individual user'),
               _class='icon-group'),
               False, URL('reporting', 'user',
                          args=[0])),
              (SPAN(I(_class='fa fa-tag fa-fw'), T('Untagged lemmas'),
               _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['lemmas'],
                          vars={'orderby': 'lemma',
                                'collation': 'el',
                                'restrictor': {'part_of_speech': None}})),
              (SPAN(I(_class='fa fa-tags fa-fw'), T('Untagged word forms'),
               _class='icon-plus-sign-alt'),
               False, URL('editing', 'listing.html',
                          args=['word_forms'],
                          vars={'orderby': 'word_form',
                                'collation': 'el',
                                'restrictor': {'construction': None}})),
              (SPAN(T(' Paths by tag'), _class='icon-tags'),
               False, URL('reporting', 'paths_by_tag')),
              (SPAN(I(_class='fa fa-list fa-fw'), T(' Attempt log'),
               _class='icon-list-alt'),
               False, URL('reporting', 'attempts')),
              (SPAN(I(_class='fa fa-frown-o fa-fw'), T('All exceptions'),
               _class='icon-frown'),
               False, URL('editing', 'listing.html',
                          args=['exceptions'])),
             (SPAN(I(_class='fa fa-frown-o fa-fw'),
              T(' Steps with Invld. Locs'), _class='icon-frown'),
              False, URL('editing', 'sil.html',
                         args=['stepsinvalidlocs'])),
             (SPAN(I(_class='fa fa-frown-o fa-fw'), T('Tags no badges'),
              _class='icon-frown'),
              False, URL('editing', 'tnb.html',
                         args=['tagsnobadges'])),
             (SPAN(I(_class='fa fa-frown-o fa-fw'),
              T(' Steps problem regexes'), _class='icon-frown'),
              False, URL('editing', 'pregex.html',
                         args=['stepsproblemregex'])),
              ]),

            (SPAN(I(_class='fa fa-cog fa-fw'), T('Utils'), _class='icon-cog'),
             False, None,
             [(SPAN(I(_class='fa fa-industry fa-fw'), T('Make paths'),
              _class='icon-cog'),
               False, URL('util', 'make_path')),
              (SPAN(I(_class='fa fa-thumbs-o-up fa-fw'), T('Test step regex'),
               _class='icon-cog'),
               False, URL('util', 'test_regex')),
              (SPAN(I(_class='fa fa-filter fa-fw'), T('Gather word forms'),
               _class='icon-cog'),
               False, URL('util', 'gather_word_forms')),
              (SPAN(T(' Bulk update'), _class='icon-cog'),
               False, URL('util', 'bulk_update')),
              (SPAN(T(' Print Select'), _class='icon-cog'),
               False, URL('plugin_utils', 'util',
               args=['print_rows_as_dicts'])),
              (SPAN(I(_class='fa fa-user fa-fw'), T('Impersonate'),
               _class='icon-cog'),
               False, URL('default', 'user', args=['impersonate'])),
              (SPAN(I(_class='fa fa-database fa-fw'), T('Export DB'),
               _class='icon-cog'),
               False, URL('util', 'export_db')),
              (SPAN(I(_class='fa fa-database fa-fw'), T('DB Backup'),
               _class='icon-cog'),
               False, URL('plugin_sqlite_backup', 'backup_db')),
              ]),

            (SPAN(I(_class='fa fa-code fa-fw'), T('Web IDE'),
             _class='icon-code'),
             False, URL('admin', 'default', 'index')),

            (SPAN(I(_class='fa fa-warning fa-fw'), T('Error reports'),
             _class='icon-frown'),
             False, URL('admin', 'default', 'errors/paideia')),

            (SPAN(I(_class='fa fa-database fa-fw'), T('Database'),
             _class='icon-sitemap'),
             False, URL('appadmin', 'index')),
            ])
          ]

if auth.has_membership('instructors', auth.user_id) or \
        auth.has_membership('administrators', auth.user_id) or \
        auth.is_impersonating():
    m += [(SPAN(I(_class='fa fa-university'),
                SPAN('Instructors', _class='hidden-sm')), False, None,
          [(SPAN(I(_class='fa fa-users fa-fw'), T('Class lists'),
                 _class='icon-group'),
            False, URL('listing', 'user')),
           (SPAN(I(_class='fa fa-question-circle fa-fw'), T('Student queries'),
            _class='icon-warning-sign'),
            False, URL('listing', 'queries')),
           (SPAN(I(_class='fa fa-list fa-fw'), T('All student step attempts'),
            _class='icon-list-alt'),
            False, URL('reporting', 'attempts')),
           ]
           )
          ]
