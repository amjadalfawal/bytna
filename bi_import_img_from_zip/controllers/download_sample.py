# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import content_disposition
import base64
import os, os.path
import csv
from os import listdir
import sys



class Download_xls(http.Controller):
    
    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_document(self,model,id, **kw):

        Model = request.env[model]
        res = Model.browse(int(id)).sudo()
        if res.img_for == 'employee':

            employee_zip = request.env['ir.attachment'].sudo().search([('name','=','employee.zip')])
            filecontent = employee_zip.datas
            filename = 'Employee.zip'
            filecontent = base64.b64decode(filecontent)

        elif res.img_for == 'partner':

            partner_zip = request.env['ir.attachment'].sudo().search([('name','=','partner.zip')])
            filecontent = partner_zip.datas
            filename = 'Partner.zip'
            filecontent = base64.b64decode(filecontent)

        elif res.img_for == 'product':

            product_zip = request.env['ir.attachment'].sudo().search([('name','=','product.zip')])
            filecontent = product_zip.datas
            filename = 'Product.zip'
            filecontent = base64.b64decode(filecontent)


        return request.make_response(filecontent,
            [('Content-Type', 'application/octet-stream'),
            ('Content-Disposition', content_disposition(filename))])