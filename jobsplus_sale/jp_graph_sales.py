# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import fields, osv
from openerp import tools

class jp_graph1(osv.Model):
    _name = "jp.graph1"
    _auto = False
    _description = "Graph"

    _columns = {
        'id': fields.many2one('crm.lead', 'Lead'),
        'user_id': fields.many2one('res.users', 'User'),
        'nbr': fields.integer('NBR'),
        'month': fields.char('Month'),
        'added_leads': fields.integer('Added Leads'),
        'created_deals': fields.integer('Created Deals'),
        'created_contracts': fields.integer('Created Contracts'),
        'closed_tasks': fields.integer('Closed tasks'),
        'invoice_deals': fields.integer('Invoice Deals'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_graph1')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_graph1 AS (
                            
                SELECT id, 1 as nbr, user_id, week_number, month, added_leads, year, created_offers, invoice_deals, 
                        created_contracts, created_deals, closed_tasks
                    FROM jp_report_sales
                    WHERE month >= (to_char(localtimestamp - interval '12 months', 'YYYY') || '-M' || to_char(localtimestamp - interval '12 months', 'MM')) and user_id in (6,7,8,23)
                    
            )""")
        
class jp_graph2(osv.Model):
    _name = "jp.graph2"
    _auto = False
    _description = "Graph"

    _columns = {
        'user_id': fields.many2one('res.users', 'User'),
        'client_id': fields.many2one('res.partner', 'Client'),
        'month': fields.char('Month'),
        'value_invoice': fields.float('Value invoice'),
        'value_margin': fields.float('Value margin'),
        'invoice_deals': fields.integer('Invoice deals'),
        'value_leasing': fields.float('Value leasing'),
        'total': fields.float('Total'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_graph2')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_graph2 AS (      
                
                SELECT id, month, client_id, user_id, value_invoice, value_margin, invoice_deals, value_leasing, value_invoice+value_leasing as total
                    FROM jp_report_sales2
                    WHERE month >= (to_char(localtimestamp - interval '12 months', 'YYYY') || '-M' || to_char(localtimestamp - interval '12 months', 'MM')) and user_id in (6,7,8,23)
                    
            )""")
        
class jp_graph3(osv.Model):
    _name = "jp.graph3"
    _auto = False
    _description = "Graph"

    _columns = {
        'type': fields.char('Type'),
        'value': fields.float('Value'),
        'month': fields.char('Month'),
        }
    
    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'jp_graph3')
        cr.execute("""
            CREATE OR REPLACE VIEW jp_graph3 AS (      
                  
            SELECT max(id+nbr) as id, month, type, sum(value) as value from (SELECT id, month, client_id, user_id, 'Rekrutacja' as type, value_invoice as value, 1 as nbr
                                FROM jp_report_sales2
                                WHERE month >= (to_char(localtimestamp - interval '12 months', 'YYYY') || '-M' || to_char(localtimestamp - interval '12 months', 'MM'))
            UNION
            SELECT id, month, client_id, user_id, 'Leasing' as type, value_leasing as value, 2 as nbr
                                FROM jp_report_sales2
                                WHERE month >= (to_char(localtimestamp - interval '12 months', 'YYYY') || '-M' || to_char(localtimestamp - interval '12 months', 'MM'))) as tab
            GROUP BY month, type
            ORDER BY month
                    
            )""")