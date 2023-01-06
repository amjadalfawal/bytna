# Import the necessary models and fields
from odoo import api, fields, models

# Define the model
class SalesTarget(models.Model):
    _name = 'sales.target'
    _description = 'Sales Target'
    _inherit = ['mail.thread']

    # Define the fields of the model
    name = fields.Char(string='Name', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    target_amount = fields.Monetary(string='Target Amount', currency_field='currency_id')
    achieved_amount = fields.Monetary(string='Achieved Amount', currency_field='currency_id', compute='_compute_achieved_amount')
    target_quantity = fields.Float(string='Target Quantity')
    achieved_quantity = fields.Float(string='Achieved Quantity', compute='_compute_achieved_quantity')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    user_id = fields.Many2one('res.users', string='Salesperson', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company.id)
    target_type = fields.Selection([
        ('none', 'None'),
        ('category', 'Category'),
        ('customer', 'Customer')
    ], string='Target Type', required=True, default='none')
    calculation_type = fields.Selection([
        ('order', 'Sales Order'),
        ('invoice', 'Invoice')
    ], string='Calculation Type', required=True, default='order')

    category_id = fields.Many2one('product.category', string='Category')
    partner_id = fields.Many2one('res.partner', string='Customer')

    # Define a function to compute the achieved amount
    @api.depends('user_id', 'start_date', 'end_date', 'target_type', 'category_id', 'partner_id', 'calculation_type')
    def _compute_achieved_amount(self):
        for target in self:
            if target.calculation_type == 'order':
                domain = [
                    ('user_id', '=', target.user_id.id),
                    ('date_order', '>=', target.start_date),
                    ('date_order', '<=', target.end_date),
                    ('state', 'in', ['sale', 'done'])
                ]
                if target.target_type == 'category':
                    domain += [('order_line.product_id.categ_id', '=', target.category_id.id)]
                elif target.target_type == 'customer':
                    domain += [('partner_id', '=', target.partner_id.id)]
                orders = self.env['sale.order'].search(domain)
                target.achieved_amount = sum(order.amount_total for order in orders)
            elif target.calculation_type == 'invoice':
                domain = [
                    ('user_id', '=', target.user_id.id),
                    ('invoice_date', '>=', target.start_date),
                    ('invoice_date', '<=', target.end_date),
                    ('state', 'in', ['posted'])
                ]
                if target.target_type == 'category':
                    domain += [('invoice_line_ids.product_id.categ_id', '=', target.category_id.id)]
                elif target.target_type == 'customer':
                    domain += [('partner_id', '=', target.partner_id.id)]
                invoices = self.env['account.move'].search(domain)
                target.achieved_amount = sum(invoice.amount_total for invoice in invoices)
    # Define a function to compute the achieved quantity
    @api.depends('user_id', 'start_date', 'end_date', 'target_type', 'category_id', 'partner_id', 'calculation_type')
    def _compute_achieved_quantity(self):
        for target in self:
            if target.calculation_type == 'order':
                domain = [
                    ('user_id', '=', target.user_id.id),
                    ('date_order', '>=', target.start_date),
                    ('date_order', '<=', target.end_date),
                    ('state', 'in', ['sale', 'done'])
                ]
                if target.target_type == 'category':
                    domain += [('order_line.product_id.categ_id', '=', target.category_id.id)]
                elif target.target_type == 'customer':
                    domain += [('partner_id', '=', target.partner_id.id)]
                orders = self.env['sale.order'].search(domain)
                
                achieved_quantity = 0
                for order in orders:
                    for order_line in order.order_line:
                        quantity = order_line.product_uom._compute_quantity(order_line.product_uom_qty, order_line.product_id.uom_id)
                        achieved_quantity += quantity

                # target.achieved_quantity = sum(order_line.product_uom_qty for order in orders for order_line in order.order_line)
                target.achieved_quantity = achieved_quantity

           
           
            elif target.calculation_type == 'invoice':
                domain = [
                    ('user_id', '=', target.user_id.id),
                    ('invoice_date', '>=', target.start_date),
                    ('invoice_date', '<=', target.end_date),
                    ('state', 'in', ['posted'])
                ]
                if target.target_type == 'category':
                    domain += [('invoice_line_ids.product_id.categ_id', '=', target.category_id.id)]
                elif target.target_type == 'customer':
                    domain += [('partner_id', '=', target.partner_id.id)]
                invoices = self.env['account.move'].search(domain)
                
                achieved_quantity = 0
                for invoice in invoices:
                    for invoice_line in invoice.invoice_line_ids:
                        quantity = invoice_line.product_uom._compute_quantity(invoice_line.quantity, invoice_line.product_id.uom_id)                
                        achieved_quantity += quantity

                # target.achieved_quantity = sum(invoice_line.quantity for invoice in invoices for invoice_line in invoice.invoice_line_ids)
                target.achieved_quantity = achieved_quantity
