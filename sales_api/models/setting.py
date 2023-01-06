import pytz
from datetime import datetime, time
from odoo import models, fields, api
from odoo.tools import float_compare

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    attendance_auto_mode = fields.Boolean(string="Kiosk Mode Auto",  readonly=False,default=True)
    attendance_geo_capture = fields.Boolean(string="Kiosk Mode geo Capture",  readonly=False,default=False)
    similarity_distance = fields.Float('similarity distance', digits=(1,1), readonly=False,  default=0.5)
    attendance_force_geo = fields.Boolean(string="Force Geo Location",  readonly=False,default=True)
    attendance_zone_rule = fields.Boolean(string="Zone Rule Check",  readonly=False,default=True)   
    similarity_distance_kiosk = fields.Float('similarity distance Kiosk', digits=(1,1), readonly=False,  default=0.5)
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            attendance_auto_mode = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_auto_mode'),
            attendance_geo_capture = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_geo_capture'),
            similarity_distance = float(self.env['ir.config_parameter'].sudo().get_param('hr_apis.similarity_distance')),
            similarity_distance_kiosk = float(self.env['ir.config_parameter'].sudo().get_param('hr_apis.similarity_distance_kiosk')),

            attendance_zone_rule = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_zone_rule'),
            attendance_force_geo = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_force_geo'),

        )
        return res


    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field1 = self.attendance_auto_mode
        field2 = float(self.similarity_distance)
        field6 = float(self.similarity_distance_kiosk)

        field3 = self.attendance_geo_capture
        filed5 = self.attendance_force_geo
        filed4 = self.attendance_zone_rule
        param.set_param('hr_apis.attendance_auto_mode', field1)
        param.set_param('hr_apis.attendance_geo_capture', field3)
        param.set_param('hr_apis.similarity_distance', field2)
        param.set_param('hr_apis.similarity_distance_kiosk', field6)
        param.set_param('hr_apis.attendance_zone_rule', filed4)
        param.set_param('hr_apis.attendance_force_geo', filed5)

    def getSettingsFaceRecognition(self, given_context=None):
        attendance_auto_mode = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_auto_mode'),
        attendance_geo_capture = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_geo_capture'),
        similarity_distance = float(self.env['ir.config_parameter'].sudo().get_param('hr_apis.similarity_distance')),
        similarity_distance_kiosk = float(self.env['ir.config_parameter'].sudo().get_param('hr_apis.similarity_distance_kiosk')),
        attendance_force_geo = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_force_geo'),
        attendance_zone_rule = self.env['ir.config_parameter'].sudo().get_param('hr_apis.attendance_zone_rule'),

        vals = {
            "mode": attendance_auto_mode[0],
            'similarity_distance': similarity_distance[0],
            'similarity_distance_kiosk': similarity_distance_kiosk[0],
            'attendance_geo_capture' : attendance_geo_capture[0],
            'attendance_force_geo': attendance_force_geo[0],
            'attendance_zone_rule': attendance_zone_rule[0]
        }
        data = {"response": vals, "message": "Setting returned"}
        return data

