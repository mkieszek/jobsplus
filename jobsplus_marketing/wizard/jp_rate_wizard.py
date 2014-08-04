# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from tools.translate import _
import pdb
import uuid

class jp_rate_wizard(osv.osv_memory):
    _name = 'jp.rate.wizard'
    _columns = {
        'name': fields.char("Name"),
        'send_to': fields.selection([('1','Client'),('2','Candidates')],'Send to', required=True),
        'contact_id': fields.many2one('res.partner','Contact'),
        'application_ids' : fields.many2many('jp.application', 'jp_application_rel','rate_id','application_id', 'Applications'),
        'deal_id': fields.many2one('jp.deal','Deal'),
        'client_id': fields.many2one('res.partner', 'Client'),
    }
    
    def rate_candidates(self, cr, uid, ids, context=None):
        applications = self.browse(cr, uid, ids)[0].application_ids
        deal_id = context and context.get('active_id', False) or False
        deal = self.pool.get('jp.deal').browse(cr, uid, deal_id)
        application_ids = []
        mail_to = ""
        
        if applications:
            for application in applications:
                if application.candidate_id.email:
                    mail_to += application.candidate_id.email+" "
                    application_ids.append(application.id)
                else:
                    raise osv.except_osv(_('Błąd'), _('Kandydat '+application.candidate_id.candidate+' nie ma adresu email!'))
                
        else:
            raise osv.except_osv(_('Błąd'), _('Musisz wybrać aplikację!'))
    
        application_obj = self.pool.get('jp.application')
        for application_id in application_ids:
            vals = {}
            vals = {
                'candidate_id': application_obj.browse(cr, uid, application_id).candidate_id.id,
                'application_id': application_id,
                'deal_id': deal.id,
                'name': deal.name+"-"+application_obj.browse(cr, uid, application_id).candidate_id.candidate,
                'state': '1',
            }
            
            self.pool.get('jp.candidate.rate').create(cr, uid, vals, context=None)
            
        return True
        
    def rate_clients(self, cr, uid, ids, context=None):
        contact = self.browse(cr, uid, ids)[0].contact_id
        deal_id = context and context.get('active_id', False) or False
        deal = self.pool.get('jp.deal').browse(cr, uid, deal_id)
        
        if contact:
            mail_to = ""
            if contact.email:
                mail_to += contact.email
                vals = {}
                vals = {
                    'client_id': contact.id,
                    'deal_id': deal.id,
                    'name': deal.name+"-"+contact.name,
                    'state': '1',
                }
                
                self.pool.get('jp.client.rate').create(cr, uid, vals, context=None)
                
            else:
                raise osv.except_osv(_('Błąd'), _('Wybrany klient nie ma adresu email!'))
        else:
            raise osv.except_osv(_('Błąd'), _('Musisz wybrać klienta!'))
        
        return True
        
    def default_get(self, cr, uid, deal_id, context=None):
        """
        This function gets default values
        """
        res = super(jp_rate_wizard, self).default_get(cr, uid, deal_id, context=context)
        deal_id = context and context.get('active_id', False) or False
        client_id = self.pool.get('jp.deal').browse(cr, uid, deal_id).client_id.id
        res.update({'deal_id': deal_id or False})
        res.update({'client_id': client_id or False})
        
        return res