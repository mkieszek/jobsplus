# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 12:06:14 2013

@author: mbereda
"""

from openerp.osv import osv,fields
import pdb

class jp_candidate2deal(osv.osv_memory):
    _name = "jp.candidate2deal"
    
    _columns = {
        'candidate_ids': fields.many2many('jp.candidate', string='Candidates'),
    }
    
    def create_applications(self, cr, uid, deal_id, context=None):
        #pdb.set_trace() 
        
        w = self.browse(cr, uid, deal_id, context=context)[0]
        deal_id = context and context.get('active_id', False) or False
        deal = self.pool.get('jp.deal').browse(cr,uid,[deal_id],context=context)[0]
        application_ids = deal.application_ids
        candidate_list = []
        for application in application_ids:
            candidate_list.append(application.candidate_id.id)
            
        for candidate in w.candidate_ids:
            values = {
                'deal_id': deal_id,
                'candidate_id': candidate and candidate.id or False,            
                'state': '1',
            }
            if candidate.id not in candidate_list:
                application_id = self.pool.get('jp.application').create(cr, uid, values, context=context)