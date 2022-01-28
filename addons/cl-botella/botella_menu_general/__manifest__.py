# -*- coding: utf-8 -*-
{
    'name': 'Menu General',
    'description': 'Módulo que coloca iconos a las aplicaciones',
    'author': 'Bazan Daniela Romina',
    'depends': [
        'calendar',
        'contacts',
        #'alan_customize',
        'mail',
        'base',
        'crm',
        'mass_mailing',
        'marketing_automation',
        'helpdesk',
        'account',
        'purchase',
        #'documents',
        'hr',
        'im_livechat',
        'website_sale',
        'botella_menu',
        'om_account_accountant',
        # TODO: stock_enterprise
        #'stock_enterprise',
        'utm',
        'link_tracker',
        'web_export_view',
        'base_address_city',
        'web_group_expand',
        'padron_afip',
        'product_unique',
        'partner_vat_unique',
        'account_check',
        'l10n_ar_bank',
        'l10n_ar_afipws_fe',
        'website_sale_require_login',
        'auto_backup',
        'botella_filters',
        'l10n_ar_sale_order_type',
        'mass_editing',
        'l10n_ar_sale_order_type',
        'website_sale_order_type',
        'sale_order_type_ux',
    ],
    'application': True,
    'installable': True,
    'data':[
        'security/res_group.xml',
        'views/menu_general_view.xml',
        # TODO: migrar estilos
        #'views/template.xml'
    ]
}
