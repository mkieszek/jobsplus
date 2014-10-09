# -*- coding: utf-8 -*-
"""
@author: mbereda
"""

from openerp.osv import osv,fields
from openerp.tools.translate import _
import pdb
import datetime

class jp_calculation2deal(osv.osv_memory):
    _name = 'jp.calculation2deal'
    
    def _calculation_ids_get(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        
        res = {}
        calculation = []
        for deal in self.browse(cr, uid, ids, context=context):                        
            res[deal.id] = calculation
        
        return res
        
    _columns = {
            'client_id': fields.many2one('res.partner', 'Client', readonly=True),
            'deal_id': fields.many2one('jp.deal','Deal', readonly=True),
            'calculation_from': fields.date('Calculation from'),
            'calculation_to': fields.date('Calculation to'),
            'file_data': fields.binary('File'),
            'file_name': fields.char('File name', size=64),
            'value_margin' : fields.float('Value margin agencies'),
            'value_leasing' : fields.float('Value leasing invoice'),
            'calculation_ids': fields.function(_calculation_ids_get, method=True, type="one2many",relation="jp.calculation", string="Calculations"),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        This function gets default values
        """
        res = super(jp_calculation2deal, self).default_get(cr, uid, fields, context=context)
        deal_id = context and context.get('active_id', False) or False
        deal_obj = self.pool.get('jp.deal')
        deal = deal_obj.browse(cr, uid, deal_id)
        res.update({'client_id': deal.client_id.id or False})
        res.update({'deal_id': deal.id or False})
        
        calculation_ids = []
        for calculation in deal.calculation_ids:
            calculation_ids.append(calculation.id)
        
        res.update({'calculation_ids': calculation_ids or False})
        
        return res