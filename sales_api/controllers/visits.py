import functools
from odoo.http import JsonRequest
from odoo.http import request
from odoo import _
import datetime
from odoo import http
from odoo.http import request
import logging
from .utils import *
from .json_request_patch import *
import datetime

_logger = logging.getLogger(__name__)

class SalesManVisits(http.Controller):
    JsonRequest._json_response = JsonRequestPatch._json_response
    
    @validate_token
    @context_wrapper
    @http.route('/api/v1/visits', type="http", auth="public", csrf=False)
    def saleManVisits(self, lang, company_id, price_list, page, limit, **kw):
        response_headers = {"Content-Type": "application/json"}
        try: 
            term = kw.get('term',False)

            visits = request.env['visits.visit'].sudo().search([('salesperson_id', '=', request.uid),('visiting_date', '=', datetime.datetime.now()),('state', '=', 'confirmed')],limit=limit, offset=(page - 1) * limit)
            total_count = request.env['visits.visit'].with_user(1).search_count([('salesperson_id', '=', request.uid),('visiting_date', '=', datetime.datetime.now()),('state', '=', 'confirmed')])
            is_last_page = True if ((page - 1) * limit) + limit > total_count else False
            visits = extra_visits_fields(visits) 
            
            _logger.info('==============visits===========')
            _logger.info(visits)
            data = {
                'visits': visits ,
                'total_count': total_count,
                'current_page': page,
                'per_page': limit,
                'is_last_page': is_last_page
            }
            obj_json = json.loads(
                json.dumps(
                    data,
                    default=date_utils.json_default,
                    skipkeys=True
                )
            )

            return Response(
                json.dumps(
                    {
                        "status": 200,
                        "msg": "Fetch Visits successfully.",
                        "data": obj_json
                    }
                ).replace('false', 'null'),
                headers=response_headers,
                status=200
            )

            

        except Exception as e:
            return Response(
                json.dumps(
                    {
                        "status": 400,
                        "msg": str(e),
                        'data' : []
                    }
                ),
                headers=response_headers,
                status=400
            )



    @validate_token
    @http.route('/api/v1/visits/customer/<int:partner_id>', type="http", auth="public", csrf=False)
    def customerInfo(self ,partner_id, **kw):
        response_headers = {"Content-Type": "application/json"}
        try: 
            partner = request.env['res.partner'].sudo().search([('id', '=', partner_id)])
            obj = partner.read(['name','id','api_image_url','partner_latitude','partner_longitude','mobile','street','barcode','sale_order_count','total_due','total_overdue','credit','debit','debit_limit','total_invoiced','allowed_days','invoice_ids','unpaid_invoices','property_product_pricelist','currency_id','tz','lang','qr_code','category_id'],load='')
            if obj[0]['id'] != False:
                _logger.info(obj[0]['currency_id'])
                obj[0]['currency_id'] =  http.request.env['res.currency'].browse(obj[0]['currency_id']).read([],load='')
                obj[0]['category_id'] =  http.request.env['res.partner.category'].browse(obj[0]['category_id']).read([],load='')           

            obj_json = json.loads(
                json.dumps(
                    obj,
                    default=date_utils.json_default,
                    skipkeys=True          
                )
            )
            return Response(
                json.dumps(
                    {
                        "status": 200,
                        "msg": "Fetch Customer successfully.",
                        "data": obj_json
                    }
                ).replace('false', 'null'),
                headers=response_headers,
                status=200
            )
          

        except Exception as e:
            return Response(
                json.dumps(
                    {
                        "status": 400,
                        "msg": str(e),
                        'data' : []
                    }
                ),
                headers=response_headers,
                status=400
            )
