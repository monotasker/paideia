# coding: utf8

if 0:
    from gluon import current, URL, A, H3
    from gluon.dal import DAL
    from gluon.tools import Auth, Crud
    request,session,response,T,cache=current.request,current.session,current.response,current.t,current.cache
    crud = Crud()
    db = DAL()
    auth = Auth()

from paideia_bugs import paideia_bugs

@auth.requires_membership(role="administrators")
def question():
    edit_form = crud.create(db.questions)
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Create a New Question')

    return dict(form = edit_form, closer=closer, the_title=the_title)


@auth.requires_membership(role="administrators")
def quiz():
    edit_form = crud.create(db.quizzes)
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Create a New Quiz')

    return dict(form = edit_form, closer=closer, the_title=the_title)

@auth.requires_membership(role="administrators")
def tag():
    edit_form = crud.create(db.tags)
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Create a New Tag')

    return dict(form = edit_form, closer=closer, the_title=the_title)

@auth.requires_login()
def q_bug():
    """creates new bug report
    Two arguments are necessary to create the bug report:
    session.qID identifies the question against which bug is logged
    request.vars.answer identifies the answer that was submitted prior to report

    the .lognew() method of paideia_bugs class also returns a response message to the user, and this function passes that message along to the view.
    """
    b = paideia_bugs(session.qID)
    return dict(b.lognew(request.vars.answer))

@auth.requires_membership(role='administrators')
def news():
    form = crud.create(db.news)
    the_title = H3('Create a New News Story')
    closer = A('close', _href=URL('#'), _class='close_link')

    return dict(form = form, the_title = the_title, closer = closer)
