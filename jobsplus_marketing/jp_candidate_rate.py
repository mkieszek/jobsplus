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
        deal_obj = self.pool.get('jp.deal')
        deal_id = deal_obj.browse(cr, uid, vals['deal_id'])
    
        application_obj = self.pool.get('jp.application')
        application = application_obj.browse(cr, uid, vals['application_id'])
        
        if application.status != '1':
            vals['uuid'] = uuid.uuid4()
            rate_id = super(jp_candidate_rate, self).create(cr, uid, vals, context=context)
            jp_config_obj = self.pool.get('jp.config.settings')
            jp_config_id = jp_config_obj.search(cr, uid, [])[-1]
            jp_www = jp_config_obj.browse(cr, uid, jp_config_id).jobsplus_www
            
            url="http://"+jp_www+"/wp-content/plugins/jobsplus-integration/api/get_candidate_rate.php?id="+str(rate_id)+"&token="+str(vals['uuid'])
            #url_handler = urllib.urlopen(url)
            mail_to = ''
            
            candidate_obj = self.pool.get('jp.candidate')
            candidate = candidate_obj.browse(cr, uid, vals['candidate_id'])
            mail_to = candidate.email
            
            position = deal_id.title
            url="http://"+jp_www+"/invisible/ocena-kandydata?&token="+str(vals['uuid'])
            
            sex = 'Szanowni Państwo'.decode('utf8')
            sex2 = 'Państwo'.decode('utf8')
            sex3 = 'Państwa'.decode('utf8')
            sex4 = 'zostali Państwo zakwalifikowani'.decode('utf8')
            sex5 = 'wyrażają Państwo'.decode('utf8')
            if application.candidate_id.sex == 'f':
                sex = 'Szanowna Pani'.decode('utf8')
                sex2 = 'Panią'.decode('utf8')
                sex3 = 'Pani'.decode('utf8')
                sex4 = 'została Pani zakwalifikowana'.decode('utf8')
                sex5 = 'wyraża Pani'.decode('utf8')
            elif application.candidate_id.sex == 'm':
                sex = 'Szanowny Panie'.decode('utf8')
                sex2 = 'Pana'.decode('utf8')
                sex3 = 'Pana'.decode('utf8')
                sex4 = 'został Pan zakwalifikowany'.decode('utf8')
                sex5 = 'wyraża Pan'.decode('utf8')
                
            body = ''

            #zaakceptowana
            if application.status == '2':
                body = _("<div style='width: 600px; font-family: Verdana; font-size: 13px;'><div style='margin-bottom: 15px;'>%s,<div>\
                        <div><b>Serdecznie dziękujemy za udział w rekrutacji na stanowisko %s,</b> przeprowadzonej przez zespół Jobs Plus.</div></br>\
                        <div><b>Gratulujemy pomyślnego rezultatu</b> i życzymy powodzenia w pracy na nowym stanowisku.</div>\
                        <div>Chcielibyśmy również poprosić %s o ocenę naszej pracy –  ankieta czeka pod linkiem:</div>\
                        <div><a href='%s'>>>ankieta oceny Jobs Plus</a></div></br>\
                        <div style='margin-bottom: 15px;'><b>Jej wypełnienie zajmie mniej niż minutę</b>, a znacząco poprawi jakość naszej pracy i wpłynie na satysfakcję przyszłych Kandydatów.</div>\
                        <div>Jeżeli powyższy odnośnik nie działa, prosimy o skopiowanie poniższego linka i wklejenie go w adres przeglądarki.</div>\
                        <div>%s</div></br>\
                        <div>Dziękujemy!</div>\
                        <div>Pozdrawiamy,</div>\
                        <div>Zespół Jobs Plus</div>\
                        <div>Niniejsza wiadomość została wygenerowana automatycznie, prosimy na nią nie odpowiadać.</div></div>")%(sex, position, sex2, url, url)
            #odrzucona po rozmowie
            elif application.status == '3' and deal_id.stage_id.sequence >= 50:
                body = _("<div style='width: 600px; font-family: Verdana; font-size: 13px;'><div style='margin-bottom: 15px;'>%s,</div>\
                        <div><b>Serdecznie dziękujemy za udział w rekrutacji na stanowisko %s,</b> przeprowadzonej przez zespół Jobs Plus.</div></br>\
                        <div>%s kandydatura została pozytywnie oceniona, jednak <b>proces ten został już zamknięty</b>\
                        i nie %s do kolejnego etapu</div>\
                        <div>Chcielibyśmy <b>poprosić %s o ocenę naszej pracy.</div>\
                        <div>Ankieta czeka na %s pod linkiem:</b>\
                        <div><a href='%s'>>>ankieta oceny Jobs Plus</a></div></br>\
                        <div><b>Jej wypełnienie zajmie mniej niż minutę</b>, a znacząco poprawi jakość naszej pracy i wpłynie na satysfakcję przyszłych Kandydatów.</div>\
                        <div>Jeżeli powyższy odnośnik nie działa, prosimy o skopiowanie poniższego linka i wklejenie go w adres przeglądarki.</div>\
                        <div>%s</div></br>\
                        <div>Jednocześnie proponujemy zachowanie <b>w bazie %s dokumentów.</b>\
                        Będziemy wracać do niej w przypadku odpowiednich procesów. Jeśli nie %s zgody na zachowanie dokumentów,\
                        wystarczy odpowiedzieć na tego maila, wpisując w tytule wiadomości NIE ZGADZAM SIĘ.</div></br>\
                        <div>Serdecznie dziękujemy!.</div>\
                        <div>Pozdrawiamy,</div>\
                        <div>Zespół Jobs Plus</div></div>")%(sex, position, sex3, sex2, sex4, sex3, url, url, sex5, sex5)
            #odrzucona przed rozmową
            elif application.status == '3' and deal_id.stage_id.sequence < 50:
                body = _("<div style='width: 600px; font-family: Verdana; font-size: 13px;'><div style='margin-bottom: 15px;'>%s,</div>\
                        <div><b>Serdecznie dziękujemy za udział w rekrutacji na stanowisko %s,</b> przeprowadzonej przez zespół Jobs Plus.</div></br>\
                        <div>W tej chwili, <b>proces ten został zamknięty</b> - proponujemy zachowanie <b>w bazie %s dokumentów.</b>\
                        Będziemy wracać do niej w przypadku odpowiednich procesów. Jeśli nie %s zgody na zachowanie dokumentów,\
                        wystarczy odpowiedzieć na tego maila, wpisując w tytule wiadomości NIE ZGADZAM SIĘ.</div></br>\
                        <div>Serdecznie dziękujemy!</div>\
                        <div>Pozdrawiamy,</div>\
                        <div>Zespół Jobs Plus</div></div>")%(sex, position, sex2, sex5)
            
            if mail_to is not "":
                users_obj = self.pool.get('res.users')
                subject = _("Oceń naszą pracę")
                uid = users_obj.search(cr, uid, [('id','=',1)])[0]
                uid_id = users_obj.browse(cr, uid, uid)
                
                email_from = "Zespół Jobs Plus<rekrutacja@jobsplus.pl>"
                vals = {'email_from': email_from,
                        'email_to': mail_to,
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': body,
                        'auto_delete': True}
                        
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        
            return rate_id