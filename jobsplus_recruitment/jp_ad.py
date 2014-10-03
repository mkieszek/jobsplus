# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 11:07:22 2013

@author: pczorniej
"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
import pdb
import datetime
from email.header import decode_header

def decode(text):
    """Returns unicode() string conversion of the the given encoded smtp header text"""
    if text:
        text = decode_header(text.replace('\r', ''))
        return ''.join([tools.ustr(x[0], x[1]) for x in text])
    
class jp_ad(osv.Model):
    _name = "jp.ad"
    _inherit = 'mail.thread'
    _description = 'Ogloszenie'

    def _portal_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict(map(lambda x: (x,{'portal_count': 0}), ids))
        # the user may not have access rights for opportunities or meetings
        try:
            for ad in self.browse(cr, uid, ids, context):
                res[ad.id] = {
                    'portal_count': len(ad.publish_ids),
                }
        except:
            pass
        return res
    
    _columns = {
        'name': fields.char('ID',readonly=True, size=64),  
        'stage_id': fields.many2one('jp.ad.stage', 'Stage'),
        'position': fields.char('Position',Size=64, required=True),
        'deal_id': fields.many2one('jp.deal','Recruitment', required=True),
        'publish_ids': fields.one2many('jp.publish','ad_id','Ads publish'),
        'portal_count': fields.function(_portal_count, string="Portals", type='integer', multi='opp_meet'),
        'country_id': fields.many2one('res.country','Country'),
        'activity': fields.boolean('Active', track_visibility='onchange'),
        'portal_id' : fields.many2one('jp.portal', 'Portal'),
        'state_id' : fields.many2one('res.country.state','State'),
        'workplace': fields.char('Workplace'),
        'trade_ids' : fields.many2many('jp.trade', 'jp_ad_trade_rel','ad_id','trade_id', 'Trade'),
        'ad_content': fields.html('Ad content'),
        'publish_on': fields.boolean('Publish on jobsplus.pl', track_visibility='onchange'),
        'highlighted': fields.boolean('Highlighted', track_visibility='onchange'),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'candidate_ids': fields.one2many('jp.candidate','ad_id','Candidates'),
        'gumtree_title': fields.char('Gumtree title'),
    }

    _defaults ={
        #'activity': False,
    }    
    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'jp.ad') or '/'

        ad_id = super(jp_ad, self).create(cr, uid, vals, context=context)
        ad = self.browse(cr, uid, ad_id)
        if ad.publish_on == True and ad.activity == True:
            groups_obj = self.pool.get('res.groups')
            users_obj = self.pool.get('res.users')
            #Wysyła wiasomość do Marketingu Jobs Plus
            config_obj = self.pool.get('jp.config.settings')
            jp_crm = config_obj.current_jp_settings(cr, uid, 'jobsplus_crm')
    
            group_id = groups_obj.search(cr, uid, [('name','=','Marketing Jobs Plus')])
            users = groups_obj.browse(cr, uid, group_id[0]).users
            mail_to = ''
            for user in users:
                if user.email != False:
                    mail_to += user.email+', '
            if mail_to != '':
                url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.ad")%(jp_crm, cr.dbname, ad.id)
                body = decode("Ogłoszenie na stanowisko %s zostało zmienione.<br/><a href='%s'>Link do ogłoszenia</a>")%(ad.position, url)
                subject = mail_message.decode("Odoo - publikacja ogłoszenia.")
                uid_id = users_obj.browse(cr, uid, uid)
                vals = {'email_from': uid_id.partner_id.name+"<"+uid_id.partner_id.email+">",
                        'email_to': mail_to,
                        'state': 'outgoing',
                        'subject': subject,
                        'body_html': body,
                        'auto_delete': True}
                        
                self.pool.get('mail.mail').create(cr, uid, vals, context=context)
        
        return ad_id
    
    def write(self, cr, uid, ids, vals, context=None):
        ad_id = super(jp_ad, self).write(cr, uid, ids, vals, context=context)
        for ad in self.browse(cr, uid, ids):
            if (ad.activity == True and (('highlighted' in vals and ad.publish_on == True) or ('publish_on' in vals))) or ('activity' in vals and vals['activity'] == False and ad.publish_on == True):
                groups_obj = self.pool.get('res.groups')
                users_obj = self.pool.get('res.users')
                #Wysyła wiasomość do Marketingu Jobs Plus
                config_obj = self.pool.get('jp.config.settings')
                jp_crm = config_obj.current_jp_settings(cr, uid, 'jobsplus_crm')
        
                group_id = groups_obj.search(cr, uid, [('name','=','Marketing Jobs Plus')])
                users = groups_obj.browse(cr, uid, group_id[0]).users
                mail_to = ''
                for user in users:
                    if user.email != False:
                        mail_to += user.email+', '
                if mail_to != '':
                    url = ("http://%s/?db=%s#id=%s&view_type=form&model=jp.ad")%(jp_crm, cr.dbname, ad.id)
                    body = decode("Ogłoszenie na stanowisko %s zostało zmienione.<br/><a href='%s'>Link do ogłoszenia</a>")%(ad.position, url)
                    subject = decode("Odoo - publikacja ogłoszenia.")
                    uid_id = users_obj.browse(cr, uid, uid)
                    vals = {'email_from': uid_id.partner_id.name+"<"+uid_id.partner_id.email+">",
                            'email_to': mail_to,
                            'state': 'outgoing',
                            'subject': subject,
                            'body_html': body,
                            'auto_delete': True}
                            
                    self.pool.get('mail.mail').create(cr, uid, vals, context=context)
                
        return ad_id
        
    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list) :
            ids = [ids]
        res = []
        if not ids:
            return res
        
        reads = self.read(cr, uid, ids, ['name', 'position'], context)

        for record in reads:
            name = record['name']
            title = record['position']
            res.append((record['id'], name + ' - ' + title))
        return res

        
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            #name = name.split(' / ')[-1]
            name_ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            position_ids = self.search(cr, uid, [('position', operator, name)] + args, limit=limit, context=context)
            ids=name_ids+position_ids
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
        
    def _deactivation_publish(self, cr, uid, context=None):
        #pdb.set_trace()
        publish_active_obj = self.pool.get('jp.publish')
        publish_active_ids = publish_active_obj.search(cr, uid, [('status','=',1)], context=context)
        
        today = datetime.date.today()
        
        for publish_active in publish_active_obj.browse(cr, uid, publish_active_ids, context=context):
            expiration_date = publish_active.expiration_date
            
            if expiration_date:
                expiration_date = datetime.datetime.strptime(expiration_date,"%Y-%m-%d").date()
                
                if today > expiration_date:
    
                    vals = {
                        'status': '2',
                    }
                    
                    publish_active_obj.write(cr, uid, [publish_active.id], vals, context=context)
        
    def deactivation_ad(self, cr, uid, context=None):
        self._deactivation_publish(cr, uid, context=context)
        
        ad_active_id = self.search(cr, uid, [('activity','=',True), ('publish_on','=', False)], context=context)
        
        if ad_active_id:
            publish_obj = self.pool.get('jp.publish')
            
            for ad_active in ad_active_id:
                publish_active_id = publish_obj.search(cr, uid, [('ad_id','=',ad_active),('status','=',1)], context=context)
                
                if not publish_active_id:

                    vals = {
                        'activity': 0                    
                    }
                    self.pool.get('jp.ad').write(cr, uid, [ad_active], vals, context=context)
                      