# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:10:54 2013

@author: mkieszek
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = "Klient"
    
    def _get_group_id(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        
        for partner in self.browse(cr, uid, ids, context=context):
            
            
            if(partner.is_group):
                res[partner.id] = partner.id
            else:
                res[partner.id] = None
        return res
        
    _columns = {
        'deal_ids': fields.one2many('jp.deal','client_id', 'Deals'),    
        'offer_ids': fields.one2many('jp.offer','client_id','Offers'),
        'contract_ids': fields.one2many('jp.contract','client_id','Contract'),
        'group_ids': fields.many2many('res.partner',
                 'res_partner_partner_rel',
                 'group_id',
                 'partner_id',
                 'Groups'),
         'is_group': fields.boolean('Is Group'),
         'group_id' : fields.function(_get_group_id, type="char", string="Group Id"),
    }
    
    def create(self, cr, uid, vals, context=None):
        #pdb.set_trace()
        if not self.search(cr, uid, [('name','=',vals['name'])]):
            partner_id = super(res_partner, self).create(cr, uid, vals, context=context)
        else:
            raise osv.except_osv(_('Błąd'), _('Klient o tej nazwie już istnieje!'))
        
        return partner_id