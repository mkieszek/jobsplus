# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 08:50:52 2013

@author: mbereda
"""

from datetime import timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import datetime


class jp_agreement_supplier(osv.Model):
    _name = "jp.agreement.supplier"
    _inherit = 'mail.thread'
    _description = _("Agreement with supplier")
    _columns = {
        'name': fields.char('Agreement', required=True),
        'supplier': fields.many2one('res.partner', 'Supplier', required=True, ondelete='cascade'),
        'date_of_contract': fields.date('Date of contract'),
        'contract_to': fields.date('Contract to'),
        'service': fields.char('Name service'),
        'type_of_agreement': fields.selection([('1','Fixed-term'),('2','Indefinite term')],'Type of agreement', required=True),
    }
    
    def create(self, cr, uid, vals, context=None):
        agreement_id = super(jp_agreement_supplier, self).create(cr, uid, vals, context=context)
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Dyrektor Administracji Jobs Plus')])
        user_ids = self.pool.get('res.users').search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
        for user in self.pool.get('res.users').browse(cr ,uid, user_ids):
            self.message_subscribe(cr, uid, [agreement_id], [user.partner_id.id], context=context)
            
        return agreement_id
    
    def notification_deadline_agreement_supplier(self, cr, uid, context=None):
        today = datetime.date.today()
        tomorrow = (today + timedelta(days = 14)).strftime("%Y-%m-%d")
        agreement_ids = self.search(cr, uid, [('contract_to','=',tomorrow)], context=None)
        agreements = self.browse(cr, uid, agreement_ids)

        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
        
        for agreement in agreements:
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.agreement.supplier")%(jp_crm, cr.dbname, agreement.id)
            subject = _("Odoo - Zakończenie umowy z dostawcą")
            body = _("Zakończenie umowy z dostawcą: %s<br/>Data zakończenia: %s<br/><a href='%s'>Link do umowy</a>")%(agreement.supplier.name,agreement.contract_to,url)
    
            self.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                    parent_id=False, attachments=None, context=context, content_subtype='html')