# -*- coding: utf-8 -*-

"""
Created on Mon Jul  8 11:07:22 2013

@author: mbereda
"""
from openerp.osv import fields, osv


class jp_sallary(osv.Model):
    _name = "jp.sallary"
    _description = 'Sallary'
    
    _columns = {
        'name': fields.char('ID',readonly=True, size=64),
    }
