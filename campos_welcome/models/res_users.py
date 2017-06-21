# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.addons.auth_signup.res_users import SignupError


import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'
    
    def auth_blaatlogin(self, cr, uid, member_number, ticket, context=None):
        user_ids = self.search(cr, uid, [("member_number", "=", member_number)])
        if not user_ids:
            crs_id = self.pool['campos.remote.system'].search(cr, uid, [('systype', '=', 'bm')])
            crs = self.pool['campos.remote.system'].browse(cr, uid, crs_id)
            values = crs.getBMuserData(member_number)
            values['member_number'] = member_number
            values['blaatlogin_ticket'] = ticket
            cr.commit()
            db, login, _ = self.signup(cr, uid, values)
            return {'db': db, 'login': login, 'do_reload': True}
            #user_ids = self.search(cr, uid, [("login", "=", login)])
        assert len(user_ids) == 1
        user = self.browse(cr, uid, user_ids[0], context=context)
        user.write({'blaatlogin_ticket': ticket})
        return {'db':cr.dbname, 'login':user.login}

    def signup(self, cr, uid, values, token=None, context=None):
        new_email = values.get('email')
        
        partner_id = False
        if new_email:
            partner_ids = self.pool['res.partner'].search(cr, uid, [('email', '=', new_email), ('is_company', '=', False)])
            if partner_ids:
                partner_id = partner_ids[0]
            else:
                part_ids = self.pool['campos.event.participant'].search(cr, uid, [('private_mailaddress', '=', new_email)])
                if part_ids:
                    partner_id = self.pool('campos.event.participant').browse(cr, uid, part_ids[0]).partner_id.id
            user_ids = self.pool['res.users'].search(cr, uid, [('login', '=', new_email)])
            if user_ids:
                partner_id = self.pool('res.users').browse(cr, uid, user_ids[0]).partner_id.id
            if partner_id:
                partner = self.pool['res.partner'].browse(cr, uid, partner_id)
                if partner.user_ids:
                    _logger.info('LOGIN: %s %s', partner.user_ids[0].login, values)
                    if not partner.last_import:
                         template_user = self.pool.get('ir.model.data').get_object(cr, 1, 'auth_signup', 'default_template_user')
                         self.pool('res.users').write(cr, 1, [ partner.user_ids[0].id], {'action_id': template_user.action_id.id,
                                                                                         'member_number': values.get('member_number'),
                                                                                         'blaatlogin_ticket': values.get('blaatlogin_ticket'),
                                                                                         'oauth_access_token': token,
                                                                                         'oauth_uid': values.get('oauth_uid'),
                                                                                         'oauth_provider_id': values.get('oauth_provider_id'),
                                                                                         'groups_id': [(4, self.pool.get('ir.model.data').get_object(cr, uid,'campos_preregistration','group_campos_groupleader').id),
                                                                                                       (4, self.pool.get('ir.model.data').get_object(cr, uid,'campos_welcome','group_campos_imported_group').id)],
                                                                                         })
                    return (cr.dbname, partner.user_ids[0].login, token if token else values.get('password'))
                else:
                    values['partner_id'] = partner_id
        return super(ResUsers, self).signup(cr, uid, values, token=token, context=context) 
        
