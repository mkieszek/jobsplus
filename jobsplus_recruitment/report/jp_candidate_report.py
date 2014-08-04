# -*- coding: utf-8 -*-

from openerp.report import report_sxw
import time
import pdb

class candidate_order(report_sxw.rml_parse):
    _name = "candidate.order"
    def __init__(self, cr, uid, name, context):
        super(candidate_order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.candidate', 'jp.candidate', 'jobsplus/trunk/jobsplus_recruitment/report/candidate_report.rml', parser=candidate_order, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: