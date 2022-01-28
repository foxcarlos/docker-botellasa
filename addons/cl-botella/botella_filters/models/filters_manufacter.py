# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductManufacter(models.Model):
    _name = 'product.manufacter'

    name = fields.Char('Descripción', required=True)
    historia_bodega_corta = fields.Char('Historia Corta bodega', required=False)
    historia_bodega_larga = fields.Text('Historia larga bodega', required=False)
    code = fields.Integer('Codigo', required=False)
    image_medium = fields.Binary('Imagen', attachment=True)
    zona_id = fields.Many2one('res.country.zone','Zona')
    state_id = fields.Many2one('res.country.state','Provincia')
    region_id = fields.Many2one('res.country.region','Región')
    country_id = fields.Many2one('res.country','País')
