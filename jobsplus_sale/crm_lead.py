# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import pdb

AVAILABLE_STATES = [
    ('draft', 'New'),
    ('cancel', 'Cancelled'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Closed')
]


class crm_lead(osv.osv):
    _inherit = 'crm.lead'
    _description = "Prospekt"
    _order = "create_date desc"
              
    _columns = {
        'task_ids': fields.one2many('project.task', 'lead_id', 'Tasks'),
        'product_id': fields.many2one('product.product', 'Product'
                                        ,track_visibility='onchange'
                                        , ondelete="set null"),
        'website': fields.char('Web site', size=255),
        'main_phone': fields.char('Main phone', size=25),
        'offer_ids': fields.one2many('jp.offer','prospect_id','Offers'),
        
        'state': fields.related('stage_id', 'state', type="selection", store=False,
                selection=AVAILABLE_STATES, string="Status", readonly=True, select=True),
    }
    
    def on_change_partner_name(self, cr, uid, ids, partner_name, context=None):
        values = {}
        if(partner_name):        
            if len(partner_name) > 3:
                values = {
                    'name': partner_name,
                    }
        return {'value' : values}
    
    def case_cancel(self, cr, uid, ids, context=None):
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.pool.get('crm.case.stage').search(cr, uid, [('sequence','=',30)])
            self.write(cr, uid, lead.id, {'stage_id': stage_id[0]}, context=context)
        return True
    
    def case_mark_won2(self, cr, uid, ids, context=None):
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.pool.get('crm.case.stage').search(cr, uid, [('sequence','=',130)])
            self.write(cr, uid, lead.id, {'stage_id': stage_id[0]}, context=context)
        return True


class crm_case_stage(osv.osv):
    _inherit = "crm.case.stage"

    _columns = {
        'state': fields.selection(AVAILABLE_STATES, 'Related Status', required=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
