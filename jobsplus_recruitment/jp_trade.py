# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 12:13:19 2013

@author: pczorniej
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _

class jp_trade(osv.Model):
    _name = "jp.trade"
    _inherit = 'mail.thread'
    _description = 'Branze'
    
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'candidate_id' : fields.many2many('jp.candidate', 'Candidate'),
        'ad_id': fields.many2many('jp.ad', 'Ad'),
    }