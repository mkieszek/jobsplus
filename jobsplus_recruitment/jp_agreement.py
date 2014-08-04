# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:05:13 2013

@author: pczorniej
"""


from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import datetime
from datetime import timedelta
import calendar

AVAILABLE_DAYS = [('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),
                 ('11','11'),('12','12'),('13','13'),('14','14'),('15','15'),('16','16'),('17','17'),('18','18'),('19','19'),('20','20'),
                ('21','21'),('22','22'),('23','23'),('24','24'),('25','25'),('26','26'),('27','27'),('28','28'),('29','29'),('30','30'),('31','31')]
                
AVAILABLE_MONTHS = [('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),('6','June'),
                    ('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]
                    

TYPE_AGREEMENT = [('1','Work contract'),('2','Contract of mandate'),('3','Service contract'),('4','Other')]

class jp_agreement(osv.Model):
    _name = "jp.agreement"
    _inherit = 'mail.thread'
    _description = 'Umowe pracownicza'
    _order = 'contract_to'
    _columns = {
    'name': fields.char('ID',
                       readonly=True, 
                       size=64),
    'type_of_agreement' : fields.selection(TYPE_AGREEMENT,string='Type of agreement'),
    'amount' : fields.float('Amount'),
    'currency_id': fields.many2one('res.currency', 'Currency', track_visibility='onchange'),
    'gross_net' : fields.selection([('1','Gross'),('2','Net')],'Gross/Net'),
    'term_of_notice' : fields.selection([('1','3 days'),('2','7 days'),('3','14 days'),('4','1 month'),('5','3 months')],'Term of notice'),
    'payment_type' : fields.selection([('1','Transfer'),('2','Cash')],'Payment type'),
    'position': fields.char('Name position', Size=64, required=True),
    'deal_id': fields.many2one('jp.deal','Recruitment', required=False),
    'date_of_contract': fields.date('Date of contract'),
    'contract_from': fields.date('Contract from'),
    'contract_to': fields.date('Contract to'),
    'client_id': fields.many2one('res.partner', "Client", required=True),
    'medical_preliminary': fields.date('Preliminary medical date'),
    'medical_heights': fields.date('Heights medical date'),
    'medical_psychotechnical': fields.date('Psychotechnical medical date'),
    'medical_health': fields.date('Health medical date'),
    'agreement_number': fields.integer('Agreement number'),
    'application_id': fields.many2one('jp.application','Application'),
    'time_sheet_ids': fields.one2many('jp.time.sheet','agreement_id','Time sheet'),
    'amount_for': fields.selection([('1','Hour'),('2','Month'),('3','Work')],'For'),
    'bank_number': fields.char('Bank account number', size=64),
    'type_account_bank': fields.selection([('1','Zloty'),('2','Currency')],'Type account bank'),
    'code_swift': fields.char('Code swift', size=64),
    'status_work': fields.selection([('1','Work'),('2','Does not work')],'Work status'),
    'date_certyficate': fields.date('Date certificate of employment'),
    'send_certyficate': fields.date('Date send certyficate of employment'),
    'date_termination': fields.date('Termination date'),
    #candidate
    'first_name': fields.char('First name', size=64, required=True),
    'last_name': fields.char('Last name', size=64, required=True),
    'candidate': fields.char('Employee', Size=64),
    'year_of_birth': fields.integer('Year of birth', required=True, size=4),
    'month_of_birth': fields.selection(AVAILABLE_MONTHS,'Month of birth'),
    'day_of_birth': fields.selection(AVAILABLE_DAYS,'Day of birth'),
    'sex': fields.selection([('f','Female'),('m','Male')],'Sex'),
    'city' : fields.char('City', size=64),
    'country' :  fields.many2one('res.country', 'Country'),        
    'email' : fields.char('Email', size=40),
    'phone' : fields.char('Phone', size=15, required=True),
    'other_contact' : fields.text('Other contact'),
    'personal_id' : fields.char('Personal ID', size=25),
    'passport_id': fields.char('Passport ID', size=25),
    'candidate_id': fields.many2one('jp.candidate', 'Candidate'),
    'country_id': fields.related('client_id', 'country_id', type="many2one", relation="res.country", string="Country", readonly=True),
    }
    
    _defaults ={
        'type_account_bank': '1',
    }
    
    _order = 'contract_to'
    
    def on_change_type(self, cr, uid, ids, type_account_bank, context=None):
        #pdb.set_trace()
        values = {}
        if type_account_bank:
            if type_account_bank in '1':
                values['code_swift']=''
        else:
            values['type_account_bank']='1'
        return {'value' : values}
        
    def on_change_application(self, cr, uid, ids, application_id, context=None):
        application_obj = self.pool.get('jp.application')
        application_id = application_obj.browse(cr, uid, application_id)
        candidate = application_id.candidate_id
        
        values = {
            'last_name' : candidate.candidate,
            'city': candidate.city,
            'country': candidate.country.id,
            'personal_id': candidate.personal_id,
            'passport_id': candidate.passport_id,
            'day_of_birth' : candidate.day_of_birth,
            'month_of_birth' : candidate.month_of_birth,
            'year_of_birth' : candidate.year_of_birth,
            'sex' : candidate.sex,
            'email' : candidate.email,
            'phone' : candidate.phone,
            'other_contact' : candidate.other_contact,
        }
        return {'value' : values}
    

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.agreement') or '/'
            
        agreement_id = super(jp_agreement, self).create(cr, uid, vals, context=context)
        
        return agreement_id
        
    def notification_deadline_agreement(self, cr, uid, context=None):
        #pdb.set_trace()
        tomorrow = datetime.date.today()+timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        
        agreement_ids = self.search(cr, uid, [('status_work','=','1'),('contract_to','=',tomorrow_str)], context=context)
        
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
        
        for agreement in self.browse(cr, uid, agreement_ids, context=context):
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.agreement")%(jp_crm, cr.dbname, agreement.id)
            subject = _("Zakończenie umowy z pracownikiem")
            body = _("Uwaga, niedługo nastąpi zakończenie umowy z pracownikiem: %s %s. <br/>Data zakończenia umowy: %s<br/><a href='%s'>Link do umowy</a>")%(agreement.first_name,agreement.last_name,agreement.contract_to,url) 
            
            self.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                parent_id=False, attachments=None, context=context, content_subtype='html')
        return True
                    
    def add_months(self, sourcedate,months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month / 12 
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return datetime.date(year,month,day)   
                
    def notification_deadline_medical(self, cr, uid, context=None):
        today = datetime.date.today()
        
        agreement_obj= self.pool.get('jp.agreement')
        agreement_ids = agreement_obj.search(cr, uid, [('status_work','=','1')], context=context)
        
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
        
        for agreement in self.browse(cr, uid, agreement_ids, context=context):
            medical_preliminary = agreement.medical_preliminary
            medical_heights = agreement.medical_heights
            medical_psychotechnical = agreement.medical_psychotechnical
            medical_health = agreement.medical_health
            subject = _("Przypomnienie o badaniach lekarskich")
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.agreement")%(jp_crm, cr.dbname, agreement.id)
            if medical_preliminary:
                medical_preliminary = datetime.datetime.strptime(medical_preliminary,"%Y-%m-%d").date()
                body = _("Przypomnienie o badaniach lekarskich dla pracownika: %s %s<br/>Data badań wstępnych: %s<br/><a href='%s'>Link do Pracownika w CRM</a>")%(agreement.first_name,agreement.last_name,agreement.medical_preliminary,url) 
                    
                if medical_preliminary == today:
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
                
                elif medical_preliminary == self.add_months(today,1):
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
                    
            if medical_heights:
                medical_heights = datetime.datetime.strptime(medical_heights,"%Y-%m-%d").date()
                body = _("Przypomnienie o badaniach lekarskich dla pracownika: %s %s<br/>Data badań wysokościowych: %s<br/><a href='%s'>Link do Pracownika w CRM</a>")%(agreement.first_name,agreement.last_name,agreement.medical_heights,url) 
                    
                if medical_heights == today:
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
                        
                elif medical_heights == self.add_months(today,1):
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
            
            if medical_psychotechnical:
                medical_psychotechnical = datetime.datetime.strptime(medical_psychotechnical,"%Y-%m-%d").date()
                body = _("Przypomnienie o badaniach lekarskich dla pracownika: %s %s<br/>Data badań psychotechnicznych: %s<br/><a href='%s'>Link do Pracownika w CRM</a>")%(agreement.first_name,agreement.last_name,agreement.medical_psychotechnical,url) 
                
                if medical_psychotechnical == today:
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
                        
                elif medical_psychotechnical == self.add_months(today,1):
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
            
            if medical_health:
                medical_health = datetime.datetime.strptime(medical_health,"%Y-%m-%d").date()
                body = _("Przypomnienie o badaniach lekarskich dla pracownika: %s %s<br/>Data badań sanitarno-epidemiologicznych: %s<br/><a href='%s'>Link do Pracownika w CRM</a>")%(agreement.first_name,agreement.last_name,agreement.medical_health,url) 
                    
                if medical_health == today:
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
                        
                elif medical_health == self.add_months(today,1):
                    agreement_obj.message_post(cr, uid, agreement.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')

        return True
        
    def open_line_agreement(self, cr, uid, id, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Agreement', 
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': id[0],
           # 'target': 'current',
        }
        
    def copy_candidate_data(self, cr, uid, context=None):
        #pdb.set_trace()
        agreement_ids = self.search(cr, uid, [])
        
        if agreement_ids:
            agreements = self.browse(cr, uid, agreement_ids)
            
            for agreement in agreements:
                candidate = agreement.candidate
                vals = {}
                first_name = ""
                last_name = ""
                x = 0
                for element in candidate:
                    if element != " ":
                        if x != 1:
                            last_name += element
                        else:
                            first_name += element
                    else:
                        x = 1
                        
                vals = {
                    'first_name': first_name,
                    'last_name': last_name,
                }
                self.write(cr, uid, agreement.id, vals, context=None)
        
        return True
        
    def copy_client(self, cr, uid, context=None):
        #pdb.set_trace()
        agreement_ids = self.search(cr, uid, [])
        
        if agreement_ids:
            agreements = self.browse(cr, uid, agreement_ids)
            
            for agreement in agreements:
                client = agreement.deal_id.client_id.id
                        
                vals = {
                    'client_id': client,
                }
                self.write(cr, uid, agreement.id, vals, context=None)
        
        return True
