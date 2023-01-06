# -*- coding: utf-8 -*-
"""
    This model is used to create a product brand fields
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderLind(models.Model):
    _inherit = 'sale.order.line'

    # sale_aviliable_slots_ids = fields.Selection(string="Sales Type", default="direct_to_pharmacy",
    #                              selection=[('direct_to_pharmacy', 'Direct to Pharmacy'),
    #                                         ('through_drugstore', 'Through Drugstore'), ])
 
    api_image_url = fields.Char(string='image url: ', related="product_id.api_image_url")