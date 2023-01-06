from tokenize import String
from odoo import models, fields


class ResDays(models.Model):
  _name = 'res.days'
  name = fields.Char(String="name")
  day = fields.Integer(String="ID")