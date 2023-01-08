# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'All in one import images from zip file',
    'version': '15.0.0.1',
    'sequence': 11,
    'category': 'Extra Tools',
    'summary': 'import image from zip import product image from zip import bulk image from zip import partner image from zip import images from zip file import product images from zip import image by zip import images by zip all images import from zip product image import',
    "price": 12,
    "currency": 'EUR',
    'description': """


        All in one import images from zip file in odoo,
        Easy to Import bulk of images on Odoo by Using Zip file,
        import images from zip file for product template in odoo,
        import images from zip file for product variants in odoo,
        import images from zip file for partner or customer in odoo,
        import images from zip file for employee in odoo,
        import images from zip file product by name or internal reference or barcode or id in odoo,
        import images from zip file partner by name or internal reference or id in odoo,
        import images from zip file employee by name or id or identification no. in odoo,

    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'depends': ['base','sale','account','hr','sale_management'],
    'data': ['security/img_security.xml',
            'security/ir.model.access.csv',
            'wizard/sale.xml',
            "data/attachment_sample.xml"

             ],
	'qweb': [
		],
    'demo': [],
    'test': [],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/wtmKw-cYtxM',
    "images":["static/description/Banner.png"],
}
