# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from datetime import timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
import pdb
import datetime

class jp_employee(osv.osv):
    _name = 'jp.employee'
    _description = "Employee"
        
    _columns = {
        'name': fields.char('Name', required=True),
        'user_id': fields.many2one('res.users', 'User'),
        'date_of_birth': fields.date('Date of birth'),
        'contract_from': fields.date('Agreement from'),
        'contract_to': fields.date('Agreement to'),
        'manager_id': fields.many2one('jp.employee','Manager'),
        'manager_user_id': fields.integer('Manager user_id'),
        'email': fields.char('Email'),
        'image': fields.binary('Image'),
    }
    
    def create(self, cr, uid, vals, context=None):
        user = self.search(cr, uid, [('user_id','=',vals['user_id'])])
        if user:
            raise osv.except_osv(_('Ostrzeżenie'), _('Wybrany użytkownik systemu jest już dodady jako pracownik.'))
        employee_id = super(jp_employee, self).create(cr, uid, vals, context=context)
        return employee_id

    def on_change_employee(self, cr, uid, ids, user_id, context=None):
        users_obj = self.pool.get('res.users')
        user_id = users_obj.browse(cr, uid, user_id)
        
        values = {
            
            'email' : user_id.partner_id.email,
            'image' : user_id.partner_id.image,
            'name': user_id.partner_id.name,
        }
        return {'value' : values}
    def on_change_manager(self, cr, uid, ids, manager_id, context=None):
        employee = self.browse(cr, uid, manager_id)
        
        values = {'manager_user_id' : employee.user_id.id}
        
        return {'value' : values}
        
    def notification_birth_employee(self, cr, uid, ids, context=None):
        groups_obj = self.pool.get('res.groups')
        group_id = groups_obj.search(cr, uid, [('name','=','Marketing Jobs Plus')])
        users = groups_obj.browse(cr, uid, group_id)[0].users
        
        employee_id = self.search(cr, uid, [('date_of_birth','!=',False)])
        employees = self.browse(cr, uid, employee_id)
        
        today = datetime.date.today()
        tomorrow = today + timedelta(days = 1)
        
        birthday = ""
        for employee in employees:
            if employee.date_of_birth:
                date_of_birth = datetime.datetime.strptime(employee.date_of_birth,"%Y-%m-%d").date()
                if date_of_birth.month == tomorrow.month and date_of_birth.day == tomorrow.day:
                    birthday += employee.name+", "
        if birthday != "":
            mail_to = ""
            users_obj = self.pool.get('res.users')
            for user in users:
                if user.partner_id.email is not '' and user.partner_id.name != 'Administrator' and user.active is True:
                    mail_to += user.partner_id.email + ", "
            if mail_to is not "":
                subject = _("Urodziny")
                body = _("Urodziny jutro obchodzi: %s")%(birthday)
                uid = users_obj.search(cr, uid, [('id','=',uid)])[0]
                uid_id = users_obj.browse(cr, uid, uid)
                
                vals = {'email_from': uid_id.partner_id.name+"<"+uid_id.partner_id.email+">",
                        'email_to': mail_to,
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': body,
                        'auto_delete': True}
                        
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
            
    def deadline_agreement_employee(self, cr, uid, context=None):
        users_obj = self.pool.get('res.users')
        today = datetime.date.today()
        next_days = today + timedelta(days = 2)
        
        employee_ids = self.search(cr, uid, [('contract_to','=',next_days),('manager_id','!=',False)])
        if employee_ids:
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
            
        for employee in self.browse(cr, uid, employee_ids):
            if employee.manager_id.email != False:
                mail_to = employee.manager_id.email
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.employee")%(jp_crm, cr.dbname, employee.id)
            subject = _("Koniec umowy z pracownikiem")
            body = _("Kończy się umowa z Twoim pracownikiem: %s <br/> Data końca umowy: %s<br/><a href='%s'>Link do pracownika</a>")\
                    %(employee.name,employee.contract_to,url)
            uid_id = users_obj.browse(cr, uid, uid)
            vals = {'email_from': uid_id.partner_id.name+"<"+uid_id.partner_id.email+">",
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True}
                    
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)