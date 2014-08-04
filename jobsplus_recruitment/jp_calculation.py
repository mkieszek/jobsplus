# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 12:06:12 2013

@author: mbereda
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, timedelta
import datetime
import pdb

class jp_calculation(osv.Model):
    _name = 'jp.calculation'
    _description = 'Calculation'
	
    _columns = {
		'calculation_from' : fields.date('From', required=True),
		'calculation_to': fields.date('To', required=True),
		'deal_id': fields.many2one('jp.deal', 'Deal'),
        'file_data': fields.binary('File', required=True),
        'file_name': fields.char('File name', size=64),
        'value_margin' : fields.float('Value margin agencies'),
        'value_leasing' : fields.float('Value leasing invoice'),
        'create_date' : fields.date('Create date'),
	}
 
    def create(self, cr, uid, vals, context=None):
        calculation_id = super(jp_calculation, self).create(cr, uid, vals, context=context)
        calculation = self.browse(cr, uid, calculation_id)
        
        report_obj = self.pool.get('jp.report.sales2')
        calc_date = datetime.datetime.strptime(calculation.calculation_from,"%Y-%m-%d").date()
        month_str = str(calc_date.year)+"-M"+str(calc_date.month).zfill(2)
        
        report_ids = report_obj.search(cr, uid, [('month','=',month_str),('client_id','=',calculation.deal_id.client_id.id)])
        if report_ids:
            report = report_obj.browse(cr, uid, report_ids[0])
            report_vals = {
                           'value_leasing': report.value_leasing+calculation.value_leasing,
                           'value_margin': report.value_margin+calculation.value_margin
                           }
            report_obj.write(cr, uid, report_ids, report_vals, context=None)
        
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_crm = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_crm
        url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.deal")%(jp_crm, cr.dbname, calculation.deal_id.id)
        
        subject = _("Utworzono nowe rozliczenie")
        body = _("Utworzono nowe rozliczenie dla deal'a: %s<br/><a href='%s'>Link do deal'a</a>")%(calculation.deal_id.title, url)
        
        self.pool.get('jp.deal').message_post(cr, uid, calculation.deal_id.id, body=body, subject=subject, type='email', subtype='mail.mt_comment', 
                        parent_id=False, attachments=None, context=context, content_subtype='html')
        return calculation_id
