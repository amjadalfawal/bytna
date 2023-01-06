import logging
from odoo import models, api, fields,exceptions, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)
import bcrypt
import time
import string    
import random # define the random module  
import hashlib
from odoo.exceptions import AccessDenied

class ResUsers(models.Model):

    _inherit = 'res.users'

    token  = fields.Char(string="token" ,  size=60, index=True)
    fb_token = fields.Char("fire base token" , size=300, index=True)
    fb_uid = fields.Char("fire base user id" , size=300, index=True)
    mobile_password = fields.Char(string="Mobile Password" , size=60, index=True)
    is_verified = fields.Boolean(string="Verfied")
    imei = fields.Char('Mobile ImeI')
    journal_id = fields.Many2one('account.journal', 'Sales Man Journal',domain="[('type','in',['cash'])]")
    def generateToken(self):
        S = 60  # number of characters in the string.  
        # call random.choices() string module to find the string in Uppercase + numeric data.  
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S))    
        dk = hashlib.pbkdf2_hmac('sha256', ran.encode() , 'salt'.encode(), 100000)
        self._setToken(dk.hex())
        return self.token

    def getUserByToken(self,token):
        rec = self.env['res.users'].search([('token','=',token)],limit=1)
        return rec

    def _setToken(self , token):
        self.token = token
        return self.token

    
    def _getToken(self):
        return self.token
    

    @api.onchange('mobile_password')
    def _onchange_mobile_password(self):
        salt = bcrypt.gensalt(rounds=16)
        if self.mobile_password == False:
            return

        hashed = bcrypt.hashpw(self.mobile_password.encode('utf-8'), salt)
        self.mobile_password = hashed.decode()
        self.generateToken()


    def generatePasswordHash(self):
        salt = bcrypt.gensalt(rounds=16)
        if self.mobile_password == False:
            return

        hashed = bcrypt.hashpw(self.mobile_password.encode('utf-8'), salt)
        self.mobile_password = hashed.decode()
        self.generateToken()


    def checkPassword(self,password):
        if self.mobile_password == False:
            raise AccessDenied("There is no mobile password set for this user call the admin")
        if bcrypt.checkpw(password.encode(), self.mobile_password.encode()):
            return True
        else:
            return False
