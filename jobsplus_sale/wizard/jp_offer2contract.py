# -*- coding: utf-8 -*-
"""
Created on Fri May 24 11:43:41 2013

@author: mkieszek
"""
from openerp.osv import osv,fields
from openerp.tools.translate import _
import pdb

PERIOD_TYPES = [
    ('day', 'Day'),
    ('week', 'Week'),
    ('month', 'Month'),
    ('year', 'Year')
]
class jp_offer2contract(osv.osv_memory):
    _name = 'jp.offer2contract'
    _description = 'Offer to Contract'    
    _columns = {
        'client_id' : fields.many2one('res.partner', 'Client', readonly=True),
        'contract_date' : fields.date('Contract date', required=True),
        'termination_date' : fields.date('Termination date'),
        'dismiss_period' : fields.integer('Dismissal period (days)', required=True),
        'contract_type' : fields.selection([('fixed', 'Fixed-term'), ('indefinite', 'Indefinite term')], 
                                   'Term type', required=True,),
        'payment_term': fields.many2one('account.payment.term', 'Payment Terms'),
        'warranty_period' : fields.integer('Warranty'),
        'offer_id' : fields.many2one('jp.offer', 'Offer', readonly=True),
        'prospect_id' : fields.many2one('crm.lead', 'Prospect', readonly=True),
        'product_id' : fields.many2one('product.product', 'Product', readonly=True),
        'warranty_period_type' : fields.selection(PERIOD_TYPES, 'Period type'),
        'dismiss_period_type' : fields.selection(PERIOD_TYPES, 'Period type',),
        'warranty': fields.boolean('Has warranty'),
    }
    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        #pdb.set_trace()
        
        res = super(jp_offer2contract, self).default_get(cr, uid, fields, context=context)
        record_id = context and context.get('active_id', False) or False
        
        if record_id:
            offer = self.pool.get('jp.offer').browse(cr, uid, record_id, context=context)
            if 'offer_id' in fields:
                res.update({'offer_id': offer.id or False})
            if 'client_id' in fields:
                res.update({'client_id': offer.client_id and offer.client_id.id or False})
            if 'prospect_id' in fields:
                res.update({'prospect_id': offer.prospect_id and offer.prospect_id.id or False})
            if 'product_id' in fields:
                res.update({'product_id': offer.product_id and offer.product_id.id or False})
        return res
        
    def action_apply(self, cr, uid, ids, context=None):
        """
        Convert offer to contract and create client from prospect.
        Close prospect and all scheduled phone calls 
        """
        if context is None:
            context = {}

        w = self.browse(cr, uid, ids, context=context)[0]
        
        partner_id = -1        
        
        if w.client_id:
            partner_id = w.client_id.id
        if w.prospect_id:
            
            partner_id = self._create_partner(cr, uid, ids, context)[w.prospect_id.id]
            lead = self.pool.get('crm.lead')
            lead.case_mark_won(cr, uid, [w.prospect_id.id], context=context)
            
            vals_partner = {
                'phone': w.prospect_id.main_phone,
                'website': w.prospect_id.website,
                'prospect_id': w.prospect_id.id,
            }
            
            self.pool.get('res.partner').write(cr, uid, [partner_id], vals_partner, context=context)
        
        vals_contract = {
            'client_id': partner_id,
            'contract_date': w.contract_date,
            'dismiss_period': w.dismiss_period,
            'message_follower_ids': False,
            'message_ids': False,
            'notes': False,
            'payment_term': w.payment_term and w.payment_term.id or False,
            'product_id': w.product_id and w.product_id.id or False,
            'sales_rep': uid,
            'stage_id': False,
            'termination_date': w.termination_date,
            'type': w.contract_type,
            'warranty': w.warranty,
            'active' : True,
            'ref_offer' : w.offer_id and w.offer_id.id or False,
            'warranty_period_type': w.warranty_period_type,
            'dismiss_period_type': w.dismiss_period_type,
            'warranty_period': w.warranty_period,
        }
        
        if vals_contract['product_id'] == False:
            raise osv.except_osv(_('Błąd'), _('Prospekt musi mieć produkt !'))
            
        contract_id = self.pool.get('jp.contract').create(cr, uid, vals_contract, context=context)

    
        offer = self.pool.get('jp.offer')
        
        offer.case_close(cr, uid, [w.offer_id.id], context)
        
        return {'type': 'ir.actions.act_window_close'}
                                        
        
        #opp_ids = [o.id for o in w.opportunity_ids]
        #if w.name == 'merge':
        #    lead_id = self.pool.get('crm.lead').merge_opportunity(cr, uid, opp_ids, context=context)
        #    lead_ids = [lead_id]
        #    lead = self.pool.get('crm.lead').read(cr, uid, lead_id, ['type'], context=context)
        #    if lead['type'] == "lead":
        #        context.update({'active_ids': lead_ids})
        #        self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)
        #else:
        #    lead_ids = context.get('active_ids', [])
        #    self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)

        #return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, lead_ids[0], context=context)

    def _create_partner(self, cr, uid, ids, context=None):
        """
        Create partner based on action.
        :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by crm_lead2opportunity_partner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        
        if context is None:
            context = {}
        lead = self.pool.get('crm.lead')
        lead_ids = context.get('active_ids', [])
        data = self.browse(cr, uid, ids, context=context)[0]
        return lead.handle_partner_assignation(cr, uid, [data.prospect_id.id], 'create', False, context=context)
    
    def on_change_type(self, cr, uid, ids, contract_type, context=None):
        values = {}
        if contract_type == 'indefinite':
            values = {
                'termination_date': False
            }
        return {'value' : values}    
    
    