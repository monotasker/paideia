from gluon import current, URL, redirect, IMG, SQLFORM, SPAN, Field
from gluon import IS_NOT_EMPTY
import datetime, random


class tag:

    def __init__(self):
        """
        set the path a student is exploring, retrieve its data, and store
        the data in the session object
        """

    def introduce_tags(self):
        """
        checks the user's performance and, if appropriate, introduces one or
        more new tags to the active set for selecting paths

        this method is called by categorize_tags if no tags are categorized
        1 (needing immediate review).
        """
        new_tag = ''
        #TODO: add logic to introduce new tag, based on student's current
        #position in the tag progression (tags.position)

        return new_tag

    def categorize_tags(self):
        """
        use stored statistics for current user to categorize the grammatical
        tags based on the user's success and the time since the user last
        used the tag.

        The categories range from 1 (need immediate review) to 4 (no review
        needed).

        this method is called at the start of each user session so that
        time-based statistics can be updated.
        """
        #TODO: Factor in how many times a tag has been successful or not
        print 'calling paideia_path.categorize_tags'
        # retrieve db at runtime from the current object
        db, auth = current.db, current.auth
        # query the db table for performance records
        record_list = db(db.tag_records.name == auth.user_id).select()
        # create new dictionary to hold categorized results
        cat = {1:[], 2:[], 3:[], 4:[]}
        for r in record_list:
            indx = r.tag
            #get success statistics for this tag
            timesR = r.times_right or 0
            timesW = r.times_wrong or 0
            #get time-based statistics for this tag
            #note: the arithmetic operations yield datetime.timedelta objects
            now_date = datetime.datetime.utcnow()
            right_dur = now_date - r.tlast_right
            wrong_dur = now_date - r.tlast_wrong
            rightWrong_dur = r.tlast_right - r.tlast_wrong
            #categorize q or tag based on this performance
            if right_dur < rightWrong_dur:          
                if rightWrong_dur.days >= 7:
                    if rightWrong_dur.days > 30:
                        if rightWrong_dur > datetime.timedelta(days=180):
                        #not due, but not attempted for 6 months
                            c = 1
                        else:
                            c = 4 #not due, delta more than a month
                    else:
                        c = 3 #not due, delta between a week and a month 
                else:
                    c = 2 # not due but delta is a week or less
            else:
                c = 1 # spaced repitition requires review
            cat[c].append(indx)

        if len(cat[1]) < 1:
            #if there are no tags needing immediate review, introduce new one
            self.introduce_tags()

        return cat

class path:
    """
    set the path a student is exploring, retrieve its data, and store 
    the data in the session object

    session:
    session.location
    session.active_paths
    session.completed_paths
    session.tagset
    session.npc
    """

    def __init__(self):

        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

    def find_unfinished(self):
        """
        Check for any paths that have been started but not finished by the
        current user.
        """
        auth, db = current.auth, current.db
        unfinished = [l.path for l in db(
                                    (db.path_log.name == auth.user_id) & 
                                    (db.path_log.last_step != 0)).select()]
        print 'found unfinished step from last time: ', unfinished
        return unfinished

    def check(self):
        """
        Find out whether to introduce another step, free the user for 
        movement, or continue with the current step.
        """

        #current object must be accessed at runtime
        session, request = current.session, current.request
        auth, db = current.auth, current.db

        #has the user completed enough paths for today?
        if session.completed_paths:
            todays = len(session.completed_paths)
            rsetting = db(db.app_settings.id == 1).select().first()
            required = rsetting.paths_per_day
            if todays >= required:
                return ['done']

        #is there any blocking state in effect?
        if session.block:
            return ['blocked']

        #check to see whether there are any paths active for this location
        if session.active_paths:
            #find list of active paths
            active = session.active_paths
            #TODO: find out last completed step in path

            #find current location
            loc = request.vars[loc]

            for p in active:
                #find the next incomplete step in the active path
                steps = db((db.paths.steps == db.steps.id) & 
                    (db.paths.id == p)).select()
                #check to see whether the step can be 
                #completed in this location

        #if not, check to see whether max number of tags are active
        #(or should this be blocking condition?)
        
        #otherwise, choose a new path
        else:
            self.pick()
            return('new')

    def pick(self):
        """Choose a new path for the user, based on tag performance"""
        request, session = current.request, current.session
        db, auth = current.db, current.auth

        print '\ncalling modules/paideia_path.pick()'
        
        #find out what location has been entered
        if 'loc' in request.vars:
            curr_loc = db(db.locations.alias == request.vars['loc']
                          ).select().first()
            session.location = curr_loc.id
        else:
            curr_loc = session.location
        print 'current location: ', curr_loc.alias, curr_loc.id

        #check to see whether any constraints are in place 
        if 'blocks' in session:
            print 'active block conditions: ', session.blocks
            #TODO: Add logic here to handle blocking conditions
        else:
            print 'no blocking conditions'
        
        #find out what paths (if any) are currently active
        a_paths = {} #session.active_paths or None
        print 'active paths: ', a_paths

        #if an active path has a step here, initiate that step
        if a_paths:
            activepaths = db(db.paths.id.belongs(a_paths.keys())).select()
            activehere = activepaths.find(lambda row: 
                                           curr_loc.id in row.locations)
            if 'completed_paths' in session and \
                    session.completed_paths is not None:
                activepaths.exclude(lambda row: 
                                    row.id in session.completed_paths) 

            if len(activepaths.as_list()) > 0:
                the_path = activehere[0]
                print 'active path in this location: ', the_path.id
                pathsteps = the_path.steps
                laststep = a_paths[the_path.id]
                print 'last step finished in this path: ', laststep
                stepindex = pathsteps.index(laststep)
                #if the last completed step was not the final in the path
                if len(pathsteps) > (stepindex + 1):
                    the_stepid = pathsteps[stepindex + 1]
                    print 'next step in this path: ', the_stepid
                    #set session flag for this active path
                    self.update_session('active_paths', 
                                        (the_path.id, the_stepid), 'ins')
                    #update attempt log 
                    self.log_attempt(the_path.id, the_stepid, 1)
                    return dict(path = the_path, step = the_stepid)
                #if the last step in the path has already been completed
                else:
                    print 'there are no more steps to complete in this path'
                    # why isn't this finding anything in active_paths to remove?
                    self.update_session('active_paths', the_path.id, 'del')
                    self.update_session('completed_paths', the_path.id, 'ins')


        #if no active path here . . .
        print 'no active paths here'
        #choose a new one
        cat = self.path_switch()
        p = self.find_paths(cat, curr_loc)
        category = p['c']
        paths = p['catXpaths']
        path_count = len(paths.as_list())
        print 'selected ', path_count, ' paths from category ', \
            category, ': \n\n', paths
        the_path = paths[random.randrange(0,path_count)]
        print 'activating path: ', the_path.id
        the_stepid = the_path.steps[0]
        print 'activating step: ', the_stepid     

        #set session flag showing that this path is now active
        self.update_session('active_paths', (the_path.id, the_stepid), 'ins')
        #log this attempt of the step
        self.log_attempt(the_path.id, the_stepid, 0)

        return dict(path = the_path, step = the_stepid)

    def path_switch(self):
        """
        choose one of four categories with a random factor but a heavy 
        weighting toward category 1
        """
        switch = random.randrange(1,101)
        print 'the switch is ', switch
        if switch in range(1,75):
            cat = 1
        elif switch in range(75,90):
            cat = 2
        elif switch in range(90,98):
            cat = 3
        else:
            cat = 4
        return cat

    def clear_session(self, session_vars):
        session = current.session

        if type(session_vars) is not list:
            session_vars = list(session_vars)
        if session_vars == 'all':
            session_vars = ['active_paths', 'answer', 'answer2', 'answer3', 
            'blocks', 'completed_paths', 'debug', 'last_query', 'path_freq', 
            'eval', 'path_freq', 'path_id', 'path_length', 'path_name', 
            'path_tags', 'qID', 'q_counter', 'question_text', 'quiz_type', 
            'readable_answer', 'response', 'tagset']
        for s in session_vars:
            if s in session:
                session[s] = None

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

    def log_attempt(self, pathid, stepid, update_switch):
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

    def find_paths(self, cat, curr_loc):
        """
        Find paths for this location that are due in the specified category 
        (in argument 'cat') and filter out paths that have been completed already
        today. If no tags in that category, move on to the next.
        """
        print '\ncalling modules/paideia_path.find_paths()'
        db, session = current.db, current.session

        #start with the category of tags, but loop through the categories
        #until some available paths are found
        cats = [1,2,3,4]
        for c in cats[cats.index(cat):] + cats[:cats.index(cat)]:
            #if any tags in this category, look for paths with these tags
            #that can be started in this location.
            paths = db(db.paths.id > 0).select()
            if len(session.tagset[c]) > 0:
                catXtags = session.tagset[c]
                print len(catXtags), ' active tags in category ', c
                catXpaths = paths.find(lambda row: 
                                (set(row.tags).intersection(set(catXtags)))
                                and (curr_loc.id in row.locations))
                print 'raw catXpaths = ', catXpaths
                """
                TODO: see whether the virtual fields approach above is slower 
                than some version of query approach below

                catXpaths = db((db.paths.tags.contains(catXtags))
                                & (db.paths.locations.contains(curr_loc.id))
                            ).select()
                """
                #filter out any of these completed already today
                if ('completed_paths' in session) and \
                        (session.completed_paths is not None):
                    comp = session.completed_paths
                    catXpaths = catXpaths.exclude(lambda row: 
                        row.id in comp)
                    print 'filtered out paths done today'
                    print catXpaths
                catXsize = len(catXpaths.as_list())
                print catXsize, ' paths not completed today in category ', c
                if catXsize < 1:
                    continue
                else:
                    break
            else:
                print 'no active tags in category ', c
                continue
        #TODO: work in a fallback in case no categories return any possible
        #paths
        return dict(catXpaths = catXpaths, c = c)

    def end(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

        pass

class step:

    def __init__(self, sid):
        db = current.db

        print '\ncreating instance of step class'
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

        nrows = db((db.npcs.id > 0)
                        & (db.npcs.location.contains(session.location))
                    ).select()

        ns_here = [n.id for n in nrows]
        print 'npcs in this location: ', ns_here
        if len(ns_here) > 1:
            nrow = nrows[random.randrange(1,len(ns_here)) - 1]
        else:
            nrow = nrows[ns_here[0]]
        print 'selected npc: ', nrow.id
        #store the id of the active npc as a session variable
        session.npc = nrow.id
        self.n = nrow
        return nrow

    def img(self):
        db = current.db

        n_img = IMG(_src=URL('default', 'download', 
                        args=db.npcs[self.n.id].image))
        return n_img

    def prompt(self):
        prompt = SPAN(self.s.prompt)
        return prompt

    def responder(self):
        """
        create and return the form to receive user response for this 
        step
        """
        session, request = current.session, current.request

        form = SQLFORM.factory(
        Field('response', 'string', requires=IS_NOT_EMPTY()))
        if form.accepts(request.vars,  session):
            session.response = request.vars.response
            redirect(URL('index', args=['response']))

        return form

class counter:

    def __init__(self):
        """include this question in the count for this quiz, send to 'end' if quiz is finished"""

    def check(self):
        #current object must be accessed at runtime, so can't be global variable
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

class map:
    """returns information needed to present the navigation map"""

    def __init__(self):

        #current object must be accessed at runtime, so can't be global variable
        db = current.db

        #prepare map interface for user to select a place to go
        self.locs = db().select(db.locations.ALL, orderby=db.locations.location)
        self.image = '/paideia/static/images/town_map.svg'