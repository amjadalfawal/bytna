{
    'name': 'PO Multi Product Selection',
    'version': '15.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Purchase order Multiple Product Selection',
    'description': """
        This module provide select multiple products
        Features includes managing
            * allow to choose multiple products at once in purchase order
    """,
    'author': "tecnotetech",
    'depends': ['base', 'product', 'purchase', 'tecnote_purchase_barcode'],
    'data': [
        'wizard/select_products_wizard_view.xml',
        'views/purchase_views.xml',
        'security/ir.model.access.csv'
    ],

    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
