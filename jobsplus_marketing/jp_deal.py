# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from tools.translate import _
import pdb

class jp_deal(osv.osv):
    _inherit = 'jp.deal'
    _description = "Deal"
    _columns = {
        'client_rate_id': fields.one2many('jp.client.rate', 'deal_id', 'Client rate'),
        'candidate_rate_id': fields.one2many('jp.candidate.rate', 'deal_id', 'Candidate rate'),
    }
