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
    'name': 'Jobs Plus - Recruitment',
    'version': '0.1',
    'category': 'Jobs Plus',
    'description': """Recruitment module for Jobs Plus.""",
    'author': 'Via IT Solution',
    'website': 'http://www.viait.pl ',
    'depends': ['jobsplus_sale'],
    'data': ['data/jp_application_sequence.xml',
             'data/jp_ad_sequence.xml',
             'data/jp_agreement_sequence.xml',
             'data/jp_candidate_sequence.xml',
             'data/jp_trade.xml',
             'data/jp_sallary.xml',
             'security/ir.model.access.csv',
             'data/jobsplus_recruitment.xml',
             ],
    'demo': [],
    'test':[],
    'installable': True,
    'images': [],
    
    #'css': ['static/src/css/*.css',],
    #'js': ['static/src/js/*.js',],
    #'qweb': ['static/src/xml/*.xml',],
    
    'update_xml' : ['report/jp_candidate_report_view.xml',
                    'view/jp_calculation_view.xml',
                    #'wizard/jp_meeting2deal_view.xml',
                    'wizard/jp_candidate2deal_view.xml',
                    'wizard/jp_recruiter2deal_view.xml',
                    'wizard/jp_attachment2candidate_view.xml',
                    'wizard/jp_calculation2deal_view.xml',
                    'view/jp_publish_view.xml',
                    'view/jp_deal_view.xml',
                    'view/jp_application_view.xml',
                    'view/jp_time_sheet_view.xml',
                    'view/jp_ad_view.xml',
                    'view/jp_agreement_view.xml',
                    'view/jp_portal_view.xml',
                    'view/jp_candidate_view.xml',
                    'view/jp_trade_view.xml',
                    'view/jp_report_recruitment_view.xml',
                    'view/jp_task_report_rec_view.xml',
                    'view/jp_deal_report_view.xml'
                    ],
    'sequence': 1001,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
# -*- coding: utf-8 -*-

