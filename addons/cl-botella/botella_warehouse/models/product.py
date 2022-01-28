# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression

class ProductTemplate(models.Model):
    _inherit ='product.template'
    _name = 'product.template'

    box_barcode = fields.Char('Codigo barra x caja', related="packaging_ids.barcode", store=True)

class Product(models.Model):
    _inherit ='product.product'
    _name = 'product.product'

    @api.depends('description_pickingout', 'name')
    def name_get(self):
        res = []
        for product in self:
            # name = '%s - %s'%(product.code, product.name)
            res.append((product.id, product.description_pickingout and product.description_pickingout or product.name))
        return res

class StockInventoryLine(models.Model):
    _inherit ='stock.inventory.line'
    _name = 'stock.inventory.line'

    box_barcode = fields.Char('Codigo barra x caja', related="product_id.box_barcode", store=False)
    default_code = fields.Char('Ref. Interna', related="product_id.default_code", store=False)
    uom_po_id = fields.Many2one('uom.uom', 'Unidad de medida Compra', related="product_id.uom_po_id", store=False)
    barcode = fields.Char('Codigo barra', related="product_id.barcode", store=False)
    price = fields.Float(
        compute='_compute_price',
        help='Price for product specified on the context',
        string="Precio de venta"
    )

    @api.multi
    def _compute_price(self):
        # TODO: esto se podría mejorar, en base a la company que está seleccionada
        tarifa_publica_botellasas = 1
        for rec in self:
            if rec.product_id:
                price = rec.product_id.with_context(pricelist=tarifa_publica_botellasas).price
                rec.price = price

class StockQuant(models.Model):
    _inherit ='stock.quant'
    _name = 'stock.quant'

    box_barcode = fields.Char('Codigo barra x caja', related="product_id.box_barcode", store=False)
    default_code = fields.Char('Ref. Interna', related="product_id.default_code", store=False)
    uom_po_id = fields.Many2one('uom.uom', 'Unidad de medida Compra', related="product_id.uom_po_id", store=False)
    barcode = fields.Char('Codigo barra', related="product_id.barcode", store=False)

class StockMoveLine(models.Model):
    _inherit ='stock.move.line'
    _name = 'stock.move.line'

    box_barcode = fields.Char('Codigo barra x caja', related="product_id.box_barcode", store=False)
    default_code = fields.Char('Ref. Interna', related="product_id.default_code", store=False)
    uom_po_id = fields.Many2one('uom.uom', 'Unidad de medida Compra', related="product_id.uom_po_id", store=False)
    barcode = fields.Char('Codigo barra', related="product_id.barcode", store=False)

class StockMove(models.Model):
    _inherit ='stock.move'
    _name = 'stock.move'

    box_barcode = fields.Char('Codigo barra x caja', related="product_id.box_barcode", store=False)
    default_code = fields.Char('Ref. Interna', related="product_id.default_code", store=False)
    uom_po_id = fields.Many2one('uom.uom', 'Unidad de medida Compra', related="product_id.uom_po_id", store=False)
    barcode = fields.Char('Codigo barra', related="product_id.barcode", store=False)

class StockLocation(models.Model):
    _inherit ='stock.location'

    packaging_id = fields.Many2one('product.packaging', 'Tipo de Posición')
    height = fields.Integer('Alto', related="packaging_id.height", store=False)
    width = fields.Integer('Ancho', related="packaging_id.width", store=False)
    length = fields.Integer('Profundidad', related="packaging_id.length", store=False)
