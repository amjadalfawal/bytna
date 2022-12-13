# -*- coding: utf-8 -*-
{
    'name': 'TecNote Sale Discount',
    'summary': ' Sale Discount',
    'description': """
        This module add manage discount in sale module.
    """
    ,
    'author': 'Amjad Alfawal',
    'website': '',
    'depends': [
        'sale_management',
        'delivery',
    ],
    'data': [
        'views/sale_order_inherit_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'application': False,
    'installable': True,
}
