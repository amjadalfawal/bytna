from datetime import datetime
from odoo.http import JsonRequest, Response
from odoo.tools import date_utils
import json
import logging

_logger = logging.getLogger(__name__)


class JsonRequestPatch(JsonRequest):

    def _json_response(self, result=None, error=None):
  
      def dict_replace_value(d, old, new):
          x = {}

          for k, v in d.items():
              if isinstance(v, dict):
                  v = dict_replace_value(v, old, new)
              elif isinstance(v, list):
                  v = list_replace_value(v, old, new)
              elif v == old:
                  v = new
              x[k] = v
          return x


      def list_replace_value(l, old, new):
          x = []
          for e in l:
              if isinstance(e, list):
                  e = list_replace_value(e, old, new)
              elif isinstance(e, dict):
                  e = dict_replace_value(e, old, new)
              elif e == old:
                  e = new
              x.append(e)

          return x

      response = {
   
      }
      default_code = 200
      if error is not None:
          response['error'] = error
      if result is not None:
          response['result'] = result
          # you don't want to remove some key of another result by mistake
          if isinstance(result, dict):
              status = result.pop('status', False)
              status_code = result.pop('status_code', False)
              data = result.pop('data', False)
              if status:
                  result.update({'status': status})
                  default_code = status
              if status_code:
                  result.update({'status_code': status_code})
                  default_code = status_code
              if data:
                  if isinstance(data, dict):
                    data = dict_replace_value(data, False, None)
                    result.update({"data":data})
                  elif isinstance(data,list):
                    data = list_replace_value(data, False, None)
                    result.update({"data":data})
  
      
      mime = 'application/json'
      body = json.dumps(response, default=date_utils.json_default)

      return Response(
          body, status=error and error.pop(
              'http_status', default_code) or default_code,
          headers=[('Content-Type', mime), ('Content-Length', len(body))]
      )


class NullEncoder(json.JSONEncoder):
    def default(self, obj):
        print('==========')
        _logger.info('==========')
        _logger.info(obj)

        if isinstance(obj, datetime):
            return str(obj)

        if isinstance(obj, bool):
            return None
      
        return super().default(obj)

        # return json.JSONEncoder.default(self, obj)
