# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 12:06:12 2013

@author: mbereda
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import datetime
from datetime import timedelta

class jp_deal(osv.Model):
    _inherit='jp.deal'
    
    def _application_count(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()
        res = dict(map(lambda x: (x,{'application_count': 0}), ids))
        # the user may not have access rights for opportunities or meetings
        try:
            for deal in self.browse(cr, uid, ids, context):
                res[deal.id] = {
                    'application_count': len(deal.application_ids),
                }
        except:
            pass
        return res
        
    def _document_ids_get(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        if context is None:
            context = {}
        
        res = {}
        for candidate in self.browse(cr, uid, ids, context=context):
            attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','jp.deal'),('res_id','=',candidate.id)], context=context)
            #attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','jp.candidate')], context=context)
                        
            res[candidate.id] = attachment_ids
        
        return res

    _columns={
            'date_middle': fields.date('Middle date', track_visibility='onchange'),
            'deal_state': fields.many2one('res.country.state', 'Work state'),
            'deal_country': fields.char('Country',Size=64),
            'recruiter_id': fields.many2one('res.users', 'Recruiter', select=True, track_visibility='onchange'),
            'recruiter_ids' : fields.many2many('res.users', 'jp_deal_recruiters_rel','deal_id','res_users', 'Recruiter assistant'),
            'application_count': fields.function(_application_count, string="Applications #", type='integer', multi='opp_meet'),
            'application_ids' : fields.one2many('jp.application', 'deal_id', 'Applications'),
            'ad_ids': fields.one2many('jp.ad', 'deal_id', 'Ads'),
            'calculation_ids' : fields.one2many('jp.calculation', 'deal_id', 'Calculations'),
            'project_ids' : fields.one2many('jp.project', 'deal_id', 'Projects'),
            'document_ids': fields.function(_document_ids_get, type="one2many",relation="ir.attachment", string="Document"),
            #'client_rate_id': fields.one2many('jp.client.rate', 'deal_id', 'Client rate'),
            #'candidate_rate_id': fields.one2many('jp.candidate.rate', 'deal_id', 'Candidate rate'),
            'color_2': fields.integer('Color index'),
    }
    
    def list_deal_get(self, cr, uid):
        result = []  
        deal_ids = self.search(cr, uid, [('state','in',['draft','open','pending'])])
        for deal in self.browse(cr, uid, deal_ids):
            result.append((deal.id, "%s - %s"%(deal.name, deal.title)))
    
        return result

    def write(self, cr, uid, ids, vals, context=None):
        deal_id = super(jp_deal, self).write(cr, uid, ids, vals, context=context)
        
        for deal in self.browse(cr, uid, ids):
            if deal.recruiter_ids:
                for recruiter in deal.recruiter_ids:
                    recruiter = self.pool.get('res.users').browse(cr, uid, [recruiter.id])[0]
                
                    self.message_subscribe(cr, uid, ids, [recruiter.partner_id.id], context=context)
                
        if 'stage_id' in vals:
            stage_obj = self.pool.get('jp.deal.stage')
            stage = stage_obj.browse(cr, uid, vals['stage_id'])
            if stage.name == 'Wstrzymany':
                ad_obj = self.pool.get('jp.ad')
                ad_ids = ad_obj.search(cr, uid, [('deal_id','=',ids[0])])
                vals_ad = {}
                vals_ad['activity'] = False
                ad_obj.write(cr, uid, ad_ids, vals_ad)
        
        return deal_id
    def open_line_ad_form(self, cr, uid, id, context=None):
        #pdb.set_trace()
        if context==None:
            context = {}
        context['default_deal_id'] = id[0]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ad', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('jp.ad')._name,
            #'res_id': id[0],
            #'target': 'current',
            'context': context,
        }
        
    def notification_middle_handover_date(self, cr, uid, context=None):
        tomorrow = datetime.date.today()+timedelta(days=1)
        
        config_obj = self.pool.get('jp.config.settings')
        jp_crm = config_obj.current_jp_settings(cr, uid, 'jobsplus_crm')
        
        deal_ids = self.search(cr, uid, [('date_middle','=',tomorrow)])
        subject = _("Data środkowa Deal'a")
        for deal in self.browse(cr, uid, deal_ids):
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, deal.id)
            body = _("Odoo - Zbliża się termin daty środkowej rekrutacji: %s<br/><a href='%s'>Link do Deal'a</a>")%(deal.name, url)
            self.message_post(cr, uid, deal.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
        
        deal_ids = self.search(cr, uid, [('handover_date','=',tomorrow)])
        subject = _("Data przekazania Deal'a")
        for deal in self.browse(cr, uid, deal_ids):
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, deal.id)
            body = _("Odoo - Zbliża się termin daty przekazania rekrutacji: %s<br/><a href='%s'>Link do Deal'a</a>")%(deal.name, url)
            self.message_post(cr, uid, deal.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
          
        return True
    
    def open_line_calculation_form(self, cr, uid, id, context=None):
        if context==None:
            context = {}
        context['default_deal_id'] = id[0]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Calculation', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('jp.calculation')._name,
            'context': context,
        }
        