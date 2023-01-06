from odoo import models, fields


class Partner(models.Model):
  _inherit = 'res.partner'

  allowed_days = fields.Many2many('res.days', string='Allowed Days')
