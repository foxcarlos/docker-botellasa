# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FiltersBrand(models.Model):
    _name = 'product.brand'
    _inherit = 'product.brand'

    bodega_id = fields.Many2one('product.bodega','Bodega')
    manufacter_id = fields.Many2one('product.manufacter','Fabricante/Grupo')
    country_id = fields.Many2one(
        'res.country',
        compute='_compute_country',
        store=True,
        string='Pais'
    )

    @api.depends('bodega_id', 'manufacter_id')
    def _compute_country(self):
        for rec in self:
            if rec.bodega_id:
                rec.country_id = rec.bodega_id.region_id.country_id and \
                                 rec.bodega_id.region_id.country_id.id or False
            elif rec.manufacter_id:
                rec.country_id = rec.manufacter_id.country_id and \
                                 rec.manufacter_id.country_id.id or False