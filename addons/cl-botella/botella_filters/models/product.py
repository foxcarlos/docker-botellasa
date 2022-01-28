# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Product(models.Model):
    _inherit ='product.template'
    _name = 'product.template'

    variedad_id = fields.Many2one('product.variety', 'Variedad Producto')
    varietal_web = fields.Char('Varietal Web')

    country_id = fields.Many2one(
        'res.country',
        compute='_compute_country',
        store=True,
        string='Pais'
    )
    region_id = fields.Many2one(
        'res.country.region',
        compute='_compute_country',
        store=True,
        string='Región'
    )
    zona_id = fields.Many2one(
        'res.country.zone',
        compute='_compute_country',
        store=True,
        string='Zona'
    )
    state_id = fields.Many2one(
        'res.country.state',
        compute='_compute_country',
        store=True,
        string='Provincia'
    )

    @api.depends('product_brand_id')
    def _compute_country(self):
        for rec in self:
            if rec.product_brand_id.bodega_id.region_id.country_id:
                rec.country_id = rec.product_brand_id.bodega_id.region_id.country_id.id
            elif rec.product_brand_id.manufacter_id.region_id.country_id:
                rec.country_id = rec.product_brand_id.manufacter_id.region_id.country_id.id
            else:
                rec.country_id = False
            if rec.product_brand_id.manufacter_id.region_id:
                rec.region_id = rec.product_brand_id.manufacter_id.region_id.id
            elif rec.product_brand_id.bodega_id.region_id:
                rec.region_id = rec.product_brand_id.bodega_id.region_id.id
            else:
                rec.region_id = False
            if rec.product_brand_id.manufacter_id.zona_id:
                rec.zona_id = rec.product_brand_id.manufacter_id.zona_id.id
            elif rec.product_brand_id.bodega_id.zona_id:
                rec.zona_id = rec.product_brand_id.bodega_id.zona_id.id
            else:
                rec.zona_id = False
            if rec.product_brand_id.bodega_id.state_id:
                rec.state_id = rec.product_brand_id.bodega_id.state_id.id
            else:
                rec.state_id = False