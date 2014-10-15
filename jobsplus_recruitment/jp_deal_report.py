# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp import tools

class jp_deal_report(osv.Model):
    _name = "jp.deal.report"
    _auto = False
    _description = "Deal report"

    _columns = {
        'id': fields.many2one('jp.deal', 'Deal'),
        'stage_id': fields.many2one('jp.deal.stage','Deals Stage', readonly=True),
        'handover_date': fields.date('Hanover date'),
        'dealy': fields.integer('Dealy'),
        'recruiter_id': fields.many2one('res.users', 'Recruiter'),
        'delay_group': fields.char('Dealy group'),
        'nbr': fields.integer('NBR'),
        'sequence' : fields.integer('Sekwencja'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_deal_report')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_deal_report AS (
            
                SELECT id, 1 as nbr, handover_date, current_date, current_date - handover_date as delay, stage_id, recruiter_id, 
                CASE 
                    WHEN current_date - handover_date is null THEN '?'
                    WHEN current_date - handover_date <=0 THEN '0'
                    WHEN current_date - handover_date <=3 THEN '3'
                    WHEN current_date - handover_date <=7 THEN '7'
                    WHEN current_date - handover_date <=10 THEN '10'
                    WHEN current_date - handover_date <=14 THEN '14'
                    WHEN current_date - handover_date <=30 THEN '30'
                    ELSE '>30'
                   END as delay_group,
                CASE 
                    WHEN current_date - handover_date is null THEN 10
                    WHEN current_date - handover_date <=0 THEN 20
                    WHEN current_date - handover_date <=3 THEN 30
                    WHEN current_date - handover_date <=7 THEN 40
                    WHEN current_date - handover_date <=10 THEN 50
                    WHEN current_date - handover_date <=14 THEN 64
                    WHEN current_date - handover_date <=30 THEN 70
                    ELSE '80'
                   END as sequence
                FROM jp_deal
                WHERE
                  state = 'open' and recruiter_id in (11,13,14,15,16,17,24)

            )""")
        
class jp_deal_report2(osv.Model):
    _name = "jp.deal.report2"
    _auto = False
    _description = "Deal report2"

    _columns = {
        'id': fields.many2one('jp.deal', 'Deal'),
        'stage_id': fields.many2one('jp.deal.stage','Deals Stage', readonly=True),
        'recruiter_id': fields.many2one('res.users', 'Recruiter'),
        'nbr': fields.integer('NBR'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_deal_report2')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_deal_report2 AS (

            select jd.id, jd.stage_id, jd.recruiter_id, 1 as nbr
            from jp_deal_stage as ds
            join jp_deal as jd on ds.id = jd.stage_id
            where jd.recruiter_id in (11,13,14,15,16,17,24) and ds.sequence in (10,20,40,50)
            )""")
        
class jp_deal_report3(osv.Model):
    _name = "jp.deal.report3"
    _auto = False
    _description = "Deal report3"

    _columns = {
        'id': fields.many2one('jp.deal', 'Deal'),
        'stage_id': fields.many2one('jp.deal.stage','Deals Stage', readonly=True),
        'planned_revenue': fields.integer('Planned revenue'),
        'recruiter_id': fields.many2one('res.users', 'Recruiter'),
        'nbr': fields.integer('NBR'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_deal_report3')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_deal_report3 AS (

            SELECT id, planned_revenue, 1 as nbr, stage_id, state, recruiter_id
            FROM jp_deal
            WHERE state = 'open' and stage_id != 8

            )""")