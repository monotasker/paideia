# coding: utf8
'''
Controller supplying data for views that list users (for admin) and list slides.

TODO: rationalize this controller organization
'''
#JOB ... this line is not liked by python ... oct 21, 2014
#from test.pickletester import myclasses
import datetime
import traceback
from paideia_stats import make_classlist, make_unregistered_list
# from pprint import pprint
# from dateutil.parser import parse
# from operator import itemgetter
if 0:
    from gluon import INPUT, A, URL, SPAN, SELECT, OPTION, FORM
    from gluon import TABLE, TR, TD
    from gluon import current, redirect
    db, auth, session = current.db, current.auth, current.session
    request, response = current.request, current.response


# @auth.requires_membership(138)
def user():
    # TODO: magic number here -- admin group is 1
    admins = db(db.auth_membership.group_id == 1
                ).select(db.auth_membership.user_id).as_list()
    admins = [a['user_id'] for a in admins]
    admins.append(auth.user_id)
    if auth.user_id in admins:
        myclasses = db(db.classes.instructor != None).select()
    else:
        myclasses = db(db.classes.instructor == auth.user_id
                       ).select()
    myclasses = myclasses.as_list()
    print type(myclasses[0]), myclasses[0]
    myclasses = sorted(myclasses,
                       key=lambda x: (x['academic_year'], x['term']),
                       reverse=True)
    print 'myclasses:', len(myclasses)

    chooser = FORM(SELECT(_name='agid',
                          _id='class-chooser',
                          *[OPTION('{} {}, section {}, {}'.format(m['academic_year'],
                                                         m['term'],
                                                         m['course_section'],
                                                         m['institution']),
                                   _value=m['id'])
                            for m in myclasses
                            ],
                          _class='form-control'
                          ),
                    _id='class_chooser')
    chooser[0].append(OPTION('Currently unenrolled but active', _value='unregistered-active'))
    chooser[0].append(OPTION('All unenrolled users', _value='unregistered-inactive'))
    chooser.append(INPUT(_type='submit', _id='chooser_submit'))

    return {'chooser': chooser, 'classid': myclasses[0]['id']}


@auth.requires_membership(role='administrators')
def promote_user():
    '''
    Move the specified user ahead one badge set.
    '''
    uid = request.vars.uid
    classid = request.vars.classid
    tp = db(db.tag_progress.name == uid).select().first()
    oldrank = tp['latest_new']
    # move remaining cat1 tags forward to cat2
    old_level1 = tp['cat1']
    print 'old_level1', old_level1
    level2 = tp['cat2']
    print 'level2', level2
    level2.extend(old_level1)
    print 'level2', level2
    tp.update_record(latest_new=(oldrank + 1),
                     cat1=[],
                     cat2=level2)
    for tag in old_level1:
        db(db.badges_begun.tag == tag).update(cat2=datetime.datetime.now())
    response.flash = 'User moved ahead to set {}'.format(oldrank + 1)
    redirect(URL('userlist.load', vars={'value': classid}))


@auth.requires_membership(role='administrators')
def demote_user():
    '''
    Move the specified user back one badge set.

    Removes all tag_records rows for the user which cover tags in the demoted
    tag set.
    '''
    uid = request.vars.uid
    classid = request.vars.classid

    tp = db(db.tag_progress.name == uid).select().first()
    oldrank = tp['latest_new']
    old_ranktags = db(db.tags.tag_position == oldrank).select()
    old_taglist = [t['id'] for t in old_ranktags]
    new_ranktags = db(db.tags.tag_position == (oldrank - 1)).select()
    new_taglist = [t['id'] for t in new_ranktags]

    old_level2 = tp['cat2']
    old_level3 = tp['cat3']
    old_level4 = tp['cat4']
    level1 = tp['cat1']
    new_level2 = [t for t in old_level2 if t not in new_taglist]
    new_level3 = [t for t in old_level3 if t not in new_taglist]
    new_level4 = [t for t in old_level4 if t not in new_taglist]
    level1.extend(new_taglist)
    tp.update_record(latest_new=(oldrank - 1),
                     cat1=level1,
                     cat2=new_level2,
                     cat3=new_level3,
                     cat4=new_level4)

    # TODO: do I have to somehow mark the actual log entries somehow as
    # removed? Should they be backed up?
    print 'demoting tags:', old_taglist
    trecs = db(db.tag_records.tag.belongs(old_taglist))
    print 'found trecs:', trecs.count()
    trecs.delete()

    for tag in new_ranktags:
        db(db.badges_begun.tag == tag).update(cat1=datetime.datetime.now(),
                                              cat2=None)

    response.flash = 'User moved back to set {}'.format(oldrank - 1)
    redirect(URL('userlist.load', vars={'value': classid}))


@auth.requires_membership(role='administrators')
def add_user():
    '''
    Adds one or more users to the specified course section.
    '''
    users = request.vars.value
    print 'add_user: value is', users


@auth.requires_membership('instructors', 'administrators')
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
    q = db((db.class_membership.name == uid) &
           (db.class_membership.class_section == classid))
    q.delete()
    redirect(URL('userlist.load', vars={'value': classid}))


@auth.requires(auth.has_membership('instructors') |
               auth.has_membership('administrators'))
def userlist():
    print 'agid', request.vars.agid, type(request.vars.agid)
    # if isinstance(request.vars.agid, (int, long)):  # selecting class
    try:
        int(request.vars.agid)
        try:
            classrow = db.classes[request.vars.agid].as_dict()
        except:  # choose a class to display as default
            print traceback.format_exc(5)
            classrow = db(db.classes.instructor == auth.user_id
                          ).select().last().as_dict()
        target = classrow['paths_per_day']
        freq = classrow['days_per_week']
        title = '{} {} {}, {}'.format(classrow['academic_year'], classrow['term'],
                                      classrow['course_section'],
                                      classrow['institution'])
        member_sel = db(db.class_membership.class_section == classrow['id']).select()
        users = db((db.auth_user.id == db.tag_progress.name) &
                   (db.auth_user.id.belongs([m['name'] for m in member_sel]))
                   ).select(orderby=db.auth_user.last_name)
        start_date = classrow['start_date']
        end_date = classrow['end_date']
        classlist = make_classlist(member_sel, users, start_date,
                                   end_date, target, classrow)
    except Exception as e:  # selecting outside of current class registrants
        print e
        target = 0
        freq = 0
        classrow = {'id': None}
        all = db(db.auth_user).select()
        registered_current = db((db.class_membership.class_section == db.classes.id) &
                                (db.classes.end_date >= datetime.datetime.now())).select()
        registered_current = list(set([r.class_membership.name for r in registered_current]))
        unregistered = all.find(lambda row: row.id not in registered_current)
        if request.vars.agid == 'unregistered-active':
            title = 'Active (last 90 days) users not currently enrolled in a course.'
            users = unregistered.find(lambda row: db((db.attempt_log.name == row.id) &
                                                          (db.attempt_log.dt_attempted >=
                                                           (datetime.datetime.now() - datetime.timedelta(days=90))
                                                           )
                                                     ))
        elif request.vars.agid == 'unregistered-inactive':
            title = 'All users not currently enrolled in a course.'
            users = all
        classlist = make_unregistered_list(users)

    response.js = "jQuery('#chooser_submit').val('View Class')"

    return {'userlist': classlist,
            'target': target,
            'freq': freq,
            'classid': classrow['id'],
            'title': title}


def add_user_form():
    '''
    Return a checklist form for adding members to the current course section.
    '''
    print 'starting add user form()'
    users = db(db.auth_user.id > 0).select()
    form = FORM(TABLE(_id='user_add_form'),
                _action=URL('add_user', vars={'classid': request.vars.classid}),
                _method='POST')
    for u in users:
        form[0].append(TR(TD(INPUT(_type='checkbox', _name='user_to_add',
                                _value=u['id'])),
                       TD(SPAN(u['last_name'], u['first_name']))))
    # submit button added to footer in view when modal assembled
    return form


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
    # TODO: re-implement this flag to force users to view new slide decks
    #if auth.is_logged_in():
    #    if session.walk and 'view_slides' in session.walk:
    #        del session.walk['view_slides']
    return dict()
