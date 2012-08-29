# coding: utf8
from gluon import current, URL, redirect, IMG, SQLFORM, SPAN, Field, INPUT, A
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

    verbose = True #controls printing of initialization and method calls

    def __init__(self):
        session = current.session
        request = current.request

        if self.verbose: print 'initializing Walk============================'
        if not session.walk:
            self.active_location = None
            self.path = None
            self.active_paths = {}
            self.completed_paths = set()
            self.step = None
            self.tag_set = {}
            # initialize the session properly
            self._categorize_tags()
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
        debug = True
        if self.verbose: print 'calling Walk._save_session_data--------------'
        session = current.session
        request = current.request

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
            session.walk.update(session_data)

        except AttributeError:
            session.walk = session_data

        if self.step:
            self.step._save_session_data()

        if debug: print 'self.step = ', self.step
        #if debug: print 'session.walk = ', session.walk

    def _get_session_data(self):
        '''
        Get the walk attributes from the session.
        '''
        debug = False
        if self.verbose: print 'calling Walk._get_session_data--------------'
        db, session, request = current.db, current.session, current.request

        path = session.walk['path']
        if path:
            self.path = db.paths(path)
        else:
            self.path = None

        if 'loc' in request.vars:
            location_alias = request.vars['loc']
            self.active_location = Location(location_alias).info()
            session.walk['active_location'] = self.active_location
            if debug: print 'self.active_location =', self.active_location
        else:
            self.active_location = None
            session.walk['active_location'] = None
            if debug: print 'no loc variable in request, setting loc to None'
        self.active_paths = session.walk['active_paths']
        self.completed_paths = session.walk['completed_paths']
        self.tag_set = session.walk['tag_set']

        # only initialize a step if we have entered a location
        if 'step' in session.walk and self.active_location:
            self.step = self._create_step_instance(session.walk['step'])
        else:
            self.step = None

    def _create_step_instance(self, step_id=None):
        '''
        Create an instance of a Step class or one of its subclasses based on
        the step's widget type.
        '''
        debug = True
        if self.verbose: print 'calling Walk._create_step_instance------------'
        db = current.db

        if not step_id:
            step_id = session.walk['step']
        if debug: print 'step id ='
        if debug: print step_id

        step = db.steps(step_id)
        step_type = db.step_types(step.widget_type)
        if debug: print 'step type ='
        if debug: print step_type

        return STEP_CLASSES[step_type.step_class](step_id)

    def _introduce(self):
        '''
        This method checks the user's performance and, if appropriate,
        introduces one or more new tags to the active set for selecting paths.
        This method is intended as private, to be called by categorize()
        if that method yields an initial result with no tags in category 1
        (needing immediate review).
        '''
        if self.verbose: print 'calling Walk._introduce--------------'
        auth, db = current.auth, current.db

        tag_progress = db(db.tag_progress.name == auth.user_id).select().first()
        # TODO: Check we aren't at the end
        if tag_progress:
            latest = tag_progress.latest_new + 1

            tag_progress.update(name=auth.user_id, latest_new=latest)

        else:
            latest = 1

            db.tag_progress.insert(name=auth.user_id, latest_new=latest)

        tags = [t.id for t in db(db.tags.position == latest).select()]

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
        debug = False
        if self.verbose: print 'calling Walk._categorize_tags--------------'
        auth, db = current.auth, current.db

        if not user:
            user = auth.user_id
        # check to make sure that a non-null value is given for user
        #assert type(user) = int
        if debug: print 'Debug: in Walk._categorize_tags, user =', user

        #TODO: Factor in how many times a tag has been successful or not

        # create new dictionary to hold categorized results
        categories = dict((x, []) for x in xrange(1, 5))

        record_list = db(db.tag_records.name == user).select()

        for record in record_list:
            #get time-based statistics for this tag
            #note: the arithmetic operations yield datetime.timedelta objects
            now_date = datetime.datetime.utcnow()
            right_dur = now_date - record.tlast_right
            wrong_dur = now_date - record.tlast_wrong
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
                        category = 3  # Not due, delta between a week and a month
                else:
                    category = 2  # Not due but delta is a week or less
            else:
                category = 1  # Spaced repetition requires review
            categories[category].append(record.tag.id)

        # If there are no tags needing immediate review, introduce new one
        if not categories[1]:
            categories[1] = self._introduce()

        self.tag_set = categories
        # return the value as well so that it can be used in Stats
        return categories

    def _unfinished(self):
        '''
        This public method checks for any paths that have been started but not
        finished by the current user. It expects finished paths to have a
        'last_step' value of 0 in its most recent entry in the db table
        path_log.

        called by: controllers/exploring.index()
        '''
        if self.verbose: print 'calling Walk._unfinished--------------'
        auth, db = current.auth, current.db

        path_logs = db(
            (db.path_log.name == auth.user_id) &
            (db.path_log.last_step != 0)
        ).select()

        # Get only most recent log for each unique path
        self.active_paths = {}
        for path in set(log.path for log in path_logs):
            log = max((p.dt_started, p) for p in path_logs if p.path == path)[1]
            self.active_paths[path.id] = log.last_step

    def _handle_blocks(self):
        '''
        Look for active blocking conditions:
            * no response given for an activated step
            * daily full paths limit reached
        Also checks to make sure that any path/step combination it returns
        is a valid combination.

        Returns:
            * (None, None) if there are no blocking conditions
            * (False, False) if daily path limit reached
            * Otherwise, return (path, step id) for active blocking conditions
        '''

        if self.verbose: print 'calling Walk._handle_blocks--------------'
        auth, db = current.auth, current.db

        # Are there any activated steps that haven't had a response yet?
        # Just get the first one we find
        path_logs = db(
            (db.path_log.name == auth.user_id) &
            (db.path_log.last_step != 0)
        ).select()

        # TODO: use UTC or adjust here for user's local tz?
        today = datetime.datetime.utcnow().date()

        for log in path_logs:
            #TODO: Is there a faster way to do this?
            attempts = db(
                    (db.attempt_log.name == auth.user_id) &
                    (db.attempt_log.path == log.path) &
                    (db.attempt_log.step == log.last_step) &
                    (db.attempt_log.dt_attempted >= log.dt_started)
                ).select(orderby=~db.attempt_log.dt_attempted)
            attempts = [a for a in attempts if a.dt_attempted.date() == today]

            # Activated step that hasn't had a response
            if attempts and self._step_in_path(log.path, log.last_step):
                return log.path, log.last_step

            # Retry failed step
            # TODO: Move this since all it does is ask the question repeatedly
            #       if the answer was incorrect
#            attempts = [a for a in attempts if a.score != 1.0]
#
#            if attempts:
#                attempt = attempts[0]
#                path = db(db.paths.id == attempt.path).select()[0]
#
#                return path, attempt.step

        # Have we reached the daily path limit? Return a default step.
        # TODO: Replace hardcoded limit (20)
        if len(self.completed_paths) >= 20:
            return _get_default_step()

        return None, None

    def activate_step(self, path, step_id):
        '''
        Activate the given step on the given path.
        '''
        debug = False
        if self.verbose: print 'calling Walk.activate_step--------------'
        session = current.session

        self.path = path
        self.step = self._create_step_instance(step_id)
        self.active_paths[path.id] = step_id
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
        if self.verbose: print 'calling Walk._deactivate_path--------------'
        if debug: print 'in Walk._deactivate_path, path =', path

        self._update_path_log(path, 0, 1)
        del self.active_paths[path]
        self.completed_paths.add(path)
        self.save_session_data()

    def _get_default_step(self):
        '''
        Return the default path and step, a StepStub directing the user
        to try another location.
        '''
        debug = False
        if self.verbose: print 'calling Walk._get_default_step--------------'
        session, db = current.session, current.db

        default_tag = db(db.tags.tag == 'default').select()[0]

        if debug:
            for p in self._get_paths():
                if default_tag.id in p.tags:
                    print 'DEBUG: in Walk._get_default_step, %s --> %s'\
                                                            % (p.id, p.tags)
        paths = [p for p in self._get_paths() if default_tag.id in p.tags]

        # Choose a path at random
        path = paths[random.randrange(0, len(paths))]

        return path, path.steps[0]

    def next_step(self):
        '''
        Choose a new path and step for the user, based on tag performance.
        Checks first for any blocking conditions and constrains the
        choice of next step accordingly.
        '''
        debug = False
        if self.verbose: print 'calling Walk.next_step--------------'

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
            # If possible, continue an active path whose next step is here.
            active_path = self._get_next_step()

            self.activate_step(active_path['path'], active_path['step'])
            self._save_session_data()

            return

    def _step_in_path(self, path, step=None):
        '''
        Check the given step id to make sure it is in the given path. If so,
        return the index of the given step in the path. If no step is given
        use the last completed step (as recorded in self.active_paths).
        If the step is not in the given path, return False.
        '''
        debug = False
        if self.verbose: print 'calling Walk._step_in_path--------------'

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
            if debug: print 'step', step, 'is in path', path.id
            return step_index
        # If impossible step id is given in active_paths
        except ValueError, err:
            if debug: print 'ValueError:', err
            if debug: print 'step', step, '*not* in path', path.id
            # Remove this path from active paths
            if path.id in self.active_paths:
                del self.active_paths[path.id]
                self._save_session_data()
            if debug: print 'self.active_paths now=', self.active_paths

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

        if debug: print 'No path to continue here'

        return False

    def _get_next_step(self):
        '''
        Determines what path and step to activate next and returns them as
        a dictionary with the keys 'path' and 'step'.

        The method looks (in order of preference) for:
        1) an active path whose next step is in this location;
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
        debug = False
        if self.verbose: print 'calling Walk._get_next_step--------------'
        session, db = current.session, current.db

        loc_id = self.active_location['id']

        # 1) try to continue an active path whose next step is in this loc
        if self.active_paths:
            if debug: print 'DEBUG: in Walk._get_next_step(),'
            if debug: print 'looking for active paths in this location'
            apaths = db(db.paths.id.belongs(self.active_paths.keys())).select()
            ahere = apaths.find(lambda row: loc_id in row.locations)

            for path in ahere:
                # make sure step belongs to the path
                step_index = self._step_in_path(path)
                if not step_index:
                    continue
                # If the last completed step was not the final in the path
                # try to activate the next step.
                if len(path.steps) > (step_index + 1):
                    step_id = path.steps[step_index + 1]
                    step = db(db.steps.id == step_id).select()[0]
                    if not loc_id in step.locations:
                        path, step_id = self._get_default_step()

                    self.active_paths[path.id] = step_id
                    self._save_session_data()
                    self._update_path_log(path.id, step_id, 1)

                    return dict(path=path, step=step_id)
                # If the last step in the path is completed, deactivate path
                else:
                    self._deactivate_path(path.id)
                    continue

            # 2) look for an active path in another location
            if debug: print 'Looking for an active path elsewhere'
            hlist = ahere.as_list()
            active_elsewhere = apaths.exclude(lambda row: row in hlist)
            if active_elsewhere:
                if debug: print 'A path active in another location'
                if debug: print 'calling Walk._get_default_step()'
                path, step_id = self._get_default_step()

                return dict(path=path, step=step_id)

        # 3)-4) look for a new path due, first in this location and otherwise
        # in another location
        if debug: print 'no active paths, looking for a new path'
        tag_list = []
        for category in xrange(1, 5):
            tag_list.extend(self.tag_set[category])
        if debug: print 'tag_list =', tag_list
        if debug: print 'tag_set =', self.tag_set

        tag_records = db(
                db.tag_records.tag.belongs(tag_list)
            ).select(orderby=db.tag_records.tag)

        elsewhere = False
        for tag_id in tag_list:
            try:
                record = tag_records.find(lambda row: row.tag == tag_id)[0]
                if not (record.path.id in self.active_paths or
                        record.path.id in self.completed_paths):
                    path = db.paths(record.path.id)

                    # Here we're returning the new path for this loc
                    if loc_id in path.locations:
                        if debug: print 'found a new path due here'
                        return dict(path=path, step=path.steps[0])

                    elsewhere = True
                    if debug: print 'found new path due elsewhere'
            except:
                continue

        # 4) Here we've found that a new path is due elsewhere, so we're
        # returning the default step
        if elsewhere:
            path, step_id = self._get_default_step()

            return dict(path=path, step=step_id)

        # 5) Choose a random path that can be started here
        if debug: print 'looking for random path'
        # TODO: This will throw errors
        paths = self._get_paths()
        path = paths[random.randrange(0, len(paths))]

        return dict(path=path, step=path.steps[0])

    # TODO: Is this method now used anywhere?
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
        debug = False
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
        if self.verbose: print 'Initializing Step============================='

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
        if self.verbose: print 'calling Step._save_session_data--------------'
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
        if self.verbose: print 'calling Step._get_session_data--------------'
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
        if self.verbose: print 'calling Step.ask----------------------------'
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
        if self.verbose: print 'calling Step._get_npc------------------------'
        debug = False

        def _get_npc_internal(npcs):
            '''
            Return an npc from the set of npcs or None if there aren't any.
            '''
            if self.verbose: print 'calling Step._get_npc_internal-----------'
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
        if self.verbose: print 'calling Step.process-----------'
        session, db, auth = current.session, current.db, current.auth

        # Get the student's response to the question
        user_response = user_response.strip()

        # Get the correct answer information from db
        answer1 = self.step.response1
        answer2 = self.step.response2
        answer3 = self.step.response3
        readable = self.step.readable_response
        i = len(readable)
        if i > 1: i = 2
        readable = readable.split('|')[:(i + 1)]
        readable = '\n'.join(readable)

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
                'readable': readable,
                'npc_img': session.walk['npc_image'],
                'bg_image': self.location['bg_image']}

    def _record(self, score, times_wrong_incr):
        '''
        Record the results of this step in db tables attempt_log and
        tag_records. score gives the increment to add to 'times right' in
        records. times_wrong gives the opposite value to add to 'times wrong'
        (i.e., negative score).
        '''
        if self.verbose: print 'calling Step._record-------------------------'
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
                    val = db.tag_records.insert(
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

        # DONE: Update the path log for this attempt
        # TODO: Merge this with Walk._update_path_log()
        # DONE: Set last_step to 0 if path has been completed
        query = (db.path_log.path == self.path.id) & (db.path_log.name == auth.user_id)
        log = db(query).select(orderby=~db.path_log.dt_started).first()
        if log:
            log.update_record(path=self.path.id, last_step=self.step.id)
        else:   # We should have an existing path_log but in case not...
            db.path_log.insert(path=self.path.id, last_step=self.step.id)

        # Log this step attempt
        db.attempt_log.insert(step=self.step.id, score=score, path=self.path.id)

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
        if self.verbose: print 'calling Step._get_prompt-----------'
        db, auth = current.db, current.auth

        uname = auth.user['first_name']
        rawtext = self.step.prompt
        newtext = rawtext.replace('[[user]]', uname)
        text = SPAN(newtext)

        #TODO: get audio file for prompt text as well.
        audio = ''

        return text  # audio

    def _get_responder(self):
        '''
        Create and return the form to receive the user's response for this
        step.
        '''
        if self.verbose: print 'calling Step._get_responder-----------'

        if isinstance(self, StepStub):
            return

        session, request = current.session, current.request
        response = current.response

        form = SQLFORM.factory(
                   Field('response', 'string', requires=IS_NOT_EMPTY()),
                   _autocomplete='off'
               )

        return form


class StepMultipleChoice(Step):
    def _get_responder(self):
        '''
        create and return the form to receive the user's response for this
        step
        '''
        if self.verbose: print 'calling StepMultipleChoice._get_responder-----'
        session, request = current.session, current.request

        vals = self.step.options
        form = SQLFORM.factory(
                   Field('response', 'string',
                    requires=IS_IN_SET(vals),
                    widget=SQLFORM.widgets.radio.widget))
        if form.process().accepted:
            session.response = request.vars.response

        return form

    def process(self):

        if self.verbose: print 'calling StepMultipleChoice._get_responder----'
        pass


class StepStub(Step):
    '''
    A step type that does not require significant user response. Useful for
    giving the user information and then freeing her/him up to perform a task.
    '''

    verbose = True

    def ask(self):
        '''
        Public method. Returns the html helpers to create the view
        for the 'ask' state of the user interface.
        '''
        if self.verbose: print 'calling StepMultipleChoice._get_responder----'

        npc = self._get_npc()
        prompt = self._get_prompt()

        self._save_session_data()

        return dict(npc_img=npc.image, prompt=prompt,
                bg_image=self.location['bg_image'])

    def complete(self):
        '''
        Complete this step:
            * Update the path_log
            * Update the attempt_log
            * Remove path from active paths
            * Add path to completed paths

        Note that the user always gets the step right.
        '''

        session, db, auth = current.session, current.db, current.auth

        # TODO: remove all of this commented code, since StepStubs
        # shouldn't be recorded as tag attempts (can't fail)
        #utc_now = datetime.datetime.utcnow()

        #tag_records = db(db.tag_records.name == auth.user_id).select()

        ## Calculate record info
        #time_last_right = utc_now
        #time_last_wrong = utc_now

        #times_right = 1
        #times_wrong = 0

        ## TODO: step stubs shouldn't be recorded in tag_records
        ## Log this tag attempt for each tag in the step
        #for tag in self.step.tags:
            ## Try to update an existing record for this tag
            #try:
                #tag_records = tag_records.find(lambda row: row.tag == tag)

                #if tag_records:
                    #tag_record = tag_records[0]

                    #time_last_wrong = tag_record.tlast_wrong

                    #times_right += tag_record.times_right

                    #tag_record.update_record(
                        #tlast_right=time_last_right,
                        #tlast_wrong=time_last_wrong,
                        #times_right=times_right,
                        #times_wrong=times_wrong,
                        #path=self.path.id,
                        #step=self.step.id
                    #)

                #else:
                    #val = db.tag_records.insert(
                        #tag=tag,
                        #tlast_right=time_last_right,
                        #tlast_wrong=time_last_wrong,
                        #times_right=times_right,
                        #times_wrong=times_wrong,
                        #path=self.path.id,
                        #step=self.step.id
                    #)

            # Print any other error that is thrown
            # TODO: Put this in a server log instead/as well or create a ticket
            # TODO: Do we want to rollback the transaction?
            #except Exception, err:
                #print 'unidentified error:'
                #print type(err)
                #print err
                #print traceback.format_exc()

        # TODO: Merge this with Walk._update_path_log()
        query = (db.path_log.path == self.path.id) & (db.path_log.name ==
                                                                auth.user_id)
        log = db(query).select(orderby=~db.path_log.dt_started).first()
        if log:
            log.update_record(path=self.path.id, last_step=0)
        else:   # We should have an existing path_log but in case we don't...
            db.path_log.insert(path=self.path.id, last_step=0)

        # Log this step attempt
        # TODO: Giving this attempt a score value will throw off stats
        db.attempt_log.insert(step=self.step.id, score=1.0, path=self.path.id)

        # Remove from active_paths and add to completed_paths
        del session.walk['active_paths'][self.path.id]
        session.walk['completed_paths'].add(self.path.id)


class StepImage(Step):
    pass


class StepImageMultipleChoice(Step):
    pass

STEP_CLASSES = {
        'step': Step,
        'step_mutlipleChoice': StepMultipleChoice,
        'step_stub': StepStub,
        'step_image': StepImage,
        'step_imageMutlipleChoice': StepImageMultipleChoice,
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
        db = current.db

        try:
            url = URL('static/images', self.npc.npc_image.image)
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
