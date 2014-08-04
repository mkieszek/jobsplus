# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 12:06:12 2013

@author: mbereda
"""
from openerp.osv import fields, osv
from tools.translate import _
import pdb

class jp_project(osv.Model):
    _name = 'jp.project'
    _description = 'Project'
	
    _columns = {
		'project_from' : fields.date('From'),
		'project_to': fields.date('To'),
		'deal_id': fields.many2one('jp.deal', 'Deal'),
        'file_data': fields.binary('File', required=True),
        'file_name': fields.char('File name', size=64),
	}
 
    def create(self, cr, uid, vals, context=None):
        project_id = super(jp_project, self).create(cr, uid, vals, context=context)
        project = self.browse(cr, uid, project_id)
        
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
        url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, project.deal_id.id)
        
        subject = _("Utworzono nowy projekt")
        body = _("Utworzono nowy projekt dla deal'a: %s<br/><a href='%s'>Link do deal'a</a>")%(project.deal_id.title, url)
        
        self.pool.get('jp.deal').message_post(cr, uid, project.deal_id.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
        return project_id