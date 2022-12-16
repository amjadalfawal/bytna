# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, AccessError
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_discount = fields.Monetary(string='Discount', compute='calc_total_discount')
    total_before_discount = fields.Monetary(string='Amount Before Discount', compute='calc_total_discount')
    default_discount = fields.Float(string='Default Discount %')

    @api.onchange('partner_id')
    def onchange_vendor(self):
        self.default_discount = self.partner_id.default_discount

    @api.onchange('default_discount')
    def onchange_default_discount(self):
        self.order_line.discount = self.default_discount

    @api.depends('order_line', 'order_line.price_total')
    def calc_total_discount(self):
        for rec in self:
            total_discount = 0.0
            total_before_discount = 0.0
            for line in rec.order_line:
                total_discount += (line.product_qty * line.price_unit * line.discount / 100)
                total_before_discount += (line.product_qty * line.price_unit)
            rec.total_discount = total_discount
            rec.total_before_discount = total_before_discount


    def _add_supplier_to_product(self):
        """
        Override to add only vendors not company.
        Also update price  and discount of vendor for each new purchase order
        """
        if not self.partner_id.ref_company_ids:

            for line in self.order_line:
                # Do not add a contact as a supplier
                partner = self.partner_id if not self.partner_id.parent_id else self.partner_id.parent_id
                if line.product_id and partner not in line.product_id.seller_ids.filtered(lambda s: s.company_id == self.company_id).mapped('name') and len(line.product_id.seller_ids) <= 10:
                    # Convert the price in the right currency.
                    currency = partner.property_purchase_currency_id or self.env.company.currency_id
                    price = self.currency_id._convert(line.price_unit, currency, line.company_id, line.date_order or fields.Date.today(), round=False)
                    # Compute the price for the template's UoM, because the supplier's UoM is related to that UoM.
                    if line.product_id.product_tmpl_id.uom_po_id != line.product_uom:
                        default_uom = line.product_id.product_tmpl_id.uom_po_id
                        price = line.product_uom._compute_price(price, default_uom)

                    supplierinfo = {
                        'name': partner.id,
                        'sequence': max(line.product_id.seller_ids.mapped('sequence')) + 1 if line.product_id.seller_ids else 1,
                        'min_qty': 0.0,
                        'price': price,
                        'discount': line.discount,
                        'currency_id': currency.id,
                        'delay': 0,
                    }
                    # In case the order partner is a contact address, a new supplierinfo is created on
                    # the parent company. In this case, we keep the product name and code.
                    seller = line.product_id.with_context(force_company=line.company_id.id)._select_seller(
                        partner_id=line.partner_id,
                        quantity=line.product_qty,
                        date=line.order_id.date_order and line.order_id.date_order.date(),
                        uom_id=line.product_uom)
                    if seller:
                        supplierinfo['product_name'] = seller.product_name
                        supplierinfo['product_code'] = seller.product_code
                    vals = {
                        'seller_ids': [(0, 0, supplierinfo)],
                    }
                    try:
                        line.product_id.write(vals)
                    except AccessError:  # no write access rights -> just ignore
                        break
                else:
                    seller = line.product_id.with_context(force_company=line.company_id.id)._select_seller(
                        partner_id=line.partner_id,
                        quantity=line.product_qty,
                        date=line.order_id.date_order and line.order_id.date_order.date(),
                        uom_id=line.product_uom)

                    seller_price = seller.currency_id._convert(seller.price, self.currency_id, line.company_id,
                                                      line.date_order or fields.Date.today(), round=False)
                    vals = {}
                    if seller_price != line.price_unit:
                        price = self.currency_id._convert(line.price_unit, seller.currency_id, line.company_id,
                                                          line.date_order or fields.Date.today(), round=False)

                        vals['price'] = price

                    if seller.discount != line.discount and line.discount < 100 :
                        vals['discount'] = line.discount

                    seller.write(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float('Discount %', digits=dp.get_precision('Discount'), default=0.0)
    sub_total_before_discount = fields.Monetary(string='Subtotal Before Disc.', help='Show Subtotal before discount',
                                                compute='_compute_amount_before_discount', store=True)


    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount_before_discount(self):
        for line in self:
            line.sub_total_before_discount = line.product_qty * line.price_unit

    def _prepare_compute_all_values(self):
        self.ensure_one()
        vals = super(PurchaseOrderLine, self)._prepare_compute_all_values()
        price = vals['price_unit'] * (1 - (self.discount or 0.0) / 100.0)
        vals['price_unit'] = price
        return vals

    def _prepare_account_move_line(self, move=False):
        self.ensure_one()
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({
            'discount': self.discount,
        })
        return res

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        return super(PurchaseOrderLine, self)._compute_amount()

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        res = super()._onchange_quantity()
        if self.product_id:
            seller = self.product_id.with_context(force_company=self.order_id.company_id.id)._select_seller(
                partner_id=self.partner_id,
                quantity=self.product_qty,
                date=self.order_id.date_order.date() ,
                uom_id=self.product_uom,
            )
            self.discount = seller.discount
        return res

    @api.model
    def create(self, vals):
        res = super(PurchaseOrderLine, self).create(vals)
        if not vals.get('discount', False):
            res.discount = res.order_id.default_discount
        return res

    def _get_stock_move_price_unit(self):
        self.ensure_one()
        line = self[0]
        if line.order_id.company_id.apply_purchase_discount_on_product_costing:
            order = line.order_id
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.taxes_id:
                price_unit = line.taxes_id.with_context(round=False).compute_all(
                    price_unit, currency=line.order_id.currency_id, quantity=1.0, product=line.product_id,
                    partner=line.order_id.partner_id
                )['total_void']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                price_unit = order.currency_id._convert(
                    price_unit, order.company_id.currency_id, self.company_id, self.date_order or fields.Date.today(),
                    round=False)
            return price_unit
        else:
            return super(PurchaseOrderLine, self)._get_stock_move_price_unit()
