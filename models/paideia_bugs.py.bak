import datetime

#hack to get imports for PyDev ide
if 0:
    from gluon import TD
    from gluon.tools import current
    from gluon.dal import DAL
    db = DAL()   
    session = current.session
    response = current.response

class paideia_bugs:
    """This class handles the creation, manipulation, and reporting of bug reports for paideia."""
    def __init__(self, qID = 0):
        self.qID = qID
        return
    def lognew(self, answer):
        """creates a new bug report and provides confirmation to the user."""
        db.q_bugs.insert(question=self.qID, a_submitted=answer)
        response.flash = 'Thanks for reporting this potential bug.'
        return dict(message = 'If this turns out to be a bug it will be taken into account as we track your learning.')
    
    def updatebug(self):
        """provides form and page components to update an existing bug and handles the  """
        edit_form = crud.update(db.q_bugs, request.args[0])
        closer = A('close', _href=URL('#'), _class='close_link')
        the_title = H3('Reviewing Bug Report for Question')
    
    def bugresponse(self, the_user):
        u = the_user
        bugs = db((db.questions.id == db.q_bugs.question) & (db.q_bugs.name == u)).select()
        l = []
        for b in bugs:
            d = []
            d.append(b.questions.question)
            d.append(b.q_bugs.a_submitted)
            d.append(b.q_bugs.date_submitted)
            d.append(b.q_bugs.bug_status)
            d.append(b.q_bugs.admin_comment)
            l.append(d)
        return l
