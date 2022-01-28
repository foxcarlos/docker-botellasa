''# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Company(models.Model):
    _inherit ='res.company'

    cai_code = fields.Char('CAI')
    cai_vto = fields.Date('Vencimiento CAI')
