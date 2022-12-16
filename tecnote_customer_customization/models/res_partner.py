from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    #   Common Fileds 
    res_route_id = fields.Many2one('res.route', string='Customer Route')

