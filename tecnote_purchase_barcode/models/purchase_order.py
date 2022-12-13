from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    barcode = fields.Char(string="Barcode", readonly=True, related='product_id.barcode', store=1)
