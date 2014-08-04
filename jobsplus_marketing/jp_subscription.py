# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from tools.translate import _

class jp_subscription(osv.osv):
    _name = 'jp.subscription'
    _columns = {
        'subscription_id': fields.integer("Subscription id"),
        'name': fields.char("Name"),
        'email': fields.char("Email"),
        'employee': fields.boolean("Employee"),
        'employer': fields.boolean("Employer"),
        'token': fields.char("Token"),
        'verification': fields.boolean("Verification"),
        'verification_date': fields.datetime("Verification date")
    }