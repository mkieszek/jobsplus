# -*- coding: utf-8 -*-
'''
Created on 30 kwi 2014

@author: pczorniej
'''
from openerp.osv import fields, osv
import pdb
import datetime
from datetime import date, timedelta

class jp_report_sales2(osv.Model):
    _name="jp.report.sales2"
    _description = 'Raport Sprzedaży'
    _order = 'month' 
    _columns={
        'name': fields.char('Name', size=64, readonly=True),
        'client_id': fields.many2one('res.partner', 'Client', readonly=True),
        'user_id': fields.many2one('res.users','Salesman', readonly=True),
        'date': fields.datetime('Date', readonly=True),
        'year': fields.char('Year', size=64, readonly=True),
        'month': fields.char('Month', size=64, readonly=True),
        'quarter': fields.char('Quarter', size=64, readonly=True),
        'invoice_deals': fields.integer('Invoice deals', readonly=True),
        'value_invoice': fields.float('Value invoice deals', readonly=True),
        'leasing_deals': fields.integer('Leasing deals', readonly=True),
        'value_margin' : fields.float('Value margin agencies', readonly=True),
        'value_leasing' : fields.float('Value leasing invoice', readonly=True),
    }
    
    def count_deal_invoice(self, cr, uid, date, client_id, context=None):
        selects = ['Do fakturowania']
        stage_obj = self.pool.get('jp.deal.stage')
        day = date.strftime("%Y-%m-%d")
        for select in selects:
            stage = stage_obj.search(cr, uid, [('name','=',select)])
            stage_id = stage_obj.browse(cr, uid, stage)[0].id
            deal_ids = self.pool.get('jp.deal.stage.history').search(cr, uid, [('date_cr','=',day),('stage_id','=',stage_id),('deal_id.client_id.id','=',client_id.id)], context=context)
        
        return len(deal_ids)
    
    def count_value_deal_invoice(self, cr, uid, date, client_id, context=None):
        selects = ['Do fakturowania']
        stage_obj = self.pool.get('jp.deal.stage')
        day = date.strftime("%Y-%m-%d")
        amount = 0.0
        for select in selects:
            stage = stage_obj.search(cr, uid, [('name','=',select)])
            stage_id = stage_obj.browse(cr, uid, stage)[0].id
            deal_ids = self.pool.get('jp.deal.stage.history').search(cr, uid, [('date_cr','=',day),('stage_id','=',stage_id),('deal_id.client_id.id','=',client_id.id)], context=context)
            amount = 0.0
            if deal_ids:
                for deal in self.pool.get('jp.deal.stage.history').browse(cr, uid, deal_ids):
                    amount += deal.deal_id.planned_revenue
            
        return amount
    
    def count_deal_leasing(self, cr, uid, date, client_id, context=None):
        selects = ['Leasing']
        stage_obj = self.pool.get('jp.deal.stage')
        day = date.strftime("%Y-%m-%d")
        for select in selects:
            stage = stage_obj.search(cr, uid, [('name','=',select)])
            stage_id = stage_obj.browse(cr, uid, stage)[0].id
            deal_ids = self.pool.get('jp.deal.stage.history').search(cr, uid, [('date_cr','=',day),('stage_id','=',stage_id),('deal_id.client_id.id','=',client_id.id)], context=context)
        return len(deal_ids)
    
    def count_value_margin(self, cr, uid, date, client_id, context=None):
        amount = 0.0
        stage_obj = self.pool.get('jp.deal.stage')
        stage = stage_obj.search(cr, uid, [('name','=','Leasing')])
        calc_obj = self.pool.get('jp.calculation')
        calc_ids = calc_obj.search(cr, uid, [('deal_id.client_id','=',client_id.id),('deal_id.stage_id','=',stage[0]),('calculation_from','=',date)])
        
        for calc in calc_obj.browse(cr, uid, calc_ids):
            amount += calc.value_margin
        return amount
    
    def count_value_leasing(self, cr, uid, date, client_id, context=None):
        amount = 0.0
        stage_obj = self.pool.get('jp.deal.stage')
        stage = stage_obj.search(cr, uid, [('name','=','Leasing')])
        calc_obj = self.pool.get('jp.calculation')
        calc_ids = calc_obj.search(cr, uid, [('deal_id.client_id','=',client_id.id),('deal_id.stage_id','=',stage[0]),('calculation_from','=',date)])
        
        for calc in calc_obj.browse(cr, uid, calc_ids):
            amount += calc.value_leasing
        return amount
    
    def count_value_deal_leasing(self, cr, uid, date, client_id, context=None):
        selects = ['Leasing']
        stage_obj = self.pool.get('jp.deal.stage')
        day = date.strftime("%Y-%m-%d")
        amount = 0.0
        
        for select in selects:
            stage = stage_obj.search(cr, uid, [('name','=',select)])
            stage_id = stage_obj.browse(cr, uid, stage)[0].id
            deal_ids = self.pool.get('jp.deal.stage.history').search(cr, uid, [('date_cr','=',day),('stage_id','=',stage_id),('deal_id.client_id.id','=',client_id.id)], context=context)
            amount = 0.0
            if deal_ids:
                for deal in self.pool.get('jp.deal.stage.history').browse(cr, uid, deal_ids):
                    amount += deal.deal_id.planned_revenue
            
        return amount
    
    def create_report(self, cr, uid, date, client, context = None):
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
        vals = {}
        vals = {
            'client_id' : client.id,
            'user_id' : client.user_id.id,
            'date': date-timedelta(days=1),
            'name': year+'-M'+ str(month).zfill(2)+'-'+str(client.id)+'-'+str(client.user_id.id).zfill(2),
            'year': year,
            'month': year+'-M'+ str(month).zfill(2),
            'quarter': year+'-Q'+str(quarter),
            'invoice_deals' : self.count_deal_invoice(cr, uid, date, client, context=context),
            'value_invoice' : self.count_value_deal_invoice(cr, uid, date, client, context=context),
            'leasing_deals' : self.count_deal_leasing(cr, uid, date, client, context=context),
            'value_margin' : self.count_value_margin(cr, uid, date, client, context=context),
            'value_leasing' : self.count_value_leasing(cr, uid, date, client, context=context),
        }
        return super(jp_report_sales2, self).create(cr, uid, vals, context=context)
         
    def update_report(self, cr, uid, date, client, context = None):
        record_id = self.search(cr, uid, [('name','=',str(date.year)+'-M'+ str(date.month).zfill(2)+'-'+str(client.id)+'-'+str(client.user_id.id).zfill(2))])
        if record_id != []:
            record = self.browse(cr, uid, record_id)[0]
            vals = {}   
            vals = {
                    'date' : date,
                    'invoice_deals' : record.invoice_deals+self.count_deal_invoice(cr, uid, date, client, context=context),
                    'value_invoice' : record.value_invoice+self.count_value_deal_invoice(cr, uid, date, client, context=context),
                    'leasing_deals' : record.leasing_deals+self.count_deal_leasing(cr, uid, date, client, context=context),
                    'value_margin' : record.value_margin+self.count_value_margin(cr, uid, date, client, context=context),
                    'value_leasing' : record.value_leasing+self.count_value_leasing(cr, uid, date, client, context=context),
            }
            super(jp_report_sales2, self).write(cr, uid, record_id, vals, context=context)
        else:
            self.create_report(cr, uid, date, client, context=context)
        return
    
    def calculate_report_sales(self, cr, uid, context=None):
        #sprawdz dzień tygodnia
        date = datetime.date.today()
        day = datetime.date.today().day
        partner_obj = self.pool.get('res.partner')
        client_ids = partner_obj.search(cr, uid, [('is_company','=',True)])
        # jeśli środa stwórz nowy rekord

        for client_id in partner_obj.browse(cr, uid, client_ids):
            if day == 1:
                self.create_report(cr, uid, date, client_id, context = None)
            # jeżeli nie to aktualizuj ostatni rekord
            else:
                self.update_report(cr, uid, date, client_id, context = None)
                
    def calculate_report_sales_old2(self, cr, uid, context=None):
        today = datetime.date.today()
        start_date = datetime.date(2014, 1, 1)
        
        partner_obj = self.pool.get('res.partner')        
        client_ids = partner_obj.search(cr, uid, [('is_company','=',True)])
        clients = partner_obj.browse(cr, uid, client_ids)

        while today>start_date:
            for client_id in clients:
                if start_date.day == 1:
                    self.create_report(cr, uid, start_date, client_id, context = None)
                    # jeżeli nie to aktualizuj ostatni rekord
                else:
                    self.update_report(cr, uid, start_date, client_id, context = None)
            print start_date
            start_date=start_date+timedelta(days=1)
            
            