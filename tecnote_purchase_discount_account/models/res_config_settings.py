# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    apply_purchase_discount_on_product_costing = fields.Boolean(related='company_id.apply_purchase_discount_on_product_costing',
                                                         string='Apply Purchase Discount On Product Costing', readonly=False)