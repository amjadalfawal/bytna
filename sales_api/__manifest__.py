{
    'name': ' Sales Apis',
    'version': '1.0',
    'category': '',
    'sequence': 45,
    'summary': 'api for Sales',
    'depends': [
        'base',
        'sale',
        'mail',
        'stock',
        'contacts',
    ],
    'description': "",
    'data': [
        'views/res_user.xml',
        'views/product_brand_ept.xml',
        'views/product_template.xml',
        'views/sales_target_view.xml',
        'views/partner_view.xml',
        'security/ir.model.access.csv',

    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
