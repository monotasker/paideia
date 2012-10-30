# coding: utf8

if 0:
    from gluon import current, A, crud, URL, H3
    auth = current.auth
    db = current.db
    request = current.request


@auth.requires_membership(role='administrators')
def question():
    edit_form = crud.update(db.questions, request.args[0])
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Editing Question ' + request.args[0])

    return dict(form = edit_form, closer=closer, the_title=the_title)

@auth.requires_membership(role='administrators')
def quiz():
    edit_form = crud.update(db.quizzes, request.args[0])
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Editing Quiz')

    return dict(form = edit_form, closer=closer, the_title=the_title)


@auth.requires_membership(role='administrators')
def tag():
    edit_form = crud.update(db.tags, request.args[0])
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Editing Tag')

    return dict(form = edit_form, closer=closer, the_title=the_title)

@auth.requires_membership(role='administrators')
def bug():
    edit_form = crud.update(db.q_bugs, request.args[0])
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Editing Bug Report')
    return dict(form = edit_form, closer=closer, the_title=the_title)

@auth.requires_membership(role='administrators')
def news():
    edit_form = crud.update(db.news, request.args[0])
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Editing New Story')

    return dict(form = edit_form, closer=closer, the_title=the_title)

@auth.requires_membership(role='administrators')
def listing():
    return dict()
