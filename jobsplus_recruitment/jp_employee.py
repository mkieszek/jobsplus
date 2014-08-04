# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:03:33 2013

@author: pczorniej
"""


from openerp.osv import fields, osv
from openerp.tools.translate import _

class jp_employee(osv.Model):
    _name = "jp.employee"
    _inherit = 'mail.thread'
    _description = 'Employee'
    _columns = {
        'name': fields.char('Name', size=64, 
                            required=True, 
                            readonly=True, 
                            select=True),
        'notes': fields.text('Notes'),
        'first_name': fields.char('First name', size=64),
        'last_name': fields.char('Last name', size=64),
        'date_of_birth': fields.date('Date of birth'),
        'residence_adress' : fields.char('Residence Adress', size=64),
        'registred_adress' : fields.char('Registred adress', size=64),
        'correspondence_address' : fields.char('Correspondence adress', size=64), 
        'medical_examination' : fields.text('Medical examination'),
        'agreement_id' : fields.many2one('jp.agreement', 'Agreement ID'),
    }