# -*- coding: utf-8 -*-
"""
Created on Mon May 27 21:51:03 2013

@author: mkieszek
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import jp_deal_stage
import pdb
import datetime
from datetime import timedelta

PERIOD_TYPES = [
    ('day', 'Day'),
    ('week', 'Week'),
    ('month', 'Month'),
    ('year', 'Year')
]

class jp_deal(osv.Model):
    _name="jp.deal"
    _inherit="mail.thread"
    _description = 'Deal'    
    _columns={
        'name': fields.char('Deal Reference', size=64, required=True, readonly=True, select=True),
        'title' : fields.char('Title', size=64, required=True, track_visibility='onchange'),
        'client_id' : fields.many2one('res.partner', 'Client', track_visibility='onchange', required=True),
        #'sales_rep' : fields.many2one('res.users', 'Sales rep', track_visibility='onchange', required=True),
        'task_ids': fields.one2many('project.task', 'deal_id', 'Tasks'),
        'contract_id' : fields.many2one('jp.contract', 'Contract',track_visibility='onchange', required=True),                           
        'handover_date' : fields.date('Handover date', track_visibility='onchange'),        
        'decision_time' : fields.integer('Decision time (days)', track_visibility='onchange'),
        'invoice_date' :  fields.date('Invoice date', track_visibility='onchange'),
        'payment_term': fields.char( 
                                        'Payment Terms', track_visibility='onchange'),
        'warranty_period' : fields.integer('Warranty',
                                    required=True, 
                                    track_visibility='onchange'),
                                    
        'warranty': fields.boolean('Has warranty', track_visibility='onchange'),
        'warranty_period_type' : fields.selection(PERIOD_TYPES, 'Period type'),
        'probability': fields.float('Success Rate (%)',group_operator="avg"),
        'planned_revenue': fields.float('Expected Revenue', track_visibility='onchange'),
        'currency_id': fields.many2one('res.currency', 'Currency', track_visibility='onchange'),
        'product_id' : fields.many2one('product.product', 'Product'),
        
        #fields for base_stage
        'date_open': fields.datetime('Opened', readonly=True),
        'date_closed': fields.datetime('Closed', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesperson', select=True, track_visibility='onchange'),
        'partner_id': fields.many2one('res.partner'
                                        , 'Partner'
                                        , ondelete='set null'
                                        , track_visibility='onchange'
                                        , select=True),
        'stage_id': fields.many2one('jp.deal.stage', 'Stage', help='Current stage of the offer', ondelete="set null"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=jp_deal_stage.AVAILABLE_STATES, string="Status", readonly=True,),
        'active': fields.boolean('Active', required=False, track_visibility='onchange'),
        'color': fields.integer('Color index'),
        'create_date' : fields.date('Create Date', readonly=True),

    }
    
    _defaults = {
        'active': 1,
        'user_id': lambda s, cr, uid, c: uid,
        'name': lambda obj, cr, uid, context: '/',
        'color' : 0,
    }

    def name_get(self, cr, uid, ids, context=None):
         """Overrides orm name_get method"""
         if not isinstance(ids, list) :
             ids = [ids]
         res = []
         if not ids:
             return res
        
         reads = self.read(cr, uid, ids, ['name', 'title'], context)

         for record in reads:
             name = record['name']
             title = record['title']
             res.append((record['id'], name + ' - ' + title))
         return res
        
    
    
    def create(self, cr, uid, vals, context=None):
        #pdb.set_trace()
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.deal') or '/'
            
        stage_id = self.pool.get('jp.deal.stage').search(cr, uid, [('state','=','draft')], context=context)[0]
        
        stage = self.pool.get('jp.deal.stage').browse(cr, uid, stage_id, context=context)

        vals['active'] = True
        vals['stage_id'] = stage_id
        vals['probability'] = stage.probability
        
        deal_id = super(jp_deal, self).create(cr, uid, vals, context=context)
        deal = self.browse(cr, uid, deal_id, context=context)
        
        self.message_subscribe(cr, uid, [deal_id], [deal.user_id.partner_id.id], context=context)

        user_ids = []
        group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Kierownik Rekrutacji Jobs Plus')])
        user_ids = self.pool.get('res.users').search(cr,uid,[('groups_id','in',group_id),('id','!=',1)])
        users_obj = self.pool.get('res.users').browse(cr, uid, user_ids)
        for user in users_obj:        
            self.message_subscribe(cr, uid, [deal_id], [user.partner_id.id], context=context)
            
        deal = self.pool.get('jp.deal').browse(cr, uid, [deal_id])[0]
        
        config_obj = self.pool.get('jp.config.settings')
        jp_crm = config_obj.current_jp_settings(cr, uid, 'jobsplus_crm')
        url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, deal.id)
        subject = _("Odoo - New Deal created: %s")%(deal.title)
        body = _('New Deal created: %s <br/>Customer: %s<br/>Sales rep: %s<br/><a href="%s">Link to Deal</a>')%(deal.title,deal.client_id.name,deal.user_id.name,url)
        
        self.pool.get('jp.deal').message_post(cr, uid, deal_id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
        
        
        #self.message_post(cr, uid, [deal_id], 
        #                  body=_('Deal %s has been created!') %(deal.name), context=context)
        
        return deal_id
    
    def on_change_contract(self, cr, uid, ids, contract_id, context=None):
        values = {}
        if contract_id:
            contract = self.pool.get('jp.contract').browse(cr, uid, contract_id, context=context)
            values = {
                'product_id' : contract.product_id and contract.product_id.id or False,
                'payment_term' : contract.payment_term and contract.payment_term.id or False,
                'warranty_period' : contract.warranty_period,
                'warranty' : contract.warranty,
                'warranty_period_type' : contract.warranty_period_type,
            }
        return {'value' : values}
        
    def on_change_stage(self, cr, uid, ids, stage_id, context=None):
        
        values = {}
        
        stage = self.pool.get('jp.deal.stage').browse(cr, uid, stage_id, context=context)

        values = {
                'stage_id' : stage_id,
                'probability' : stage.probability,
        }
        
        return {'value' : values}
        
    def open_line(self, cr, uid, id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deal', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.pool.get('jp.candidate')._name,
            'res_id': id[0],
            'target': 'self',
        }

    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            #name = name.split(' / ')[-1]
            name_ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            title_ids = self.search(cr, uid, [('title', operator, name)] + args, limit=limit, context=context)
            ids=name_ids+title_ids
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        if ids:
            today = datetime.date.today()
            
            selects = ['Do fakturowania','Zafakturowany','Zapłacony','Wygrany','Przegrany']
            
            stage_obj = self.pool.get('jp.deal.stage')
            for select in selects:
                stage = stage_obj.search(cr, uid, [('name','=',select)])
                stage_id = stage_obj.browse(cr, uid, stage)[0].id
        
                if vals.has_key('stage_id')==True:
                    if int(vals['stage_id']) == stage_id:
                        vals['date_closed'] = today
                
            deal_id = super(jp_deal, self).write(cr, uid, ids, vals, context=context)

            deal = self.browse(cr, uid, ids)[0]
            if 'stage_id' in vals or 'recruiter_id' in vals:
                value = {
                    'deal_id': ids[0],
                    'stage_id': deal.stage_id.id,
                    'date_cr': today,
                }
                if deal.recruiter_id:
                    value['recruiter_id'] = deal.recruiter_id.id
                stage_id = self.pool.get('jp.deal.stage.history').create(cr, uid, value, context=None)
            
            #komunikat do zmiany statusu
            if 'stage_id' in vals:
                subject = _("Odoo - Zmieniono status Deal'a")
                body = _("Zmieniono status Deal'a: %s<br/>Aktualny status to: %s")%(deal.name, deal.stage_id.name)
                self.message_post(cr, uid, deal.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                            parent_id=False, attachments=None, context=context, content_subtype='html')
                
            stage_invoice = stage_obj.search(cr, uid, [('name','=','Do fakturowania')])
            if 'stage_id' in vals and vals['stage_id']==stage_invoice[0]:
                users_obj = self.pool.get('res.users')
                group_obj = self.pool.get('res.groups')
                group_id = group_obj.search(cr,uid,[('name','=','Dyrektor Administracji Jobs Plus')])
                users = group_obj.browse(cr, uid, group_id)[0].users
                mail_to = ""
                for user in users:
                    if user.partner_id.email is not False and user.active is True:
                        mail_to += user.partner_id.email + ", "
                if mail_to is not "":
                    config_obj = self.pool.get('jp.config.settings')
                    jp_crm = config_obj.current_jp_settings(cr, uid, 'jobsplus_crm')
                    url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, ids[0])
                    
                    subject = _("Odoo - Deal: %s ma status do fakturowania")%(deal.title)
                    body = _("Zmienion status deala na do fakturowania.<br/>Deal: %s<br/>Klient: %s<br/>Przewidywany dochód: %s<br/>Sprzedawca: %s<br/><a href='%s'>Link do Deal'a</a>")\
                            %(deal.title,deal.client_id.name,deal.planned_revenue,deal.user_id.name,url)
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
            return deal_id
        else:
            return False
    
    def create_report(self, cr, uid, ids, context=None):
        self.pool.get('jp.report.sales2').calculate_report_sales(cr, uid, context=None)
        