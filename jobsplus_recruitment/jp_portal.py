# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:20:53 2013

@author: pczorniej
"""

from openerp.osv import fields, osv
from tools.translate import _
import pdb

class jp_portal(osv.Model):
    _name = "jp.portal"
    _inherit = 'mail.thread'
    _description = 'Portal'
    _columns = {
                'name': fields.char('Portal', size=64, required=True),
                'activity' : fields.boolean('Activity'),
                'type_a': fields.selection([('1','Package'),('2','Paid')],'Type', required=True),
                'cost': fields.float('Cost'),
                'code': fields.char('Code', size=64),
                'login': fields.char('Login',size=64),
                'password': fields.char('Password',size=64),
                'publish_ids': fields.one2many('jp.publish','portal_id','Publish'),
                'ad_ids': fields.one2many('jp.ad','portal_id','Ad'),
                }
                
    _defaults ={
        'type_a': '2',
    }
    
    def on_change_type(self, cr, uid, ids, type_a, context=None):
        #pdb.set_trace()
        values = {}
        if type_a:
            if type_a in '1':
                values['cost']=0.00
        else:
            values['type_a']='1'
        return {'value' : values}