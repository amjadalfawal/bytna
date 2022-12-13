from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    available_qty = fields.Float(string="Available Qty", compute='compute_available_qty')

    @api.depends('product_id')
    def compute_available_qty(self):
        for line in self:
            if line.product_id:
                line.available_qty = line.product_id.qty_available
            else:
                line.available_qty = 0
