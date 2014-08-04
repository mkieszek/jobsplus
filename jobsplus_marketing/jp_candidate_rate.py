# -*- coding: utf-8 -*-

"""
Created on Wed Jun 19 13:10:54 2013

@author: mbereda
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import uuid
import urllib

class jp_candidate_rate(osv.osv):
    _name = 'jp.candidate.rate'
    _order = 'write_date desc'
    _columns = {
        'name': fields.char("Name"),
        'rate': fields.char("Rate"),
        'application_id': fields.many2one('jp.application', 'Application'),
        'candidate_id': fields.many2one('jp.candidate', "Candidate"),
        'state': fields.selection([('1','Sent'),('2','Rated')],'State'),
        'deal_id': fields.many2one('jp.deal', 'Deal'),
        'uuid': fields.char("UUID"),
        
    }
    
    def create(self, cr, uid, vals, context=None):
        vals['uuid'] = uuid.uuid4()
        rate_id = super(jp_candidate_rate, self).create(cr, uid, vals, context=context)
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
        url="http://"+jp_www+"/wp-content/plugins/jobsplus-integration/api/get_candidate_rate.php?id="+str(rate_id)+"&token="+str(vals['uuid'])
        url_handler = urllib.urlopen(url)
        mail_to = ''
        
        candidate_obj = self.pool.get('jp.candidate')
        candidate = candidate_obj.browse(cr, uid, vals['candidate_id'])
        mail_to = candidate.email
        
        deal_obj = self.pool.get('jp.deal')
        deal_id = deal_obj.browse(cr, uid, vals['deal_id'])
        
        position = deal_id.title
        url="http://"+jp_www+"/invisible/ocena-kandydata?&token="+str(vals['uuid'])
        
        application_obj = self.pool.get('jp.application')
        application = application_obj.browse(cr, uid, vals['application_id'])
        
        if application.status == '2':
            body = _("<div style='width: 600px;'><div style='margin-bottom: 15px;'>Szanowni Państwo,<div>\
                    <div><b>Serdecznie dziękujemy za udział w rekrutacji na stanowisko %s.</b> przeprowadzonej przez zespół Jobs Plus. <b>Gratulujemy pomyślnego rezultatu</b> i życzymy powodzenia w pracy na nowym stanowisku.</div>\
                    <div>Chcielibyśmy również poprosić Państwa o ocenę naszej pracy –  ankieta czeka na Państwa pod linkiem:</div>\
                    <div><a href='%s'>Formularz oceny</a></div>\
                    <div style='font-size: 12px;'>Jeżeli powyższy odnośnik nie działa, skopiuj poniższy link i wklej w adres przeglądarki</div>\
                    <div style='font-size: 12px;'>%s</div>\
                    <div style='margin-bottom: 15px;'><b>Jej wypełnienie potrwa około jedną minutę.</b></div>\
                    <div>Dziękujemy.</div>\
                    <div style='margin-left: 200px'>Z poważaniem</div>\
                    <div style='margin-left: 200px'>Zespół Jobs Plus</div></div>")%(position, url, url)
        else:
            body = _("<div style='width: 600px;'><div style='margin-bottom: 15px;'>Szanowni Państwo,</div>\
                    <div style='margin-bottom: 15px;'><b>Serdecznie dziękujemy za udział w rekrutacji na stanowisko %s.</b></div>\
                    przeprowadzonej przez zespół Jobs Plus. Cieszymy się, że mogliśmy Państwa poznać. Informujemy, że <b>proces ten został zamknięty</b> i niestety nie znaleźli się Państwo w gronie rekomendowanych Kandydatów.\
                    Jednocześnie zapewniamy, że <b>zachowamy w bazie Państwa kandydaturę</b> i będziemy wracać do niej w przypadku odpowiednich procesów.\
                    <div>Chcielibyśmy również <b>poprosić Państwa o ocenę naszej pracy –  ankieta czeka na Państwa pod linkiem:</b>\
                    <div><a href='%s'>Formularz oceny</a></div>\
                    <div style='font-size: 12px;'>Jeżeli powyższy odnośnik nie działa, skopiuj poniższy link i wklej w adres przeglądarki</div>\
                    <div style='font-size: 12px;'>%s</div>\
                    <div style='margin-bottom: 15px;'><b>Jej wypełnienie potrwa około jedną minutę.</b></div>\
                    <div>Dziękujemy.</div>\
                    <div style='margin-left: 200px'>Z poważaniem</div>\
                    <div style='margin-left: 200px'>Zespół Jobs Plus</div></div>")%(position, url, url)
        
        if mail_to is not "":
            users_obj = self.pool.get('res.users')
            subject = _("Oceń proces rekrutacji")
            uid = users_obj.search(cr, uid, [('id','=',1)])[0]
            uid_id = users_obj.browse(cr, uid, uid)
            
            email_from = uid_id.partner_id.name+"<"+uid_id.partner_id.email+">"
            vals = {'email_from': email_from,
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True}
                    
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        
        return rate_id