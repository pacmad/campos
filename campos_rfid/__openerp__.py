# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CampOS RFID',
    'description': """
        CampOS RFID Interface""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': ['mail', 'campos_jobber_final',
                'web_action_request',
                'web_widget_x2many_barchart',
                
    ],
    'data': [
        'views/event_registration.xml',
        'views/campos_event_participant.xml',
        'security/campos_rfid_device.xml',
        'views/campos_rfid_device.xml',
        'security/campos_canteen_slot.xml',
        'views/campos_canteen_slot.xml',
        'security/campos_canteen_stat.xml',
        'views/campos_canteen_stat.xml',
        'security/campos_canteen_instanse.xml',
        'views/campos_canteen_instanse.xml',
        'security/campos_canteen_ticket.xml',
        'views/campos_canteen_ticket.xml',
        'data/campos.canteen.slot.csv',
        'security/campos_rfid_log.xml',
        'views/campos_rfid_log.xml',
        'security/campos_cat_inst.xml',
        'views/campos_cat_inst.xml',
        'security/campos_cat_stat.xml',
        'views/campos_cat_stat.xml',
        #'views/event_registration_meatlist.xml',
        'views/event_day_meat.xml',
        'security/campos_cat_ticket.xml',
        'views/campos_cat_ticket.xml',
        'data/ir_cron.xml',
        
    ],
    'demo': [
    ],
}
