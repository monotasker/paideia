import datetime
from gluon import current
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
        mystep = db.steps[step_id]
        self.prompt = mystep['prompt'] if mystep else None
        self.step_options = mystep['step_options'] if mystep else None
        self.readable_response = mystep['readable_response'] if mystep else None
        if isinstance(loc_id, str):
            self.loc_id = db(db.locations.loc_alias == loc_id
                             ).select(db.locations.id).first()

    def log_new(self, answer, log_id, score, user_comment):
        """
        creates a new bug report and provides confirmation to the user.
        """
        response = current.response
        db = current.db
        try:
            argdict = {"step": self.step_id,
                       "in_path": self.path_id,
                       "map_location": self.loc_id,
                       "prompt": self.prompt,
                       "step_options": self.step_options,
                       "user_response": answer,
                       "sample_answers": self.readable_response,
                       "user_comment": user_comment,
                       "score": score}

            if log_id not in [None, False, 'None']:  # to allow for queries on repeating (unrecorded) steps
                argdict['log_id'] = log_id

            db.bugs.insert(**argdict)
            return True
        except Exception:
            print traceback.format_exc(5)
            mail = current.mail
            msg = '<html>A user tried to submit a step bug report, but the' \
                  'report failed. Traceback: {} \n\n' \
                  'The request data is:\n{}\n' \
                  '</html>'.format(traceback.format_exc(5), pprint(current.request))
            mail.send(mail.settings.sender, 'bug reporting error', msg)
            return False

    def _fix_attempt_logs(self, bugrows, newscore, message, bug_id):
        """
        """
        db = current.db
        logids = list(set([b.log_id for b in bugrows]))
        logquery = db(db.attempt_log.id.belongs(logids))
        # print 'logids', logids
        # print 'logquery', logquery.count()
        assert logquery.count() == len(logids)
        logrows = logquery.select()
        logquery.update(**{'score': newscore})
        db.commit()
        message += '\nCorrected {} attempt_log rows: {}. '.format(str(logquery.count()),
                                                              logids)
        # confirm that scores were changed
        newlogs = db(db.attempt_log.id.belongs(logids)).select()
        badlogscores = [l.score for l in newlogs if l.score != newscore]
        assert not badlogscores, '{} logs have wrong score'.format(len(badlogscores))

        return logrows, message

    def _fix_tag_records(self, bugusers, logrows, message, bug_id, scoredif,
                         newscore):
        """
        Fix last_right, last_wrong, times_right, and times_wrong in tag_records
        """
        # print 'logrows is length', len(logrows)
        db = current.db
        right_threshold = 0.999999
        try:
            # find affected records
            mystep = db.steps(self.step_id)
            tagids = mystep.tags
            tag2ids = mystep.tags_secondary
            trecords = db((db.tag_records.tag.belongs(tagids)) &
                          (db.tag_records.name.belongs(bugusers))).select()
            t2records = db((db.tag_records.tag.belongs(tag2ids)) &
                           (db.tag_records.name.belongs(bugusers))).select()

            # loop over users to fix their record for each affected tag
            updated_list = []
            for myname in bugusers:
                myrecs = trecords.find(lambda r: r.name == myname)
                myrecs2 = t2records.find(lambda r: r.name == myname)
                # print '\nuser {} has {} affected tag records'.format(myname, len(myrecs))
                # print 'and {} affected records for secondary tags'.format(len(myrecs2))
                new_logs_right = logrows.find(lambda r: r.name == myname)
                # print 'new_logs_right is', logrows
                if len(new_logs_right):
                    newdates = [r.dt_attempted for r in new_logs_right]
                    new_latest_right = max(newdates)
                    new_earliest_right = min(newdates)
                    for tr2 in myrecs2:
                        # correct list of secondary-right datetimes for
                        # secondary tags
                        if newscore >= right_threshold:
                            seclist = tr2.secondary_right
                            seclist.extend(newdates)
                        tr2.update_record(**{'secondary_right': seclist})
                        db.commit()
                    for tr in myrecs:
                        if newscore >= right_threshold:
                            # print '\ntrying to update tag_record {}'.format(tr.id)
                            updates = {}

                            # correct last right and last wrong dates
                            # bring tlast_right forward if necessary
                            if new_latest_right > tr.tlast_right:
                                updates['tlast_right'] = new_latest_right

                            # adjust tlast_wrong if falls during affected period
                            if tr.tlast_wrong > new_earliest_right and \
                                    tr.tlast_wrong < new_latest_right:
                                rightids = [r.id for r in new_logs_right]
                                # find wrong logs during period
                                oldlogs = db((db.attempt_log.name == myname) &
                                             (db.attempt_log.dt_attempted >=
                                              new_earliest_right) &
                                             (db.attempt_log.dt_attempted <=
                                              new_latest_right) &
                                             (db.attempt_log.step.tags.contains([tr.tag])) &
                                             (db.attempt_log.score <
                                              right_threshold)
                                             ).select()
                                # print 'oldlogs is', len(oldlogs)
                                if oldlogs:
                                    odates = [l.dt_attempted for l in oldlogs]
                                    updates['tlast_wrong'] = max(odates)
                            # print 'done with tag record', tr.id

                        # correct counts for times right and wrong
                        rightsum = sum(scoredif for l in new_logs_right)
                        updates['times_right'] = tr.times_right + rightsum
                        updates['times_wrong'] = tr.times_wrong - rightsum
                        if updates['times_wrong'] < 0:
                            updates['times_wrong'] = 0
                        # print 'updates: ', updates
                        # commit the updates to db
                        updated_list.append(tr.id)
                        tr.update_record(**updates)
                        db.commit()

                else:  # user has no wrong logs to be changed
                    print 'user has no wrong logs to be changed'
            message += '\nUpdated these tag records rows: {}. '.format(updated_list)

        except Exception:
            print traceback.format_exc(5)
            message += '\nTag_records rows for bug {} could not be reversed. '.format(bug_id)

        return updated_list, message

    def undo(self, bug_id, log_id, score, bugstatus, user_id, comment,
             user_response, user_comment, adjusted_score):
        '''
        Reverse the recorded effects of a single wrong answer for a given user.

        Intended to be run when an administrator or instructor sets a bug to
        'confirmed' or 'fixed'.
        '''
        db = current.db
        response = current.response
        message = ''
        newscore = adjusted_score if adjusted_score != None else 1.0
        comments = {'confirmed': 'You\'re right. There was a problem with the '
                                 'evaluation of your answer. We\'ll work on fixing '
                                 'it. When the problem is resolved this report '
                                 'will be marked "fixed" and we will adjust any '
                                 'other affected step attempts in your record. '
                                 'Thanks for helping to make Paideia even better.',
                    'fixed': 'The problem with this step has now been fixed and '
                             'any negative affects on your performance record '
                             'have been reversed. Thanks again for your help.'
                    }
        admin_comment = comment if comment else comments[bugstatus]

        # Find all equivalent bug reports
        thisuser_bug_query = db((db.bugs.step == self.step_id) &
                                (db.bugs.in_path == self.path_id) &
                                (db.bugs.user_response == user_response) &
                                (db.bugs.user_name == int(user_id)) &
                                (db.bugs.score != newscore))
        general_bug_query = db((db.bugs.step == self.step_id) &
                               (db.bugs.in_path == self.path_id) &
                               (db.bugs.user_response == user_response) &
                               (db.bugs.user_comment == user_comment) &
                               (db.bugs.score != newscore))
        general_bugrows = general_bug_query.select()
        user_bugrows = thisuser_bug_query.select()
        bugrows = general_bugrows & user_bugrows

        # Update those bug reports with the new values
        statusid = db(db.bug_status.status_label == bugstatus).select().first().id
        newvals = {'adjusted_score': newscore,
                   'admin_comment': comment,
                   'bug_status': statusid}
        thisuser_bug_query.update(**newvals)
        general_bug_query.update(**newvals)
        bugusers = list(set([b.user_name for b in bugrows]))
        message += "\nUpdated {} bug reports for {} users. ".format(len(bugrows),
                                                                  len(bugusers))
        # don't adjust records if no score change
        if score < adjusted_score and abs(score - adjusted_score) > 0.0000009:
            # Find and fix affected attempt log rows
            logrows, message = self._fix_attempt_logs(bugrows, newscore,
                                                      message, bug_id)

            # Find and fix tag_records for affected users
            scoredif = adjusted_score - score
            recids, message = self._fix_tag_records(bugusers, logrows,
                                                    message, bug_id, scoredif,
                                                    adjusted_score)

        # print message
        return message

    def bugresponses(self, user):
        '''
        Returns a list of the bug reports submitted by 'user'. Each list item
        is itself a list containing the step prompt, user_response,
        date_submitted, bug_status, and admin_comment for an individual bug
        report.
        '''
        db = current.db
        print 'possible vals:'
        print list(set([v.deleted for v in db(db.bugs.id > 0).select()]))
        bugs_q = ((db.steps.id == db.bugs.step) &
                  (db.bugs.user_name == user))
        bugs = db(bugs_q).select(orderby=~db.bugs.date_submitted)
        bugs.exclude(lambda r: r.bugs.deleted is True)
        lst = []
        for b in bugs:
            try:
                display = []
                display.append(b.bugs.id)
                display.append(b.steps.prompt)
                display.append(b.bugs.user_response)
                display.append(b.bugs.sample_answers)
                display.append(b.bugs.score)
                display.append(b.bugs.date_submitted)
                display.append(b.bugs.user_comment)
                #get status label instead of raw status reference
                s = b.bugs.bug_status
                if s is None:
                    s = 5
                st = db(db.bug_status.id == s).select().first()
                status = st.status_label
                display.append(status)
                display.append(b.bugs.adjusted_score)
                display.append(b.bugs.admin_comment)
                if b.bugs.hidden:
                    display.append('bug-read')
                else:
                    display.append('bug-unread')
                lst.append(display)
            except Exception:
                print traceback.format_exc(5)
        return lst

    @staticmethod
    def delete_bug(log_id):
        '''
        Static method to set bug record as "deleted." This will prevent it
        from appearing in ordinary lists of bug reports. The record is not
        actually removed from the database, so that it may be examined if
        necessary later on.
        '''
        db = current.db
        myargs = {'deleted': True,
                  'modified_on': datetime.datetime.utcnow()}
        try:
            myrow = db.bugs(log_id)
            print myrow
            myrow.update_record(**myargs)
            db.commit()
            print 'committed'
            print myrow.deleted is True
            return myrow.id
        except Exception, e:
            print 'Error'
            print e
            return 'false'


def trigger_bug_undo(*args, **kwargs):
    """
    """
    db = current.db
    mystatus = db(db.bug_status.id == kwargs['bug_status']).select().first()
    result = "No records reversed."

    pprint(kwargs)
    pprint(args)
    if mystatus['status_label'] in ['fixed', 'confirmed', 'allowance_given']:
        # print 'undoing bug!'
        # print 'args'
        # pprint(args)
        # print 'kwargs'
        # pprint(kwargs)
        step_id = kwargs['step']
        path_id = kwargs['in_path']
        loc_id = kwargs['map_location']
        bug_id = kwargs['id']
        log_id = kwargs['log_id']
        score = kwargs['score']
        # below needed to avoid error updating non-existent log entry
        adjusted_score = kwargs['adjusted_score'] if kwargs['log_id'] else 0
        bugstatus = mystatus['status_label']
        user_id = kwargs['user_name']
        comment = kwargs['admin_comment']
        user_comment = kwargs['user_comment']
        user_response = kwargs['user_response']
        mybug = Bug(step_id=step_id, path_id=path_id, loc_id=loc_id)
        result = mybug.undo(bug_id, log_id, score, bugstatus, user_id, comment,
                            user_response, user_comment, adjusted_score)
    return result
