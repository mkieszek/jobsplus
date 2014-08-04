# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 09:48:26 2013

@author: mbereda
"""

from openerp.osv import osv,fields
from openerp.tools.translate import _
import pdb
import datetime

class jp_attachment2candidate(osv.Model):
    _name = 'jp.attachment2candidate'
    
    def _document_ids_get(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        
        res = {}
        for candidate in self.browse(cr, uid, ids, context=context):
            attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','jp.candidate'),('res_id','=',candidate.id)], context=context)
                        
            res[candidate.id] = attachment_ids
        
        return res
        
    _columns = {
            'candidate': fields.char('ID', readonly=True),
            'candidate_id': fields.many2one('jp.candidate','Candidate', readonly=True),
            'candidate_name': fields.char('Candidate', readonly=True),
            'document_ids': fields.function(_document_ids_get, method=True, type="one2many",relation="ir.attachment", string="Document"),
    }
    
    def default_get(self, cr, uid, candidate_id, context=None):
        """
        This function gets default values
        """
        res = super(jp_attachment2candidate, self).default_get(cr, uid, candidate_id, context=context)
        application_id = context and context.get('active_id', False) or False
        candidate = self.pool.get('jp.application').browse(cr, uid, application_id).candidate_id
        res.update({'candidate_id': candidate.id or False})
        res.update({'candidate_name': candidate.candidate or False})
        res.update({'candidate': candidate.name or False})
        
        document_ids = self.pool.get('jp.candidate').browse(cr, uid, candidate.id).document_ids
        documents = []
        for document in document_ids:
            documents.append(document.id)
            
        if document_ids:
            res.update({'document_ids': documents})
        return res