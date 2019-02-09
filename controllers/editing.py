# coding: utf8

if 0:
    from gluon import current, URL
    auth = current.auth
    db = current.db
    request = current.request
from applications.paideia.modules.paideia_bugs import Bug
from applications.paideia.modules.paideia_utils import simple_obj_print
import re

@auth.requires_membership(role='administrators')
def listing():
    return dict()

@auth.requires_membership(role='administrators')
def undo_bug():
    '''
    Controller to receive ajax signal and trigger the Bug class method to undo
    the effects of a reported bug on the user's performance record.
    '''
    b = Bug(request.vars.step, request.vars.in_path, request.vars.map_location)
    u = b.undo(request.vars.id, request.vars.log_id, float(request.vars.score),
               request.vars.bug_status, request.vars.user_name,
               request.vars.admin_comment)
    return u

@auth.requires_membership(role='administrators')
def sil():
    """ """
    response = current.response
        # Scripts for charts
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/d3/3.4.10/d3.min.js')
    response.files.append(URL('static', 'js/user_stats.js'))

    # Include files for Datatables jquery plugin and bootstrap css styling
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.0/'
                          'js/jquery.dataTables.min.js')
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables-colvis/1.1.0/'
                          'js/datatables.colvis.min.js')
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables-colvis/1.1.0/'
                          'css/datatables.colvis.min.css')
    response.files.append("https://cdn.datatables.net/fixedcolumns/3.0.1/js/"
                          "dataTables.fixedColumns.min.js")  # fixedColumns plugin
    response.files.append("https://cdn.datatables.net/fixedcolumns/3.0.1/css/"
                          "dataTables.fixedColumns.css")  # fixedColumns plugin css
    response.files.append("https://cdn.datatables.net/plug-ins/28e7751dbec/"
                          "integration/bootstrap/3/dataTables.bootstrap.css")  # bootstrap css

    steps_inactive_locations_data = []
    steps_inactive_locations_data = db(db.steps_inactive_locations.id > 0).select(db.steps_inactive_locations.ALL,orderby=db.steps_inactive_locations.step_id).as_list()
    #simple_obj_print(steps_inactive_locations_data, "steps_inactive_locations_data")
    return {'steps_inactive_locations_data': steps_inactive_locations_data}


@auth.requires_membership(role='administrators')
def tnb():
    """ 
    tags no badges report
    """
    response = current.response
        # Scripts for charts
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/d3/3.4.10/d3.min.js')
    response.files.append(URL('static', 'js/user_stats.js'))

    # Include files for Datatables jquery plugin and bootstrap css styling
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.0/'
                          'js/jquery.dataTables.min.js')
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables-colvis/1.1.0/'
                          'js/datatables.colvis.min.js')
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables-colvis/1.1.0/'
                          'css/datatables.colvis.min.css')
    response.files.append("https://cdn.datatables.net/fixedcolumns/3.0.1/js/"
                          "dataTables.fixedColumns.min.js")  # fixedColumns plugin
    response.files.append("https://cdn.datatables.net/fixedcolumns/3.0.1/css/"
                          "dataTables.fixedColumns.css")  # fixedColumns plugin css
    response.files.append("https://cdn.datatables.net/plug-ins/28e7751dbec/"
                          "integration/bootstrap/3/dataTables.bootstrap.css")  # bootstrap css

    tags = db(db.tags.id > 0).select(db.tags.id).as_list()
    tag_ids =  [t['id'] for t in tags]
    badges = db(db.badges.id > 0).select(db.badges.tag).as_list()
    badge_tag_ids = [t['tag'] for t in badges]
    tag_no_badge_ids = list(set(tag_ids).difference(badge_tag_ids))
    tag_no_badge_ids_data = []
    
    if tag_no_badge_ids:
        tag_no_badge_ids_data = db(db.tags.id.belongs(tag_no_badge_ids)).select(db.tags.id,db.tags.tag,db.tags.tag_position,db.tags.modified_on, orderby=db.tags.id).as_list()

    print({'tag_no_badge_ids': tag_no_badge_ids})
    print({'tag_no_badge_ids_data': tag_no_badge_ids_data})
    return {'tag_no_badge_ids_data': tag_no_badge_ids_data}



@auth.requires_membership(role='administrators')
def pregex():
    """ 
    problem regex report
    """
    response = current.response
        # Scripts for charts
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/d3/3.4.10/d3.min.js')
    response.files.append(URL('static', 'js/user_stats.js'))

    # Include files for Datatables jquery plugin and bootstrap css styling
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables/1.10.0/'
                          'js/jquery.dataTables.min.js')
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables-colvis/1.1.0/'
                          'js/datatables.colvis.min.js')
    response.files.append('//cdnjs.cloudflare.com/ajax/libs/datatables-colvis/1.1.0/'
                          'css/datatables.colvis.min.css')
    response.files.append("https://cdn.datatables.net/fixedcolumns/3.0.1/js/"
                          "dataTables.fixedColumns.min.js")  # fixedColumns plugin
    response.files.append("https://cdn.datatables.net/fixedcolumns/3.0.1/css/"
                          "dataTables.fixedColumns.css")  # fixedColumns plugin css
    response.files.append("https://cdn.datatables.net/plug-ins/28e7751dbec/"
                          "integration/bootstrap/3/dataTables.bootstrap.css")  # bootstrap css
    steps = db(db.steps.id > 0).select(db.steps.id).as_list()
    step_ids =  [s['id'] for s in steps]
    exception_responses = []
    for s in step_ids:
        step = db.steps[s]
        x = {'id':s, '1': '-','2': '-','3': '-'}
        try:
            if step['response1']:
                #print {'testing id': s, 'response1' : step['response1']}
                if re.match(step['response1'], "dummy", re.I | re.U):
                    print({'passed id': s, 'response1' : step['response1']})
                    pass
        except re.error:
            x['1'] = step['response1']
            print({'failed id': s, 'response1' : step['response1']})
        try:
            if step['response2']:
                if re.match(step['response2'], "dummy", re.I | re.U):
                    pass
        except re.error:
            x['2'] = step['response2'] 
        try:
            if step['response3']:
                if re.match(step['response3'], "dummy", re.I | re.U):
                    pass
        except re.error:
            x['3'] = step['response3'] 
        if ( not((x['1'] == '-') and (x['2'] == '-') and (x['3'] == '-'))):
            exception_responses.append(x)
    #print {'exception_responses': exception_responses}
    return {'exception_responses': exception_responses}
