from gluon import current, URL, redirect
import datetime, random


class paideia_tag:

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

class paideia_path:

    def __init__(self):
        """
        set the path a student is exploring, retrieve its data, and store 
        the data in the session object
        """

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
                steps = db((db.paths.steps == db.steps.id) & (db.paths.id == p)).select()
                #check to see whether the step can be completed in this location

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
        curr_loc = db(db.locations.alias == request.vars['loc']).select().first()
        print 'current location: ', curr_loc.alias, curr_loc.id

        #check to see whether any constraints are in place 
        if 'blocks' in session:
            print 'active block conditions: ', session.blocks
            #TODO: Add logic here to handle blocking conditions
        else:
            print 'no blocking conditions'
        
        #find out what paths (if any) are currently active
        a_paths = session.active_paths or None
        print 'active paths: ', a_paths

        #if an active path has a step here, initiate that step
        #TODO: add tests to see whether active is actually here and 
        # to see whether last completed step was last in the path. 
        if a_paths:
            activepaths = db(db.paths.id.belongs(a_paths.keys())).select()
            activehere = activepaths.find(lambda row: 
                                          curr_loc.id in row.locations)
            the_path = activehere[0]
            print 'active path in this location: ', the_path.id
            pathsteps = the_path.steps
            laststep = a_paths[the_path.id]
            print 'last step finished in this path: ', laststep
            stepindex = pathsteps.index(laststep)
            the_stepid = pathsteps[stepindex + 1]
            print 'next step in this path: ', the_stepid
            session.active_paths[the_path.id] = the_stepid

            return dict(path = the_path, step = the_stepid)
        #if no active path here . . .
        print 'no active paths here'
        print 'selecting new path . . .'
        #choose category for path randomly but with weighting
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
        #find a new path to begin, starting with selected category
        p = self.find_paths(cat, curr_loc)
        category = p['c']
        paths = p['catXpaths']
        path_count = len(paths.as_list())
        print 'selected ', path_count, ' paths from category ', \
            category, ': \n\n', paths
        the_path = paths[random.randrange(1,path_count+1)]
        print 'activating path: ', the_path.id
        the_stepid = the_path.steps[0]
        print 'activating step: ', the_stepid     
        #set session flag showing that this path is now active
        if session.active_paths:
            session.active_paths[the_path.id] = the_stepid
        else:
            session.active_paths = {the_path.id:the_stepid}
        #log this attempt of the step
        self.log_attempt(the_path.id, the_stepid, 0)

        return dict(path = the_path, step = the_stepid)


    def log_attempt(self, pathid, stepid, update_switch):
        if update_switch == 1:
            logs = db(db.path_log.path == pathid).select()
            logdate = max(l.dt_started for l in logs)
            log = logs.find(lambda row: row.datetime == logdate).first()
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
                """
                TODO: see whether the virtual fields approach above is slower 
                than some version of query approach below

                catXpaths = db((db.paths.tags.contains(catXtags))
                                & (db.paths.locations.contains(curr_loc.id))
                            ).select()
                """
                #filter out any of these completed already today
                if session.completed_paths:
                    comp = session.completed_paths
                    catXpaths = catXpaths.exclude(lambda row: row.id in comp)        
                    print 'filtered out paths done today'
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

    def set(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

        if not session.path_length:
            the_path = db(db.quizzes.id == request.vars.path).select()
            session.path_id = the_path[0].id
            session.path_length = the_path[0].length
            session.path_name = the_path[0].quiz
            session.path_freq = the_path[0].frequency
            session.path_tags = the_path[0].tags

    def end(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

        pass

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

    def __init__(self):

        #current object must be accessed at runtime, so can't be global variable
        db = current.db

        #prepare map interface for user to select a place to go
        self.locs = db().select(db.locations.ALL, orderby=db.locations.location)
        self.image = '/paideia/static/images/town_map.svg'