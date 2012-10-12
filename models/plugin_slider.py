from plugin_ajaxselect import AjaxSelect
if 0:
    from gluon import current, URL, Field, IS_IN_DB
    response, db = current.response, current.db
import datetime

#js file necessary for AjaxSelect widget
response.files.insert(5, URL('static',
                          'plugin_ajaxselect/plugin_ajaxselect.js'))
response.files.append(URL('static', 'plugin_ajaxselect/plugin_ajaxselect.css'))
response.files.append(URL('static', 'plugin_slider/plugin_slider.css'))

db.define_table('plugin_slider_themes',
    Field('theme_name', 'string'),
    Field('description', 'text'),
    format='%(theme_name)s'
    )

db.define_table('plugin_slider_slides',
    Field('slide_name', 'string'),
    Field('content', 'text'),
    Field('theme', 'list:reference plugin_slider_themes'),
    Field('updated', 'datetime', default=datetime.datetime.utcnow()),
    format='%(slide_name)s'
    )
db.plugin_slider_slides.theme.requires = IS_IN_DB(db,
                                    'plugin_slider_themes.id',
                                    db.plugin_slider_themes._format,
                                    multiple=True)

db.define_table('plugin_slider_decks',
    Field('deck_name', 'string'),
    Field('deck_slides', 'list:reference plugin_slider_slides'),
    Field('theme', 'list:reference plugin_slider_themes'),
    Field('position', 'integer'),
    format='%(deck_name)s'
    )
db.plugin_slider_decks.deck_slides.requires = IS_IN_DB(db,
                                    'plugin_slider_slides.id',
                                    db.plugin_slider_slides._format,
                                    multiple=True)
db.plugin_slider_decks.theme.requires = IS_IN_DB(db,
                                    'plugin_slider_themes.id',
                                    db.plugin_slider_themes._format,
                                    multiple=True)
db.plugin_slider_decks.deck_slides.widget = lambda field, value: \
                                    AjaxSelect().widget(
                                        field, value, 'plugin_slider_slides',
                                        refresher=True,
                                        multi='basic',
                                        lister='editlinks',
                                        sortable='true')
