# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    total_discount_amount = fields.Monetary(string='Discount', compute='_compute_total_discount_amount')

    total_amount_before_discount = fields.Monetary(string='Amount Before Discount', compute='_compute_total_amount_before_discount')

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit', 'invoice_line_ids.discount')
    def _compute_total_discount_amount(self):
        for move in self:
            total_lines_discount = sum(
                (line.quantity * line.price_unit * line.discount) for line in move.invoice_line_ids)
            move.total_discount_amount = total_lines_discount / 100

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.price_unit', 'invoice_line_ids.discount')
    def _compute_total_amount_before_discount(self):
        for move in self:
            move.total_amount_before_discount = sum(
                line.quantity * line.price_unit for line in move.invoice_line_ids)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sub_total_before_discount = fields.Monetary(string='Subtotal Before Discount',
                                                compute='_compute_sub_total_before_discount', store=True)

    @api.depends('quantity', 'price_unit', 'tax_ids', 'discount')
    def _compute_sub_total_before_discount(self):
        for line in self:
            line.sub_total_before_discount = line.quantity * line.price_unit
