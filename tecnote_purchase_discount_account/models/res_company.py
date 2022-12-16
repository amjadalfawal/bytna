# -*- coding: utf-8 -*-

from odoo import fields, models


class CompanyInherit(models.Model):
    _inherit = 'res.company'

    apply_purchase_discount_on_product_costing = fields.Boolean(string='Apply Purchase Discount On Product Costing')