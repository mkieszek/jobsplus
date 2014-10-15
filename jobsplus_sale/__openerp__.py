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
    'name': 'Jobs Plus - Sale',
    'version': '0.1',
    'category': 'Sale',
    'description': """Sale module for Jobs Plus. 2013-05-28 20:32""",
    'author': 'Via IT Solution',
    'website': 'http://www.viait.pl ',
    'depends': ['product', 'crm', 'mail', 'account','contacts','document', 'project', 'base_import'],
    
    'demo': [],
    'test':[],
    'installable': True,
    'images': [],
    'data': ['security/jp_security.xml',
             'data/jp_offer_sequence.xml',
             'data/jp_contract_sequence.xml',
             'data/jp_deal_stage_data.xml',
             'security/ir.model.access.csv',
             'data/jp_task_data.xml',
             'data/crm_lead_data.xml'],
                    
    'update_xml' : ['wizard/jp_offer2contract_view.xml',
                    'view/account_payment_term_view.xml',
                    'view/jp_offer_view.xml',
                    'view/jp_contract_view.xml',
                    'view/crm_lead_view.xml',
                    'view/jp_tasks_view.xml',
                    'view/res_partnet_view.xml',
                    'view/jp_deal_view.xml',
                    #'view/crm_meeting_view.xml',
                    'view/res_config_view.xml',
                    'view/jp_report_sales_view.xml',
                    'view/jp_report_sales2_view.xml',
                    'view/jp_offer_report_view.xml',
                    'view/jp_task_report_view.xml',
                    'view/jp_report_charts_view.xml',
                    'view/jp_graph_sales_view.xml',
                    ],
    'sequence': 10000,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
