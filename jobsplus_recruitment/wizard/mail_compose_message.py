# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from tools.translate import _
import pdb

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'
    _description = "Mail"
    
    _columns = {
        'candidate_email': fields.char('Candidate email', readonly=True)
    }

    def default_get(self, cr, uid, data, context=None):
        """
        This function gets default values
        """
        #pdb.set_trace()
        res = super(mail_compose_message, self).default_get(cr, uid, data, context=context)
        candidate_id = context and context.get('active_id', False) or False
        if candidate_id != False:
            candidate = self.pool.get('jp.candidate').browse(cr, uid, candidate_id)
            if not candidate.email:
                raise osv.except_osv(_('Błąd'), _('Kandydat nie ma adresu email!'))
            res.update({'candidate_email': candidate.email or False})        
        
        return res
    def send_mail_candidate(self, cr, uid, ids, context=None):
        send = self.browse(cr, uid, ids)[0]
        
        if not (send.body and send.subject):
            raise osv.except_osv(_('Błąd'), _('Musisz wypełnić temat i treść wiadomości.'))
        users_obj = self.pool.get('res.users')
        
        mail_to = send.candidate_email
        uid = users_obj.search(cr, uid, [('id','=',uid)])[0]
        uid_id = users_obj.browse(cr, uid, uid)
        
        email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
            
        vals = {'email_from': email_from,
                'email_to': mail_to,
                'state': 'outgoing',
                'subject': send.subject,
                'body_html': send.body,
                'auto_delete': True}
                
        self.pool.get('mail.mail').create(cr, uid, vals, context=context)