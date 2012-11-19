
def ICONLINK(title, text, icon):
    linktitle = '{}_icon'.format(title)
    link_classes = '{} icon-only icon-{}'.format(linktitle, icon)
    link = A(SPAN(text, _class='accessible'),
                _href='#',
                _class=link_classes,
                _id=linktitle)
    return link

def TOOLTIP(title, text, content, icon=None):
    '''
    Build and return a tooltip widget with the supplied content.
    '''
    # build widget wrapper
    wrapper_title = '{}_wrapper'.format(title)
    wrapper_classes = '{} tip_wrapper'.format(wrapper_title)
    tip_wrapper = DIV(_class=wrapper_classes, _id=wrapper_title)

    # add tip trigger link
    if icon:
        tip_wrapper.append(ICONLINK(title, text, icon))
    else:
        trigger_title = '{}_trigger'.format(title)
        trigger_classes = '{} trigger'.format(trigger_title)
        tip_wrapper.append(A(text, _classes=trigger_classes, _id=trigger_title))

    # add tip content
    tip_classes = '{} tip'.format(title)
    tip_wrapper.append(DIV(content, _class=tip_classes, _id=title))

    return tip_wrapper
