from gluon import current, SQLFORM, redirect, A, URL, H3
from gluon.tools import Crud


class Bug(object):
    """
    Handles the creation, manipulation, and reporting of bug
    reports for paideia.
    """
    def __init__(self, step=None, path=None, location=None):
        session = current.session

        if not step:
            step = session.walk['step']
        self.step = step
        if not path:
            path = session.walk['path']
        self.path = path
        if not location:
            location = session.walk['location']
        self.location = location
        return

    def log_new(self, answer):
        """
        creates a new bug report and provides confirmation to the user.
        """
        response, db = current.response, current.db
        try:
            db.bugs.insert(step=self.step, path=self.path,
                            location=self.location, user_response=answer)
            response.flash = 'Thanks for reporting this potential bug. We will\
                    look at the question to see what the problem was. If there\
                    turns out to be a problem with the question, this answer\
                    will be ignored as we track your learning. Check your\
                    profile page in the next few days to see the instructor\'s\
                    response to your bug report.'
            return True
        except:
            response.flash = 'Sorry, something went wrong with your bug\
                    report. Please contact the instructor.'
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

    def bugresponse(self, the_user):

        db = current.db

        bugs = db((db.steps.id == db.bugs.step) & (db.bugs.name == the_user)).select()
        lst = []
        for b in bugs:
            display = []
            display.append(b.questions.step)
            display.append(b.bugs.user_response)
            display.append(b.bugs.date_submitted)
            #get status label instead of raw status reference
            s = bug.bugs.bug_status
            if s == None:
                s = 5
            st = db(db.bug_status.id == s).select().first()
            status = st.status_label
            display.append(status)
            display.append(bug.bugs.admin_comment)
            lst.append(display)
        return lst
