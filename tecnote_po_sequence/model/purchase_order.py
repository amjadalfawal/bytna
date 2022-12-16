# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in purchase order lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new purchase order lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for purchase in self:
            purchase.max_line_sequence = (
                max(purchase.mapped('order_line.sequence') or [0]) + 1)

    max_line_sequence = fields.Integer(
        string='Max sequence in lines',
        compute='_compute_max_line_sequence',
        store=True
    )

    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(PurchaseOrder, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(PurchaseOrder,
                     self.with_context(keep_line_sequence=True)).copy(default)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # re-defines the field to change the default
    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying the purchase order.",
        default=9999,
        string="Sequence"
    )

    # displays sequence on the order line
    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the purchase order.",
        related='sequence',
        string="No.",
        readonly=True,
        store=True
    )

    @api.model
    def create(self, values):
        line = super(PurchaseOrderLine, self).create(values)
        # We do not reset the sequence if we are copying a complete purchase order
        if self.env.context.get('keep_line_sequence'):
            line.order_id._reset_sequence()
        return line
