{
    'name' : 'Productos',
    'description': 'Menu para dar de alta productos',
    'author': 'Romina Bazan',
    'depends': ['base',
                'import_product_variant',
                'product',
                'botella_product',
                'import_product_image',
                'website_sale',
                #'alan_customize'
               ],
    'application': True,
    'installable': True,
    'data' : ['views/menu_view.xml']
}
