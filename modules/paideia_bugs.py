from gluon import current
from datetime import timedelta
import traceback


class Bug(object):
    """
    Handles the creation, manipulation, and reporting of bug
    reports for paideia.
    """
    def __init__(self, step_id=None, path_id=None, loc_id=None):
        """
        Initialize a Bug object for generating bug reports on specific user
        interactions.
        """
        self.step_id = step_id
        self.path_id = path_id
        self.loc_id = loc_id
        print 'bug.init: step_id is', self.step_id
        print 'bug.init: path_id is', self.path_id
        print 'bug.init: loc_id is', self.loc_id

    def log_new(self, answer, log_id, score):
        """
        creates a new bug report and provides confirmation to the user.
        """
        response = current.response
        db = current.db
        print 'in bug.log_new:'
        try:
            db.bugs.insert(step=self.step_id,
                           in_path=self.path_id,
                           map_location=self.loc_id,
                           user_response=answer,
                           log_id=log_id,
                           score=score)
            response.flash = 'Thanks for reporting this potential bug. We '\
                             'will look at the question to see what the '\
                             'problem was. If there turns out to be a '\
                             'problem with the question, this answer will '\
                             'be ignored as we track your learning. Check '\
                             'your profile page in the next few days to see '\
                             'the instructor\'s response to your bug report.'
            return True
        except Exception:
            print traceback.format_exc(5)
            mail = current.mail
            response.flash = 'Sorry, something went wrong with your bug' \
                             'report. An email including the details of ' \
                             'your response has been sent automatically to ' \
                             'the instructor.'
            msg = '<html>A user tried to submit a step bug report, but the' \
                  'report failed. The request data is:\n{}\nThe request' \
                  'data is: n/a</html>'
            mail.send(mail.settings.sender, 'bug reporting error', msg)
            # TODO: Log these errors.
            return False

    def undo(self, user_id, bug_id, log_id):
        '''
        Reverse the recorded effects of a single wrong answer for a given user.

        Intended to be run when an administrator or instructor sets a bug to
        'confirmed' or 'fixed'.
        '''
        db = current.db
        step_id = self.step_id

        bug_row = db.bugs(bug_id)

        # don't do anything if the original answer was counted as correct
        if bug_row.score == 1:
            return True

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
                elif lastr - bugdate >= timedelta(seconds=1):
                    pass
                else:
                    args['tlast_right'] = bugdate

                # revert the last wrong date
                lastw = trecord.tlast_wrong
                if lastw == bugdate:
                    pass
                elif lastw - bugdate >= timedelta(seconds=1):
                    pass
                else:
                    oldlogs = db((db.attempt_log.name == user_id) &
                                (db.attempt_log.step == step_id) &
                                (db.attempt_log.score < 1)
                                 ).select(orderby=~db.attempt_log.dt_attempted)
                    oldlogs = oldlogs.find(lambda row:
                            (bugdate - row.dt_attempted) >
                            timedelta(seconds=1))
                    prev_log = oldlogs.first()
                    args['tlast_wrong'] = prev_log.dt_attempted

                # revert counts for times right and wrong
                args['times_right'] = (trecord.times_right + 1)
                args['times_wrong'] = (trecord.times_wrong - 1)

                trecord.update_record(**args)

                return 'Bug {} reversed.'.format(bug_id)

        except Exception, e:
            print type(e), e
            return 'Bug {} could not be reversed.'.format(bug_id)

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
        bugs = db(bugs_q).select(orderby=~db.bugs.date_submitted)
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
