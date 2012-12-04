# coding: utf8
if 0:
    from gluon import current, UL, LI, A, URL, SPAN
    db, auth, session = current.db, current.auth, current.session
import datetime
import calendar
from pytz import timezone
import pprint

# TODO: rework to use plugin_listandedit as a widget


@auth.requires_membership(role='administrators')
def user():
    users = db(db.auth_user.id == db.tag_progress.name).select(orderby=db.auth_user.last_name)

    # TODO: move this logic to stats module
    today = datetime.date.today()
    monthcal = calendar.monthcalendar(today.year, today.month)
    this_week = [w for w in monthcal if today.day in w][0]
    pprint.pprint(this_week)
    last_week_month = today.month
    weekindex = monthcal.index(this_week)
    if weekindex != 0:
        last_week = monthcal[weekindex - 1]
    else:
        lastmonth = today - datetime.timedelta(months=1)
        lastmonth = lastmonth.month
        lastmonthcal = calendar.monthcalendar(today.year, lastmonth)
        last_week = lastmonthcal[-1]
        if last_week == this_week:
            last_week = lastmonthcal[-2]
        # TODO: put previous month here for last_week_month
    pprint.pprint(last_week)

    countlist = {}
    for user in users:
        print user.auth_user.last_name
        logs = db(db.attempt_log.name == user.auth_user.id).select()
        tz_name = user.auth_user.time_zone
        if tz_name is None:
            tz_name = 'America/Toronto'
        tz = timezone(tz_name)
        now_local = tz.fromutc(datetime.datetime.utcnow())

        this_weeklist = []
        for day in this_week:
            if day < 10:
                day = '0{}'.format(day) #avoid error due to invalid day num
            datestring = '{}{}{}'.format(day, today.month, today.year)
            print datestring
            date = datetime.datetime.strptime(datestring, "%d%m%Y").date()
            print date
            daylogs = logs.find(lambda row:
                                tz.fromutc(row.dt_attempted).date() - date
                                == datetime.timedelta(days=0))
            print 'logs for day', day
            print daylogs
            count = len(daylogs)
            this_weeklist.append((day, count))
        tw_gooddays = len([d[0] for d in this_weeklist if d[1] >= 20])

        last_weeklist = []
        for day in last_week:
            datestring = '{}{}{}'.format(day, today.month, today.year)
            print datestring
            date = datetime.datetime.strptime(datestring, "%d%m%Y").date()
            print date
            daylogs = logs.find(lambda row:
                                tz.fromutc(row.dt_attempted).date() - date
                                == datetime.timedelta(days=0))
            count = len(daylogs)
            last_weeklist.append((day, count))
        lw_gooddays = len([d[0] for d in last_weeklist if d[1] >= 20])

        countlist[user.auth_user.id] = (tw_gooddays, lw_gooddays)
    pprint.pprint(countlist)

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
