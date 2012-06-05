# coding: utf8
from gluon import current, URL, redirect, IMG, SQLFORM, SPAN, Field, INPUT, A
from gluon import IS_NOT_EMPTY, IS_IN_SET
import datetime, random, pprint, re, string


### Utility functions

def get_locations():
    '''
    Return all locations in the game.
    '''

    db = current.db
    cache = current.cache

    # TODO: Review cache time
    return db().select(db.locations.ALL,
                       orderby=db.locations.location,
                       cache=(cache.ram, 60*60))

def get_paths():
    '''
    Return all paths in the game.
    '''

    db = current.db
    cache = current.cache

    # TODO: Review cache time
    return db().select(db.paths.ALL,
                       orderby=db.paths.id,
                       cache=(cache.ram, 60*60))

### End utility functions

# TODO: Deprecate eventually
class Utils(object):
    """
    Miscellaneous utility functions, gathered in a class for convenience.
    """

    def clear_session(self):
        session, response = current.session, current.response

        print '\ncalling path.clear_session()'

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
        print 'clearing session vars: ', session_vars

        for s in session_vars:
            if s in session:
                del session[s]
        print 'cleared session.', s

        print pprint.pprint(session)

    def update_session(self, session_index, val, switch):
        """insert, update, or delete property of the session object"""
        session = current.session

        print '\ncalling modules/paideia_path.update_session()'
        print 'val = ', val
        if switch == 'del':
            if type(val) == tuple:
                val = val[0]
            if session_index in session and val in session[session_index]:
                del session[session_index][val]
                print 'removing session.', session_index, '[', val, ']'
            print 'nothing to remove'
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
            print 'session.', session_index, ': ', session[session_index]


class Walk(object):
    """
    A class handling the "movement" of a user from one path or step to the
    next (i.e., transitions between states outside a single step). In other
    words, this class prepares path-related information needed immediately
    before path selection.
    """

    def __init__(self, user):

        self.map = Map()
        self.active_location = None
        self.path = None
        self.active_paths = None
        self.completed_paths = None
        self.step = None
        self.tag_set = None
        self.user = user

    def _introduce(self):
        """
        This method checks the user's performance and, if appropriate,
        introduces one or more new tags to the active set for selecting paths.
        This method is intended as private, to be called by categorize()
        if that method yields an initial result with no tags in category 1
        (needing immediate review).

        :param cat:dict()

        JEFF: By convention, private methods in Python are prefixed with an underscore
              (see http://docs.python.org/tutorial/classes.html#private-variables)
        """

        db = current.db

        tag_progress = db(db.tag_progress.name == self.user.id).select().first()
        # TODO: Check we aren't at the end
        if tag_progress:
            latest = tag_progress.latest_new + 1
        else:
            latest = 1

        db.tag_progress.update_or_insert(
            db.tag_progress.name == self.user.id,
            name=self.user.id,
            latest_new=latest
        )

        tags = [t for t in db(db.tags.position == latest).select()]

        return tags

    def categorize_tags(self):
        """
        This method uses stored statistics for current user to categorize the grammatical
        tags based on the user's success and the time since the user last
        used the tag.

        The categories range from 1 (need immediate review) to 4 (no review
        needed).

        this method is called at the start of each user session so that
        time-based statistics can be updated.


        """
        #TODO: Factor in how many times a tag has been successful or not
        print 'calling paideia_path.categorize_tags'
        db = current.db

        # create new dictionary to hold categorized results
        categories = dict((x, []) for x in xrange(1, 5))

        record_list = db(db.tag_records.name == self.user.id).select()

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
            categories[category].append(record.tag)

        # If there are no tags needing immediate review, introduce new one
        if not categories[1]:
            categories[1] = self._introduce()

        self.tag_set = categories

    def unfinished(self):
        """
        This public method checks for any paths that have been started but not
        finished by the current user. It expects finished paths to have a
        'last_step' value of 0 in its most recent entry in the db table
        path_log.

        implemented by:

        """

        db = current.db

        print '\ncalling walk.unfinished()'
        path_logs = db(
            (db.path_log.name == self.user.id) &
            (db.path_log.last_step != 0)
        ).select()

        # Get only most recent log for each unique path
        self.active_paths = {}
        for path in set(log.path for log in path_logs):
            log = max((p.dt_started, p) for p in path_logs if p.path == path)[1]
            self.active_paths[path] = log.last_step

    def pick_path(self, location):
        """Choose a new path for the user, based on tag performance"""

        print '\ncalling Path.pick()'

        # check for active blocking conditions
        # TODO: Implement logic to do something with True result here
        if self.get_blocks():
            print 'block in place'

        # if possible, continue an active path whose next step is here
        active_paths = location.active_paths(self)
        if not active_paths:
            print 'no active paths here'
        else:
            return active_paths

        #otherwise choose a new path
        db = current.db

        category = self.get_category()
        paths, category = self.find_paths(category, location, get_paths())

        try:
            path_count = len(paths)
        except TypeError:
            path_count = 0

        if not path_count:
            print 'no available paths, so reviewing some already completed today'
            self.completed_paths = None
            # TODO: Fix this - I'm not sure what happens if active_location is None...
            paths, category = self.find_paths(category, self.active_location, get_paths())
        else:
            print 'selected ', path_count, ' paths from category ', \
                category, ': \n\n', paths

        path = paths[random.randrange(0, path_count)]

        print 'activating path: ', path.id
        print 'activating path: ', type(path)
        step_id = path.steps[0]
        print 'activating step: ', step_id
        print 'activating step: ', type(step_id)

        #set session flag showing that this path is now active
        self.path = path#.id
        self.step = Step(step_id)

        #log this attempt of the step
        self.log(path.id, step_id, 0)

#        return dict(path = path, step = the_stepid)

    def get_category(self):
        """
        choose one of four categories with a random factor but a heavy
        weighting toward category 1
        """
        switch = random.randrange(1,101)
        print 'the switch is ', switch
        if switch in range(1,75):
            category = 1
        elif switch in range(75,90):
            category = 2
        elif switch in range(90,98):
            category = 3
        else:
            category = 4
        return category

    def find_paths(self, cat, location, paths):
        """
        Find paths for this location that are due in the specified category
        (in argument 'cat') and filter out paths that have been completed
        already today. If no tags in that category, move on to the next.
        """
        print '\ncalling modules/paideia_path.find_paths()'

        #start with the category of tags, but loop through the categories
        #until some available paths are found
        categories = [1, 2, 3, 4]
        index = categories.index(cat)
        category_paths = None
        for category in categories[index:] + categories[:index]:
            #if any tags in this category, look for paths with these tags
            #that can be started in this location.
            tags = set(t.id for t in self.tag_set[category])
            if len(tags) > 0:
                print len(tags), 'active tags in category', category
                category_paths = paths.find(lambda row: (
                    set(t for t in row['tags']).intersection(tags) and
                    (location.location.id in row['locations'])
                ))
                print 'raw category_paths = ', category_paths
                """
                TODO: see whether the virtual fields approach above is slower
                than some version of query approach below

                catXpaths = db((db.paths.tags.contains(tags))
                                & (db.paths.locations.contains(curr_loc.id))
                            ).select()
                """
                #filter out any of these completed already today
                if self.completed_paths is not None:
                    print 'completed paths: ', self.completed_paths
                    category_paths = category_paths.find(
                        lambda row: row.id not in self.completed_paths
                    )
                    print 'filtered out paths done today'
                    print category_paths
                category_size = len(category_paths)
                print category_size, ' paths not completed today in category ', category
                if category_size:
                    break
            else:
                print 'no active tags in category ', category
                continue
        #TODO: work in a fallback in case no categories return any possible
        #paths (do this in pick_path?)
        return (category_paths, category)

    def get_blocks(self):
        """
        Find out whether any blocking conditions are in place and trigger
        appropriate responses.
        """
        #current object must be accessed at runtime
        session = current.session

        #check to see whether any constraints are in place
        if 'blocks' in session:
            print 'active block conditions: ', session.blocks
            #TODO: Add logic here to handle blocking conditions
            #TODO: First priority is to add a blocking condition should be a
            #when the user has been presented with the prompt for a step but
            #has not submitted any response for processing. The blocking
            #condition should force the user either to return to the step
            #prompt or to submit a bug report.
            return True
        else:
            print 'no blocking conditions'
            return False

    def log(self, pathid, stepid, update_switch):
        """either create or update entries in the attempt_log table"""
        print '\ncalling modules/paideia_path.log_attempt()'
        db = current.db

        if update_switch == 1:
            logs = db(db.path_log.path == pathid).select()
            logdate = max(l.dt_started for l in logs)
            log = logs.find(lambda row: row.dt_started == logdate).first()
            log.update_record(last_step = stepid)
        else:
            db.path_log.insert(path = pathid, last_step = stepid)
        db.attempt_log.insert(step = stepid)

# TODO: Deprecate eventually
class Path(object):
    """
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
    """

    def __init__(self, loc):
        self.loc = loc

    def end(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request
        auth, db = current.auth, current.db

        pass


class Step(object):

    def __init__(self, sid):
        db, session = current.db, current.session

        print '\ncreating instance of step class'
        self.pid = session.walk.path
        self.sid = sid
        self.s = db.steps[sid]
        self.ns = None
        self.n = None

    def ask(self):
        """Public method. Returns the html helpers to create the view
        for the 'ask' state of the user interface."""
        print '\ncalling ask() method of step class'
        self.n = self.npc()
        print self.n
        img = self.img()
        print img
        prompt = self.prompt()
        print prompt
        responder = self.responder()

        return dict(npc_img = img, prompt = prompt, responder = responder)

    def npc(self):
        """Given a set of npcs for this step (in self.ns) select one of
        the npcs at random, store the id in a session variable, and return
        the corresponding db row object"""
        db, session = current.db, current.session
        print '\ncalling npc() method of step class'
        if session.walk.active_location is None:
            return   # TODO: return what?
        nrows = db((db.npcs.id > 0)
                        & (db.npcs.location.contains(session.walk.active_location.location.id))
                    ).select()
        nrows = nrows.exclude(lambda row: row.id in self.s.npcs)
        ns_here = [n.id for n in nrows]
        print 'npcs in this location: ', ns_here
        if len(ns_here) > 1:
            nrow = nrows[random.randrange(1,len(ns_here)) - 1]
        else:
            nrow = nrows.find(lambda row: row.id in ns_here)[0]
        print 'selected npc: ', nrow.id
        #store the id of the active npc as a session variable
        session.npc = nrow.id
        self.n = nrow
        return nrow

    def img(self):
        """Get the image to present as a depiction of the current npc"""
        db, session = current.db, current.session

        n_img = IMG(_src=URL('default', 'download',
                        args=db.npcs[self.n.id].image))
        session.image = n_img
        return n_img


    def process(self):
        """
        handles the user's response to the step prompt. In this base 'step'
        class this involves comparing the user's typed response with the
        regular expressions provided for the step. The evaluation is then
        logged and stored in the db, and the appropriate information
        presented to the user.
        """
        session, db, auth = current.session, current.db, current.auth

        print '\ncalling process() method of step class'
        # get the student's response to the question
        r = string.strip(session.response)
        # get the correct answer information from db
        print self.s
        answer = self.s.response1
        answer2 = self.s.response2
        answer3 = self.s.response3
        readable = self.s.readable_response

        # compare the student's response to the regular expressions
        try:
            if re.match(answer, r, re.I):
                score = 1
                reply = "Right. Κάλη."
            elif re.match(answer2, r, re.I) and answer2 != 'null':
                score = 0.5
                #TODO: Get this score value from the db instead of hard coding it here.
                reply = "Οὐ κάκος. You're close."
                #TODO: Vary the replies
            elif re.match(answer3, r, re.I) and answer3 != 'null':
                #TODO: Get this score value from the db instead of hard coding it here.
                score = 0.3
            else:
                score = 0
                reply = "Incorrect. Try again!"
            # set the increment value for times wrong, depending on score
            if score < 1: nscore = 1
            else: nscore = 0
            # record the results in statistics for this step and this tag
            self.record(score, nscore)

        #handle errors if the student's response cannot be evaluated
        except re.error:
            redirect(URL('index', args=['error', 'regex']))

        img = session.image

        return dict(reply=reply, readable=readable, npc_img = img)

    def record(self, score, nscore):
        """Record the results of this step in db tables attempt_log and
        tag_records. score gives the increment to add to 'times right' in
        records. nscore gives the opposite value to add to 'times wrong'
        (i.e., negative score)."""
        db, auth = current.db, current.auth
        utcnow = datetime.datetime.utcnow()
        print '\ncalling step.record()'

        #log this step attempt
        db.attempt_log.insert(step=self.sid, score=score, path=self.pid)
        print 'recorded in db.attempt_log:'
        print db(db.attempt_log.id > 0).select().last()

        #log this tag attempt for each tag in the step
        trows = db(db.tag_records.id > 0).select()
        #calculate record info
        for t in self.s.tags:
            lr = utcnow
            lw = utcnow
            # try to update an existing record for this tag
            try:
                trow = trows.find(lambda row: (row.tag == t) &
                                            (row.name == auth.user_id)).first()
                if score == 1:
                    lw = trow.tlast_wrong
                elif score == 0:
                    lr = trow.tlast_right
                    lw = utcnow
                else:
                    score = 0
                    lw = utcnow
                    lr = utcnow
                tr = trow.times_right + score
                tw = trow.times_wrong + nscore
                trow.update_record(tlast_right = lr, tlast_wrong = lw,
                                        times_right = tr, times_wrong = tw,
                                        path = self.pid)
                print 'updating existing tag record for ', trow.tag
            # if none exists, insert a new one
            except AttributeError:
                db.tag_records.insert(tag = t,
                                        times_right = score,
                                        times_wrong = nscore,
                                        path = self.pid)
                print 'inserting new tag record for ', t
            # print any other error that is thrown
            except Exception, err:
                print 'unidentified error:'
                print type(err)
                print err

        #TODO: update the path log for this attempt
        #TODO: check to see whether this is the last step in the path and if so
        #remove from active_paths and add to completed_paths

    def prompt(self):
        """Get the prompt text to be presented from the npc to start the
        step interaction"""
        prompt = SPAN(self.s.prompt)
        #TODO: get audio file for prompt text as well.
        return prompt

    def responder(self):
        """
        create and return the form to receive the user's response for this
        step
        """
        session, request = current.session, current.request

        form = SQLFORM.factory(
                   Field('response', 'string', requires=IS_NOT_EMPTY()))
        if form.process().accepted:
            session.response = request.vars.response

        return form


class StepMultipleChoice(Step):
    def responder(self):
        """
        create and return the form to receive the user's response for this
        step
        """
        session, request = current.session, current.request

        vals = self.s.options
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
    """A step type that does not require significant user response. Useful for
    giving the user information and then freeing her/him up to perform a task.
    """

    def responder(self):
        pass

    def process(self):
        pass


class Npc(object):

    def __init__(self):
        pass

    def pick(self):
        """Given a set of npcs for this step (in self.ns) select one of
        the npcs at random, store the id in a session variable, and return
        the corresponding db row object"""
        db, session = current.db, current.session
        print '\ncalling npc() method of step class'

        nrows = db((db.npcs.id > 0)
                        & (db.npcs.location.contains(session.location))
                    ).select()
        nrows = nrows.exclude(lambda row: row.id in self.s.npcs)
        ns_here = [n.id for n in nrows]
        print 'npcs in this location: ', ns_here
        if len(ns_here) > 1:
            nrow = nrows[random.randrange(1,len(ns_here)) - 1]
        else:
            nrow = nrows.find(lambda row: row.id in ns_here)[0]
        print 'selected npc: ', nrow.id
        #store the id of the active npc as a session variable
        session.npc = nrow.id
        self.n = nrow
        return nrow

    def img(self):
        """Get the image to present as a depiction of the current npc"""
        db, session = current.db, current.session

        n_img = IMG(_src=URL('default', 'download',
                        args=db.npcs[self.n.id].image))
        session.image = n_img
        return n_img


class Counter(object):
    """This class is deprecated"""

    def __init__(self):
        """include this question in the count for this quiz, send to 'end'
        if quiz is finished"""

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
    """
    This class finds and returns information on the student's current
    'location' within the town, based on the url variable 'loc' which
    is accessed via the web2py request object.

    implemented in:
    controllers/exploring.walk()
    """
    def __init__(self, location, image):

        self.location = location
        self.image = image

    def info(self):
        """
        Determine what location has just been entered and retrieve its
        details from db. Returns a dictionary with the keys 'id', 'alias',
        and 'img'.
        """

        info = {
            'id': self.location.id,
            'alias': self.location.alias,
            'img': self.image
        }

        return info

    def active_paths(self, walk):
        """
        check for an active path in this location and make sure
        it has another step to begin. If so return a dict containing the
        id for the path ('path') and the step ('step'). If not return False.
        """
        session, db = current.session, current.db

        if walk.active_paths:
            active_paths = db(db.paths.id.belongs(walk.active_paths.keys())).select()
            active_here = active_paths.find(lambda row:
                                           self in row.locations)
            # TODO: Do we need this - shouldn't a path be moved from active_paths to completed_paths when it's ended?
            if walk.completed_paths:
                active_paths.exclude(lambda row: row.id in walk.completed_paths)

            if len(active_paths):
                for path in active_here:
                    print 'active path in this location: ', path.id
                    psteps = path.steps
                    last = walk.active_paths[path.id]
                    print 'last step finished in this path: ', last
                    try: sindex = psteps.index(last)
                    #if impossible step id is given in active_paths
                    except ValueError, err:
                        #remove this path from active paths
                        self.update_session('active_paths',
                                            (path.id, 0), 'del')
                        #set the log for this attempt as if path completed
                        self.log_attempt(path.id, 0, 1)
                        print err
                        continue

                    #if the last completed step was not the final in the path
                    if len(psteps) > (sindex + 1):
                        sid = psteps[sindex + 1]
                        print 'next step in this path: ', sid
                        #set session flag for this active path
                        self.update_session('active_paths', (path.id, sid), 'ins')
                        #update attempt log
                        self.log_attempt(path.id, sid, 1)
                        return dict(path = path, step = sid)

                    #if the last step in the path has already been completed
                    else:
                        print 'there are no more steps to complete in this path'
                        # why isn't this finding anything in active_paths to remove?
                        self.update_session('active_paths', path.id, 'del')
                        self.update_session('completed_paths', path.id, 'ins')
                        continue
                else:
                    return False
            else:
                return False
        else:
            return False


class Map(object):
    """This class returns information needed to present the navigation map"""

    def __init__(self):

        #current object must be accessed at runtime
        db = current.db

        #prepare map interface for user to select a place to go
        self.locations = get_locations()
        # TODO: Define this in a setting or somewhere
        self.image = '/paideia/static/images/town_map.svg'


