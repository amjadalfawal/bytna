from odoo.http import Controller, request, Response
from odoo import http, _
from odoo.tools import date_utils
from .utils import *
import json
import math
import base64
import logging
_logger = logging.getLogger(__name__)
from .json_request_patch import *

class SaleOrderController(Controller):
    """
    Add custom APIS that uses the sale.order model
    :routes /api/v1/order/list
            /api/v1/order/create
            /api/v1/order/validate
            /api/v1/order/print/<int:order_id>
            /api/v1/order/print-raw/<int:order_id>
            /api/v1/order/get/<int:order_id>
            /api/v1/order/rate
    """
    JsonRequest._json_response = JsonRequestPatch._json_response

    # /api/v1/order/list
    @http.route('/api/v1/order/list', cors="*", type="http", method=["GET"], auth="public", csrf=False)
    @validate_token
    @context_wrapper
    def order_list(self, lang, company_id, price_list, page, limit, **kw):
        """
        Fetch User orders
        :param kw: metadata (lang, company-id, Authorization)
        :return: status: 403, Invalid api token,
                 status: 400, User not linked a partner,
                 status: 200, Fetch orders successfully
        """
        # TODO: wrap metadata in a wrapper
        resp_header = {"Content-Type": "application/json"}
        # partner_id = request.pid
        _logger.info('================')
        _logger.info(request.uid)
        _logger.info('================')
        partner_id = int(kw.get('partner_id',False))
        status =  kw.get('status',False)
        date_from = kw.get('from',False)
        date_to = kw.get('to',False)

        orders_domain = [('user_id', '=', request.uid), ('company_id', '=', company_id)]

        # if partner_id:
        #     orders_domain.append(('partner_id', '=', partner_id))
        
        _logger.info('=======partner_id=========')
        _logger.info(partner_id)
        _logger.info('================')

        status =  kw.get('status',False)
        date_from = kw.get('from',False)
        date_to = kw.get('to',False)

        # orders_domain = [('user_id', '=', request.uid), ('company_id', '=', company_id)]

        if partner_id:
            orders_domain += [('partner_id', '=', partner_id)]
        
        # if status:
        #     #todo status 
        #     orders_domain = [('partner_id', '=', partner_id), ('company_id', '=', company_id)]

        # if date_from:
        #     #todo status 
        #     orders_domain = [('partner_id', '=', partner_id), ('company_id', '=', company_id)]

        # if date_to:
        #     #todo status 
        #     orders_domain = [('partner_id', '=', partner_id), ('company_id', '=', company_id)]


        _logger.info(orders_domain)
        # get orders
        orders = http.request.env['sale.order'].with_user(1).with_context(lang=lang).search(orders_domain
                                                                                            , limit=limit,
                                                                                            offset=(page - 1) * limit)
        # get orders total count (without pagination limit)
        total_count = http.request.env['sale.order'].with_user(1).with_context(lang=lang).search_count(orders_domain)
        orders = orders.read(
            fields=['id', 'name', 'date_order', 'create_date', 'partner_id',
                     'currency_id', 'order_line', 'invoice_status', 'note', 'amount_total',
                    'amount_tax', 'delivery_count','state','user_id','delivery_status','total_amount_before_discount','total_discount_amount'],load='')

        for obj in orders:  # iterate over orders and fetch details
            line = http.request.env['sale.order.line'].with_user(1).with_context(lang=lang).search(
                [('order_id', '=', obj['id'])])  # get order lines
            # delivery_address = http.request.env['res.partner'].with_user(1).with_context(lang=lang).search(
            #     [('id', '=', obj['partner_shipping_id'][0])], limit=1)  # get order delivery address
            # invoice_address = http.request.env['res.partner'].with_user(1).with_context(lang=lang).search(
            #     [('id', '=', obj['partner_invoice_id'][0])], limit=1)  # get order billing address

            stock_picking_domain = [('sale_id', '=', obj['id']), ('picking_type_code', '=', 'outgoing'),
                                    ('state', '=', 'done')]
            stock_picking = http.request.env['stock.picking'].with_user(1).with_context(lang=lang).search(stock_picking_domain, limit=1)

            obj['partner_id'] =  http.request.env['res.partner'].browse(obj['partner_id']).read(['name','id','api_image_url','partner_latitude','partner_longitude','mobile','street','barcode','sale_order_count','total_due','total_overdue','credit','debit','debit_limit','total_invoiced','allowed_days','invoice_ids','unpaid_invoices','property_product_pricelist','currency_id','tz','lang','qr_code'],load='')
            if obj['partner_id'][0]['id'] != False:
                obj['partner_id'][0]['currency_id'] =  http.request.env['res.currency'].browse(obj['partner_id'][0]['currency_id']).read([],load='')
            
            obj['currency_id'] =  http.request.env['res.currency'].browse(obj['currency_id']).read([],load='')
            obj['delivery_out_date'] = stock_picking.date_done  # get delivery date
            obj['order_line'] = line.read(fields=['id', 'name', 'price_unit', 'price_subtotal', 'price_tax',
                                                  'price_total', 'product_id','product_uom','discount','qty_delivered', 'qty_invoiced',
                                                  'product_uom_qty', 'api_image_url','sub_total_before_discount','discount_type','discount_amount'])
            lines_count = 0
            for line in obj["order_line"]:  # fetch each product related to an order line
                prod_id = line["product_id"][0]
                product = http.request.env['product.product'].with_user(1).browse(prod_id)
                is_service_product = False

                if product and product.type == 'service':  # check is service product
                    is_service_product = True

                if not is_service_product:
                    lines_count += 1 * int(line["product_uom_qty"])
            obj['order_line_count'] = lines_count  # order lines count without service products

            # obj['partner_shipping_id'] = delivery_address.read(
            #     fields=['type', 'country_id', 'state_id', 'comment', 'city', 'email', 'phone',
            #             'mobile', 'name', 'parent_id', 'parent_name', 'partner_latitude', 'partner_longitude',
            #             'partner_map_address', 'is_default_address'])  # fetch delivery address data
            # obj['partner_invoice_id'] = invoice_address.read(
            #     fields=['type', 'country_id', 'state_id', 'comment', 'city', 'email', 'phone',
            #             'mobile', 'name', 'parent_id', 'parent_name', 'partner_latitude', 'partner_longitude',
            #             'partner_map_address', 'is_default_address'])  # fetch billing address data

        is_last_page = True if ((page - 1) * limit) + limit > total_count else False
        data = {
            'orders': orders,
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
                    "msg": "Fetch orders successfully.",
                    "data": obj_json
                }
            ).replace('false', 'null'),
            headers=resp_header
        )

    # /api/v1/order/create
    @http.route('/api/v1/order/create', cors="*", csrf=False, type='json', auth="public", methods=['OPTIONS', 'POST'])
    @validate_token  
    @context_wrapper
    def order_create(self, *, lang, company_id, price_list, page, limit, **kw):
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
            product_ids = values.get('product_ids', False)  # products
            visit_id = values.get('visit_id',False)
            # partner_shipping_id = values.get('shipping_id', False)  # delivery address
            # partner_invoice_id = values.get('invoice_address_id', False)  # billing address
            # delivery_slot_id = values.get('delivery_slot_id', False)  # day date slot
            # delivery_slot_time_id = values.get('delivery_slot_time_id', False)  # time slot
            # payment_provider = values.get('payment_provider', False)  # STRIP or PAYPA
            # transaction_ref = values.get('transaction_ref', False)  # payment transaction ref from payment provider
            # xtend_pos_id = values.get('xtend_pos_id', False)  # Delivery Pos id (similar to company-id)
            note = values.get('note', False)  # note about the order
            # payment_draft_id = values.get('payment_draft', False)  # payment draft from Odoo
            partner_id =  values.get('partner_id', False) # partner that created the order
            # valid delivery carrier
            # carrier_id = http.request.env['delivery.carrier'].sudo().search(
            #     [('acess_token', '!=', False), ('company_id', '=', company_id)], limit=1)

            # if partner_invoice_id:  # billing address provided
            #     # Get address object
            #     invoice_address_domain = [('id', '=', partner_invoice_id), ('parent_id', '=', user.partner_id.id),
            #                               ('type', '=', 'invoice')]
            #     invoice_address = http.request.env['res.partner'].with_user(1).with_context(
            #         lang=lang).with_company(company_id).search(invoice_address_domain)
            #     if not invoice_address:  # address not found
            #         return {'msg': _('Invoice address (%s) was not found' % partner_invoice_id), 'status_code': 400}
            #     # set language to german
            #     invoice_address.with_user(1).write({
            #         "lang": "de_DE"
            #     })

            # if not partner_invoice_id:  # set delivery address as billing address if was not chosen
            #     partner_invoice_id = partner_shipping_id

            if not partner_id:  # User is not related to a partner
                return {'msg': _('Customer (%s) not found' % partner_id), 'status_code': 400}

            # if not payment_provider:  # Payment provider is required
            #     return {'msg': _('Missing payment_provider (%s) not found' % payment_provider), 'status_code': 400}

            # journal_id = http.request.env['account.journal'].with_user(1).with_company(company_id).search(
            #     [('code', 'ilike', payment_provider)], limit=1)

            if not request.user_id.journal_id.id:  # journal not found (try to check the journal code if changed)
                return {'msg': _('Missing Journal not found contact System Admin'), 'status_code': 400}

            journal_id = request.user_id.journal_id
            # if not transaction_ref:  # transaction_ref is required
            #     return {'msg': _('Missing transaction_ref (%s) not found' % transaction_ref), 'status_code': 400}

            # if not carrier_id:  # no valid carrier list
            #     return {'msg': _('No active Carrier in this company(%s) ' % carrier_id), 'status_code': 400}

            # if partner_shipping_id:
            #     # get address object
            #     delivery_address_domain = [('id', '=', partner_shipping_id), ('parent_id', '=', user.partner_id.id),
            #                                ('type', '=', 'delivery')]
            #     delivery_address = http.request.env['res.partner'].with_user(1).with_context(
            #         lang=lang).with_company(company_id).search(delivery_address_domain)
            #     if not delivery_address:  # address not found
            #         return {'msg': _('Delivery address (%s) was not found' % partner_shipping_id),
            #                 'status_code': 400}
            #     # change address language to german
            #     delivery_address.with_user(1).write({
            #         "lang": "de_DE"
            #     })
            #     # set user email as the delivery address email
            #     user.partner_id.with_user(1).write({
            #         "email": delivery_address.email
            #     })
            # # set language to german for the emails

            # user.partner_id.with_user(1).write({
            #     "lang": "de_DE"
            # })
            # sale order data
            so_data = {
                'partner_id': partner_id,
                'partner_shipping_id': partner_id,
                # 'partner_invoice_id': partner_invoice_id,
                # 'delivery_slot_id': delivery_slot_id,
                # 'delivery_slot_time_id': delivery_slot_time_id,
                # 'payment_provider': payment_provider,
                # "transaction_ref": transaction_ref,
                'company_id': company_id,
                'note': note,
                'user_id' : request.uid,
                'visit_id':visit_id
            }

            sol_data = []
            sol_total = 0
            prod_qty = {}

            # context for price_list and language
            context = dict(request.env.context, quantity=1, pricelist=price_list.id, lang=lang)
            # read sale order lines data with products
            for line_data in product_ids:
                prod_id = line_data.get('product_id', False)
                product = http.request.env['product.product'].with_user(1).with_company(company_id).browse(prod_id).with_context(context).sorted('price')
                price = product.price  # product price in the company
                if price <= 0:
                    price = product.lst_price  # general price for product
                # is_service_product = False
                # if product and product.type == 'service':
                #     is_service_product = True
                if not prod_id:  # product missing
                    return {'msg': _('Product (%d) not found' % prod_id), 'status_code': 400}
              
                discount_type = line_data.get('discount_type',False)
                sol_val = {
                    'product_id': prod_id,
                    'product_uom_qty': int(line_data.get('qty', 1)),
                    'price_unit': price,
                    'discount': line_data.get('discount_value',False),
                    'product_uom' : line_data.get('uom_id',False)
                }
                # if not is_service_product:  # service products (delivery tax)
                prod_qty.update({prod_id: int(line_data.get('qty', 1))})
                sol_total += (price * int(line_data.get('qty', 1)))
                sol_data.append([0, 0, sol_val])

                so_data.update({'order_line': sol_data})
            # create sale_order
            so_id = request.env['sale.order'].with_user(1).with_company(company_id).create(so_data)
            # add delivery tax to order using the wizard
            # delivery_wizard = http.request.env['choose.delivery.carrier'].sudo().with_company(company_id).create({
            #     'order_id': so_id.id,
            #     'carrier_id': carrier_id.id,
            # })
            # choose_delivery_carrier = delivery_wizard
            # choose_delivery_carrier._get_shipment_rate()  # calculate shipment prices
            # choose_delivery_carrier.sudo().with_company(company_id).button_confirm()
            # so_id.amount_delivery = choose_delivery_carrier.delivery_price  # set sale order delivery amount
            # confirm order to send to delivery carrier
            confirm_res = so_id.with_user(1).with_company(company_id).action_confirm()

            if not confirm_res:  # delivery carrier rejected the order
                return {'msg': 'Order has been created but not Confirmed', 'status_code' : 400}
            # create invoices for order
            invoice = so_id.with_user(1).with_company(company_id)._create_invoices()
            if invoice.state in ['draft', 'Draft']:
                invoice.with_user(1).with_company(company_id).action_post()
            # send invoice email to billing address
            # invoice_template = http.request.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
            # invoice.message_post_with_template(int(invoice_template.id),
            #                                    email_layout_xmlid="mail.mail_notification_paynow")

            # invoice.with_user(1).write({'is_move_sent': True})
            # if payment_draft_id:  # delete payment draft
            #     payment_draft = http.request.env['account.payment'].with_user(1).with_context(lang=lang).search(
            #         [('id', '=', payment_draft_id), ('partner_id', '=', partner_id.id),
            #          ('company_id', '=', company_id)], limit=1)
                # if payment_draft:
                #     payment_draft.unlink()
            # create payment from the invoices
            is_paid = values.get('is_paid', False)
            if is_paid:
                payment = http.request.env['account.payment.register'].with_user(1).with_company(company_id).with_context(
                    active_model='account.move', active_ids=invoice.ids).create(
                    {'journal_id': journal_id.id})._create_payments()
            # send sale_order email to user
            # so_id._send_order_confirmation_mail()
            return {
                'msg': _('Sale Order Created Successfully'),
                'status_code': 200,
                'sale_order_id': so_id.id,
                'sale_order_ref': so_id.name
            }

        except Exception as e:
            return e

    # /api/v1/order/validate
    @http.route('/api/v1/order/validate', cors="*", csrf=False, type='json', auth="public",
                methods=['POST', 'OPTIONS'])
    @context_wrapper
    def order_validate(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Validate sale order request before create
        :param kw:(lang, company-id,auth-token)
        :return: status: 403, User Not Linked With Partner,
                 status: 400, address not found,
                 status: 400, address related to another company
                 status: 400, Customer not found,
                 status: 400, Error in products price or products limits
                 status: 200, valid order,
                 status: 400, something went wrong
        """
        try:
            # context data
            header = request.httprequest.headers['Authorization']
            token = header.replace('Bearer ', '')
            # get user
            user = request.env['res.users'].with_user(1).with_context(lang=lang).search(
                [('token', '=', token)], limit=1)
            # check if user linked with partner
            if not user.partner_id:
                return {
                    "status": 403,
                    "msg": "User Not Linked With Partner Call Administrator ",
                    "data": False
                }
            # request body
            values = json.loads(request.httprequest.data)
            delivery_id = values.get('delivery_id', False)
            if delivery_id is not False:
                # get delivery address object
                delivery_id = request.env['res.partner'].with_user(1).search([('id', '=', delivery_id)], limit=1)
                if not delivery_id.id:  # address not found
                    return {'msg': _('Address Not Found'), 'status_code': 400, 'valid': False, 'data': False}
                # get zip codes
                zip_code_id = request.env['zip.code.company'].with_user(1).search([('name', '=', delivery_id.zip)],
                                                                                  order='id desc', limit=1)
                # get company for the required zipcodes
                company = request.env['res.company'].with_user(1).search([('zip_code_ids', 'in', [zip_code_id.id])],
                                                                         order='id desc', limit=1)
                if company.id != int(company_id):  # companies are not the same
                    return {'msg': _('Address Related To Another Company'), 'status_code': 400, 'valid': False,
                            'data': False}

            product_ids = values.get('product_ids', False)  # get product_ids
            partner_id = user.partner_id
            # set context
            context = dict(http.request.env.context, quantity=1, pricelist=price_list.id, lang=lang)
            if not partner_id:  # no such customer
                return {
                    'msg': _('Customer (%s) not found' % partner_id),
                    'status_code': 400,
                    'valid': False,
                    'data': False
                }
            wrong_qty_ids = []
            wrong_price_ids = []
            for line_data in product_ids:  # check each order line
                prod_id = line_data.get('product_id', False)
                # get product
                product = http.request.env['product.product'].with_user(1).with_company(company_id).browse(prod_id)
                product = product.with_company(company_id).with_context(context).sorted('price')
                is_service_product = False
                if product and product.type == 'service':
                    is_service_product = True
                if not prod_id:  # product not found
                    return {'msg': _('Product (%d) not found' % prod_id), 'status_code': 400, 'valid': False,
                            'data': False}
                if not is_service_product:  # check valid price for delivery products
                    price = product.price  # product price per company
                    if price <= 0:  # no special price in this company
                        price = product.lst_price  # use product list price
                    temp_price = float(line_data.get('unit_price', 0.0))
                    if not math.isclose(price, temp_price):  # the selling price isn't the same as the product price
                        wrong_price_ids.append(product.id)

            if len(wrong_price_ids) > 0 and len(wrong_qty_ids) > 0:  # if we invalid products
                # get wrong quantity products
                products = http.request.env['product.product'].with_user(1).with_context(lang=lang).with_company(
                    company_id).with_context(context).search([('id', 'in', wrong_qty_ids)])
                wrong_qty_products = products.with_company(company_id).with_context(context).read(
                    ['id', 'name', 'description', 'api_image_url', 'lst_price', 'virtual_available', 'qty_available'])
                # get wrong price products
                products = http.request.env['product.product'].with_user(1).with_context(lang=lang).with_company(
                    company_id).with_context(context).search([('id', 'in', wrong_price_ids)])
                wrong_price_products = products.with_company(company_id).with_context(context)
                wrong_price_products = extra_product_fields(wrong_price_products, company_id=company_id)
                # serialize response object
                data = {
                    'wrong_price_products': wrong_price_products,
                    'wring_qty_ids': wrong_qty_products
                }
                obj_json = json.loads(
                    json.dumps(
                        data,
                        default=date_utils.json_default,
                        skipkeys=True
                    )
                )

                return {
                    'status_code': 400,
                    'msg': "Error in products price or products limits",
                    'valid': False,
                    'data': obj_json
                }

            return {'msg': "Valid", 'status_code': 200, 'valid': True, 'data': False}
        except Exception as e:
            return {'msg': str(e), 'status_code': 400, 'valid': False, 'data': False}

    # /api/v1/order/print/<int:order_id>
    @http.route(['/api/v1/order/print/<int:order_id>'], csrf=False, type='http', auth="public", website=True, cors="*")
    @context_wrapper
    def order_print(self, order_id, *, lang, company_id, price_list, page, limit, **kwargs):
        """
        Generate order pdf file
        :param order_id: the required order
        :param kwargs: (lang, company-id, auth-token)
        :return: generated pdf file (application/pdf)
        """
        # context data
        header = request.httprequest.headers['Authorization']
        token = header.replace('Bearer ', '')
        resp_header = {"Content-Type": "application/json"}
        # check valid user
        user = http.request.env['res.users'].sudo().with_context(lang=lang).search(
            [('token', '=', token)], limit=1)
        if not user.partner_id:  # User not linked with a partner
            return Response(
                json.dumps(
                    {
                        "status": 400,
                        "msg": "User Not Linked With Partner Call Administrator ",
                        "data": False
                    }
                ),
                headers=resp_header
            )
        partner_id = user.partner_id.id
        # get order
        order = http.request.env['sale.order'].with_user(1).with_company(company_id).with_context(lang=lang).search(
            [('partner_id', '=', partner_id), ('id', '=', order_id)], limit=1)
        if not order.id:  # order not found for this customer
            return Response(
                json.dumps(
                    {
                        "status": 403,
                        "msg": "Order Dont Belong For This Customer ",
                        "data": False
                    }
                ),
                headers=resp_header
            )
        # generate pdf file
        pdf = request.env.ref('sale.action_report_saleorder')._render_qweb_pdf([order.id])[0]
        pdf_http_headers = [('Content-Type', 'application/pdf'),
                            ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdf_http_headers)

    # /api/v1/order/print-raw/<int:order_id>
    @http.route(['/api/v1/order/print-raw/<int:order_id>'], csrf=False, type='http', auth="public", website=True,
                cors="*")
    @context_wrapper
    def order_print_raw(self, order_id, *, lang, company_id, price_list, page, limit, **kwargs):
        """
        Generate order file in base64 encoding
        :param order_id: the required order
        :param kwargs: (lang, company-id, auth-token)
        :return: status: 400, User Not Linked With Partner,
                 status: 403, Order related to another user,
                 status: 200, with the file encoded in base64
        """
        # context data
        header = request.httprequest.headers['Authorization']
        token = header.replace('Bearer ', '')
        resp_header = {"Content-Type": "application/json"}
        # get user
        user = http.request.env['res.users'].sudo().search([('token', '=', token)], limit=1)
        if not user.partner_id:  # user not linked with a partner
            return Response(
                json.dumps(
                    {
                        "status": 400,
                        "msg": "User Not Linked With Partner Call Administrator",
                        "data": False
                    }
                ),
                headers=resp_header
            )
        partner_id = user.partner_id.id
        # get order
        order = request.env['sale.order'].with_user(1).with_company(company_id).with_context(lang=lang).search(
            [('partner_id', '=', partner_id), ('id', '=', order_id)], limit=1)
        if not order.id:  # order related to another partner (user)
            return Response(
                json.dumps(
                    {
                        "status": 403,
                        "msg": "Order Dont Belong For This Customer ",
                        "data": False
                    }
                ),
                headers=resp_header
            )
        # generate pdf file
        pdf = request.env.ref('sale.action_report_saleorder')._render_qweb_pdf([order.id])[0]
        # pdf file --> base64
        b64_pdf = base64.b64encode(pdf).decode()

        return Response(
            json.dumps(
                {
                    "status": 200,
                    "msg": "the data generated Successfully",
                    "data": b64_pdf
                }
            ),
            headers=resp_header
        )

    # /api/v1/order/get/<int:order_id>
    @http.route('/api/v1/order/get/<int:order_id>', cors="*", type="http", method=["GET"], auth="public", csrf=False)
    @context_wrapper
    def order_get(self, order_id, *, lang, company_id, price_list, page, limit, **kw):
        """
        Fetch order details
        :param order_id: required order
        :param kw: (lang, company-id)
        :return: status: 404, Order not found,
                 status: 200, Order fetched successfully
        """
        # context data
        resp_header = {"Content-Type": "application/json"}
        context = dict(http.request.env.context, quantity=1,
                       pricelist=price_list.id, lang=lang)
        # get order object
        order = request.env['sale.order'].with_user(1).with_context(lang=lang).search(
            [('id', '=', order_id)], limit=1)
        if len(order) != 1 or not order:  # order not found
            return Response(
                json.dumps(
                    {
                        "status": 404,
                        "msg": f"Order Not Found",
                        "data": False
                    }
                ),
                headers=resp_header,
                status=404
            )
        company_id = order.company_id
        order = order.read(
            fields=['id', 'name', 'date_order', 'create_date', 'partner_id', 'currency_id', 'order_line',
                    'partner_shipping_id', 'partner_invoice_id', 'payment_provider', 'delivery_slot_id',
                    'delivery_slot_time_id', 'invoice_status', 'note', 'amount_total', 'amount_tax', 'delivery_count',
                    'cart_quantity', 'amount_delivery'])[0]
        # get order lines
        line = request.env['sale.order.line'].with_user(1).with_context(lang=lang).search(
            [('order_id', '=', order['id'])])
        # get delivery address (partner)
        delivery_address = http.request.env['res.partner'].with_user(1).with_context(lang=lang).search(
            [('id', '=', order['partner_shipping_id'][0])], limit=1)
        # get invoice address (partner)
        invoice_address = http.request.env['res.partner'].with_user(1).with_context(lang=lang).search(
            [('id', '=', order['partner_invoice_id'][0])], limit=1)
        # read order lines data
        order['order_line'] = line.read(fields=['id', 'name', 'price_unit', 'price_subtotal', 'price_tax',
                                                'price_total', 'product_id', 'name_short', 'qty_invoiced',
                                                'product_uom_qty', 'api_image_url'])
        lines_count = 0
        for line in order["order_line"]:  # calc order lines count without service products
            prod_id = line["product_id"][0]
            product = http.request.env['product.product'].with_user(1).browse(prod_id)
            is_service_product = False
            if product and product.type == 'service':
                is_service_product = True
            if not is_service_product:
                lines_count += 1 * int(line["product_uom_qty"])
        order['order_line_count'] = lines_count
        # get products data
        product_ids = [line['product_id'][0] for line in order['order_line']]
        products = http.request.env['product.product'].with_user(1).with_context(context=context).with_company(
            company_id).search([('id', 'in', product_ids)])
        products = products.with_context(context).sorted('price')
        products = extra_product_fields(products, company_id=company_id.id)

        # get delivery address data
        order['partner_shipping_id'] = delivery_address.read(
            fields=['type', 'country_id', 'state_id', 'comment', 'city', 'email', 'phone',
                    'mobile', 'name', 'parent_id', 'parent_name', 'partner_latitude', 'partner_longitude',
                    'partner_map_address', 'is_default_address'])
        # get invoice address data
        order['partner_invoice_id'] = invoice_address.read(
            fields=['type', 'country_id', 'state_id', 'comment', 'city', 'email', 'phone',
                    'mobile', 'name', 'parent_id', 'parent_name', 'partner_latitude', 'partner_longitude',
                    'partner_map_address', 'is_default_address'])

        data = {
            'order': order,
            'products': products
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
                    "msg": "Order details fetched successfully",
                    "data": obj_json
                }
            ),
            headers=resp_header
        )

    # /api/v1/order/rate
    @http.route('/api/v1/order/rate', cors="*", type="json", method=["POST"], auth="public", csrf=False)
    @context_wrapper
    def order_rate(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Rate the order out of 5.0 with comment
        :param kw: (lang, company-id, auth-token)
        :return: status: 400, User Not Linked With Partner,
                 status: 400, Order not related to this user,
                 status: 404, Order was not found,
                 status: 400, Rating out of range,
                 status: 200, Rated successfully,
                 status: 400, Something went wrong
        """
        # context data
        header = request.httprequest.headers['Authorization']
        token = header.replace('Bearer ', '')
        resp_header = {"Content-Type": "application/json"}
        # check valid user
        user = request.env['res.users'].with_user(1).with_context(lang=lang).search(
            [('token', '=', token)], limit=1)
        if not user.partner_id:
            return Response(
                json.dumps(
                    {
                        "status": 400,
                        "msg": "User Not Linked With Partner Call Administrator",
                        "data": False
                    }
                ),
                headers=resp_header
            )
        # get request payload
        partner_id = user.partner_id.id
        data = json.loads(request.httprequest.data)
        try:
            order_id = data.get("order_id")  # required order
            comment = data.get("comment", "")  # comment as string
            rate = float(data.get("rate"))  # rate as float [1.0 - 5.0]
            # get order
            order = http.request.env['sale.order'].with_user(1).with_company(company_id).with_context(lang=lang).search(
                [('partner_id', '=', partner_id), ('id', '=', order_id)], limit=1)
            if not order:  # Order not found with this partner
                order = http.request.env['sale.order'].with_user(1).with_company(company_id).with_context(
                    lang=lang).search([('id', '=', order_id)], limit=1)
                if order:  # check if order belong to another user
                    return {
                        "status": 400,
                        "msg": "Order is not related to this user",
                        "data": False
                    }
                return {  # order not found for any user
                    "status": 404,
                    "msg": "Order not found",
                    "data": False
                }
            if rate < 1.0 or rate > 5.0:  # check rate out of range [1.0 - 5.0]
                return {
                    "status": 400,
                    "msg": "Rating must be in range [1.0 - 5.0]",
                    "data": False
                }
            # create rate object
            rating = request.env['new.rate'].with_user(1).create({
                "rate_value": rate,
                "rate_comment": comment,
                "partner_id": partner_id,
                "company_id": company_id,
                "order_id": order_id
            })
            # serialize response object
            data = {
                'rating': rating.with_context(lang=lang).read(
                    fields=["id", "rate_value", "rate_comment", "order_id", "partner_id", "company_id"])
            }
            obj_json = json.loads(
                json.dumps(
                    data,
                    default=date_utils.json_default,
                    skipkeys=True
                )
            )
            return {
                "status": 200,
                "msg": "Order was rated successfully",
                "data": obj_json
            }

        except Exception as e:
            return {
                "status": 400,
                "msg": str(e),
                "data": False
            }
