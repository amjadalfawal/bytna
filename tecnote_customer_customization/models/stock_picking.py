from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    route_id = fields.Char( related='partner_id.res_route_id.name',store=True)
