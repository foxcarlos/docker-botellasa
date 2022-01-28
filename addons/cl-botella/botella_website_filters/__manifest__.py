# -*- coding: utf-8 -*-
{
    'name' : 'Botella Website Filters',
    'summary': 'Módulo con adaptaciones web/filtros pais, region, bodega, fabricante',
    'author': 'Gabriela Rivero',
    'depends': ['website_sale',
                'atharva_theme_general',
                'botella_filters',
               ],
    'application': False,
    'data' : [
        'views/templates.xml',
        'views/assets.xml',
        'views/product_variety_template.xml',
        'views/product_country_template.xml',
        'views/product_state_template.xml',
        'views/product_region_template.xml',
        'views/product_zona_template.xml',
        'views/product_puntaje_template.xml',
        'views/price_template.xml',
        ],
    'qweb': [
    ],
    'installable': True,
}
