# -*- coding: utf-8 -*-
"""
Created on Mon May 27 21:51:03 2013

@author: mbereda
"""

from openerp.osv import fields, osv
import pdb
import datetime
from datetime import date, timedelta

class jp_report_recruitment(osv.Model):
    _name="jp.report.recruitment"
    _description = 'Report recruitment'
    _columns={
        'name': fields.char('Name', size=64, readonly=True),
        'year': fields.char('Year', size=64, readonly=True),
        'month': fields.char('Month', size=64, readonly=True),
        'week_number': fields.char('Week number', size=64, readonly=True),
        'quarter': fields.char('Quarter', size=64, readonly=True),
        'recruiter_id': fields.many2one('res.users', 'Recruiter', readonly=True),
        'open_deals': fields.integer('Open deals', readonly=True),
        'open_handover_deals': fields.integer('Open deals(deadline)', readonly=True),
        'meeting_deals': fields.integer('Meeting deals', readonly=True),
        'won_deals': fields.integer('Won deals', readonly=True),
        'transfer_candidates': fields.integer('Transfer candidates', readonly=True),
        'lost_deals': fields.integer('Lost deals', readonly=True),
        'cease_deals': fields.integer('Cease deals', readonly=True),
        'closed_tasks': fields.integer('Closed tasks', readonly=True),
        'date': fields.datetime('Date', readonly=True),
    }
    _order = "week_number desc, name"

    def count_deal_open(self, cr, uid, date, user_id, context=None):
        day = date.strftime('%Y-%m-%d')
        stage_ids = self.pool.get('jp.deal.stage').search(cr, uid, [('state','=','open')])
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        count = 0
        for stage in stage_ids:
            stage_history_id = stage_history_obj.search(cr, uid, [('stage_id','=',stage),('recruiter_id','=', user_id),('date_cr','=',day)])
            if stage_history_id:
                count += len(stage_history_id)
        
        return count
        
    def count_deal_open_hendover(self, cr, uid, date, user_id, context=None):
        day = date.strftime('%Y-%m-%d')
        stage_ids = self.pool.get('jp.deal.stage').search(cr, uid, [('state','=','open')])
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        deal_obj = self.pool.get('jp.deal')
        count = 0
        start_week = datetime.date.today()-timedelta(days=(datetime.datetime.today().weekday()))
        stop_week = datetime.date.today()+timedelta(days=6-(datetime.datetime.today().weekday()))
        for stage in stage_ids:
            stage_history_id = stage_history_obj.search(cr, uid, [('stage_id','=',stage),('recruiter_id','=', user_id),('date_cr','>=',start_week),('date_cr','<=',stop_week)])
            if stage_history_id:
                stage_historys = stage_history_obj.browse(cr, uid, stage_history_id)
                for stage_history in stage_historys:
                    deal_id = stage_history.deal_id
                    deals = deal_obj.search(cr, uid, [('id','=',deal_id.id)])
                    for deal in deal_obj.browse(cr, uid, deals):
                        if deal.handover_date < day:
                            count += 1
        
        return count
        
    def count_meeting_deal(self, cr, uid, date, user_id, context=None):
        day = date.strftime('%Y-%m-%d')
        stage_id = self.pool.get('jp.deal.stage').search(cr, uid, [('name','=','Spotkania')])[0]
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        stage_history_id = stage_history_obj.search(cr, uid, [('stage_id','=',stage_id),('recruiter_id','=', user_id),('date_cr','=',day)])
        
        return len(stage_history_id)
        
    def count_deal_won(self, cr, uid, date, user_id, context=None):
        day = date.strftime('%Y-%m-%d')
        stage_id = self.pool.get('jp.deal.stage').search(cr, uid, [('name','=','Wygrany')])[0]
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        stage_history_id = stage_history_obj.search(cr, uid, [('stage_id','=',stage_id),('recruiter_id','=', user_id),('date_cr','=',day)])
        
        return len(stage_history_id)
        
    def count_transfer_candidates(self, cr, uid, date, user_id, context=None):
        application_obj = self.pool.get('jp.application')
        day = date.strftime('%Y-%m-%d %H:%M:%S')
        next_day = (date+timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        application_ids = application_obj.search(cr, uid, [('create_uid','=',user_id),('create_date','>=',day),('create_date','<',next_day),('status','=',2)])
        
        return len(application_ids)
        
    def count_deal_lost(self, cr, uid, date, user_id, context=None):
        day = date.strftime('%Y-%m-%d')
        stage_id = self.pool.get('jp.deal.stage').search(cr, uid, [('name','=','Przegrany')])[0]
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        stage_history_id = stage_history_obj.search(cr, uid, [('stage_id','=',stage_id),('recruiter_id','=', user_id),('date_cr','=',day)])
                
        return len(stage_history_id)
        
    def count_deal_cease(self, cr, uid, date, user_id, context=None):
        day = date.strftime('%Y-%m-%d')
        stage_id = self.pool.get('jp.deal.stage').search(cr, uid, [('name','=','Wstrzymany')])[0]
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        stage_history_id = stage_history_obj.search(cr, uid, [('stage_id','=',stage_id),('recruiter_id','=', user_id),('date_cr','=',day)])
        
        return len(stage_history_id)
        
    def count_task_closed(self, cr, uid, date, user_id, context=None):
        start_day = date.strftime('%Y-%m-%d %H:%M:%S')
        stop_day = (date+timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        task_ids = self.pool.get('project.task').search(cr, uid, [('state','=','done'), ('user_id','=',user_id), ('date_end','>=',start_day),('date_end','<',stop_day)], context=context)
        
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
        
        vals = {} 
        vals = {
            'recruiter_id': user_id,
            'date': date,
            'open_deals': self.count_deal_open(cr, uid, date, user_id, context=context),
            'open_handover_deals': self.count_deal_open_hendover(cr, uid, date, user_id, context=context),
            'meeting_deals': self.count_meeting_deal(cr, uid, date, user_id, context=context),
            'won_deals': self.count_deal_won(cr, uid, date, user_id, context=context),
            'transfer_candidates': self.count_transfer_candidates(cr, uid, date, user_id, context=context),
            'lost_deals': self.count_deal_lost(cr, uid, date, user_id, context=context),
            'cease_deals': self.count_deal_cease(cr, uid, date, user_id, context=context),
            'closed_tasks': self.count_task_closed(cr, uid, date, user_id, context=context),
            'name': str(user_id)+'-'+str(date.isocalendar()[1]).zfill(2),
            'year': year,
            'month': year+'-M'+ str(month).zfill(2),
            'week_number': year+'-W'+str(date.isocalendar()[1]).zfill(2),
            'quarter': year+'-Q'+str(quarter),
        }
        return super(jp_report_recruitment, self).create(cr, uid, vals, context=context)
        
    def update_report(self, cr, uid, date, user_id, context = None):
        record_id = self.search(cr, uid, [('name','=',str(user_id)+'-'+str(date.isocalendar()[1]).zfill(2))])
        if record_id != []:
            record = self.browse(cr, uid, record_id)[0]
            vals = {}
            vals = {
                'date': date,
                'open_deals': record.open_deals+self.count_deal_open(cr, uid, date, user_id, context=context),
                'open_handover_deals': self.count_deal_open_hendover(cr, uid, date, user_id, context=context),
                'meeting_deals': record.meeting_deals+self.count_meeting_deal(cr, uid, date, user_id, context=context),
                'won_deals': record.won_deals+self.count_deal_won(cr, uid, date, user_id, context=context),
                'transfer_candidates': record.transfer_candidates+self.count_transfer_candidates(cr, uid, date, user_id, context=context),
                'lost_deals': record.lost_deals+self.count_deal_lost(cr, uid, date, user_id, context=context),
                'cease_deals': record.cease_deals+self.count_deal_cease(cr, uid, date, user_id, context=context),
                'closed_tasks': record.closed_tasks+self.count_task_closed(cr, uid, date, user_id, context=context),
            }
            super(jp_report_recruitment, self).write(cr, uid, record_id, vals, context=context)
        else:
            self.create_report(cr, uid, date, user_id, context=context)
        return 
    
    def calculate_report_recruitment(self, cr, uid, context=None):
        #sprawdz dzień tygodnia
        day = datetime.date.today().weekday()
        today = datetime.date.today()
        #dla każdego użytkownika z uprawnieniami rekruter
        group_obj = self.pool.get('res.groups')
        group = group_obj.search(cr, uid, [('name','=','Rekruter Jobs Plus')])[0]
        group_id = group_obj.browse(cr, uid, group)
        user_ids = group_id.users
        # jeśli poniedziałek stwórz nowy rekord
        for user_id in user_ids:
            #tych nie raportujemy
            if (user_id.id in (11, 13, 14, 15, 16, 17, 24)):
                if day == 0:
                    self.create_report(cr, uid, today, user_id.id, context = None)
                # jeżeli nie to aktualizuj ostatni rekord
                else:
                    self.update_report(cr, uid, today, user_id.id, context = None)
                    
        return True
        
    def copy_data(self, cr, uid, context=None):
        selects = ['Do fakturowania','Zafakturowany','Zapłacony','Wygrany','Przegrany','Nowy','Rekrutacja','Do przekazania','Przekazane','Spotkania','Wstrzymany','Leasing']
        deal_obj = self.pool.get('jp.deal')
        deal = deal_obj.search(cr, uid, [],context=context)
        deal_ids = deal_obj.browse(cr, uid, deal)
        stage_obj = self.pool.get('jp.deal.stage')
        stage_history_obj = self.pool.get('jp.deal.stage.history')
        mail_obj = self.pool.get('mail.message')
        
        #usuwanie poprzednich danych historycznych
        for stage_h_id in stage_history_obj.search(cr, uid, []):
            stage_history_obj.unlink(cr, uid, stage_h_id)
        
        for deal in deal_ids:
            for select in selects:
                mail = mail_obj.search(cr, uid, [('body','ilike',select+"</div>"),('res_id','=',deal.id),('model', '=', 'jp.deal')],context=context)
                mail_ids = mail_obj.browse(cr, uid, mail)
                
                if mail_ids:
                    for mail_id in mail_ids:
                        stage_id = stage_obj.search(cr, uid, [('name','=',select)])[0]
                        vals={}
                        vals={
                            'date_cr': mail_id.date,
                            'stage_id': stage_id,
                            'deal_id': mail_id.res_id,
                            'recruiter_id': deal.recruiter_id.id,
                        }
                        stage_history_obj.create(cr, uid, vals, context=context)
        
        return True
        
    def calculate_report_recruitment_old(self, cr, uid, context=None):
        today = datetime.date.today()
        start_date = datetime.date(2013, 12, 01)
        
        group_obj = self.pool.get('res.groups')
        group = group_obj.search(cr, uid, [('name','=','Rekruter Jobs Plus')])[0]
        group_id = group_obj.browse(cr, uid, group)
        user_ids = group_id.users
        while today>start_date:
            for user_id in user_ids:
                #tych nie raportujemy
                if(user_id.id in (11, 13, 14, 15, 16, 17, 24)):
                    if start_date.weekday() == 0:
                        self.create_report(cr, uid, start_date, user_id.id, context = None)
                        # jeżeli nie to aktualizuj ostatni rekord
                    else:
                        self.update_report(cr, uid, start_date, user_id.id, context = None)
            start_date=start_date+timedelta(days=1)
