# coding: utf8
if 0:
    from gluon import current, UL, LI, A, URL, SPAN, SELECT, OPTION, FORM, INPUT
    db, auth, session = current.db, current.auth, current.session
    request, response = current.request, current.response
import datetime
import calendar
from pytz import timezone
import itertools


@auth.requires_membership(role='administrators')
def user():
    myclasses = db(db.classes.instructor == auth.user_id).select()
    chooser = FORM(SELECT(_id='class_chooser'), _id='class_chooser')
    for m in myclasses:
        optstring = '{} {} {}, {}'.format(m.year, m.term,
                                          m.section, m.institution)
        chooser[0].append(OPTION(optstring, _value=m.id))
    chooser.append(INPUT(_type='submit'))

    return {'chooser': chooser, 'row': myclasses[0].id}


@auth.requires_membership(role='administrators')
def userlist():
    # define minimum daily required # of paths
    #TODO: add class selection here so that I can narrow these figures
    print 'starting'
    row = db.classes(request.vars.row)
    print row
    target = row.paths_per_day
    freq = row.days_per_week
    # find dates for this week, last week, and earliest possible span
    today = datetime.datetime.utcnow()
    now = timezone('UTC').localize(today)
    thismonth = calendar.monthcalendar(today.year, today.month)

    thisweek = [w for w in thismonth if today.day in w][0]
    today_index = thisweek.index(today.day)
    tw_index = thismonth.index(thisweek)

    lastweek = thismonth[tw_index - 1]
    delta = datetime.timedelta(days=(8 + today_index))
    lw_firstday = today - delta

    tw_prev = None
    if 0 in thisweek:
        if thisweek.index(0) < thisweek.index(today.day):
            lastmonth = calendar.monthcalendar(today.year, today.month - 1)
            tw_prev = lastmonth[-1]
            lastweek = lastmonth[-2]
            thisweek = [d for d in itertools.chain(thisweek, tw_prev) if d != 0]

    lw_prev = None
    if 0 in lastweek:
        lastmonth = calendar.monthcalendar(today.year, today.month - 1)
        lw_prev = lastmonth[-1]
        lastweek = [d for d in itertools.chain(lastweek, lw_prev) if d != 0]

    users = db(db.auth_user.id == db.tag_progress.name).select(
                                            orderby=db.auth_user.last_name)

    logs = db((db.attempt_log.name.belongs([u.auth_user.id for u in users])) &
            (db.attempt_log.dt_attempted > lw_firstday)).select(db.attempt_log.dt_attempted)

    countlist = {}
    for user in users:
        print 'user', user.auth_user.id
        tz_name = user.auth_user.time_zone
        if tz_name is None:
            tz_name = 'America/Toronto'
        tz = timezone(tz_name)
        offset = now - tz.localize(today)  # How do I know when to use "ambiguous" instead?
        # alternative is to do tz.fromutc(datetime)
        tw_count = 0
        for day in thisweek:
            daycount = len([l for l in logs if (l.dt_attempted - offset).day == day])
            #count = len(logs.find(lambda row: tz.fromutc(row.dt_attempted).day == day))
            if daycount > 0:
                tw_count += 1
        print tw_count, '\n'

        tw_min_count = 0
        for day in thisweek:
            daycount = len([l for l in logs if (l.dt_attempted - offset).day == day])
            #count = len(logs.find(lambda row: tz.fromutc(row.dt_attempted).day == day))
            if daycount >= target:
                tw_count += 1
        print tw_count, '\n'

        lw_count = 0
        for day in lastweek:
            daycount = len([l for l in logs if (l.dt_attempted - offset).day == day])
            if daycount > 0:
                lw_count += 1
        print lw_count

        lw_min_count = 0
        for day in lastweek:
            daycount = len([l for l in logs if (l.dt_attempted - offset).day == day])
            if daycount >= target:
                lw_count += 1
        print lw_count

        countlist[user.auth_user.id] = (tw_count, tw_min_count,
                                        lw_count, lw_min_count)

    return {'users': users, 'countlist': countlist,
            'target': target, 'freq': freq}


# TODO: rework using plugin_bloglet
def news():
    """
    Display site news stories in a view.
    """
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
    """
    Assemble a list of links to the slide sets and send to the view.
    """
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
