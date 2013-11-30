from gluon import current
#from datetime import timedelta
import traceback
from pprint import pprint


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
        db = current.db
        self.step_id = step_id
        self.path_id = path_id
        self.loc_id = loc_id
        if isinstance(loc_id, str):
            self.loc_id = db(db.locations.loc_alias == loc_id
                             ).select(db.locations.id).first()
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
                  'report failed. Traceback: {} \n\n' \
                  'The request data is:\n{}\n' \
                  '</html>'.format(traceback.format_exc(5), pprint(current.request))
            mail.send(mail.settings.sender, 'bug reporting error', msg)
            return False

    def undo(self, bug_id, log_id, score, bugstatus, user_id, comment):
        '''
        Reverse the recorded effects of a single wrong answer for a given user.

        Intended to be run when an administrator or instructor sets a bug to
        'confirmed' or 'fixed'.
        '''
        newscore = 1.0
        db = current.db

        # Find all equivalent bug reports
        bug_row = db.bugs(bug_id)
        bug_query = db((db.bugs.step == bug_row.step) &
                       (db.bugs.in_path == bug_row.in_path) &
                       (db.bugs.user_response == bug_row.user_response) &
                       (db.bugs.score < 1))
        bugrows = bug_query.select()

        # Update those bug reports with the new values
        bug_query.update(**{'score': newscore,
                            'admin_comment': comment,
                            'bug_status': bugstatus})

        # Fix scores for all identical attempts in log
        # TODO: This will only work for bugs recorded since adding
        # user_response to attempt_log table
        try:
            logquery = db((db.attempt_log.step == bug_row.step) &
                        (db.attempt_log.user_response == bug_row.user_response) &
                        (db.attempt_log.score != newscore))
            if not logquery.count():
                # TODO: for now, also correct target log row directly by id
                logquery = db(db.attempt_log.id == log_id)
        except AttributeError:
            logquery = db(db.attempt_log.id == log_id)
        logquery.update(**{'score': newscore})
        logrows = logquery.select()
        print '\ncorrecting', logquery.count(), 'log entries'
        print [l.id for l in logrows]

        if newscore - 1 <= 0.000000009:  # account for float inaccuracy
            # Fix last_right, last_wrong, times_right, and times_wrong in each
            # tag_records row for each affected user
            try:
                tagids = db.steps(bug_row.step).tags
                names = set([b.name for b in bugrows])
                trecords = db((db.tag_records.tag.belongs(tagids)) &
                              (db.tag_records.name.belongs(names))).select()
                for myname in names:
                    myrecs = trecords.find(lambda r: r.name == myname)
                    new_logs_right = logrows.find(lambda r:
                                                  (r.name == myname) and
                                                  (abs(r.score - 1) <= 0.000000009))
                    newdates = [r.dt_attempted for r in new_logs_right]
                    new_latest_right = max(newdates)
                    new_earliest_right = min(newdates)
                    for tr in myrecs:
                        updates = {}
                        # correct last right and last wrong dates
                        if new_latest_right > tr.tlast_right:
                            updates['tlast_right'] = new_latest_right
                        if tr.tlast_wrong > new_earliest_right and \
                                tr.tlast_wrong < new_latest_right:
                            rightids = [r.id for r in new_logs_right]
                            oldlogs = db((db.attempt_log.name == myname) &
                                         (db.attempt_log.dt_attempted
                                          > new_earliest_right) &
                                         (db.attempt_log.dt_attempted
                                          < new_latest_right) &
                                         (db.attempt_log.step.tags.contains([tr.tag])) &
                                         (abs(db.attempt_log.score - 1) > 0.00000009)
                                         ).select()
                            oldlogs.exclude(lambda r: r.id in rightids)
                            if oldlogs:
                                odates = [l.dt_attempted for l in oldlogs]
                                updates['tlast_wrong'] = max(odates)

                        # correct counts for times right and wrong
                        rightcount = sum(l.score for l in new_logs_right)
                        updates['times_right'] += rightcount
                        updates['times_wrong'] -= rightcount
                        # commit the updates to db
                        print '\nupdating tag record', tr.id
                        pprint(updates)
                        tr.update_record(**updates)
                return 'Bug {} reversed.'.format(bug_id)

            except Exception:
                print traceback.format_exc(5)
                return 'Bug {} could not be reversed.'.format(bug_id)

    def bugresponses(self, user):
        '''
        Returns a list of the bug reports submitted by 'user'. Each list item
        is itself a list containing the step prompt, user_response,
        date_submitted, bug_status, and admin_comment for an individual bug
        report.
        '''
        db = current.db

        bugs_q = ((db.steps.id == db.bugs.step) & (db.bugs.user_name == user))
        bugs = db(bugs_q).select(orderby=~db.bugs.date_submitted)
        lst = []
        for b in bugs:
            try:
                display = []
                display.append(b.bugs.id)
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
            except Exception:
                print traceback.format_exc(5)
        return lst
