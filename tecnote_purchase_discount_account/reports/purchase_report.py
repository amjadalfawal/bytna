# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    discount = fields.Float('Discount %', readonly=True)
    barcode = fields.Char(string="Barcode", readonly=True, group_operator="max")
    sub_total_before_discount = fields.Monetary(string='Subtotal Before Disc.', readonly=True)
    total_discount = fields.Monetary( readonly=True)
    price_tax = fields.Float(string='Tax', readonly=True)
    list_price = fields.Float(string='Sale Price', readonly=True, group_operator="avg")
    external_id = fields.Char(string='Product External ID', readonly=True, group_operator="max")
    price_average_after_disc = fields.Float('Average Cost After Discount', readonly=True, group_operator="avg")
    analytic_tag_id = fields.Many2one(comodel_name="account.analytic.tag", string="Analytic Tags",  readonly=True )

    def _select(self):
        return super(PurchaseReport, self)._select() + """
        ,sum(l.sub_total_before_discount / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as sub_total_before_discount,
        SUM((l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0)) * l.discount / 100) AS total_discount,

        l.discount, p.barcode, aat.account_analytic_tag_id as analytic_tag_id, l.price_tax,
        sum(t.list_price)::decimal(16,2) as list_price, p.external_id,
        (sum((l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0)) - ((l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0)) * l.discount / 100))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2) as price_average_after_disc
        """


    def _from(self):
        from_str = super(PurchaseReport, self)._from()

        return from_str + """left join account_analytic_tag_purchase_order_line_rel aat on (aat.purchase_order_line_id = l.id)

                                     """

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", l.discount, p.barcode, aat.account_analytic_tag_id, l.price_tax, p.external_id"
