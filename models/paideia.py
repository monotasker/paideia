# coding: utf8

#plugin from http://dev.s-cubism.com/plugin_multiselect_widget
from plugin_multiselect_widget import hmultiselect_widget, vmultiselect_widget

db.define_table('categories',
    Field('category'),
    Field ('description'),
    format='%(category)s')

db.define_table('tags',
    Field('tag', 'string'),
    format='%(tag)s')

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
    format='%(question)s')

db.questions.tags.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple = True)
db.questions.tags.widget = vmultiselect_widget

db.define_table('quizzes',
    Field('quiz'),
    Field('length'),
    Field('tags', 'list:reference db.tags'),
    Field('frequency'),
    Field('groups', 'list:reference db.auth_group'),
    Field('start_date', 'date', default=request.now),
    Field('end_date', 'date'),
    format='%(quiz)s')

db.quizzes.tags.requires = IS_IN_DB(db, 'tags.id', db.tags._format, multiple = True)
db.quizzes.groups.requires = IS_IN_DB(db, 'auth_group.id', db.auth_group._format, multiple = True)

db.define_table('question_records',
    Field('name', db.auth_user, default=auth.user_id),
    Field('question', db.questions),
    Field('times_right', 'double'),
    Field('times_wrong', 'double'),
    Field('last_right', 'date', default=request.now),
    Field('last_wrong', 'date', default=request.now),
    Field('category', db.categories)
    )

db.define_table('quiz_records',
    Field('name', db.auth_user, default=auth.user_id),
    Field('quiz', db.quizzes),
    Field('score', 'double'),
    Field('date_taken', 'date', default=request.now)
    )

db.define_table('q_bugs',
    Field('question', db.questions),
    Field('a_submitted'),
    Field('name', db.auth_user, default=auth.user_id),
    Field('date_submitted', 'date', default=request.now),
    format='%(question)s')

db.define_table('news',
    Field('story', 'text'),
    Field('title', 'string'),
    Field('name', db.auth_user, default=auth.user_id),
    Field('date_submitted', 'datetime', default=request.now),
    Field('last_edit', 'datetime', default=request.now),
    format='%(title)s')
