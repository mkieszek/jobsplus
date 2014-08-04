from openerp.osv import fields, osv
from openerp.tools.translate import _
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