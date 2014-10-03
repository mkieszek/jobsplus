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


class jp_invoice(osv.Model):
    _name = "jp.invoice"
    _inherit = 'mail.thread'
    _description = 'Invoice'
    
    def _amount_gross(self, cr, uid, ids, name, arg, context=None):
        #pdb.set_trace()     
        val = {}
        invoice_ids = self.browse(cr, uid, ids)
        for invoice in invoice_ids:
            val[invoice.id] = invoice.amount_net + invoice.amount_vat
            
        return val
        
    _columns = {
        'name': fields.char('Invoice', required=True),
        'supplier': fields.many2one('res.partner', 'Supplier', required=True, ondelete='cascade'),
        'adress': fields.char('Adress'),
        'regon': fields.char('Regon'),
        'nip': fields.char('NIP'),
        'bank_number': fields.char('Bank account number'),
        'date_of_invoice': fields.date('Date of invoice'),
        'date_of_payment': fields.date('Date of payment'),
        'amount_net': fields.integer('Amount Net'),
        'amount_vat': fields.integer('Amount Vat'),
        'amount_gross': fields.function(_amount_gross, type="integer", string='Amount gross', readonly=True),
        'payment_type' : fields.selection([('1','Transfer'),('2','Cash')],'Payment type'),
        'document_type' : fields.selection([('1','Receipt'),('2','Invoice'),('3','Bill')],'Document type'),
        'service': fields.char('Name service'),
    }
    
    def create(self, cr, uid, vals, context=None):
        invoice_id = super(jp_invoice, self).create(cr, uid, vals, context=context)
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Dyrektor Administracji Jobs Plus')])
        user_ids = self.pool.get('res.users').search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
        for user in self.pool.get('res.users').browse(cr ,uid, user_ids):
            self.message_subscribe(cr, uid, [invoice_id], [user.partner_id.id], context=context)

        invoice = self.browse(cr, uid, invoice_id)
        subject = _("Odoo - Dodano nową fakturę")
        body = _("Dodano nową fakturę kosztową<br/>Dostawca: %s <br/>Data płatności: %s <br/>Kwota Netto: %s")\
                %(invoice.supplier.name, invoice.date_of_payment, invoice.amount_net)

        self.message_post(cr, uid, invoice.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                parent_id=False, attachments=None, context=context, content_subtype='html')
            
        return invoice_id
    
    def notification_deadline_payment(self, cr, uid, context=None):
        groups_obj = self.pool.get('res.groups')
        users_obj = self.pool.get('res.users')
        today = datetime.date.today()
        tomorrow = today + timedelta(days = 1)
        invoice_ids = self.search(cr, uid, [('date_of_payment','=',tomorrow)])
        if invoice_ids:
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
    
            group_id = groups_obj.search(cr, uid, [('name','=','Dyrektor Administracji Jobs Plus')])
            users = groups_obj.browse(cr, uid, group_id[0]).users
            mail_to = ''
            for user in users:
                if user.email != False:
                    mail_to += user.email+', '
            if mail_to != '':
                for invoice in self.browse(cr, uid, invoice_ids):
                    url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.invoice")%(jp_crm, cr.dbname, invoice.id)
                    subject = _("Odoo - Termin zapłaty faktury: %s")%(invoice.name)
                    body = _("Uwaga, mija termin zapłaty faktury: %s<br/>Dostawca: %s <br/>Data płatności: %s <br/>Kwota Netto: %s<br/><a href='%s'>Link do faktury</a>")\
                            %(invoice.name, invoice.supplier.name, invoice.date_of_payment, invoice.amount_net, url)
                    uid_id = users_obj.browse(cr, uid, uid)
                    vals = {'email_from': uid_id.partner_id.name+"<"+uid_id.partner_id.email+">",
                            'email_to': mail_to,
                            'state': 'outgoing',
                            'subject': subject,
                            'body_html': body,
                            'auto_delete': True}
                            
                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
                        
    def on_change_gross(self, cr, uid, ids, amount_vat, amount_net, context=None):
        value = {
            'amount_gross': amount_net + amount_vat
        }
        return {'value': value}
        
    def on_change_supplier(self, cr, uid, ids, supplier, context=None):
        #pdb.set_trace()
        partner = self.pool.get('res.partner').browse(cr, uid, supplier)
        if partner.bank_number != False:
            bank_number = partner.bank_number
        else:
            bank_number = ''
        values  = {
            'bank_number': bank_number,
        }
        
        return {'value' : values}