# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:18:07 2013

@author: pczorniej
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import datetime
import time
import psycopg2
import urlparse
import re
from openerp.report import report_sxw
from email.header import decode_header

def decode(text):
    """Returns unicode() string conversion of the the given encoded smtp header text"""
    if text:
        text = decode_header(text.replace('\r', ''))
        return ''.join([tools.ustr(x[0], x[1]) for x in text])

AVAILABLE_DAYS = [('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),
                 ('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),
                ('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')]
                
AVAILABLE_MONTHS = [('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),
                    ('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]
                    
AVAILABLE_FOR = [('1','Hour'),('2','Month'),('3','Work')]

class jp_candidate(osv.Model):
    _name = "jp.candidate"
    _inherit = 'mail.thread'
    _description = 'Kandydata'
    _order = "create_date desc"
    
    def _document_ids_get(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        if context is None:
            context = {}
        
        res = {}
        for candidate in self.browse(cr, uid, ids, context=context):
            attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','jp.candidate'),('res_id','=',candidate.id)], context=context)
            #attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','jp.candidate')], context=context)
                        
            res[candidate.id] = attachment_ids
        
        return res
    
    def _document_ids_search(self, cr, uid, obj, name, args, context):
        #pdb.set_trace()        
        ids = []
        args_candidate = []
        for cond in args:
            args_candidate.append(('index_content',cond[1],cond[2]))    
        
        args_candidate.append(('res_model','=','jp.candidate'))
        
        attachment_ids = self.pool.get('ir.attachment').search(cr, uid, args_candidate, context=context)
        
        for attachment in self.pool.get('ir.attachment').browse(cr, uid, attachment_ids, context=context):
            ids.append(attachment.res_id)     
            
        if ids:
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]
        
    def _application_ids_search(self, cr, uid, obj, name, args, context):
        if not args:
            args = [('application_search','ilike','a')]
        ids = []
        args_candidate_title = []
        for cond in args:
            args_candidate_title.append(('title',cond[1],cond[2]))    
        
        deal_ids = self.pool.get('jp.deal').search(cr, uid, args_candidate_title, context=context)
        deals = self.pool.get('jp.deal').browse(cr, uid, deal_ids, context=context)
        
        for deal in deals:
            for application in deal.application_ids:
                ids.append(application.candidate_id.id)
            
        if ids:
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]
        
    def _position_other_search(self, cr, uid, obj, name, args, context):
        if not args:
            args = [('position_other_search','ilike','a')]    
        ids = []
        args_candidate_title = []
        args_candidate_possition = []
        args_candidate_document = []
        
        #Deal
        for cond in args:
            args_candidate_title.append(('title',cond[1],cond[2]))    
        
        deal_ids = self.pool.get('jp.deal').search(cr, uid, args_candidate_title, context=context)
        deals = self.pool.get('jp.deal').browse(cr, uid, deal_ids, context=context)
        
        for deal in deals:
            for application in deal.application_ids:
                ids.append(application.candidate_id.id)     
        
        #Position
        for cond in args:
            args_candidate_possition.append(('current_possition',cond[1],cond[2]))    
        
        candidate_ids = self.pool.get('jp.candidate').search(cr, uid, args_candidate_possition, context=context)
        
        for candidate in self.pool.get('jp.candidate').browse(cr, uid, candidate_ids, context=context):
            ids.append(candidate.id) 
        
        #Document
        for cond in args:
            args_candidate_document.append(('index_content',cond[1],cond[2]))    
        
        args_candidate_document.append(('res_model','=','jp.candidate'))
        
        attachment_ids = self.pool.get('ir.attachment').search(cr, uid, args_candidate_document, context=context)
        
        for attachment in self.pool.get('ir.attachment').browse(cr, uid, attachment_ids, context=context):
            ids.append(attachment.res_id)
            
        if ids:
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]
        
    def _document_count(self, cr, uid, ids, name, arg, context=None):
        #pdb.set_trace()        
        val={}
        for candidate in self.browse(cr, uid, ids, context=context):
            val[candidate.id] = {
                'count_document': len(candidate.document_ids)
            }
            val[candidate.id] = len(candidate.document_ids)
        
        return val
        
    def _agreement_ids(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        val = {}
        for candidate in self.browse(cr, uid, ids, context=context):
            application_ids = self.pool.get('jp.application').search(cr, uid, [('candidate_id','=',candidate.id)], context=context)
            agreement_ids = self.pool.get('jp.agreement').search(cr, uid, [('application_id','in',application_ids)], context=context)
                    
            val[candidate.id] = agreement_ids
        
        return val
    
    def _candidate_rate_ids(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        val = {}
        for candidate in self.browse(cr, uid, ids, context=context):
            application_ids = self.pool.get('jp.application').search(cr, uid, [('candidate_id','=',candidate.id)], context=context)
            candidate_rate_ids = self.pool.get('jp.candidate.rate').search(cr, uid, [('application_id','in',application_ids)], context=context)
                    
            val[candidate.id] = candidate_rate_ids
        
        return val
    
    def _last_deal_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for candidate in self.browse(cr, uid, ids):
            if candidate.application_ids:
                last_deal = candidate.application_ids[0].deal_id
                res[candidate.id] = [last_deal.name+' - '+last_deal.title]
            else:
                res[candidate.id] = ['']
                
        return res
    
    def _get_image_icon(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for candidate in self.browse(cr, uid, ids):
            if candidate.source_receive == '1':
                res[candidate.id] = '%'
            elif candidate.source_receive == '2':
                res[candidate.id] = 's'
            elif candidate.source_receive == '3':
                res[candidate.id] = '&'
            elif candidate.source_receive == '4':
                res[candidate.id] = '2'
            else:
                res[candidate.id] = ''
        return res
        
    _columns = {
        'candidate': fields.char('Candidate', Size=64, required=True),
        'name': fields.char('ID', size=64, readonly=True),
        'notes': fields.text('Notes'),
        'year_of_birth': fields.integer('Year of birth', size=4),
        'month_of_birth': fields.selection(AVAILABLE_MONTHS,'Month of birth'),
        'day_of_birth': fields.selection(AVAILABLE_DAYS,'Day of birth'),
        'sex': fields.selection([('f','Female'),('m','Male')],'Sex'),
        'education': fields.selection([('p','Primary education'),('l','Lower secondary'),
                                      ('v','Vocational education'),('s','Secondary education'),
                                      ('h','Higher education')],'Education'),
        'nationality': fields.many2one('res.country','Nationality'),                
        'experience': fields.html('Experience'),
        'state_id' : fields.many2one('res.country.state','State'),
        'city' : fields.char('City', size=64),
        'country' :  fields.many2one('res.country', 'Country'),        
        'email' : fields.char('Email', size=40),
        'phone' : fields.char('Phone', size=15),
        'other_contact' : fields.text('Other contact'),
        'trade_ids' : fields.many2many('jp.trade', 'jp_trade_rel','candidate_id','trade_id', 'Trade'),
        'work_state' : fields.many2one('res.country.state', 'Work state'),
        'rate' : fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5')],'Rate'),
        'current_possition': fields.char('Current possition', size=100),
        'posting_date': fields.date('Date of posting'),
        'personal_id' : fields.char('Personal ID', size=25),
        'passport_id': fields.char('Passport ID', size=25),
        'application_search': fields.function(_application_ids_search, type="one2many", relation="jp.application", string="Recruitment", fnct_search=_application_ids_search),    
        'application_ids': fields.one2many('jp.application', 'candidate_id', 'Applications'),
        'document_ids': fields.function(_document_ids_get, type="one2many",relation="ir.attachment", string="Document", fnct_search=_document_ids_search),
        'candidate2deal': fields.many2one('jp.candidate2deal','Candidate'),
        'position_other_search': fields.function(_position_other_search, type="one2many", relation="jp.candidate", string='Position+', fnct_search=_position_other_search),
        'reference': fields.text("Reference"),
        'amount': fields.integer('Amount'),
        'currency_id': fields.many2one('res.currency', 'Currency', track_visibility='onchange'),
        'financial_for': fields.selection(AVAILABLE_FOR, 'For'),
        'count_document': fields.function(_document_count, type="integer", string='Count document'),
        'agreement_ids': fields.function(_agreement_ids, type="one2many", relation="jp.agreement", string='Application'),
        'create_date': fields.date('Create'),
        'portal_id': fields.many2one('jp.portal','Portal'),
        'source_receive': fields.selection([('1', 'Mail'),('2', 'Outlook'),('3', 'Manual'),('4', "www")],'Source receive'),
        'sallary_id': fields.many2one('jp.sallary','Sallary'),
        'last_deal_id': fields.function(_last_deal_id, type="string", string="Last Deal"),
        'ad_id': fields.many2one('jp.ad', "Ad"),
        'image_icon': fields.function(_get_image_icon, type='char', string='Source receive'),
        'email_title': fields.char('Email title', readonly=True),
    }
    
    
    def create(self, cr, uid, vals, context=None):
        #pdb.set_trace()
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.candidate') or '/'
        
        manual_ids = self.pool.get('jp.portal').search(cr, uid, [('name', '=','Manual')], context=context)
        if manual_ids:
            vals['source_receive'] = self.pool.get('jp.portal').search(cr, uid, [('name','=','Manual')], context=context)[0]
            
        candidate_id = super(jp_candidate, self).create(cr, uid, vals, context=context)
        
        return candidate_id
    
    def copy(self, cr, uid, ids, vals, context=None):
        raise osv.except_osv(decode('Błąd'), decode('Opcja niedostępna'))
        return True
        
    def name_get(self, cr, uid, ids, context=None):
         """Overrides orm name_get method"""
         if not isinstance(ids, list) :
             ids = [ids]
         res = []
         if not ids:
             return res
        
         reads = self.read(cr, uid, ids, ['name', 'candidate'], context)

         for record in reads:
             name = record['name']
             title = record['candidate']
             res.append((record['id'], name + ' - ' + title))
         return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            #name = name.split(' / ')[-1]
            name_ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            candidate_ids = self.search(cr, uid, [('candidate', operator, name)] + args, limit=limit, context=context)
            ids=name_ids+candidate_ids
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
        
    def open_line(self, cr, uid, id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Candidate', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': id[0],
            'target': 'self',
        }
        
    def marge_candidates(self, cr, uid, from_int, to_int, context=None):
        application_obj = self.pool.get('jp.application')
        attachment_obj = self.pool.get('ir.attachment')
        conn = psycopg2.connect(database=cr.dbname)
        cur = conn.cursor()
        query = ("SELECT count(email), email FROM jp_candidate GROUP BY email HAVING count(email) >= %s and count(email) <= %s")%(from_int, to_int)
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        emails = []
        for row in rows:
            emails.append(row[1])

        for email in emails:
            email_ids = self.search(cr, uid, [('email','=',email)])
            email = self.browse(cr, uid, email_ids)
            for cand in email:
                email.remove(cand)
                if len(cand.document_ids) > 0:
                    for cand2 in email:
                        if len(cand2.document_ids) == len(cand.document_ids):
                            ok = 0
                            for document in cand.document_ids:
                                for doc in cand2.document_ids:
                                    if document.name == doc.name and document.file_size == doc.file_size and len(cand.document_ids) == len(cand2.document_ids):
                                        ok += 1
                            if ok == len(cand.document_ids):
                                app_cand2_ids = application_obj.search(cr, uid, [('candidate_id','=', cand2.id)])
                                if app_cand2_ids:
                                    for app_cand2 in app_cand2_ids:
                                        vals = {
                                            'candidate_id': cand.id,
                                        }
                                        application_obj.write(cr, uid, app_cand2, vals, context=None)
                                if cand2.experience != False or cand2.reference != False or cand2.notes != False:
                                    vals = {}
                                    if cand.experience == False:
                                        vals['experience'] = cand2.experience
                                    else:
                                        vals['experience'] = cand.experience+cand2.experience
                                    if cand.reference == False:
                                        vals['reference'] = cand2.reference
                                    else:
                                        vals['reference'] = cand.reference+cand2.reference
                                    if cand.notes == False:
                                        vals['notes'] = cand2.notes
                                    else:
                                        vals['notes'] = cand.notes+cand2.notes
                                            
                                    self.write(cr, uid, cand.id, vals, context=None)
                                self.unlink(cr, uid, [cand2.id], context=None)
                                email.remove(cand2)
                            else:
                                if cand.candidate == cand2.candidate and cand.last_deal_id == cand2.last_deal_id and cand.phone == cand2.phone and cand.state_id.id == cand2.state_id.id:
                                    if cand2.experience != False or cand2.reference != False or cand2.notes != False:
                                        vals = {}
                                        if cand.experience == False:
                                            vals['experience'] = cand2.experience
                                        else:
                                            vals['experience'] = cand.experience+cand2.experience
                                        if cand.reference == False:
                                            vals['reference'] = cand2.reference
                                        else:
                                            vals['reference'] = cand.reference+cand2.reference
                                        if cand.notes == False:
                                            vals['notes'] = cand2.notes
                                        else:
                                            vals['notes'] = cand.notes+cand2.notes
                                                
                                        self.write(cr, uid, cand.id, vals, context=None)
                                    for document in cand2.document_ids:
                                        document_vals = {}
                                        document_vals['res_id'] = cand.id
                                        attachment_obj.write(cr, uid, document.id, document_vals, context=None)
                                    for application in cand2.application_ids:
                                        application_obj.write(cr, uid, [application.id], {'candidate_id': cand.id})
                                    self.unlink(cr, uid, [cand2.id], context=None)
                                    email.remove(cand2)
                        else:
                            if cand.candidate == cand2.candidate and cand.last_deal_id == cand2.last_deal_id and cand.phone == cand2.phone and cand.state_id.id == cand2.state_id.id:
                                if cand2.experience != False or cand2.reference != False or cand2.notes != False:
                                    vals = {}
                                    if cand.experience == False:
                                        vals['experience'] = cand2.experience
                                    else:
                                        vals['experience'] = cand.experience+cand2.experience
                                    if cand.reference == False:
                                        vals['reference'] = cand2.reference
                                    else:
                                        vals['reference'] = cand.reference+cand2.reference
                                    if cand.notes == False:
                                        vals['notes'] = cand2.notes
                                    else:
                                        vals['notes'] = cand.notes+cand2.notes
                                            
                                    self.write(cr, uid, cand.id, vals, context=None)
                                for document in cand2.document_ids:
                                    document_vals = {}
                                    document_vals['res_id'] = cand.id
                                    attachment_obj.write(cr, uid, document.id, document_vals, context=None)
                                for application in cand2.application_ids:
                                    application_obj.write(cr, uid, [application.id], {'candidate_id': cand.id})
                                self.unlink(cr, uid, [cand2.id], context=None)
                                email.remove(cand2)
                                    
        return True
    
    def application_unlink(self, cr, uid, context=None):
        conn = psycopg2.connect(database=cr.dbname)
        cur = conn.cursor()
        query = ("SELECT count(candidate_id), candidate_id, deal_id FROM jp_application GROUP BY candidate_id, deal_id HAVING count(candidate_id) > 1")
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        candidates = []
        for row in rows:
            candidates.append(row[1])
            
        application_obj = self.pool.get('jp.application')
        apps = []
        
        for candidate in self.browse(cr, uid, candidates):
            for app in candidate.application_ids:
                apps.append(app)
            for application in apps:
                apps.remove(application)
                for application2 in apps:
                    if application.deal_id.id == application2.deal_id.id and application.status == application2.status:
                        application_obj.unlink(cr, uid, [application2.id])
        
        empty_app_ids = application_obj.search(cr, uid, [('candidate_id','=',False)])
        application_obj.unlink(cr, uid, empty_app_ids)
            
        return True
    
    def report(self, cr, uid, ids, vals, context=None):
        self.pool.get('jp.report.recruitment').calculate_report_recruitment(cr ,uid, context=context)
        return True
    
    def open_candidate(self, cr, uid, id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Candidate', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'jp.candidate',
            'res_id': id[0],
            'target': 'new',
            'context': context,
        }
        
    def message_new(self, cr, uid, msg_dict, custom_values=None, context=None):
        if context is None:
            context = {}
        data = {}
        if isinstance(custom_values, dict):
            data = custom_values.copy()
        model = context.get('thread_model') or self._name
        model_pool = self.pool.get(model)
        fields = model_pool.fields_get(cr, uid, context=context)
        if 'name' in fields and not data.get('name'):
            data['name'] = msg_dict.get('subject', '')
        if model == 'jp.candidate':
            email = msg_dict.get('email_from')
            candidate_email = self.get_email(cr, uid, email, context=None)
            if email != None:
                data['email'] = candidate_email
                data['candidate'] = candidate_email
                data['source_receive'] = '1'
                data['email_title'] = msg_dict.get('subject')
                if msg_dict.get('subject') != None:
                    ad_id = self.get_ad(cr, uid, msg_dict.get('subject'), context=None)
                    if ad_id != False:
                        data['ad_id'] = ad_id
                del data['name']
            attachments = msg_dict['attachments']
            x = 0
            for attach in attachments:
                if attach[0].find("?") > 0:
                    attach_name = re.search(r'[\w]+\.[\w]+',attach[0])
                    if attach_name != None:
                        attach = (attach_name.group(), attach[1])
                        attachments[x] = attach
                x += 1
        if msg_dict.get('email_from') != None:
            res_id = model_pool.create(cr, uid, data, context=context)
            if model == 'jp.candidate' and ad_id != False:
                deal_id = model_pool.browse(cr, uid, res_id).ad_id.deal_id.id
                vals = {}
                vals = {
                        'deal_id': deal_id,
                        'candidate_id': res_id
                        }
                
                self.pool.get('jp.application').create(cr, uid, vals, context=None)
        else:
            res_id = False
        return res_id
    
    def get_email(self, cr, uid, email_from, context=None):
        email = re.search(r'[\w\.-]+@[\w\.-]+', email_from).group()
        return email
    
    def get_candidate_name(self, cr, uid, email_from, context=None):
        if not email_from.index('Gumtree'):
            candidate_name = re.search(r'\w+ \w+', email_from)
            if candidate_name != None:
                candidate_name = candidate_name.group()
            else:
                candidate_name = False
        else:
            candidate_name = False
        return candidate_name
        
    def get_ad(self, cr, uid, subject, context=None):
        ad_obj = self.pool.get('jp.ad')
        subject_ad = re.search('AD\d{4,5}', subject)
        if subject_ad != None:
            ad = ad_obj.search(cr, uid, [('name','=',subject_ad.group())])
            if ad:
                ad_id = ad[0]
            else:
                ad_id = False
        elif re.search('\\x9e.*\\xe2', subject.encode('utf-8')) != None:
            gumtree_title = re.search('\\x9e.*\\xe2', subject.encode('utf-8')).group()
            gumtree_title = gumtree_title.replace('\x9e','')
            gumtree_title = gumtree_title.replace('\xe2','')
            ad_id = ad_obj.search(cr, uid, [('gumtree_title','=',gumtree_title)])[0]
        else:
            ad_id = False
        return ad_id
