# Copyright (C) 2014-Today GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today La Louve (http://www.lalouve.net)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import math
import string
import random
import logging
_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):
    _inherit = "product.template"


    def random_string(self,length):
        return ''.join(random.choice(string.digits) for m in range(length))
        

    def calculate_check_digit(self,gtin):
        '''Given a GTIN (8-14) or SSCC, calculate its appropriate check digit'''
        reverse_gtin = gtin[::-1]
        total = 0
        count = 0
        for char in reverse_gtin:
            digit = int(char)
            if count % 2 == 0:
                digit = digit * 3
            total = total + digit
            count = count + 1

        nearest_multiple_of_ten = int(math.ceil(total / 10.0) * 10)
        return nearest_multiple_of_ten - total
        
    @api.model
    def create(self, vals):
        template = super(ProductTemplate,self).create(vals)
        _logger.info('=======================')  
        _logger.info(template)
        if template.barcode == False and len(str(template.barcode)) != 14 :
            barcode = self.random_string(13)
            barcode_check_digit =  self.calculate_check_digit(barcode)
            template.write({
                'barcode' : barcode +str(barcode_check_digit),
            })

        return template
  
  
    def write(self, vals):
        template = super(ProductTemplate,self).write(vals)
        _logger.info('=========write==============')  
        _logger.info(vals)
        _logger.info(self)
        _logger.info(vals.get('barcode',False))
        _logger.info(len(str(vals.get('barcode',False))))


        if vals.get('barcode',False) and len(str(vals.get('barcode',False))) != 14 :
            barcode = self.random_string(13)
            barcode_check_digit =  self.calculate_check_digit(barcode)
            self.write({
                'barcode' : barcode+str(barcode_check_digit),
            })

        return template
