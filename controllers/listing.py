# coding: utf8
'''
Controller supplying data for views that list users (for admin) and list slides.

TODO: rationalize this controller organization
'''
if 0:
    from gluon import INPUT, UL, LI, A, URL, SPAN, SELECT, OPTION, FORM
    from gluon import current, redirect
    db, auth, session = current.db, current.auth, current.session
    request, response = current.request, current.response
import datetime
import calendar
import traceback
from pytz import timezone
import itertools


@auth.requires_membership(role='administrators')
def user():
    print 'starting user ----------------------------------'
    print 'user is', auth.user_id
    # TODO: magic number here -- admin group is 1
    admins = db(db.auth_membership.group_id == 1
                ).select(db.auth_membership.user_id).as_list()
    admins = [a['user_id'] for a in admins]
    admins.append(auth.user_id)
    print 'admins', admins
    myclasses = db(db.auth_group.course_instructor.belongs(admins)
                   ).select().as_list()
    chooser = FORM(SELECT(_id='class_chooser_select'), _id='class_chooser')
    for m in myclasses:
        optstring = '{} {} {}, {}'.format(m['academic_year'], m['term'],
                                          m['course_section'], m['institution'])
        chooser[0].append(OPTION(optstring, _value=m['id']))
    chooser.append(INPUT(_type='submit'))
    print 'returning------------------------------------------'
    return {'chooser': chooser, 'row': myclasses[0]}


@auth.requires_membership(role='administrators')
def remove_user():
    '''
    Removes a user from membership in a course section and refreshes the list.

    Expects two variables to be supplied via request.vars:

        uid         the id of the user to be removed (from db.auth_user)

        classid     the id of the class from which s/he should
                    be removed (from db.classes)
    '''
    uid = request.vars.uid
    classid = request.vars.classid
    q = db((db.auth_membership.user_id == uid) &
           (db.auth_membership.group_id == classid))
    print 'found', q.count(), 'records'
    q.delete()
    print 'classid is', classid
    redirect(URL('userlist.load', vars={'value': classid}))


def week_bounds():
    '''
    Return datetime objects representing the last day of this week and previous.
    '''
    today = datetime.datetime.utcnow()
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

    return lastweek, lw_firstday, thisweek


def get_offset(user):
    '''
    Return the user's offset from utc time based on their time zone.
    '''
    today = datetime.datetime.utcnow()
    now = timezone('UTC').localize(today)
    tz_name = user.auth_user.time_zone if user.auth_user.time_zone \
        else 'America/Toronto'
    offset = now - timezone(tz_name).localize(today)  # when to use "ambiguous"?
    # alternative is to do tz.fromutc(datetime)

    return offset


@auth.requires_membership(role='administrators')
def userlist():
    try:
        # define minimum daily required # of paths
        # TODO: add class selection here so that I can narrow these figures
        try:
            print 'value is', request.vars.value
            row = db.auth_group[request.vars.value]
        except:
            print traceback.format_exc(5)
            row = db(db.auth_group.course_instructor == auth.user_id
                     ).select().first()
        target = row['paths_per_day']
        freq = row['days_per_week']

        member_sel = db(db.auth_membership.group_id == row['id']).select()
        members = [m['user_id'] for m in member_sel]
        users = db((db.auth_user.id == db.tag_progress.name) &
                   (db.auth_user.id.belongs([m['id'] for m in members]))
                   ).select(orderby=db.auth_user.last_name)

        lastweek, lw_firstday, thisweek = week_bounds()

        logs = db((db.attempt_log.name.belongs([u.auth_user.id for u in users])) &
                  (db.attempt_log.dt_attempted > lw_firstday)
                  ).select(db.attempt_log.dt_attempted, db.attempt_log.name)

        countlist = {}
        for user in users:
            offset = get_offset(user)

            spans = [{'days': thisweek, 'count': 0, 'min_count': 0},
                     {'days': lastweek, 'count': 0, 'min_count': 0}]
            for span in spans:
                for day in span['days']:
                    mylogs = logs.find(lambda row: row.name == user.auth_user.id)
                    daycount = len([l for l in mylogs if (l['dt_attempted'] - offset).day == day])
                    #count = len(logs.find(lambda row: tz.fromutc(row.dt_attempted).day == day))

                    if daycount > 0:
                        span['count'] += 1
                    if daycount >= target:
                        span['min_count'] += 1

            countlist[user.auth_user.id] = (spans[0]['count'], spans[0]['min_count'],
                                            spans[1]['count'], spans[1]['min_count'])
        return {'users': users, 'countlist': countlist,
                'target': target, 'freq': freq, 'classid': row['id']}
    except Exception:
        print traceback.format_exc(5)


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
                                    orderby=db.plugin_slider_decks.deck_position)
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
    # TODO: re-implement this flag to force users to view new slide decks
    #if auth.is_logged_in():
        #if session.walk and 'view_slides' in session.walk:
            #del session.walk['view_slides']

    return dict(slides=slides)
