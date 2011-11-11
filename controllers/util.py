# coding: utf8
"""
import datetime

def copytimes():
    dates = db(db.q_bugs.id > 0).select()
    c = 0
    for d in dates:
        t = datetime.time(12,0,0)
        dt1 = datetime.datetime.combine(date1, t)
        c += 1
        d.update_record(submitted = dt1)
    form = SQLFORM.grid(db.q_bugs)
        
    return dict(records_update = c, form = form)
    
"""
   
"""       
def copytimes_back():
    dates = db(db.question_records.id > 0).select()
    c = 0
    for d in dates:
        date1 = d.tlast_right
        date2 = d.tlast_wrong
        c += 1
        d.update_record(last_right = date1, last_wrong = date2)
    form = SQLFORM.grid(db.question_records)
        
    return dict(records_update = c, form = form)
"""        