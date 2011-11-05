
if 0:
    from gluon import current, URL, redirect 
    from gluon.dal import DAL
    from gluon.tools import Auth
    request,session,response,T,cache=current.request,current.session,current.response,current.t,current.cache
    db = DAL()
    auth = Auth()

class activepath:

    def __init__(self):
        """set the path a student is exploring, retrieve its data, and store the data in the session object"""
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
        if session.q_counter:
            if int(session.q_counter) >= int(session.path_length):
                session.q_counter = 0
                redirect(URL('index', args=['end']))
                return dict(end="yes")
            else:
                session.q_counter += 1
        else:
            session.q_counter = 1

    