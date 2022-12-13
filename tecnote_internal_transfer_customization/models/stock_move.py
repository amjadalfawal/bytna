from odoo import api, fields, models
from datetime import datetime, timedelta
import math


class StockMove(models.Model):
    _inherit = 'stock.move'

    onhand_qty_source_loc = fields.Float(string='On Hand Qty(Source)', compute='_calc_onhand_qty_source')
    onhand_qty_dest_loc = fields.Float(string='On Hand Qty(Destination)', compute='_calc_onhand_qty_dest')
    last_sold_seven_days = fields.Float(string='Sold Last 7 Days', compute='_calc_sold_last_seven_days')

    @api.depends('product_id')
    def _calc_sold_last_seven_days(self):
        for record in self:
            record.last_sold_seven_days = 0.0
            if record.product_id:
                last_seven_days = datetime.today() - timedelta(days=7)
                stock_moves = self.env['stock.move'].sudo().search(
                    [('company_id', '=', self.env.company.id), ('product_id', '=', record.product_id.id),
                     ('state', '=', 'done'),
                     ('picking_code', '=', 'outgoing'), ('date', '>=', last_seven_days)])
                record.last_sold_seven_days = sum(stock_move.quantity_done for stock_move in stock_moves)



    @api.depends('product_id', 'picking_code', 'location_id')
    def _calc_onhand_qty_source(self):
        for move in self:
            move.onhand_qty_source_loc = 0.0
            if move.picking_code == 'internal' and move.product_id and move.location_id:
                quants = self.env['stock.quant']._gather(move.product_id, move.location_id, lot_id=False,
                                                         package_id=False,
                                                         owner_id=False, strict=True)
                move.onhand_qty_source_loc = sum([quant.quantity for quant in quants])
                

    @api.depends('product_id', 'picking_code', 'location_dest_id')
    def _calc_onhand_qty_dest(self):
        for move in self:
            move.onhand_qty_dest_loc = 0.0
            if move.picking_code == 'internal' and move.product_id and move.location_dest_id:
                quants = self.env['stock.quant']._gather(move.product_id, move.location_dest_id, lot_id=False,
                                                         package_id=False,
                                                         owner_id=False, strict=True)
                move.onhand_qty_dest_loc = sum([quant.quantity for quant in quants])




    

