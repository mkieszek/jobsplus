# -*- coding: utf-8 -*-
"""
@author: pczorniej
"""

from openerp.osv import fields, osv
import pdb
import datetime
from openerp import tools
from datetime import date, timedelta

class jp_offer_report(osv.Model):
    """ Lead Report Sales """
    _name = "jp.offer.report"
    _auto = False
    _description = "Offer report"

    _columns = {
        'stage_id' : fields.many2one('jp.offer.stage','Offers Stage', readonly=True),
        'nbr' : fields.integer('nbr', readonly=True),
        'sales_rep':fields.many2one('res.users', 'User', readonly=True),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_offer_report')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_offer_report AS (
            
                SELECT id, stage_id, 1 as nbr, sales_rep
                
                FROM jp_offer 
                where sales_rep in (6,7,8,23)

            )""")
        
class jp_revenue_report(osv.Model):
    _name = "jp.revenue.report"
    _auto = False
    _description = "Planned Revenue"

    _columns = {
        'planned_revenue': fields.integer('Planned Revenue', readonly=True),
        'month' : fields.char('Month', readonly=True),
        'stage_id' : fields.many2one('jp.deal.stage','stage',readonly=True),
        }
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_revenue_report')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_revenue_report AS (
            
            SELECT id, planned_revenue, to_char(handover_date, 'YYYY-MM') as month, stage_id
            FROM jp_deal
            where handover_date > cast(date_trunc('month', current_date - interval '1 month') as date) and handover_date < cast(date_trunc('month', current_date + interval '5 month')- interval '1 day' as date)
            )""")
        
        
class jp_deal_report32(osv.Model):
    _name = "jp.deal.report32"
    _auto = False
    _description = "Deal report32"

    _columns = {
        'id': fields.many2one('jp.deal', 'Deal'),
        'stage_id': fields.many2one('jp.deal.stage','Deals Stage', readonly=True),
        'planned_revenue': fields.integer('Planned revenue'),
        'user_id': fields.many2one('res.users', 'Salesman'),
        'nbr': fields.integer('NBR'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_deal_report3')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_deal_report32 AS (

            SELECT id, planned_revenue, 1 as nbr, stage_id, state, user_id
            FROM jp_deal
            WHERE state = 'open' and stage_id != 8

            )""")
        