# coding: utf8

from plugin_ajaxselect import AjaxSelect
from itertools import chain
import datetime
import os
import re

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
response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.css'))

dtnow = datetime.datetime.utcnow()


#TODO: Fix this regex validator
class IS_VALID_REGEX(object):
    """
    custom validator to check regex in step definitions against the given
    readable responses.
    """
    def __init__(self):
        self.error_message = 'Given answers do not satisfy regular expression.'

    def __call__(self, value):
        request = current.request
        answers = request.vars.readable_response
        alist = answers.split('|')
        regex = value.encode('string-escape')
        for a in alist:
            if re.match(a.strip(), regex, re.I):
                print a.strip()
                print 'it matched!'
            else:
                print 'answer ', a, ' did not match the regex provided.'
                print regex
                return (value, self.error_message)
        return (value, None)

#TODO:Allow for different class profiles with different settings
db.define_table('classes',
                Field('institution', 'string', default='Tyndale Seminary', unique=True),
                Field('year', 'integer', default=dtnow.year),
                Field('term', 'string'),
                Field('section', 'string'),
                Field('instructor', 'reference auth_user', default=auth.user_id),
                Field('start_date', 'datetime'),
                Field('end_date', 'datetime'),
                Field('paths_per_day', 'integer', default=40),
                Field('days_per_week', 'integer', default=5),
                Field('members', 'list:reference auth_user'),
                format='%(institution)s, %(year)s %(term)s %(section)s, '
                       '%(instructor.last_name)s, %(instructor.first_name)s'
                )

db.define_table('images',
    Field('image', 'upload',
          uploadfolder=os.path.join(request.folder, "static/images")),
    Field('title', 'string'),
    Field('description', 'string'),
    format='%(title)s')

db.define_table('audio',
    Field('clip', 'upload',
          uploadfolder=os.path.join(request.folder, "static/audio")),
    Field('title', 'string'),
    Field('description', 'string'),
    format='%(title)s')

db.define_table('journals',
    Field('user', db.auth_user, default=auth.user_id),
    Field('pages', 'list:reference pages'),
    format='%(user)s')
db.journals.user.requires = IS_NOT_IN_DB(db, 'journals.user')

db.define_table('pages',
    Field('page', 'text'),
    format='%(page)s')

db.define_table('categories',
    Field('category', unique=True),
    Field('description'),
    format='%(category)s')

db.define_table('tags',
    Field('tag', 'string', unique=True),
    Field('position', 'integer'),
    Field('slides', 'list:reference plugin_slider_decks'),
    format='%(tag)s')

db.tags.tag.requires = IS_NOT_IN_DB(db, 'tags.tag')

db.tags.slides.requires = IS_IN_DB(db,
                                   'plugin_slider_decks.id',
                                   '%(deck_name)s',
                                   multiple=True)
db.tags.slides.widget = lambda field, value: \
                                    AjaxSelect(field, value,
                                               'plugin_slider_decks',
                                               refresher=True,
                                               multi='basic',
                                               lister='editlinks').widget()

db.define_table('badges',
    Field('badge_name', 'string', unique=True),
    Field('tag', db.tags),
    Field('description', 'text'),
    format='%(badge_name)s')
db.badges.badge_name.requires = IS_NOT_IN_DB(db, 'badges.badge_name')
db.badges.tag.requires = IS_EMPTY_OR(IS_IN_DB(db, 'tags.id', db.tags._format))

db.define_table('locations',
    Field('location', unique=True),
    Field('alias', unique=True),
    Field('readable'),
    Field('bg_image', db.images),
    format='%(location)s')
db.locations.location.requires = IS_NOT_IN_DB(db, 'locations.location')
db.locations.alias.requires = IS_NOT_IN_DB(db, 'locations.alias')
db.locations.bg_image.requires = IS_EMPTY_OR(IS_IN_DB(db, 'images.id',
                                                     db.images._format))

db.define_table('npcs',
    Field('name', 'string', unique=True),
    Field('location', 'list:reference locations'),
    Field('npc_image', db.images),
    Field('notes', 'text'),
    format='%(name)s')
db.npcs.name.requires = IS_NOT_IN_DB(db, 'npcs.name')
db.npcs.location.requires = IS_IN_DB(db, 'locations.id',
                                    db.locations._format, multiple=True)
db.npcs.location.widget = lambda field, value: AjaxSelect(field, value,
                                                          'locations',
                                                          multi='basic',
                                                          lister='editlinks'
                                                          ).widget()

db.define_table('step_types',
    Field('type', unique=True),
    Field('widget'),
    Field('step_class'),
    format='%(type)s')

db.define_table('step_hints',
    Field('label', unique=True),
    Field('text', 'text'),
    format='%(label)s')

db.define_table('step_instructions',
    Field('label', unique=True),
    Field('text', 'text'),
    format='%(label)s')

db.define_table('step_status',
    Field('status_num', 'integer', unique=True),
    Field('status_label', 'text', unique=True),
    format='%(status_label)s')

db.define_table('steps',
    Field('prompt', 'text'),
    Field('prompt_audio', db.audio, default=0),
    Field('widget_type', db.step_types, default=1),
    Field('widget_image', db.images, default=0),
    Field('options', 'list:string'),
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
    format='%(prompt)s')
db.steps.options.widget = SQLFORM.widgets.list.widget
#db.steps.response1.requires = IS_VALID_REGEX()
db.steps.npcs.requires = IS_IN_DB(db, 'npcs.id',
                                      db.npcs._format, multiple=True)
db.steps.npcs.widget = lambda field, value: AjaxSelect(field, value, 'npcs',
                                                       multi='basic',
                                                       lister='editlinks'
                                                       ).widget()
db.steps.tags.requires = IS_IN_DB(db, 'tags.id',
                                      db.tags._format, multiple=True)
db.steps.tags.widget = lambda field, value: AjaxSelect(field, value, 'tags',
                                                       refresher=True,
                                                       multi='basic',
                                                       lister='editlinks'
                                                       ).widget()
db.steps.tags_secondary.requires = IS_IN_DB(db, 'tags.id',
                                                db.tags._format,
                                                multiple=True)
db.steps.tags_secondary.widget = lambda field, value: \
                                            AjaxSelect(field, value,
                                                       'tags',
                                                       refresher=True,
                                                       multi='basic',
                                                       lister='editlinks'
                                                       ).widget()
db.steps.tags_ahead.requires = IS_IN_DB(db, 'tags.id',
                                            db.tags._format,
                                            multiple=True)
db.steps.tags_ahead.widget = lambda field, value: AjaxSelect(field, value,
                                                             'tags',
                                                             refresher=True,
                                                             multi='basic',
                                                             lister='editlinks'
                                                             ).widget()
db.steps.locations.requires = IS_IN_DB(db, 'locations.id',
                                           db.locations._format,
                                           multiple=True)
db.steps.locations.widget = lambda field, value: AjaxSelect(field, value,
                                                            'locations',
                                                            multi='basic',
                                                            lister='editlinks'
                                                            ).widget()
db.steps.hints.requires = IS_IN_DB(db, 'step_hints.id',
                                       db.step_hints._format,
                                       multiple=True)
db.steps.hints.widget = lambda field, value: AjaxSelect(field, value,
                                                        'step_hints',
                                                        multi='basic',
                                                        lister='editlinks'
                                                        ).widget()
db.steps.instructions.requires = IS_IN_DB(db, 'step_instructions.id',
                                              db.step_instructions._format,
                                              multiple=True)
db.steps.instructions.widget = lambda field, value: \
                                            AjaxSelect(field, value,
                                                       'step_instructions',
                                                       multi='basic',
                                                       lister='editlinks'
                                                       ).widget()

db.define_table('badges_begun',
    Field('name', db.auth_user, default=auth.user_id),
    Field('tag', db.tags),
    Field('cat1', 'datetime', default=dtnow),
    Field('cat2', 'datetime'),
    Field('cat3', 'datetime'),
    Field('cat4', 'datetime'))

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
                                                        'steps',
                                                        refresher=True,
                                                        multi='basic',
                                                        lister='editlinks',
                                                        sortable='true'
                                                        ).widget()


class PathsVirtualFields(object):
    def tags(self):
        steprows = db(db.steps.id.belongs(self.paths.steps)).select()
        nlists = [s.tags for s in steprows]
        return list(chain.from_iterable(nlists))
db.paths.virtualfields.append(PathsVirtualFields())

# TODO: remove path_log table
db.define_table('path_log',
                Field('name', db.auth_user, default=auth.user_id),
                Field('path', db.paths),
                Field('dt_started', 'datetime', default=dtnow),
                Field('last_step', db.steps),
                Field('dt_completed', 'datetime', default=None)
                )
db.path_log.name.requires = IS_IN_DB(db, 'auth_user.id', db.auth_user._format)
db.path_log.path.requires = IS_IN_DB(db, 'paths.id', db.paths._format)
db.path_log.last_step.requires = IS_IN_DB(db, 'steps.id', db.steps._format)

db.define_table('attempt_log',
                Field('name', db.auth_user, default=auth.user_id),
                Field('step', db.steps),
                Field('path', db.paths),
                Field('score', 'double'),
                Field('dt_attempted', 'datetime', default=dtnow)
                )
db.attempt_log.name.requires = IS_IN_DB(db, 'auth_user.id',
                                db.auth_user._format)
db.attempt_log.step.requires = IS_IN_DB(db, 'steps.id', db.steps._format)
db.attempt_log.path.requires = IS_IN_DB(db, 'paths.id', db.paths._format)

db.define_table('tag_records',
                Field('name', db.auth_user, default=auth.user_id),
                Field('tag', db.tags),
                Field('times_right', 'double'),
                Field('times_wrong', 'double'),
                Field('tlast_wrong', 'datetime', default=dtnow),
                Field('tlast_right', 'datetime', default=dtnow),
                Field('path', db.paths),
                Field('step', db.steps),
                Field('secondary_right', 'list:string')
                )
db.tag_records.name.requires = IS_IN_DB(db, 'auth_user.id',
                                    db.auth_user._format)
db.tag_records.tag.requires = IS_IN_DB(db, 'tags.id', db.tags._format)
db.tag_records.step.requires = IS_IN_DB(db, 'steps.id', db.steps._format)
db.tag_records.path.requires = IS_IN_DB(db, 'paths.id', db.paths._format)

db.define_table('bug_status',
    Field('status_label'),
    format='%(status_label)s')

db.define_table('bugs',
    Field('step', db.steps),
    Field('path', db.paths),
    Field('location', db.locations),
    Field('user_response'),
    Field('score', 'double'),
    Field('log_id', db.attempt_log),
    Field('user_name', db.auth_user, default=auth.user_id),
    Field('date_submitted', 'datetime', default=dtnow),
    Field('bug_status', db.bug_status, default=5),
    Field('admin_comment', 'text'),
    Field('hidden', 'boolean'),
    format='%(step)s')

db.define_table('session_data',
    Field('user', db.auth_user, default=auth.user_id),
    Field('updated', 'datetime', default=dtnow),
    Field('session_start', 'datetime', default=dtnow),
    Field('data', 'text'),
    format='%(user)s')
