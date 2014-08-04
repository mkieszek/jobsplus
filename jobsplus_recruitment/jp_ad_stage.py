# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:08:49 2013

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

class jp_ad_stage(osv.Model):
    _name = "jp.ad.stage"
    
    _description = 'Ad stage'
    _columns = {
        'name': fields.char('Name', size=20, required=True, readonly=True, select=True),       
        'sequence': fields.integer('Sequence'),
        'state' : fields.selection(AVAILABLE_STATES, 'State', required=True),
     } 
    sql_constraints = [('jp_ad_stage_name_unique','unique(name)','Ad stage name already exists')]