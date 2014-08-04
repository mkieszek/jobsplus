# -*- coding: utf-8 -*-
"""
Created on Mon May 27 21:51:03 2013

@author: mbereda
"""

from openerp.osv import fields, osv
import pdb

class jp_deal_stage_history(osv.Model):
    _name="jp.deal.stage.history"
    _description = 'Stage history'
    _columns={
        'deal_id': fields.many2one('jp.deal', 'Deal', readonly=True),
        'stage_id': fields.many2one('jp.deal.stage', 'Stage', readonly=True),
        'recruiter_id': fields.many2one('res.users', 'Recruiter_id'),
        'date_cr': fields.date('Create'),
    }