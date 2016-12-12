# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface

import logging

_logger = logging.getLogger(__name__)

class WebtourParticipant(models.Model):
    _inherit = 'campos.event.participant'
    
    webtourususeridno = fields.Char('webtour us User ID no', required=False)
    webtourusgroupidno = fields.Char(string='webtour us Group ID no', related='registration_id.webtourusgroupidno')                                 
    
    tocampfromdestination_id = fields.Many2one('campos.webtourusdestination',
                                            'destinationidno',
                                            ondelete='set null')
    fromcamptodestination_id = fields.Many2one('campos.webtourusdestination',
                                            'destinationidno',
                                            ondelete='set null')
    tocampdate = fields.Date('To Camp Date', required=False)
    fromcampdate = fields.Date('From Camp Date', required=False)
    usecamptransporttocamp = fields.Boolean('Use Camp Transport to Camp', required=False, default=True)
    usecamptransportfromcamp = fields.Boolean('Use Camp Transport from Camp', required=False, default=True)
    tocampusneed_id = fields.Char('To Camp Need ID', required=False)
    fromcampusneed_id = fields.Char('From Camp Need ID', required=False)
   
    @api.model
    def get_create_usgroupidno_tron(self):
        
        _logger.info("get_create_usgroupidno_tron: Here we go...")
        
        #Get all usGroupIDno's from webtour and conver to a simple list
        response_doc=webtourinterface.usgroup_getall()
        usgroups = response_doc.getElementsByTagName("a:IDno")
        usgrouplist=[]

        for g in usgroups:
            usgrouplist.append(str(g.firstChild.data))
        
        _logger.info("get_create_usgroupidno_tron: Got %d usGroupIDno's from Webtour", len(usgrouplist))           

        # find all registrations missing usgroupidno
        rs_missingusgroupidno= self.env['event.registration'].search([('event_id', '=', 1),('state', '=', 'open'),('scoutgroup', '=', True),('webtourusgroupidno','not in',usgrouplist)])
        
        # for each registation check usgroupidno name and create if missing
        for rec in rs_missingusgroupidno:
            newidno=webtourinterface.usgroup_getbyname(str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.usgroup_create(str(rec.id))
                if newidno != "0": #remember also this usgroupidno
                    usgrouplist.append
                
            _logger.info("get_create_usgroupidno_tron Group: %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, newidno)
            
            if newidno <> "0": #Update registration
                dicto = {}
                dicto["webtourusgroupidno"] = newidno
                rec.write(dicto) 

        # find participants missing usUserIDno, from Registration having a usGroupIDno
        rs_missingususeridno= self.env['campos.event.participant'].search([('participant', '=', True),('webtourususeridno', '=', False),('webtourusgroupidno', 'in', usgrouplist)])
        for rec in rs_missingususeridno:
            newidno=webtourinterface.ususer_getbyexternalid(str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.ususer_create(str(rec.id), rec.webtourusgroupidno,str(rec.id),str(rec.registration_id))
            
            _logger.info("get_create_usgroupidno_tron User: %s %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, rec.webtourususeridno,newidno)
            
            if newidno <> "0": #Update participant
                dicto = {}
                dicto["webtourususeridno"] = newidno
                rec.write(dicto)            

        return True
    
    @api.one
    def write(self, vals):
        _logger.info("Transportation Participant Write Entered %s", vals.keys())
        for par in self:
            _logger.info("Transportation Participant Write Kilroy WAS HERRE")       
            if 'tocampfromdestination_id' in vals:
                _logger.info("Transportation Participant Write found new dest %s", par.tocampfromdestination_id)
        ret = super(WebtourParticipant, self).write(vals)    
        return ret
    
    @api.multi
    def write(self, vals):
        _logger.info("Transportation Participant Write Entered %s", vals.keys())
        for par in self:
            _logger.info("Transportation Participant Write Kilroy WAS HERRE")       
            if 'tocampfromdestination_id' in vals:
                _logger.info("Transportation Participant Write found new dest %s", par.tocampfromdestination_id)
        ret = super(WebtourParticipant, self).write(vals)    
        return ret