# -*- coding: utf-8 -*-
{
    'name' : 'Botella Warehouse',
    'summary': 'Módulo con adaptaciones de Warehouse/Inventario para Botellasas',
    'author': 'Gabriela Rivero',
    'depends': ['stock_barcode',
                'botella_product',
               ],
    'application': False,
    'data' : [
        'views/product_view.xml',
        'views/export_invertoy_report_view.xml',
        'views/botella_warehouse_import.xml',
        'data/tipo_ubicaciones_data.xml',
        'data/locations_data.xml',
        'data/transporte_data.xml',
        'data/remito_data.xml',
        ],
    'qweb': [
        'static/src/xml/stock_barcode.xml',
    ],
    'installable': False,
}
