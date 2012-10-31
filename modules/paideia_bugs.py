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

    def log_new(self, answer, log_id, score, step=None, path=None):
        """
        creates a new bug report and provides confirmation to the user.
        """
        if self.verbose: print 'calling Bug.log_new object ================='
        debug = True
        response = current.response
        db = current.db
        if step == None:
            step = self.step
        if path == None:
            path = self.path

        location = db(db.locations.alias ==
                                    self.location['alias']).select().first()
        if debug:
            print 'score =', score
            print 'log_id =', log_id

        try:
            db.bugs.insert(step=step,
                            path=path,
                            location=location.id,
                            user_response=answer,
                            log_id=log_id,
                            score=score)
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

    def undo(self, user, bug_id, log_id, step=None, db=None):
        '''
        Reverse the recorded effects of a single wrong answer for a given user.

        Intended to be run when an administrator or instructor sets a bug to
        'confirmed' or 'fixed'.
        '''
        if db is None:
            db = current.db
        if step_id is None:
            step_id = self.step
        bug_row = db.bugs(bug_id)

        # don't do anything if the original answer was counted as correct
        if bug_row.score == 1:
            return

        try:
            # correct score in the attempt_log table
            log_row = db.attempt_log(log_id)
            log_row.update_record(score=1)

            # correct tag_records entry for each tag on the step
            step_id = bug_row.step
            tagset = db.steps(step_id).tags
            for tag in tagset:
                trecord = db((db.tag_records.tag == tag) &
                            (db.tag_records.name == user_id)).select().first()
                args = {}

                # revert the last right date
                bugdate = bug_row.date_submitted
                lastr = trecord.tlast_right
                if lastr == bugdate:
                    pass
                elif lastr - bugdate >= datetime.timedelta(seconds=1):
                    pass
                else:
                    args[tlast_right] = bugdate

                # revert the last wrong date
                lastw = trecord.tlast_wrong
                if lastw == bugdate:
                    pass
                elif lastw - bugdate >= datetime.timedelta(seconds=1):
                    pass
                else:
                    oldlogs = db((db.attempt_log.name == user) &
                                (db.attempt_log.step == step_id) &
                                (db.attempt_log.score < 1)
                                ).select(orderby=~db.attempt_log.dt_attempted)
                    oldlogs = oldlogs.find(lambda row:
                            (bugdate - row.dt_attempted) >
                            datetime.timedelta(seconds=1))
                    prev_log = oldlogs.first()
                    args[tlast_wrong] = prev_log.dt_attempted

                # revert counts for times right and wrong
                args[times_right] = (trecord.times_right + 1)
                args[times_wrong] = (trecord.times_wrong - 1)

                trecord.update_record(**args)
        except Exception, e:
            print type(e), e

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
