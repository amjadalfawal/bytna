# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import fields, models


class ProductLabelLayout(models.TransientModel):
    _inherit = 'product.label.layout'


    def _prepare_report_data(self):
        xml_id, data = super()._prepare_report_data()

        if 'zpl' in self.print_format:
            xml_id = 'stock.label_product_product'

        if self.picking_quantity == 'picking' and self.move_line_ids.ids != False:
            qties = defaultdict(int)
            custom_barcodes = defaultdict(list)
            custom_expiretions = defaultdict(list)

            uom_unit = self.env.ref('uom.product_uom_categ_unit', raise_if_not_found=False)
            for line in self.move_line_ids:
                qty = line.print_qty
                if qty == False or qty <=0:
                    qty = line.product_uom_qty if line.product_uom_qty >= line.qty_done else line.qty_done 
                if line.product_uom_id.category_id == uom_unit:
                    if (line.lot_id or line.lot_name) and int(qty):
                        custom_barcodes[line.product_id.id].append((line.barcode, int(qty)))
                        custom_expiretions[line.barcode].append(line.lot_id.expiration_date)
                        continue
                    qties[line.product_id.id] += qty
            # Pass only products with some quantity done to the report
            data['quantity_by_product'] = {p: int(q) for p, q in qties.items() if q}
            data['custom_barcodes'] = custom_barcodes
            data['custom_expiretions'] = custom_expiretions

        return xml_id, data

# product.report_simple_label_dymo
