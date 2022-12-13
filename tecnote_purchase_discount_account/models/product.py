# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Product(models.Model):
    _inherit = 'product.product'

    external_id = fields.Char('External ID', compute='_compute_xml_id', help="External ID", store=1)

    def _compute_xml_id(self):
        res = self.get_external_id()
        for rec in self:
            rec.external_id = res.get(rec.id)