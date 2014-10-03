# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 09:48:26 2013

@author: mbereda
"""

from openerp.osv import osv,fields
from openerp.tools.translate import _
import pdb
import datetime

class jp_recruiter2deal(osv.Model):
    _name = 'jp.recruiter2deal'
    
    _columns = {
            'deal_id': fields.many2one('jp.deal','Deal', readonly=True),       
            'recruiter_id': fields.many2one('res.users', 'Recruiter', required=True, domain=[('groups_id.name','in',['Rekruter Jobs Plus']),['id','!=',1]]),
            'date_middle': fields.date('Middle date', track_visibility='onchange'),
            'handover_date': fields.date('Handover date', track_visibility='onchange'),
    }
    
    def default_get(self, cr, uid, deal_id, context=None):
        """
        This function gets default values
        """
        res = super(jp_recruiter2deal, self).default_get(cr, uid, deal_id, context=context)
        deal_id = context and context.get('active_id', False) or False
        res.update({'deal_id': deal_id or False})

        deal = self.pool.get('jp.deal').browse(cr,uid,[deal_id], context=context)[0]
        recruiter_id = deal.recruiter_id and deal.recruiter_id.id or False
        res.update({'recruiter_id': recruiter_id})
        
        date_middle = deal.date_middle
        res.update({'date_middle': date_middle})
        
        res.update({'handover_date': deal.handover_date})
        
        return res
        
    def assign_recruiter(self, cr, uid, deal_id, context=None):
        #pdb.set_trace()
        w = self.browse(cr, uid, deal_id, context=context)[0]
        
        deal_id = context and context.get('active_id', False) or False
        
        values = {
            'recruiter_id': w.recruiter_id and w.recruiter_id.id or False,
            'date_middle': w.date_middle,
            'handover_date': w.handover_date,
        }
        recruiter_id = w.recruiter_id.id
        recruiter = self.pool.get('res.users').browse(cr, uid, [recruiter_id])[0]
        
        deal_obj = self.pool.get('jp.deal')
        deal_obj.write(cr, uid, [deal_id], values, context=context)
        
        mail_to = recruiter.email
        if mail_to is not "":
            deal = deal_obj.browse(cr, uid, deal_id)
            users_obj = self.pool.get('res.users')
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, deal.id)
            
            subject = "Recruiter %s assigned to deal %s"
            body = "Recruiter has been assigned to deal.<br/>Recruiter: %s<br/>Deal: %s<br/>Middle date: %s<br/>Finish date: %s<br/><a href='%s'>Link to Deal</a>"
                                                
            uid = users_obj.search(cr, uid, [('id','=',1)])[0]
            uid_id = users_obj.browse(cr, uid, uid)

            translation_obj = self.pool.get('ir.translation')        
            if w.recruiter_id.partner_id.lang == 'pl_PL':
                transl = translation_obj.search(cr, uid, [('src','=',body)])
                transl_sub = translation_obj.search(cr, uid, [('src','=',subject)])
                if transl:
                    trans = translation_obj.browse(cr, uid, transl)[0]
                    body = trans.value
                if transl_sub:
                    trans_sub = translation_obj.browse(cr, uid, transl_sub)[0]
                    subject = trans_sub.value
                    
            email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
                
            vals = {'email_from': email_from,
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': subject % (w.recruiter_id.name, deal.title),
                    'body_html': body % (deal.recruiter_id.name, deal.name, deal.date_middle, deal.handover_date, url),
                    'auto_delete': True}
                    
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)