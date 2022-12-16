{
    'name': ' Tecnote Customer Routes',
    'summary': 'Tecnote Customer Routes',
    'depends': [
        'base',
        'sale_management',
        'contacts',
        'stock'

    ],
    'description': "Tecnote Customer Routes Model",
    'data': [
        'security/ir.model.access.csv',
        'views/res_route_view.xml',
        'views/res_partner_view.xml',
        'views/sale_view.xml',
        'views/picking_view.xml',
        'views/menuitems.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
