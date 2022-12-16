from odoo import api, fields, models
from datetime import datetime, timedelta
import logging 
_logger = logging.getLogger(__name__)
import string
import random
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    barcode = fields.Char(string="Barcode",compute='compute_barcode',store=True)
    print_qty = fields.Integer(string="Print Qty")
    


    @api.onchange('product_id')
    def _onchange_product_id_barcode(self):
        for rec in self:
            if rec.product_id and rec.product_id.barcode:
                rec.barcode = rec.product_id.barcode
            else:
                rec.barcode = False


    def random_string(self,length):
        return ''.join(random.choice(string.digits) for m in range(length))

    @api.onchange('expiration_date')
    def onchange_expiry_date(self):
        for line in self:
            _logger.info('=======out if==========')
            _logger.info(self)
            _logger.info(line.expiration_date)
            _logger.info(line.lot_id)
            _logger.info(line.lot_id.expiration_date)
            if line.expiration_date:
                _logger.info('=============inside if ===========')
                if line.lot_id.id == False :
                    random = self.random_string(4)
                    lot_id = self.env['stock.production.lot'].sudo().create({
                        'product_id' : line.product_id.id,
                        'name' : random+self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                        'expiration_date': line.expiration_date,
                        'use_date':line.expiration_date,
                        'removal_date':line.expiration_date,
                        'alert_date':line.expiration_date,
                    })
                    line.lot_id = lot_id
                    line.lot_name = line.lot_id.name
                    if line.product_id.barcode != False: 
                        line.barcode = "01"+line.product_id.barcode+"10"+line.lot_id.name

                elif line.expiration_date  and str(line.expiration_date) != str(line.lot_id.expiration_date) :
                    line.lot_id.expiration_date = line.expiration_date
                    line.lot_id.use_date = line.expiration_date
                    line.lot_id.removal_date = line.expiration_date
                    line.lot_id.alert_date = line.expiration_date
                    if line.product_id.barcode != False and line.barcode == False: 
                        line.barcode = "01"+line.product_id.barcode+"10"+line.lot_id.name
                else:
                    return

    

    @api.depends('lot_id','expiration_date')
    def compute_barcode(self):
        for rec in self:
            if rec.product_id.barcode != False and rec.lot_id.name != False:
                rec.barcode = "01"+rec.product_id.barcode+"10"+rec.lot_id.name



