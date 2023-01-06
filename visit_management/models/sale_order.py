from odoo import models, fields, api


class SaleOrder(models.Model):
  _inherit = 'sale.order'

  visit_id = fields.Many2one('visits.visit', string='Visit')
