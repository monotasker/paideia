# coding: utf8
import datetime
from gluon import current
from pprint import pprint
import traceback
from itertools import chain

if 0:
    from web2py.gluon import current, URL

def do_user_promotion(uid=0, classid=0):
    '''
    Move the specified user ahead one badge set.
    '''
    debug = True
    db = current.db
    if debug: print('starting paideia_user_management/do_user_promotion ==========================')
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

    # make sure no tags previously missed being activated
    # if so, add to level2
    all_active_tags = list(chain(level2, tp['cat3'], tp['cat4']))
    if debug: print('all active tags:', all_active_tags)
    # filtering out id 0 used by information flags
    should_be_active = db((db.tags.tag_position < (oldrank + 1)) &
                          (db.tags.tag_position != 0)).select()
    missing = [t.id for t in should_be_active if t.id not in all_active_tags]
    if debug: print('earlier missed activating tags:', missing)
    if missing:
        level2.extend(missing)
        for tag in missing:  # create level 1 record in badges_begun
            db((db.badges_begun.tag == tag) &
               (db.badges_begun.name == uid)).update(cat1=datetime.datetime.now())
        if debug: print('new level 2 with previously missed tags:', level2)

    # update badges_begun records with level 2 record
    for tag in old_level1 + missing:
        db((db.badges_begun.tag == tag) &
           (db.badges_begun.name == uid)).update(cat2=datetime.datetime.now())

    # add badges begun records for new level1 tags
    to_newly_activate = [t.id for t in
                         db(db.tags.tag_position == (oldrank + 1)).select()]
    if debug: print('activating new level 1 tags:', to_newly_activate)
    newly_activated = []
    for tag in to_newly_activate:
        newly_activated.append(db.badges_begun.insert(tag=tag, name=uid))
    if debug: print('added new badges_begun rows:', newly_activated)

    # update tag_progress record
    tp_result = tp.update_record(latest_new=(oldrank + 1),
                                 cat1=to_newly_activate,
                                 cat2=level2)

    db.commit()

    changed_tags = list(chain(to_newly_activate, old_level1, missing))
    bb_result = db((db.badges_begun.tag.belongs(changed_tags)) &
                   (db.badges_begun.name == uid)).select()
    if debug: print("changed badges_begun records:")
    if debug: pprint(bb_result)

    return({'tag_progress': tp_result,
            'badges_begun': bb_result})


def do_user_demotion(uid=0, classid=0):
    '''
    Move the specified user back one badge set.

    Removes all tag_records rows for the user which cover tags in the demoted
    tag set.
    '''
    debug = True
    db = current.db
    if debug: print('starting paideia_user_management/do_user_demotion ==========================')
    if debug: print('uid:', uid)
    if debug: print('classid:', classid)
    tp = db(db.tag_progress.name == uid).select().first()
    oldrank = tp['latest_new']
    old_ranktags = db(db.tags.tag_position == oldrank).select()
    old_taglist = [t['id'] for t in old_ranktags]
    if debug: print("old highest set tags:", old_taglist)
    new_ranktags = db(db.tags.tag_position == (oldrank - 1)).select()
    new_taglist = [t['id'] for t in new_ranktags]
    if debug: print("new highest set tags:", new_taglist)

    old_level2 = tp['cat2']
    if debug: print("old level2 tags:", old_level2)
    old_level3 = tp['cat3']
    if debug: print("old level3 tags:", old_level3)
    old_level4 = tp['cat4']
    if debug: print("old level4 tags:", old_level4)
    new_level1 = new_taglist
    if debug: print("new level1 tags:", new_taglist)
    new_level2 = [t for t in old_level2 if t not in new_taglist]
    if debug: print("new level2 tags:", new_level2)
    new_level3 = [t for t in old_level3 if t not in new_taglist]
    if debug: print("new level3 tags:", new_level3)
    new_level4 = [t for t in old_level4 if t not in new_taglist]
    if debug: print("new level4 tags:", new_level4)
    tp_result = tp.update_record(latest_new=(oldrank - 1),
                                 cat1=new_level1,
                                 cat2=new_level2,
                                 cat3=new_level3,
                                 cat4=new_level4)

    # TODO: do I have to somehow mark the actual log entries somehow as
    # removed? Should they be backed up?
    if debug: print('removing tag records for:', old_taglist + new_taglist)
    trecs = db((db.tag_records.tag.belongs(old_taglist)) &
               (db.tag_records.name == uid))
    if debug: print('found tag records to delete:', trecs.count())
    trec_result = trecs.delete()
    if debug: print('deleted:', trec_result, 'tag records')

    bb_demoted_count = 0
    for tag in new_ranktags:
        bb_demoted_count += db((db.badges_begun.tag == tag) &
                               (db.badges_begun.name == uid)
                               ).update(cat1=datetime.datetime.now(),
                                        cat2=None)
    if debug: print('rolled back badges_begun date for',
                    bb_demoted_count, 'records')
    bb_removed_count = 0
    for tag in old_ranktags:
        bb_removed_count += db((db.badges_begun.tag == tag) &
                               (db.badges_begun.name == uid)
                               ).delete()
    if debug: print('removed badges_begun records for', bb_removed_count, 'tags')

    db.commit()

    bb_result_demoted = db((db.badges_begun.tag.belongs(new_taglist)) &
                           (db.badges_begun.name == uid)).select()

    return({'tag_progress': tp_result,
            'tag_records_removed': trec_result,
            'badges_begun_demoted': bb_result_demoted,
            'badges_begun_removed': bb_removed_count})


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
