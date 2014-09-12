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
        
        sex = 'Szanowni Państwo'.decode('utf8')
        sex2 = 'Państwa'.decode('utf8')
        sex3 = 'Państwa'.decode('utf8')
        sex4 = 'zostali Państwo zakwalifikowani'.decode('utf8')
        sex5 = 'wyrażają Państwo'.decode('utf8')
        
        if client.title2 == '1':
            sex = 'Szanowna Pani'.decode('utf8')
            sex2 = 'Panią'.decode('utf8')
            sex4 = 'została Pani zakwalifikowana'.decode('utf8')
            sex5 = 'wyraża Pani'.decode('utf8')
        elif client.title2 == '2':
            sex = 'Szanowny Panie'.decode('utf8')
            sex2 = 'Pana'.decode('utf8')
            sex4 = 'został Pan zakwalifikowany'.decode('utf8')
            sex5 = 'wyraża Pan'.decode('utf8')
         
        body = ''
        
        if deal_id.stage_id.sequence == 100: #Przegrany
            body = _("<div style='width: 600px; font-family: Verdana; font-size: 13px;'><div>%s,<div></br>\
                    <div><b>Serdecznie dziękujemy za współpracę i skorzystanie z usług Jobs Plus.</b></div>\
                    <div>Żałujemy, że nie udało się z sukcesem zamknąć projektu i tym bardziej chcielibyśmy <b>poprosić %s o ocenę naszej pracy.</b></div></br>\
                    <div><b>Ankieta czeka na %s pod linkiem:</b></div>\
                    <div><a href='%s'>>> ankieta oceny Jobs Plus</a></div></br>\
                    <div><b>Jej wypełnienie zajmie mniej niż minutę i pomoże ulepszyć naszą pracę.</b></div></br>\
                    <div>Jeżeli powyższy odnośnik nie działa, prosimy o skopiowanie poniższego linka i wklejenie go w adres przeglądarki</div>\
                    <div>%s</div></br>\
                    <div>Serdecznie dziękujemy.</div>\
                    <div>Z poważaniem,</div>\
                    <div>Zespół Jobs Plus</div></br>\
                    <div>Niniejsza wiadomość została wygenerowana automatycznie, prosimy na nią nie odpowiadać.</div></div>")%(sex, sex2, sex2, url, url)
        elif deal_id.stage_id.sequence == 90: #Wygrany
            body = _("<div style='width: 600px; font-family: Verdana; font-size: 13px;'><div>%s,<div></br>\
                    <div><b>Serdecznie dziękujemy za współpracę i skorzystanie z usług Jobs Plus.</b></div></br>\
                    <div>Chcielibyśmy <b>poprosić %s o ocenę naszej pracy –  ankieta czeka na %s pod linkiem:</b></div>\
                    <div><a href='%s'>>> ankieta oceny Jobs Plus</a></div></br>\
                    <div><b>Jej wypełnienie zajmie mniej niż minutę i pomoże ulepszyć naszą pracę.</b></div></br>\
                    <div>Jeżeli powyższy odnośnik nie działa, prosimy o skopiowanie poniższego linka i wklejenie go w adres przeglądarki</div>\
                    <div>%s</div></br>\
                    <div>Serdecznie dziękujemy.</div>\
                    <div>Z poważaniem,</div>\
                    <div>Zespół Jobs Plus</div></br>\
                    <div>Niniejsza wiadomość została wygenerowana automatycznie, prosimy na nią nie odpowiadać.</div></div>")%(sex, sex2, sex2, url, url)
        else: 
            body = _(("<div style='width: 600px; font-family: Verdana; font-size: 13px;'><div>%s,<div></br>\
                    <div><b>Serdecznie dziękujemy za współpracę i skorzystanie z usług Jobs Plus.</b></div></br>\
                    <div>Chcielibyśmy <b>poprosić %s o ocenę naszej dotychczasowej pracy, celem udoskonalenia jej jakości.</b></div></br>\
                    <div>Ankieta czeka na %s pod linkiem:</div>\
                    <div><a href='%s'>>>ankieta oceny Jobs Plus</a></div></br>\
                    <div><b>Jej wypełnienie zajmie mniej niż minutę i pomoże ulepszyć naszą pracę.</b></div></br>\
                    <div>Jeżeli powyższy odnośnik nie działa, prosimy o skopiowanie poniższego linka i wklejenie go w adres przeglądarki</div>\
                    <div>%s</div></br>\
                    <div>Serdecznie dziękujemy.</div>\
                    <div>Z poważaniem,</div>\
                    <div>Zespół Jobs Plus</div></br>\
                    <div>Niniejsza wiadomość została wygenerowana automatycznie, prosimy na nią nie odpowiadać.</div></div>"))%(sex, sex2, sex2, url, url)
        
        if mail_to is not "":
            users_obj = self.pool.get('res.users')
            subject = _("Oceń naszą pracę")
            uid = users_obj.search(cr, uid, [('id','=',1)])[0]
            uid_id = users_obj.browse(cr, uid, uid)
            
            email_from = "Zespół Jobs Plus<handel@jobsplus.pl>"
            vals = {'email_from': email_from,
                    'email_to': mail_to,
                    'state': 'outgoing',
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True}
                    
            self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        
        return rate_id