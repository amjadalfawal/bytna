from odoo.http import Controller, request, Response
from odoo import http
from odoo.tools import date_utils
import json
from .utils import context_wrapper
from .json_request_patch import *


class BrandController(Controller):
    """
    Add custom APIS that uses the product.brand.ept model
    :routes /api/v1/brand/list
    """
    JsonRequest._json_response = JsonRequestPatch._json_response

    @http.route('/api/v1/brand/list', cors="*", type="http", method=["GET"], auth="public", csrf=False)
    @context_wrapper
    def brand_list(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Get published brands list based on search `name` or all the published brands
        :param kw: (lang, company-id)
        :return: status: 200, with fetched brands
        """
        response_headers = {"Content-Type": "application/json"}
        brand_name = kw.get('name', False)
        context = dict(request.env.context, quantity=1,pricelist=price_list.id, lang=lang)
        if brand_name:  # search for specific brand name
            brands_domain = [('is_featured_brand', '=', True),('name', 'ilike', brand_name)]
            brands = request.env['product.brand.ept'].with_context(context).with_user(1).with_company(
                company_id).search(brands_domain, limit=limit, offset=(page - 1) * limit, order='create_date desc')
            total_count = request.env['product.brand.ept'].with_user(1).with_company(company_id).search_count(
                brands_domain)

        else:  # get all published brands
            brands_domain = []
            brands = request.env['product.brand.ept'].with_context(context).with_user(1).with_company(
                company_id).search(brands_domain, order='create_date desc', limit=limit,
                                   offset=(page - 1) * limit)
            total_count = request.env['product.brand.ept'].with_user(1).with_company(company_id).search_count(
                brands_domain)

        brands = brands.with_context(context).with_user(1).with_company(company_id).read(
            fields=['sequence', 'name',  'id', 'description', 'is_featured_brand',
                     'products_count'])
        tmp_val = (page - 1) * limit + limit
        is_last_page = True if tmp_val >= total_count else False

        data = {
            'brands': brands,
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
                    "msg": "Fetch brands successfully.",
                    "data": obj_json
                }
            ).replace('false', 'null'),
            headers=response_headers,
            status=200
        )
