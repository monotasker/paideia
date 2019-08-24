# coding: utf8
'''
Controller supplying data for views that list things in admin interfaces.

TODO: rationalize this controller organization
'''
# JOB ... this line is not liked by python ... oct 21, 2014
# from test.pickletester import myclasses
from copy import copy
import datetime
import traceback
from paideia_stats import make_classlist, make_unregistered_list
from pprint import pprint
# from dateutil.parser import parse
# from operator import itemgetter
if 0:
    from gluon import INPUT, A, URL, SPAN, SELECT, OPTION, FORM
    from gluon import TABLE, TR, TD, CAT
    from gluon import current, redirect
    db, auth, session = current.db, current.auth, current.session
    request, response = current.request, current.response


@auth.requires(auth.has_membership('instructors') |
               auth.has_membership('administrators'))
def get_my_classes(classid=None):
    """
    Return user's classes as a list of dicts

    The list will be sorted by date according to the year and term, then
    alphanumberically by section label. If a classid argument is supplied, that
    item will be moved to the top of the list and will also be provided as a
    separate return value

    """
    classid = None if classid == 'none' else classid
    if auth.has_membership('administrators'):
        myclasses = db(db.classes.instructor != None).select()
    else:
        myclasses = db(db.classes.instructor == auth.user_id
                       ).select(db.classes.id,
                                db.classes.academic_year,
                                db.classes.term,
                                db.classes.course_section,
                                db.classes.institution)

    active_class = None
    if len(myclasses):
        myclasses = myclasses.as_list()
        terms = ('fall', 'september', 'october', 'november', 'december'
                 'winter intersession', 'january',
                 'winter', 'february', 'march',
                 'spring/summer', 'april', 'may', 'june', 'july', 'august')
        term_order = lambda t: terms.index(t)
        myclasses = sorted(myclasses,
                           key=lambda x: (x['academic_year'],
                               term_order(x['term']),
                               x['course_section']),
                           reverse=True)
        try:
            active_class = [m for m in myclasses if m.get('id') ==
                            int(request.vars.classid)][0]
            if debug: print('found active class', request.vars.classid)
            myclasses = [m for m in myclasses if m.get('id') !=
                            int(request.vars.classid)]
            myclasses.insert(0, active_class)
        except (IndexError, TypeError):
            pass

    return myclasses


@auth.requires(auth.has_membership('instructors') |
               auth.has_membership('administrators'))
def queries():
    debug = False

    # Include files for Datatables jquery plugin and bootstrap css styling
    response.files.append(imports['datatables_css'])
    response.files.append(imports['pdfmake'])
    response.files.append(imports['pdfmake_vfsfonts'])
    response.files.append(imports['datatables'])

    classid = request.vars.classid if 'classid' in list(request.vars.keys()) \
        else None
    myclasses = get_my_classes(classid=classid)

    if myclasses:
        admin = True if auth.has_membership('administrators') else False
        return {'myclasses': myclasses,
                'classid': myclasses[0]['id'],
                'admin': admin}
    else:
        return {'classid': None}


@auth.requires(auth.has_membership('instructors') |
               auth.has_membership('administrators'))
def user():
    debug = False
    myclasses = get_my_classes()

    if myclasses:
        admin = True if auth.has_membership('administrators') else False
        return {'myclasses': myclasses,
                'classid': myclasses[0]['id'],
                'admin': admin}
    else:
        return {'classid': None}


@auth.requires_membership(role='administrators')
def promote_user():
    '''
    Move the specified user ahead one badge set.
    '''
    debug = False
    if debug: print('starting listing/promote_user ==========================')
    uid = request.vars.uid
    classid = request.vars.classid
    if debug: print('classid:', classid)
    tp = db(db.tag_progress.name == uid).select().first()
    oldrank = tp['latest_new']
    # move remaining cat1 tags forward to cat2
    old_level1 = tp['cat1']
    if debug: print('old_level1', old_level1)
    level2 = tp['cat2']
    if debug: print('level2', level2)
    level2.extend(old_level1)
    if debug: print('level2', level2)

    # make sure no tags were missed being activated
    all_active_tags = level2 + tp['cat3'] + tp['cat4']
    should_be_active = db(db.tags.tag_position <= (oldrank + 1)).select()
    missing = [t.id for t in should_be_active if t.id not in all_active_tags]
    if debug: print('missed activating tags:', missing)
    if missing:
        level2.extend(missing)
        old_level1.extend(missing)  # so badges_begun are updated
        for tag in missing:  # create level 1 record in badges_begun
            db((db.badges_begun.tag == tag) &
               (db.badges_begun.name == uid)).update(cat1=datetime.datetime.now())
        if debug: print('new level 2 with missed tags:', level2)

    # update tag_progress record
    tp.update_record(latest_new=(oldrank + 1),
                     cat1=[],
                     cat2=level2)
    # update badges_begun records with level 2 record
    for tag in old_level1:
        db((db.badges_begun.tag == tag) &
           (db.badges_begun.name == uid)).update(cat2=datetime.datetime.now())

    redirect(URL('user.html', vars={'classid': classid}))


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
    print('demoting tags:', old_taglist)
    trecs = db((db.tag_records.tag.belongs(old_taglist)) &
               (db.tag_records.name == uid))
    print('found trecs:', trecs.count())
    trecs.delete()

    for tag in new_ranktags:
        db((db.badges_begun.tag == tag) &
           (db.badges_begun.name == uid)).update(cat1=datetime.datetime.now(),
                                                cat2=None)

    response.flash = 'User moved back to set {}'.format(oldrank - 1)
    redirect(URL('user.html', vars={'classid': classid}))


@auth.requires_membership(role='administrators')
def add_user():
    '''
    Adds one or more users to the specified course section.
    '''
    users = request.vars.value
    print('add_user: value is', users)


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
    redirect(URL('userlist.load', vars={'agid': classid}))


@auth.requires(auth.has_membership('instructors') |
               auth.has_membership('administrators'))
def querylist():
    debug = True
    try:
        if request.vars.agid == 'all':
            members = [m for m in
                       db().iterselect(db.auth_user.id)]
        elif request.vars.agid in ['unregistered-active',
                                   'unregistered-inactive']:
            pass
        else:
            classid = int(request.vars.agid)
            members = list(set([m.name for m in
                               db(db.class_membership.class_section ==
                                  classid).iterselect()]
                               ))
        filtervals = {'unanswered': [5],
                      'answered': (7, 6, 4, 3, 2),
                      'confirmed': [1],
                      'fixed': [2],
                      'all': None}
        my_filter = filtervals[request.vars.filter]
        if my_filter:
            queries = db((db.bugs.user_name.belongs(members)) &
                         (db.bugs.bug_status.belongs(my_filter))
                         ).select().as_list()
        else:
            queries = db(db.bugs.user_name.belongs(members)).select().as_list()
        status_rows = db(db.bug_status.id > 0).select()
        for q in queries:
            # provide readable student name
            q['user_id'] = copy(q['user_name'])
            mystudent = db.auth_user(q['user_name'])
            q['user_name'] = '{}, {}'.format(mystudent['last_name'],
                                             mystudent['first_name']
                                             )
            # order vals with the record's current status at the top
            vals = [num for num in range(1, len(status_rows) + 1)
                    if num != q['bug_status']]
            if isinstance(q['bug_status'], int):
                vals.insert(0, q['bug_status'])
            print(vals)
            statuses = ((r['id'], r['status_label']) for v in vals
                        for r in status_rows
                        if r['id'] == v)
            q['bug_status'] = statuses

    except Exception as e:
        print(e)
        queries = None

    return {'queries': queries}


@auth.requires(auth.has_membership('instructors') |
               auth.has_membership('administrators'))
def userlist():
    debug = False
    if debug:
        print('starting listing/userlist =============================')
        print('agid', request.vars.agid, type(request.vars.agid))
    # if isinstance(request.vars.agid, (int, long)):  # selecting class
    try:
        int(request.vars.agid)
        try:
            classrow = db.classes[int(request.vars.agid)].as_dict()
        except Exception:  # choose a class to display as default
            print(traceback.format_exc(5))
            classrow = db(db.classes.instructor == auth.user_id
                          ).select().last().as_dict()
        target = classrow['paths_per_day']
        freq = classrow['days_per_week']
        title = '{} {} {}, {}'.format(classrow['academic_year'],
                                      classrow['term'],
                                      classrow['course_section'],
                                      classrow['institution'])
        member_sel = db(db.class_membership.class_section ==
                        classrow['id']).select()
        if debug:
            print('in member_sel:')
            for m in member_sel:
                print(db.auth_user(m['name']).last_name, ', ', \
                    db.auth_user(m['name']).first_name)
            print('---------')

        users = db((db.auth_user.id == db.tag_progress.name) &
                   (db.auth_user.id.belongs([m['name'] for m in member_sel]))
                   ).select(orderby=db.auth_user.last_name)

        if debug:
            print('in users:')
            for u in users:
                print(u.auth_user.last_name)
                print('---------')

        start_date = classrow['start_date']
        end_date = classrow['end_date']
        classlist = make_classlist(member_sel, users, start_date,
                                   end_date, target, classrow)
        if end_date > datetime.datetime.now():
            in_process = True
        else:
            in_process = False

    except Exception:  # selecting outside of current class registrants
        target = 0
        freq = 0
        classrow = {'id': None}
        all = db(db.auth_user).select()
        registered_current = db((db.class_membership.class_section ==
                                 db.classes.id) &
                                (db.classes.end_date >=
                                 datetime.datetime.now())).select()
        registered_current = list(set([r.class_membership.name for r
                                       in registered_current]))
        unregistered = all.find(lambda row: row.id not in registered_current)
        if request.vars.agid == 'unregistered-active':
            title = 'Active (last 90 days) users not currently enrolled in ' \
                    'a course.'
            users = unregistered.find(
                lambda row: db((db.attempt_log.name == row.id) &
                               (db.attempt_log.dt_attempted >=
                                (datetime.datetime.now() -
                                 datetime.timedelta(days=90))
                                )
                               ))
        elif request.vars.agid == 'unregistered-inactive':
            title = 'All users not currently enrolled in a course.'
            users = all
        classlist = make_unregistered_list(users)
        in_process = True

    return {'userlist': classlist,
            'target': target,
            'freq': freq,
            'classid': classrow['id'],
            'title': title,
            'in_process': in_process}


def add_user_form():
    '''
    Return a checklist form for adding members to the current course section.
    '''
    print('starting add user form()')
    users = db(db.auth_user.id > 0).select()
    form = FORM(TABLE(_id='user_add_form'),
                _action=URL('add_user',
                            vars={'classid': request.vars.classid}),
                _method='POST')
    for u in users:
        form[0].append(TR(TD(INPUT(_type='checkbox', _name='user_to_add',
                                   _value=u['id'])),
                       TD(SPAN(u['last_name'], u['first_name']))))
    # submit button added to footer in view when modal assembled
    return form


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


def lessons():
    """
    Assemble a list of links to the slide sets and send to the view.
    """
    # TODO: re-implement this flag to force users to view new slide decks
    #if auth.is_logged_in():
    #    if session.walk and 'view_slides' in session.walk:
    #        del session.walk['view_slides']
    active_lesson = int(request.args[0]) if request.args else None
    active_video = None
    if active_lesson:
        active_video = db.lessons(active_lesson).video_url[17:]
        active_set = str(db.lessons(active_lesson).lesson_position)[:-1]
    elif auth.is_logged_in():
        active_set = db(db.tag_progress.name == auth.user_id
                        ).select().first().latest_new
        active_set = str(active_set)
    else:
        active_set = None
    lessons = db(db.lessons.active == True
                 ).select(orderby=db.lessons.lesson_position
                          ).as_list() 
    for l in lessons:
        mybadges = db(db.badges.tag.belongs(l['lesson_tags'])).select()
        l['badges'] = mybadges.as_list()
    return {'lessons': lessons,
            'active_video': active_video,
            'active_set': active_set}
