# -*- coding: utf-8 -*-
"""
Created on Mon May 20 22:15:49 2013

@author: mkieszek
"""

from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta

AVAILABLE_STATES = [
    ('draft', 'New'),
    ('cancel', 'Cancelled'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Closed')
]

class jp_contract_stage(osv.Model):
     _name = 'jp.contract.stage'
     _order = 'sequence asc'
     _description = 'Contract stage'
     _columns = {
        'name': fields.char('Name', required=True),
        'sequence': fields.integer('Sequence'),
        'state' : fields.selection(AVAILABLE_STATES, 'State', required=True),
     }
     sql_constraints = [('jp_contract_stage_name_unique','unique(name)', 
                         'Contract state name already exists')]
