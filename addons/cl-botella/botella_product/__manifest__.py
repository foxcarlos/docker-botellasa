{
    'name' : 'Botella Product',
    'description': ' Agrega campos en productos',
    'author': 'Romina Bazan',
    'depends': ['product',
                'product_brand',
                'product_dimension',
                'product_packaging_dimension',
                'product_planned_price',
                #'alan_customize'
    ],
    'data' : ['views/products_view.xml',
              #'views/products_packaging_view.xml',
              'views/products_brand.xml',
              #TODO: comento el acceso porque solo tiene variey y format
              #'security/ir.model.access.csv',
              #TODO: comento el archivo de grupos, porque tiene los roles de la app
              #'security/res_group.xml',
              #TODO : ver si data.xml (variantes ) las cargo con este archivo o los migro
              #'data/data.xml',
              'data/uom_data.xml',
             ],
    'installable': True,
}
