from odoo.http import Controller, request, Response
from odoo import http
from odoo.tools import date_utils
import json
from .utils import context_wrapper
import logging
_logger = logging.getLogger(__name__)
from .json_request_patch import *

class CategoryController(Controller):
    """
    Add custom APIS that uses the product.category model
    :routes /api/v1/category/list
            /api/v1/category/sub/<int:category_id>
    """
    JsonRequest._json_response = JsonRequestPatch._json_response

    # /api/v1/category/list
    @http.route('/api/v1/category/list', cors="*", type="http", method=["GET"], auth="public", csrf=False)
    @context_wrapper
    def category_list(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Get general categories list
        :param kw:(page, per_page, name)
        :return: status: 200, with fetched categories
        """
        resp_header = {"Content-Type": "application/json"}
        # get request payload
        category_name = kw.get('name', False)
        # build search query
        search_query = [('parent_id', '=', False)]
        search_query.append(('name', 'ilike', str(category_name).lower())) if category_name else None
        # get categories and total count
        categories = request.env['product.category'].with_user(1).with_context(lang=lang).with_company(
            company_id).search(search_query, limit=limit, offset=(page - 1) * limit)
        total_count = request.env['product.category'].with_user(1).with_company(company_id).search_count(
            search_query)
        
        categories = categories.with_company(company_id).read(fields=['id', 'name', 'api_image_url'])

        for item in categories:  # get products count for each category
            _logger.info('=========')
            _logger.info(company_id)
            _logger.info('=========')

            products_count = request.env['product.product'].sudo().with_context(lang=lang).with_company(company_id).search_count([('categ_id', '=', item['id']),('is_deactivate', '=', False)])
            item['products_count'] = products_count

        # check if it's the last page
        tmp_val = (page - 1) * limit + limit
        is_last_page = True if tmp_val >= total_count else False

        data = {
            'categories': categories,
            'total_count': total_count,
            'current_page': page,
            'per_page': limit,
            'is_last_page': is_last_page
        }
        # serialize the response object
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
                    "msg": "Fetch categories successfully.",
                    "data": obj_json
                }
            ).replace('false', 'null'),
            headers=resp_header,
            status=200
        )

    # /api/v1/category/sub/<int:category_id>
    @http.route('/api/v1/category/sub/<int:category_id>', cors="*", type="http", method=["GET"], auth="public",
                csrf=False)
    @context_wrapper
    def category_sub(self, category_id, *, lang, company_id, price_list, page, limit, **kw):
        """
        Get sub-categories for the parent category (category_id)
        :param category_id: Parent category_id
        :param kw: (Lang, company-id, page, per_page)
        :return: status: 404, if category_id not found for this company
                 status: 200, with fetched sub-categories
        """
        resp_header = {"Content-Type": "application/json"}
        # get parent category
        parent_category = request.env['product.category'].with_user(1).with_context(lang=lang).with_company(
            company_id).search([('id', '=', category_id)])

        if not parent_category:  # if parent category not found
            return Response(
                json.dumps(
                    {
                        "status": 404,
                        "msg": "Category Not Found",
                        "data": {}
                    }
                ),
                headers=resp_header,
                status=404
            )
        # build search query
        search_query = [('parent_id', '=', category_id)]
        # get sub-categories and their total_count
        sub_categories = request.env['product.category'].with_user(1).with_context(lang=lang).with_company(
            company_id).search(search_query, limit=limit, offset=(page - 1) * limit)
        total_count = request.env['product.category'].with_user(1).with_company(company_id).search_count(
            search_query)

        sub_categories = sub_categories.with_company(company_id).read(fields=['id', 'name'])
        # check if last page
        tmp_val = (page - 1) * limit + limit
        is_last_page = True if tmp_val >= total_count else False
        # serialize the response object
        data = {
            'sub-categories': sub_categories,
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
                    "msg": "Fetch sub-categories successfully.",
                    "data": obj_json
                }
            ),
            headers=resp_header,
            status=200
        )
