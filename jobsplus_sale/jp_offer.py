# -*- coding: utf-8 -*-
"""
Created on Mon May 20 13:33:45 2013

@author: mkieszek
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import jp_offer_stage


class jp_offer(osv.Model):
    _name = "jp.offer"
    _inherit = 'mail.thread'
    _description = 'Oferte'
    _columns = {
        'name': fields.char('Offer Reference', size=64, required=True, readonly=True, select=True),
        'title' : fields.char('Title', size=64, required=True),
        'client_id' : fields.many2one('res.partner', 'Client', track_visibility='onchange'),
        'prospect_id' : fields.many2one('crm.lead', 'Prospect', track_visibility='onchange'),
        'product_id' : fields.many2one('product.product', 'Product', track_visibility='onchange'),
        'sent_date' : fields.date('Sent date', track_visibility='onchange'),
        'notes': fields.text('Notes'),
        'sales_rep' : fields.many2one('res.users', 'Sales rep', track_visibility='onchange'),
        
                                    
        #fields for base_stage
        'date_open': fields.datetime('Opened', readonly=True),
        'date_closed': fields.datetime('Closed', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesperson', select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner'
                                        , 'Partner'
                                        , ondelete='set null'
                                        , track_visibility='onchange'
                                        , select=True),
        'stage_id': fields.many2one('jp.offer.stage', 'Stage', track_visibility='onchange', help='Current stage of the offer', ondelete="set null"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=jp_offer_stage.AVAILABLE_STATES, string="Status", readonly=True,),
        'active': fields.boolean('Active', required=False),
        'task_ids': fields.one2many('project.task', 'offer_id', 'Tasks'),
        'color': fields.integer('Color Index'),
        'contract_id': fields.one2many('jp.contract', 'ref_offer', 'Contract'),

    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
        'active' : True,
        'color': 0,
        'sales_rep': lambda obj, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.offer') or '/'
        
        vals['stage_id'] = self.pool.get('jp.offer.stage').search(cr, uid, [('state','=','draft')], context=context)[0]
                
        offer_id = super(jp_offer, self).create(cr, uid, vals, context=context)
        offer = self.browse(cr, uid, offer_id, context=context)
        
        #self.message_post(cr, uid, [offer_id], body=_('Offer %s has been created!') %(offer.name), context=context)
        
        return offer_id
        
    def case_cancel(self, cr, uid, ids, context=None):
        """ Overrides case_cancel from base_stage to set probability """
        
        #res = super(jp_offer, self).case_cancel(cr, uid, ids, context=context)
        
        stage_done_ids = self.pool.get('jp.offer.stage').search(cr, uid, [('state','=','cancel')], context=context)
        #stage_done = offer_state.get_stage_done(cr, uid, context=context)
        
        self.write(cr, uid, ids, {'stage_id': stage_done_ids[0]}, context=context)  
        
        return True#res
    
    def case_close(self, cr, uid, ids, context=None):
        #res = super(jp_offer, self).case_close(cr, uid, ids, context=context)
        
        stage_done_ids = self.pool.get('jp.offer.stage').search(cr, uid, [('state','=','done')], context=context)
        #stage_done = offer_state.get_stage_done(cr, uid, context=context)
        
        self.write(cr, uid, ids, {'stage_id': stage_done_ids[0]}, context=context)        
        return True#res        
        
    def convert2deal(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, ids, context=context)[0]
        
        if w.contract_id:
            if w.client_id.id != False:
                contract_obj = self.pool.get('jp.contract')
                contract_id = contract_obj.browse(cr, uid, w.contract_id[0].id)
                vals_deal = {}
                vals_deal = {
                    'client_id': w.client_id.id,
                    'contract_id': w.contract_id[0].id,
                    'title': w.title,
                    'product_id' : contract_id.product_id and contract_id.product_id.id or False,
                    'payment_term' : contract_id.payment_term and contract_id.payment_term.id or False,
                    'warranty_period' : contract_id.warranty_period,
                    'warranty' : contract_id.warranty,
                    'warranty_period_type' : contract_id.warranty_period_type,
                    'user_id': uid,
                }
                
                self.pool.get('jp.deal').create(cr, uid, vals_deal, context=None)
            else:
                raise osv.except_osv(_('Błąd'), _('Oferta musi mieć klienta !'))
        else:
            raise osv.except_osv(_('Błąd'), _('Najpierw utwórz umowę !'))
        
        return True
