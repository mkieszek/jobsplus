#  -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time

from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from openerp import tools, SUPERUSER_ID

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from base_calendar import get_real_ids, base_calendar_id2real_id
from openerp.addons.base_status.base_state import base_state

import pdb
#
# crm.meeting is defined here so that it may be used by modules other than crm,
# without forcing the installation of crm.
#

class crm_meeting_type(osv.Model):
    _name = 'crm.meeting.type'
    _description = 'Meeting Type'
    _columns = {
        'name': fields.char('Name', size=64, required=True, translate=True),
    }

class crm_meeting(base_state, osv.Model):
    """ Model for CRM meetings """
    _name = 'crm.meeting'
    _description = "Spotkanie"
    _order = "id desc"
    _inherit = ["calendar.event", "mail.thread", "ir.needaction_mixin"]
    
    def _user_partner_id(self, cr, uid, ids, name, arg, context=None):
        vals={}
        #pdb.set_trace()
        partner = self.pool.get('res.users').search(cr, uid, [('id','=',uid)], context=context)
        partner_id = self.pool.get('res.users').browse(cr, uid, partner)[0].partner_id.id
        
        for id in ids:
            vals[id]=partner_id
        
        return vals
        
        
    def _my_attendee_search(self, cr, uid, obj, name, args, context):
        ids=[]
        ids_ok=[]
        args = []
        #pdb.set_trace()
        
        for cond in args:
            args.append(('id',cond[1],cond[2]))    
        partner = self.pool.get('res.users').search(cr, uid, [('id','=',uid)], context=context)
        partner_id = self.pool.get('res.users').browse(cr, uid, partner)[0].partner_id.id
        
        ids.append(self.search(cr, uid, [('partner_ids','=',partner_id)]))
        
        ids = ids[0]
        if ids:
            for idx, val in enumerate(ids):
                if type(val) is str:
                    ids[idx] = int(val[:val.index('-')])
                    
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]
        
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
        'name': fields.char('Meeting Subject', size=128, required=True, states={'done': [('readonly', True)]}),
        'categ_ids': fields.many2many('crm.meeting.type', 'meeting_category_rel',
            'event_id', 'type_id', 'Tags'),
        'attendee_ids': fields.many2many('calendar.attendee', 'meeting_attendee_rel',\
                            'event_id', 'attendee_id', 'Attendees', states={'done': [('readonly', True)]}),
        'my_partner_id': fields.function(_user_partner_id, type="integer", string='Partner', fnct_search=_my_attendee_search),

    }
    _defaults = {
        'state': 'open',
        'alarm_id': lambda self, cr, uid, ctx: self.pool.get('res.alarm').search(cr, uid, [('trigger_duration','=',15),('trigger_interval','=','minutes')], context=ctx),
    }
    def create(self, cr, uid, vals, context=None):
        
        user_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        user = user_obj.search(cr, uid, [('id','=',uid)], context=context)
        partner_id = user_obj.browse(cr, uid, user)[0].partner_id.id
        
        partner_ids = vals['partner_ids'][0][2]
        x = 0
        for partner in partner_ids:
            if partner == partner_id:
                x = 0
        #Add user to attendee
        #if x != 1:
        #    partner_ids.append(partner_id)
        
        #check if res.partner is a mail group and add members of that group to the meeting
        member_ids = []
        group_ids = []
        for partner_row in vals['partner_ids'][0][2]:
            partner = partner_obj.browse(cr, uid, partner_row)
            if partner.is_group:
                group_ids.append(partner_row)
                for member in partner.group_ids:
                    member_ids.append(member.id)
            else:
                member_ids.append(partner.id)
        
        partners = list(set(member_ids))
        
        vals['partner_ids'] = [[6, False, partners]]
        
        meeting = super(crm_meeting, self).create(cr, uid, vals, context=context)
        self.message_subscribe(cr, uid, [meeting], partners, context=context)
        
        return meeting
        
    def write(self, cr, uid, ids, vals, context=None):
        #pdb.set_trace()
        if ('partner_ids' in vals):
            partner_obj = self.pool.get('res.partner')
            member_ids = []
            group_ids = []
            for partner_row in vals['partner_ids'][0][2]:
                partner = partner_obj.browse(cr, uid, partner_row)
                if partner.is_group:
                    group_ids.append(partner_row)
                    for member in partner.group_ids:
                        member_ids.append(member.id)
                else:
                    member_ids.append(partner.id)
        
            partners = list(set(member_ids))
        
            vals['partner_ids'] = [[6, False, partners]]
            
            self.message_subscribe(cr, uid, ids, vals['partner_ids'][0][2], context=context)
        
        meeting = super(crm_meeting, self).write(cr, uid, ids, vals, context=context)
        """
        meeting_id = self.browse(cr, uid, ids)[0]
        if ("date" in vals) or ("location" in vals):
            if ("date" in vals):
                date_start = fields.datetime.context_timestamp(cr, uid, datetime.strptime(vals['date'], tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context).strftime("%Y-%m-%d %H:%M:%S")
                date_deadline = fields.datetime.context_timestamp(cr, uid, datetime.strptime(vals['date_deadline'], tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context).strftime("%Y-%m-%d %H:%M:%S")
                if ("location" in vals):
                    location = vals['location']
                elif (meeting_id.location == False):
                    location = "---"
                else:
                    location = meeting_id.location
            elif ("location" in vals):
                date_start = fields.datetime.context_timestamp(cr, uid, datetime.strptime(meeting_id.date, tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context).strftime("%Y-%m-%d %H:%M:%S")
                date_deadline = fields.datetime.context_timestamp(cr, uid, datetime.strptime(meeting_id.date_deadline, tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context).strftime("%Y-%m-%d %H:%M:%S")
                location = vals['location']
                
            subject = _("Change details of meeting: %s")%(meeting_id.name)
            body = _('Change details of meeting: %s <br/> <li>Start: %s <br/> <li>Deadline: %s<br/><li>Location: %s')%(meeting_id.name,date_start,date_deadline,location)
            
            self.message_post(cr, uid, ids[0], body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                                parent_id=False, attachments=None, context=context, content_subtype='html')
        """
        return meeting
        
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        if context is None:
            context = {}
        new_args = []
        partner_args = []        
         
        for arg in args:
            if arg[0] not in ('participant', unicode('participant')):
                new_args.append(arg)
            else:
                partner_args.append(arg)
        
        res = super(crm_meeting, self).search(cr, uid, new_args, offset=0, limit=0, order=order, context=context, count=False)
          
        new_res = []
        if(partner_args):
            partner = self.pool.get('res.users').search(cr, uid, [('id','=',partner_args[0][2])], context=context)
            partner_id = self.pool.get('res.users').browse(cr, uid, partner)[0].partner_id.id
            
            for meeting in self.browse(cr, uid, res):
                for partner in meeting.partner_ids:
                    if(partner.id == partner_id):
                        new_res.append(meeting.id)
                
            return new_res
        else:
            return res
        
        
    def message_get_subscription_data(self, cr, uid, ids, context=None):
        res = {}
        for virtual_id in ids:
            real_id = base_calendar_id2real_id(virtual_id)
            result = super(crm_meeting, self).message_get_subscription_data(cr, uid, [real_id], context=context)
            res[virtual_id] = result[real_id]
        return res

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default['attendee_ids'] = False
        return super(crm_meeting, self).copy(cr, uid, id, default, context)

    def onchange_partner_ids(self, cr, uid, ids, value, context=None):
        """ The basic purpose of this method is to check that destination partners
            effectively have email addresses. Otherwise a warning is thrown.
            :param value: value format: [[6, 0, [3, 4]]]
        """
        res = {'value': {}}
        if not value or not value[0] or not value[0][0] == 6:
            return
        res.update(self.check_partners_email(cr, uid, value[0][2], context=context))
        return res

    def check_partners_email(self, cr, uid, partner_ids, context=None):
        """ Verify that selected partner_ids have an email_address defined.
            Otherwise throw a warning. """
        partner_wo_email_lst = []
        for partner in self.pool.get('res.partner').browse(cr, uid, partner_ids, context=context):
            if not partner.email:
                partner_wo_email_lst.append(partner)
        if not partner_wo_email_lst:
            return {}
        warning_msg = _('The following contacts have no email address :')
        for partner in partner_wo_email_lst:
            warning_msg += '\n- %s' % (partner.name)
        return {'warning': {
                    'title': _('Email addresses not found'),
                    'message': warning_msg,
                    }
                }
    # ----------------------------------------
    # OpenChatter
    # ----------------------------------------

    # shows events of the day for this user
    def _needaction_domain_get(self, cr, uid, context=None):
        return [('date', '<=', time.strftime(DEFAULT_SERVER_DATE_FORMAT + ' 23:59:59')), ('date_deadline', '>=', time.strftime(DEFAULT_SERVER_DATE_FORMAT + ' 23:59:59')), ('user_id', '=', uid)]

    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                        subtype=None, parent_id=False, attachments=None, context=None, **kwargs):
        if isinstance(thread_id, str):
            thread_id = get_real_ids(thread_id)
        return super(crm_meeting, self).message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, **kwargs)

class mail_message(osv.osv):
    _inherit = "mail.message"

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        '''
        convert the search on real ids in the case it was asked on virtual ids, then call super()
        '''
        for index in range(len(args)):
            if args[index][0] == "res_id" and isinstance(args[index][2], str):
                args[index][2] = get_real_ids(args[index][2])
        return super(mail_message, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def _find_allowed_model_wise(self, cr, uid, doc_model, doc_dict, context=None):
        if doc_model == 'crm.meeting':
            for virtual_id in self.pool.get(doc_model).get_recurrent_ids(cr, uid, doc_dict.keys(), [], context=context):
                doc_dict.setdefault(virtual_id, doc_dict[get_real_ids(virtual_id)])
        return super(mail_message, self)._find_allowed_model_wise(cr, uid, doc_model, doc_dict, context=context)

class ir_attachment(osv.osv):
    _inherit = "ir.attachment"

    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        '''
        convert the search on real ids in the case it was asked on virtual ids, then call super()
        '''
        for index in range(len(args)):
            if args[index][0] == "res_id" and isinstance(args[index][2], str):
                args[index][2] = get_real_ids(args[index][2])
        return super(ir_attachment, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

    def write(self, cr, uid, ids, vals, context=None):
        '''
        when posting an attachment (new or not), convert the virtual ids in real ids.
        '''
        if isinstance(vals.get('res_id'), str):
            vals['res_id'] = get_real_ids(vals.get('res_id'))
        return super(ir_attachment, self).write(cr, uid, ids, vals, context=context)

class invite_wizard(osv.osv_memory):
    _inherit = 'mail.wizard.invite'

    def default_get(self, cr, uid, fields, context=None):
        '''
        in case someone clicked on 'invite others' wizard in the followers widget, transform virtual ids in real ids
        '''
        result = super(invite_wizard, self).default_get(cr, uid, fields, context=context)
        if 'res_id' in result:
            result['res_id'] = get_real_ids(result['res_id'])
        return result
