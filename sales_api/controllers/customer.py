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

class SalesManCustomer(http.Controller):
    JsonRequest._json_response = JsonRequestPatch._json_response
    
    @validate_token
    @context_wrapper
    @http.route('/api/v1/customers', type="http", auth="public", csrf=False)
    def unActiveCustomers(self, lang, company_id, price_list, page, limit, **kw):
        response_headers = {"Content-Type": "application/json"}
        try: 
            term = kw.get('term',False)
            domain = [('customer_rank','=', 1),'|',('qr_code','=',False),'&',('partner_latitude','=',0.0),('partner_longitude','=',0.0)]
            partners = request.env['res.partner'].sudo().search(domain,limit=limit, offset=(page - 1) * limit)
            total_count = request.env['res.partner'].with_user(1).search_count(domain)
            _logger.info('==============customers===========')

            is_last_page = True if ((page - 1) * limit) + limit > total_count else False
            partners = partners.read(fields=['name','id','api_image_url','partner_latitude','partner_longitude','mobile','street','barcode','sale_order_count','total_due','total_overdue','credit','debit','debit_limit','total_invoiced','allowed_days','invoice_ids','unpaid_invoices','property_product_pricelist','currency_id','tz','lang','qr_code','category_id'],load='')            
            for obj in partners:
                if obj['id'] != False:
                    _logger.info(obj['currency_id'])
                    obj['currency_id'] =  http.request.env['res.currency'].browse(obj['currency_id']).read([],load='')      
                    obj['category_id'] =  http.request.env['res.partner.category'].browse(obj['category_id']).read([],load='')           
            _logger.info('==============customers===========')
            _logger.info(partners)
            data = {
                'partners': partners ,
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



    @validate_token
    @context_wrapper
    @http.route('/api/v1/customers/types', type="http", auth="public", csrf=False)
    def customerTypes(self, lang, company_id, price_list, page, limit, **kw):
        response_headers = {"Content-Type": "application/json"}
        try: 

            tags = request.env['res.partner.category'].sudo().search([('active','=',True)],limit=limit, offset=(page - 1) * limit)
            _logger.info('==============customers===========')
            tags = tags.read([],load='')                  
            _logger.info('==============customers===========')
            _logger.info(tags)
            data = {
                'types': tags,
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
                        "msg": "Fetch Tags Successfully.",
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



    @http.route('/api/v1/customers/create', cors="*", csrf=False, type='json', auth="public", methods=['OPTIONS', 'POST'])
    @validate_token  
    @context_wrapper
    def createCustomer(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Create sale order with provided payload
        :param kw: (lang, company-id, auth token)
        :return: status: 403, User Not Linked With Partner,
                 status: 400, missing parameter from the payload,
                 status: 400, carrier rejected the order,
                 status: 200, created successfully
        """
        try:
            # get request payload
            values = json.loads(request.httprequest.data)
            phone_number = values.get('phone_number', False)  # products
            address = values.get('address',False)
            partner_latitude = values.get('partner_latitude',False)
            partner_longitude = values.get('partner_longitude',False)
            qr_code = values.get('qr_code',False)
            tags = values.get('tags', False)  # note about the order
            name =  values.get('name', False) # partner that created the order
            # if not partner_id:  # User is not related to a partner
            #     return {'msg': _('Customer (%s) not found' % partner_id), 'status_code': 400}

            partner_data = {
                'name': name,
                'qr_code': qr_code,
                'partner_latitude':partner_latitude,
                'partner_longitude' : partner_longitude,
                'street':address,
                'mobile':phone_number,
                'customer_rank': 1,
                'category_id' : [(6, 0, tags if tags != False else [])],
            }
            partner = request.env['res.partner'].with_user(1).create(partner_data)
            return {
                'msg': _('Partner Created Successfully'),
                'status_code': 200,
                'partner_id' : partner.id


            }

        except Exception as e:
            return {
                'msg': str(e),
                'status_code': 400,
            }




    @http.route('/api/v1/customers/update', cors="*", csrf=False, type='json', auth="public", methods=['OPTIONS', 'POST'])
    @validate_token  
    @context_wrapper
    def updateCustomer(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Create sale order with provided payload
        :param kw: (lang, company-id, auth token)
        :return: status: 403, User Not Linked With Partner,
                 status: 400, missing parameter from the payload,
                 status: 400, carrier rejected the order,
                 status: 200, created successfully
        """
        try:
            # get request payload
            values = json.loads(request.httprequest.data)
            phone_number = values.get('phone_number', False)  # products
            address = values.get('address',False)
            partner_latitude = values.get('partner_latitude',False)
            partner_longitude = values.get('partner_longitude',False)
            qr_code = values.get('qr_code',False)
            tags = values.get('tags', False)  # note about the order
            name =  values.get('name', False) # partner that created the order
            partner_id =  values.get('partner_id', False) # partner that created the order

            if not partner_id:  # User is not related to a partner
                return {'msg': _('Customer (%s) not found' % partner_id), 'status_code': 400}


            partner_data = {
                'name': name,
                'qr_code': qr_code,
                'partner_latitude':partner_latitude,
                'partner_longitude' : partner_longitude,
                'street':address,
                'mobile':phone_number,
                'customer_rank': 1,
                'category_id' : [(6, 0, tags if tags != False else [])],

            }
            partner = request.env['res.partner'].with_user(1).browse(int(partner_id))
            partner.write(partner_data)
            return {
                'msg': _('Partner Updated Successfully'),
                'status_code': 200,
                'partner_id' : partner.id

            }

        except Exception as e:
            return {
                'msg': str(e),
                'status_code': 400,
            }
