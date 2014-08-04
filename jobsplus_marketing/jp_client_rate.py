# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import uuid
import urllib

class jp_client_rate(osv.osv):
    _name = 'jp.client.rate'
    _order = 'write_date desc'
    _columns = {
        'name': fields.char("Name"),
        'rate': fields.char("Rate"),
        'deal_id': fields.many2one('jp.deal', 'Deal'),
        'client_id': fields.many2one('res.partner','Client'),
        'state': fields.selection([('1','Sent'),('2','Rated')],'State'),
        'rate_contact' : fields.integer('Contact with the agency'),
        'rate_candidate' : fields.integer('Acquired candidate'),
        'rate_time' : fields.integer('Duration'),
        'rate_quality_price' : fields.integer('Quality for price'),
        'uuid' : fields.char('UUID'),
    }
    
    def create(self, cr, uid, vals, context=None):
        vals['uuid'] = uuid.uuid4()
        rate_id = super(jp_client_rate, self).create(cr, uid, vals, context=context)
        jp_config_obj = self.pool.get('jp.config.settings')
        jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
        jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www

        url="http://"+jp_www+"/wp-content/plugins/jobsplus-integration/api/get_client_rate.php?id="+str(rate_id)+"&token="+str(vals['uuid'])
        url_handler = urllib.urlopen(url)
        mail_to = ''
        
        client_obj = self.pool.get('res.partner')
        client = client_obj.browse(cr, uid, vals['client_id'])
        mail_to = client.email
        
        deal_obj = self.pool.get('jp.deal')
        deal_id = deal_obj.browse(cr, uid, vals['deal_id'])
        
        url="http://"+jp_www+"/invisible/ocena-klienta?&token="+str(vals['uuid'])
        
        if deal_id.stage_id.id == 10: #Przegrany
            body = _("<div style='width: 600px;'><div style='margin-bottom: 15px;'>Szanowni Państwo,<div>\
                    <div><b>Serdecznie dziękujemy za współpracę i skorzystanie z usług Jobs Plus.</b></div>\
                    <div>Chcielibyśmy również <b>poprosić Państwa o ocenę naszej pracy –  ankieta czeka na Państwa pod linkiem:</b></div>\
                    <div><a href='%s'>Formularz oceny</a></div>\
                    <div style='font-size: 12px;'>Jeżeli powyższy odnośnik nie działa, skopiuj poniższy link i wklej w adres przeglądarki</div>\
                    <div style='font-size: 12px;'>%s</div>\
                    <div style='margin-bottom: 15px;'><b>Jej wypełnienie potrwa około jedną minutę.</b></div>\
                    <div>Dziękujemy.</div>\
                    <div style='margin-left: 200px'>Z poważaniem</div>\
                    <div style='margin-left: 200px'>Zespół Jobs Plus</div></div>")%(url, url)
        elif deal_id.stage_id.id == 9: #Wygrany
            body = _("<div style='width: 600px;'><div style='margin-bottom: 15px;'>Szanowni Państwo,<div>\
                    <div><b>Serdecznie dziękujemy za współpracę i skorzystanie z usług Jobs Plus.</b></div>\
                    <div>Chcielibyśmy również <b>poprosić Państwa o ocenę naszej pracy –  ankieta czeka na Państwa pod linkiem:</b></div>\
                    <div><a href='%s'>Formularz oceny</a></div>\
                    <div style='font-size: 12px;'>Jeżeli powyższy odnośnik nie działa, skopiuj poniższy link i wklej w adres przeglądarki</div>\
                    <div style='font-size: 12px;'>%s</div>\
                    <div style='margin-bottom: 15px;'><b>Jej wypełnienie potrwa około jedną minutę.</b></div>\
                    <div>Dziękujemy.</div>\
                    <div style='margin-left: 200px'>Z poważaniem</div>\
                    <div style='margin-left: 200px'>Zespół Jobs Plus</div></div>")%(url, url)
        else: 
            body = _("<div style='width: 600px;'><div style='margin-bottom: 15px;'>Szanowni Państwo,<div>\
                    <div><b>Serdecznie dziękujemy za współpracę i skorzystanie z usług Jobs Plus.</b></div>\
                    <div>Chcielibyśmy również <b>poprosić Państwa o ocenę naszej pracy –  ankieta czeka na Państwa pod linkiem:</b></div>\
                    <div><a href='%s'>Formularz oceny</a></div>\
                    <div style='font-size: 12px;'>Jeżeli powyższy odnośnik nie działa, skopiuj poniższy link i wklej w adres przeglądarki</div>\
                    <div style='font-size: 12px;'>%s</div>\
                    <div style='margin-bottom: 15px;'><b>Jej wypełnienie potrwa około jedną minutę.</b></div>\
                    <div>Dziękujemy.</div>\
                    <div style='margin-left: 200px'>Z poważaniem</div>\
                    <div style='margin-left: 200px'>Zespół Jobs Plus</div></div>")%(url, url)
        
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