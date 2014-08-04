# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 19:59:12 2013

@author: mkieszek
"""

from openerp.osv import fields, osv
from tools.translate import _
import time
import pdb
import pytz
import re
from datetime import timedelta, datetime, date

"""
{'alarm_id': False,
 'allday': False,
 'attendee_ids': [],
 'byday': False,
 'categ_ids': [[6, False, []]],
 'class': 'public',
 'count': 1,
 'date': '2013-06-13 06:00:00',
 'date_deadline': '2013-06-13 07:00:00',
 'day': 0,
 'description': False,
 'duration': 1,
 'end_date': False,
 'end_type': 'count',
 'fr': False,
 'interval': 1,
 'location': False,
 'mo': False,
 'name': 'Nowe zdarzenie',
 'organizer': 'Administrator <crm@jobsplus.pl>',
 'partner_ids': [[6, False, []]],
 'recurrency': False,
 'recurrent_id': 0,
 'recurrent_id_date': False,
 'rrule_type': False,
 'sa': False,
 'select1': 'date',
 'show_as': 'busy',
 'su': False,
 'th': False,
 'tu': False,
 'user_id': 1,
 'we': False,
 'week_list': False}
"""

class crm_meeting(osv.Model):
    """ Model for CRM meetings """
    _inherit = 'crm.meeting'
    
    def _org_att_search(self, cr, uid, ids_i, name, args, context):
        ids = []
        args_organizer = []
        args_attendee = []
        if args:
            for arg in args:
                args_attendee.append(('cn',arg[1],arg[2]))
            attendee_ids = self.pool.get('calendar.attendee').search(cr, uid, args_attendee)
            attendees = self.pool.get('calendar.attendee').browse(cr, uid, attendee_ids)
            
            for attendee in attendees:
                for meeting in attendee.meeting_ids:
                    ids.append(meeting.id)
            
            for arg in args:
                args_organizer.append(('organizer',arg[1],arg[2]))
            organizer_ids = self.search(cr, uid, args_organizer)
            for org in organizer_ids:
                if not isinstance(org, basestring):
                    ids.append(org)
                else:
                    ids.append(int(re.search('\d+',org).group()))
        
            if ids:
                return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]
    
    _columns = {
        #'org_att_search': fields.function(_org_att_search, type="one2many", relation="calendar.event", string='Organizer or Attendee', fnct_search=_org_att_search),
    }
  
    def write(self, cr,uid, ids, vals, context=None):
        meeting_id = super(crm_meeting, self).write(cr, uid, ids, vals, context=context)
        if isinstance(ids, str) == False:
            if ('date' in vals or 'date_deadline' in vals or 'location' in vals) and ids:
                meeting_id = self.browse(cr, uid, ids)[0]
                translation_obj = self.pool.get('ir.translation')
                for attendee in meeting_id.attendee_ids:
                    mail_to = ""
                    if attendee.email != '' or attendee.email != False:
                        mail_to = attendee.email
                    
                    jp_config_obj = self.pool.get('jp.config.settings')
                    jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
                    jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
                    jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
                    url_ac = "http://%s/wp-content/plugins/jobsplus-integration/api/accept_meeting.php?attendee_id=%s&status=accepted"%(jp_www, attendee.id)
                    url_de = "http://%s/wp-content/plugins/jobsplus-integration/api/accept_meeting.php?attendee_id=%s&status=declined"%(jp_www, attendee.id)
                    url_te = "http://%s/wp-content/plugins/jobsplus-integration/api/accept_meeting.php?attendee_id=%s&status=tentative"%(jp_www, attendee.id)
                    
                    url = ("http://%s/?db=%s#id=%s&view_type=form&model=crm.meeting")%(jp_crm, cr.dbname, meeting_id.id)
                    if mail_to is not "":
                        users_obj = self.pool.get('res.users')
                        subject = "Meeting details changed: %s"
                        body = "Please be informed that meeting details have been changed<br/>Place: %s<br/>Start date: %s<br/>Duration: %s<br/><a href='%s'>Accept...</a><br/><a href='%s'>Tentative...</a><br/><a href='%s'>Reject...</a><br/><a href='%s'>Propose a new date</a>"
                        
                        if attendee.partner_id.lang == 'pl_PL':
                            transl = translation_obj.search(cr, uid, [('src','=',body)])
                            transl_sub = translation_obj.search(cr, uid, [('src','=',subject)])
                            if transl:
                                trans = translation_obj.browse(cr, uid, transl)[0]
                                body = trans.value
                            if transl_sub:
                                trans_sub = translation_obj.browse(cr, uid, transl_sub)[0]
                                subject = trans_sub.value
                              
                        uid = users_obj.search(cr, uid, [('id','=',1)])[0]
                        uid_id = users_obj.browse(cr, uid, uid)
                        email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
                        meeting_date = (fields.datetime.context_timestamp(cr, uid, datetime.strptime(meeting_id.date, '%Y-%m-%d %H:%M:%S'), context=context)).strftime('%Y-%m-%d %H:%M')
                        
                        if meeting_id.location == False:
                            meeting_location = ''
                        else:
                            meeting_location = meeting_id.location
                            
                        value = {'email_from': email_from,
                                'email_to': mail_to,
                                'state': 'outgoing',
                                'subject': subject % (meeting_id.name),
                                'body_html': body % (meeting_location,meeting_date,meeting_id.duration,url_ac,url_te,url_de,url),
                                'auto_delete': True}
                                
                        self.pool.get('mail.mail').create(cr, uid, value, context=context)

        return True
        
    def unlink(self, cr, uid, ids, context=None):
        #pdb.set_trace()
        meeting_id = []
        meeting_id = ids
        if ids:
            meeting_date = ''
            if isinstance(ids[0], basestring):
                ids = [int(re.search('\d+',ids[0]).group())]
                meeting_date = datetime.strptime(re.search('2\d+',meeting_id[0]).group(), '%Y%m%d%H%M%S')
                meeting_date = fields.datetime.context_timestamp(cr, uid, meeting_date, context=context)
                meeting_date = meeting_date.strftime('%Y-%m-%d %H:%M:%S')
            meeting = self.browse(cr, uid, ids)[0]
            attendee_obj = self.pool.get('calendar.attendee')
            attendee = attendee_obj.search(cr, uid, [('meeting_ids','=',meeting.id)])
            if meeting_date is '':
                meeting_date = fields.datetime.context_timestamp(cr, uid, datetime.strptime(meeting.date, "%Y-%m-%d %H:%M:%S"), context=context)
                meeting_date = meeting_date.strftime('%Y-%m-%d %H:%M:%S')
            
            translation_obj = self.pool.get('ir.translation')
            for user in attendee_obj.browse(cr, uid, attendee):
                mail_to = ""
                if user.partner_id.email and user.user_id.active is True:
                    mail_to += user.partner_id.email+", "
            
                if mail_to is not "":
                    users_obj = self.pool.get('res.users')
                    subject = "Meeting canceled: %s"
                    body = "Meeting %s has been canceled<br/>Start date: %s<br/>Duration: %s"
                    uid = users_obj.search(cr, uid, [('id','=',uid)])[0]
                    uid_id = users_obj.browse(cr, uid, uid)
                    
                    if user.partner_id.lang == 'pl_PL':
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
                            'subject': subject % (meeting.name),
                            'body_html': body % (meeting.name, meeting_date, meeting.duration),
                            'auto_delete': True}
                            
                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
                
        return super(crm_meeting, self).unlink(cr, uid, meeting_id, context)
        
    def _check_meeting_colision(self, cr, uid, date, date_deadline, organizer, id=0, context=None):
        meeting_obj = self.pool.get('crm.meeting')
        
        search_domain = [('organizer','=', organizer),('date','<', date_deadline),('date_deadline','>',date_deadline)]
        meeting_ids = meeting_obj.search(cr, uid, search_domain, context=context)
        self._check_meeting_list(cr, uid, meeting_ids, id, context=context)
        
        search_domain = [('organizer','=', organizer),('date','<=', date),('date_deadline','>', date)]
        meeting_ids = meeting_obj.search(cr, uid, search_domain, context=context)
        self._check_meeting_list(cr, uid, meeting_ids, id, context=context)
        
        search_domain = [('organizer','=', organizer),('date','>', date),('date_deadline','<', date_deadline)]
        meeting_ids = meeting_obj.search(cr, uid, search_domain, context=context)
        self._check_meeting_list(cr, uid, meeting_ids, id, context=context)
        
        search_domain = [('organizer','=', organizer),('date','<=', date),('date_deadline','>', date_deadline)]
        meeting_ids = meeting_obj.search(cr, uid, search_domain, context=context)
        self._check_meeting_list(cr, uid, meeting_ids, id, context=context)
        
    def _check_meeting_list(self, cr, uid, ids, id, context=None):
        if(ids):
            if(len(ids) == 1):
                if(ids[0] != id):
                    raise osv.except_osv(_("Meetings colision!","You planned already meeting for that timeframe"))
            else:
                raise osv.except_osv(_("Meetings colision!","You planned already meeting for that timeframe"))
