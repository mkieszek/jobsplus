# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:44:45 2013

@author: mkieszek
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import jp_contract_stage


PERIOD_TYPES = [
    ('day', 'Day'),
    ('week', 'Week'),
    ('month', 'Month'),
    ('year', 'Year')
]


class jp_contract(osv.Model):
    _name = "jp.contract"
    _inherit = 'mail.thread'
    _description = 'Umowe'    
    
    _columns = {
        'name': fields.char('Contract Reference', size=64, 
                            required=True, 
                            readonly=True, 
                            select=True),
        'client_id' : fields.many2one('res.partner', 
                                      'Client', 
                                      required=True, 
                                      track_visibility='onchange'),
        'contract_date' : fields.date('Contract date', 
                                      required=True, 
                                      track_visibility='onchange'),        
        'product_id' : fields.many2one('product.product', 
                                       'Product', 
                                       required=True, 
                                       track_visibility='onchange'),
        'termination_date' : fields.date('Termination date', 
                                  track_visibility='onchange'),
        'dismiss_period' : fields.integer('Dismissal period',
                                           track_visibility='onchange',
                                           required=True),
        'stage_id': fields.many2one('jp.contract.stage', 
                                    'Stage', 
                                    track_visibility='onchange', 
                                    ondelete="set null"),                            
        'type' : fields.selection([('fixed', 'Fixed-term'), ('indefinite', 'Indefinite term')], 
                                   'Term type', 
                                   required=True, 
                                   track_visibility='onchange'),
        'payment_term': fields.many2one('account.payment.term', 
                                        'Payment Terms'),
        'warranty': fields.boolean('Has warranty', track_visibility='onchange'),
        'warranty_period' : fields.integer('Warranty',
                                    track_visibility='onchange'),
        'ref_offer' : fields.many2one('jp.offer', 
                                      'Reference offer',
                                      track_visibility='onchange'),
        'notes': fields.text('Notes'),   
        'sales_rep' : fields.many2one('res.users', 'Sales rep', track_visibility='onchange'),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=jp_contract_stage.AVAILABLE_STATES, string="Status", readonly=True,),
        'active': fields.boolean('Active', required=False),
        'task_ids': fields.one2many('project.task', 'contract_id', 'Tasks'),
        'deal_ids': fields.one2many('jp.deal', 'contract_id', 'Deals'),
        'warranty_period_type' : fields.selection(PERIOD_TYPES, 'Period type'),
        'dismiss_period_type' : fields.selection(PERIOD_TYPES, 'Period type'),
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
        'warranty': True,
        'sales_rep': lambda obj, cr, uid, context: uid,
    }
    
    def name_get(self, cr, uid, ids, context=None):
         """Overrides orm name_get method"""
         if not isinstance(ids, list) :
             ids = [ids]
         res = []
         if not ids:
             return res
        
         reads = self.read(cr, uid, ids, ['name', 'client_id', 'product_id'], context)

         for record in reads:
             name = record['name']
             client_name = record['client_id'][1]
             product_name = record['product_id'][1]
             res.append((record['id'], name + ' ' + client_name + ' ' + product_name))
         return res    
    
    def create(self, cr, uid, vals, context=None):
        
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.contract') or '/'
            
        vals['stage_id'] = self.pool.get('jp.contract.stage').search(cr, uid, [('state','=','open')], context=context)[0]
        vals['active'] = True
        contract_id = super(jp_contract, self).create(cr, uid, vals, context=context)
        
        self.send_mail(cr, uid, contract_id, context = context)
        
        return contract_id
    
    def on_change_type(self, cr, uid, ids, type, context=None):
        values = {}
        if type == 'indefinite':
            values = {
                'termination_date': False
            }
        return {'value' : values}

    def send_mail(self, cr, uid, contract_id, context=None):
        #pdb.set_trace()
        users_obj = self.pool.get('res.users')
        user_ids = users_obj.search(cr,uid,[])
        users = users_obj.browse(cr, uid, user_ids)
        
        mail_to = ""
        for user in users:
            if user.partner_id.email is not False and user.active is True:
                mail_to += user.partner_id.email + ", "
        if mail_to is not "":
            contract = self.browse(cr, uid, contract_id)
            create_uid = users_obj.browse(cr, uid, uid).name
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
            url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.contract")%(jp_crm, cr.dbname, contract_id)
            subject = _("Congratulations, we have a new customer contract.")
            body = _("New contract with customer: %s <br/>Signed by: %s<br/><a href='%s'>Say congrats cuz it's worth.</a>")\
                    %(contract.client_id.name,create_uid,url)
            uid = users_obj.search(cr, uid, [('id','=',1)])[0]
            uid_id = users_obj.browse(cr, uid, uid)
            
            email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
                
            vals = {'email_from': email_from,
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True}
                    
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        