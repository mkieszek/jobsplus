# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = "Klienta"
   
    def _count_closed_deals(self, cr, uid, ids, name, arg, context=None):
        #pdb.set_trace()
        val = {}
        for partner in self.browse(cr, uid, ids):
            count = 0
            for deal in partner.deal_ids:
                if deal.state == 'done':
                    count += 1
            val[partner.id] = count
        
        return val
        
    def _amount_revenue(self, cr, uid, ids, name, arg, context=None):
        val = {}
        for partner in self.browse(cr, uid, ids):
            amount = 0.00
            for deal in partner.deal_ids:
                if deal.state == 'done' and deal.planned_revenue != 0 and deal.currency_id != False:
                    if deal.currency_id.name == "PLN":
                        amount += deal.planned_revenue
                    else:
                        if deal.currency_id.name == "EUR":
                            currency_obj = self.pool.get('res.currency')
                            pln_id = currency_obj.search(cr, uid, [('name','=','PLN')])[0]
                            
                            currency_rate_obj = self.pool.get('res.currency.rate')
                            pln_currency = currency_rate_obj.search(cr, uid, [('currency_id','=',pln_id)])
                            pln_rate = currency_rate_obj.browse(cr, uid, pln_currency)[0].rate
                            
                            amount += deal.planned_revenue * pln_rate
                        else:
                            currency_obj = self.pool.get('res.currency')
                            pln_id = currency_obj.search(cr, uid, [('name','=','PLN')])[0]
                            
                            currency_rate_obj = self.pool.get('res.currency.rate')
                            pln_currency = currency_rate_obj.search(cr, uid, [('currency_id','=',pln_id)])
                            pln_rate = currency_rate_obj.browse(cr, uid, pln_currency)[0].rate
                            
                            deal_currency_id = deal.currency_id.id
                            deal_currency = currency_rate_obj.search(cr, uid, [('currency_id','=',deal_currency_id)])
                            deal_rate = currency_rate_obj.browse(cr, uid, deal_currency)[0].rate
                            
                            euro_revenue = deal.planned_revenue / deal_rate
                            pln_revenue = euro_revenue*pln_rate
                            amount += pln_revenue
                        
            val[partner.id] = amount
        
        return val
        
    def _client_rate_ids(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        val = {}
        for client in self.browse(cr, uid, ids, context=context):
            deal_ids = self.pool.get('jp.deal').search(cr, uid, [('client_id','=',client.id)], context=context)
            client_rate_ids = self.pool.get('jp.client.rate').search(cr, uid, [('deal_id','in',deal_ids)], context=context)
                    
            val[client.id] = client_rate_ids
        
        return val
        
    _columns = {
        'closed_deals': fields.function(_count_closed_deals, type='integer', string="Count closed deals", readonly=True),
        'amount_revenue': fields.function(_amount_revenue, type="float", string="Amount revenue (PLN)", readonly=True),
        'client_rate_ids': fields.function(_client_rate_ids, type="one2many", relation='jp.client.rate', string='Rates'),
        'bank_number': fields.char('Bank account number'),
        'agreement_sup_ids': fields.one2many('jp.agreement.supplier','supplier', 'Supplier'),
        'invoice_ids': fields.one2many('jp.invoice', 'supplier', 'Supplier'),
    }
