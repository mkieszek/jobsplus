# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp import tools

class jp_task_report(osv.Model):
    _name = "jp.task.report"
    _auto = False
    _description = "Task report"

    _columns = {
        'id': fields.many2one('project.task', 'Deal'),
        'deadline': fields.char('Tasks Stage'),
        'user_id': fields.many2one('res.users', 'User'),
        'nbr': fields.integer('NBR'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_task_report')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_task_report AS (
                            
                select id, user_id, state, deadline_datetime, 1 as nbr,
                CASE
                  WHEN deadline_datetime is NULL THEN 'Brak daty'
                  WHEN extract(epoch from (deadline_datetime - (localtimestamp - interval '2 hours'))) <= 0 THEN 'Po termine'
                  WHEN extract(epoch from (deadline_datetime - (localtimestamp - interval '2 hours'))) > 0 THEN 'Przed terminem'
                  END as deadline
                from project_task
                where (state!='done' and state!='cancelled') and user_id in (6,7,8,23)
            )""")
        
class jp_task_report2(osv.Model):
    _name = "jp.task.report2"
    _auto = False
    _description = "Task report2"

    _columns = {
        'id': fields.many2one('jp.deal', 'Deal'),
        'stage_id': fields.many2one('project.task.type','Tasks Stage', readonly=True),
        'user_id': fields.many2one('res.users', 'User'),
        'nbr': fields.integer('NBR'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_task_report2')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_task_report2 AS (
            
                SELECT id, 1 as nbr, stage_id, user_id
                FROM project_task
                where state='open'

            )""")