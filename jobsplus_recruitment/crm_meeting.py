# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 12:55:43 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

class crm_meeting(osv.Model):
    _inherit='crm.meeting'
    _columns={
            'application_id': fields.many2one('jp_application','Application'),         
            'candidate_id': fields.many2one('jp.candidate', 'Candidate'),   
    }
