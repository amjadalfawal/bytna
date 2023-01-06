import logging
from odoo import models, api, fields,exceptions, _
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):

    _inherit = 'res.partner'
   
   
    api_image_url = fields.Char("image url" , size=300  ,compute='_compute_image_url')
    qr_code = fields.Char('Qr Code')
    @api.depends('name')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('base.url')
        for obj in self:
            obj.api_image_url = str(base_url) + '/web/image?' + 'model=res.partner&id=' + str(obj.id) + '&field=image_512'



