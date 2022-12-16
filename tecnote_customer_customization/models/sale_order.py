from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    route_id = fields.Char( related='partner_id.res_route_id.name',store=True)

