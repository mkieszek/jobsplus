# -*- coding: utf-8 -*-

"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb

class jp_application(osv.osv):
    _inherit = 'jp.application'
    _description = "Application"
    _columns = {
        'rate_id' : fields.many2many('jp.rate.wizard', 'Rate'),
    }