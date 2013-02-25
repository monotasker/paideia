# coding: utf8
if 0:
    from gluon import current, UL, LI, A, URL, SPAN
    db, auth, session = current.db, current.auth, current.session
import datetime
import calendar
from pytz import timezone
import pprint
from timeit import Timer

# TODO: rework to use plugin_listandedit as a widget


@auth.requires_membership(role='administrators')
def user():
    # define minimum daily required # of paths
    target = 20
    # find dates for this week, last week, and earliest possible span
    today = datetime.datetime.today()
    thismonth = calendar.monthcalendar(today.year, today.month)
    thisweek = [w for w in thismonth if today.day in w][0]
    today_index = thisweek.index(today.day)
    tw_index = thismonth.index(thisweek)
    lastweek = thismonth[tw_index - 1]
    delta = datetime.timedelta(days = (8+today_index))
    lw_firstday = today - delta

    tw_prev = None
    if 0 in thisweek:
        if thisweek.index(0) < thisweek.index(today.day):
            lastmonth = calendar.monthcalendar(today.year, today.month - 1)
            tw_prev = lastmonth[-1]
            lastweek = lastmonth[-2]

    lw_prev = None
    if 0 in lastweek:
        lastmonth = calendar.monthcalendar(today.year, today.month - 1)
        lw_prev = lastmonth[-1]

    users = db(db.auth_user.id == db.tag_progress.name).select(
                                            orderby=db.auth_user.last_name)
    logs = db((db.attempt_log.name.belongs([u.auth_user.id for u in users])) &
            (db.attempt_log.dt_attempted > lw_firstday)).select()
    countlist = {}
    for user in users:
        tz_name = user.auth_user.time_zone
        if tz_name is None:
            tz_name = 'America/Toronto'
        tz = timezone(tz_name)

        tw_count = 0
        if tw_prev:
            thisweek = [d for d in thisweek if d != 0]
            tw_prev = [d for d in tw_prev if d != 0]
            thisweek += tw_prev
        for day in thisweek:
            count = len(logs.find(lambda row: tz.fromutc(row.dt_attempted).day == day))
            if count >= target:
                tw_count += 1

        lw_count = 0
        if lw_prev:
            lastweek = [d for d in lastweek if d != 0]
            lw_prev = [d for d in lw_prev if d != 0]
            lastweek += lw_prev
        for day in lastweek:
            count = len(logs.find(lambda row: tz.fromutc(row.dt_attempted).day == day))
            if count >= target:
                lw_count += 1

        countlist[user.auth_user.id] = (tw_count, lw_count)

    return dict(users=users, countlist=countlist)


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
    debug = False
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
