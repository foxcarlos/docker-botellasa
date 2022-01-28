# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductVariety(models.Model):
    _name = 'product.variety'
    name_variedad = fields.Char('Descripción', required=False)
    code = fields.Char('Codigo', required=False)
    sinonimo_variedad = fields.Char('Sinonimo variedad', required=False)
    categoria_padre = fields.Many2one('product.public.category', 'Categoria Padre')
    product_ids = fields.One2many(
        "product.template", "variedad_id", string="Productos"
    )

    @api.depends('name_variedad')
    def name_get(self):
        res = []
        for variety in self:
            # name = '%s - %s'%(variety.code, variety.name)
            res.append((variety.id, variety.name_variedad))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # args = args or []
        domain = []
        if name == '0':
        	return []
        if name:
            domain = ['|', ('code', operator, name), ('name_variedad', operator, name + '%')]
        varieties = self.search(domain, limit=limit)
        return varieties.name_get()
