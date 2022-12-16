# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            line = self.purchase_line_id
            order = line.order_id
            if order.company_id.apply_purchase_discount_on_product_costing:
                price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if line.taxes_id:
                    price_unit = \
                    line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id,
                                                                        quantity=1.0)['total_void']
                if line.product_uom.id != line.product_id.uom_id.id:
                    price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
                if order.currency_id != order.company_id.currency_id:
                    # The date must be today, and not the date of the move since the move move is still
                    # in assigned state. However, the move date is the scheduled date until move is
                    # done, then date of actual move processing. See:
                    # https://github.com/odoo/odoo/blob/2f789b6863407e63f90b3a2d4cc3be09815f7002/addons/stock/models/stock_move.py#L36
                    price_unit = order.currency_id._convert(
                        price_unit, order.company_id.currency_id, order.company_id, fields.Date.context_today(self),
                        round=False)
                return price_unit
        return super(StockMove, self)._get_price_unit()