from odoo import api, fields, models


class ResRoute(models.Model):
    _name = 'res.route'
    _rec_name = 'code'

    name = fields.Char('Route Name')
    desceription = fields.Char('Route Descreption')
    code = fields.Char('Short Code')
