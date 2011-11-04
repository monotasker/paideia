import datetime

class paideia_bugs:
    """This class handles the creation, manipulation, and reporting of bug reports for paideia."""
    def __init__(self):
        return
    def lognew(self,  qID,  answer):
        """creates a new bug report and provides confirmation to the user."""
        db.q_bugs.insert(question=qID, a_submitted=answer)
        response.flash = 'Thanks for reporting this potential bug.'
        return dict(message = 'If this turns out to be a bug it will be taken into account as we track your learning.')
   # def updatebug(self):
   # def bugresponse(self):
