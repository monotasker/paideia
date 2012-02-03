# coding: utf8

#hack for PyDev error checking and debugging
if 0:
    from gluon import current, IS_IN_DB
    from gluon.dal import DAL, Field
    from gluon.tools import Auth
    auth = Auth()
    db = DAL()
    request = current.request
    from applications.paideia.modules.plugin_multiselect_widget import hmultiselect_widget, vmultiselect_widget

#os module needed for setting upload folders for images and audio
import os
#plugin from http://dev.s-cubism.com/plugin_multiselect_widget
from plugin_multiselect_widget import hmultiselect_widget, vmultiselect_widget
from plugin_ajaxselect import AjaxSelect
import datetime

dtnow = datetime.datetime.utcnow()

db.define_table('categories',
    Field('category'),
    Field ('description'),
    format='%(category)s')

db.define_table('tags',
    Field('tag', 'string'),
    format='%(tag)s')

db.define_table('locations',
    Field('location'),
    Field('background', 'upload', uploadfolder=os.path.join(request.folder, "static/images")),
    format='%(location)s')

db.define_table('npcs',
    Field('name', 'string'),
    Field('location', 'list:reference db.locations'),
    Field('image', 'upload', uploadfolder=os.path.join(request.folder,"static/images")),
    format='%(name)s')

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
    Field('audio', 'upload', uploadfolder=os.path.join(request.folder, "static/audio")),
    format='%(question)s')

db.questions.tags.requires = IS_IN_DB(db, 'questions.id', db.questions._format, multiple = True)
db.questions.npcs.requires = IS_IN_DB(db, 'npcs.id', db.npcs._format, multiple = True)
db.questions.npcs.widget = lambda field, value: AjaxSelect(field, value, 'tags', multi = 'v').widget()
db.questions.tags.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple = True)
db.questions.tags.widget = lambda field, value: AjaxSelect(field, value, 'tags', refresher = True, multi = 'v').widget() #vmultiselect_widget
db.questions.tags_secondary.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple = True)
db.questions.tags_secondary.widget = lambda field, value: AjaxSelect(field, value, 'tags', multi = 'v').widget()

db.define_table('quizzes',
    Field('quiz'),
    Field('length'),
    Field('tags', 'list:reference db.tags'),
    Field('frequency'),
    Field('groups', 'list:reference db.auth_group'),
    Field('start_date', 'date', default=dtnow),
    Field('end_date', 'date'),
    format='%(quiz)s')

db.quizzes.tags.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple = True)
db.quizzes.groups.requires = IS_IN_DB(db, 'auth_group.id', db.auth_group._format, multiple = True)

db.define_table('question_records',
    Field('name', db.auth_user, default=auth.user_id),
    Field('question', db.questions),
    Field('times_right', 'double'),
    Field('times_wrong', 'double'),
    Field('tlast_wrong', 'datetime', default=dtnow),
    Field('tlast_right', 'datetime', default=dtnow),
    Field('category', db.categories)
    )

db.define_table('tag_records',
    Field('name', db.auth_user, default=auth.user_id),
    Field('tag', db.tags),
    Field('times_right', 'double'),
    Field('times_wrong', 'double'),
    Field('tlast_wrong', 'datetime', default=dtnow),
    Field('tlast_right', 'datetime', default=dtnow),
    Field('category', db.categories)
    )

db.define_table('attempt_log',
    Field('name', db.auth_user, default=auth.user_id),
    Field('question', db.questions),
    Field('score', 'double'),
    Field('quiz', db.quizzes),
    Field('dt_attempted', 'datetime', default=dtnow)
    )

db.define_table('quiz_records',
    Field('name', db.auth_user, default=auth.user_id),
    Field('quiz', db.quizzes),
    Field('score', 'double'),
    Field('date_taken', 'datetime', default=dtnow)
    )

db.define_table('bug_status',
    Field('status_label'),
    format='%(status_label)s')

db.define_table('q_bugs',
    Field('question', db.questions),
    Field('a_submitted'),
    Field('name', db.auth_user, default=auth.user_id),
    Field('submitted', 'datetime', default=dtnow),
    Field('bug_status', db.bug_status, default=1),
    Field('admin_comment',  'text'),
    Field('prev_lastright',  'datetime'),
    Field('prev_lastwrong', 'datetime'),
    format='%(question)s')

db.define_table('news',
    Field('story', 'text'),
    Field('title', 'string'),
    Field('name', db.auth_user, default=auth.user_id),
    Field('date_submitted', 'datetime', default=dtnow),
    Field('last_edit', 'datetime', default=dtnow),
    format='%(title)s')
