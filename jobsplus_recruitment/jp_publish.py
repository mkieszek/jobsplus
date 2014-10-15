# -*- coding: utf-8 -*-
"""
Created on Tue Jul 30 08:50:52 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

AVAILABLE_STATUS = [
    ('1', 'Active'),
    ('2', 'Inactive')
]

class jp_publish(osv.Model):
    _name = "jp.publish"
    _inherit = 'mail.thread'
    _description = 'Publish'
    _columns = {
            'ad_id': fields.many2one('jp.ad','Ad'),
            'portal_id': fields.many2one('jp.portal','Portal'),
            'link': fields.char('Link', size=255, readonly=True),
            'date_added': fields.date('Date Added'),
            'expiration_date': fields.date('Expiration date'),
            'status' : fields.selection(AVAILABLE_STATUS, 'Status'),
    }
    
    def create(self, cr, uid, vals, context=None):
        #pdb.set_trace()
        portal_id = vals['portal_id']
        ad_id = vals['ad_id']
                
        ad = self.pool.get('jp.ad').browse(cr, uid, ad_id, context=context)  
        portal = self.pool.get('jp.portal').browse(cr, uid, portal_id, context=context)
        
        config_obj = self.pool.get('jp.config.settings')
        jp_crm = config_obj.current_jp_settings(cr, uid, 'jobsplus_crm')
        
        vals['link'] = ("http://%s/dla-pracownikow/wyslij-swoje-cv/?ad_id=%s&portal=%s" % (jp_crm, ad_id,portal.code))
        publish_id = super(jp_publish, self).create(cr, uid, vals, context=context)
    
        #Activation ad
        if 'status' in vals and vals['status'] == '1':
            vals_ad = {
                'activity': True,
            }
            self.pool.get('jp.ad').write(cr, uid, [ad.id], vals_ad, context=context)
        return publish_id
      