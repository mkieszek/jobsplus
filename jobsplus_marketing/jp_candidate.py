# -*- coding: utf-8 -*-

"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

class jp_candidate(osv.osv):
    _inherit = 'jp.candidate'
    _description = "Candidate"
    
    def _candidate_rate_ids(self, cr, uid, ids, field_name, arg, context=None):
        #pdb.set_trace()        
        val = {}
        for candidate in self.browse(cr, uid, ids, context=context):
            application_ids = self.pool.get('jp.application').search(cr, uid, [('candidate_id','=',candidate.id)], context=context)
            candidate_rate_ids = self.pool.get('jp.candidate.rate').search(cr, uid, [('application_id','in',application_ids)], context=context)
                    
            val[candidate.id] = candidate_rate_ids
        
        return val
        
    _columns = {
        'candidate_rate_ids': fields.function(_candidate_rate_ids, type="one2many", relation='jp.candidate.rate', string='Rates'),
        'tag_ids' : fields.many2many('jp.candidate.tag', 'jp_candidate_tag_rel', 'candidate_id', 'tag_id', 'Tags')
    }