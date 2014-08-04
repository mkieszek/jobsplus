# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:28:33 2013

@author: pczorniej
"""

from openerp.osv import fields, osv
from tools.translate import _

class jp_time_sheet(osv.Model):
    _name = "jp.time.sheet"
    _inherit = 'mail.thread'
    _description = 'Time sheet'
    _columns = {
    'name': fields.char('Name',Size=64),    
    'agreement_id': fields.many2one('jp.agreement', 'Agreement'),
    'hours': fields.integer('Regular hours'),
    'year': fields.selection([('2012','2012'),('2013','2013'),('2014','2014'),('2015','2015'),('2016','2016'),('2017','2017'),
                              ('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022'),('2023','2023')],'Year'),
    'months': fields.selection([('1','January'),('2','February'),('3','March'),('4','April'),
                                ('5','May'),('6','June'),('7','July'),('8','August'),('9','September'),
                                ('10','October'),('11','November'),('12','December')],'Month'),
    'hours_50': fields.float('50%'),
    'hours_100': fields.float('100%'),
    'night': fields.float('Night'),
    }