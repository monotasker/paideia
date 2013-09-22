from gluon import A, URL


def IMG_CHOOSER(table=None, downloadfield=None,
                titlefield=None, descrfield=None):
    """
    Helper object that returns a link to launch an image-choosing widget.

    This is for use especially with markdown, markmin, and other plain text
    data types in which one might need to insert the file location for an
    uploaded image. Rather than require that the user remember the file name,
    which may be mangled on upload, the widget allows the user to choose the
    file visually or by readable title.
    """
    urlvars = {'table': table,
               'downloadfield': downloadfield,
               'titlefield': titlefield,
               'descrfield': descrfield}
    link = A('Insert image',
             _href=URL('plugin_img_chooser', 'open.load', vars=urlvars),
             _class='plugin_img_chooser_launchlink',
             cid='plugin_img_chooser_modal')
    return link
