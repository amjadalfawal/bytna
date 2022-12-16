# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    total_discount = fields.Monetary(string='Discount', compute='calc_total_discount')
    total_before_discount = fields.Monetary(string='Amount Before Discount', compute='calc_total_discount')

    @api.depends('invoice_line_ids')
    def calc_total_discount(self):
        for rec in self:
            total_discount = 0.0
            total_before_discount = 0.0
            for line in rec.invoice_line_ids:
                total_discount += (line.quantity * line.price_unit * line.discount / 100)
                total_before_discount += (line.quantity * line.price_unit)
            rec.total_discount = total_discount
            rec.total_before_discount = total_before_discount

    def button_draft(self):
        res = super(AccountMoveInherit, self).button_draft()
        for invoice in self:
            if invoice.is_invoice(include_receipts=True):
                discount_entry_lines = invoice.line_ids.filtered(lambda x: x.disc_related_invoice_line_id)
                discount_entry_lines.with_context(check_move_validity=False).unlink()
        return res

    def _post(self, soft=True):
        for invoice in self:
            if invoice.is_invoice(
                    include_receipts=True) and not invoice.company_id.apply_purchase_discount_on_product_costing:
                discount_entry_lines = invoice.line_ids.filtered(lambda x: x.disc_related_invoice_line_id)
                discount_entry_lines.with_context(check_move_validity=False).unlink()
                for line in invoice.line_ids.filtered(lambda x: not x.exclude_from_invoice_tab):
                    discount_amount = line.quantity * line.price_unit * line.discount / 100.0
                    if float_compare(discount_amount, 0.0, 5) > 0:
                        company = invoice.company_id
                        currency = line.currency_id
                        date = invoice.date

                        if invoice.move_type in ('out_invoice', 'in_refund', 'out_receipt'):
                            type = 'out'
                            if not line.product_id:
                                raise ValidationError(_("No product defined in the invoice line, can't get the discount"
                                                        " expense account."))
                            if line.product_id and not line.product_id.categ_id.discount_expense_account_id:
                                raise ValidationError(
                                    _('No discount expense account defined in the product category [%s].') % (
                                        line.product_id.categ_id.name))
                            account_id = line.product_id.categ_id.discount_expense_account_id.id
                        else:
                            type = 'in'
                            if not line.product_id:
                                raise ValidationError(_("No product defined in the invoice line, can't get the discount"
                                                        " income account."))
                            if line.product_id and not line.product_id.categ_id.discount_expense_account_id:
                                raise ValidationError(
                                    _('No discount income account defined in the product category [%s].') % (
                                        line.product_id.categ_id.name))
                            account_id = line.product_id.categ_id.discount_income_account_id.id

                        if currency and currency != company.currency_id:
                            # Multi-currencies.
                            discount_amount_conv = currency._convert(discount_amount, company.currency_id, company,
                                                                     date)
                            amount_currency = discount_amount
                            debit = discount_amount < 0.0 and abs(discount_amount_conv) or 0.0
                            credit = discount_amount > 0.0 and abs(discount_amount_conv) or 0.0
                        else:
                            # Single-currency.
                            amount_currency = 0.0
                            debit = discount_amount < 0.0 and abs(discount_amount) or 0.0
                            credit = discount_amount > 0.0 and abs(discount_amount) or 0.0

                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': line.name,
                            'debit': debit if type == 'out' else credit,
                            'credit': credit if type == 'out' else debit,
                            'quantity': 1.0,
                            'amount_currency': (
                                        discount_amount > 0.0 and - amount_currency or amount_currency) if type == 'out' else (
                                        discount_amount > 0.0 and amount_currency or -amount_currency),
                            'date_maturity': False,
                            'move_id': invoice.id,
                            'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                            'account_id': line.account_id.id,
                            'partner_id': invoice.commercial_partner_id.id,
                            'exclude_from_invoice_tab': True,
                            'disc_related_invoice_line_id': line.id,
                        })
                        self.env['account.move.line'].with_context(check_move_validity=False).create({
                            'name': 'Discount',
                            'debit': credit if type == 'out' else debit,
                            'credit': debit if type == 'out' else credit,
                            'quantity': 1.0,
                            'amount_currency': (
                                        discount_amount > 0.0 and amount_currency or -amount_currency) if type == 'out' else (
                                        discount_amount > 0.0 and -amount_currency or amount_currency),
                            'date_maturity': False,
                            'move_id': invoice.id,
                            'currency_id': invoice.currency_id.id if invoice.currency_id != invoice.company_id.currency_id else False,
                            'account_id': account_id,
                            'partner_id': invoice.commercial_partner_id.id,
                            'exclude_from_invoice_tab': True,
                            'disc_related_invoice_line_id': line.id,
                        })
        return super(AccountMoveInherit, self)._post(soft)


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    disc_related_invoice_line_id = fields.Many2one('account.move.line', string='Disc. Related Invoice Line',
                                                   ondelete='cascade')
