# -*- coding: utf-8 -*-
from email.policy import default
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

# class ProjectTask(models.Model):
#     _inherit="project.task"
#     order_id = fields.Many2one("sale.order",string="Related Sales Order")

class PickingTags(models.Model):
    _name = "piciking.tags"
    name = fields.Char(string="name")
    color = fields.Integer()


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    package_status = fields.Selection(selection=[("prepare", "To Prepare"), ("ready", "To Ship"),('shiped','Shiped')],default="prepare",string="Pacakge Status")
    shiped_date = fields.Datetime('Shiped Date', required=False, readonly=False, select=True, default=False)
    tag_ids = fields.Many2many('piciking.tags')
    is_printed = fields.Boolean('printed',default=False)
    @api.onchange('package_status')
    def _onchange_package_status(self):
        for line in self:
            if line.package_status == "shiped":
                line.shiped_date = fields.datetime.now()

        return True

    
    def mark_as_printed(self):
        self.is_printed = True




class SaleOrder(models.Model):
    _inherit = 'sale.order'
    total_discount_amount = fields.Monetary(string='Discount', tracking=True,compute='_compute_total_discount_amount')
    total_amount_before_discount = fields.Monetary(string='Amount Before Discount', tracking=True,compute='_compute_total_amount_before_discount')

    @api.depends('order_line.product_uom_qty', 'order_line.price_unit', 'order_line.discount')
    def _compute_total_discount_amount(self):
        for order in self:
            total_lines_discount = sum(
                (line.product_uom_qty * line.price_unit * line.discount) for line in order.order_line)
            order.total_discount_amount = total_lines_discount / 100

    @api.depends('order_line.product_uom_qty', 'order_line.price_unit', 'order_line.discount')
    def _compute_total_amount_before_discount(self):
        for order in self:
            order.total_amount_before_discount = sum(
                line.product_uom_qty * line.price_unit for line in order.order_line)
            _logger.info(order.tax_totals_json)






class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sub_total_before_discount = fields.Monetary(string='Subtotal Before Discount',
                                                compute='_compute_sub_total_before_discount', store=True)
    discount_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     default='percentage')
    discount_amount = fields.Monetary(string='Discount Amount')

    @api.onchange('discount_type')
    def _onchange_discount_type(self):
        for line in self:
            line.discount_amount = 0
            line.discount = 0

    @api.onchange('discount_amount', 'discount')
    def _onchange_discount_amount(self):
        for line in self:
            if line.discount_type == 'percentage' and line.discount:
                line.discount_amount = (
                    line.product_qty * line.price_unit * line.discount) / 100

            elif line.discount_type == 'amount' and line.discount_amount:
                line.discount = (line.discount_amount * 100) / \
                    (line.product_qty * line.price_unit)

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_sub_total_before_discount(self):
        for line in self:
            line.sub_total_before_discount = line.product_uom_qty * line.price_unit
