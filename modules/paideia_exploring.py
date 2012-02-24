from gluon import current, URL, redirect

class paideia_path:

    def __init__(self):
        """set the path a student is exploring, retrieve its data, and store the data in the session object"""

        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

    def check(self):
        """Find out whether to introduce another step, free the user for movement, or continue with 
        the current step."""
        
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db
        
        #has the user completed enough paths for today?
        if session.completed_paths:
            len(session.completed_paths)
        
        
    def pick(self):
        """Choose a new path for the user, based on tag performance"""    
        
    def set(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

        if not session.path_length:
            the_path = db(db.quizzes.id == request.vars.path).select()
            session.path_id = the_path[0].id
            session.path_length = the_path[0].length
            session.path_name = the_path[0].quiz
            session.path_freq = the_path[0].frequency
            session.path_tags = the_path[0].tags
    
    def end(self):
        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db        
        
        pass

class counter:

    def __init__(self):
        """include this question in the count for this quiz, send to 'end' if quiz is finished"""

    def check(self):        
        #current object must be accessed at runtime, so can't be global variable
        session, request = current.session, current.request

        if session.q_counter:
            if int(session.q_counter) >= int(session.path_length):
                session.q_counter = 0
                redirect(URL('index', args=['end']))
                return dict(end="yes")
            else:
                session.q_counter += 1
        else:
            session.q_counter = 1

    def set(self):
        
    def clear(self):
        
