# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class SelectProducts(models.TransientModel):
    _name = 'select.products'
    _description = 'Select Products'

    product_ids = fields.Many2many('product.product', string='Products')

    def select_products(self):
        order_id = self.env['purchase.order'].browse(self._context.get('active_id', False))
        for product in self.product_ids:
            created_purchase_order_line = self.env['purchase.order.line'].with_context(
                keep_line_sequence=True).create({
                'product_id': product.id,
                'name': product.name,
                'date_planned': order_id.date_planned or datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'product_uom': product.uom_id.id,
                'price_unit': product.lst_price,
                'product_qty': 1.0,
                'display_type': False,
                'order_id': order_id.id
            })
            created_purchase_order_line._onchange_quantity()
