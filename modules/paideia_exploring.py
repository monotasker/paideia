# coding: utf8
from gluon import current, redirect, Field
from gluon import IMG, SQLFORM, SPAN, DIV, URL, A, UL, LI, MARKMIN
from gluon import IS_NOT_EMPTY, IS_IN_SET
#from gluon.sql import Row, Rows

import datetime
import random
import re
import traceback


# TODO: Deprecate eventually
class Utils(object):
    '''
    Miscellaneous utility functions, gathered in a class for convenience.
    '''
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

    def __init__(self):
        session = current.session
        auth = current.auth

        if self.verbose:
            print 'initializing Walk============================'
        if not session.walk:
            self.active_location = None
            self.path = None
            self.active_paths = {}
            self.completed_paths = set()
            self.step = None
            # initialize the session properly
            self.tag_set = self._categorize_tags()
            self.new_badges = self._new_badges(auth.user_id, self.tag_set)
            self._unfinished()
            self._save_session_data()
        else:
            self._get_session_data()

        self.map = Map()
        self.staying = False

    def _save_session_data(self):
        '''
        Save attributes in session.
        '''
        #debug = True
        if self.verbose:
            print 'calling Walk._save_session_data--------------'
        session = current.session

        session_data = {}

        if self.path:
            session_data['path'] = self.path.id
        else:
            session_data['path'] = None

        if self.active_location:
            session_data['active_location'] = self.active_location
        session_data['active_paths'] = self.active_paths
        session_data['completed_paths'] = self.completed_paths
        session_data['tag_set'] = self.tag_set
        try:
            session_data['new_badges'] = self.new_badges
        except AttributeError:
            pass

        try:
            session.walk.update(session_data)
        except AttributeError:
            session.walk = session_data

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

        path = session.walk['path']
        if path:
            self.path = db.paths(path)
        else:
            self.path = None

        if 'loc' in request.vars:
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
        self.active_paths = session.walk['active_paths']
        self.completed_paths = session.walk['completed_paths']
        self.tag_set = session.walk['tag_set']

        # create step instance here if we're processing a user's response
        if ('response' in request.vars) and (request.args(0) == 'ask'):
            self.step = self._create_step_instance()
            print 're-activating step'

    def _create_step_instance(self, step_id=None):
        '''
        Create an instance of a Step class or one of its subclasses based on
        the step's widget type.
        '''
        debug = True
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
        This method checks the user's performance and, if appropriate,
        introduces one or more new tags to the active set for selecting paths.
        This method is intended as private, to be called by categorize()
        if that method yields an initial result with no tags in category 1
        (needing immediate review).
        '''
        if self.verbose:
            print 'calling Walk._introduce--------------'
        auth = current.auth
        db = current.db
        session = current.session

        tag_progress = db(db.tag_progress.name == auth.user_id).select()[0]
        # TODO: Check we aren't at the end of the tag progression
        if tag_progress:
            latest = tag_progress.latest_new + 1

            tag_progress.update(name=auth.user_id, latest_new=latest)

        else:
            latest = 1

            db.tag_progress.insert(name=auth.user_id, latest_new=latest)

        tags = [t.id for t in db(db.tags.position == latest).select()]
        # TODO: Use slide deck titles (so correlate them with tags somewhere)
        session.walk['view_slides'] = tags

        return tags

    def _categorize_tags(self, user=None):
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
        debug = True
        if self.verbose: print 'calling Walk._categorize_tags--------------'
        auth = current.auth
        db = current.db

        if not user:
            user = auth.user_id
        #TODO: Factor in how many times a tag has been successful or not

        # create new dictionary to hold categorized results
        categories = dict((x, []) for x in xrange(1, 5))

        record_list = db(db.tag_records.name == user).select()

        for record in record_list:
            #get time-based statistics for this tag
            #note: the arithmetic operations yield datetime.timedelta objects
            now_date = datetime.datetime.utcnow()
            right_dur = now_date - record.tlast_right
            right_wrong_dur = record.tlast_right - record.tlast_wrong

            # Categorize q or tag based on this performance
            if right_dur < right_wrong_dur:
                if right_wrong_dur.days >= 7:
                    if right_wrong_dur.days > 30:
                        if right_wrong_dur > datetime.timedelta(days=180):
                            category = 1  # Not due, not attempted for 6 months
                        else:
                            category = 4  # Not due, delta more than a month
                    else:
                        category = 3  # Not due, delta between a week and month
                else:
                    category = 2  # Not due but delta is a week or less
            else:
                category = 1  # Spaced repetition requires review
            categories[category].append(record.tag.id)

        if debug: print categories

        # Remove duplicate tag id's from each category
        for k, v in categories.iteritems():
            categories[k] = list(set(v))

        # If there are no tags needing immediate review, introduce new one
        if not categories[1]:
            categories[1] = self._introduce()

        self.tag_set = categories
        # return the value as well so that it can be used in Stats
        return categories

    def _new_badges(self, user, categories):
        '''
        Find any tags that have been newly promoted to a higher category,
        update the user's row in db.tag_progress, and return a dictionary of
        those new tags whose structure mirrors that of session.walk['tag_set'].
        '''
        if self.verbose: print 'calling Walk._new_badges ---------------------'
        debug = True
        db = current.db
        auth = current.auth

        # If a tag has moved up in category, award the badge
        # TODO: needs to be tested!!!
        mycats = db(db.tag_progress.name == auth.user_id).select().first()
        if debug: print 'mycats =', mycats

        new_badges = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        all_badges = {'cat1': [], 'cat2': [], 'cat3': [], 'cat4': []}
        for categ, lst in categories.iteritems():
            if lst:
                print 'current badges =', lst
                categ = 'cat{0}'.format(str(categ))
                if mycats and mycats[categ]:
                    new = [t for t in lst if t not in mycats[categ]]
                else:
                    new = [t for t in lst]
                if new:
                    if debug: print 'newly awarded badges =', new
                    new_badges[categ] = new
                    all_badges[categ] = new + lst

        db.tag_progress.update_or_insert(**{
                                            'name': auth.user_id,
                                            'cat1': all_badges['cat1'],
                                            'cat2': all_badges['cat2'],
                                            'cat3': all_badges['cat3'],
                                            'cat4': all_badges['cat4'],
                                            })

        if new_badges:
            if debug: print 'new badges =', new_badges
            return new_badges
        else:
            if debug: print 'no new badges awarded'
            return None

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
        auth, db, session = current.auth, current.db, current.session

        if 'new_badges' in session.walk:
            return self._get_util_step('award badge')  # tag id=81

        # TODO: insert these session.walk values in _introduce and _categorize)
        if 'view_slides' in session.walk:
            return self._get_util_step('view slides')  # tag id=80

        # TODO: need to fix check for step that was never finished
        #upath, ustep = self._unfinished_today()
        #if upath:
            #return upath, ustep

        # Have we reached the daily path limit? Return a default step.
        # TODO: Replace hardcoded limit (20)
        if len(session.walk['completed_paths']) >= 20:
            if 'quota_override' in session.walk and \
                                                session.walk['quota_override']:
                pass
            else:
                return self._get_util_step('end of quota')  # tag id=79

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
        debug = True
        if self.verbose:
            print 'calling Walk.activate_step--------------'
        session = current.session
        db = current.db

        # allow for situations where the path id is given rather than the
        # path's row object. (As in 'retry' state.)
        if type(path) == int:
            path = db.paths[path]

        self.path = path
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
        if debug:
            print 'in Walk._deactivate_path, path =', path

        self._update_path_log(path, 0, 1)
        del self.active_paths[path]
        self.completed_paths.add(path)
        self._save_session_data()

    def _get_util_step(self, tag):
        '''
        Return the default path and step for a particular utility situation.
        These include
        - having reached the daily quota of completed paths
        - having an incomplete path whose next step is in another location
        - having a newly introduced tag whose slides must be viewed
        - having a newly awarded badge
        '''
        debug = True
        if self.verbose:
            print 'calling Walk._get_util_step--------------'
        session, db = current.session, current.db

        tag_id = db(db.tags.tag == tag).select()[0].id
        steps = db(db.steps.tags.contains(tag_id)).select()
        if debug:
            print 'steps with tag', tag, 'id=', tag_id
            print steps

        # Choose a step at random
        if len(steps) > 1:
            step = steps[random.randrange(0, len(steps))]
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
        debug = True
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
        debug = True
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
        if self.active_paths:
            if debug:
                print 'looking for active paths in this location'
                print 'active_paths =', self.active_paths
            apaths = db(db.paths.id.belongs(self.active_paths.keys())).select()

            for path in apaths:
                # make sure step belongs to the path
                step_id = self.active_paths[path.id]
                step_index = self._step_in_path(path, step_id)
                if debug:
                    print 'index of the last started step is', step_index
                if type(step_index) is bool:
                    if debug:
                        print 'step', step_id, 'not in path', path.id
                    continue

                # 1) try to activate the next step if it can be done here.
                if len(path.steps) > (step_index + 1):
                    if debug:
                        print len(path.steps), 'steps in this path'
                    step_id = path.steps[step_index + 1]
                    step = db.steps[step_id]
                    if debug: print step

                    # 2) If not in this location, send user elsewhere
                    if debug: print 'loc_id =', loc_id
                    if debug: print 'step.locations =', step.locations
                    if not loc_id in step.locations:
                        if debug:
                            print 'next step elsewhere, getting default'
                        return self._get_util_step('default')

                    self.active_paths[path.id] = step_id
                    self._update_path_log(path.id, step_id, 1)
                    if debug:
                        print 'getting next step', step_id
                        print 'of path', path.id
                    return path, step_id
                # If the last step in the path is completed, deactivate path
                # and try the next in apaths
                else:
                    self._deactivate_path(path.id)
                    if debug:
                        print 'last step already completed for path', path.id
                    continue

        # 3)-4) look for a new path due, first in this location and otherwise
        # in another location
        if debug: print 'no active paths, looking for a new path'  # DEBUG

        cat = self._get_category()
        cat_range = self.tag_set.keys()
        cat_list = cat_range[cat:5] + cat_range[0:cat]
        if debug: print 'category list to try:', cat_list

        # cycle through categories, starting with the one from _get_category()
        for cat in cat_list:
            if debug: print 'Trying category', cat  # DEBUG
            tag_list = self.tag_set[cat]
            p_list = db(db.paths.id > 0).select()
            p_list = p_list.find(lambda row: [t in row.tags for t in tag_list])
            # exclude paths completed in this session
            if self.completed_paths:
                p_list.exclude(lambda row: row.id in self.completed_paths)
            if p_list:
                if debug: print 'some new paths are available in cat', cat
                # 3) Find and activate a due path that starts here
                for path in p_list:
                    step1_id = path.steps[0]
                    first_step = db.steps[step1_id]
                    if loc_id in first_step.locations:
                        print 'found path', path.id, 'step', step1_id, 'due'
                        return path, step1_id
                    else:
                        continue
                # 4) If due paths are elsewhere, trigger default step
                return self._get_util_step('default')

        #TODO: Fall back here to repeating random paths from completed_paths
        # first that can be started here
        # then that can't (trigger default step)

        # 5) Choose a random path that can be started here
        if debug: print 'looking for random path with active tags'  # DEBUG
        paths = self._get_paths()
        max_rank = db(db.tag_progress.name == auth.user_id).first().latest_new
        tag_list = db(db.tags.id <= max_rank)
        paths.find(lambda row: [t in row.tags for t in tag_list])
        path = paths[random.randrange(0, len(paths))]

        return path, path.steps[0].id

    def _get_category(self):
        '''
        Choose one of four categories with a random factor but a heavy
        weighting toward category 1
        '''

        if self.verbose: print 'calling Walk._get_category--------------'
        switch = random.randrange(1, 101)

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
            query = (db.path_log.path == path_id) & (db.path_log.name ==
                                                                auth.user_id)
            log = db(query).select(orderby=~db.path_log.dt_started).first()
            log.update_record(path=path_id, last_step=step_id)
        else:
            db.path_log.insert(path=path_id, last_step=step_id)


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
        debug = True
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

        npc = self._get_npc()
        prompt = self._get_prompt()
        responder = self._get_responder()
        self._save_session_data()
        if debug: print 'bg_image =', self.location['bg_image']

        return dict(npc_img=npc.image, prompt=prompt,
                    responder=responder,
                    bg_image=self.location['bg_image'])

    def _get_npc(self):
        '''
        Given a set of npcs for this step select one of the npcs at random and
        return the corresponding Npc object.
        '''
        # TODO: Make sure that subsequent steps of the current path use the
        # same npc if in the same location
        if self.verbose:
            print 'calling', type(self).__name__, '._get_npc--------------'
        debug = False

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
                return npcs[random.randrange(1, npc_count) - 1]
            elif npc_count == 1:
                return npcs[0]
            else:
                return None

        db, session = current.db, current.session

        if session.walk['active_location'] is None:
            return   # TODO: maybe we return a 404 here (or in ask(), etc.)?

        if debug: print 'self.location =', self.location
        npcs = db(
                    (db.npcs.id.belongs(self.step.npcs)) &
                    (db.npcs.location.contains(self.location['id']))
                ).select()

        npc = _get_npc_internal(npcs)

        # If we haven't found an npc at the location and step, get a random one
        # from this location.
        if not npc:
            npcs = db(db.npcs.location.contains(self.location['id'])).select()

            npc = _get_npc_internal(npcs)

        # If we haven't found an npc at the location, get a random one from
        # this step.
        if not npc:
            npcs = db((db.npcs.id.belongs(self.step.npcs))).select()

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
        session, db, auth = current.session, current.db, current.auth

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
            else:
                score = 0
                reply = "Incorrect. Try again!"

            # Set the increment value for times wrong, depending on score
            if score < 1:
                times_wrong = 1
            else:
                times_wrong = 0

            # Record the results in statistics for this step and this tag
            self._record(score, times_wrong)

        # Handle errors if the student's response cannot be evaluated
        except re.error:
            redirect(URL('index', args=['error', 'regex']))

        # TODO: This replaces the Walk.save_session_data() that was in the
        # controller. Make sure this saving of step data is enough.
        self._save_session_data()

        return {'reply': reply,
                'readable': readable_short,
                'readable_long': readable_long,
                'bug_reporter': self._get_bug_reporter(),
                'npc_img': session.walk['npc_image'],
                'bg_image': self.location['bg_image']}

    def _get_bug_reporter(self):
        '''
        Construct and return a SPAN helper containing the contents of the
        tooltip containing the message and link allowing students to submit
        a bug report for the current step.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '._get_bug_reporter-----'
        request, response = current.request, current.response

        bug_reporter = DIV(_class='tip bug_reporter')
        text1 = SPAN('If you think your answer wasn\'nt evaluated properly, ')
        link = A('click here',
                    _href=URL('creating', 'bug.load',
                                vars=dict(answer=request.vars.response,
                                loc=request.vars.loc)),
                    cid='bug_reporter',
                    _class='button-bug-reporter')
        text2 = SPAN('to submit a bug report for this question.')
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
        if self.verbose:
            print 'calling', type(self).__name__, '._record---------------'
        db, auth, session = current.db, current.auth, current.session

        utc_now = datetime.datetime.utcnow()

        tag_records = db(db.tag_records.name == auth.user_id).select()

        # Calculate record info
        time_last_right = utc_now
        time_last_wrong = utc_now

        times_right = score
        times_wrong = times_wrong_incr

        # Log this tag attempt for each tag in the step
        for tag in self.step.tags:
            # Try to update an existing record for this tag
            try:
                tag_records = tag_records.find(lambda row: row.tag == tag)

                if tag_records:
                    tag_record = tag_records[0]

                    if score == 1:
                        time_last_wrong = tag_record.tlast_wrong
                    elif score == 0:
                        time_last_right = tag_record.tlast_right
                    else:
                        score = 0
                        time_last_right = tag_record.tlast_right

                    times_right += tag_record.times_right
                    times_wrong += tag_record.times_wrong

                    tag_record.update_record(
                        tlast_right=time_last_right,
                        tlast_wrong=time_last_wrong,
                        times_right=times_right,
                        times_wrong=times_wrong,
                        path=self.path.id,
                        step=self.step.id
                    )

                else:
                    db.tag_records.insert(
                        tag=tag,
                        tlast_right=time_last_right,
                        tlast_wrong=time_last_wrong,
                        times_right=times_right,
                        times_wrong=times_wrong,
                        path=self.path.id,
                        step=self.step.id
                    )

            # Print any other error that is thrown
            # TODO: Put this in a server log instead/as well or create a ticket
            # TODO: Do we want to rollback the transaction?
            except Exception, err:
                print 'unidentified error:'
                print type(err)
                print err
                print traceback.format_exc()

        # TODO: Merge this with Walk._update_path_log()?
        log = db(
                (db.path_log.path == self.path.id) &
                (db.path_log.name == auth.user_id)
                ).select(orderby=~db.path_log.dt_started).first()

        if log:
            log.update_record(path=self.path.id, last_step=self.step.id)
        else:   # We should have an existing path_log but in case not...
            db.path_log.insert(path=self.path.id, last_step=self.step.id)

        # Log this step attempt
        db.attempt_log.insert(step=self.step.id,
                              score=score,
                              path=self.path.id)

        # Check to see whether this is the last step in the path and if so
        # remove from active_paths and add to completed_paths
        if self.path.steps[-1] == self.step.id:
            del session.walk['active_paths'][self.path.id]
            session.walk['completed_paths'].add(self.path.id)

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
            for k, v in self._get_replacements().iteritems():
                newtext = newtext.replace(k, v.xml())
        except AttributeError:
            if debug: print 'No replacements for this Step type'

        prompt = MARKMIN(newtext)

        try:
            prompt.append(self._get_step_image())
        except AttributeError:
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
        debug = True

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

        session, request = current.session, current.request

        form = SQLFORM.factory(
                    Field('response', 'string', requires=IS_NOT_EMPTY()),
                    _autocomplete='off'
                )
        instructions = self._get_instructions()
        wrapper = DIV(form, instructions, _class='responder')

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
        readable = self.step.readable_response

        # Compare the student's response to the stored answers
        if answer1 == readable:
            score = 1
            reply = "Right. Κάλον."
        elif answer2 != 'null' and answer1 == readable:
            score = 0.5
            #TODO: Get this score value from the db instead of hard
            #coding it here.
            reply = "Οὐ κάκον. You're close."
            #TODO: Vary the replies
        elif answer3 != 'null' and answer1 == readable:
            #TODO: Get this score value from the db instead of hard
            #coding it here.
            score = 0.3
        else:
            score = 0
            reply = "Sorry, that wasn't right. Try again!"

        # Set the increment value for times wrong, depending on score
        if score < 1:
            times_wrong = 1
        else:
            times_wrong = 0

        # Record the results in statistics for this step and this tag
        self._record(score, times_wrong)

        # TODO: This replaces the Walk.save_session_data() that was in the
        # controller. Make sure this saving of step data is enough.
        self._save_session_data()

        return {'reply': reply,
                'readable': answer1,
                'bug_reporter': self._get_bug_reporter(),
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

    def complete(self):
        '''
        Complete this step:
            * Do not update the path_log
            * Do not update the attempt_log
            * Remove path from active paths
            * Add path to completed paths

        Note that the user always gets the step right.
        '''
        if self.verbose:
            print 'calling', type(self).__name__, '.complete -------------'
        session = current.session

        del session.walk['active_paths'][self.path.id]
        #TODO: completed_paths shouldn't count utility paths
        session.walk['completed_paths'].add(self.path.id)

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
        return map_button


class StepNonBlocking(Step):
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

        return buttons


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
        debug = True
        session = current.session
        db = current.db

        badges = ''
        if 'new_badges' in session.walk:
            for k, v in session.walk['new_badges'].iteritems():
                if k == 'cat1':
                    for tag in v:
                        badge = db(db.badges.tag == tag).select().first()
                        badge_name = '{0} {1},'.format('beginner',
                                                       badge.badge_name)
                        badges += badge_name
                    if badges[-1] == ',':
                        badges = badges[:len(badges)]
        if debug: print 'badges =', badges

        slides = ''
        if 'view_slides' in session.walk:
            for t in session.walk['view_slides']:
                # convert this to link once plugin_slider supports it
                tag_slides = db.tags[t].slides
                title_list = [db.plugin_slider_decks[d].deck_name
                                                        for d in tag_slides]
                for li in title_list:
                    slides += '- {0}'.format(li)
        if debug: print 'slides =', slides

        replacements = {'[[badge_list]]': badges, '[[slides]]': slides}

        return replacements

    pass


class StepDailyQuota(StepNonBlocking, StepStub):
    '''
    This step class alerts the user that the daily quota of paths has been
    completed, but provides a continue button (from StepNonBlocking). As in
    StepStub, it still does not allow processing of any user response.
    '''
    #TODO: provide self._get_substitution override method to sub in the
    # user's required quota of paths per day.
    verbose = True

    def _get_replacements(self):
        '''
        Just here as a hook to introduce _add_flag into the step processing
        cycle.
        '''
        self._add_flag()

    def _add_flag(self):
        '''
        Add the session flag overriding the user's daily quota
        of steps, allowing the user to continue on to a new step.
        '''
        session = current.session

        session.walk['quota_override'] = True


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
        debug = True
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
                        badge = db(db.badges.tag == tag).select().first()
                        if debug: print 'badge =', badge
                        ranks = ['beginner', 'apprentice',
                                                'journeyman', 'master']
                        try:
                            #TODO: chokes on this line if badge == None
                            badge_name = '{0} {1}'.format(ranks[n - 1],
                                                          badge.badge_name)
                            rank_verbs = ['starting to learn',
                                            'making good progress with',
                                            'gaining a good working grasp of',
                                            'mastering']
                            badge_desc = 'for {0} {1}'.format(
                                                        rank_verbs[n - 1],
                                                        badge.description)
                            if debug: print 'badge_desc =', badge_desc
                            badges += ('- **{0}** {1}\n'.format(badge_name,
                                                               badge_desc))
                        except:
                            badges += '- unknown\n'
        if debug: print badges
        print 'bla, bla'
        self._remove_flag()

        return {'[[badge_list]]': badges}

    def _remove_flag(self):
        '''
        remove the session flag for newly awarded badges, allowing the user
        to continue on to a new step.
        '''
        session = current.session

        del session.walk['new_badges']
        print 'removed award badges flag'


class StepImage(Step):
    '''
    This subclass of Step adds an image in the prompt area.
    '''
    verbose = True

    def _get_step_image(self):
        '''
        Returns the image to be displayed in the step prompt, wrapped in a
        web2py IMG() helper object.
        '''
        debug = True
        if self.verbose:
            print 'calling', type(self).__name__, '._get_step_image -----'
        try:
            url = URL('static/images', self.step.widget_image)
            if debug:
                print url
            return IMG(_src=url)
        except:
            print '._get_image(): Could not find npc image'
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
            self.image = self._get_image()

            self._save_session_data()

        else:
            self._get_session_data()

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
            self.npc = db.npcs(session.walk['npc'])
            self.image = session.walk['npc_image']
        else:
            self.npc = None
            self.image = None

        self.location = session.walk['active_location']

    def _get_image(self):
        '''
        Get the image to present as a depiction of the npc.
        '''
        debug = False

        try:
            url = URL('static/images', self.npc.npc_image.image)
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
        if self.alias:
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
