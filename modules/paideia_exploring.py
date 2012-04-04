# coding: utf8
from gluon import current, URL, redirect, IMG, SQLFORM, SPAN, Field, INPUT, A
from gluon import IS_NOT_EMPTY, IS_IN_SET
import datetime, random, pprint, re, string


class Utils(object):
    """
    Miscellaneous utility functions, gathered in a class for convenience.
    """
    def __init__(self):
        pass

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
                session[s] = None
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


class Tag(object):

    def __init__(self, record_list):
        """
        :param record_list: rows (gluon.storage) object containing the db 
        records from tag_records table that belong to the current user.

        implemented in:
        controllers/index.py
        """
        self.record_list = record_list

    def introduce(self):
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

    def categorize(self):
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
        
        # create new dictionary to hold categorized results
        cat = {1:[], 2:[], 3:[], 4:[]}
        for r in self.record_list:
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

        return cat


class Walk(object):
    """
    A class handling the "movement" of a user from one path or step to the 
    next (i.e., transitions between states outside a single step).
    """

    def __init__(self):
        pass

    def unfinished(self):
        """
        Check for any paths that have been started but not finished by the
        current user. Expects finished paths to have a 'last_step' value of 0.
        """
        auth, db, session = current.auth, current.db, current.session

        print '\ncalling paideia_path.find_unfinished()'
        mylogs = db((db.path_log.name == auth.user_id) & 
                                    (db.path_log.last_step != 0)).select()
        unfinished = [l.path for l in mylogs]

        #get only most recent log for each unique path
        ukeys = {}
        for e in unfinished:
            newt = mylogs[e].dt_started
            if e in ukeys:
                if newt > ukeys[e]:
                    ukeys[e] = newt
                else:
                    pass
            else:
                ukeys[e] = newt

        #build dict with last completed step for each unique path
        adict = {}
        for u in ukeys:
            myrow = mylogs.find(lambda row: (row.id == u)).first()
            adict[u] = myrow.last_step
        print 'found ', len(adict.keys()), ' unfinished step from last time: '
        print adict

        #add unfinished to session.active_paths
        try: 
            for k, v in adict.items():
                session.active_paths[k] = v
        except Exception, err:
            print Exception, err

        return adict

    def blocks(self):
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
            #TODO: One blocking condition should be a started step that doesn't have a 
            #processed user response -- force either repeating of the step prompt or 
            #logging of an error report.
            return True
        else:
            print 'no blocking conditions'
            return False

    def active(self):
        """
        check for an active path in this location and make sure 
        it has another step to begin. If so return a dict containing the
        id for the path ('path') and the step ('step'). If not return False.
        """
        session, db = current.session, current.db

        a_paths = session.active_paths or None
        if a_paths:
            activepaths = db(db.paths.id.belongs(a_paths.keys())).select()
            activehere = activepaths.find(lambda row: 
                                           self.curr_loc in row.locations)
            if 'completed_paths' in session \
                    and session.completed_paths is not None:
                activepaths.exclude(lambda row: 
                                    row.id in session.completed_paths) 

            if len(activepaths.as_list()) > 0:
                for p in activehere:
                    print 'active path in this location: ', p.id
                    psteps = p.steps
                    last = a_paths[p.id]
                    print 'last step finished in this path: ', last
                    try: sindex = psteps.index(last)
                    #if impossible step id is given in active_paths
                    except ValueError, err: 
                        #remove this path from active paths
                        self.update_session('active_paths', 
                                            (p.id, 0), 'del')
                        #set the log for this attempt as if path completed
                        self.log_attempt(p.id, 0, 1)
                        print err
                        continue

                    #if the last completed step was not the final in the path
                    if len(psteps) > (sindex + 1):
                        sid = psteps[sindex + 1]
                        print 'next step in this path: ', sid
                        #set session flag for this active path
                        self.update_session('active_paths', (p.id, sid), 'ins')
                        #update attempt log 
                        self.log_attempt(p.id, sid, 1)
                        return dict(path = p, step = sid)

                    #if the last step in the path has already been completed
                    else:
                        print 'there are no more steps to complete in this path'
                        # why isn't this finding anything in active_paths to remove?
                        self.update_session('active_paths', p.id, 'del')
                        self.update_session('completed_paths', p.id, 'ins')
                        continue
                else:
                    return False
            else:
                return False
        else:
            return False

    def loc(self):
        """find out what location has been entered"""
        
        return Location()    


class Path(object):
    """
    set the path a student is exploring, retrieve its data, and store 
    the data in the session object

    ## session variables available:
    ### This first set is used to track information about a user's session that persists
    beyond a single step execution.

    session.location (list: id, alias)
    session.active_paths (dict: id:last active step)
    session.completed_paths (list: int for path id)
    session.tagset (dict: each of four categories is a key, list of tag 
        ids as its value)

    ### This second set should be used exclusively to preserve current data 
    during execution of a single step (i.e., retrieve the results of 
    path.pick() in step.process()). By the end of step.process() they 
    should be returned to a value of None:

    session.npc
    session.step (single int)
    session.path (single int)
    session.image
    """

    def __init__(self):
        self.curr_loc = None

    def pick(self):
        """Choose a new path for the user, based on tag performance"""
        request, session = current.request, current.session
        db, auth = current.db, current.auth

        print '\ncalling modules/paideia_path.pick()'
        # find current location in game world
        curr_loc = self.loc()
        # check for active blocking conditions
        # TODO: Implement logic to do something with True result here
        if self.blocks() == True:
            print 'block in place'
        # if possible, continue an active path whose next step is here
        a = self.active()
        if a == False:
            print 'no active paths here'
            pass
        else:
            return a                    
        #otherwise choose a new path
        cat = self.switch()
        p = self.find(cat, curr_loc)
        category = p['c']
        paths = p['catXpaths']
        path_count = len(paths.as_list())
        if path_count < 1:
            print 'no available paths, so reviewing some already completed today'
            session.completed = None
            p = self.find(cat, curr_loc)
            category = p['c']
            paths = p['catXpaths']
            path_count = len(paths.as_list())
        else:
            print 'selected ', path_count, ' paths from category ', \
                category, ': \n\n', paths
        the_path = paths[random.randrange(0,path_count)]
        print 'activating path: ', the_path.id
        the_stepid = the_path.steps[0]
        print 'activating step: ', the_stepid     

        #set session flag showing that this path is now active
        self.update_session('active_paths', (the_path.id, the_stepid), 'ins')
        session.path = the_path.id
        session.step = the_stepid
        #log this attempt of the step
        self.log_attempt(the_path.id, the_stepid, 0)

        return dict(path = the_path, step = the_stepid)

    def switch(self):
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

    def find(self, cat, curr_loc):
        """
        Find paths for this location that are due in the specified category 
        (in argument 'cat') and filter out paths that have been completed 
        already today. If no tags in that category, move on to the next.
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
                    print 'completed paths: ', comp
                    catXpaths = catXpaths.find(lambda row: 
                        row.id not in comp)
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
        session, request, auth, db = current.session, current.request
        auth, db = current.auth, current.db

        pass


class Step(object):

    def __init__(self, sid):
        db, session = current.db, current.session

        print '\ncreating instance of step class'
        self.pid = session.path
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


class StepEnd(Step):
    """A Step type that closes off a multi-step path."""
    def __init__(self):
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
    """docstring for Location"""
    def __init__(self, arg):
        pass

    def find(self):
        """Determine what location has just been entered and retrieve its 
        details from db"""
        request, session = current.request, current.session
        db = current.db

        if 'loc' in request.vars:
            curr_loc = db(db.locations.alias == request.vars['loc']
                          ).select().first()
            session.location = [curr_loc.id,curr_loc.alias]
            self.curr_loc = curr_loc.id
        else:
            curr_loc = db.locations[session.location]
            self.curr_loc = session.location
        print 'current location: ', curr_loc.alias, curr_loc.id    
        return curr_loc
        
    def img(self):
        pass


class Map(object):
    """returns information needed to present the navigation map"""

    def __init__(self):

        #current object must be accessed at runtime
        db = current.db

        #prepare map interface for user to select a place to go
        self.locs = db().select(db.locations.ALL, 
                                        orderby=db.locations.location)
        self.image = '/paideia/static/images/town_map.svg'