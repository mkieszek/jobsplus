# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 10:55:38 2013

@author: pczorniej
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, timedelta
import datetime
import pdb

AVAILABLE_STATES = [
    ('1', 'New'),
    ('2', 'Approved'),
    ('3', 'Rejected')
]

class jp_application(osv.Model):
    _name = "jp.application"
    _inherit = 'mail.thread'
    _description = 'Aplikacje'
    _columns = {
        'name': fields.char('ID', size=64,
                            readonly=True),
        'deal_id': fields.many2one('jp.deal','Deal', required=True, ondelete="cascade"),
        #'stage_id': fields.many2one('jp.application.stage', 'Stage'),
        'candidate_id': fields.many2one('jp.candidate', 'Candidate', ondelete="cascade"),
        'note': fields.text('Notes'),
        'candidate': fields.related('candidate_id', 'candidate', type='char', string="Candidate", readonly=True),
        'status' : fields.selection(AVAILABLE_STATES, 'Status'),
        'create_date': fields.date('Create'),
    }
    
    _defaults = {
        'status' : '1',
    }
    _order = 'create_date desc'

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.application') or '/'
            
        application_id = super(jp_application, self).create(cr, uid, vals, context=context)
        
        return application_id
        
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        
        reads = self.read(cr, uid, ids, ['name', 'candidate'], context)
        for record in reads:
            name = record['name']
            title = record['candidate']
            res.append((record['id'], name + ' - ' + title))
        return res

        
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            #name = name.split(' / ')[-1]
            name_ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            candidate_ids = self.search(cr, uid, [('candidate_id', operator, name)] + args, limit=limit, context=context)
            ids=name_ids+candidate_ids
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
        
    def open_line_deal(self, cr, uid, id, context=None):
        #pdb.set_trace()
        application_obj = self.pool.get('jp.application').browse(cr, uid, id, context=context)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deal', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('jp.deal')._name,
            'res_id': application_obj[0].deal_id.id,
            'target': 'self',
        }
        
    def open_line_candidate(self, cr, uid, id, context=None):
        #pdb.set_trace()
        application_obj = self.pool.get('jp.application').browse(cr, uid, id, context=context)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Candidate', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('jp.candidate')._name,
            'res_id': application_obj[0].candidate_id.id,
            'target': 'self',
            'context': context,
        }
        
    """def open_candidate(self, cr, uid, id, context=None):
        #pdb.set_trace()
        application_obj = self.pool.get('jp.application').browse(cr, uid, id, context=context)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Candidate', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('jp.candidate')._name,
            'res_id': application_obj[0].candidate_id.id,
            'target': 'new',
            'context': context,
        }
        context = {
            'res_model': 'jp.candidate',
        }"""
        
    def new_applications(self, cr, uid, context=None):
        users_obj = self.pool.get('res.users')
        deal_obj = self.pool.get('jp.deal')
        yesterday = datetime.date.today()-timedelta(days=1)
        today = datetime.date.today()
        deal_list = {}
        application_ids = self.search(cr, uid, [('create_date','>',yesterday),('create_date','<',today)])
        
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
        
        for application in self.browse(cr, uid, application_ids):
            deal = application.deal_id.id
            if deal != False:
                if deal in deal_list:
                    deal_list[deal] += 1
                else:
                    deal_list[deal] = 1
        
        for deal_id, app_count in deal_list.items():
            deal = deal_obj.browse(cr, uid, deal_id)
            user = users_obj.browse(cr, uid, deal.recruiter_id.id)
            
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, deal.id)
            mail_to = ""
            if user.partner_id.email is not False and user.active is True:
                mail_to += user.partner_id.email + " "
            if mail_to is not "":
                subject = _("Nowe aplikacje do rekrutacji: %s")%(deal.title)
                body = _("Zostały dodane nowe aplikacje do deal'a: %s.<br/>Ilość nowych aplikacji to: %s<br/><a href='%s'>Link do Deal'a</a>")%(deal.title, app_count, url)
                uid = users_obj.search(cr, uid, [('id','=',1)])[0]
                uid_id = users_obj.browse(cr, uid, uid)
                
                email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
                    
                vals = {'email_from': email_from,
                        'email_to': mail_to,
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': body,
                        'auto_delete': True}
                        
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        
        return True
    
    def application_rejected(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        application = self.browse(cr, uid, ids)[0]
        vals = {}
        vals = {
                'status': '3', 
                }
        self.write(cr, uid, application.id, vals, context=None)
        
        return True
    def application_approved(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        application = self.browse(cr, uid, ids)[0]
        vals = {}
        vals = {
                'status': '2', 
                }
        self.write(cr, uid, application.id, vals, context=None)
        
        return True
