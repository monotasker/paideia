# coding: utf8
import datetime
import traceback
from gluon import current
from pprint import pprint

if 0:
    from web2py.gluon import current, URL

def do_user_promotion(uid=0, classid=0):
    '''
    Move the specified user ahead one badge set.
    '''
    debug = False
    db = current.db
    if debug: print('starting paideia_user_management/promote_user ==========================')
    if debug: print('uid:', uid)
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
    tp_result = tp.update_record(latest_new=(oldrank + 1),
                                 cat1=[],
                                 cat2=level2)
    # update badges_begun records with level 2 record
    for tag in old_level1:
        db((db.badges_begun.tag == tag) &
           (db.badges_begun.name == uid)).update(cat2=datetime.datetime.now())
    db.commit()

    bb_result = db((db.badges_begun.tag.belongs(old_level1)) &
                   (db.badges_begun.name == uid)).select()

    return({'tag_progress': tp_result,
            'badges_begun': bb_result})


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


def add_user():
    '''
    Adds one or more users to the specified course section.
    '''
    users = request.vars.value
    print('add_user: value is', users)


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
