
# -*- encoding: utf-8 -*-
{
    'name': 'Carga de productos y variantes',
    'version': '1.0',
    'category': 'Nybble',
    'sequence': 1,
    'summary': 'Carga de productos y variantes',
    'depends': ['stock', ],
    'author': 'Romina',
    'description': """
Carga de productos y variantes
===============
Agrega un wizard en productos para importar productos a partir de archivo excel
""",
    'data': [
        'wizards/carga_productos_variantes.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': False,
    'application': False,
    'auto_install': False,
}
