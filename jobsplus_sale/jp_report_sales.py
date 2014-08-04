# -*- coding: utf-8 -*-
"""
Created on Mon May 27 21:51:03 2013

@author: mbereda
"""

from openerp.osv import fields, osv
import pdb
import datetime
from datetime import date, timedelta

class jp_report_sales(osv.Model):
    _name="jp.report.sales"
    _description = 'Raport Sprzedawców'  
    _order = 'week_number'  
    _columns={
        'name': fields.char('Name', size=64, readonly=True),
        'user_id': fields.many2one('res.users', 'User', readonly=True),
        'created_deals': fields.integer('Created deals', readonly=True),
        'invoice_deals': fields.integer('Invoice deals', readonly=True),
        'added_leads': fields.integer('Added leads', readonly=True),
        'closed_tasks': fields.integer('Closed tasks', readonly=True),
        'date': fields.datetime('Date', readonly=True),
        'year': fields.char('Year', size=64, readonly=True),
        'month': fields.char('Month', size=64, readonly=True),
        'week_number': fields.char('Week number', size=64, readonly=True),
        'quarter': fields.char('Quarter', size=64, readonly=True),
        'created_offers' : fields.integer('Created offers', readonly=True),
        'created_contracts' : fields.integer('Created contracts', readonly=True),
    }

        
    def count_deal_new(self, cr, uid, date, user_id, context=None):
        date_up=date+timedelta(days=1)
        date_up = date_up.strftime("%Y-%m-%d %H:%M:%S")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        deal_ids = self.pool.get('jp.deal').search(cr, uid, [('create_date','<',date_up),('create_date','>',date), ('create_uid','=',user_id)], context=context)
        
        return len(deal_ids)
        
    def count_deal_invoice(self, cr, uid, date, user_id, context=None):
        selects = ['Do fakturowania']
        deals=[]
        stage_obj = self.pool.get('jp.deal.stage')
        date = date.strftime("%Y-%m-%d")
        for select in selects:
            stage = stage_obj.search(cr, uid, [('name','=',select)])
            stage_id = stage_obj.browse(cr, uid, stage)[0].id
            deal_ids = self.pool.get('jp.deal.stage.history').search(cr, uid, [('date_cr','=',date),('stage_id','=',stage_id),('create_uid','=',user_id)], context=context)
            if deal_ids != []: 
                deals.append(deal_ids)
        return len(deals)
    
    def count_offers_new(self, cr, uid, date, user_id, context=None):
        date_up=date+timedelta(days=1)
        date_up = date_up.strftime("%Y-%m-%d %H:%M:%S")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        offers_ids = self.pool.get('jp.offer').search(cr, uid, [('create_date','<',date_up),('create_date','>',date),('create_uid','=',user_id)], context=context)
        
        return len(offers_ids)
    
    def count_contracts_new(self, cr, uid, date, user_id, context=None):
        date_up=date+timedelta(days=1)
        date_up = date_up.strftime("%Y-%m-%d %H:%M:%S")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        contract_ids = self.pool.get('jp.contract').search(cr, uid, [('create_date','<',date_up),('create_date','>',date),('create_uid','=',user_id)], context=context)
        
        return len(contract_ids)
        
    def count_lead_new(self, cr, uid, date, user_id, context=None):
        date_up=date+timedelta(days=1)
        date_up = date_up.strftime("%Y-%m-%d %H:%M:%S")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        lead_ids = self.pool.get('crm.lead').search(cr, uid, [('create_date','<',date_up),('create_date','>',date), ('create_uid','=',user_id)], context=context)
        
        return len(lead_ids)
        
    def count_task_closed(self, cr, uid, date, user_id, context=None):
        date_up=date+timedelta(days=1)
        date_up = date_up.strftime("%Y-%m-%d %H:%M:%S")
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        task_ids = self.pool.get('project.task').search(cr, uid, [('state','=','done'), ('user_id','=',user_id),('date_end','<',date_up),('date_end','>',date)], context=context)
        
        return len(task_ids)
        
    def create_report(self, cr, uid, date, user_id, context = None):
        month = date.month
        year = str(date.year)
        
        quarter = 0
        if month <4:
            quarter = 1
        elif month <7:
            quarter = 2
        elif month < 10:
            quarter = 3
        else:
            quarter = 4
        vals={}
        vals = {
            'user_id': user_id,
            'date': date-timedelta(days=1),
            'created_deals': self.count_deal_new(cr, uid, date, user_id, context=context),
            'invoice_deals': self.count_deal_invoice(cr, uid, date, user_id, context=context),
            'added_leads': self.count_lead_new(cr, uid, date, user_id, context=context),
            'closed_tasks': self.count_task_closed(cr, uid, date, user_id, context=context),
            'created_offers': self.count_offers_new(cr, uid, date, user_id, context=context),
            'created_contracts': self.count_contracts_new(cr, uid, date, user_id, context=context),
            'name': str(user_id)+'-'+str(date.isocalendar()[1]).zfill(2),
            'year': year,
            'month': year+'-M'+ str(month).zfill(2),
            'week_number': year+'-W'+str(date.isocalendar()[1]).zfill(2),
            'quarter': year+'-Q'+str(quarter),
        }
        return super(jp_report_sales, self).create(cr, uid, vals, context=context)
         
    def update_report(self, cr, uid, date, user_id, context = None):
        record_id = self.search(cr, uid, [('name','=',str(user_id)+'-'+str(date.isocalendar()[1]).zfill(2))])
        if record_id != []:
            record = self.browse(cr, uid, record_id)[0]
            vals={}
            vals = {
                'date': date,
                'created_deals': record.created_deals+self.count_deal_new(cr, uid, date, user_id, context=context),
                'invoice_deals': record.invoice_deals+self.count_deal_invoice(cr, uid, date, user_id, context=context),
                'added_leads': record.added_leads+self.count_lead_new(cr, uid, date, user_id, context=context),
                'closed_tasks': record.closed_tasks+self.count_task_closed(cr, uid, date, user_id, context=context),
                'created_offers': record.created_offers+self.count_offers_new(cr, uid, date, user_id, context=context),
                'created_contracts': record.created_contracts+self.count_contracts_new(cr, uid, date, user_id, context=context),
            }
            super(jp_report_sales, self).write(cr, uid, record_id, vals, context=context)
        else:
            self.create_report(cr, uid, date, user_id, context=context)
        return 
         
    def calculate_report_sales(self, cr, uid, context=None):
        #sprawdz dzień tygodnia
        date = datetime.date.today()
        day = datetime.date.today().weekday()
        
        #dla każdego użytkownika z uprawnieniami handlowiec
        group_obj = self.pool.get('res.groups')
        group = group_obj.search(cr, uid, [('name','=','Handlowiec Jobs Plus')])[0]
        group_id = group_obj.browse(cr, uid, group)
        user_ids = group_id.users
        # jeśli poniedziałek stwórz nowy rekord
        for user_id in user_ids:
            #tych nie raportujemy
            if(user_id.id in (6, 7, 8, 23)):
                if day == 0:
                    self.create_report(cr, uid, date, user_id.id, context = None)
                # jeżeli nie to aktualizuj ostatni rekord
                else:
                    self.update_report(cr, uid, date, user_id.id, context = None)
    
    def copy_data(self, cr, uid, context=None):
        selects = ['Do fakturowania','Zafakturowany','Zapłacony','Wygrany','Przegrany']
        
        deal_obj = self.pool.get('jp.deal')
        deal = deal_obj.search(cr, uid, [('date_closed','=',False)],context=context)
        deal_ids = deal_obj.browse(cr, uid, deal)
        
        for deal in deal_ids:
            for select in selects:
                mail_obj = self.pool.get('mail.message')
                mail = mail_obj.search(cr, uid, [('body','ilike',select),('res_id','=',deal.id),('model', '=', 'jp.deal')],context=context)
                mail_ids = mail_obj.browse(cr, uid, mail)
                
                if mail_ids != []:
                    vals={}
                    vals={
                        'date_closed': mail_ids[0].date,
                    }
                    self.pool.get('jp.deal').write(cr, uid, [deal.id], vals, context=context)
                    break
        
        return
        
    def calculate_report_sales_old(self, cr, uid, context=None):
        today = datetime.date.today()
        day = datetime.date.today().weekday()
        start_date = datetime.date(2013, 6, 1)

        group_obj = self.pool.get('res.groups')
        group = group_obj.search(cr, uid, [('name','=','Handlowiec Jobs Plus')])[0]
        group_id = group_obj.browse(cr, uid, group)
        user_ids = group_id.users
            
        while today>start_date:
            for user_id in user_ids:
                if(user_id.id in (6, 7, 8, 23)):
                    if start_date.weekday() == 0:
                        self.create_report(cr, uid, start_date, user_id.id, context = None)
                        # jeżeli nie to aktualizuj ostatni rekord
                    else:
                        self.update_report(cr, uid, start_date, user_id.id, context = None)
                
            start_date=start_date+timedelta(days=1)
            