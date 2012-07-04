# coding: utf8
from gluon import current, URL, redirect, IMG, SQLFORM, SPAN, Field, INPUT, A
from gluon import IS_NOT_EMPTY, IS_IN_SET
from gluon.sql import Row, Rows

import datetime, random, pprint, re, traceback


### Utility functions

### End utility functions

# TODO: Deprecate eventually
class Utils(object):
    '''
    Miscellaneous utility functions, gathered in a class for convenience.
    '''

    def clear_session(self):
        session, response = current.session, current.response

        if response.vars and ('session_var' in response.vars):
            session_vars = response.vars['session_var']
        else:
            session_vars = 'all'

        if session_vars == 'all':
            session_vars = ['active_paths', 'answer', 'answer2', 'answer3',
            'blocks', 'completed_paths', 'debug', 'last_query', 'path_freq',
            'eval', 'path_freq', 'path_id', 'path_length', 'path_name',
            'path_tags', 'qID', 'q_counter', 'question_text', 'quiz_type',
            'readable_answer', 'response', 'tagset']
        if type(session_vars) is not list:
            session_vars = list(session_vars)

        for s in session_vars:
            if s in session:
                del session[s]

    def update_session(self, session_index, val, switch):
        '''insert, update, or delete property of the session object'''
        session = current.session

        if switch == 'del':
            if type(val) == tuple:
                val = val[0]
            if session_index in session and val in session[session_index]:
                del session[session_index][val]
        else:
            if session_index in session and session[session_index] is not None:
                if type(val) == tuple and (val[0] in session[session_index]):
                    session[session_index][val[0]] = val[1]
                elif type(val) == tuple:
                    session[session_index] = {val[0]:val[1]}
                else:
                    session[session_index].append(val)
            else:
                if type(val) == tuple:
                    session[session_index] = {val[0]:val[1]}
                else:
                    session[session_index] = [val]

class Walk(object):
    '''
    A class handling the "movement" of a user from one path or step to the
    next (i.e., transitions between states outside a single step). In other
    words, this class prepares path-related information needed immediately
    before path selection.
    '''

    def __init__(self):

        session = current.session

        if not session.walk:
            self.active_location = None
            self.path = None
            self.active_paths = {}
            self.completed_paths = set()
            self.step = None
            self.tag_set = []

        else:
            self.get_session_data()

        self.map = Map()

    def save_session_data(self):
        '''
        Save attributes in session.
        '''

        session = current.session

        session_data = {}

        if self.path:
            session_data['path'] = self.path.id
        else:
            session_data['path'] = None

        session_data['active_paths'] = self.active_paths
        session_data['completed_paths'] = self.completed_paths
        if self.active_location:
            session_data['active_location'] = self.active_location.location.alias
        else:
            session_data['active_location'] = None
        session_data['tag_set'] = self.tag_set

        try:
            session.walk.update(session_data)

        except AttributeError:
            session.walk = session_data

        if self.step:
            self.step.save_session_data()

    def get_session_data(self):
        '''
        Get the walk attributes from the session.
        '''

        db, session = current.db, current.session

        path = session.walk['path']
        if path:
            self.path = db.paths(path)
        else:
            self.path = None

        location_alias = session.walk['active_location']

        if location_alias:
            self.active_location = Location(location_alias)
        else:
            self.active_location = None
        self.active_paths = session.walk['active_paths']
        self.completed_paths = session.walk['completed_paths']
        self.tag_set = session.walk['tag_set']

        if 'step' in session.walk:
            self.step = Step()
        else:
            self.step = None

    def _introduce(self):
        '''
        This method checks the user's performance and, if appropriate,
        introduces one or more new tags to the active set for selecting paths.
        This method is intended as private, to be called by categorize()
        if that method yields an initial result with no tags in category 1
        (needing immediate review).

        :param cat:dict()

        JEFF: By convention, private methods in Python are prefixed with an underscore
              (see http://docs.python.org/tutorial/classes.html#private-variables)
        '''

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

    def categorize_tags(self):
        '''
        This method uses stored statistics for current user to categorize the grammatical
        tags based on the user's success and the time since the user last
        used the tag.

        The categories range from 1 (need immediate review) to 4 (no review
        needed).

        this method is called at the start of each user session so that
        time-based statistics can be updated.


        '''
        #TODO: Factor in how many times a tag has been successful or not
        auth, db = current.auth, current.db

        # create new dictionary to hold categorized results
        categories = dict((x, []) for x in xrange(1, 5))

        record_list = db(db.tag_records.name == auth.user_id).select()

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
                            category = 1 # Not due, but not attempted for 6 months
                        else:
                            category = 4 # Not due, delta more than a month
                    else:
                        category = 3 # Not due, delta between a week and a month
                else:
                    category = 2 # Not due but delta is a week or less
            else:
                category = 1 # Spaced repetition requires review
            categories[category].append(record.tag.id)

        # If there are no tags needing immediate review, introduce new one
        if not categories[1]:
            categories[1] = self._introduce()

        self.tag_set = categories

    def unfinished(self):
        '''
        This public method checks for any paths that have been started but not
        finished by the current user. It expects finished paths to have a
        'last_step' value of 0 in its most recent entry in the db table
        path_log.

        implemented by:

        '''

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

    def pick_path(self, location):
        '''
        Choose a new path for the user, based on tag performance.
        '''

        # Check for active blocking conditions
        # TODO: Implement logic to do something with True result here

        # If possible, continue an active path whose next step is here
        active_paths = location.active_paths(self)
        if active_paths:
            return active_paths

        # Otherwise choose a new path
        db = current.db

        category = self.get_category()
        paths, category = self.find_paths(category, location, self.get_paths())

        path_count = len(paths)

        if not len(paths):
            print 'No available paths, so reviewing some already completed today'
            self.completed_paths = set()
            paths, category = self.find_paths(category, location, self.get_paths())

        path = paths[random.randrange(0, len(paths))]

        step_id = path.steps[0]
        print 'activating step: ', step_id

        #set session flag showing that this path is now active
        self.path = path
        self.save_session_data()

        self.step = Step(step_id)

        # Log this attempt of the step
        self.update_path_log(path.id, step_id, 0)

    def get_category(self):
        '''
        Choose one of four categories with a random factor but a heavy
        weighting toward category 1
        '''
        switch = random.randrange(1,101)

        if switch in range(1,75):
            category = 1
        elif switch in range(75,90):
            category = 2
        elif switch in range(90,98):
            category = 3
        else:
            category = 4
        return category

    def get_paths(self):
        '''
        Return all paths in the game.
        '''

        db = current.db
        cache = current.cache

        # TODO: Review cache time
        return db().select(db.paths.ALL,
                        orderby=db.paths.id,
                        cache=(cache.ram, 60*60))

    def find_paths(self, cat, location, paths):
        '''
        Find paths for this location that are due in the specified category
        (in argument 'cat') and filter out paths that have been completed
        already today. If no tags in that category, move on to the next.
        '''

        #start with the category of tags, but loop through the categories
        #until some available paths are found
        categories = [1, 2, 3, 4]
        index = categories.index(cat)
        category_paths = None
        for category in categories[index:] + categories[:index]:
            # If any tags in this category, look for paths with these tags
            # that can be started in this location.
            tags = set(self.tag_set[category])
            if len(tags) > 0:
                category_paths = paths.find(lambda row: (
                    set(row['tags']).intersection(tags) and
                    (location.location.id in row['locations'])
                ))

                '''
                TODO: see whether the virtual fields approach above is slower
                than some version of query approach below

                catXpaths = db((db.paths.tags.contains(tags))
                                & (db.paths.locations.contains(curr_loc.id))
                            ).select()
                '''
                # Filter out any of these completed already today
                if self.completed_paths:
                    category_paths = category_paths.find(
                        lambda row: row.id not in self.completed_paths
                    )

                if category_paths:
                    break
            else:
                continue

        #TODO: work in a fallback in case no categories return any possible
        #      paths (do this in pick_path?)
        return (category_paths, category)

    def get_blocks(self):
        '''
        Find out whether any blocking conditions are in place and trigger
        appropriate responses.
        '''

        # Current object must be accessed at runtime
        session = current.session

        # Check to see whether any constraints are in place
        if 'blocks' in session:
            #TODO: Add logic here to handle blocking conditions
            #TODO: First priority is to add a blocking condition should be a
            #when the user has been presented with the prompt for a step but
            #has not submitted any response for processing. The blocking
            #condition should force the user either to return to the step
            #prompt or to submit a bug report.
            return True
        else:
            return False

    def update_path_log(self, path_id, step_id, update_switch):
        '''
        Create or update entries in the path_log table.
        '''

        auth, db = current.auth, current.db

        if update_switch:
            query = db.path_log.path == path_id & db.path_log.name == auth.user_id
            log = db(query).select(orderby=~db.path_log.dt_started).first()
            log.update_record(path=path_id, last_step=step_id)
        else:
            db.path_log.insert(path=path_id, last_step=step_id)


# TODO: Deprecate eventually
class Path(object):
    '''
    set the path a student is exploring, retrieve its data, and store
    the data in the session object

    ## session variables available:
    ### This first set is used to track information about a user's session that persists
    beyond a single step execution.

    session.active_paths (dict: id:last active step)
    session.completed (list: int for path id)
    session.tag_set (dict: each of four categories is a key, list of tag
        ids as its value)

    ### This second set should be used exclusively to preserve current data
    during execution of a single step (i.e., retrieve the results of
    path.pick() in step.process()). By the end of step.process() they
    should be returned to a value of None:

    session.step (single int)
    session.path (single int)
    session.image
    '''

    def __init__(self, loc):
        self.loc = loc

    def end(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request
        auth, db = current.auth, current.db

        pass


class Step(object):

    def __init__(self, step=None):

        db, session = current.db, current.session

        if step is not None:
            self.path = db.paths(session.walk['path'])
            self.step = db.steps(step)

            self.npc = None
            self.save_session_data()
        else:
            self.get_session_data()

    def save_session_data(self):
        '''
        Save attributes in session.
        '''

        session = current.session

        session_data = {}

        session_data['step'] = self.step.id

        session.walk.update(session_data)

        if self.npc:
            self.npc.save_session_data()

    def get_session_data(self):
        '''
        Get the step attributes from the session.
        '''

        db, session = current.db, current.session

        try:
            self.path = db.paths(session.walk['path'])
            self.step = db.steps(session.walk['step'])
            self.npc = Npc()

        except KeyError:
            self.path = db.paths(session.walk['path'])
            self.step = None
            self.npc = None

    def ask(self):
        '''
        Public method. Returns the html helpers to create the view
        for the 'ask' state of the user interface.
        '''

        npc = self.get_npc()
        prompt = self.get_prompt()
        responder = self.get_responder()

        self.save_session_data()

        session = current.session

        return dict(npc_img=npc.image, prompt=prompt, responder=responder)

    def get_npc(self):
        '''
        Given a set of npcs for this step select one of the npcs at random and
        return the corresponding Npc object.
        '''

        db, session = current.db, current.session

        if session.walk['active_location'] is None:
            return   # TODO: maybe we return a 404 here (or in ask()and other callers?)

        location = Location(session.walk['active_location'])

        npcs = db(
            (db.npcs.id.belongs(self.step.npcs)) &
            (db.npcs.location.contains(location.location.id))
        ).select()

        npc_count = len(npcs)

        if npc_count > 1:
            npc = npcs[random.randrange(1, npc_count) - 1]
        else:
            npc = npcs.first()

        self.npc = Npc(npc)

        return self.npc

    def process(self, user_response):
        '''
        Handles the user's response to the step prompt.

        In this base 'step' class this involves comparing the user's typed
        response with the regular expressions provided for the step. The
        evaluation is then logged and stored in the db, and the appropriate
        information presented to the user.
        '''

        session, db, auth = current.session, current.db, current.auth

        # Get the student's response to the question
        user_response = user_response.strip()

        # Get the correct answer information from db
        answer1 = self.step.response1
        answer2 = self.step.response2
        answer3 = self.step.response3
        readable = self.step.readable_response

        # Compare the student's response to the regular expressions
        try:
            if re.match(answer1, user_response, re.I):
                score = 1
                reply = "Right. Κάλη."
            elif answer2 != 'null' and re.match(answer2, user_response, re.I):
                score = 0.5
                #TODO: Get this score value from the db instead of hard coding it here.
                reply = "Οὐ κάκος. You're close."
                #TODO: Vary the replies
            elif answer3 != 'null' and re.match(answer3, user_response, re.I):
                #TODO: Get this score value from the db instead of hard coding it here.
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
            self.record(score, times_wrong)

        # Handle errors if the student's response cannot be evaluated
        except re.error:
            redirect(URL('index', args=['error', 'regex']))

        return dict(reply=reply, readable=readable, npc_img=self.npc.image)

    def record(self, score, times_wrong_incr):
        '''
        Record the results of this step in db tables attempt_log and
        tag_records. score gives the increment to add to 'times right' in
        records. times_wrong gives the opposite value to add to 'times wrong'
        (i.e., negative score).
        '''

        db, auth, session = current.db, current.auth, current.session

        utc_now = datetime.datetime.utcnow()

        # Log this step attempt
        db.attempt_log.insert(step=self.step.id, score=score, path=self.path.id)

        # Log this tag attempt for each tag in the step
        tag_records = db(db.tag_records.name == auth.user_id).select()

        # Calculate record info
        time_last_right = utc_now
        time_last_wrong = utc_now

        times_right = score
        times_wrong = times_wrong_incr

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
        # TODO: Merge this with Walk.update_path_log()
        query = (db.path_log.path == self.path.id) & (db.path_log.name == auth.user_id)
        log = db(query).select(orderby=~db.path_log.dt_started).first()
        if log:
            log.update_record(path=self.path.id, last_step=self.step.id)
        else:   # We should already have an existing path_log but in case we don't...
            db.path_log.insert(path=self.path.id, last_step=self.step.id)

        # Check to see whether this is the last step in the path and if so
        # remove from active_paths and add to completed_paths
        if self.path.steps[-1] == self.step:
            del session.walk['active_paths'][self.path.id]
            session.walk['completed_paths'].add(self.path.id)

    def get_prompt(self):
        '''
        Get the prompt text to be presented from the npc to start the step
        interaction.
        '''

        text = SPAN(self.step.prompt)

        #TODO: get audio file for prompt text as well.
        audio = ''

        return text#, audio

    def get_responder(self):
        '''
        Create and return the form to receive the user's response for this step.
        '''

        session, request, response = current.session, current.request, current.response

        form = SQLFORM.factory(
                   Field('response', 'string', requires=IS_NOT_EMPTY())
               )

        return form


class StepMultipleChoice(Step):
    def get_responder(self):
        '''
        create and return the form to receive the user's response for this
        step
        '''
        session, request = current.session, current.request

        vals = self.step.options
        form = SQLFORM.factory(
                   Field('response', 'string',
                    requires=IS_IN_SET(vals),
                    widget = SQLFORM.widgets.radio.widget))
        if form.process().accepted:
            session.response = request.vars.response

        return form

    def process(self):
        pass


class StepStub(Step):
    '''A step type that does not require significant user response. Useful for
    giving the user information and then freeing her/him up to perform a task.
    '''

    def get_responder(self):
        pass

    def process(self):
        pass


class Npc(object):

    def __init__(self, npc=None):

        if npc is not None:
            self.npc = npc
            self.image = self.get_image()

            self.save_session_data()

        else:
            self.get_session_data()

    def save_session_data(self):
        '''
        Save attributes in session.
        '''

        session = current.session

        session_data = {}

        session_data['npc'] = self.npc.id
        session_data['npc_image'] = self.image

        session.walk.update(session_data)

    def get_session_data(self):
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

    def get_image(self):
        '''
        Get the image to present as a depiction of the npc.
        '''

        db = current.db

        image = IMG(_src=URL('default', 'download', args=self.npc.image))

        return image


class Counter(object):
    '''This class is deprecated'''

    def __init__(self):
        '''include this question in the count for this quiz, send to 'end'
        if quiz is finished'''

    def check(self):
        #current object must be accessed at runtime
        session, request = current.session, current.request

        if session.q_counter:
            if int(session.q_counter) >= int(session.path_length):
                session.q_counter = 0
                redirect(URL('index', args=['end']))
                return dict(end="yes")
            else:
                session.q_counter += 1
        else:
            session.q_counter = 1

    def set(self):
        pass

    def clear(self):
        pass


class Location(object):
    '''
    This class finds and returns information on the student's current
    'location' within the town, based on the url variable 'loc' which
    is accessed via the web2py request object.

    implemented in:
    controllers/exploring.walk()
    '''

    def __init__(self, alias):

        db = current.db

        self.location = db(db.locations.alias == alias).select().first()
        self.image = IMG(
            _src=URL('default', 'download', args=self.location.background)
        )

    def info(self):
        '''
        Determine what location has just been entered and retrieve its
        details from db. Returns a dictionary with the keys 'id', 'alias',
        and 'img'.
        '''

        info = {
            'id': self.location.id,
            'alias': self.location.alias,
            'img': self.image
        }

        return info

    def active_paths(self, walk):
        '''
        Check for an active path in this location and make sure
        it has another step to begin. If so return a dict containing the
        id for the path ('path') and the step ('step').
        '''
        session, db = current.session, current.db

        if walk.active_paths:
            active_paths = db(db.paths.id.belongs(walk.active_paths.keys())).select()
            active_here = active_paths.find(lambda row: self.location.id in row.locations)
            # TODO: Do we need this - shouldn't a path be moved from active_paths to completed_paths when it's ended?
            if walk.completed_paths:
                active_paths.exclude(lambda row: row.id in walk.completed_paths)

            if len(active_paths):
                for path in active_here:
                    last = walk.active_paths[path.id]

                    try:
                        step_index = path.steps.index(last)

                    # If impossible step id is given in active_paths
                    except ValueError, err:
                        # Remove this path from active paths
                        del walk.active_paths[path.id]
                        walk.save_session_data()

                        # Set the log for this attempt as if path completed
                        self.log_attempt(path.id, 0, 1)
                        # TODO: Log error instead/as well
                        print err
                        continue

                    # If the last completed step was not the final in the path
                    if len(path.steps) > (step_index + 1):
                        step_id = path.steps[step_index + 1]

                        # Set session flag for this active path
                        walk.active_paths[path.id] = step_id
                        walk.save_session_data()

                        # Update attempt log
                        self.log_attempt(path.id, step_id, 1)

                        return dict(path=path, step=step_id)

                    # If the last step in the path has already been completed
                    else:
                        del walk.active_paths[path.id]
                        walk.completed_paths.add(path.id)
                        walk.save_session_data()

                        continue

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
                           cache=(cache.ram, 60*60)).as_list()


