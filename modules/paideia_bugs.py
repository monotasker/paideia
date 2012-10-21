from gluon import current


class Bug(object):

    verbose = False

    """
    Handles the creation, manipulation, and reporting of bug
    reports for paideia.
    """
    def __init__(self, step=None, path=None, location=None):
        if self.verbose: print '\nInitializing Bug object ==================='
        debug = False
        session = current.session

        if (step is None) and (session.walk) and ('retry' in session.walk):
            path = session.walk['retry'][0]
            step = session.walk['retry'][1]
        elif (step is None) and (session.walk) and ('step' in session.walk):
            path = session.walk['path']
            step = session.walk['step']
        self.step = step
        self.path = path
        if (location is None) and (session.walk) and ('active_location'
                                                           in session.walk):
            location = session.walk['active_location']
        self.location = location
        if debug:
            print 'initial arguments:', self.step, self.path, self.location

        return

    def log_new(self, answer):
        """
        creates a new bug report and provides confirmation to the user.
        """
        if self.verbose: print 'calling Bug.log_new object ================='
        debug = False
        response = current.response
        db = current.db

        location = db(db.locations.alias ==
                                    self.location['alias']).select().first()
        if debug:
            print 'location =', self.location
            print 'step =', self.step
            print 'path =', self.path
            print 'answer =', answer

        try:
            db.bugs.insert(step=self.step, path=self.path,
                            location=location.id, user_response=answer)
            response.flash = 'Thanks for reporting this potential bug. We will\
                    look at the question to see what the problem was. If there\
                    turns out to be a problem with the question, this answer\
                    will be ignored as we track your learning. Check your\
                    profile page in the next few days to see the instructor\'s\
                    response to your bug report.'
            return True
        except Exception, e:
            response.flash = 'Sorry, something went wrong with your bug\
                    report. Please contact the instructor.'
            # TODO: Log these errors.
            print 'Error in Bug.log_new():', e
            return False

    # TODO: Deprecated in favour of plugin_listandedit
    #def updatebug(self):
        #"""
        #Provides form and page components to update an existing bug and
        #handles the form processing.
        #"""
        #request, db = current.request, current.db
        #crud = Crud(db)

        #edit_form = crud.update(db.bugs, request.args[0])
        #closer = A('close', _href=URL('#'), _class='close_link')
        #the_title = H3('Reviewing Bug Report for Question')

    def bugresponses(self, user):
        '''
        Returns a list of the bug reports submitted by 'user'. Each list item
        is itself a list containing the step prompt, user_response,
        date_submitted, bug_status, and admin_comment for an individual bug
        report.
        '''
        db = current.db
        debug = False

        bugs_q = (db.steps.id == db.bugs.step) & (db.bugs.user_name == user)
        bugs = db(bugs_q).select()
        if debug: print 'DEBUG: bugs.select() =', bugs
        lst = []
        for b in bugs:
            display = []
            display.append(b.steps.prompt)
            display.append(b.bugs.user_response)
            display.append(b.bugs.date_submitted)
            #get status label instead of raw status reference
            s = b.bugs.bug_status
            if s is None:
                s = 5
            st = db(db.bug_status.id == s).select().first()
            status = st.status_label
            display.append(status)
            display.append(b.bugs.admin_comment)
            lst.append(display)
        return lst
