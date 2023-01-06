from odoo.http import Controller, request, Response
from odoo import http
from odoo.tools import date_utils
from .utils import *
import json
from .json_request_patch import *


class ProductController(Controller):
    """
    Add custom APIS that uses the product.product model
    :routes /api/v1/product/get-by-category/<int:category_id>
            /api/v1/product/search
            /api/v1/product/get-by-brand/<int:brand_id>
            /api/v1/product/<int:product_id>
            /api/v1/product/review
            /api/v1/product/search-filters
            /api/v1/product/auto-complete
    """
    JsonRequest._json_response = JsonRequestPatch._json_response

    # /api/v1/product/get-by-category/<int:category_id>
    @http.route('/api/v1/product/get-by-category/<int:category_id>', cors="*", type="http", method=["GET"],
                auth="public", csrf=False)
    @context_wrapper
    def product_get_by_category(self, category_id, *, lang, company_id, price_list, page, limit, **kw):
        """
        Fetch products and tags based on category_id
        :param category_id: the required category to filter on
        :param kw: metadata (lang, company-id, Authorization)
        :return: status: 200, products and tags with its related products
        """
        header = request.httprequest.headers['Authorization'] if request.httprequest.headers.has_key(
            'Authorization') else False
        token = header.replace('Bearer ', '') if header is not False else ''

        resp_header = {"Content-Type": "application/json"}

        products_domain = [('categ_id', '=', category_id),('is_deactivate', '=', False)]
        products = request.env['product.product'].with_user(1).with_context(lang=lang).with_company(company_id).search(products_domain, limit=limit, offset=(page - 1) * limit)  # Get Products

        # Get products total_count
        total_count = request.env['product.product'].with_user(1).search_count(products_domain)

        is_last_page = True if ((page - 1) * limit) + limit > total_count else False

        context = dict(
            request.env.context,
            quantity=1,
            pricelist=price_list.id,
            lang=lang
        )
        products = products.with_context(context).sorted('price')  # sort products on price
        # Get extra fields for the products
        products = extra_product_fields(products, company_id=company_id, token=token)

        # # Get Tags based on category_id
        # tags = request.env['product.category.tag'].with_user(2).with_context(lang=lang).with_company(company_id).search([('category_id', '=', category_id)], limit=limit, offset=(page - 1) * limit)
        # tags = tags.read(fields=['id', 'name', 'product_ids', 'api_image_url', 'category_id'])

        # for tag in tags:  # Get for each tag the related products
        #     product_tag_domain = [('id', 'in', tag['product_ids']),
        #                           ('is_deactivate', '=', False)]
        #     products_temp = request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
        #         company_id).search(product_tag_domain, limit=limit, offset=(page - 1) * limit)
        #     products_temp = products_temp.with_context(context).sorted('price')
        #     tag['product_ids'] = extra_product_fields(products_temp, company_id=company_id, token=token)

        data = {
            'products': products,
            # 'tags': tags,
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
                    "msg": "Fetch product by category successfully.",
                    "data": obj_json
                }
            ).replace('false', 'null'),
            headers=resp_header,
            status=200
        )

    # /api/v1/product/search
    @http.route('/api/v1/product/search', cors="*", type="json", method=["POST"], auth="public", csrf=False)
    @context_wrapper
    def product_search(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Search for products based on a search `term`
        :param kw: metadata (lang, company-id, Authorization)
        :return: status: 200, fetch products based on search term
        """
        data = json.loads(request.httprequest.data)  # get request payload
        term = data.get('term')
        # search domain for the products
        product_domain = ['|', '|',
                          ('name', 'ilike', term),
                          ('list_price', 'ilike', term),
                          ('description', 'ilike', term),
                          ('is_deactivate', '=', False)]

        products = request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
            company_id).search(product_domain, limit=limit, offset=(page - 1) * limit)
        total_count = request.env['product.product'].with_user(2).with_company(company_id).search_count(
            product_domain)

        is_last_page = True if ((page - 1) * limit) + limit > total_count else False

        context = dict(request.env.context, quantity=1,pricelist=price_list.id, lang=lang)
        # sort products and get required fields
        products = products.with_context(context).sorted('price')
        
        products = products.read(['id', 'name', 'description', 'api_image_url',
                                  'list_price', 'virtual_available', 'qty_available', 'price',
                                  'product_template_image_ids', 'taxes_id'])
        for obj in products:  # Get product template image, tax, and discount
            images = request.env['product.image'].with_user(2).with_context(lang=lang).with_company(
                company_id).search([('id', 'in', obj['product_template_image_ids'])])
            obj['product_template_image_ids'] = images.read(fields=['id', 'name', 'api_image_url'])
            # calculate the difference between the listed price and the company price
            difference = obj['list_price'] - obj['price']
            if obj['list_price'] != 0:
                discount = round(difference * 100 / obj['list_price'])
            else:
                discount = 0
            obj['tax'] = '19%'
            obj['disc'] = str(discount) + "%"

        data = {
            'products': products,
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
        return {
            "status": 200,
            "msg": "Fetch product search successfully.",
            "data": obj_json
        }

    # /api/v1/product/get-by-brand/<int:brand_id>
    @http.route('/api/v1/product/get-by-brand/<int:brand_id>', cors="*", type="http", method=["GET"], auth="public",
                csrf=False)
    @context_wrapper
    def product_get_by_brand(self, brand_id, *, lang, company_id, price_list, page, limit, **kw):
        """
        Fetch products based on brand_id
        :param brand_id: the required brand to filter on
        :param kw: metadata (lang, company-id)
        :return: status: 404, if brand not found
                 status: 200, fetch brand products successfully
        """
        response_headers = {"Content-Type": "application/json"}
        context = dict(request.env.context, quantity=1,
                       pricelist=price_list.id, lang=lang)
        brand = http.request.env['product.brand.ept'].with_context(context).with_user(2).with_company(
            company_id).search([('id', '=', brand_id)], limit=1)  # Get brand
        if not brand:
            return Response(
                json.dumps(
                    {
                        "status": 404,
                        "msg": "Brand Not Found",
                        "data": {}
                    }
                ),
                headers=response_headers,
                status=404)
        products_domain = [('product_brand_ept_id', '=', brand.id),
                           ('is_deactivate', '=', False)]
        # Get Products with the same brand
        products = http.request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
            company_id).search(products_domain, limit=limit, offset=(page - 1) * limit)

        total_count = http.request.env['product.product'].with_user(2).with_company(
            company_id).search_count(products_domain)
        # Get products extra fields
        products = extra_product_fields(products, company_id=company_id)

        tmp_val = (page - 1) * limit + limit
        is_last_page = True if tmp_val >= total_count else False

        data = {
            'products': products,
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
                    "msg": "Fetch Products by brand successfully.",
                    "data": obj_json
                }
            ).replace('false', 'null'),
            headers=response_headers,
            status=200
        )

    # /api/v1/product/<int:product_id>
    @http.route('/api/v1/product/<int:product_id>', cors="*", type="http", method=["GET"], auth="public",
                csrf=False)
    @context_wrapper
    def get_product_details(self, product_id, *, lang, company_id, price_list, page, limit, **kw):
        """
        Fetch product details using product_id
        :param product_id: the required product
        :param kw: metadata (lang, company-id, Authorization)
        :return: status: 404, if product not found
                 status: 200, fetch product details
        """
        resp_header = {"Content-Type": "application/json"}
        header = request.httprequest.headers['Authorization'] if request.httprequest.headers.has_key(
            'Authorization') else False
        token = header.replace('Bearer ', '') if header is not False else ''
        context = dict(request.env.context, quantity=1, pricelist=price_list.id, lang=lang)
        product_domain = [('id', '=', product_id), ('is_deactivate', '=', False)]
        product = http.request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
            company_id).search(product_domain, limit=1)
        if not product:
            return Response(
                json.dumps(
                    {
                        "status": 404,
                        "msg": "Product not found",
                        "data": {}
                    }
                ),
                headers=resp_header,
                status=200
            )

        product = product.with_context(context).sorted('price')
        # use token to check is product is in the user wishlist
        product = extra_product_fields(
            product, company_id=company_id, token=token)
        data = {
            'products': product,
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
                    "msg": "Fetch Product details successfully.",
                    "data": obj_json
                }
            ).replace('false', 'null'),
            headers=resp_header,
            status=200
        )

    # /api/v1/product/review
    @http.route('/api/v1/product/review', cors="*", type="json", method=["POST"], auth="public", csrf=False)
    @context_wrapper
    def product_review(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Review product out of 5.0 with comment
        :param kw: metadata (lang, company-id, Authorization)
        :return: status: 404, if product not found,
                 status: 400, if rating not in valid range,
                 status: 200, successfully rated with rate object,
                 status: 400, something went wrong
        """
        header = request.httprequest.headers['Authorization']
        token = header.replace('Bearer ', '')
        resp_header = {"Content-Type": "application/json"}
        user = http.request.env['res.users'].with_user(2).with_context(lang=lang).search(
            [('token', '=', token)], limit=1)
        if not user.partner_id:
            return Response(json.dumps({
                "status": 400,
                "msg": "User Not Linked With Partner Call Administrator ",
                "data": False
            }),
                headers=resp_header)
        # get payload data
        data = json.loads(request.httprequest.data)
        partner_id = user.partner_id.id
        try:
            product_id = data.get("product_id")
            comment = data.get("comment", "")
            rate = float(data.get("rate"))

            # get product object
            product_domain = [('id', '=', product_id),
                              ('is_deactivate', '=', False)]
            product = http.request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
                company_id).search(product_domain, limit=1)

            if not product:  # product not found
                return {
                    "status": 404,
                    "msg": f"Product not found",
                    "data": False
                }
            if rate < 1.0 or rate > 5.0:  # rating out of valid range
                return {
                    "status": 400,
                    "msg": "Rating must be in range [1.0 , 5.0]",
                    "data": False
                }

            # create new.rate object
            rating = request.env['new.rate'].with_user(2).create({
                "rate_value": rate,
                "rate_comment": comment,
                "partner_id": partner_id,
                "company_id": company_id,
                "product_id": product_id
            })

            # read required field for the new.rate
            data = {
                'rating': rating.with_context(lang=lang).read(
                    fields=["id", "rate_value", "rate_comment", "product_id", "partner_id", "company_id"])
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
                "msg": "Product was reviewed successfully",
                "data": obj_json
            }
        except Exception as e:
            return {
                "status": 400,
                "msg": str(e),
                "data": False
            }

    # /api/v1/product/search-filters
    @http.route('/api/v1/product/search-filters', cors="*", type="json", method=["POST"], auth="public", csrf=False)
    @context_wrapper
    def product_search_filters(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Search for products with filters
        :param kw: (lang, company-id, Authorization)
        :return: status: 200, with fetched products and brands
        """
        header = request.httprequest.headers['Authorization'] if request.httprequest.headers.has_key(
            'Authorization') else False

        token = header.replace('Bearer ', '') if header != False else ''

        # get request payload
        data = json.loads(request.httprequest.data)
        term = data.get('term', False)  # search term as string
        category_ids = data.get('category_ids', False)  # get products from the categories
        brand_ids = data.get('brand_ids', False)  # get products from the brands
        order_type = data.get('order_type', 3)  # order the results
        # build search queries
        products_domain = [('is_deactivate', '=', False)]
        brand_domain = []
        if term:  # search for the text term
            products_domain += ['|', '|', ('name', 'ilike', term), ('list_price', 'ilike', term),
                                ('description', 'ilike', term)]
            brand_domain.append(('name', 'ilike', term))
        if category_ids:  # add category_ids filter to search query
            products_domain.append(('categ_id', 'in', category_ids))
        if brand_ids:  # add brands_ids filter to search query
            products_domain.append(('product_brand_ept_id', 'in', brand_ids))
        # Get products and brands
        products = http.request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
            company_id).search(products_domain, )
        brands = http.request.env['product.brand.ept'].with_user(2).with_context(lang=lang).with_company(
            company_id).search(brand_domain, )
        # order context (price_list, lang)
        # context = dict(http.request.env.context, quantity=1, pricelist=price_list.id, lang=lang)

        switcher = {
            1: "name",
            2: "name",
            3: "create_date",
            4: "create_date",
            5: "list_price",
            6: "list_price",
        }
        reverse_order = False
        offset = (page - 1) * limit
        # check if order desc
        if order_type in [2, 3, 5]:
            reverse_order = True
        # order on create_date or price
        if order_type in [3, 4, 5, 6]:
            products = products.sorted(switcher.get(order_type), reverse=reverse_order)
        # order on name
        if order_type in [1, 2]:
            products = products.sorted(key=lambda x: str.lower(x["name"]).strip(),
                                                             reverse=reverse_order)  # strip and lower-case the text

        # get products extra fields
        products = extra_product_fields(products, company_id=company_id, token=token)

        total_count = len(products)  # get products total_count
        brands = brands  # sort the brands
        brands = brands[offset:(limit + offset if limit is not None else None)]  # perform pagination
        products = products[offset:(limit + offset if limit is not None else None)]  # perform pagination

        brands = brands.with_context(lang=lang).with_user(2).with_company(company_id).read(
            fields=['sequence', 'name', 'id', 'description', 'is_featured_brand',
                     'products_count'])

        # check if last_page
        tmp_val = (page - 1) * limit + limit
        is_last_page = True if tmp_val >= total_count else False
        # serialize the response object
        data = {
            'products': products,
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
        return {
            "status": 200,
            "msg": "Fetch product search successfully.",
            "data": obj_json
        }

    # deprecated function
    def orderTypeToString(self, argument=3):
        # sortByEnum {
        #     alphabticalAZ=1,
        #     alphabticalZA=2,
        #     newestFirst = 3,
        #     oldestFirst = 4,
        #     priceHighLow=5,
        #     priceLowHigh=6
        # }
        switcher = {
            1: "name asc",
            2: "name desc",
            3: "create_date desc",
            4: "create_date asc",
            5: "list_price desc",
            6: "list_price asc",
        }

        # get() method of dictionary data type returns
        # value of passed argument if it is present
        # in dictionary otherwise second argument will
        # be assigned as default value of passed argument
        return switcher.get(argument)

    # /api/v1/product/auto-complete
    @http.route('/api/v1/product/auto-complete', cors="*", type="json", method=["POST"], auth="public", csrf=False)
    @context_wrapper
    def product_auto_complete(self, *, lang, company_id, price_list, page, limit, **kw):
        """
        Get products for to autocomplete in the search bar
        :param kw: (lang ,company-id)
        :return: status: 200, with required products
        """
        # Get request payload
        data = json.loads(request.httprequest.data)
        term = data.get('term', False)  # get search term as string
        order_type = data.get('order_type', 3)  # get order type (name, create_date, list_price)
        # build search query
        products_domain = [('is_deactivate', '=', False)]
        if term:
            products_domain += ['|', '|', ('name', 'ilike', term), ('list_price', 'ilike', term),
                                ('description', 'ilike', term)]
        # get the products
        products = http.request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
            company_id).search(products_domain, limit=limit, offset=(page - 1) * limit,
                               order=self.orderTypeToString(argument=order_type))
        # sort products on price and get extra fields with context
        context = dict(http.request.env.context, quantity=1, pricelist=price_list.id, lang=lang)
        products = products.with_context(context).sorted('price')
        products = products.with_context(lang=lang).with_user(2).with_company(company_id).read(
            fields=['id', 'name', 'api_image_url'])
        total_count = http.request.env['product.product'].with_user(2).with_context(lang=lang).with_company(
            company_id).search_count(products_domain)
        # check if last_page
        tmp_val = (page - 1) * limit + limit
        is_last_page = True if tmp_val >= total_count else False
        data = {
            'products': products,
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
        return {
            "status": 200,
            "msg": "Fetch product search successfully.",
            "data": obj_json
        }
