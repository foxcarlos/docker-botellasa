# -*- coding: utf-8 -*-
{
    'name' : 'Botella Warehouse Data',
    'summary': 'Módulo con adaptaciones de Warehouse/Inventario para Botellasas',
    'author': 'Gabriela Rivero',
    'depends': [# 'stock_barcode',
                #'botella_product',
                'delivery',
                'product_dimension',
                'product_packaging_dimension',
                # TODO evaluar modulos de stock dimension
                #'stock_quant_package_dimension',
                #'stock_quant_package_dimension_total_weight_from_packaging',
                'stock_reception_screen',
                #'shopfloor',
                'stock_move_location',
               ],
    'application': False,
    'data' : [
        #'views/product_view.xml',
        #'views/export_invertoy_report_view.xml',
        # 'views/botella_warehouse_import.xml',
        # TODO: definir dimension de ubicacion stock.location.storage.type
        #'data/tipo_ubicaciones_data.xml',
        'views/picking_view.xml',
        'data/locations_data.xml',
        'data/transporte_data.xml',
        # 'data/remito_data.xml',
        ],
    'qweb': [
        #'static/src/xml/stock_barcode.xml',
    ],
    'installable': True,
}
