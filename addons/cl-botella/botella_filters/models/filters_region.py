# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FiltersRegion(models.Model):
    _name = 'res.country.region'

    name = fields.Char('Region', required=False)
    country_id = fields.Many2one('res.country', 'Pais')
    product_ids = fields.One2many(
        "product.template", "region_id", string="Productos"
    )

class Country(models.Model):
    _inherit = 'res.country'

    product_ids = fields.One2many(
        "product.template", "country_id", string="Productos"
    )

class State(models.Model):
    _inherit = 'res.country.state'

    product_ids = fields.One2many(
        "product.template", "state_id", string="Productos"
    )
