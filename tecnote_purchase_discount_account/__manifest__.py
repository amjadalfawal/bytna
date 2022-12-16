# -*- coding: utf-8 -*-
{
    'name': 'Purchase Discount Account',
    'category': 'Operations/Purchase',
    'summary': 'Purchase Discount Account',
    'description': """
This module adds discount to the purchase module, separate the invoice discount entries.
Also Pass value of discount and price of last purchase order to vendor pricelist

""",
    'author': 'tecnote Technology',
    'website': 'https://www.tecnote.ca/',
    'depends': ['account_accountant', 'purchase', 'purchase_stock'],
    'data': [
        'views/purchase_views.xml',
        'views/report_purchase_order.xml',
        'views/invoice_report.xml',
        'views/product_supplierinfo_view.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'reports/purchase_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}