# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Jobs Plus - Marketing and Administration',
    'version': '0.1',
    'category': 'Jobs Plus',
    'description': """ """,
    'author': 'Via IT Solution',
    'website': 'http://www.viait.pl ',
    'depends': ['jobsplus_recruitment'],
    'data': ['security/jp_security.xml',
            'security/ir.model.access.csv'],
    'demo': [],
    'test':[],
    'installable': True,
    'images': [],
    'update_xml' : ['view/jp_invoice_view.xml',
                    'view/jp_agreement_supplier_view.xml',
                    'wizard/jp_rate_wizard_view.xml',
                    'view/jp_deal_view.xml',
                    'view/res_partner_view.xml',
                    'view/jp_client_rate_view.xml',
                    'view/jp_candidate_rate_view.xml',
                    'view/jp_candidate_view.xml',
                    'view/jp_employee_view.xml',
                    'view/jp_subscription_view.xml',
                    'view/jp_candidate_tag_view.xml',
                    'view/jp_segmentation_view.xml'
                    ],
    'sequence': 1001,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
# -*- coding: utf-8 -*-