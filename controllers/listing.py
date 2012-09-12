# coding: utf8
if 0:
    from gluon import current, UL, LI, A, URL
    db, auth, session = current.db, current.auth, current.session

# TODO: rework to use plugin_listandedit as a widget


@auth.requires_membership(role='administrators')
def user():
    users = db().select(db.auth_user.ALL, orderby=db.auth_user.last_name)
    return dict(users=users)


# TODO: rework using plugin_bloglet
def news():
    newslist = db(db.news).select(orderby=~db.news.date_submitted)
    if db(
        (db.auth_membership.user_id == auth.user_id) &
        (db.auth_membership.group_id == 1)
    ).select():
        button = A('new story',
                    _href=URL('creating', 'news.load'),
                    cid='modal_frame',
                    _class='create_link news_create_link')
    else:
        button = ''
    return dict(newslist=newslist, button=button)


def slides():
    slidelist = db(db.plugin_slider_decks.id > 0).select(
                                    orderby=db.plugin_slider_decks.position)
    slides = UL()
    for s in slidelist:
        slides.append(LI(A(s.deck_name,
                            _href=URL('plugin_slider',
                                'start_deck.load',
                                args=[s.id]),
                            cid='slideframe')
                        ))
    if auth.is_logged_in():
        if 'view_slides' in session.walk:
            del session.walk['view_slides']

    return dict(slides=slides)
