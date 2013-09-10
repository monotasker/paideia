
"""
A web2py plugin providing a modal widget to select an uploaded file and
insert a link to that file in the active form field at the current cursor
position.

Author: Ian W. Scott (scottianw@gmail.com)
License: GPL 3.0

Linux Installation

At a terminal, run the following commands:

cd {path to web2py application root directory}
ln -s plugins/plugin_img_chooser/controllers/plugin_img_chooser.py controllers/
ln -s plugins/plugin_img_chooser/modules/plugin_img_chooser.py modules/
ln -s plugins/plugin_img_chooser/views/plugin_img_chooser/ views/plugin_img_chooser
ln -s plugins/plugin_img_chooser/static/plugin_img_chooser/ static/plugin_img_chooser

Usage

Call like this:
{app directory}/plugin_img_chooser/chooser.load?tb="images"&u="image"&d="description"&t="title"
"""

if 0:
    from gluon import IMG, current, URL, A, SPAN
    session = current.session
    request = current.request
    db = current.db


def chooser(self):
    """
    Create the image choosing widget to populate the modal window in plugin_img_chooser.
    """
    table = request.vars['tb']
    uploadfield = request.vars['u']
    titlefield = request.vars['t']
    descrfield = request.vars['d']

    query = db(db[table].id > 0).select()
    images = []
    for row in query:
        the_url = URL('download', args=row[uploadfield])
        img = {'title': A(row[titlefield], _href=the_url),
               'thumb': IMG(_src=the_url,
                           _alt=row[descrfield],
                           _title=row[titlefield],
                           _class='plugin_img_chooser_thumbnail'),
               'description': SPAN(row[descrfield])}
        images.append(img)

    return {'images': images}
