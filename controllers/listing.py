# coding: utf8
if 0:
    from gluon import current, UL, LI, A, URL, SPAN
    db, auth, session = current.db, current.auth, current.session
import datetime

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
    debug = True
    slidelist = db(db.plugin_slider_decks.id > 0).select(
                                    orderby=db.plugin_slider_decks.position)
    progress = db(db.tag_progress.name == auth.user_id).select().first()

    slides = UL()
    for s in slidelist:
        badges = db((db.tags.slides.contains(s.id))
                      & (db.badges.tag == db.tags.id)).select()
        classes = ''
        try:
            if s.updated and (datetime.datetime.utcnow() - s.updated
                              < datetime.timedelta(days=14)):
                classes = 'plugin_slider_new '
        except Exception:
            pass
        if progress and [t.tags.id for t in badges
                            if t.tags.position <= progress.latest_new]:
            classes += 'plugin_slider_active '
        try:
            slides.append(LI(A(s.deck_name,
                                _href=URL('plugin_slider',
                                    'start_deck.load',
                                    args=[s.id]),
                                cid='slideframe',
                                _class=classes)
                            ))
            for b in badges:
                if debug: print b.badges.badge_name
                slides[-1].append(SPAN(b.badges.badge_name))
        except Exception, e:
            print type(e), e
    if auth.is_logged_in():
        if session.walk and 'view_slides' in session.walk:
            del session.walk['view_slides']

    return dict(slides=slides)
