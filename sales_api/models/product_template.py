import logging
from odoo import models, api, fields,exceptions, _


class ProductPTemplate(models.Model):

    _inherit = 'product.template'

    api_image_url = fields.Char("image url" , size=300  ,compute='_compute_image_url')
    short_desc = fields.Char("Short Description",translate=True)
    is_deactivate = fields.Boolean('is deactivate' ,company_dependent=True)
    min_limit = fields.Integer(string="min",company_dependent=True,check_company=True,default=1)
    max_limit = fields.Integer(string="max",company_dependent=True,check_company=True,default=5)
    product_template_image_ids = fields.One2many('product.image', 'product_tmpl_id', string="Extra Product Media", copy=True)
    uom_allowed_ids = fields.Many2many('uom.uom', string='Allowed Unit of Measure App')
    category_id = fields.Many2one(related='uom_id.category_id', string='Category')
    product_brand_ept_id = fields.Many2one(
        'product.brand.ept',
        string='Brand',
        help='Select a brand for this product'
    )
    @api.depends('name')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('base.url')
        for obj in self:
            obj.api_image_url = str(base_url) + '/web/image?' + 'model=product.template&id=' + str(obj.id) + '&field=image_512'


class ProductProduct(models.Model):

    _inherit = 'product.product'

    api_image_url = fields.Char("image url" , size=300  ,compute='_compute_image_url')


    @api.depends('name')
    def _compute_image_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('base.url')
        for obj in self:
            obj.api_image_url = str(base_url) + '/web/image?' + 'model=product.product&id=' + str(obj.id) + '&field=image_512'
