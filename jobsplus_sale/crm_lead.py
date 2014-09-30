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
        """ Overrides case_cancel from base_stage to set probability """
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False, [('probability', '=', 0.0), ('fold', '=', True)], context=context)
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                    _('Warning'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id}, context=context)
        return True


class crm_case_stage(osv.osv):
    _inherit = "crm.case.stage"

    _columns = {
        'state': fields.selection(AVAILABLE_STATES, 'Related Status', required=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
