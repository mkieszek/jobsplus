# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp import tools

class jp_task_report_rec(osv.Model):
    _name = "jp.task.report.rec"
    _auto = False
    _description = "Task report"

    _columns = {
        'id': fields.many2one('project.task', 'Deal'),
        'deadline': fields.char('Tasks Stage'),
        'user_id': fields.many2one('res.users', 'User'),
        'nbr': fields.integer('NBR'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_task_report_rec')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_task_report_rec AS (
                            
                select id, user_id, state, deadline_datetime, 1 as nbr,
                CASE
                  WHEN deadline_datetime is NULL THEN 'Brak daty'
                  WHEN extract(epoch from (deadline_datetime - (localtimestamp - interval '2 hours'))) <= 0 THEN 'Po termine'
                  WHEN extract(epoch from (deadline_datetime - (localtimestamp - interval '2 hours'))) > 0 THEN 'Przed terminem'
                  END as deadline
                from project_task
                where user_id in (11,13,14,15,16,17,24) and (state != 'done' or state != 'cancelled')

            )""")