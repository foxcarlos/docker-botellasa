# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductBrand(models.Model):
    _name = 'product.brand'
    _inherit = 'product.brand'

    manufacture_name = fields.Char('Descripción', required=False)
    historia_bodega_corta = fields.Char('Historia Corta bodega', required=False)
    historia_bodega_larga = fields.Text('Historia larga bodega', required=False)
    code = fields.Char('Codigo', required=False)
    # image_medium = fields.Binary('Imagen', attachment=True)
    # image_medium ahora se llama logo , esto debo cambiar en wizard de importar imagenes

    @api.model
    def create(self, vals):
        if 'manufacture_name' in vals.keys():
            vals['name'] = vals['manufacture_name']
        return super(ProductBrand, self).create(vals)

    def write(self, vals):
        if 'manufacture_name' in vals.keys():
            vals['name'] = vals['manufacture_name']
        return super(ProductBrand, self).write(vals)
