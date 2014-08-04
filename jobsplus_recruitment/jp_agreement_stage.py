# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:05:42 2013

@author: pczorniej
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _

AVAILABLE_STATES = [
    ('draft', 'New'),
    ('cancel', 'Cancelled'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Closed')
]

class jp_agreement_stage(osv.Model):
    _name = "jp.agreement.stage"
    _description = 'Work contract stage'
    _columns = {
        'name': fields.char('Name',size=64, required=True, readonly=True, select=True),
        'sequence': fields.integer('Sequence'),
        'state': fields.selection(AVAILABLE_STATES, 'State', required=True),
    }
    sql_constraints = [('jp_agreement_stage_name_unique','unique(name)','Agreement stage name already exists')]