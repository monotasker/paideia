#! /etc/bin/python
# -*- coding: utf8 -*-
"""
Model file defining abstracted data structure for dedicated Paideia fields.

This uses the web2py Data Abstraction Layer to allow easy migrations and
movement from one db system to another.

"""

from plugin_ajaxselect import AjaxSelect
# from itertools import chain
from datetime import datetime
from datetime import timezone
import os
import random
import string
import traceback
import uuid
from paideia_utils import simple_obj_print
from plugin_widgets import SortedOptionsWidget
# import re

if 0:
    from web2py.gluon import URL, current, Field, IS_IN_DB, IS_NOT_IN_DB, SQLFORM
    from web2py.gluon import IS_EMPTY_OR, IS_IN_SET, SPAN, A, I
    from web2py.applications.paideia.modules.plugin_ajaxselect import AjaxSelect
    from web2py.applications.paideia.modules.paideia_utils import simple_obj_print
    from web2py.applications.paideia.modules.plugin_widgets import SortedOptionsWidget
    response = current.response
    request = current.request
    auth = current.auth
    db = current.db

# js file necessary for AjaxSelect widget
# TODO: move these to an AjaxSelect model file
response.files.insert(5, URL('static',
                             'plugin_ajaxselect/plugin_ajaxselect.js'))
# response.files.append(URL('static',
# 'plugin_ajaxselect/plugin_ajaxselect.css'))
response.files.append(URL('static', 'css/plugin_listandedit.css'))
response.files.append(URL('static', 'css/plugin_slider.css'))

dtnow = datetime.now(timezone.utc)

db.define_table('classes',
                Field('institution', 'string', default='Tyndale Seminary'),
                Field('academic_year', 'integer', default=dtnow.year),  # year
                Field('term', 'string'),
                Field('course_section', 'string'),
                Field('instructor', 'reference auth_user',
                      default=auth.user_id),
                Field('start_date', 'datetime'),
                Field('end_date', 'datetime'),
                Field('paths_per_day', 'integer', default=40),
                Field('days_per_week', 'integer', default=5),
                Field('a_target', 'integer'),
                Field('a_cap', 'integer'),
                Field('b_target', 'integer'),
                Field('b_cap', 'integer'),
                Field('c_target', 'integer'),
                Field('c_cap', 'integer'),
                Field('d_target', 'integer'),
                Field('d_cap', 'integer'),
                Field('f_target', 'integer'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(institution)s, %(academic_year)s %(term)s '
                       '%(course_section)s, %(instructor)s'
                )
db.classes.term.requires = IS_EMPTY_OR(IS_IN_SET(('fall',
                                                  'winter intersession',
                                                  'winter',
                                                  'spring/summer',
                                                  'january', 'february',
                                                  'march', 'april', 'may',
                                                  'june', 'july', 'august',
                                                  'september', 'october',
                                                  'november', 'december')))

db.define_table('class_keys',
                Field('class_key', 'string', default=lambda: ''.join(
                    random.choice(string.ascii_letters) for i in range(10)),
                    unique=True
                    ),
                Field('class_section', 'reference classes'),
                Field('created_date', 'datetime', default=dtnow),
                Field('cancelled', 'boolean', default=False),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                )

db.define_table('class_membership',
                Field('name', 'reference auth_user'),
                Field('class_section', 'reference classes'),
                Field('custom_start', 'datetime'),
                Field('starting_set'),
                Field('custom_end', 'datetime'),
                Field('ending_set'),
                Field('custom_a_cap', 'integer'),
                Field('custom_b_cap', 'integer'),
                Field('custom_c_cap', 'integer'),
                Field('custom_d_cap', 'integer'),
                Field('final_grade', 'list:string'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(name)s, %(class_section)s'
                )
db.class_membership.final_grade.requires = IS_EMPTY_OR(IS_IN_SET(('A+', 'A',
                                                                  'A-', 'B+',
                                                                  'B', 'B-',
                                                                  'C+', 'C',
                                                                  'C-', 'D+',
                                                                  'D', 'D-',
                                                                  'F')))

db.define_table('images',
                Field('image', 'upload', length=128,
                      uploadfolder=os.path.join(request.folder,
                                                "static/images")),
                Field('title', 'string', length=256),
                Field('description', 'string', length=256),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(title)s')

db.define_table('audio',
                Field('clip', 'upload', length=128,
                      uploadfolder=os.path.join(request.folder,
                                                "static/audio")),
                Field('clip_ogg', 'upload', length=128,
                      uploadfolder=os.path.join(request.folder,
                                                "static/audio")),
                Field('clip_m4a', 'upload', length=128,
                      uploadfolder=os.path.join(request.folder,
                                                "static/audio")),
                Field('title', 'string', length=256),
                Field('description', 'string', length=256),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(title)s')

db.define_table('journals',
                Field('name', db.auth_user, default=auth.user_id),
                Field('journal_pages', 'list:reference journal_pages'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(name)s')
db.journals.name.requires = IS_NOT_IN_DB(db, 'journals.name')

db.define_table('journal_pages',
                Field('journal_page', 'text'),  # was page (reserved term)
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(page)s')

db.define_table('categories',
                Field('category', unique=True),
                Field('description'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(category)s')

db.define_table('tags',
                Field('tag', 'string', unique=True),
                Field('tag_position', 'integer'),  # was position (reserved)
                Field('slides', 'list:reference plugin_slider_decks'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format=lambda row: row['tag'])
# db.executesql('CREATE INDEX IF NOT EXISTS idx_tags1 ON tags (tag,
# tag_position);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_tags2 ON tags (tag_position);')

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

# don't force uniqueness on lemma field to allow for homographs
db.define_table('lemmas',
                Field('lemma', 'string'),
                Field('part_of_speech'),
                Field('glosses', 'list:string'),
                Field('times_in_nt', 'integer'),
                Field('first_tag', db.tags),
                Field('thematic_pattern', 'string', default='none'),
                Field('real_stem', 'string', default='none'),
                Field('genitive_singular', 'string', default='none'),
                Field('future', 'string', default='none'),
                Field('aorist_active', 'string', default='none'),
                Field('perfect_active', 'string', default='none'),
                Field('perfect_passive', 'string', default='none'),
                Field('aorist_passive', 'string', default='none'),
                Field('other_irregular', 'string', default='none'),
                Field('extra_tags', 'list:reference tags'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(lemma)s')
db.lemmas.part_of_speech.requires = IS_IN_SET(('verb', 'adverb', 'noun',
                                               'pronoun', 'proper_noun',
                                               'conjunction', 'preposition',
                                               'particle', 'adjective',
                                               'interjection', 'article', 'idiom'))
db.lemmas.thematic_pattern.requires = IS_EMPTY_OR(IS_IN_SET(
    ('alpha thematic',
     'alpha contract',
     'epsilon contract1',
     'epsilon contract2',
     'omicron contract',
     '3rd decl upsilon',
     '3rd decl epsilon',
     'liquid verb')))
db.lemmas.extra_tags.requires = IS_IN_DB(db, 'tags.id',
                                         db.tags._format,
                                         multiple=True)
db.lemmas.extra_tags.widget = lambda field, value: AjaxSelect(field, value,
                                                              indx=1,
                                                              multi='basic',
                                                              lister='simple',
                                                              orderby='tag'
                                                              ).widget()

db.define_table('step_instructions',
                Field('instruction_label'),  # was label (reserved term)
                Field('instruction_text', 'text'),  # was text (reserved term)
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(instruction_label)s')

db.define_table('constructions',
                Field('construction_label', unique=True),
                Field('readable_label', unique=True),
                Field('trans_regex_eng'),
                Field('trans_templates', 'list:string'),
                Field('form_function'),
                Field('instructions', 'list:reference step_instructions'),
                Field('tags', 'list:reference tags'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(construction_label)s')
db.constructions.instructions.requires = IS_IN_DB(db, 'step_instructions.id',
                                                  db.step_instructions._format,
                                                  multiple=True)
db.constructions.instructions.widget = lambda field, value: \
    AjaxSelect(field, value,
               indx=1,
               multi='basic',
               lister='simple',
               orderby='instruction_label'
               ).widget()
db.constructions.tags.requires = IS_IN_DB(db, 'tags.id',
                                          db.tags._format,
                                          multiple=True)
db.constructions.tags.widget = lambda field, value: \
    AjaxSelect(field, value,
               indx=1,
               multi='basic',
               lister='simple',
               orderby='tag'
               ).widget()

# don't force uniqueness on word_form field to allow for homographs
db.define_table('word_forms',
                Field('word_form', 'string'),
                Field('source_lemma', db.lemmas),
                Field('tense', 'string', default='none'),
                Field('voice', 'string', default='none'),
                Field('mood', 'string', default='none'),
                Field('person', 'string', default='none'),
                Field('number', 'string', default='none'),
                Field('grammatical_case', default='none'),
                Field('gender', 'string', default='none'),
                Field('declension', 'string', default='none'),
                Field('thematic_pattern', 'string', default='none'),
                Field('construction', db.constructions),
                Field('tags', 'list:reference tags'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(word_form)s')
db.word_forms.source_lemma.widget = \
    lambda fld, val: SortedOptionsWidget().widget(fld, val, collation='el')
db.word_forms.tense.requires = IS_IN_SET(('present', 'imperfect', 'future',
                                          'aorist1', 'aorist2', 'perfect1',
                                          'perfect2', 'pluperfect', 'none'))
db.word_forms.voice.requires = IS_IN_SET(('active', 'middle', 'passive',
                                          'middle/passive', 'none'))
db.word_forms.mood.requires = IS_IN_SET(('indicative', 'imperative',
                                         'infinitive', 'subjunctive',
                                         'optative', 'participle', 'none'))
db.word_forms.grammatical_case.requires = IS_IN_SET(('nominative',
                                                     'accusative',
                                                     'genitive', 'dative',
                                                     'vocative',
                                                     'nominative or '
                                                     'accusative',
                                                     'undetermined',
                                                     'none'))
db.word_forms.person.requires = IS_IN_SET(('first', 'second', 'third', 'none'))
db.word_forms.number.requires = IS_IN_SET(('singular', 'plural', 'none'))
db.word_forms.gender.requires = IS_IN_SET(('masculine', 'feminine',
                                           'neuter', 'masculine or feminine',
                                           'masculine or neuter',
                                           'undetermined', 'none'))
db.word_forms.tags.requires = IS_IN_DB(db, 'tags.id',
                                       db.tags._format,
                                       multiple=True)
db.word_forms.tags.widget = lambda field, value: AjaxSelect(field, value,
                                                            indx=1,
                                                            multi='basic',
                                                            lister='simple',
                                                            orderby='tag'
                                                            ).widget()

db.define_table('badges',
                Field('badge_name', 'string', unique=True),
                Field('tag', 'reference tags'),
                Field('description', 'text'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(badge_name)s')
db.badges.badge_name.requires = IS_NOT_IN_DB(db, 'badges.badge_name')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_badges1 ON badges (tag);')

db.define_table('locations',
                Field('map_location'),  # was location (reserved term)
                Field('loc_alias'),  # was alias (reserved term)
                Field('readable'),
                Field('bg_image', 'reference images'),
                Field('loc_active', 'boolean'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(map_location)s')
db.locations.map_location.requires = IS_NOT_IN_DB(db, 'locations.map_location')
db.locations.loc_alias.requires = IS_NOT_IN_DB(db, 'locations.loc_alias')
db.locations.bg_image.requires = IS_EMPTY_OR(IS_IN_DB(db, 'images.id',
                                                      db.images._format))

db.define_table('npcs',
                Field('name', 'string', unique=True),
                Field('map_location', 'list:reference locations'),  # location
                Field('npc_image', 'reference images'),
                Field('notes', 'text'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
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
                Field('step_type'),  # was type (reserved term)
                Field('widget'),
                Field('step_class'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(step_type)s')

db.define_table('step_hints',
                Field('hint_label'),  # was label (reserved term)
                Field('hint_text', 'text'),   # was text (reserved term)
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(hint_label)s')

db.define_table('step_status',
                Field('status_num', 'integer', unique=True),
                Field('status_label', 'text', unique=True),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(status_label)s')

db.define_table('steps',
                Field('prompt', 'text'),
                Field('prompt_audio', 'reference audio', default=0),
                Field('widget_type', 'reference step_types', default=1),
                Field('widget_image', 'reference images', default=0),
                Field('step_options', 'list:string'),  # was options (reserved)
                Field('response1', 'text'),
                Field('readable_response'),
                Field('outcome1', default=None),
                Field('response2', 'text', default=None),
                Field('outcome2', default=None),
                Field('response3', 'text', default=None),
                Field('outcome3', default=None),
                Field('hints', 'list:reference step_hints'),
                Field('instructions', 'list:reference step_instructions'),
                Field('tags', 'list:integer'),
                Field('tags_secondary', 'list:reference tags'),
                Field('tags_ahead', 'list:reference tags'),
                Field('lemmas', 'list:reference lemmas'),
                Field('npcs', 'list:reference npcs'),
                Field('locations', 'list:integer'),
                Field('status', 'reference step_status', default=1),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(id)s: %(prompt)s')
db.steps.prompt_audio.requires = IS_EMPTY_OR(IS_IN_DB(db, 'audio.id',
                                                      db.audio._format))
db.steps.widget_image.requires = IS_EMPTY_OR(IS_IN_DB(db, 'images.id',
                                                      db.images._format))
db.steps.step_options.widget = SQLFORM.widgets.list.widget
db.steps.npcs.requires = IS_IN_DB(db, 'npcs.id', db.npcs._format,
                                  multiple=True)
db.steps.npcs.widget = lambda field, value: AjaxSelect(field, value,
                                                       indx=1,
                                                       multi='basic',
                                                       lister='simple',
                                                       refresher=True,
                                                       orderby='name'
                                                       ).widget()
db.steps.tags.requires = IS_IN_DB(db, 'tags.id',
                                  db.tags._format, multiple=True)
db.steps.tags.widget = lambda field, value: AjaxSelect(field, value,
                                                       indx=2,
                                                       refresher=True,
                                                       multi='basic',
                                                       lister='simple',
                                                       orderby='tag_position'
                                                       ).widget()
db.steps.tags_secondary.requires = IS_EMPTY_OR(IS_IN_DB(db, 'tags.id',
                                               db.tags._format, multiple=True))
db.steps.tags_secondary.widget = lambda field, value: AjaxSelect(
    field, value,
    indx=3,
    refresher=True,
    multi='basic',
    lister='simple',
    orderby='tag'
).widget()
db.steps.tags_ahead.requires = IS_EMPTY_OR(IS_IN_DB(db, 'tags.id',
                                                    db.tags._format,
                                                    multiple=True))
db.steps.tags_ahead.widget = lambda field, value: AjaxSelect(field, value,
                                                             indx=4,
                                                             refresher=True,
                                                             multi='basic',
                                                             lister='simple',
                                                             orderby='tag'
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
db.steps.hints.requires = IS_EMPTY_OR(IS_IN_DB(db, 'step_hints.id',
                                               db.step_hints._format,
                                               multiple=True))
db.steps.hints.widget = lambda field, value: AjaxSelect(field, value,
                                                        indx=6,
                                                        refresher=True,
                                                        multi='basic',
                                                        lister='simple',
                                                        orderby='hint_label'
                                                        ).widget()
db.steps.instructions.requires = IS_EMPTY_OR(IS_IN_DB(
    db, 'step_instructions.id',
    db.step_instructions._format,
    multiple=True))
db.steps.instructions.widget = lambda field, value: \
    AjaxSelect(field, value,
               indx=7,
               refresher=True,
               multi='basic',
               lister='simple',
               orderby='instruction_label'
               ).widget()


db.steps.lemmas.requires = IS_EMPTY_OR(IS_IN_DB(db, 'lemmas.id',
                                                db.lemmas._format,
                                                multiple=True))
db.steps.lemmas.widget = lambda field, value: \
    AjaxSelect(field, value,
               indx=7,
               refresher=True,
               multi='basic',
               lister='simple',
               orderby='lemma'
               ).widget()

db.define_table('badges_begun',
                Field('name', 'reference auth_user', default=auth.user_id),
                Field('tag', 'reference tags'),
                Field('cat1', 'datetime', default=dtnow),
                Field('cat2', 'datetime'),
                Field('cat3', 'datetime'),
                Field('cat4', 'datetime'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(name)s, %(tag)s')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_bdgs_begun1
#   ON badges_begun (name)')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_bdgs_begun2
#   ON badges_begun (tag)')

db.define_table('tag_progress',
                Field('name', 'reference auth_user', default=auth.user_id,
                      unique=True),
                Field('latest_new', 'integer', default=1),  # order ranking
                # FIXME: change cat fields back to list:reference
                # (will require removing legacy tag ids)
                Field('cat1', 'list:integer'),
                Field('cat2', 'list:integer'),
                Field('cat3', 'list:integer'),
                Field('cat4', 'list:integer'),
                Field('rev1', 'list:integer'),
                Field('rev2', 'list:integer'),
                Field('rev3', 'list:integer'),
                Field('rev4', 'list:integer'),
                Field('all_choices', 'integer', default=0),
                Field('cat1_choices', 'integer', default=0),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(name)s, %(latest_new)s')
db.tag_progress.name.requires = IS_NOT_IN_DB(db, db.tag_progress.name)

db.define_table('path_styles',
                Field('style_label', unique=True),
                Field('components', 'list:string'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(style_label)s')

db.define_table('paths',
                Field('label'),
                Field('steps', 'list:reference steps'),
                Field('path_style', 'reference path_styles'),
                Field('path_tags', compute=lambda row: row.steps),
                # compute=lambda row: [tag for step in row.paths.steps
                # for tag in db.steps[step].tags]),
                Field('path_active', 'boolean',
                      compute=lambda row: all([s for s in row.paths.steps
                                               if (db.steps[s].status != 2) and
                                               db.steps[s].locations])),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(label)s')

# FIXME
# db.paths.tags_for_steps = Field.Virtual('tags_for_steps',
#                              lambda row: [tag for step in row.paths.steps
#                                           for tag in db.steps[step].tags])
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

"""
#class PathsVirtualFields(object):
    #def tags(self):
        #steprows = db(db.steps.id.belongs(self.paths.steps)).select()
        #nlists = [s.tags for s in steprows]
        #return list(chain.from_iterable(nlists))

    #def tags_secondary(self):
        #steprows = db(db.steps.id.belongs(self.paths.steps)).select()
        #nlists = [s.tags_secondary for s in steprows]
        #return list(chain.from_iterable(nlists))

    #def tags_ahead(self):
        #try:
            #steprows = db(db.steps.id.belongs(self.paths.steps)).select()
            #nlists = [s.tags_ahead for s in steprows]
            #return list(chain.from_iterable(nlists))
        #except TypeError:
            #return None

#db.paths.virtualfields.append(PathsVirtualFields())
"""

db.define_table('attempt_log',
                Field('name', 'reference auth_user', default=auth.user_id),
                Field('step', 'reference steps'),
                Field('in_path', 'reference paths'),  # was path (reserved)
                Field('score', 'double'),
                Field('dt_attempted', 'datetime', default=dtnow),
                Field('user_response', 'string'),
                Field('category_for_user', 'integer'),
                Field('selection_category', 'string'),
                Field('new_content', 'string'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                )
# db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_1 ON attempt_log (name);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_2 ON attempt_log (name,
# dt_attempted);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_3 ON attempt_log
# (dt_attempted);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_alog_3 ON attempt_log
# (in_path);')

db.define_table('tag_records',
                Field('name', 'reference auth_user', default=auth.user_id),
                Field('tag', 'reference tags'),
                Field('times_right', 'double'),
                Field('times_wrong', 'double'),
                Field('tlast_wrong', 'datetime', default=dtnow),
                Field('tlast_right', 'datetime', default=dtnow),
                Field('in_path', 'reference paths'),  # was path (reserved)
                Field('step', 'reference steps'),
                Field('secondary_right', 'list:string'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                Field('first_attempt', 'datetime'),
                )
# db.executesql('CREATE INDEX IF NOT EXISTS idx_trecs_1 ON tag_records (name,
# tag);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_trecs_2 ON tag_records (tag,
# name);')

db.define_table('bug_status',
                Field('status_label'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(status_label)s')

db.define_table('bugs',
                Field('step', 'reference steps'),
                Field('in_path', 'reference paths'),
                Field('map_location', 'reference locations'),
                Field('prompt', 'text'),
                Field('step_options', 'list:string'),
                Field('user_response'),
                Field('sample_answers', 'text'),
                Field('score', 'double'),
                Field('adjusted_score', 'double'),
                Field('log_id', 'reference attempt_log'),
                Field('user_name', 'reference auth_user',
                      default=auth.user_id),
                Field('user_comment', 'text'),
                Field('date_submitted', 'datetime', default=dtnow),
                Field('bug_status', 'reference bug_status', default=5),
                Field('admin_comment', 'text'),
                Field('public', 'boolean'),
                Field('deleted', 'boolean'),
                Field('flagged', 'boolean'),
                Field('pinned', 'boolean'),
                Field('popularity', 'list:reference auth_user'),
                Field('helpfulness', 'list:reference auth_user'),
                Field('posts', 'list:reference bug_posts'),
                Field('user_role', 'list:string'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(step)s')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_bugs_1 ON bugs (user_name,
# bug_status);')
db.bugs.step.requires = IS_EMPTY_OR(IS_IN_DB(db, 'steps.id',
                                             db.steps._format))
db.bugs.in_path.requires = IS_EMPTY_OR(IS_IN_DB(db, 'paths.id',
                                             db.paths._format))
db.bugs.log_id.requires = IS_EMPTY_OR(IS_IN_DB(db, 'attempt_log.id',
                                               db.attempt_log._format))

db.define_table('bugs_read_by_user',
                Field('user_id', 'reference auth_user', default=auth.user_id),
                Field('read_item_id', 'reference bugs'),
                Field('read_status', 'boolean'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow))

db.define_table('bug_posts',
                Field('poster', 'reference auth_user', default=auth.user_id),
                Field('poster_role', 'list:string'),
                Field('on_bug', 'reference bugs'),
                Field('dt_posted', 'datetime', default=dtnow),
                Field('thread_index', 'integer'),
                Field('post_body', 'text'),
                Field('public', 'boolean'),
                Field('hidden', 'list:reference auth_user'),
                Field('deleted', 'boolean'),
                Field('flagged', 'boolean'),
                Field('pinned', 'boolean'),
                Field('popularity', 'list:reference auth_user'),
                Field('helpfulness', 'list:reference auth_user'),
                Field('comments', 'list:reference bug_post_comments'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
)

db.define_table('posts_read_by_user',
                Field('user_id', 'reference auth_user', default=auth.user_id),
                Field('read_item_id', 'reference bug_posts'),
                Field('on_bug', 'reference bugs'),
                Field('read_status', 'boolean'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow))

db.define_table('bug_post_comments',
                Field('commenter', 'reference auth_user', default=auth.user_id),
                Field('commenter_role', 'list:string'),
                Field('on_post', 'reference bug_posts'),
                Field('dt_posted', 'datetime', default=dtnow),
                Field('thread_index', 'integer'),
                Field('comment_body', 'text'),
                Field('public', 'boolean'),
                Field('hidden', 'list:reference auth_user'),
                Field('deleted', 'boolean'),
                Field('flagged', 'boolean'),
                Field('pinned', 'boolean'),
                Field('popularity', 'list:reference auth_user'),
                Field('helpfulness', 'list:reference auth_user'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                )

db.define_table('comments_read_by_user',
                Field('user_id', 'reference auth_user', default=auth.user_id),
                Field('read_item_id', 'reference bug_post_comments'),
                Field('on_bug_post', 'reference bug_posts'),
                Field('on_bug', 'reference bugs'),
                Field('read_status', 'boolean'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow))

db.define_table('session_data',
                Field('name', 'reference auth_user'),  # default=auth.user_id
                Field('updated', 'datetime', default=dtnow),
                Field('session_start', 'datetime', default=dtnow),
                Field('blocks', 'text'),
                Field('path', 'reference paths'),
                Field('remaining_steps', 'list:reference steps'),
                Field('step_for_prompt', 'integer'),
                Field('step_for_reply', 'integer'),
                Field('completed_paths', 'text'),
                Field('cats_counter', 'integer'),
                Field('old_categories', 'text'),
                Field('tag_records', 'text'),
                Field('tag_progress', 'text'),
                Field('rank', 'integer'),
                Field('promoted', 'text'),
                Field('demoted', 'text'),
                Field('new_tags', 'string'),
                Field('session_start', 'datetime'),
                Field('loc', 'string'),
                Field('prev_loc', 'string'),
                Field('npc', 'reference npcs'),
                Field('prev_npc', 'reference npcs'),
                Field('past_quota', 'boolean'),
                Field('viewed_slides', 'boolean'),
                Field('reported_badges', 'boolean'),
                Field('reported_promotions', 'boolean'),
                Field('repeating', 'boolean'),
                Field('new_content', 'boolean'),
                Field('active_cat', 'integer'),
                Field('quota', 'integer'),
                Field('inventory', 'text'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(name)s')

db.define_table('weekly_user_stats',
                Field('name', 'reference auth_user', default=auth.user_id),
                Field('tag', 'reference tags'),
                Field('year', 'integer'),
                Field('month', 'integer'),
                Field('week', 'integer'),
                Field('week_start', 'datetime'),
                Field('week_end', 'datetime'),
                Field('day1_right', 'list:reference attempt_log'),
                Field('day2_right', 'list:reference attempt_log'),
                Field('day3_right', 'list:reference attempt_log'),
                Field('day4_right', 'list:reference attempt_log'),
                Field('day5_right', 'list:reference attempt_log'),
                Field('day6_right', 'list:reference attempt_log'),
                Field('day7_right', 'list:reference attempt_log'),
                Field('day1_wrong', 'list:reference attempt_log'),
                Field('day2_wrong', 'list:reference attempt_log'),
                Field('day3_wrong', 'list:reference attempt_log'),
                Field('day4_wrong', 'list:reference attempt_log'),
                Field('day5_wrong', 'list:reference attempt_log'),
                Field('day6_wrong', 'list:reference attempt_log'),
                Field('day7_wrong', 'list:reference attempt_log'),
                Field('done', 'integer', default=0),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(name)s, %(year)s, %(month)s, %(week)s')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_userstats_1 '
#              'ON user_stats (week, year, name);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_userstats_1 '
#              'ON user_stats (name, week, year);')
# db.executesql('CREATE INDEX IF NOT EXISTS idx_userstats_1 '
#              'ON user_stats (year, week, name);')

db.define_table('tagged_attempts_by_week',
                Field('name', 'reference auth_user', default=auth.user_id),
                Field('year', 'integer'),
                Field('month', 'integer'),
                Field('week', 'integer'),
                Field('tag_id', 'reference tags'),
                Field('attempts_right', 'list:reference attempt_log'),
                Field('attempts_wrong', 'list:reference attempt_log'),
                Field('weekstart', 'datetime')
                )

db.define_table('lessons',
                Field('title', 'string'),
                Field('video_url', 'text'),
                Field('pdf', 'upload', default='static/pdf-slides/'),
                Field('lesson_tags', 'list:reference tags'),
                Field('lesson_position', 'integer'),
                Field('active', 'boolean'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(title)s')
# db.lessons.title.requires = IS_NOT_IN_DB(db, 'lessons.title')
db.lessons.lesson_tags.widget = lambda field, value: AjaxSelect(field, value,
                                                         indx=1,
                                                         refresher=True,
                                                         multi='basic',
                                                         lister='simple',
                                                         sortable=False,
                                                         orderby='~id'
                                                         ).widget()

db.define_table('topics',
                Field('topic', 'string'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(topic)s')

db.define_table('content_pages',
                Field('title', 'string'),
                Field('content', 'text'),
                Field('first_authored', 'datetime', default=dtnow),
                Field('last_updated', 'datetime', default=dtnow),
                Field('author', 'reference auth_user', default=auth.user_id),
                Field('topics', 'list:reference topics'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow),
                format='%(title)s')


"""
HELPER TABLES
paths2steps ... follows C_UD of paths to create 1-1 relationshitp
steps2tags ... follows C_UD of steps to create 1-1 relationshitp
Joseph Boakye <jboakye@bwachi.com> Oct 10 2014
"""
db.define_table('step2tags',
                Field('step_id', 'reference steps'),
                Field('tag_id', 'reference tags'),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow))


db.define_table('path2steps',
                Field('path_id', 'reference paths'),
                Field('step_id', 'reference steps'),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow))

def insert_trigger_for_steps(f, given_step_id):
    # given_step_id is of <class 'gluon.dal.Reference'>
    step_id = int(given_step_id)
    local_f = f
    if (dict != type(local_f)):
        local_f = local_f.as_dict()
    if 'tags' in local_f:
        tag_ids = local_f['tags']
        for tag_id in tag_ids:
            if db(db.tags.id == tag_id).count() > 0:
                db.step2tags.insert(tag_id=tag_id, step_id=step_id)
            else:
                simple_obj_print(tag_id, "orphan tag:")
        db.commit()
    create_or_update_steps_inactive_locations(f, given_step_id)


def update_trigger_for_steps(s, f):
    for r in s.select():
        db(db.step2tags.step_id == r.id).delete()
        x = db(db.steps.id == r.id
               ).select(db.steps.tags, db.steps.locations).first()
        if x:
            tag_ids = (x.as_dict())['tags']
            locations = (x.as_dict())['locations']
            insert_trigger_for_steps({'tags': tag_ids, 'locations': locations},
                                     r.id)


def insert_trigger_for_paths(f, given_path_id):
    path_id = int(given_path_id)
    local_f = f
    if (dict != type(local_f)):
        local_f = local_f.as_dict()
    # delete all steps_inactive_locations data for this path
    old_steps_list = [s['step_id'] for s
                      in db(db.path2steps.path_id == given_path_id
                            ).select(db.path2steps.step_id).as_list()]
    db(db.steps_inactive_locations.step_id.belongs(old_steps_list)).delete()
    new_steps_list = []
    if 'steps' in local_f:
        step_ids = local_f['steps']
        for step_id in step_ids:
            new_steps_list.append(step_id)
            if db(db.steps.id == step_id).count() > 0:
                db.path2steps.insert(step_id=step_id, path_id=path_id)
            else:
                simple_obj_print(step_id, "orphan step:")
            db.commit()
    old_steps_list.extend(new_steps_list)
    for step_id in old_steps_list:
        step_locs = db.steps[step_id].as_dict()['locations']
        create_or_update_steps_inactive_locations({'locations': step_locs},
                                                  step_id)


def update_trigger_for_paths(s, f):
    for r in s.select():
        db(db.path2steps.path_id == r.id).delete()
        x = db(db.paths.id == r.id).select(db.paths.steps).first()
        if x:
            step_ids = (x.as_dict())['steps']
            insert_trigger_for_paths({'steps': step_ids}, r.id)


# take care of steps_inactive_locations
def before_delete_trigger_for_paths(s):
    old_steps_list = []
    for r in s.select():
        old_steps_list = [stp['step_id'] for stp
                          in db(db.path2steps.path_id == r.id
                                ).select(db.path2steps.step_id).as_list()]
    current.old_steps_list = old_steps_list


# take care of steps_inactive_locations
def after_delete_trigger_for_paths(s):
    for step_id in current.old_steps_list:
        step_locs = db.steps[step_id].as_dict()['locations']
        create_or_update_steps_inactive_locations({'locations': step_locs},
                                                  step_id)


# take care off steps_inactive_locations
def after_update_trigger_for_locations(s, f):
    local_f = f
    if (dict != type(local_f)):
        local_f = local_f.as_dict()
    simple_obj_print(local_f, 'new rochelle local_f is: ')
    if (('loc_active' in local_f) and (local_f['loc_active'])):
        for r in s.select():
            db(db.steps_inactive_locations.loc_id == r.id).delete()
        db.commit()
    # just set to inactive
    if (('loc_active' in local_f) and (not local_f['loc_active'])):
        # get all steps
        steps = db(db.steps.id > 0
                   ).select(db.steps.id, db.steps.locations).as_list()
        for r in s.select():
            for step in steps:
                while True:
                    locs = step['locations']
                    if (not locs):
                        break
                    if not(r.id in locs):
                        break
                    create_or_update_steps_inactive_locations({'locations':
                                                               locs},
                                                              step['id'])
                    break


def create_or_update_steps_inactive_locations(f, given_step_id):
    step_id = int(given_step_id)
    local_f = f
    if (dict != type(local_f)):
        local_f = local_f.as_dict()
    # delete everything for this step first
    db((db.steps_inactive_locations.step_id == step_id)).delete()
    if 'locations' in local_f:
        while True:
            loc_ids = local_f['locations']
            if (not loc_ids):
                break
            bad_loc_ids = []
            on_to_the_next = True
            for loc_id in loc_ids:
                if db((db.locations.id == loc_id) &
                      (db.locations.loc_active == 'T')
                      ).count() == 1:
                    on_to_the_next = False
                    break
                else:
                    bad_loc_ids.append(loc_id)
            if not on_to_the_next:
                break
            for loc_id in bad_loc_ids:
                db((db.steps_inactive_locations.loc_id == loc_id) &
                   (db.steps_inactive_locations.step_id == step_id)
                   ).delete()
                loc_data = {}
                loc_data['step_id'] = step_id
                loc_data['loc_id'] = loc_id
                get_steps_inactive_locations_fields(loc_data)
                simple_obj_print(loc_data, "troy: loc data")
                db.steps_inactive_locations.insert(
                    loc_id=loc_data['loc_id'],
                    step_id=loc_data['step_id'],
                    step_desc=loc_data['step_desc'],
                    loc_desc=loc_data['loc_desc'],
                    in_paths=loc_data['in_paths'])
            break  # from while true
    db.commit()


def get_steps_inactive_locations_fields(id_data):
    """
    input: {step_id: xx, loc_id: xxx}
    """
    id_data['step_desc'] = (db.steps[id_data['step_id']]).as_dict()['prompt']
    id_data['loc_desc'] = (
        db.locations[id_data['loc_id']]).as_dict()['map_location']
    id_data['in_paths'] = [p['path_id'] for p
                           in db(db.path2steps.step_id == id_data['step_id']
                                 ).select(db.path2steps.path_id).as_list()]
    return True


# no need for delete ... will be taken care of by foreign key
db.steps._after_insert.append(
    lambda f, given_id: insert_trigger_for_steps(f, given_id))
db.steps._after_update.append(
    lambda s, f: update_trigger_for_steps(s, f))
db.paths._after_insert.append(
    lambda f, given_id: insert_trigger_for_paths(f, given_id))
db.paths._after_update.append(
    lambda s, f: update_trigger_for_paths(s, f))
db.paths._before_delete.append(
    lambda s: before_delete_trigger_for_paths(s))
db.paths._after_delete.append(
    lambda s: after_delete_trigger_for_paths(s))
db.locations._after_update.append(
    lambda s, f: after_update_trigger_for_locations(s, f))

# exceptions .... when the bug table is not enough
db.define_table('exceptions',
                Field('step', 'text'),
                Field('in_path', 'text'),
                Field('map_location', 'text'),
                Field('user_response', 'text'),
                Field('score', 'double'),
                Field('log_id', 'text'),
                Field('user_name', db.auth_user, default=auth.user_id),
                Field('date_submitted', 'datetime', default=dtnow),
                Field('bug_status', db.bug_status, default=5),
                Field('admin_comment', 'text'),
                Field('hidden', 'boolean'),
                Field('uuid', length=64, default=lambda: str(uuid.uuid4())),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow)
                )

# exception_steps  .... steps with all inactive locations
db.define_table('steps_inactive_locations',
                Field('step_id', 'reference steps'),
                Field('loc_id', 'reference locations'),
                Field('step_desc', 'text'),
                Field('loc_desc', 'text'),
                Field('in_paths', 'list:integer'),
                Field('modified_on', 'datetime', default=dtnow, update=dtnow))

"""
These functions create step2tags and path2steps data for
legacy paths and steps.
They only need to be ran once after which they SHOULD be commented out
Joseph Boakye <jboakye@bwachi.com>
Oct 11, 2014
---------------------  run once for legacy system -----------------

def create_step2tags_from_steps():
    db.step2tags.truncate()
    for row in db(db.steps.id > 0).select():
        insert_trigger_for_steps({'tags': row.tags},row.id)
    return True
create_step2tags_from_steps()

def create_path2steps_from_paths():
    db.path2steps.truncate()
    for row in db(db.paths.id > 0).select():
        insert_trigger_for_paths({'steps': row.steps},row.id)
    return True
create_path2steps_from_paths()

def create_steps_inactive_locations_for_steps():
    print "---called martha---"
    db(db.steps_inactive_locations.id > 0).delete()
    print "---called martha 2---"
    steps = db(
        db.steps.id > 0).select(db.steps.id,db.steps.locations).as_list()
    print "---called martha 3---"
    for step in steps:
        print "---called martha 4---"
        locs = step['locations']
        create_or_update_steps_inactive_locations({'locations':
            locs},step['id'])
    db.commit()
create_steps_inactive_locations_for_steps()

-----------------  end run once for legacy system -------------
"""


# Badges for header ===========================================================
try:
    db = current.db
    print(auth.user_id)
    bug_rows = db((db.bugs.user_name == auth.user_id) &
                  (db.bugs.deleted == False) &
                  (db.bugs.admin_comment != '')).select()
                  #  FIXME: (db.bugs.hidden == False)
    bug_count = len(bug_rows)
    print(bug_count, "bugs")
    if bug_count > 0:
        response.badges = SPAN(A(I(_class='fa fa-inbox'), "  ",
                                 SPAN(bug_count),
                                 _href='/paideia/default/user/profile'
                                 '#tab_bug_reports',
                                 _class='badge',
                                 _id='unread-counter'),
                               _class='badge-wrapper')
    else:
        pass
except Exception as e:
    traceback.print_exc()
