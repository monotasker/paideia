from gluon import current, URL, redirect

class activepath:

    def __init__(self):
        """set the path a student is exploring, retrieve its data, and store the data in the session object"""

        #current object must be accessed at runtime, so can't be global variable
        session, request, auth, db = current.session, current.request, current.auth, current.db

        if not session.path_length:
            the_path = db(db.quizzes.id == request.vars.path).select()
            session.path_id = the_path[0].id
            session.path_length = the_path[0].length
            session.path_name = the_path[0].quiz
            session.path_freq = the_path[0].frequency
            session.path_tags = the_path[0].tags


class counter:

    def __init__(self):
        """include this question in the count for this quiz, send to 'end' if quiz is finished"""

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


