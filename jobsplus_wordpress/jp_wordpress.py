# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 13:30:31 2013

@author: mkieszek
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import timedelta, datetime, date
import urllib
import pdb
import math
import time 

class jp_wordpress(osv.osv_memory):
    _name = 'jp.wordpress'
    _description = 'Jp wordpress'
    
    def get_countries(self, cr, uid):
        result = []
        
        country_obj = self.pool.get('res.country')
        
        country_ids = country_obj.search(cr, uid, [])
        
        for country in country_obj.browse(cr, uid, country_ids):
            result.append([country.id, _(country.name)])
            
        return result
    
    def get_trades(self, cr, uid):
        result = []
        
        trade_obj = self.pool.get('jp.trade')
        
        trade_ids = trade_obj.search(cr, uid, [])
        
        for trade in trade_obj.browse(cr, uid, trade_ids):
            result.append([trade.id, _(trade.name)])
                
        return result
    def get_ads(self, cr, uid, args):
        #pdb.set_trace()
        result = []        
        search = [('activity','=', True)]

        for arg in args:
            search.append((arg[0],arg[1],arg[2]))
            
        ad_obj = self.pool.get('jp.ad')
        ad_ids = ad_obj.search(cr, uid, search)
        
        for ad in ad_obj.browse(cr, uid, ad_ids):
            trade_ids=[]
            for trade in ad.trade_ids:
                trade_ids.append(trade.id)
            result.append([ad.id, ad.name, ad.position, ad.country_id.id, ad.ad_content, ad.state_id.id, ad.highlighted, trade_ids, ad.create_date, ad.publish_on])
            
        return result
    
    def get_states(self, cr, uid):
        result = []
        country_ids = self.pool.get('res.country').search(cr, uid, [('name','ilike','Poland')])
        
        state_obj = self.pool.get('res.country.state')
        state_ids = state_obj.search(cr, uid, [('country_id','=', country_ids[0])])        
        
        for state in state_obj.browse(cr, uid, state_ids):
            result.append([state.id, _(state.name)])
            
        return result
        
    def get_sallarys(self, cr, uid):
        result = []
        
        sallary_obj = self.pool.get('jp.sallary')
        
        sallary_ids = sallary_obj.search(cr, uid, [])
        
        for sallary in sallary_obj.browse(cr, uid, sallary_ids):
            result.append([sallary.id, _(sallary.name)])
                
        return result
        
    def add_candidate(self, cr, uid, args):
        candidate_obj = self.pool.get('jp.candidate')
        vals = {}
        trade_ids = args['trade_ids']
        sallary_id = args['sallary_ids']
        state_id = args['state_ids']
        ad_id = int(args['ad_id'])
        title = args['title']
        trades = []
        i=0
        #pdb.set_trace()
        for trade in trade_ids:
            i=i+1
            if trade != ',':
                if trade_ids[i]!=',':
                    trades.append(int(trade+trade_ids[i]))
                elif trade_ids[i-2]==',':
                    trades.append(int(trade))
        
        sallarys = []
        i=0
        for sallary in sallary_id:
            if sallary != ',':
                sallarys.append(int(sallary))
                
        states = []
        for state in state_id:
            i=i+1
            if state != ',':
                if state_id[i]!=',':
                    states.append(int(state+state_id[i]))
                elif state_id[i-2]==',':
                    states.append(int(state))
        
        vals = {
            'candidate': ("%s %s")%(args['name'],args['surname']),
            'phone': args['phone'],
            'email': args['email'],
            'trade_ids': [[6,False,trades]],
            'sallary_id': sallarys and sallarys[0] or False,
            'state_id': states and states[0] or False,
        }
        
        if args['portal'] != None and args['portal'] != '':
            portal_obj = self.pool.get('jp.portal')
            portal = portal_obj.search(cr, uid, [('code','=',args['portal'])])
            if portal:
                portal_id = portal_obj.browse(cr, uid, portal)[0].id
                vals['portal_id'] = portal_id
            
        vals['source_receive'] = '4'
        #pdb.set_trace()
        candidate_id = candidate_obj.create(cr, uid, vals, context=None)
        
        if ad_id > 0:
            ad_obj = self.pool.get('jp.ad')
            ad_ids = ad_obj.search(cr, uid, [('name','=',title)], context=None)
            if ad_ids:
                ad = ad_obj.browse(cr, uid, ad_ids)
                deal_id = ad and ad[0] and ad[0].deal_id.id or False
                if deal_id:
                    value = {
                        'deal_id': deal_id,
                        'candidate_id': candidate_id,
                    }
                    self.pool.get('jp.application').create(cr, uid, value, context=None)
        
        cv_data = args['cv_file_data']
        if cv_data != None:
            document_obj = self.pool.get('ir.attachment')
            missing_padding = 4 - len(cv_data) % 4
            if missing_padding:
                cv_data += b'='* missing_padding        
        
            cv_vals = {
                'name': args['cv_file_name'],
                'datas': cv_data,
                'datas_fname': args['cv_file_name'],
                'res_model': 'jp.candidate',
                'res_id': candidate_id
            }
            document_obj.create(cr, uid, cv_vals)
        
        if('lm_file_name' in args):
            lm_data = args['lm_file_data']
            missing_padding = 4 - len(lm_data) % 4
            if missing_padding:
                lm_data += b'='* missing_padding
            cv_vals['datas'] = lm_data
            cv_vals['name'] = args['lm_file_name']
            cv_vals['datas_fname'] = args['lm_file_name']
            document_obj.create(cr, uid, cv_vals)
                        
        
        if('other_file_name' in args):
            other_data = args['other_file_data']
            missing_padding = 4 - len(other_data) % 4
            if missing_padding:
                other_data += b'='* missing_padding
            cv_vals['datas'] = other_data
            cv_vals['name'] = args['other_file_name']
            cv_vals['datas_fname'] = args['other_file_name']
            document_obj.create(cr, uid, cv_vals)
        
        return candidate_id
    def accept_meeting(self, cr, uid, attendee_id, status):
        attendee_obj = self.pool.get('calendar.attendee')
        id = int(attendee_id)
        
        if status == 'accepted':           
            attendee_obj.do_accept(cr, uid, [id])
        elif status == 'declined':
            attendee_obj.do_decline(cr, uid, [id])
        elif status == 'tentative':
            attendee_obj.do_tentative(cr, uid, [id])
        else:
            return False
        event_id = attendee_obj.browse(cr, uid, id).meeting_ids[0].id
        return event_id
             
    def get_candidate_rate(self, cr, uid, vals):
        candidate_rate_obj = self.pool.get('jp.candidate.rate')
        candidate_rate_id = candidate_rate_obj.search(cr, uid, [('id','=',vals['id']),('state','=','1')])
        if candidate_rate_id:
            candidate_rate = candidate_rate_obj.browse(cr, uid, candidate_rate_id[0])
            value = {}
            value = {
                'rate': vals['rate'],
                'state': '2',
            }
            candidate_rate_obj.write(cr, uid, candidate_rate.id, value)
        
        return True
    def get_client_rate(self, cr, uid, vals):
        client_rate_obj = self.pool.get('jp.client.rate')
        client_rate_id = client_rate_obj.search(cr, uid, [('id','=',vals['id']),('state','=','1')])
        if client_rate_id:
            client_rate = client_rate_obj.browse(cr, uid, client_rate_id[0])
            value = {}
            value = {
                'rate': vals['rate'],
                'state': '2',
            }
            client_rate_obj.write(cr, uid, client_rate.id, value)
        
        return True
        
    def get_subscription(self, cr, uid, vals):
        subscription_obj = self.pool.get('jp.subscription')
        subscription_id = subscription_obj.search(cr, uid, [('subscription_id','=',int(vals['subscription_id']))])
        if subscription_id:
            subscription = subscription_obj.browse(cr, uid, subscription_id[0])
            value = {}
            verification = 0
            if vals['verification']:
                verification = int(vals['verification'])
                
            value = {
                'verification': verification,
                'verification_date': vals['verification_date'],
            }
            subscription_obj.write(cr, uid, subscription.id, value)
        else:
            value = {}
            verification = 0
            if vals['verification']:
                verification = int(vals['verification'])
                
            value = {
                'subscription_id': int(vals['subscription_id']),
                'name': vals['name'],
                'email': vals['email'],
                'employee': int(vals['employee']),
                'employer': int(vals['employer']),
                'token': vals['token'],
                'verification': verification,
                'verification_date': vals['verification_date'],
            }
            subscription_obj.create(cr, uid, value)
            
        return True
    
    def meeting_details(self, cr, uid, vals, context=None):
        meeting = self.pool.get('calendar.attendee').browse(cr, uid, int(vals)).meeting_ids[0]
        name = meeting.name
        start_date = (fields.datetime.context_timestamp(cr, uid, datetime.strptime(meeting.date, '%Y-%m-%d %H:%M:%S'), context=context)).strftime('%Y-%m-%d %H:%M')
        stop_date = (fields.datetime.context_timestamp(cr, uid, datetime.strptime(meeting.date_deadline, '%Y-%m-%d %H:%M:%S'), context=context)).strftime('%Y-%m-%d %H:%M')
        att_name = ''
        for attendee in meeting.attendee_ids:
            att_name += attendee.partner_id.name+"<br/> "
            
        description = ''
        if meeting.description != False:
            description = meeting.description
            
        location = ''
        if meeting.location != False:
            location = meeting.location
                       
        start_date_dur = datetime.strptime(meeting.date, "%Y-%m-%d %H:%M:%S")
        stop_date_dur = datetime.strptime(meeting.date_deadline, "%Y-%m-%d %H:%M:%S")
        duration = stop_date_dur - start_date_dur
        dur_str = ''
        dur_minutes = duration.seconds/60
        if meeting.allday != True:  
            if dur_minutes < 60:
                dur_str = '00:'+str(dur_minutes)
            elif duration.days != 0:
                hours = int(math.floor(dur_minutes/60))
                minutes = int(dur_minutes - (hours*60))
                days = duration.days
                dur_str = str(days)+" dzień i "+str(hours)+":"+str(minutes)
            elif dur_minutes >= 60 and dur_minutes < 60*24:
                hours = int(math.floor(dur_minutes/60))
                minutes = int(dur_minutes - (hours*60))
                dur_str = str(hours)+":"+str(minutes)
        else:
            dur_str = 'Cały dzień'
                
        return name, start_date, stop_date, att_name, description, location, dur_str
        
    def upload_attachment(self, cr, uid, args):
        return True
        
    def run_upload(self, cr, uid, context=None):
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
        url=("http://%s/wp-content/plugins/jobsplus-integration/api/get_dictionaries.php")%(jp_www)
        urlhandler = urllib.urlopen(url) 
        
    def run_upload_client_rate(self, cr, uid, context=None):
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
        url_client=("http://%s/wp-content/plugins/jobsplus-integration/api/get_client_rate.php?export=client")%(jp_www)
        
        urlhandler = urllib.urlopen(url_client)
        
    def run_upload_candidate_rate(self, cr, uid, context=None):
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
        url_candidate=("http://%s/wp-content/plugins/jobsplus-integration/api/get_candidate_rate.php?export=candidate")%(jp_www)
        urlhandler = urllib.urlopen(url_candidate)
        
    def run_upload_subscription(self, cr, uid, context=None):
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
        url_subscription=("http://%s/wp-content/plugins/jobsplus-integration/api/get_subscription.php?export=subscription")%(jp_www)
        urlhandler = urllib.urlopen(url_subscription)
        