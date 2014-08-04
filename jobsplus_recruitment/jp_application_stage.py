# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 10:59:36 2013

@author: pczorniej
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _

AVAILABLE_STATES = [
    ('1', 'Duration'),
    ('2', 'Transfer'),
    ('3', 'Accepted'),
    ('4', 'Hired'),
    ('5', 'Rejected')
]

class jp_application_stage(osv.Model):
    _name = "jp.application.stage"
    _description = 'Application stage'
    _columns = {
        'name': fields.char('Name', size=20,
                            required=True,
                            readonly=True,
                            select=True),
        'sequence': fields.integer('Sequence'),
        'state' : fields.selection(AVAILABLE_STATES, 
                                   'State', 
                                   required=True)
    }
    sql_constraints = [('jp_application_stage_name_unique','unique(name)', 
                         'Application state name already exists')]