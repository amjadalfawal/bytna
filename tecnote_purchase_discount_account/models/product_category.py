# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = "product.category"

    discount_income_account_id = fields.Many2one('account.account', company_dependent=True,
        string="Discount Income Account",
        domain="[('deprecated', '=', False), ('company_id', '=', current_company_id), ('internal_group', '=', 'income')]",
        help="This account will be used when validating a customer invoice with discount.")
    discount_expense_account_id = fields.Many2one('account.account', company_dependent=True,
        string="Discount Expense Account",
        domain="[('deprecated', '=', False), ('company_id', '=', current_company_id), ('internal_group', '=', 'expense')]",
        help="This account will be used when validating a vendor bill with discount.")
