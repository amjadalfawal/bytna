from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class PartnerLedgerController(http.Controller):

  @http.route('/api/visits', methods=['POST'], type="json", auth="public", website=True, csrf=False)
  def get_partner_ledger(self, **kw):
    request_body = request.jsonrequest
    if not request.httprequest.headers.get('authorization'):
      return {
          "status": 403,
          "message": "Authentication Errors : Set Authorization Code in Header",
          "data": False
      }
    if request.httprequest.headers[
        'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
      return {"status": 403, "message": "Authentication Errors : not authenticate", "data": False}
    result = self.get_visits_json(request_body['user_id'])
    return result

  def get_visits_json(self, user_id):
    visits = request.env['visits.visit'].sudo().search([('salesperson_id', '=', user_id),
                                                        ('visiting_date', '=', datetime.now()),
                                                        ('state', '=', 'confirmed')])
    visits_lst = []
    for visit in visits:
      visits_lst.append({
          'user_id': visit.salesperson_id.id,
          'visit_id': visit.id,
          'partner_id': visit.partner_id.id,
          'code': visit.name,
          'plannign': visit.visit_schedule_id.name
      })

    return visits_lst