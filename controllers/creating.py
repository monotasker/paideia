# coding: utf8
from paideia_bugs import Bug

if 0:
    from gluon import current, URL, A, H3
    from gluon.dal import DAL
    from gluon.tools import Auth, Crud
    request, session = current.request, current.session
    response, T, cache = current.response, current.t, current.cache
    crud = Crud()
    db = DAL()
    auth = Auth()


@auth.requires_membership(role="administrators")
def tag():
    edit_form = crud.create(db.tags)
    closer = A('close', _href=URL('#'), _class='close_link')
    the_title = H3('Create a New Tag')

    return {'form': edit_form, 'closer': closer, 'the_title': the_title}


@auth.requires_login()
def bug():
    """
    Create a new bug report for a step.
    """
    print 'controller.bug:'
    rvars = request.vars
    print 'vars are', rvars
    b = Bug(step_id=rvars.step_id, path_id=rvars.path_id, loc_id=rvars.loc_id)
    print 'created bug object successfully'
    print 'bug is', b
    logged = b.log_new(rvars.answer, rvars.log_id, rvars.score)
    print 'logged bug - response is', logged
    return dict(success=logged)
