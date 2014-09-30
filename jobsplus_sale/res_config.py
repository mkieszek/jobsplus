# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.addons.mail.mail_message import decode
import pdb

class jp_config_settings(osv.osv):
    _name = 'jp.config.settings'
    _inherit = 'res.config.settings'

    _columns = {
            'jobsplus_www': fields.char('Jobs Plus www'),
            'jobsplus_crm': fields.char('Jobs Plus CRM'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(jp_config_settings, self).default_get(cr, uid, fields, context)
        config_id = self.search(cr, uid, [])
        if config_id:
            res['jobsplus_www'] = self.browse(cr, uid, config_id[-1]).jobsplus_www
            res['jobsplus_crm']= self.browse(cr, uid, config_id[-1]).jobsplus_crm
        return res
    
    def current_jp_settings(self, cr, uid, field):
        jp_config_id = self.search(cr, uid, [])
        if not jp_config_id:
            raise osv.except_osv(decode('Ostrzeżenie!'), decode('Skontaktuj się z administratorem w celu ustawień CRM'))
        
        if field == 'jobsplus_www':
            return self.browse(cr, uid, jp_config_id).jobsplus_www
        elif field == 'jobsplus_crm':
            return self.browse(cr, uid, jp_config_id).jobsplus_crm