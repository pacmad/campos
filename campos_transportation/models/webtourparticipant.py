# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from ..interface import webtourinterface

import logging
from math import sin, cos, sqrt, atan2, radians
from operator import itemgetter
import googlemaps

_logger = logging.getLogger(__name__)

class WebtourParticipant(models.Model):
    _inherit = 'campos.event.participant'
    
    webtourususeridno = fields.Char('webtour us User ID no', required=False)
    webtourusgroupidno = fields.Char(string='webtour us Group ID no', related='registration_id.webtourusgroupidno')                                 
    
    tocampfromdestination_id = fields.Many2one('campos.webtourusdestination',
                                            'To camp Pick up',
                                            ondelete='set null') #, store=Truecompute='_compute_tocampfromdestination_id',
  
    fromcamptodestination_id = fields.Many2one('campos.webtourusdestination',
                                            'From camp Drop off',
                                            ondelete='set null')#,compute='_compute_fromcamptomdestination_id', store=True
    
    tocampdate = fields.Date(string='To Camp Date')
    fromcampdate = fields.Date(string='From Camp Date')
    
    tocampusneed_id = fields.Many2one('campos.webtourusneed','To Camp Need ID',ondelete='set null')
    fromcampusneed_id = fields.Many2one('campos.webtourusneed','From Camp Need ID',ondelete='set null')
    
    tocamp_TripType_id = fields.Many2one(related='registration_id.event_id.webtourconfig_id.tocamp_campos_TripType_id', readonly=True) 
    specialtocampdate_id = fields.Many2one('campos.webtourconfig.triptype.date', 'Special To Camp Date', domain="[('campos_TripType_id','=',tocamp_TripType_id)]", ondelete='set null', required=False) 
    
    fromcamp_TripType_id = fields.Many2one(related='registration_id.event_id.webtourconfig_id.fromcamp_campos_TripType_id', readonly=True)
    specialfromcampdate_id = fields.Many2one('campos.webtourconfig.triptype.date', 'Special From Camp Date', domain="[('campos_TripType_id','=',fromcamp_TripType_id)]", ondelete='set null', required=False) 

    individualtocampfromdestination_id = fields.Many2one('campos.webtourusdestination',
                                            'Individual To camp Pick up',
                                            ondelete='set null')
    individualfromcamptodestination_id = fields.Many2one('campos.webtourusdestination',
                                            'Individual From camp Drop off',
                                            ondelete='set null')
    
    recalctoneed = fields.Boolean('recalctoneed')
    recalcfromneed = fields.Boolean('recalcfromneed')
    
    tocamptravelgroup = fields.Selection([    ('1', 'Group 1'),
                                              ('2', 'Group 2'),
                                              ('3', 'Group 3'),
                                              ('4', 'Group 4'),
                                              ('5', 'Group 5')], default='1', string='Travel Group to Camp')
    
    fromcamptravelgroup = fields.Selection([  ('1', 'Group 1'),
                                              ('2', 'Group 2'),
                                              ('3', 'Group 3'),
                                              ('4', 'Group 4'),
                                              ('5', 'Group 5')], default='1', string='Travel Group from Camp')
    
    groupisdanish = fields.Boolean(related='registration_id.groupisdanish')
    donotparticipate = fields.Boolean('Do not participate') 
    
            
    @api.one
    def _compute_tocampfromdestination_id(self):
            #_logger.info("_compute_tocampfromdestination_id %s %s %s %s %s %s %s", len(self), par.id, par.tocampfromdestination_id, par.individualtocampfromdestination_id,par.registration_id.webtourgrouptocampdestination_id,par.registration_id.group_entrypoint.defaultdestination_id,par.registration_id.webtourdefaulthomedestination)
            destination=False
            if self.individualtocampfromdestination_id:
                destination = self.individualtocampfromdestination_id
            elif self.registration_id.webtourgrouptocampdestination_id:
                destination = self.registration_id.webtourgrouptocampdestination_id
            elif self.registration_id.group_entrypoint.defaultdestination_id:
                destination = self.registration_id.group_entrypoint.defaultdestination_id
            elif self.registration_id.webtourdefaulthomedestination:
                destination = self.registration_id.webtourdefaulthomedestination
            
            if  destination == False:
                _logger.info("_compute_tocampfromdestination_id No Destination known !!!!!!! %s", self.id)
                self.tocampfromdestination_id = False;
            else:
                if self.tocampfromdestination_id != destination:
                    _logger.info("_compute_tocampfromdestination_id Update %s %s %s",self.id,self.tocampfromdestination_id,destination)
                    self.tocampfromdestination_id = destination
                    return True
            
            return False 
                                                  
    @api.one
    def _compute_fromcamptomdestination_id(self):
        #_logger.info("_compute_fromcamptomdestination_id %s %s %s %s %s %s %s", len(self), par.id, par.fromcamptodestination_id, par.individualfromcamptodestination_id,par.registration_id.webtourgroupfromcampdestination_id,par.registration_id.group_exitpoint.defaultdestination_id,par.registration_id.webtourdefaulthomedestination)
        destination=self.fromcamptodestination_id
        if self.individualfromcamptodestination_id:
            destination = self.individualfromcamptodestination_id
        elif self.registration_id.webtourgroupfromcampdestination_id:
            destination = self.registration_id.webtourgroupfromcampdestination_id
        elif self.registration_id.group_exitpoint.defaultdestination_id:
            destination = self.registration_id.group_exitpoint.defaultdestination_id
        elif self.registration_id.webtourdefaulthomedestination:
            destination = self.registration_id.webtourdefaulthomedestination

        if  destination == False:
            _logger.info("individualfromcamptodestination_id No Destination known !!!!!!! %s",self.id)
            self.fromcamptodestination_id = False;
        else:
            if self.fromcamptodestination_id != destination:
                _logger.info("individualfromcamptodestination_id Update %s %s %s",self.id, self.fromcamptodestination_id.id,destination.id)
                self.fromcamptodestination_id = destination
                return True
        
        return False                
                         
    @api.one
    def _compute_tocampdate(self):        
        tocampdate = False
        dates = []
        if self.specialtocampdate_id:
            tocampdate = self.specialtocampdate_id.name
        else:
            for d in self.camp_day_ids:
                if d.will_participate:
                    dates.append(d.the_date)
    
            dates.sort()
            if len(dates) > 0:
                tocampdate = dates[0]
            else :
                tocampdate = False
                
        if self.tocampdate != tocampdate:
            _logger.info("_compute_tocampdate, Update %s %s %s %s %s",self.id, self.specialtocampdate_id,dates,self.tocampdate,tocampdate)
            self.tocampdate = tocampdate      
            return True
        
        return False                
            
    @api.one
    def _compute_fromcampdate(self):
        dates = []
        fromcampdate = False           
        if self.specialfromcampdate_id:
            fromcampdate = self.specialfromcampdate_id.name
        else:
            for d in self.camp_day_ids:
                if d.will_participate:
                    dates.append(d.the_date)
    
            dates.sort(reverse=True)
            if len(dates) > 0:
                fromcampdate = dates[0]
            else :
                fromcampdate = False
        if self.fromcampdate != fromcampdate:
            _logger.info("_compute_fromcampdate, Update %s %s %s %s %s",self.id,self.specialfromcampdate_id,dates,self.fromcampdate,fromcampdate)
            self.fromcampdate = fromcampdate
            return True
        
        return False
              
    @api.model
    def get_create_usgroupidno_tron(self):
        MAX_LOOPS_usGroup = 100  #Max No of Groups pr Scheduled call
        MAX_LOOPS_usUser = 1000  #Max No of Users pr Scheduled call
        _logger.info("get_create_usgroupidno_tron: Here we go...")

        # find participants having transort need but missing usGroupIDno
        rs_missingusGroupIDno= self.env['campos.event.participant'].search([('registration_id.event_id', '=', 1),('webtourusgroupidno', '=', False),('registration_id.scoutgroup', '=', True)
                                                                            ,'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        # make at list of distinct Registrationid missing
        missingRegistrationidlist=[]
        for r in rs_missingusGroupIDno:
            if r.registration_id.id in missingRegistrationidlist: 
                continue 
            else:
                missingRegistrationidlist.append(r.registration_id.id)                                                                       

        #_logger.info("get_create_usgroupidno_tron: %s usGroupIDno's missing ",missingRegistrationidlist)
             
        #Get all usGroupIDno's from webtour and conver to a simple list
        response_doc=webtourinterface.usgroup_getall(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'))
        usgroups = response_doc.getElementsByTagName("a:IDno")
        usgrouplist=[]

        for g in usgroups:
            usgrouplist.append(str(g.firstChild.data))

        # find all registrations missing usgroupidno or is missing in webtour
        rs_missingusgroupidno= self.env['event.registration'].search(['|',('id','in',missingRegistrationidlist)
                                                                      ,'&',('webtourusgroupidno', '!=', False),('webtourusgroupidno','not in',usgrouplist)])
        
        _logger.info("get_create_usgroupidno_tron: %d (%d) usGroupIDno's missing. Got %d usGroupIDno's from Webtour",len(missingRegistrationidlist),len(rs_missingusgroupidno),len(usgrouplist))    
        
        # for each registation check usgroupidno name and create if missing
        g = 0
        for rec in rs_missingusgroupidno:
            newidno=webtourinterface.usgroup_getbyname(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id))
            if newidno == "0":
                # xx newidno=webtourinterface.usgroup_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id))
                if newidno != "0": #remember also this usgroupidno
                    usgrouplist.append
                
            _logger.info("get_create_usgroupidno_tron Group: %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, newidno)
            
            if newidno <> "0": #Update registration
                dicto = {}
                dicto["webtourusgroupidno"] = newidno
                rec.write(dicto)
                 
            rec.env.cr.commit()                 
            
            g = g +1
            if g > MAX_LOOPS_usGroup:
                break

               
        # find participants missing usUserIDno, from Registration having a usGroupIDno
        rs_missingususeridno= self.env['campos.event.participant'].search([('webtourususeridno', '=', False),('webtourusgroupidno', 'in', usgrouplist)
                                                                          ,'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        
        # for each participant check ususeridno name and create if missing
        g=0
        for rec in rs_missingususeridno:
            newidno=webtourinterface.ususer_getbyexternalid(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.ususer_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),str(rec.id), rec.webtourusgroupidno,str(rec.id),str(rec.registration_id))
            
            _logger.info("get_create_usgroupidno_tron User: %s %s %s %s %s",str(rec.id), rec.name, rec.webtourusgroupidno, rec.webtourususeridno,newidno)
            
            if newidno <> "0": #Update participant
                dicto = {}
                dicto["webtourususeridno"] = newidno
                rec.write(dicto)
                
            rec.env.cr.commit()               
            
            g = g +1
            if g > MAX_LOOPS_usUser:
                break
            
        self.env['campos.webtourusneed'].get_create_usneed_tron()        

        return True
    
    @api.multi
    def write(self, vals):
        _logger.info("Write Entered %s", vals.keys())
        ret = super(WebtourParticipant, self).write(vals)
                      
        for par in self:
            notdoneto = True
            notdonefrom = True
            if  'recalctoneed' in vals or 'individualtocampfromdestination_id' in vals:           
                if [True] == par._compute_tocampfromdestination_id():
                    notdoneto = False
                   
            if  'recalcfromneed' in vals or 'individualfromcamptodestination_id' in vals:
                if [True] == par._compute_fromcamptomdestination_id():
                    notdonefrom = False
            
            if  ('camp_day_ids' in vals
                 or 'specialtocampdate_id'):    
                if [True] == par._compute_tocampdate():
                    notdoneto = False
                    
            if  ('camp_day_ids' in vals
                 or 'specialfromcampdate_id'):        
                if [True] == par._compute_fromcampdate():
                    notdonefrom = False                
                
            if  ('tocampfromdestination_id' in vals
                or 'tocamptravelgroup' in vals
                or 'tocampdate' in vals
                or 'transport_to_camp' in vals               
                or ('recalctoneed' in vals and notdoneto)
                or 'deregistered' in vals 
                ):
                par.update_tocampusneed()

            if  ('fromcamptodestination_id' in vals 
                or 'fromcamptravelgroup' in vals                                
                or 'fromcampdate' in vals
                or 'transport_from_camp' in vals
                or ('recalcfromneed' in vals and notdonefrom)
                or 'deregistered' in vals                
                ):
                par.update_fromcampusneed()
                
            if 'state' in vals:
                par.donotparticipate = par.state == 'deregistered'
            else:
                if par.donotparticipate != (par.state == 'deregistered'):
                    par.donotparticipate = par.state == 'deregistered'                            
                                                                      
        return ret

    @api.one
    def update_tocampusneed(self):
      
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.registration_id.event_id.id)])
        campdesination= webtourconfig.campdestinationid.destinationidno
        # Check if date included in to From camp dates
        rs= self.env['campos.webtourconfig.triptype.date'].search([('campos_TripType_id', '=', self.tocamp_TripType_id.id),('name', '=', self.tocampdate)])
        
        if self.tocampusneed_id.id == False:
            dicto1 = {}
            dicto1["participant_id"] = self.id
            dicto1["travelgroup"] = self.tocamptravelgroup
            dicto1["campos_demandneeded"] = self.transport_to_camp and not self.donotparticipate and len(rs)> 0 
            dicto1["campos_TripType_id"] = webtourconfig.tocamp_campos_TripType_id.id
            dicto1["campos_traveldate"]  = self.tocampdate
            dicto1["campos_startdestinationidno"] = self.tocampfromdestination_id.destinationidno
            dicto1["campos_enddestinationidno"] = campdesination
            dicto1["webtour_useridno"] = self.webtourususeridno
            dicto1["webtour_groupidno"] = self.webtourusgroupidno
            dicto1["campos_writeseq"] = self.env['ir.sequence'].get('webtour.transaction')
        
            usneed_obj = self.env['campos.webtourusneed']                
            self.tocampusneed_id = usneed_obj.create(dicto1)
        else:
            dicto1 = {}   
            dicto1["travelgroup"] = self.tocamptravelgroup                             
            dicto1["campos_demandneeded"]  = self.transport_to_camp and not self.donotparticipate and len(rs)> 0 
            dicto1["campos_traveldate"]  = self.tocampdate
            dicto1["campos_startdestinationidno"]  = self.tocampfromdestination_id.destinationidno
            dicto1["campos_enddestinationidno"]  = campdesination
            dicto1["webtour_useridno"]  = self.webtourususeridno
            dicto1["webtour_groupidno"]  = self.webtourusgroupidno
            dicto1["campos_writeseq"]  = self.env['ir.sequence'].get('webtour.transaction')  
            self.tocampusneed_id.write(dicto1)
            
        _logger.info("Update_tocampusneed %s", dicto1)
        
    @api.one
    def update_fromcampusneed(self):
      
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', self.registration_id.event_id.id)])
        campdesination= webtourconfig.campdestinationid.destinationidno           
        # Check if date included in to From camp dates
        rs= self.env['campos.webtourconfig.triptype.date'].search([('campos_TripType_id', '=', self.fromcamp_TripType_id.id),('name', '=', self.fromcampdate)])
                            
        if self.fromcampusneed_id.id == False:
            dicto1 = {}
            dicto1["participant_id"] = self.id
            dicto1["travelgroup"] = self.fromcamptravelgroup            
            dicto1["campos_demandneeded"] = self.transport_from_camp and not self.donotparticipate and len(rs)> 0      
            dicto1["campos_TripType_id"] = webtourconfig.fromcamp_campos_TripType_id.id                                  
            dicto1["campos_traveldate"] = self.fromcampdate                  
            dicto1["campos_startdestinationidno"] = campdesination
            dicto1["campos_enddestinationidno"] = self.fromcamptodestination_id.destinationidno
            dicto1["webtour_useridno"] = self.webtourususeridno
            dicto1["webtour_groupidno"] = self.webtourusgroupidno
            dicto1["campos_writeseq"] = self.env['ir.sequence'].get('webtour.transaction')
                                                
            usneed_obj = self.env['campos.webtourusneed']                
            self.fromcampusneed_id = usneed_obj.create(dicto1)
        else:
            dicto1 = {} 
            dicto1["travelgroup"] = self.fromcamptravelgroup               
            dicto1["campos_demandneeded"]  = self.transport_from_camp and not self.donotparticipate and len(rs)> 0 
            dicto1["campos_traveldate"] = self.fromcampdate 
            dicto1["campos_startdestinationidno"]  = campdesination
            dicto1["campos_enddestinationidno"]  = self.fromcamptodestination_id.destinationidno
            dicto1["webtour_useridno"]  = self.webtourususeridno
            dicto1["webtour_groupidno"]  = self.webtourusgroupidno     
            dicto1["campos_writeseq"]  = self.env['ir.sequence'].get('webtour.transaction')
            self.fromcampusneed_id.write(dicto1)
                       
        _logger.info("update_fromcampusneed %s", dicto1)
         
    
    
    @api.multi
    def action_webtour_jobber_findclosestlocations(self):
        for par in self:
            if par.groupisdanish:
                # If gep point is missing, try to calculate
                if (par.partner_id.partner_latitude==0):
                    par.partner_id.geocode_address()
                    if (par.partner_id.partner_latitude > 0):
                        _logger.info("Try to commit Non Google geocode")
                        par.env.cr.commit()
                    
                # if still no result try geocode with Googlemap
                if (par.partner_id.partner_latitude==0):
                    gmaps2 = googlemaps.Client(key=self.env['ir.config_parameter'].get_param('campos_transportation_googlemaps_key.geocode'))
        
                    _logger.info("Try to Geocode with Googlemaps %s %s %s",par.partner_id.street,par.partner_id.zip,par.partner_id.city)
                    
                    try:
                        a = par.partner_id.street+', '+ par.partner_id.zip+' '+par.partner_id.city
                        geocode_result = gmaps2.geocode(a)
                        lat=geocode_result[0]['geometry']['location']['lat']
                        lng=geocode_result[0]['geometry']['location']['lng']
                        par.partner_id.partner_latitude = float(lat)
                        par.partner_id.partner_longitude = float(lng)
                        _logger.info("Got Googlemap Geocoding  %f %f",par.partner_id.partner_latitude,par.partner_id.partner_longitude)
                        par.env.cr.commit()
                    except:
                        pass
                                        
                # If geo point pressent lets go.... GOOGLEMAP DIAABLED          
                if (par.partner_id.partner_latitude<>0):    
        
                    destinations = self.env['campos.webtourusdestination'].search([('name', '<>', '')])
                    
                    # approximate radius of earth in km
                    R = 6373.0
                    
                    #Home adresse cord
                    lat1 = radians(par.partner_id.partner_latitude)
                    lon1 = radians(par.partner_id.partner_longitude)  
        
                    dists=[] #placeholder for beeline distance from home to all destinations
                    
                    for d in destinations:
                        lat2 = radians(float(d.latitude))
                        lon2 = radians(float(d.longitude))
                        
                        dlon = lon2 - lon1
                        dlat = lat2 - lat1
        
                        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                        c = 2 * atan2(sqrt(a), sqrt(1 - a))
                        distance = R * c
                        
                        dists.append([d.id,distance,float(d.latitude),float(d.longitude)]) 
                      
                    sdists = sorted(dists, key=itemgetter(1)) #we need the distance i acending order
                          
                    lat1 = par.partner_id.partner_latitude
                    lon1 = par.partner_id.partner_longitude
                                          
                    n = 0;  #counter for no of dist to googlemaps
                    origins=[] #placeholder list for origons to googlemaps
                    destinations =[] #placeholder list for desinations to googlemaps
                    origins.append((lat1,lon1)) #Home add            
                    homedestination = False
                    homedistance = False
                    homeduration = False
                    for d in sdists: # loop through sorted pickuplocations and prepare datat for googlemaps request
        
                        destinations.append((d[2],d[3])) # get geo point stored in loop above
                        n = n+1 
                        if (n > 4):
                            break       #Max 5 distinations    
                          
                    # call googlemap to find distances by car to the neerst distinations
                    gmaps = googlemaps.Client(key=self.env['ir.config_parameter'].get_param('campos_transportation_googlemaps_key.distance_matrix'))
                    matrix = gmaps.distance_matrix(origins, destinations)
                    _logger.info("Google maps responce %s", matrix)
                    
                    n = 0
                    for d in sdists: # loop through sorted pickuplocations and evaluate corosponing googlemaps responce
                        distance=matrix['rows'][0]['elements'][n]['distance']['value']
                        distancekm =  distance/1000.0             
                        duration=matrix['rows'][0]['elements'][n]['duration']['text']
                        
                        if (n == 0): 
                            homedistance = distancekm
                            homeduration = duration
                            homedestination = d[0]
                        else:
                            if (homedistance > distancekm):
                                homedestination = d[0]
                                homedistance = distancekm
                                homeduration = duration                    
                        
                        n = n+1 
                        if (n > 4):
                            break       #Max 5 distinations                       
                        
                    if homedestination:
                        _logger.info("Closest Home Destination found %s %f %s",homedestination, homedistance,homeduration)
                        par.individualtocampfromdestination_id=homedestination
                        par.individualfromcamptodestination_id=homedestination

                    else:
                        _logger.info("!!!!!!!!!!!! No Home Destination found")    
                 
    @api.multi
    def clearusecamptransport(self):
        # find participants missing usUserIDno, from Registration having a usGroupIDno
        #rs = self.env['campos.event.participant'].search([('transport_from_camp', '=', True)])
        #for rec in rs:
        #    rec.transport_from_camp = False   
        
        return True
    
class WebtourParticipantCampDay(models.Model):
    '''
    One persons participation to a camp in one day Webtour
    '''
    _inherit = 'campos.event.participant.day'
    webtourcamptransportation = fields.Char('Camp transportation',compute='_compute_webtourcamptransportation')

    @api.one
    def _compute_webtourcamptransportation(self):
        #_logger.info("_compute_webtourcamptransportation %s %s %s", self, self.participant_id,self.participant_id.tocampfromdestination_id)
        if self.the_date == self.participant_id.tocampdate:
            if self.participant_id.transport_to_camp and self.participant_id.tocampfromdestination_id.placename:
                # Check if date included in to To camp dates
                rs= self.env['campos.webtourconfig.triptype.date'].search([('campos_TripType_id', '=', self.participant_id.tocamp_TripType_id.id),('name', '=', self.participant_id.tocampdate)])
                #_logger.info("_compute_webtourcamptransportation rs %s", rs)
                
                if len(rs)> 0:
                    self.webtourcamptransportation = 'To Camp from: ' + self.participant_id.tocampfromdestination_id.webtourname
                else:
                    self.webtourcamptransportation = 'No Camp Transportation To camp avaible this day!!!'
            else:
                self.webtourcamptransportation = ''
                           
        elif self.the_date == self.participant_id.fromcampdate:
            if self.participant_id.transport_from_camp and self.participant_id.fromcamptodestination_id.placename:
                # Check if date included in to To camp dates
                rs= self.env['campos.webtourconfig.triptype.date'].search([('campos_TripType_id', '=', self.participant_id.fromcamp_TripType_id.id),('name', '=', self.participant_id.fromcampdate)])
                #_logger.info("_compute_webtourcamptransportation rs %s", rs)
                
                if len(rs)> 0:
                    self.webtourcamptransportation = 'From Camp to: ' + self.participant_id.fromcamptodestination_id.webtourname                    
                else:
                    self.webtourcamptransportation = 'No Camp Transportation From camp avaible this day!!!'
            else:
                self.webtourcamptransportation = ''
        else:
                self.webtourcamptransportation = ''

             

                
        