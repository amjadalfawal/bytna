# -*- coding: utf-8 -*-
{
    'name': "tecnote Internal Transfer Customization ",
    'summary': """tecnote Internal Transfer Customization
       """,
    'description': """ addOn hand in the source location ,On hand in a destination location,sold last 7 days from the destination location            
    """,
    'author': "Tecnote Technology",
    'website': "https://www.tecnote.ca/",
    'depends': ['stock','product_expiry','stock_barcode'],

    'data': [
        'views/stock_production_lot.xml',
        'views/stock_picking.xml',
        'report/product_label.xml'
    ],
}
