# coding: utf8

from plugin_ajaxselect import AjaxSelect
from itertools import chain
import datetime
import os
#js file necessary for AjaxSelect widget
response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.js'))
response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.css'))

dtnow = datetime.datetime.utcnow()

#TODO:Allow for different class profiles with different settings
db.define_table('app_settings',
    Field('paths_per_day', 'integer', default=10),
    Field('days_per_week', 'integer', default=5)
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
    Field('pages', 'list:reference db.pages'),
    format='%(user)s')

db.define_table('pages',
    Field('page', 'text'),
    format='%(page)s')

db.define_table('categories',
    Field('category'),
    Field('description'),
    format='%(category)s')

db.define_table('tags',
    Field('tag', 'string'),
    Field('position', 'integer'),
    format='%(tag)s')

db.define_table('locations',
    Field('location'),
    Field('alias'),
    Field('bg_image', db.images),
    format='%(location)s')

db.define_table('npcs',
    Field('name', 'string'),
    Field('location', 'list:reference db.locations'),
    Field('npc_image', db.images),
    Field('notes', 'text'),
    format='%(name)s')
db.npcs.location.requires = IS_IN_DB(db, 'locations.id',
                                     db.locations._format, multiple=True)
db.npcs.location.widget = lambda field, value: \
                         AjaxSelect().widget(field, value, 'locations',
                                    multi='basic')

db.define_table('inv_items',
    Field('item_name', 'string'),
    Field('item_image', db.images),
    format='%(item_name)s')

db.define_table('inventory',
    Field('owner', db.auth_user, default=auth.user_id),
    Field('items_held', 'list:reference db.inv_items'),
    format='%(owner)s inventory')

#this table is deprecated
#TODO: refactor out questions entirely
db.define_table('questions',
    Field('question', 'text'),
    Field('answer'),
    Field('value', 'double', default=1.0),
    Field('readable_answer'),
    Field('answer2', default='null'),
    Field('value2', 'double', default=0.5),
    Field('answer3', default='null'),
    Field('value3', 'double', default=0.3),
    Field('frequency', 'double'),
    Field('tags', 'list:reference db.tags'),
    Field('tags_secondary', 'list:reference db.tags'),
    Field('status', 'integer'),
    Field('npcs', 'list:reference db.npcs'),
    Field('next', 'list:reference db.questions'),
    Field('audio', 'upload', uploadfolder=os.path.join(request.folder,
        "static/audio")),
    format='%(question)s')
db.questions.npcs.requires = IS_IN_DB(db, 'npcs.id',
                                db.npcs._format, multiple=True)
db.questions.npcs.widget = lambda field, value: AjaxSelect().widget(field,
                                                    value, 'npcs',
                                                    multi='basic')
db.questions.tags.requires = IS_IN_DB(db, 'tags.id',
                                db.tags._format, multiple=True)
db.questions.tags.widget = lambda field, value: AjaxSelect().widget(field,
                                                    value, 'tags',
                                                    refresher=True,
                                                    multi='basic')
db.questions.tags_secondary.requires = IS_IN_DB(db, 'tags.id',
                                        db.tags._format, multiple=True)
db.questions.tags_secondary.widget = lambda field, value: AjaxSelect().widget(
                                                    field, value, 'tags',
                                                    multi='basic')

db.define_table('step_types',
    Field('type'),
    Field('widget'),
    Field('step_class'),
    format='%(type)s')

#TODO: transfer all questions data over to steps table
db.define_table('steps',
    Field('prompt', 'text'),
    Field('prompt_audio', db.audio, default=0),
    Field('widget_type', db.step_types, default=1),
    Field('widget_image', db.images, default=0),
    Field('options', 'list:string'),
    Field('response1'),
    Field('readable_response'),
    Field('outcome1', default='null'),
    Field('response2', default='null'),
    Field('outcome2', default='null'),
    Field('response3', default='null'),
    Field('outcome3', default='null'),
    Field('tags', 'list:reference db.tags'),
    Field('tags_secondary', 'list:reference db.tags'),
    Field('npcs', 'list:reference db.npcs'),
    Field('locations', 'list:reference db.locations'),
    Field('status', 'integer'),
    format='%(prompt)s')
db.steps.options.widget = SQLFORM.widgets.list.widget
db.steps.npcs.requires = IS_IN_DB(db, 'npcs.id',
                                      db.npcs._format, multiple=True)
db.steps.npcs.widget = lambda field, value: AjaxSelect().widget(
                                                field, value, 'npcs',
                                                multi='basic',
                                                lister='editlinks')
db.steps.tags.requires = IS_IN_DB(db, 'tags.id',
                                      db.tags._format, multiple=True)
db.steps.tags.widget = lambda field, value: AjaxSelect().widget(
                                                field, value, 'tags',
                                                refresher=True,
                                                multi='basic',
                                                lister='editlinks')
db.steps.tags_secondary.requires = IS_IN_DB(db, 'tags.id',
                                                db.tags._format,
                                                multiple=True)
db.steps.tags_secondary.widget = lambda field, value: AjaxSelect().widget(
                                                field, value, 'tags',
                                                multi='basic',
                                                lister='editlinks')
db.steps.locations.requires = IS_IN_DB(db, 'locations.id',
                                                db.locations._format,
                                                multiple=True)
db.steps.locations.widget = lambda field, value: AjaxSelect().widget(
                                                field, value, 'locations',
                                                multi='basic',
                                                lister='editlinks')
#this table is deprecated
#TODO: do we need an equivalent for steps? The same data could be retrieved as
# needed from the attempts_log table.
db.define_table('question_records',
    Field('name', db.auth_user, default=auth.user_id),
    Field('question', db.questions),
    Field('times_right', 'double'),
    Field('times_wrong', 'double'),
    Field('tlast_wrong', 'datetime', default=dtnow),
    Field('tlast_right', 'datetime', default=dtnow),
    Field('category', db.categories)
    )

db.define_table('tag_progress',
    Field('name', db.auth_user, default=auth.user_id),
    Field('latest_new', db.tags),
    format='%(name)s, %(latest_new)s')

db.define_table('paths',
    Field('label'),
    Field('steps', 'list:reference db.steps'),
    format='%(label)s')
db.paths.steps.requires = IS_IN_DB(db, 'steps.id',
                                   db.steps._format, multiple=True)
db.paths.steps.widget = lambda field, value: AjaxSelect().widget(
                                        field, value, 'steps',
                                        refresher=True,
                                        multi='basic',
                                        lister='editlinks')


class PathsVirtualFields(object):
    def locations(self):
        steprows = db(db.steps.id.belongs(self.paths.steps)).select().first()
        return steprows.locations

    def tags(self):
        steprows = db(db.steps.id.belongs(self.paths.steps)).select()
        nlists = [s.locations for s in steprows]
        return list(chain.from_iterable(nlists))
db.paths.virtualfields.append(PathsVirtualFields())

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
    Field('step', db.steps)
    )
db.tag_records.name.requires = IS_IN_DB(db, 'auth_user.id',
                                    db.auth_user._format)
db.tag_records.tag.requires = IS_IN_DB(db, 'tags.id', db.tags._format)
db.tag_records.step.requires = IS_IN_DB(db, 'steps.id', db.steps._format)
db.tag_records.path.requires = IS_IN_DB(db, 'paths.id', db.paths._format)

db.define_table('bug_status',
    Field('status_label'),
    format='%(status_label)s')

db.define_table('q_bugs',
    Field('question', db.questions),
    Field('a_submitted'),
    Field('name', db.auth_user, default=auth.user_id),
    Field('submitted', 'datetime', default=dtnow),
    Field('bug_status', db.bug_status, default=1),
    Field('admin_comment', 'text'),
    Field('prev_lastright', 'datetime'),
    Field('prev_lastwrong', 'datetime'),
    format='%(question)s')

db.define_table('news',
    Field('story', 'text'),
    Field('title', 'string'),
    Field('name', db.auth_user, default=auth.user_id),
    Field('date_submitted', 'datetime', default=dtnow),
    Field('last_edit', 'datetime', default=dtnow),
    format='%(title)s')
