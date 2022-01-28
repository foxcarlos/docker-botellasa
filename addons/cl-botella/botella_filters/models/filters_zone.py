# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FiltersZone(models.Model):
    _name = 'res.country.zone'

    name = fields.Char('Zona', required=False)
    product_ids = fields.One2many(
        "product.template", "zona_id", string="Productos"
    )
