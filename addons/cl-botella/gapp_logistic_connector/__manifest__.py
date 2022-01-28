# Copyright 2019 jeo Software
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Conector GAPP Logistica",
    "summary": "Automatiza el envio y recepcion de mercaderia al deposito",
    "version": "12.0.0.0.0",
    "development_status": "Alpha",
    "category": "stock",
    "website": "http://jeosoft.com.ar",
    "author": "jeo Software",
    "maintainers": ["jobiols"],
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "excludes": [],
    "depends": [
        "base",
        'stock'
    ],
    "data": [
        'data/mail_template_data.xml',
        'views/stock_picking_view.xml'
    ],
    "demo": [
    ],
    "qweb": [
    ]
}
