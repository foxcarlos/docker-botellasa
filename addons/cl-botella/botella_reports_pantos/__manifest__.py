# -*- coding: utf-8 -*-
{
    'name' : 'Botella Informes Pantos',
    'summary': 'Módulo con informes',
    'author': 'Romina Bazan',
    'depends': ['stock_barcode',
                'botella_product',
                #stock_report_quantity_by_location
               ],
    'application': False,
    'data' : [
        'security/ir.model.access.csv',
        'wizards/occupied_positions_view.xml',
        'wizards/internal_movement_view.xml'
        ],
    'qweb': [
        #'static/src/xml/stock_barcode.xml',
    ],
    'installable': False,
}
