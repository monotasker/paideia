if 0:
    from gluon import current, URL
    response = current.response


response.files.append(URL('static',
            'plugin_listandedit/plugin_listandedit.css'))
response.files.append(URL('static',
            'plugin_listandedit/plugin_listandedit.js'))


def plugin_listandedit():
    '''
    Public interface method to call in views in order to embed the
    plugin_listandedit widget.
    '''
    return LOAD('plugin_listandedit', 'widget.load', ajax=True)

