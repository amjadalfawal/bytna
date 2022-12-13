# -*- coding: utf-8 -*-
{
    'name': "tecnote Internal Transfer Customization ",
    'summary': """tecnote Internal Transfer Customization
       """,
    'description': """ addOn hand in the source location ,On hand in a destination location,sold last 7 days from the destination location            
    """,
    'author': "Tecnote Technology",
    'website': "https://www.tecnote.ca/",
    'depends': ['stock','stock_barcode'],

    'data': [
        'views/stock_production_lot.xml',
        'views/stock_picking.xml',
        'report/product_label.xml'
        # 'report/delivery_report.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'tecnote_internal_transfer_customization/static/src/**/*.js',
    #     ],
    #     'web.assets_qweb': [
    #         'tecnote_internal_transfer_customization/static/src/**/*.xml',
    #     ],
    # }
}
