# -*- coding: utf-8 -*-
"""
Created on Mon May 27 11:49:30 2013

@author: mkieszek
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta
import pdb
import time
import datetime

TASK_TYPES = [('call', 'Call'), ('email','Email'), ('meeting', 'Meeting'), ('document', 'Document'), ('administration', 'Administration'), ('recruitment','Recruitment')]
_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled')]

class project_task(osv.osv):
    _inherit = 'project.task'
    _order = 'deadline_datetime'
    _description = "Zadanie"
    
    _track = {
        'state': {
            'project.mt_task_new': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['new', 'draft'],
            'project.mt_task_started': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'open',
            'project.mt_task_closed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
        }
    }
    
    def _get_customer(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        if context is None:
            context = {}
        
        res = {}
        for task in self.browse(cr, uid, ids, context=context):
            client_id = None
            res[task.id] = {}
            if(task.partner_id):
                client_id = task.partner_id
            elif(task.deal_id):
                client_id = task.deal_id.client_id
            elif(task.offer_id):
                client_id = task.offer_id.client_id
            elif(task.contract_id):
                client_id = task.contract_id.client_id
            
            if(client_id):
                res[task.id] = client_id and client_id.id or False
            else:
                res[task.id] = None
        
        return res
    
    def _get_case_name(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = {}
        
        for task in self.browse(cr, uid, ids, context=context):
            case = None            
            if(task.partner_id):
                case = 'Partner'
            elif(task.deal_id):
                case = 'Deal'
            elif(task.offer_id):
                case = 'Offer'
            elif(task.contract_id):
                case = 'Contract'
            elif(task.lead_id):
                case = 'Prospect'
            
            if(case):
                res[task.id] = case
            else:
                res[task.id] = None
        
        return res
    
    def _get_client_name(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        
        res = {}
        
        for task in self.browse(cr, uid, ids, context=context):
            client_name = None
            res[task.id] = {}
            if(task.partner_id):
                client_name = task.partner_id.name
            elif(task.deal_id):
                client_name = task.deal_id.client_id.name
            elif(task.offer_id and task.offer_id.client_id):
                client_name = task.offer_id.client_id.name
            elif(task.offer_id and task.offer_id.prospect_id):
                client_name = task.offer_id.prospect_id.partner_name
            elif(task.contract_id and task.contract_id.client_id):
                client_name = task.contract_id.client_id.name
            elif(task.lead_id):
                client_name = task.lead_id.partner_name
            if(client_name):
                res[task.id] = client_name
            else:
                res[task.id] = None
        
        return res
        
    def _get_today(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()
        if context is None:
            context = {}
        
        res = {}
        
        now = datetime.datetime.now()
        start = now.strftime("%Y-%m-%d 00:00")
        end = now.strftime("%Y-%m-%d 23:59")
        start = datetime.datetime.strptime(start,"%Y-%m-%d %H:%M")
        end = datetime.datetime.strptime(end,"%Y-%m-%d %H:%M")
        
        for task in self.browse(cr, uid, ids, context=context):
            deadline_id = task.deadline_datetime
            
            if deadline_id:
                deadline_id = datetime.datetime.strptime(deadline_id,"%Y-%m-%d %H:%M:%S")
                
                if deadline_id > now and end > deadline_id:
                    color = 'green'
                else:
                    if now > deadline_id:
                        color = 'red'
                    else:
                        color = 'black'
            else:
                color = 'black'
                   
            res[task.id] = color
        
        return res
    
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead', readonly=True),
        'offer_id' :fields.many2one('jp.offer', 'Offer', readonly=True),
        'contract_id' : fields.many2one('jp.contract', 'Contract', readonly=True),
        'deal_id' : fields.many2one('jp.deal', 'Deal', readonly=True),
        'author_id': fields.many2one('res.users', 'Author', readonly=True),
        'client_id': fields.function(_get_customer, type="many2one",relation="res.partner", string="Client"),
        'case_name' : fields.function(_get_case_name, type="char", string="Case"),
        'task_type': fields.selection(TASK_TYPES, required=True, string="Type"),
        'deadline_datetime' : fields.datetime('Deadline'),
        'client_name': fields.function(_get_client_name, type="char", string="Customer"),
        'color':fields.function(_get_today, string='Color', type="char"),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True, select=True),
    }
    
    _defaults = {
        'author_id': lambda obj, cr, uid, context: uid,
        'user_id': lambda obj,cr, uid, context: uid
    }
    
    def cancel_task(self,cr,uid,ids,context=None):
        stage_id = self.pool.get('project.task.type').search(cr, uid, [('sequence','=',30)]) 
        self.write(cr, uid, ids, {'stage_id': stage_id[0]}, context=context)
        tasks = self.browse(cr, uid, ids, context=context)
        
        #sprawdzenie powiazanego obiektu
        for task in tasks:
            case_id = 0        
            case_obj = None 
            if(task.lead_id):
                case_obj=self.pool.get('crm.lead')
                case_id=task.lead_id.id
            elif(task.offer_id):
                case_obj=self.pool.get('jp.offer')
                case_id=task.offer_id.id
            elif(task.contract_id):
                case_obj=self.pool.get('jp.contract')
                case_id=task.contract_id.id
            elif(task.deal_id):
                case_obj=self.pool.get('jp.deal')
                case_id=task.deal_id.id
            elif(task.partner_id):
                case_obj=self.pool.get('res.partner')
                case_id=task.partner_id.id
                
        #zapisanie do powiazanego obiektu wiadomosci            
            if(case_obj):
                body = _('<b>Task: </b>%s<li><b>Stage: </b>%s</li>')%(task.name,task.stage_id.name)
                case=case_obj.browse(cr,uid,case_id,context=context)
                case_obj.message_post(cr, uid, [case_id], body=body, context=context)

    def close_task(self,cr,uid,ids,context=None):
        stage_id = self.pool.get('project.task.type').search(cr, uid, [('sequence','=',20)]) 
        self.write(cr, uid, ids, {'stage_id': stage_id[0]}, context=context)
        tasks = self.browse(cr, uid, ids, context=context)
        
        #sprawdzenie powiazanego obiektu
        for task in tasks:
            case_id = 0        
            case_obj = None 
            if(task.lead_id):
                case_obj=self.pool.get('crm.lead')
                case_id=task.lead_id.id
            elif(task.offer_id):
                case_obj=self.pool.get('jp.offer')
                case_id=task.offer_id.id
            elif(task.contract_id):
                case_obj=self.pool.get('jp.contract')
                case_id=task.contract_id.id
            elif(task.deal_id):
                case_obj=self.pool.get('jp.deal')
                case_id=task.deal_id.id
            elif(task.partner_id):
                case_obj=self.pool.get('res.partner')
                case_id=task.partner_id.id
                
        #zapisanie do powiazanego obiektu wiadomosci            
            if(case_obj):
                body = _('<b>Task: </b>%s<li><b>Stage: </b>%s</li>')%(task.name,task.stage_id.name)
                case=case_obj.browse(cr,uid,case_id,context=context)
                case_obj.message_post(cr, uid, [case_id], body=body, context=context)
        
    def open_task(self,cr,uid,ids,context=None):
        stage_id = self.pool.get('project.task.type').search(cr, uid, [('sequence','=',11)]) 
        self.write(cr, uid, ids, {'stage_id': stage_id[0]}, context=context)
        tasks = self.browse(cr, uid, ids, context=context)
        
        #sprawdzenie powiazanego obiektu
        for task in tasks:
            case_id = 0        
            case_obj = None 
            if(task.lead_id):
                case_obj=self.pool.get('crm.lead')
                case_id=task.lead_id.id
            elif(task.offer_id):
                case_obj=self.pool.get('jp.offer')
                case_id=task.offer_id.id
            elif(task.contract_id):
                case_obj=self.pool.get('jp.contract')
                case_id=task.contract_id.id
            elif(task.deal_id):
                case_obj=self.pool.get('jp.deal')
                case_id=task.deal_id.id
            elif(task.partner_id):
                case_obj=self.pool.get('res.partner')
                case_id=task.partner_id.id
                
        #zapisanie do powiazanego obiektu wiadomosci            
            if(case_obj):
                body = _('<b>Task: </b>%s<li><b>Stage: </b>%s</li>')%(task.name,task.stage_id.name)
                case=case_obj.browse(cr,uid,case_id,context=context)
                case_obj.message_post(cr, uid, [case_id], body=body, context=context)

    def open_line(self, cr, uid, id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Task', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': id[0],
           # 'target': 'current',
        }
        
    def task_term(self, cr, uid, context=None):
        users_obj = self.pool.get('res.users')
        users_ids = users_obj.search(cr, uid, [('active','=',True),('email','!=',False)])
        date_a = datetime.datetime.now().strftime("%Y-%m-%d 00:01:00")
        date_b = (datetime.datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d 00:01:00")
        
        for user in users_obj.browse(cr, uid, users_ids):
            task_deadline = self.search(cr, uid, [('state','in',['draft','open']),('deadline_datetime','<=',date_a),('user_id','=',user.id)], context=context)
            task_term = self.search(cr, uid, [('state','in',['draft','open']),('deadline_datetime','<=',date_b),('deadline_datetime','>=',date_a),('user_id','=',user.id)], context=context)
            
            if task_deadline or task_term:
                subject = _("OpenERP: informacje o zadaniach.")
                body = _("Informacje o zadaniach przypisanych do Ciebie.<br/>Ilość zadań przeterminowanych: %s.<br/>Ilość zadań na dziś: %s.")\
                        %(str(len(task_deadline)),str(len(task_term)))
                uid_id = users_obj.browse(cr, uid, uid)
                vals = {'email_from': uid_id.partner_id.name+"<"+uid_id.partner_id.email+">",
                        'email_to': user.email,
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': body,
                        'auto_delete': True}
                        
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
                                
    def create(self, cr, uid, vals, context=None):
        task_id = super(project_task, self).create(cr, uid, vals, context=context)
        
        users_obj = self.pool.get('res.users')

        if 'user_id' in vals and vals['user_id'] != uid:
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=project.task")%(jp_crm, cr.dbname, task_id)
            task = self.browse(cr, uid, task_id)
            deadline = task.deadline_datetime
            if not deadline:
                deadline = ''
            description = task.description
            if not description:
                description = ''
            priority = [_('Very important'),_('Important'),_('Medium'),_('Low'),_('Very Low')]
            subject = _("You have a new task: %s")%(task.name)
            uid_id = users_obj.browse(cr, uid, uid)
            body = _("User: %s<br/>Created for you a task: %s<br/>Type: %s<br/>Priority: %s<br/>Deadline: %s<br/>Description: %s<br/><a href='%s'>Link to task</a>")\
                    %(uid_id.name, task.name, task.task_type, priority[int(task.priority)], deadline, description, url)
                
            self.pool.get('project.task').message_post(cr, uid, task_id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                            parent_id=False, attachments=None, context=context, content_subtype='html')
        return task_id
        
    def write(self, cr, uid, ids, vals, context=None):
        task_id = super(project_task, self).write(cr, uid, ids, vals, context=context)
        
        if 'user_id' in vals or 'deadline_datetime' in vals:
            task = self.browse(cr, uid, ids)[0]
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=project.task")%(jp_crm, cr.dbname, ids[0])
            subject = _("Task changed : %s")%(task.name)
            body = _("CRM task has been changed.<br/>Description: %s<br/>Assigned to: %s<br/>Stop date: %s<br/><a href='%s'>Link to task</a>")%(task.name,task.user_id.name, task.deadline_datetime,url)
            
            self.pool.get('project.task').message_post(cr, uid, task.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                            parent_id=False, attachments=None, context=context, content_subtype='html')
        return task_id
    
class project_task_type(osv.osv):
    _inherit = 'project.task.type'
    _columns = {
            'state': fields.selection(_TASK_STATE, 'Related Status', required=True),
    }
    
    _defaults = {
                 'state': 'open',
                 }