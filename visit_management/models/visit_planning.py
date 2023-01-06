from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class VisitsPlanning(models.Model):
  _name = 'visits.planning'
  _inherit = ['mail.thread']

  name = fields.Char('Serial Number', required=True, index=True, default='New', copy=False)
  start_date = fields.Date('Start Date', required=True)
  end_date = fields.Date('End Date', required=True)
  schedule_by = fields.Selection([('custom',"Customer By Sales Mane"),('all', 'All Customers'), ('sales_person', 'By SalesPerson')],string='Mode',required=True,default='all')
  salesperson_id = fields.Many2one('res.users', string='SalesPerson', track_visibility='onchange')
  # customer_ids = fields.One2many('res.partner', 'plan_id', string='field_name')
  state = fields.Selection([
      ('draft', 'Draft'),
      ('confirmed', 'Confirmed'),
      ('generated', 'Generated'),
      ('canceled', 'Canceled'),
  ],
  string='Status',
  readonly=True,
  copy=False,
  index=True,
  track_visibility='onchange',
  default='draft')
  visits_ids = fields.One2many('visits.visit', 'visit_schedule_id', string='Visits')

  @api.model
  def create(self, vals):
    if vals.get('name', 'New') == 'New':
      vals['name'] = self.env['ir.sequence'].next_by_code('visits.schedule') or '/'
    return super(VisitsPlanning, self).create(vals)

  def action_view_visits(self):
    for rec in self:
      visits = self.mapped('visits_ids')
      return {
          'name': ('Visits'),
          'view_type': 'form',
          'view_mode': 'tree,form',
          'res_model': 'visits.visit',
          'type': 'ir.actions.act_window',
          'target': 'current',
          'context': {
              'default_visit_schedule_id': rec.id
          },
          'domain': [('id', 'in', visits.ids)],
      }

  def action_confirmed(self):
    for rec in self:
      return rec.write({'state': 'confirmed'})


  def actionGenerate(self):
      visit_records = self.env['visits.visit']
      for rec in self:
          domain = []
          if rec.schedule_by == 'sales_person':
              domain = [('user_id', '=', rec.salesperson_id.id)]

          search_customers = self.env['res.partner'].search(domain)
          for customer in search_customers:
              common_day_ids = list(set(customer.allowed_days.mapped('name')))
              if common_day_ids:
                  date_temp_list = self.getDateList(self.start_date, self.end_date, common_day_ids)
                  for date in date_temp_list:
                      day = date and date.strftime('%A') or ''
                      visit_records += self.env['visits.visit'].create({
                          'partner_id': customer.id,
                          'visiting_day': day,
                          'salesperson_id': customer.user_id.id,
                          'visiting_date': date,
                          'state': 'confirmed',
                          'visit_schedule_id': rec.id
                      })
      return rec.write({'state': 'generated'})


  def getDateList(self, start_date, end_date, common_days):
    date_lst = []
    current_date = start_date
    while current_date <= end_date:
        day = current_date.strftime('%A')
        if not common_days or day in common_days:
            date_lst.append(current_date)
        current_date += relativedelta(days=1)
    return date_lst


  def action_canceled(self):
    for rec in self:
      rec.visits_ids.state = 'canceled'
      rec.write({'state': 'canceled'})
