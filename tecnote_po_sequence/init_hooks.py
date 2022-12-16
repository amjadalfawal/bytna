
from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    """
    Fetches all the purchase order and resets the sequence of the order lines
    """
    env = Environment(cr, SUPERUSER_ID, {})
    purchase = env['purchase.order'].search([])
    purchase._reset_sequence()
