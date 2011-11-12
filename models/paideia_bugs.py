import datetime

#hack to get imports for PyDev ide
if 0:
    from gluon import current, SQLFORM, redirect, A, URL, H3
    from gluon.tools import Auth, Crud
    from gluon.dal import DAL
    db = DAL()
    auth = Auth()
    cache=current.cache
    T = current.t
    response = current.response
    service = current.service
    request = current.request
    session = current.session
    crud = Crud()
    
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
            d.append(b.q_bugs.submitted)
            #get status label instead of raw status reference
            s = b.q_bugs.bug_status
            if s == None:
                s = 5
            st = db(db.bug_status.id == s).select().first()
            status = st.status_label
            d.append(status)
            d.append(b.q_bugs.admin_comment)
            l.append(d)
        return l
