# -*- coding: utf8 -*-

from plugin_ajaxselect import AjaxSelect
from itertools import chain
import datetime
import os
#import re

if 0:
    from gluon import URL, current, Field, IS_IN_DB, IS_NOT_IN_DB, SQLFORM
    from gluon import IS_EMPTY_OR
    response = current.response
    request = current.request
    auth = current.auth
    db = current.db

#js file necessary for AjaxSelect widget
#TODO: move these to an AjaxSelect model file
response.files.insert(5, URL('static',
                      'plugin_ajaxselect/plugin_ajaxselect.js'))
response.files.insert(6, URL('static',
                      'plugin_framework/js/jquery-ui-1.10.3.custom/js/jquery-ui-1.10.3.custom.min.js'))
#response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.css'))

dtnow = datetime.datetime.utcnow()


#TODO: Fix this regex validator
#class IS_VALID_REGEX(object):
    #"""
    #custom validator to check regex in step definitions against the given
    #readable responses.
    #"""
    #def __init__(self):
        #self.error_message = 'Given answers do not satisfy regular expression.'

    #def __call__(self, value):
        #request = current.request
        #answers = request.vars.readable_response
        #alist = answers.split('|')
        #regex = value.encode('string-escape')
        #for a in alist:
            #if re.match(a.strip(), regex, re.I):
                #print a.strip()
                #print 'it matched!'
            #else:
                #print 'answer ', a, ' did not match the regex provided.'
                #print regex
                #return (value, self.error_message)
        #return (value, None)

db.define_table('classes',
                Field('institution', 'string', default='Tyndale Seminary',
                      unique=True),
                Field('academic_year', 'integer', default=dtnow.year),  # was year (reserved term)
                Field('term', 'string'),
                Field('course_section', 'string'),
                Field('instructor', 'reference auth_user', default=auth.user_id),
                Field('start_date', 'datetime'),
                Field('end_date', 'datetime'),
                Field('paths_per_day', 'integer', default=40),
                Field('days_per_week', 'integer', default=5),
                Field('members', 'list:reference auth_user'),
                format='%(institution)s, %(academic_year)s %(term)s '
                       '%(course_section)s %(instructor.last_name)s, '
                       '%(instructor.first_name)s'
                )

db.define_table('images',
    Field('image', 'upload', length=128,
          uploadfolder=os.path.join(request.folder, "static/images")),
    Field('title', 'string', length=256),
    Field('description', 'string', length=256),
    format='%(title)s')

db.define_table('audio',
    Field('clip', 'upload', length=128,
          uploadfolder=os.path.join(request.folder, "static/audio")),
    Field('clip_ogg', 'upload', length=128,
          uploadfolder=os.path.join(request.folder, "static/audio")),
    Field('title', 'string', length=256),
    Field('description', 'string', length=256),
    format='%(title)s')

db.define_table('journals',
    Field('name', db.auth_user, default=auth.user_id),
    Field('journal_pages', 'list:reference journal_pages'),  # was pages (reserved term)
    format='%(name)s')
db.journals.name.requires = IS_NOT_IN_DB(db, 'journals.name')

db.define_table('journal_pages',
    Field('journal_page', 'text'),  # was page (reserved term)
    format='%(page)s')

db.define_table('categories',
    Field('category', unique=True),
    Field('description'),
    format='%(category)s')

db.define_table('tags',
    Field('tag', 'string', unique=True),
    Field('tag_position', 'integer'),  # was position (reserved term)
    Field('slides', 'list:reference plugin_slider_decks'),
    format=lambda row: row['tag'])

db.tags.tag.requires = IS_NOT_IN_DB(db, 'tags.tag')

db.tags.slides.requires = IS_IN_DB(db,
                                   'plugin_slider_decks.id',
                                   '%(deck_name)s',
                                   multiple=True)
db.tags.slides.widget = lambda field, value: \
                                    AjaxSelect(field, value,
                                               indx=1,
                                               refresher=True,
                                               multi='basic',
                                               lister='simple',
                                               orderby='deck_name').widget()

db.define_table('badges',
    Field('badge_name', 'string', unique=True),
    Field('tag', db.tags),
    Field('description', 'text'),
    format='%(badge_name)s')
db.badges.badge_name.requires = IS_NOT_IN_DB(db, 'badges.badge_name')
db.badges.tag.requires = IS_EMPTY_OR(IS_IN_DB(db, 'tags.id', db.tags._format))

db.define_table('locations',
    Field('map_location'),  # , unique=True  # was location (reserved term)
    Field('loc_alias'),  # , unique=True  # was alias (reserved term)
    Field('readable'),
    Field('bg_image', db.images),
    Field('loc_active', 'boolean'),
    format='%(map_location)s')
db.locations.map_location.requires = IS_NOT_IN_DB(db, 'locations.map_location')
db.locations.loc_alias.requires = IS_NOT_IN_DB(db, 'locations.loc_alias')
db.locations.bg_image.requires = IS_EMPTY_OR(IS_IN_DB(db, 'images.id',
                                                     db.images._format))

db.define_table('npcs',
    Field('name', 'string', unique=True),
    Field('map_location', 'list:reference locations'),  # was location (reserved term)
    Field('npc_image', db.images),
    Field('notes', 'text'),
    format='%(name)s')
db.npcs.name.requires = IS_NOT_IN_DB(db, 'npcs.name')
db.npcs.map_location.requires = IS_IN_DB(db, 'locations.id',
                                    db.locations._format, multiple=True)
db.npcs.map_location.widget = lambda field, value: AjaxSelect(field, value,
                                                              indx=1,
                                                              multi='basic',
                                                              lister='simple'
                                                              ).widget()

db.define_table('step_types',
    Field('step_type'),  # , unique=True   # was type (reserved term)
    Field('widget'),
    Field('step_class'),
    format='%(step_type)s')

db.define_table('step_hints',
    Field('hint_label'),  # , unique=True  # was label (reserved term)
    Field('hint_text', 'text'),   # was text (reserved term)
    format='%(hint_label)s')

db.define_table('step_instructions',
    Field('instruction_label'),  # , unique=True  # was label (reserved term)
    Field('instruction_text', 'text'),  # was text (reserved term)
    format='%(instruction_label)s')

db.define_table('step_status',
    Field('status_num', 'integer', unique=True),
    Field('status_label', 'text', unique=True),
    format='%(status_label)s')

db.define_table('steps',
    Field('prompt', 'text'),
    Field('prompt_audio', db.audio, default=0),
    Field('widget_type', db.step_types, default=1),
    Field('widget_image', db.images, default=0),
    Field('step_options', 'list:string'),  # was options (reserved term)
    Field('response1'),
    Field('readable_response'),
    Field('outcome1', default=None),
    Field('response2', default=None),
    Field('outcome2', default=None),
    Field('response3', default=None),
    Field('outcome3', default=None),
    Field('hints', 'list:reference step_hints'),
    Field('instructions', 'list:reference step_instructions'),
    Field('tags', 'list:reference tags'),
    Field('tags_secondary', 'list:reference tags'),
    Field('tags_ahead', 'list:reference tags'),
    Field('npcs', 'list:reference npcs'),
    Field('locations', 'list:reference locations'),
    Field('status', db.step_status, default=1),
    format='%(id)s: %(prompt)s')
db.steps.step_options.widget = SQLFORM.widgets.list.widget
#db.steps.response1.requires = IS_VALID_REGEX()
db.steps.npcs.requires = IS_IN_DB(db, 'npcs.id', db.npcs._format, multiple=True)
db.steps.npcs.widget = lambda field, value: AjaxSelect(field, value,
                                                       indx=1,
                                                       multi='basic',
                                                       lister='simple',
                                                       refresher=True,
                                                       orderby='name'
                                                       ).widget()
db.steps.tags.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple=True)
db.steps.tags.widget = lambda field, value: AjaxSelect(field, value,
                                                       indx=2,
                                                       refresher=True,
                                                       multi='basic',
                                                       lister='simple',
                                                       orderby='tag_position'
                                                       ).widget()
db.steps.tags_secondary.requires = IS_IN_DB(db, 'tags.id', db.tags._format,
                                            multiple=True)
db.steps.tags_secondary.widget = lambda field, value: AjaxSelect(field, value,
                                                                 indx=3,
                                                                 refresher=True,
                                                                 multi='basic',
                                                                 lister='simple',
                                                                 orderby='tag_position'
                                                                 ).widget()
db.steps.tags_ahead.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple=True)
db.steps.tags_ahead.widget = lambda field, value: AjaxSelect(field, value,
                                                             indx=4,
                                                             refresher=True,
                                                             multi='basic',
                                                             lister='simple',
                                                             orderby='tag_position'
                                                             ).widget()
db.steps.locations.requires = IS_IN_DB(db, 'locations.id',
                                       db.locations._format,
                                       multiple=True)
db.steps.locations.widget = lambda field, value: AjaxSelect(field, value,
                                                            indx=5,
                                                            refresher=True,
                                                            multi='basic',
                                                            lister='simple'
                                                            ).widget()
db.steps.hints.requires = IS_IN_DB(db, 'step_hints.id',
                                   db.step_hints._format,
                                   multiple=True)
db.steps.hints.widget = lambda field, value: AjaxSelect(field, value,
                                                        indx=6,
                                                        refresher=True,
                                                        multi='basic',
                                                        lister='simple',
                                                        orderby='hint_label'
                                                        ).widget()
db.steps.instructions.requires = IS_IN_DB(db, 'step_instructions.id',
                                          db.step_instructions._format,
                                          multiple=True)
db.steps.instructions.widget = lambda field, value: \
                                            AjaxSelect(field, value,
                                                       indx=7,
                                                       refresher=True,
                                                       multi='basic',
                                                       lister='simple',
                                                       orderby='instruction_label'
                                                       ).widget()

db.define_table('badges_begun',
    Field('name', db.auth_user, default=auth.user_id),
    Field('tag', db.tags),
    Field('cat1', 'datetime', default=dtnow),
    Field('cat2', 'datetime'),
    Field('cat3', 'datetime'),
    Field('cat4', 'datetime'),
    format='%(name)s, %(tag)s')

db.define_table('tag_progress',
    Field('name', db.auth_user, default=auth.user_id),
    Field('latest_new', 'integer', default=1),  # not tag id but order ranking
    Field('cat1', 'list:reference tags'),
    Field('cat2', 'list:reference tags'),
    Field('cat3', 'list:reference tags'),
    Field('cat4', 'list:reference tags'),
    Field('rev1', 'list:reference tags'),
    Field('rev2', 'list:reference tags'),
    Field('rev3', 'list:reference tags'),
    Field('rev4', 'list:reference tags'),
    format='%(name)s, %(latest_new)s')
db.tag_progress.name.requires = IS_NOT_IN_DB(db, db.tag_progress.name)

db.define_table('paths',
    Field('label'),
    Field('steps', 'list:reference steps'),
    format='%(label)s')
db.paths.steps.requires = IS_IN_DB(db, 'steps.id',
                                   db.steps._format, multiple=True)
db.paths.steps.widget = lambda field, value: AjaxSelect(field, value,
                                                        indx=1,
                                                        refresher=True,
                                                        multi='basic',
                                                        lister='simple',
                                                        sortable=True,
                                                        orderby='~id'
                                                        ).widget()


class PathsVirtualFields(object):
    def tags(self):
        steprows = db(db.steps.id.belongs(self.paths.steps)).select()
        nlists = [s.tags for s in steprows]
        return list(chain.from_iterable(nlists))

    def tags_secondary(self):
        steprows = db(db.steps.id.belongs(self.paths.steps)).select()
        nlists = [s.tags_secondary for s in steprows]
        return list(chain.from_iterable(nlists))

    def tags_ahead(self):
        try:
            steprows = db(db.steps.id.belongs(self.paths.steps)).select()
            nlists = [s.tags_ahead for s in steprows]
            return list(chain.from_iterable(nlists))
        except TypeError:
            return None

db.paths.virtualfields.append(PathsVirtualFields())

db.define_table('attempt_log',
                Field('name', db.auth_user, default=auth.user_id),
                Field('step', db.steps),
                Field('in_path', db.paths),  # was path (reserved term)
                Field('score', 'double'),
                Field('dt_attempted', 'datetime', default=dtnow)
                )
db.attempt_log.name.requires = IS_IN_DB(db, 'auth_user.id',
                                db.auth_user._format)
db.attempt_log.step.requires = IS_IN_DB(db, 'steps.id', db.steps._format)
db.attempt_log.in_path.requires = IS_IN_DB(db, 'paths.id', db.paths._format)
db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_1 ON attempt_log (name);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_2 ON attempt_log (name, dt_attempted);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_3 ON attempt_log (dt_attempted);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_3 ON attempt_log (in_path);')

db.define_table('tag_records',
                Field('name', db.auth_user, default=auth.user_id),
                Field('tag', db.tags),
                Field('times_right', 'double'),
                Field('times_wrong', 'double'),
                Field('tlast_wrong', 'datetime', default=dtnow),
                Field('tlast_right', 'datetime', default=dtnow),
                Field('in_path', db.paths),  # was path (reserved term)
                Field('step', db.steps),
                Field('secondary_right', 'list:string')
                )
db.tag_records.name.requires = IS_IN_DB(db, 'auth_user.id',
                                    db.auth_user._format)
db.tag_records.tag.requires = IS_IN_DB(db, 'tags.id', db.tags._format)
db.tag_records.step.requires = IS_IN_DB(db, 'steps.id', db.steps._format)
db.tag_records.in_path.requires = IS_IN_DB(db, 'paths.id', db.paths._format)
db.executesql('CREATE INDEX IF NOT EXISTS idx_trecs_1 ON tag_records (name, tag);')

db.define_table('bug_status',
    Field('status_label'),
    format='%(status_label)s')

db.define_table('bugs',
    Field('step', db.steps),
    Field('in_path', db.paths),
    Field('map_location', db.locations),
    Field('user_response'),
    Field('score', 'double'),
    Field('log_id', db.attempt_log),
    Field('user_name', db.auth_user, default=auth.user_id),
    Field('date_submitted', 'datetime', default=dtnow),
    Field('bug_status', db.bug_status, default=5),
    Field('admin_comment', 'text'),
    Field('hidden', 'boolean'),
    format='%(step)s')
db.executesql('CREATE INDEX IF NOT EXISTS idx_bugs_1 ON bugs (user_name, bug_status);')

db.define_table('session_data',
    Field('name', db.auth_user, default=auth.user_id),
    Field('updated', 'datetime', default=dtnow),
    Field('session_start', 'datetime', default=dtnow),
    Field('other_data', 'text'),
    format='%(name)s')

db.define_table('user_stats',
    Field('name', db.auth_user, default=auth.user_id),
    Field('year', 'integer'),
    Field('month', 'integer'),
    Field('week', 'integer'),
    Field('updated', 'datetime', default=dtnow),
    Field('day1', 'list:reference attempt_log'),
    Field('day2', 'list:reference attempt_log'),
    Field('day3', 'list:reference attempt_log'),
    Field('day4', 'list:reference attempt_log'),
    Field('day5', 'list:reference attempt_log'),
    Field('day6', 'list:reference attempt_log'),
    Field('day7', 'list:reference attempt_log'),
    Field('logs_by_tag', 'text'),
    Field('logs_right', 'list:reference attempt_log'),
    Field('logs_wrong', 'list:reference attempt_log'),
    Field('done', 'integer', default=0),
    format='%(name)s, %(year)s, %(month)s, %(week)s')
db.executesql('CREATE INDEX IF NOT EXISTS idx_userstats_1 '
              'ON user_stats (week, year, name);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_userstats_1 '
              'ON user_stats (name, week, year);')
db.executesql('CREATE INDEX IF NOT EXISTS idx_userstats_1 '
              'ON user_stats (year, week, name);')

db.define_table('topics',
    Field('topic', 'string'),
    format='%(topic)s')

db.define_table('content_pages',
    Field('title', 'string'),
    Field('content', 'text'),
    Field('first_authored', 'datetime', default=dtnow),
    Field('last_updated', 'datetime', default=dtnow),
    Field('author', 'reference auth_user', default=auth.user_id),
    Field('topics', 'list:reference topics'),
    format='%(title)s')
