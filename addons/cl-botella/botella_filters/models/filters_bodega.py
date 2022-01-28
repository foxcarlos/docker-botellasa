# -*- coding: utf-8 -*-
from odoo import models, fields, api

class FiltersBodega(models.Model):
    _name = 'product.bodega'
    name = fields.Char('Descripción', required=False)
    manufacter_id = fields.Many2one('product.manufacter', 'Fabricante')
    state_id = fields.Many2one('res.country.state', 'Provincia')
    region_id = fields.Many2one('res.country.region', 'Región')
    zona_id = fields.Many2one('res.country.zone', 'Zona')
