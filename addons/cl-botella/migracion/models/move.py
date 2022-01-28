''# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit ='account.move'

    idant = fields.Integer('Id anterior')

class AccountMoveLine(models.Model):
    _inherit ='account.move.line'

    idant = fields.Integer('Id anterior')
