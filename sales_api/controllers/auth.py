import functools
from odoo.http import JsonRequest
from odoo.http import request
from odoo import _
import datetime
from odoo import http
from odoo.http import request
import logging
import json
from .utils import *
from .json_request_patch import *
import datetime

_logger = logging.getLogger(__name__)



class AuthController(http.Controller):

    JsonRequest._json_response = JsonRequestPatch._json_response

    @http.route('/api/v1/login', type="json", auth="public", csrf=False)
    def SalesLogin(self, **kw):
        try:
            data = json.loads(request.httprequest.data)
            _logger.info('==============data payload==============')
            _logger.info(data)
            _logger.info('==============data payload==============')

            user = http.request.env['res.users'].sudo().search([('login', '=', data.get('username'))], limit=1)
            _logger.info('==============user==============')

            if user or len(user) > 0:
                _logger.info(user.checkPassword(data.get('password')))
                if user.checkPassword(data.get('password')) == False:
                    return {"status": 400, "msg": "Wrong Password", "data": None}

                user.write({
                    'imei' : data.get('imei',False),
                })

                #todo add option imei check
                # elif user.imei != data.get('imei',False):
                #     return {"status": 403, "msg": "Wrong Device Contact Hr", "data": None}

                return {"status": 200, "msg": "Success", "data":  user.read(fields=['id', 'partner_id', 'currency_id','imei' ,'lang', 'login', 'token', 'display_name', 'create_date', 'phone', 'notification_type'],load='')}

            return {"status": 400, "msg": "invalid user name", "data": None}

        except Exception as e:
            return {"status": 400, "msg": str(e), "data": str(e)}
