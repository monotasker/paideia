
if 0:
    from gluon import IMG, current
    session = current.session
    request = current.request

def open(self):
    """
    Create the image choosing widget to populate the modal window in plugin_img_chooser.
    """
    table = request.vars['table']
    uploadfield = request.vars['uploadfield']
    titlefield = request.vars['titlefield']
    descrfield = request.vars['descrfield']

    query = db(db[table]).select()
    images = []
    for row in query:
        img = IMG(_src=URL('download', args=row.uploadfield),
                  _alt=row['titlefield'],
                  _title=row['titlefield'],
                  _class='plugin_img_chooser_thumbnail')


    return images
