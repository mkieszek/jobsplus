# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 09:29:53 2013

@author: mbereda
"""


from datetime import datetime, timedelta, date
from openerp.osv import fields, osv
import pdb
import pytz
import time

class jp_meeting2deal(osv.Model):
    _name = "jp.meeting2deal"
    #_inherit = ["calendar.event", "mail.thread", "ir.needaction_mixin", "crm.meeting"]
    
    def _tz_get(self, cr, uid, context=None):
        return [(x.lower(), x) for x in pytz.all_timezones]
    
    
    def onchange_dates(self, cr, uid, ids, start_date, duration=False, end_date=False, allday=False, context=None):
        """Returns duration and/or end date based on values passed
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user's ID for security checks,
        @param ids: List of calendar event's IDs.
        @param start_date: Starting date
        @param duration: Duration between start date and end date
        @param end_date: Ending Datee
        @param context: A standard dictionary for contextual values
        """
        if context is None:
            context = {}

        value = {}
        if not start_date:
            return value
        if not end_date and not duration:
            duration = 1.00
            value['duration'] = duration

        start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if allday: # For all day event
            duration = 24.0
            value['duration'] = duration
            # change start_date's time to 00:00:00 in the user's timezone
            user = self.pool.get('res.users').browse(cr, uid, uid)
            tz = pytz.timezone(user.tz) if user.tz else pytz.utc
            start = pytz.utc.localize(start).astimezone(tz)     # convert start in user's timezone
            start = start.replace(hour=0, minute=0, second=0)   # change start's time to 00:00:00
            start = start.astimezone(pytz.utc)                  # convert start back to utc
            start_date = start.strftime("%Y-%m-%d %H:%M:%S")
            value['date'] = start_date

        if end_date and not duration:
            end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            diff = end - start
            duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
            value['duration'] = round(duration, 2)
        elif not end_date:
            end = start + timedelta(hours=duration)
            value['date_deadline'] = end.strftime("%Y-%m-%d %H:%M:%S")
        elif end_date and duration and not allday:
            # we have both, keep them synchronized:
            # set duration based on end_date (arbitrary decision: this avoid
            # getting dates like 06:31:48 instead of 06:32:00)
            end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
            diff = end - start
            duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
            value['duration'] = round(duration, 2)

        return {'value': value}

    def onchange_partner_id(self, cr, uid, ids, partner_id,context=None):
        """
        Make entry on email and availbility on change of partner_id field.
        @param cr: the current row, from the database cursor
        @param uid: the current user's ID for security checks
        @param ids: list of calendar attendee's IDs
        @param partner_id: changed value of partner id
        @param context: a standard dictionary for contextual values
        @return: dictionary of values which put value in email and availability fields
        """
        
        if not partner_id:
            return {'value': {'email': ''}}
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        return {'value': {'email': partner.email}}
    
    _columns = {
        # base_state required fields
        'create_date': fields.datetime('Creation Date', readonly=True),
        'write_date': fields.datetime('Write Date', readonly=True),
        'date_open': fields.datetime('Confirmed', readonly=True),
        'date_closed': fields.datetime('Closed', readonly=True),
        'partner_ids': fields.many2many('res.partner', 'crm_meeting_partner_rel', 'meeting_id', 'partner_id',
            string='Attendees', states={'done': [('readonly', True)]}),
        'state': fields.selection(
                    [('draft', 'Unconfirmed'), ('open', 'Confirmed')],
                    string='Status', size=16, readonly=True, track_visibility='onchange'),
        # Meeting fields
        'name': fields.char('Meeting Subject', size=128, required=True, readonly=True),
        'categ_ids': fields.many2many('crm.meeting.type', 'meeting_category_rel',
            'event_id', 'type_id', 'Tags'),
        'attendee_ids': fields.many2many('calendar.attendee', 'meeting_attendee_rel',\
                            'event_id', 'attendee_id', 'Attendees', states={'done': [('readonly', True)]}),
        
        'candidate_id': fields.many2one('jp.candidate','Candidate', readonly=True),
        'deal_id': fields.many2one('jp.deal','Deal', readonly=True),
        'date': fields.datetime('Date meeting', required=True,),
        'date_deadline': fields.datetime('Date deadline'),
        'allday': fields.boolean('All Day', states={'done': [('readonly', True)]}),
        'mo': fields.boolean('Mon'),
        'tu': fields.boolean('Tue'),
        'we': fields.boolean('Wed'),
        'th': fields.boolean('Thu'),
        'fr': fields.boolean('Fri'),
        'sa': fields.boolean('Sat'),
        'su': fields.boolean('Sun'),
        'duration': fields.float('Duration', states={'done': [('readonly', True)]}),
        'description': fields.text('Description', states={'done': [('readonly', True)]}),
        'organizer': fields.char("Organizer", size=256, states={'done': [('readonly', True)]}),
        'user_id': fields.many2one('res.users', 'Responsible', states={'done': [('readonly', True)]}),
        'recurrency': fields.boolean('Recurrent', help="Recurrent Meeting"),
        'week_list': fields.selection([
            ('MO', 'Monday'),
            ('TU', 'Tuesday'),
            ('WE', 'Wednesday'),
            ('TH', 'Thursday'),
            ('FR', 'Friday'),
            ('SA', 'Saturday'),
            ('SU', 'Sunday')], 'Weekday'),
        'byday': fields.selection([
            ('1', 'First'),
            ('2', 'Second'),
            ('3', 'Third'),
            ('4', 'Fourth'),
            ('5', 'Fifth'),
            ('-1', 'Last')], 'By day'),
        'class': fields.selection([('public', 'Public'), ('private', 'Private'), \
             ('confidential', 'Public for Employees')], 'Privacy', states={'done': [('readonly', True)]}),
        'location': fields.char('Location', size=264, help="Location of Event", states={'done': [('readonly', True)]}),
        'recurrent_id': fields.integer('Recurrent ID'),
        'recurrent_id_date': fields.datetime('Recurrent ID date'),
        'end_date': fields.date('Repeat Until'),
        'end_type' : fields.selection([('count', 'Number of repetitions'), ('end_date','End date')], 'Recurrence Termination'),
        'interval': fields.integer('Repeat Every', help="Repeat every (Days/Week/Month/Year)"),
        'day': fields.integer('Date of month'),
        'count': fields.integer('Repeat', help="Repeat x times"),
        'alarm_id': fields.many2one('res.alarm', 'Reminder', states={'done': [('readonly', True)]},
                        help="Set an alarm at this time, before the event occurs" ),
        'select1': fields.selection([('date', 'Date of month'),
                                    ('day', 'Day of month')], 'Option'),
        'rrule_type': fields.selection([
            ('daily', 'Day(s)'),
            ('weekly', 'Week(s)'),
            ('monthly', 'Month(s)'),
            ('yearly', 'Year(s)')
            ], 'Recurrency', states={'done': [('readonly', True)]},
            help="Let the event automatically repeat at that interval"),
        'show_as': fields.selection([('free', 'Free'), ('busy', 'Busy')], \
                                                'Show Time as', states={'done': [('readonly', True)]}),
        'rrule': fields.char('Recurrent Rule'),
    }
    
    _defaults = {
        'state': 'open',
    }    
    
    def default_get(self, cr, uid, application_id, context=None):
        """
        This function gets default values
        """        
        #pdb.set_trace()
        res = super(jp_meeting2deal, self).default_get(cr, uid, application_id, context=context)
        application_id = context and context.get('active_id', False) or False   
        
        application = self.pool.get('jp.application').browse(cr,uid,[application_id], context=context)[0]
        candidate_id = application.candidate_id and application.candidate_id.id or False
        
        deal_id = application.deal_id and application.deal_id.id or False
        res.update({'deal_id': deal_id})
        res.update({'candidate_id': candidate_id})
        
        deal_title = application.deal_id and application.deal_id.title or False
        candidate_candidate = application.candidate_id and application.candidate_id.candidate or False
        res.update({'name': 'Spotkanie z %s dla %s'%(candidate_candidate,deal_title)})
        return res
        
    def add_meeting(self, cr, uid, application_id, context=None):
        #pdb.set_trace()
        
        w = self.browse(cr, uid, application_id, context=context)[0]
        application_id = context and context.get('active_id', False) or False   
        application = self.pool.get('jp.application').browse(cr,uid,[application_id], context=context)[0]
        candidate_id = application.candidate_id and application.candidate_id.id or False
        deal_id = application.deal_id and application.deal_id.id or False
                
        values_meeting = {
            'deal_id': deal_id,
            'candidate_id': candidate_id,
            'name': w.name,
            'alarm_id': w.alarm_id,
            'allday': w.allday,
            'attendee_ids': [],
            'byday': w.byday,
            'categ_ids': [[6, False, []]],
            'class': 'public',
            'count': 1,
            'date': w.date,
            'date_deadline': w.date_deadline,
            'day': w.day,
            'description': w.description,
            'duration': w.duration,
            'end_date': w.end_date,
            'end_type': w.end_type,
            'fr': w.fr,
            'interval': w.interval,
            'location': w.location,
            'mo': w.mo,
            'organizer': w.organizer,
            'partner_ids': [[6, False, []]],
            'recurrency': w.recurrency,
            'recurrent_id': w.recurrent_id,
            'recurrent_id_date': w.recurrent_id_date,
            'rrule_type': w.rrule_type,
            'sa': w.sa,
            'select1': w.select1,
            'show_as': w.show_as,
            'su': w.su,
            'th': w.th,
            'tu': w.tu,
            'user_id': w.user_id,
            'we': w.we,
            'week_list': w.week_list,
        }
        self.pool.get('crm.meeting').create(cr,uid,values_meeting,context=context)        
        
        values_application = {
            'state': '2'        
        }
        self.pool.get('jp.application').write(cr, uid, [application_id], values_application, context=context)
        