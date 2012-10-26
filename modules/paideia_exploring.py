# coding: utf8
from gluon import current, redirect, Field
from gluon import IMG, SQLFORM, SPAN, DIV, URL, A, UL, LI, MARKMIN
from gluon import IS_NOT_EMPTY, IS_IN_SET
#from gluon.sql import Row, Rows

import datetime
from dateutil.parser import parse
import ast
from itertools import chain
from copy import deepcopy
from random import randrange
import re
import traceback
from pytz import timezone
import logging
logger = logging.getLogger('web2py.app.paideia')
logger.setLevel(logging.DEBUG)


# TODO: Deprecate eventually
class Utils(object):
    '''
    Miscellaneous utility functions, gathered in a class for convenience.
    '''
    verbose = True

    def __init__(self):
        pass

    def _session_to_db(self, data):
        '''
        Serialize session.walk data and store it in db.session_data
        '''
        if self.verbose:
            print 'calling Utils._session_to_db============================'
        debug = False
        auth = current.auth
        db = current.db

        # prepare the session data for serialization
        wdb = deepcopy(data)
        if debug: print 'copy:', wdb
        # make sure 'retry' is list
        if 'retry' in wdb and type(wdb['retry']) != list:
            wdb['retry'] = list(wdb['retry'])
        # convert datetime to iso string
        if type(wdb['session_start']) == str:
            pass
        else:
            wdb['session_start'] = wdb['session_start'].isoformat(' ')
        # convert bg_image IMG helper to html string
        al = data['active_location']
        if al and al['bg_image'] is not None:
            if type(al['bg_image']) is str:
                wdb['active_location']['bg_image'] = al['bg_image']
            else:
                wdb['active_location']['bg_image'] = al['bg_image'].xml()
        # convert complete_paths from set to list
        wdb['completed_paths'] = list(data['completed_paths'])
        # convert npc_image IMG helper to html string
        if 'npc_image' in data and data['npc_image'] is not None:
            if type(data['npc_image']) is str:
                wdb['npc_image'] = data['npc_image']
            else:
                wdb['npc_image'] = data['npc_image'].xml()

        if debug: print 'serialized as:', wdb
        # make sure date for session_start field is datetime, not string
        tdb = data['session_start']
        if type(tdb) == str:
            tdb = parse(tdb)
        db.session_data.update_or_insert(db.session_data.user == auth.user_id,
                                 updated=datetime.datetime.utcnow(),
                                 session_start=tdb,
                                 data=wdb)
        if debug: print 'saved in db'

    def _db_to_session(self, data):
        '''
        Retrieve stored session data and deserialize for use.
        '''
        if self.verbose:
            print 'calling Utils._db_to_session============================'
        debug = False
        auth = current.auth
        db = current.db

        try:
            sdata = ast.literal_eval(data)
            if debug: print "deserialized data as:", sdata
        # if the db value still has unserialized objects, delete and recheck
        except (ValueError('malformed string'), SyntaxError) as e:
            print type(e), e
            db(db.session_data.user == auth.user_id).delete()
            print 'deleted bad data'
            return None

        # deserialize datetime:
        try:
            sdata['session_start'] = parse(sdata['session_start'])
        except Exception as e:
            print 'couldn\'t deserialize datetime for session_start'
            print type(e), e
            pass
        # convert bg_image html back to IMG helper
        try:
            istring = sdata['active_location']['bg_image']
            isrc = re.search(r'src=[\"]?([^\" >]+)', istring).group(1)
            isrc = isrc.split('="')[1]
            if isrc[-1] == '"':
                isrc = isrc[:-1]
            sdata['active_location']['bg_image'] = IMG(_src=URL(isrc))
        except Exception, e:
            print 'couldn\'t deserialize bg_image'
            print type(e), e

        # convert completed paths from list back to set
        sdata['completed_paths'] = set(sdata['completed_paths'])

        # convert npc_image html back to IMG helper
        try:
            istring = sdata['npc_image']
            isrc = re.search(r'src=[\"]?([^\" >]+)', istring).group(1)
            isrc = isrc.split('="')[1]
            if isrc[-1] == '"':
                isrc = isrc[:-1]
            sdata['npc_image'] = IMG(_src=URL(isrc))
        except Exception, e:
            print 'couldn\'t deserialize npc_image'
            print type(e), e

        return sdata

    # TODO: Move logic to controller and remove class
    def clear_session(self):
        session, response = current.session, current.response

        if response.vars and ('session_var' in response.vars):
            session_vars = response.vars['session_var']
        else:
            session_vars = 'all'

        if session_vars == 'all':
            session_vars = ['walk']
        if type(session_vars) is not list:
            session_vars = list(session_vars)

        for s in session_vars:
            if s in session:
                del session[s]


class Walk(object):
    '''
    A class handling the "movement" of a user from one path or step to the
    next (i.e., transitions between states outside a single step). In other
    words, this class prepares path-related information needed immediately
    before path selection.
    '''

    verbose = True  # controls printing of initialization and method calls

    def __init__(self, force_new_session=False):
        '''
        Initialize a Walk object. When it is initialized, maintain session
        data through each 24-hour day by:
        - Checking whether the web2py session object has a walk attribute
        - If so, check that its 'initialized' date is the same as today
        - If either of these checks fails, look for a 'session_stored' row
        in the db for this user with today's date
            - If so, create session.walk with that data and continue
              initializing Walk object
        - If that returns None, initialize the Walk object with default data
        '''
        if self.verbose:
            print 'initializing Walk============================'
        debug = False

        if force_new_session is True:
            if debug:
                print 'forcing new session'
            self._start_new_session()
        # TODO: This check is too costly to do every time, rework
        # maybe pass whole serialized Walk object via session?
        # then just check start date of Walk object?
        if self._check_for_session() is True:
            if debug: print 'session data present and not stale'
            self._get_session_data()
        else:
            if debug:
                print 'session stale or not present, starting new session'
            self._start_new_session()

        # TODO: This doesn't need to be instantiated every time
        self.map = Map()

    def _start_new_session(self):
        '''
        Initialize this Walk object's instance variables with defaults and
        save the results to session object.
        '''
        if self.verbose:
            print 'calling Walk._start_new_session() -------------------------'
        auth = current.auth

        # create placeholder instance attributes
        self.active_location = None
        self.path = None
        self.active_paths = {}
        self.completed_paths = set()
        self.view_slides = None
        self.step = None
        # initialize the session properly
        self.tag_set = self._categorize_tags()
        self.new_badges = self._new_badges(self.tag_set, auth.user_id)
        # self._unfinished()
        # TODO: deprecated _unfinished in present state, but need replacement
        self.session_start = datetime.datetime.utcnow()
        # store newly initialized attributes in session object
        self._save_session_data(True)

    def _check_for_session(self):
        '''
        Return True if 'walk' is in session and it was created today, or if
        there is a db.session_data row that was created today. In the latter
        case populate session.walk with the data from the db record. Otherwise
        return False.
        '''
        if self.verbose:
            print 'calling Walk._check_for_session() ------------------------'
        debug = False
        auth = current.auth
        session = current.session
        db = current.db

        # TODO: What about case where db data is newer than session data?
        mysession = db(db.session_data.user == auth.user_id).select().first()
        if debug: print 'stored data in db', mysession

        tz_name = db.auth_user[auth.user_id].time_zone
        tz = timezone(tz_name)
        now_local = tz.fromutc(datetime.datetime.utcnow())
        if debug: print 'current local time:', now_local

        if session.walk and ('session_start' in session.walk):
            start = session.walk['session_start']
            if debug: print 'session.walk:', session.walk
            if type(start) != datetime.datetime:
                start = parse(start)
            session_start_local = tz.fromutc(start)
            if debug: print 'session started at:', session_start_local
            if (session_start_local.day == now_local.day):
                if debug: print 'session started today'
                return True
            else:
                if debug: print 'session is stale'
                pass

        elif mysession:
            session_start_local = tz.fromutc(mysession.session_start)
            if debug: print 'db session started at:', session_start_local
            if session_start_local.day == now_local.day:
                retrieved = Utils()._db_to_session(mysession.data)
                if debug: print 'session started today'
                if retrieved:
                    session.walk = retrieved
                    return True
                else:
                    if debug: print 'malformed db data'
                    return False
            else:
                if debug: print 'db session is stale'
                pass

        return False

    def _save_session_data(self, new=False):
        '''
        Save instance attributes in web2py session object for data persistence.
        '''
        #debug = False
        if self.verbose:
            print 'calling Walk._save_session_data--------------'
        session = current.session

        session_data = {
            'active_paths': self.active_paths,
            'completed_paths': self.completed_paths,
            'tag_set': self.tag_set,
            'view_slides': self.view_slides,
            'new_badges': self.new_badges,
            'path': None,
            'step': None,
            'active_location': None,
            'quota_override': False,
            'session_start': self.session_start or datetime.datetime.utcnow()
            }

        if self.path:
            session_data['path'] = self.path.id
        if self.step:
            session_data['step'] = self.step.step.id
        if self.active_location:
            session_data['active_location'] = self.active_location
        try:
            session.walk.update(session_data)
        except AttributeError:
            session.walk = session_data

        if new is True:
            session.walk['session_start'] = datetime.datetime.utcnow()

        Utils()._session_to_db(session.walk)

    def _get_session_data(self):
        '''
        Get the walk attributes from the session.
        '''
        debug = False
        if self.verbose:
            print 'calling Walk._get_session_data--------------'
        db = current.db
        session = current.session
        request = current.request

        logger.debug('here is session.walk:{}'.format(session.walk))

        # set session.walk attributes as instance attributes (with fallbacks)
        defaults = {'active_paths': {},
                    'completed_paths': set(),
                    'tag_set': {1: [], 2: [], 3: [], 4: []},
                    'new_badges': None,
                    'view_slides': None,
                    'session_start': datetime.datetime.utcnow()}
        for k, v in defaults.iteritems():
            val = session.walk[k] if k in session.walk else v
            setattr(self, k, val)

        # only start with a path value if one is already in session
        path_id = session.walk['path']
        self.path = db.paths(path_id) if path_id else None

        # only create a location object if the request included a loc
        if 'loc' in request.vars and request.vars['loc'] is not None:
            location_alias = request.vars['loc']
            self.active_location = Location(location_alias).info()
            session.walk['active_location'] = self.active_location
            if debug:
                print 'self.active_location =', self.active_location
        else:
            self.active_location = None
            session.walk['active_location'] = None
            if debug:
                print 'no loc variable in request, setting loc to None'

        # create step instance here if we're processing a user's response
        if ('response' in request.vars) and \
                (request.args[0] in ['ask', 'retry']):
            print 're-activating step'
            self.step = self._create_step_instance()

    def _create_step_instance(self, step_id=None):
        '''
        Create an instance of a Step class or one of its subclasses based on
        the step's widget type.
        '''
        debug = False
        if self.verbose:
            print 'calling Walk._create_step_instance------------'
        db = current.db
        session = current.session

        if not step_id:
            step_id = session.walk['step']

        if debug:
            print 'step id =', step_id
        step = db.steps(step_id)
        step_type = db.step_types(step.widget_type)
        if debug:
            print 'step type =', step_type

        return STEP_CLASSES[step_type.step_class](step_id)

    def _introduce(self):
        '''
        Introduce into the user's active tags (self.tag_list and
        db.tag_progress) the tags for the next position in the tag progression.
        Also record this user's new position in that progression in
        db.tag_progress.latest_new. Set self.view_slides to a list of the newly
        introduced tags (by id), and return that same list.
        '''
        if self.verbose:
            print 'calling Walk._introduce--------------'
        debug = False
        auth = current.auth
        db = current.db

        uid = auth.user_id
        progress_sel = db(db.tag_progress.name == uid).select()
        # Make sure only one record per user
        # TODO: enforce at db level and remove
        if len(progress_sel) > 1:
            for r in progress_sel[1:]:
                if debug: print 'deleting extra record for this user:', r
                del db.tag_progress[r.id]

        progress = progress_sel.first()
        if progress is None:
            #If this user is just starting, so doesn't have table row
            latest = 1
            # TODO: Check we aren't at the end of the tag progression
        else:
            latest = progress.latest_new + 1
        if debug: print 'latest_new now =', latest

        tags = [t.id for t in db(db.tags.position == latest).select()]
        if debug: print 'introducing new tag(s):', tags
        # set the flag for the user to view any slides associated with these
        # tags
        self.view_slides = tags

        db.tag_progress.update_or_insert(db.tag_progress.name == uid,
                                          name=uid, latest_new=latest,
                                          cat1=tags)

        return tags

    def _find_cats(self, categories, record_list):
        '''
        Categorize the user's active subject tags based on a combination of
        timed repetition and overall success with the tag to date.

        Returns a dictionary with four keys (cat1, cat2, cat3, cat4)
        corresponding to the four review categories, with cat1 meaning the
        tag needs immediate review and the other categories indicating
        progressively smaller likelihood of a path with the tag being chosen.
        '''
        for record in record_list:
            #get time-based statistics for this tag
            #note: arithmetic operations yield datetime.timedelta objects
            now_date = datetime.datetime.utcnow()
            right_dur = now_date - record.tlast_right
            right_wrong_dur = record.tlast_right - record.tlast_wrong

            # Categorize q or tag based on this performance
            # spaced repetition algorithm for promotion from cat1
            # ======================================================
            # for category 2
            if ((right_dur < right_wrong_dur)
                    # don't allow promotion from cat1 within 1 day
                    and (right_wrong_dur > datetime.timedelta(days=1))
                    # require at least 10 right answers
                    and (record.times_right >= 10)) \
                or ((record.times_right > 0)  # prevent zero division error
                    and ((record.times_wrong / record.times_right) <= 0.125)
                    and (right_dur <= datetime.timedelta(days=2))) \
                or ((record.times_wrong == 0)  # prevent zero division error
                    and (record.times_right >= 20)):
                    # allow for 1 wrong answer for every 8 correct
                    # promote in any case if the user has never had a wrong
                    # answer in 20+ attempts
                # ==================================================
                # for category 3
                if right_wrong_dur.days >= 7:
                    # ==============================================
                    # for category 4
                    if right_wrong_dur.days > 30:
                        # ==========================================
                        # for review
                        if right_wrong_dur > datetime.timedelta(days=180):
                            category = 'cat1'  # Not tried for 6 months
                        else:
                            category = 'cat4'  # Not due, delta > a month
                    else:
                        category = 'cat3'  # delta between a week and month
                else:
                    category = 'cat2'  # Not due but delta is a week or less
            else:
                category = 'cat1'  # Spaced repetition requires review

            categories[category].append(record.tag.id)

        return categories

    def _categorize_tags(self, user=None, auth=None, db=None, progress=None):
        '''
        This method uses stored statistics for current user to categorize the
        grammatical tags based on the user's success and the time since the
        user last used the tag.

        The categories range from 1 (need immediate review) to 4 (no review
        needed).

        This method is called at the start of each user session so that
        time-based statistics can be updated. It is also called by
        Stats.categories() to provide a progress report for the student's
        profile page.

        Returns a dictionary with four keys corresponding to the four
        categories. The value for each key is a list holding the id's
        (integers) of the tags that are currently in the given category.
        '''
        debug = False
        if self.verbose: print 'calling Walk._categorize_tags--------------'
        # inject default dependencies
        if auth is None:
            auth = current.auth
        if db is None:
            db = current.db
        if user is None:
            user = auth.user_id
            if debug: print 'user:', user
        if progress is None:
            progress = db(db.tag_progress.name == user).select().first()
            if progress is None:
                db.tag_progress.insert(latest_new=1)

        # TODO: Factor in how many times a tag has been successful or not
        # TODO: Look at secondary tags

        # create new dictionary to hold categorized results
        catlabels = ['cat1', 'cat2', 'cat3', 'cat4']
        categories = dict((x, []) for x in catlabels)

        # get record of user performance for each tag tried
        record_list = db(db.tag_records.name == user).select()
        if debug: print 'initial record_list', [r.id for r in record_list]
        # find and remove any duplicate entries in tag_records
        discrete_tags = set([t.tag for t in record_list])
        kept = []
        if len(record_list) > len(discrete_tags):
            for tag in discrete_tags:
                shortlist = record_list.find(lambda row: row.tag == tag)
                if debug: print 'shortlist', [s.id for s in shortlist]
                kept.append(shortlist[0].id)
                if len(shortlist) > 1:
                    for row in shortlist[1:]:
                        row.delete_record()
            record_list = record_list.find(lambda row: row.id in kept)
        if debug: print 'filtered record_list', [r.id for r in record_list]

        # if user has not tried any tags yet, start first set
        if record_list.first() is None:
            if debug: print 'No tag_records for this user'
            firsttags = [t.id for t in db(db.tags.position == 1).select()]
            categories['cat1'] = firsttags
            reviews['cat1'] = firsttags
            self.view_slides = firsttags
            if debug: print 'setting categories to initial value', categories
        # otherwise, categorize tags that have been tried
        else:
            # run basic categorizing algorithm
            categories = self._find_cats(categories, record_list)
        if debug: print 'raw categorized tags:', categories

        # Make sure untried tags are still included
        rank = progress.latest_new

        #check for untried in current and all lower ranks
        left_out = []
        for r in range(1, rank + 1):
            newtags = [t.id for t in db(db.tags.position == r).select()]
            alltags = list(chain(*categories.values()))
            left_out.extend([t for t in newtags if t not in alltags])
        if left_out:
            categories['cat1'].extend(left_out)
            if debug: print 'adding untried tags', left_out, 'to cat1'

        # Remove duplicate tag id's from each category
        # Make sure each of the tags is not beyond the user's current ranking
        # even if some were actually tried before (through system error)
        for k, v in categories.iteritems():
            if v:
                newv = [t for t in v if db.tags[t].position <= rank]
                categories[k] = list(set(newv))

        # If there are no tags needing immediate review, introduce new one
        if not categories['cat1']:
            categories['cat1'] = self._introduce()
        # TODO: Could this categorization be done by a background process?

        self.tag_set = categories
        if debug: print 'final categorized tags:', categories
        if debug: print 'active_paths:', self.active_paths

        # return the value as well so that it can be used in Stats
        return categories

    def _new_badges(self, categories, user=None, db=None):
        '''
        Find any tags that have been newly promoted to a higher category,
        update the user's row in db.tag_progress, and return a dictionary of
        those new tags whose structure mirrors that of session.walk['tag_set'].
        '''
        if self.verbose: print 'calling Walk._new_badges ---------------------'
        debug = True
        if db is None:
            db = current.db
        if user is None:
            auth = current.auth
            user = auth.user_id

        # If a tag has moved up in category, award the badge
        mycats = db(db.tag_progress.name == user).select().first()
        if debug: print 'mycats =', mycats

        new_badges = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        for category, lst in categories.iteritems():
            if lst:
                print 'current badges =', lst
                # make sure to check against higher categories too
                catindex = categories.keys().index(category)
                mycats_gteq = dict((k, mycats[k]) for k
                           in ['cat1', 'cat2', 'cat3', 'cat4'][catindex:])
                oldtags = list(chain([val for cat in mycats_gteq.values() for val in cat]))
                print 'oldtags', oldtags
                if debug:
                    print 'looking in equal and higher cats:', mycats_gteq
                new = [t for t in lst if t not in oldtags]
                if new:
                    if debug: print 'newly awarded badges =', new
                    new_badges[category] = new

        # build dictionary of values to record in tag_progress
        # start with old values
        update_cats = dict((c, v) for c, v in mycats.as_dict().iteritems()
                            if c in categories.keys())
        if debug: print 'old categories were', update_cats
        # if tags new or promoted, change 'cat' lists
        for cat in new_badges:
            if new_badges[cat] is not None:
                for t in new_badges[cat]:
                    try:
                        oldcat = [c for c, v in update_cats.iteritems()
                                    if (type(v) == list) and (t in v)][0]
                        update_cats[oldcat].remove(t)
                    except IndexError:
                        print 'This tag appears to be new; not removing from \
                                old position'
                    update_cats[cat].append(t)
        # new max-category values
        if debug: print 'new cat values:', update_cats
        # record this session's working categorization as 'review' categories
        update_cats['rev1'] = categories['cat1']
        update_cats['rev2'] = categories['cat2']
        update_cats['rev3'] = categories['cat3']
        update_cats['rev4'] = categories['cat4']

        # do this here so that we can compare db to categories first
        # TODO: this is a bad place to update the db values
        db(db.tag_progress.name == user).update(**update_cats)

        result = []
        if [result.append(lst) for k, lst in new_badges.iteritems() if lst]:
            if debug: print 'new badges =', new_badges
            return new_badges
        else:
            if debug: print 'no new badges awarded'
            return None

    # TODO: method deprecated
    def _unfinished(self):
        '''
        This public method checks for any paths that have been started but not
        finished by the current user. It expects finished paths to have a
        'last_step' value of 0 in its most recent entry in the db table
        path_log.

        called by: controllers/exploring.index()
        '''
        if self.verbose:
            print 'calling Walk._unfinished--------------'
        auth, db = current.auth, current.db

        path_logs = db(
            (db.path_log.name == auth.user_id) &
            (db.path_log.last_step != 0)
        ).select()

        # Get only most recent log for each unique path
        self.active_paths = {}
        for path in set(log.path for log in path_logs):
            log = max((p.dt_started, p)
                      for p in path_logs if p.path == path)[1]
            self.active_paths[path.id] = log.last_step

    def _handle_blocks(self):
        '''
        Look for active blocking conditions:
            * a new badge has been awarded
            * a new badge is being started (and slides need to be viewed)
            * no response given for an activated step
            * daily full paths limit reached
        Also checks to make sure that any path/step combination it returns
        is a valid combination.

        Returns:
            * (None, None) if there are no blocking conditions
            * Otherwise, return (path, step id) for active blocking conditions
        '''

        if self.verbose:
            print 'calling Walk._handle_blocks--------------'
        debug = False

        auth, db, session = current.auth, current.db, current.session

        if self.new_badges is not None:
            return self._get_util_step('award badge')  # tag id=81

        # TODO: insert these session.walk values in _introduce and _categorize)
        if self.view_slides is not None:
            return self._get_util_step('view slides')  # tag id=80

        # TODO: need to fix check for step that was never finished
        #upath, ustep = self._unfinished_today()
        #if upath:
            #return upath, ustep

        # Have we reached the daily path limit? Return a default step.
        # TODO: Replace hardcoded limit (20)
        if len(self.completed_paths) == 20:
            if 'quota_override' in session.walk and \
                                                session.walk['quota_override']:
                pass
            else:
                return self._get_util_step('end of quota')  # tag id=79

        if (len(self.completed_paths) % 20) == 0:
            if debug: print 'completed n*20 paths, re-categorizing...'
            self.tag_set = self._categorize_tags()

        return None, None

    def _unfinished_today(self):
        '''
        If there are any newly activated paths that haven't had a response yet,
        activate the first one whose next step is in this loc.
        '''
        if self.verbose:
            print 'calling Walk.unfinished_today--------------'
        db, auth = current.db, current.auth

        # Get this user's unfinished paths
        path_logs = db(
            (db.path_log.name == auth.user_id) &
            (db.path_log.last_step != 0)
        ).select()

        # TODO: use UTC or adjust here for user's local tz?
        today = datetime.datetime.utcnow().date()

        # Activate the first unfinished step that hasn't had a response
        for log in path_logs:
            # Filter out if it wasn't started today
            #TODO: Is there a faster way to do this?
            # yes: look for any in path_logs that aren't in active_paths
            attempts = db(
                (db.attempt_log.name == auth.user_id) &
                (db.attempt_log.path == log.path) &
                (db.attempt_log.step == log.last_step) &
                (db.attempt_log.dt_attempted >= log.dt_started)
            ).select(orderby=~db.attempt_log.dt_attempted)
            attempts = [a for a in attempts if a.dt_attempted.date() == today]
            ls = log.last_step
            in_path = self._step_in_path(log.path, ls)
            here = self.active_location['id'] in db.steps[ls].locations

            # If it's in this loc, activate; otherwise, show default step
            if attempts and in_path and here:
                return log.path, log.last_step
            elif attempts and in_path:
                return self._get_util_step('default')  # tag id=70

        return None, None

    def activate_step(self, path, step_id):
        '''
        Activate the given step on the given path.
        '''
        debug = False
        if self.verbose:
            print 'calling Walk.activate_step--------------'
        session = current.session
        db = current.db
        if debug:
            print 'step_id is', step_id
            print 'path is', path

        step_id = int(step_id)
        # allow for situations where the path id is given rather than the
        # path's row object. (As in 'retry' state.)
        if (type(path) == int) or (type(path) == str):
            path = db.paths[path]

        # handle odd error where activate_step called at Walk.__init__
        # even though no path or step is in session for reactivation
        # TODO: why this error?
        if step_id is None:
            # select a new path and/or step
            path, step = self._get_next_step()

        self.path = path
        # avoid adding utility redirect path 30 to active paths
        if step_id != 30:
            self.active_paths[path.id] = step_id
        if debug:
            print 'activating step', step_id
        self.step = self._create_step_instance(step_id)
        self._save_session_data()
        if debug:
            print 'session.walk["active_paths"] is now'
            print session.walk["active_paths"]
            print 'session.walk["path"] is now', session.walk["path"]
            print 'session.walk["step"] is now', session.walk["step"]
        self._update_path_log(path.id, step_id, 0)

    def _deactivate_path(self, path):
        '''
        Deactivate the given path. It will then be considered "completed" for
        the current day and will not be repeated.
        '''
        debug = False
        if self.verbose:
            print 'calling Walk._deactivate_path--------------'
        db = current.db

        if debug:
            print 'in Walk._deactivate_path, path =', path

        self._update_path_log(path, 0, 1)
        del self.active_paths[path]
        # TODO: find more elegant way to avoid adding utility steps
        if [v for v in db.paths[path].tags if v in [70, 79, 80, 81]]:
            pass
        else:
            self.completed_paths.add(path)
        self._save_session_data()

    def _get_util_step(self, tag, next_loc=None):
        '''
        Return the default path and step for a particular utility situation.
        These include
        - having reached the daily quota of completed paths
        - having an incomplete path whose next step is in another location
        - having a newly introduced tag whose slides must be viewed
        - having a newly awarded badge
        '''
        debug = False
        if self.verbose:
            print 'calling Walk._get_util_step--------------'
        session, db = current.session, current.db
        if next_loc:
            session.walk['next_loc'] = next_loc

        tag_id = db(db.tags.tag == tag).select()[0].id
        steps = db(db.steps.tags.contains(tag_id)).select()
        if debug:
            print 'steps with tag', tag, 'id=', tag_id
            print steps

        # Choose a step at random
        if len(steps) > 1:
            step = steps[randrange(0, len(steps))]
        else:
            step = steps[0]

        path = db(db.paths.steps.contains(step.id)).select().first()
        if debug: print 'returning path id=', path.id
        if debug: print 'returning step id=', step.id

        return path, step.id

    def next_step(self):
        '''
        Choose a new path and step for the user, based on tag performance.
        Checks first for any blocking conditions and constrains the
        choice of next step accordingly.
        '''
        debug = False
        if self.verbose:
            print 'calling Walk.next_step--------------'

        # Handle active blocking conditions
        # TODO: condition is being deprecated
        #if not self.staying:

        path, step_id = self._handle_blocks()
        # _handle_blocks() returns None, None if no blocks present
        # if daily max reached, returns default step
        if path and step_id:
            if debug:
                print 'blocking conditions found'
                print 'by activating path', path, ', step', step_id
            self.activate_step(path, step_id)
            return

        else:
            # select the next path and/or step
            new_path, new_step = self._get_next_step()

            self.activate_step(new_path, new_step)

            return

    def _step_in_path(self, path, step=None):
        '''
        Check the given step id to make sure it is in the given path. If so,
        return the index of the given step in the path. If no step is given
        use the last completed step (as recorded in self.active_paths).
        If the step is not in the given path, return False.
        '''
        debug = False
        if self.verbose:
            print 'calling Walk._step_in_path--------------'

        if not step:
            try:
                step = self.active_paths[path.id]
            except Exception, e:
                print 'Error encountered in Walk._step_in_path()'
                print e
        if debug:
            print 'checking that step', step, 'is in path', path.id
        try:
            step_index = path.steps.index(step)
            if debug:
                print 'step', step, 'is index', step_index, 'in path', path.id
            return step_index
        # If impossible step id is given in active_paths
        except ValueError, err:
            if debug:
                print 'ValueError:', err
                print 'step', step, '*not* in path', path.id
            # Remove this path from active paths
            if path.id in self.active_paths:
                del self.active_paths[path.id]
                self._save_session_data()
            if debug:
                print 'self.active_paths now=', self.active_paths

            # Set the log for this attempt as if path completed
            self._update_path_log(path.id, 0, 1)
            # TODO: Log error instead/as well
            return False

    def stay(self):
        '''
        Continue the current path in this location if possible. (Deprecated)
        '''
        # TODO: This method is now deprecated
        debug = False

        session, db = current.session, current.db
        if debug:
            print 'calling Walk.stay() =============='
            print 'self.step.step.id =', self.step.step.id
            print 'self.path.id =', self.path.id

        index = self.path.steps.index(self.step.step.id)
        if index + 1 < len(self.path.steps):
            try:
                step = db.steps(self.path.steps[index + 1])
                if self.active_location['id'] in step.locations:
                    self.activate_step(self.path, step.id)
                    self._save_session_data()
                    return True
            except Exception, e:
                print 'Exception raised trying to continue active path in'
                print 'Walk.stay()'
                print e

        if debug:
            print 'No path to continue here'

        return False

    def _get_next_step(self):
        '''
        Determines what path and step to activate next and returns them as
        a dictionary with the keys 'path' and 'step'.

        The method looks (in order of preference) for:
        1)  an active path whose next step is in this location;
        2) an active path whose next step is in another location (in which
        case the default step is activated;
        3) a new path which can be started in this location and whose tags are
        due for review by the current user;
        4) a new path started in another location whose tags are
        due (in which case the default step is activated);
        5) any random path which can be started here;
        6) any random path which can be started elsewhere (in which case the
        default step is activated)
        '''
        debug = True
        if self.verbose:
            print 'calling Walk._get_next_step--------------'
        db = current.db
        auth = current.auth

        loc_id = self.active_location['id']

        # 1) try to continue an active path whose next step is in this loc
        if len(self.active_paths.keys()) > 0:
            if debug:
                print 'looking for active paths in this location'
                print 'active_paths =', self.active_paths
            # remove all but one active path (since more is wrong data)
            start_len = len(self.active_paths.keys())
            lastk = self.active_paths.keys()[-1]
            if debug: print 'last active path:', lastk
            if start_len > 1:
                self.active_paths = {lastk: self.active_paths[lastk]}
                if debug: print 'removing', (start_len - 1), 'active paths'
            apath = db.paths[lastk]
            if debug: print 'active path:', apath

            # make sure step belongs to the path
            step_id = self.active_paths[apath.id]
            step_index = self._step_in_path(apath, step_id)
            if debug: print 'index of the unfinished step is', step_index
            if type(step_index) is bool:
                if debug:
                    print 'step', step_id, 'not in path', apath.id
                # Remove it from active paths
                del self.active_paths[apath]
                # Move on to selecting a new path (#3 below)
            else:
                # 1) try to activate the step if it can be done here.
                step = db.steps[step_id]
                if debug: print step.id
                if debug: print 'loc_id =', loc_id, 'locs =', step.locations
                # 2) If not in this location, send user elsewhere
                if not loc_id in step.locations:
                    if debug: print 'step is elsewhere, getting redirect step'
                    return self._get_util_step('default')

                # 1) Otherwise re-activate this step
                self._update_path_log(apath.id, step_id, 1)
                if debug: print 'activating step', step_id, 'of path', apath.id
                return apath, step_id

        # 3)-4) look for a new path due, first in this location and otherwise
        # in another location
        if debug: print 'no active paths, looking for a new path'
        cat = self._get_category()  # generate weighted random number for cat
        cat_range = range(1, 5)
        cat_list = cat_range[cat:5] + cat_range[0:cat]
        if debug: print 'category list to try:', cat_list

        # cycle through categories, starting with the one from _get_category()
        p_list1 = db().select(db.paths.ALL, orderby='<random>')
        p_list1 = p_list1.find(lambda row:
                [stp for stp in row.steps if db.steps[stp].status != 2])
        if debug: print 'filtered path list', [p.id for p in p_list1]
        for cat in cat_list:
            if debug: print 'Trying category', cat  # DEBUG

            # find paths with tags in the current category
            # include max category and review 'columns'
            tag_list = self.tag_set['cat' + str(cat)]
            p_list = p_list1.find(lambda row:
                                  [t for t in row.tags if t in tag_list])
            if debug: print 'paths tagged in this cat:', [p.id for p in p_list]

            # exclude paths already completed in this session
            if self.completed_paths is not None:
                if debug: print 'already completed:', self.completed_paths
                p_list.exclude(lambda row: row.id in self.completed_paths)
                if debug: print 'path list without those:', p_list
                # prevent getting hung up because of steps with right tag but
                # with no location
                p_list.exclude(lambda row: db.steps[row.steps[0]].locations
                                                                    is None)

            if len(p_list) > 0:
                if debug: print 'some new paths are available in cat', cat
                # 3) Find and activate a due path that starts here
                for path in p_list:
                    try:
                        step1_id = path.steps[0]
                        if debug: print 'step1_id', step1_id
                        first_step = db.steps[step1_id]
                        if debug:
                            print 'first_step', first_step
                            print 'first_step.locations', first_step.locations
                        if loc_id in first_step.locations:
                            print 'path', path.id, 'step', step1_id, 'due'
                            return path, step1_id
                        else:
                            continue
                    except Exception, e:
                        print type(e), e
                        continue

                # 4) If due paths are elsewhere, trigger default step
                next_locs = db.steps[p_list[0].steps[0]].locations
                next_loc = next_locs[randrange(0, len(next_locs))]
                if debug: print 'sending to loc', next_loc

                return self._get_util_step('default', next_loc)

        #TODO: Fall back here to repeating random paths from completed_paths
        # first that can be started here
        # then that can't (trigger default step)

        # 5) Choose a random path that can be started here
        if debug: print 'looking for random path with active tags'  # DEBUG
        max_rank = db(db.tag_progress.name
                      == auth.user_id).select().first().latest_new
        tag_list = db(db.tags.position <= max_rank).select()
        # filter out paths whose tags aren't in the tag_list
        paths = p_list1.find(lambda row:
                     [t for t in row.tags if t in [l.id for l in tag_list]])
        for p in paths:
            the_step = db.steps[p.steps[0]]
            if the_step.locations and (loc_id in the_step.locations):
                return p, the_step
            else:
                continue

        # 6) Send user to look elsewhere for a path with active tags
        next_locs = db.steps[paths[0].steps[0]].locations
        next_loc = next_locs[randrange(0, len((next_locs) + 1))]
        if debug: print 'sending to loc', next_loc

        return self._get_util_step('default', next_loc)

    def _get_category(self):
        '''
        Choose one of four categories with a random factor but a heavy
        weighting toward category 1
        '''

        if self.verbose: print 'calling Walk._get_category--------------'
        switch = (1, 101)

        if switch in range(1, 75):
            category = 1
        elif switch in range(75, 90):
            category = 2
        elif switch in range(90, 98):
            category = 3
        else:
            category = 4
        return category

    def _get_paths(self):
        '''
        Return all paths in the game.
        '''
        if self.verbose: print 'calling Walk._get_paths--------------'
        db = current.db
        cache = current.cache

        # TODO: Review cache time
        return db().select(db.paths.ALL,
                        orderby=db.paths.id,
                        cache=(cache.ram, 60 * 60))

    def _update_path_log(self, path_id, step_id, update_switch):
        '''
        Create or update entries in the path_log table.
        '''
        if self.verbose: print 'calling Walk._update_path_log--------------'
        auth, db = current.auth, current.db

        if update_switch:
            try:
                query = (db.path_log.path == path_id) & (db.path_log.name ==
                                                                auth.user_id)
                log = db(query).select(orderby=
                                            ~db.path_log.dt_started).first()
                log.update_record(path=path_id, last_step=step_id)
            except AttributeError:
                # handling active path/step that was never given path_log row
                db.path_log.insert(path=path_id, last_step=step_id)

            return True
        else:
            db.path_log.insert(path=path_id, last_step=step_id)

            return True

        return False


class Step(object):

    verbose = True

    def __init__(self, step=None):

        debug = False
        db, session = current.db, current.session
        if self.verbose:
            print 'Initializing', type(self).__name__, '=================='

        if step is not None:
            self.path = db.paths(session.walk['path'])
            self.step = db.steps(step)
            self.location = session.walk['active_location']
            self.npc = None
            self._save_session_data()
        else:
            self._get_session_data()

        if debug: print 'session.walk["active_location"] ='
        if debug: print session.walk["active_location"]

    def _save_session_data(self):
        '''
        Save attributes in session.
        '''
        debug = False
        if self.verbose:
            print 'calling', type(self).__name__, '._save_session_data----'
        session = current.session

        session_data = {}
        session_data['step'] = self.step.id
        session.walk.update(session_data)

        if self.npc:
            self.npc._save_session_data()

        if debug: print 'session_data =', session_data

        return

    def _get_session_data(self):
        '''
        Get the step attributes from the session.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_session_data-----'
        db, session = current.db, current.session

        self.location = session.walk['active_location']
        self.path = db.paths(session.walk['path'])
        try:
            self.step = db.steps(session.walk['step'])
            self.npc = Npc(session.walk['npc'])
        except KeyError:
            self.step = None
            self.npc = None

    def ask(self):
        '''
        Public method. Returns the html helpers to create the view
        for the 'ask' state of the user interface.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '.ask-------------------'
        debug = False

        npc = self._get_npc(self.step, self.location)
        prompt = self._get_prompt()
        responder = self._get_responder()
        badgetip = self._get_badge_display(self.step.id)
        if badgetip:
            prompt.append(badgetip)
        self._save_session_data()
        if debug: print 'bg_image =', self.location['bg_image']

        return dict(npc_img=npc.image, prompt=prompt,
                    responder=responder,
                    bg_image=self.location['bg_image'])

    def _get_badge_display(self, step_id):
        '''
        Return an html helper object to display the badges for the specified
        question's primary and secondary tags.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_badge_display-------'
        #debug = False
        db = current.db

        badgetip = DIV(A(SPAN('badges', _class='accessible'),
                        _href='#',
                        _class='prompt_badges_icon icon-only icon-ul'),
                    _class='prompt_badges_wrapper tip_wrapper')

        the_step = db.steps[step_id]
        bsel = db(db.badges.tag == db.tags.id).select()
        bsel1 = bsel.find(lambda row: row.tags.id in the_step.tags)
        bsel2 = bsel.find(lambda row: row.tags.id in the_step.tags_secondary)
        if (bsel1 is None) and (bsel2 is None):
            return None

        badgeset1 = [LI(b.badges.badge_name) for b in bsel1]
        badgelist1 = UL(*badgeset1)

        badgeset2 = [LI(b.badges.badge_name) for b in bsel2]
        badgelist2 = UL(*badgeset2)

        btext = DIV('This step focuses on these badges:', badgelist1,
                    _class='prompt_badges')

        if len(badgeset2) > 0:
            btext.append('It also assumes you\'ve already been working on')
            btext.append(' these other badges:')
            btext.append(badgelist2)
        badgetip.append(btext)

        return badgetip

    def _get_npc(self, step, location):
        '''
        Given a set of npcs for this step select one of the npcs at random and
        return the corresponding Npc object.
        '''
        # TODO: Make sure that subsequent steps of the current path use the
        # same npc if in the same location
        if self.verbose:
            print 'calling', type(self).__name__, '._get_npc--------------'
        debug = True

        def _get_npc_internal(npcs):
            '''
            Return an npc from the set of npcs or None if there aren't any.
            '''
            if self.verbose:
                print 'calling', type(self).__name__, '._get_npc_internal-'
            if npcs is None:
                return

            npc_count = len(npcs)

            if npc_count > 1:
                return npcs[randrange(1, npc_count) - 1]
            elif npc_count == 1:
                return npcs[0]
            else:
                return None

        db, session = current.db, current.session

        if session.walk['active_location'] is None:
            return   # TODO: maybe we return a 404 here (or in ask(), etc.)?

        if debug: print 'self.location =', location

        # belongs selector needs 'list of tuples'
        if debug:
            print 'step.npcs', step.npcs
        if len(step.npcs) == 1:
            npcs = db.npcs(step.npcs[0])
            npc = npcs
        else:
            npcs = db(db.npcs.id.belongs(tuple([n for n in step.npcs]))).select()
            npcs = npcs.find(lambda row: location['id'] in row.location)
            if len(npcs) > 1:
                npc = _get_npc_internal(npcs)
            else:
                npc = npcs.first()
        if debug: print 'npc set:', npcs

        # If we haven't found an npc at the location and step, get a random one
        # from this location.
        if not npc:
            npcs = db(db.npcs.location.contains(location['id'])).select()
            npc = _get_npc_internal(npcs)
        # If we haven't found an npc at the location, get a random one from
        # this step.
        if not npc:
            npcs = db((db.npcs.id.belongs(step.npcs))).select()
            npc = _get_npc_internal(npcs)
        # If we still haven't found an npc, just get a random one
        if not npc:
            npcs = db(db.npcs.id > 0).select()
            npc = _get_npc_internal(npcs)

        self.npc = Npc(npc.id)

        return self.npc

    def process(self, user_response):
        '''
        Handles the user's response to the step prompt.

        In this base 'step' class this involves comparing the user's typed
        response with the regular expressions provided for the step. The
        evaluation is then logged and stored in the db, and the appropriate
        information presented to the user.
        '''
        debug = False
        if self.verbose:
            print 'calling', type(self).__name__, '.process----------'
        session = current.session

        # Get the student's response to the question
        user_response = user_response.strip()
        if debug:
            print 'user_response'
        # Get the correct answer information from db
        answer1 = self.step.response1
        answer2 = self.step.response2
        answer3 = self.step.response3
        readable = self.step.readable_response
        if '|' in readable:
            i = len(readable)
            if i > 1: i = 2
            print readable
            readable_short = readable.split('|')[:(i + 1)]
            readable_short = [unicode(r, 'utf-8') for r in readable_short]
            print readable_short
            readable_long = readable.split('|')
            readable_long = [unicode(r, 'utf-8') for r in readable_long]
        else:
            readable_short = [readable]
            readable_long = None

        # Compare the student's response to the regular expressions
        try:
            if re.match(answer1, user_response, re.I):
                score = 1
                reply = "Right. Κάλον."
            elif answer2 != 'null' and re.match(answer2, user_response, re.I):
                score = 0.5
                #TODO: Get this score value from the db instead of hard
                #coding it here.
                reply = "Οὐ κάκον. You're close."
                #TODO: Vary the replies
            elif answer3 != 'null' and re.match(answer3, user_response, re.I):
                #TODO: Get this score value from the db instead of hard
                #coding it here.
                score = 0.3
                reply = "Οὐ κάκον. You're close."
            else:
                score = 0
                reply = "Incorrect. Try again!"

            # Set the increment value for times wrong, depending on score
            if score < 1:
                times_wrong = 1
            else:
                times_wrong = 0

        # Handle errors if the student's response cannot be evaluated
        except re.error:
            redirect(URL('index', args=['error', 'regex']))
            reply = 'Oops! I seem to have encountered an error in this step.'
            readable_short = None
            readable_long = None

        # TODO: This replaces the Walk.save_session_data() that was in the
        # controller. Make sure this saving of step data is enough.
        self._save_session_data()
        log_id = self._complete(score, times_wrong)

        return {'reply': reply,
                'readable': readable_short,
                'readable_long': readable_long,
                'bug_reporter': self._get_bug_reporter(self.step,
                                                       self.path,
                                                       user_response,
                                                       log_id,
                                                       score),
                'npc_img': session.walk['npc_image'],
                'bg_image': self.location['bg_image']}

    def _get_bug_reporter(self, step, path, answer, log_id, score):
        '''
        Construct and return a SPAN helper containing the contents of the
        tooltip containing the message and link allowing students to submit
        a bug report for the current step.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_bug_reporter-----'
        request, response = current.request, current.response

        bug_reporter = DIV(_class='bug_reporter tip')
        text1 = SPAN('If you think your answer wasn\'t evaluated properly, ')
        link = A('click here',
                    _href=URL('creating', 'bug',
                                vars=dict(step=step.id,
                                            path=path.id,
                                            answer=request.vars.response,
                                            log_id=log_id,
                                            score=score,
                                            loc=request.vars.loc)),
                    cid='bug_reporter',
                    _class='button-bug-reporter')
        text2 = SPAN(' to submit a bug report for this question.')
        bug_reporter.append(text1)
        bug_reporter.append(link)
        bug_reporter.append(text2)

        return bug_reporter

    def _record(self, score, times_wrong_incr):
        '''
        Record the results of this step in db tables attempt_log and
        tag_records. score gives the increment to add to 'times right' in
        records. times_wrong gives the opposite value to add to 'times wrong'
        (i.e., negative score).
        '''
        debug = False

        if self.verbose:
            print 'calling', type(self).__name__, '._record---------------'
        db, auth, session = current.db, current.auth, current.session

        utc_now = datetime.datetime.utcnow()
        tag_records = db(db.tag_records.name == auth.user_id).select()
        if debug: print 'tag_records:', tag_records

        # Calculate record info
        time_last_right = utc_now
        time_last_wrong = utc_now
        tagset = set(self.step.tags)
        if debug: print 'recording for tags:', tagset

        # Log this tag attempt for each tag in the step
        for tag in tagset:
            # Try to update an existing record for this tag
            try:
                tag_records = tag_records.find(lambda row: row.tag == tag)
                if debug: print 'tag_records with tag:', tag_records

                if tag_records:
                    tag_record = tag_records[0]

                    times_right = tag_record.times_right
                    times_wrong = tag_record.times_wrong

                    if score == 1:
                        time_last_wrong = tag_record.tlast_wrong
                        times_right += 1
                    elif score == 0:
                        time_last_right = tag_record.tlast_right
                        times_wrong += 1
                    else:
                        score = 0
                        time_last_right = tag_record.tlast_right
                        times_wrong += 1

                    tag_record.update_record(
                        tlast_right=time_last_right,
                        tlast_wrong=time_last_wrong,
                        times_right=times_right,
                        times_wrong=times_wrong,
                        path=self.path.id,
                        step=self.step.id
                    )
                    if debug: print 'updated existing record'

                else:
                    times_right = 1
                    times_wrong = 0
                    if score != 1:
                        times_right = 0
                        times_wrong = 1

                    db.tag_records.insert(
                        tag=tag,
                        tlast_right=time_last_right,
                        tlast_wrong=time_last_wrong,
                        times_right=times_right,
                        times_wrong=times_wrong,
                        path=self.path.id,
                        step=self.step.id
                    )
                    if debug: print 'created new record'

        # TODO: Work on more concise version below

        # # Log this tag attempt for each tag in the step
        # for tag in self.step.tags:
        #     # Try to update an existing record for this tag
        #     try:
        #         tag_record = tag_records.find(lambda row:
        #                                             row.tag == tag).first()

        #         if tag_record:
        #             if score == 1:
        #                 time_last_wrong = tag_record.tlast_wrong
        #             elif score == 0:
        #                 time_last_right = tag_record.tlast_right
        #             else:
        #                 score = 0
        #                 time_last_right = tag_record.tlast_right

        #             times_right += tag_record.times_right
        #             times_wrong += tag_record.times_wrong

        #         db.tag_records.update_or_insert(
        #                 {'name': auth.user_id,
        #                 'tag': tag},
        #                 tlast_right=time_last_right,
        #                 tlast_wrong=time_last_wrong,
        #                 times_right=times_right,
        #                 times_wrong=times_wrong,
        #                 path=self.path.id,
        #                 step=self.step.id
        #             )

            # Print any other error that is thrown
            # TODO: Put this in a server log instead/as well or create a ticket
            # TODO: Do we want to rollback the transaction?
            except Exception, err:
                print 'unidentified error:'
                print type(err)
                print err
                print traceback.format_exc()

        # TODO: Merge this with Walk._update_path_log()?
        # TODO: Note that last_step has to be set to 0 either here or in
        # complete() *after* this.
        log = db(
                (db.path_log.path == self.path.id) &
                (db.path_log.name == auth.user_id)
                ).select(orderby=~db.path_log.dt_started).first()

        # Log this path completion/progress
        if log:
            log.update_record(path=self.path.id, last_step=self.step.id)
        else:   # We should have an existing path_log but in case not...
            db.path_log.insert(path=self.path.id, last_step=self.step.id)

        # Log this step attempt
        db.attempt_log.insert(step=self.step.id,
                              score=score,
                              path=self.path.id)
        a_log = db((db.attempt_log.name == auth.user_id) &
                    (db.attempt_log.step == self.step.id)
                    ).select(orderby=~db.attempt_log.dt_attempted)

        return a_log.first().id

    def _complete(self, score, times_wrong):
        '''
        Record the current session data in the db for cross-session
        persistence.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._complete -----------'
        debug = False
        session = current.session
        request = current.request

        # TODO: Where appropriate, make sure last_step is recorded as 0
        # Record evaluation of step response
        log_id = None
        if request.args[0] != 'retry':
            log_id = self._record(score, times_wrong)

        # Check to see whether this is the last step in the path and if so
        # remove from active_paths and add to completed_paths
        # also set path to None in session.walk
        if debug:
            print 'self.path.steps:', self.path.steps
            print 'self.path.steps[-1]:', self.path.steps[-1]
        # if this was the last step in the path, end the path
        stepcount = len(self.path.steps)
        if self.path.steps[-1] == self.step.id:
            if self.path.id in session.walk['active_paths']:
                del session.walk['active_paths'][self.path.id]
            session.walk['completed_paths'].add(self.path.id)
            session.walk['path'] = None
            session.walk['step'] = None
        # if there's another step in this path, make it active
        elif stepcount > 1:
            s_index = self.path.steps.index(self.step.id)
            next_s = self.path.steps[s_index + 1]
            session.walk['step'] = next_s
            session.walk['active_paths'][self.path.id] = next_s

        session.walk['retry'] = [self.path.id, self.step.id]

        # Store session data in db
        # This needs to happen last
        Utils()._session_to_db(session.walk)

        # TODO: In path selection, re-activate any path or step that is still
        # in session.walk when controller in the 'ask' state
        # TODO: Remove from session._get_next_path the logic to deactivate
        # final steps, etc.?

        return log_id

    def _get_prompt(self):
        '''
        Get the prompt text to be presented from the npc to start the step
        interaction.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_prompt-----------'
        debug = True
        auth = current.auth

        uname = auth.user['first_name']
        rawtext = self.step.prompt
        newtext = rawtext.replace('[[user]]', uname)
        try:
            reps = self._get_replacements()
            if debug: print reps
            for k, v in reps.iteritems():
                newtext = newtext.replace(k, v)
        except AttributeError:
            if debug: print 'No replacements for this Step type'

        prompt = DIV(MARKMIN(newtext))

        try:
            if debug: print 'getting prompt image'
            prompt.append(self._get_step_image())
        except AttributeError:
            if debug: print 'No step image for this Step type'
            pass

        try:
            audio = self._get_step_audio()
            if audio:
                prompt.append(audio)
        except AttributeError:
            pass

        return prompt

    def _get_step_audio(self):
        '''
        Return the url (as a string) of the audio file for the current step's
        prompt.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_step_audio--------'
        debug = False

        try:
            url = URL('static/audio', self.step.prompt_audio)
            if debug: print url
            if url:
                return url.xml()
        except:
            print '._get_step_audio(): Could not find step audio'
            return

    def _get_responder(self):
        '''
        Create and return the form to receive the user's response for this
        step.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_responder--------'

        # TODO: this return not needed now? Or should .complete() be called?
        if isinstance(self, StepStub):
            return

        form = SQLFORM.factory(
                    Field('response', 'string', requires=IS_NOT_EMPTY()),
                    _autocomplete='off'
                )
        wrapper = DIV(form, _class='responder')

        instructions = self._get_instructions()
        if instructions:
            wrapper.append(instructions)

        return wrapper

    def _get_instructions(self):
        '''
        Return a web2py DIV() element holding a link that displays a tooltip
        with the instructions to accompany the current step's responder form.
        '''
        db = current.db

        inst_div = DIV(
                        A('tips', _class='instructions \
                                            icon-only icon-lightbulb'),
                        DIV(UL(), _class='instructions tip'),
                    _class='prompt_tips')

        iset = db.steps[self.step.id].instructions
        if iset:
            for i in iset:
                inst_div[-1][0].append(LI(i))

            return inst_div
        else:
            return None


class StepMultipleChoice(Step):

    def _get_responder(self):
        '''
        create and return the form to receive the user's response for this
        step
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_responder-----'
        session, request = current.session, current.request

        vals = self.step.options
        form = SQLFORM.factory(
                    Field('response', 'string',
                    requires=IS_IN_SET(v for v in vals),
                    widget=SQLFORM.widgets.radio.widget))
        if form.process().accepted:
            session.response = request.vars.response

        instructions = self._get_instructions()
        wrapper = DIV(form, instructions, _class='responder')

        return wrapper

    def process(self, user_response):
        '''
        Evaluate the user's answer to a StepMultipleChoice prompt, record
        her/his performance, and return the appropriate reply elements.

        This method overrides Step.process for the StepMultipleChoice subclass.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_responder----'
        debug = False
        session, db, auth = current.session, current.db, current.auth

        # Get the student's response to the question
        user_response = user_response.strip()
        if debug:
            print user_response

        # Get the correct answer information from db
        answer1 = self.step.response1
        answer2 = self.step.response2
        answer3 = self.step.response3
        # readable = self.step.readable_response

        # Compare the student's response to the stored answers
        if user_response == answer1:
            score = 1
            reply = "Right. Κάλον."
        elif answer2 != 'null' and user_response == answer2:
            score = 0.5
            #TODO: Get this score value from the db instead of hard
            #coding it here.
            reply = "Οὐ κάκον. You're close."
            #TODO: Vary the replies
        elif answer3 != 'null' and user_response == answer2:
            #TODO: Get this score value from the db instead of hard
            #coding it here.
            score = 0.3
            reply = "Οὐ κάκον. You're close."
        else:
            score = 0
            reply = "Sorry, that wasn't right. Try again!"

        # Set the increment value for times wrong, depending on score
        if score < 1:
            times_wrong = 1
        else:
            times_wrong = 0

        # Record the results in statistics for this step and this tag
        log_id = self._complete(score, times_wrong)

        # TODO: This replaces the Walk.save_session_data() that was in the
        # controller. Make sure this saving of step data is enough.
        self._save_session_data()

        return {'reply': reply,
                'readable': answer1,
                'bug_reporter': self._get_bug_reporter(self.step,
                                                        self.path,
                                                        user_response,
                                                        log_id,
                                                        score),
                'npc_img': session.walk['npc_image'],
                'bg_image': self.location['bg_image']}


class StepStub(Step):
    '''
    A step type that does not require significant user response. Useful for
    giving the user information and then freeing her/him up to perform a task.
    It does not, however, allow the user to continue at the current location,
    but sends her/him back to the map.
    '''

    verbose = True

    def _complete(self):
        '''
        Complete this step:
            * Do not update the path_log
            * Do not update the attempt_log
            * Remove path from active paths
            * Add path to completed paths

        Note that the user always gets the step right.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._complete -------------'
        debug = False
        session = current.session
        db = current.db

        if self.path is None:
            self.path = db.paths(session.walk['path'])
        if debug: print 'self.path', self.path

        # if this is part of a multi-step path
        # test with path 93 step 107
        if self.path and (len(self.path.steps) > 1) and (self.step.id !=
                                                          self.path.steps[-1]):
            # TODO: In some cases when step 30 (nothing here) is activated
            # between steps of a multi-step path, no other path is activated,
            # but the step 30 will not be found in the path.steps list
            # so this condition prevents a ValueError.
            if self.step.id == 30:
                if debug:
                    print 'this is intermediate "not here" step'
                    print 'preserving path and active_paths info'
            else:
                thisi = self.path.steps.index(self.step.id)
                next = self.path.steps[thisi + 1]
                session.walk['active_paths'][self.path.id] = next
                if debug: print 'next step in path', self.path.id, 'is', next

        # if it's a terminal stub
        else:
            if self.path and self.path.id in session.walk['active_paths']:
                if debug: print 'path:', self.path.id
                del session.walk['active_paths'][self.path.id]
            elif session.walk['path'] in session.walk['active_paths'].keys():
                if debug: print 'path:', session.walk['path']
                del session.walk['active_paths'][session.walk['path']]
            if debug:
                print 'session active_paths:', session.walk['active_paths']
        # either way, remove 'path' and 'step' from session.walk
        session.walk['path'] = None
        session.walk['step'] = None
        if debug: print 'session path:', session.walk['step']
        if debug: print 'session step:', session.walk['step']
        if debug: print 'session active_paths:', session.walk['active_paths']

        # Store session data in db
        Utils()._session_to_db(session.walk)

    def _get_responder(self):
        '''
        overrides Step._get_responder() to remove everything but the map
        button built into the view template.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_responder -------'
        map_button = A("Map", _href=URL('walk'),
                        cid='page',
                        _class='button-yellow-grad back_to_map icon-location')
        responder = DIV(map_button, _class='responder')

        self._complete()

        return responder

    def _get_badge_display(self, step_id):
        '''
        overrides Step._get_badge_display() to simply return None so that no
        confusing button is presented for step stubs that require no badges
        '''
        return None


class StepRedirect(StepStub):
    '''
    Step type to redirect user to a different location.
    '''

    def _get_replacements(self):
        '''
        Provide the string replacement data to be used in the step prompt.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_replacements ----'
        debug = True
        session = current.session
        db = current.db

        if 'active_paths' in session.walk \
                            and session.walk['active_paths'] \
                            and session.walk['active_paths'].keys()[0] != 30:
            if debug: print 'getting loc for active path'
            next_step = session.walk['active_paths'].values()[0]
            if debug: print next_step
            next_locids = db.steps[next_step].locations
            if debug: print next_locids
            # find a location that actually has a readable name
            for n in next_locids:
                if debug: print n
                if debug: print db.locations[n]
                next_loc = db.locations[n].readable
                if next_loc is None:
                    continue
                else:
                    break
        elif 'next_loc' in session.walk and session.walk['next_loc']:
            if debug: print 'getting loc from session.walk["next_loc"]'
            next_loc = db.locations[session.walk['next_loc']].readable
        else:
            next_loc = 'another location in town'

        if debug: print 'next_loc is', next_loc
        replacements = {'[[next_loc]]': next_loc}

        return replacements


class StepNonBlocking(StepStub, Step):
    '''
    This abstract class provides a responder that includes a "continue"
    button, allowing the user to move directly to another step in the current
    location. It overrides the following methods of Step:
    Step._get_responder()
    '''

    def _get_responder(self):
        '''
        Create and return the html helper for the buttons to allow the user
        to continue here.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_responder--------'
        request = current.request

        buttons = A("Continue", _href=URL('walk', args=['ask'],
                                        vars=dict(loc=request.vars['loc'])),
                    cid='page',
                    _class='button-green-grad next_q')

        wrapper = DIV(buttons, _class='responder')

        self._complete()

        return wrapper


class StepViewSlides(StepStub):
    '''
    Provides a step that stops a student and asks her/him to view the
    slides for newly activated tags/badges.
    '''
    verbose = True

    def _get_replacements(self):
        '''
        Provide the string replacement data to be used in the step prompt.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_replacements ----'
        debug = False
        session = current.session
        db = current.db

        slidelist = []
        badgelist = []
        if ('view_slides' in session.walk) and (session.walk['view_slides']
                                                              is not None):
            for t in session.walk['view_slides']:
                # convert this to link once plugin_slider supports it
                tag_slides = db.tags[t].slides
                slidelist += [db.plugin_slider_decks[d].deck_name
                                                        for d in tag_slides]

                badge = db(db.badges.tag == t).select().first()
                badge_name = '{0} {1}'.format('beginner', badge.badge_name)
                badgelist.append(badge_name)

            # Filter out duplicates
            slidelist = list(set(slidelist))
            badgelist = list(set(badgelist))

            badges = ''
            slides = ''
            for l in badgelist:
                badges += '- {0}\n'.format(l)
            for i in slidelist:
                slides += '- {0}\n'.format(i)

            if debug: print 'badges =', badges
            if debug: print 'slides =', slides

            replacements = {'[[badge_list]]': badges, '[[slides]]': slides}

            return replacements

        return None


class StepDailyQuota(StepNonBlocking, StepStub):
    '''
    This step class alerts the user that the daily quota of paths has been
    completed, but provides a continue button (from StepNonBlocking). As in
    StepStub, it still does not allow processing of any user response.
    '''
    #TODO: provide self._get_substitution override method to sub in the
    # user's required quota of paths per day.
    verbose = True

    def _complete(self):
        '''
        Add the session flag overriding the user's daily quota
        of steps, allowing the user to continue on to a new step.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._complete-----------'
        session = current.session
        session.walk['quota_override'] = True
        super(StepDailyQuota, self)._complete()


class StepAwardBadges(StepNonBlocking, StepStub):
    '''
    A step type that, like StepStub, doesn't take or process a user response.
    Unlike that parent class, though, StepMessage provides a "continue" button
    (inherited from StepNonBlocking) that allows the user to proceed with
    more paths at the current location. This is used for alerting user to
    newly awarded badges.
    '''
    verbose = True

    def _get_replacements(self):
        '''
        Provide the string replacement data to be used in the step prompt.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_replacements ---'
        debug = False
        session = current.session
        db = current.db
        auth = current.auth

        badges = ''
        if 'new_badges' in session.walk:
            for k, v in session.walk['new_badges'].iteritems():
                if debug: print 'new_badges =', session.walk['new_badges']
                #TODO: cludge to handle change in new_badges keys to simple int
                print k, k[:3], k[3:]
                if k[:3] == 'cat' and int(k[3:]) in [1, 2, 3, 4]:
                    n = int(k[3:])
                    print v
                    for tag in v:
                        print 'auth =', auth.user_id
                        b = db(db.badges.tag == tag).select()[0]
                        if debug: print 'badge =', b
                        ranks = ['beginner', 'apprentice',
                                                'journeyman', 'master']
                        try:
                            #TODO: chokes on this line if badge == None
                            badge_name = '{0} {1}'.format(ranks[n - 1],
                                                          b.badge_name)
                            rank_verbs = ['starting to learn',
                                        'making good progress with',
                                        'gaining a good working grasp of',
                                        'mastering']
                            badge_desc = 'for {0} {1}'.format(
                                                        rank_verbs[n - 1],
                                                        b.description)
                            if debug: print 'badge_desc =', badge_desc
                            badges += ('- **{0}** {1}\n'.format(
                                                badge_name, badge_desc))
                        except:
                            badges += '- unknown\n'
        if debug: print badges
        self._remove_flag('new_badges')

        return {'[[badge_list]]': badges}

    # TODO: This should really be a method of Walk
    def _remove_flag(self, flag_name):
        '''
        remove the session flag for newly awarded badges, allowing the user
        to continue on to a new step.
        '''
        session = current.session

        del session.walk[flag_name]
        print 'removed award badges flag'


class StepImage(Step):
    '''
    This subclass of Step adds an image in the prompt area.
    '''
    verbose = True

    def _get_step_image(self, db=None):
        '''
        Returns the image to be displayed in the step prompt, wrapped in a
        web2py IMG() helper object.
        '''
        debug = False
        if self.verbose:
            print 'calling', type(self).__name__, '._get_step_image -----'
        if db == None:
            db = current.db

        try:
            url = URL('static/images', db.images(self.step.widget_image).image)
            if debug:
                print url
            return IMG(_src=url, _class='prompt_image')
        except:
            print '._get_image(): Could not find image for prompt'
            return


class StepImageMultipleChoice(StepImage, StepMultipleChoice):
    '''
    This subclass of StepMultipleChoice adds an image in the prompt
    area (inherited from StepImage).
    '''
    verbose = True

    pass

STEP_CLASSES = {
        'step': Step,
        'step_multipleChoice': StepMultipleChoice,
        'step_stub': StepStub,
        'StepRedirect': StepRedirect,
        'step_image': StepImage,
        'step_imageMutlipleChoice': StepImageMultipleChoice,
        'step_awardBadges': StepAwardBadges,
        'step_dailyQuota': StepDailyQuota,
        'step_viewSlides': StepViewSlides
    }


class Npc(object):

    def __init__(self, npc_id=None):

        db, session = current.db, current.session

        if npc_id is not None:
            self.npc = db.npcs(npc_id)
            self.image = self._get_image(self.npc)

            self._save_session_data()

        else:
            self._get_session_data()
            info = self._get_session_data()
            self.npc = info.npc
            self.image = info.image
            self.location = info.location

    def _save_session_data(self):
        '''
        Save attributes in session.
        '''
        session = current.session

        session_data = {}
        session_data['npc'] = self.npc.id
        session_data['npc_image'] = self.image

        session.walk.update(session_data)

    def _get_session_data(self):
        '''
        Get the walk attributes from the session.
        '''

        db, session = current.db, current.session

        if 'npc' in session.walk:
            npc = db.npcs(session.walk['npc'])
            image = session.walk['npc_image']
        else:
            npc = None
            image = None

        location = session.walk['active_location']

        return {'image': image, 'npc': npc, 'location': location}

    def _get_image(self, row):
        '''
        Get the image to present as a depiction of the npc.
        '''
        debug = False
        db = current.db

        if debug: print row
        try:
            url = URL('static/images', db.images[row.npc_image].image)
            if debug:
                print url
            # TODO: Add title attribute
            return IMG(_src=url)
        except:
            print 'Npc._get_image(): Could not find npc image'
            return


class Location(object):
    '''
    This class finds and returns information on the student's current
    'location' within the town, based on the url variable 'loc' which
    is accessed via the web2py request object.

    implemented in:
    controllers/exploring.walk()
    '''
    debug = False

    def __init__(self, alias):

        self.alias = alias
        if alias:
            self.db_data = self._get_db(alias)
            if self.db_data:
                if self.debug:
                    print 'calling Location.__init__ ============'
                    print 'self.db_data =', self.db_data
                self.id = self.db_data.id
                self.img = self._get_img()
        else:
            self.db_data = None
            self.id = None
            self.img = None

    def _get_db(self, alias):
        '''
        Return the web2py row() object corresponding to the db record
        for the location with the given alias.
        '''
        db = current.db
        db_data = db(db.locations.alias == alias).select().first()
        return db_data

    def _get_img(self):
        '''
        Retrieve the background image for the given location and return
        it as a web2py IMG() helper object.
        '''
        db = current.db
        if self.debug:
            print 'in _get_img() self.db_data.bg_image ='
            print self.db_data.bg_image
        filename = db.images[self.db_data.bg_image].image
        img = IMG(_src=URL('static/images', filename))
        return img

    def info(self):
        '''
        Return a dict holding the location info
        '''
        if self.alias and self.alias != 'None':
            return {'alias': self.alias,
                    'id': self.id,
                    'bg_image': self.img}
        else:
            return None


class Map(object):
    '''This class returns information needed to present the navigation map'''

    def __init__(self):

        # Prepare map interface for user to select a place to go
        self.locations = self.get_locations()

        # TODO: Define this in a setting or somewhere
        self.image = '/paideia/static/images/town_map.svg'

    def get_locations(self):
        '''
        Return all locations in the game.
        '''

        db = current.db
        cache = current.cache

        # TODO: Review cache time
        return db().select(db.locations.ALL,
                           orderby=db.locations.location,
                           cache=(cache.ram, 60 * 60)).as_list()

