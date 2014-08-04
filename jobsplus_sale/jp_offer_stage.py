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

class jp_offer_stage(osv.Model):
     _name = 'jp.offer.stage'
     _order = 'sequence asc'

     _columns = {
        'name': fields.char('Name', required=True),
        'sequence': fields.integer('Sequence', help="Used to order the note stages"),
        'state' : fields.selection(AVAILABLE_STATES, 'State', required=True),
        'fold': fields.boolean('Fold by Default'),
        
     }
     sql_constraints = [('jp_stage_name_unique','unique(name)', 'Stage name already exists')]
     
     def get_stage_done(cr, uid, context=None):
        return self.search(cr, uid, [('state', '=', 'done')], context=context)