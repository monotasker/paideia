from gluon import current, SQLFORM, redirect, A, URL, H3
from gluon.tools import Crud


class paideia_bugs:
    """This class handles the creation, manipulation, and reporting of bug reports for paideia."""
    def __init__(self, qID = 0):
        self.qID = qID
        return

    def lognew(self, answer):
        """creates a new bug report and provides confirmation to the user."""

        response, db = current.response, current.db

        db.q_bugs.insert(question=self.qID, a_submitted=answer)
        response.flash = 'Thanks for reporting this potential bug.'
        return dict(message = 'If this turns out to be a bug it will be taken into account as we track your learning.')

    def updatebug(self):
        """provides form and page components to update an existing bug and handles the  """

        request, db = current.request, current.db
        crud = Crud(db)

        edit_form = crud.update(db.q_bugs, request.args[0])
        closer = A('close', _href=URL('#'), _class='close_link')
        the_title = H3('Reviewing Bug Report for Question')

    def bugresponse(self, the_user):

        db = current.db

        bugs = db((db.questions.id == db.q_bugs.question) & (db.q_bugs.name == the_user)).select()
        lst = []
        for bug in bugs:
            display = []
            display.append(bug.questions.question)
            display.append(bug.q_bugs.a_submitted)
            display.append(bug.q_bugs.submitted)
            #get status label instead of raw status reference
            s = bug.q_bugs.bug_status
            if s == None:
                s = 5
            st = db(db.bug_status.id == s).select().first()
            status = st.status_label
            display.append(status)
            display.append(bug.q_bugs.admin_comment)
            lst.append(display)
        return lst
