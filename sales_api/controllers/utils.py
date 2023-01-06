import functools
from odoo import http
from odoo.http import request
from math import radians, cos, sin, asin, sqrt
import logging
_logger = logging.getLogger(__name__)
SUDO = 1

def context_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        lang = request.httprequest.headers['Lang'] if request.httprequest.headers.has_key('Lang') else 'en'
        company_id = int(request.httprequest.headers['company-id']) if request.httprequest.headers.has_key('company-id') else 1
        price_list = request.env['product.pricelist'].with_user(2).with_context(lang=lang).with_company(company_id).search([], order='id desc', limit=1)
        page = int(kwargs.get('page', 1))
        limit = int(kwargs.get('per_page', 5))
        if 'page' in kwargs:
            kwargs.pop('page')
        if 'per_page' in kwargs:
            kwargs.pop('per_page')
        return func(*args, lang=lang, company_id=company_id, price_list=price_list, page=page, limit=limit, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

def validate_token(func):
    """ decorator to validate user token """
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        lang = request.httprequest.headers['Lang'] if request.httprequest.headers.has_key('Lang') else 'en'
        header = request.httprequest.headers['Authorization'] if request.httprequest.headers.has_key('Authorization') else False
        token = header.replace('Bearer ', '') if header != False else "no_token"
        user = http.request.env['res.users'].with_user(2).with_context(lang=lang).search([('token', '=', token)], limit=1)
        if user.id == False:
            return {
                "status": 403,
                "msg": "Invalid Token",
                "data": False
            }
        if user.partner_id.id == False:
            return {
                "status": 403,
                "msg": "User Not Linked With Partner",
                "data": False
            }
        request.uid = user.id
        request.user_id = user
        request.pid = user.partner_id.id
        request.partner_id = user.partner_id

        return func(self, *args, **kwargs)
    return wrap

def haversine(self,lon1, lat1, lon2, lat2 ):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def checkZoneRule(self,cu,latitude,longitude,accuracy):
    employees_rec = http.request.env["hr.employee"].sudo().search([('user_id.id','=',cu.id)])
    lat1 = latitude
    lon1 = longitude
    for zone in employees_rec.attendance_zones :
        a = self.haversine(lon1, lat1, zone.center_longitude, zone.center_latitude)
        if a <= zone.radius:
            return True
    return False
        

def extra_visits_fields(visits, company_id=1):
    visits = visits.read(fields=['id','name', 'partner_id','visiting_day','start_date','end_date','rate_visit', 'visit_notes', 'state', 'visit_status', 'create_date'],load='')
    for obj in visits:  # get more fields
        _logger.info('==========')
        _logger.info(obj)
        _logger.info(obj['partner_id'])
        _logger.info('==========')
        
        obj['partner_id'] =  http.request.env['res.partner'].browse(obj['partner_id']).read(['name','id','api_image_url','partner_latitude','partner_longitude','mobile','street','barcode','sale_order_count','total_due','total_overdue','credit','debit','debit_limit','total_invoiced','allowed_days','invoice_ids','unpaid_invoices','property_product_pricelist','currency_id','tz','lang','qr_code','category_id'],load='')
        _logger.info(obj['partner_id'][0]['currency_id'])
        if obj['partner_id'][0]['id'] != False:
            _logger.info(obj['partner_id'][0]['currency_id'])
            obj['partner_id'][0]['currency_id'] =  http.request.env['res.currency'].browse(obj['partner_id'][0]['currency_id']).read([],load='')
            obj['partner_id'][0]['category_id'] =  http.request.env['res.partner.category'].browse(obj['partner_id'][0]['category_id']).read([],load='')           

    visits[:] = [item for item in visits if item != {}]  # remove the empty products (deactivated)
    return visits

def get_uom_by_category(uom_id,product_id):
    # uom =  http.request.env['uom.uom'].with_user(1).search([('id', '=' , uom_id)],limit=1)
    # if uom.id != False:
        # uom_ids =  http.request.env['uom.uom'].with_user(1).search([('category_id', '=' , uom.category_id.id),('active','=',True)])
        # uom_ids =  uom_ids.with_user(1).read(['name','id','rounding'],load='')
        # context = dict(http.request.env.context, quantity=1, pricelist=1, )
        # products = products.with_context(context).sorted('price')    
    product = http.request.env['product.product'].with_user(1).browse(product_id)
    uom_ids = False
    if len(product.uom_allowed_ids) > 0:
        uom_ids = product.uom_allowed_ids.with_user(1).read(['name','id','rounding'],load='')
    else:
        uom_ids = product.uom_id.with_user(1).read(['name','id','rounding'],load='')
    _logger.info('========')
    _logger.info(uom_ids)
    _logger.info(product.uom_allowed_ids)
    _logger.info('========')

    for obj in uom_ids:
        uom = http.request.env['uom.uom'].with_user(1).browse(obj['id'])
        obj['price'] = product.price
        if product.price <= 0:  # check for price discount
            obj['price'] = product.lst_price 
                    
        obj['price'] = product.uom_id._compute_price(obj['price'], uom)

        difference = product.uom_id._compute_price(product.lst_price, uom)  - obj['price']

        if product.uom_id._compute_price(product.lst_price, uom) != 0:
            discount = round(difference * 100 / product.uom_id._compute_price(product.lst_price, uom))
        else:
            discount = 0

        

        obj['disc'] = str(discount) + "%"


        if discount > 0 and obj['price'] > 0:
            obj['is_discount'] = True
        else:
            obj['is_discount'] = False


        if discount < 0 :
            obj['disc'] = str(0) + "%"
            obj['is_discount'] = False

    return uom_ids
    # return None

def extra_product_fields(products,  company_id=1, token=''):

    """
    It takes products and read their extra fields, such as:
    product_template_image, is_wishlist, price, discount, ... and etc.
    :param products: products list
    :param company_id: products company
    :param token: user token
    :return: products list with extra fields
    """

    # read extra product fields
    products = products.with_company(company_id).read(
        ['id', 'name', 'product_template_image_ids', 'description', 'api_image_url', 'product_template_image_ids',
         'list_price', 'virtual_available', 'uom_id' , 'qty_available', 'price', 'short_desc', 'taxes_id', 'is_deactivate',
         'weight', 'volume', 'type'],load='')
    for obj in products:  # get more fields
        # get product template image
     
        obj['uom_ids'] = get_uom_by_category(obj['uom_id'],obj['id'])


        images = http.request.env['product.image'].with_user(2).with_company(company_id).search(
            [('id', 'in', obj['product_template_image_ids'])])
        obj['product_template_image_ids'] = images.read(fields=['id', 'name', 'api_image_url'])
        if obj['price'] <= 0:  # check for price discount
            obj['price'] = obj['list_price']
        difference = obj['list_price'] - obj['price']
        if obj['list_price'] != 0:
            discount = round(difference * 100 / obj['list_price'])
        else:
            discount = 0
        obj['disc'] = str(discount) + "%"
        if discount > 0 and obj['price'] > 0:
            obj['is_discount'] = True
        else:
            obj['is_discount'] = False


        if obj['is_deactivate'] is True:
            obj.clear()
    products[:] = [item for item in products if item != {}]  # remove the empty products (deactivated)
    return products
