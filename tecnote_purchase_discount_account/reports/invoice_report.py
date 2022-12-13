# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    discount = fields.Float('Discount %', readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """
        , line.discount
        """
