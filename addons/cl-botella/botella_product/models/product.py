# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Product(models.Model):
    _inherit ='product.template'
    _name = 'product.template'

    short_description = fields.Char('Descripción Corta (mobile)', required=False)
    long_description = fields.Char('Descripción Larga (web)', required=False)
    product = fields.Char('Producto', required=False)
    alcohol = fields.Char('Alcohol', required=False)
    puntajes = fields.Char('Puntajes', required=False)
    enologo = fields.Char('Enólogo', required=False)
    elaboracion_crianza_corta = fields.Char('Descripción Corta', required=False)
    elaboracion_crianza_larga = fields.Text('Descripción Larga', required=False)
    notas_cata = fields.Char('Notas cata', required=False)
    maridaje = fields.Char('Maridaje', required=False)
    precio_euros_bodega = fields.Float('Precio euros bodega', required=False)
    landed_cost_euros = fields.Float('Landed cost', required=False)
    inv_inal = fields.Char('Nro. inv/inal', required=False)
    # TODO: resolver esto! fecha de vencimiento no va en el producto!! idem lote
    fecha_vencimiento = fields.Date('Fecha vencimiento', required=False)
    despacho_aduanero = fields.Char('Despacho aduana', required=False)
    lote = fields.Char('Lote', required=False)
    comision_ventas = fields.Integer('Comisión de ventas', required=False)
    comision_cobranzas = fields.Integer('Comisión cobranzas', required=False)
    coleccion = fields.Char('Colección', required=False)
    modelo = fields.Char('Modelo', required=False)
    marca = fields.Char('Marca', required=False)
    #area = fields.Char('Area', required=False)
    area = fields.Selection(
        [('Cristaleria','Cristaleria'),
         ('Cerveza','Cerveza'),
         ('Vinos','Vinos'),
        ]
    )
    historia_bodega_corta = fields.Char('Historia Corta bodega', readonly=True, related='product_brand_id.historia_bodega_corta')
    historia_bodega_larga = fields.Text('Historia larga bodega', readonly=True, related='product_brand_id.historia_bodega_larga')
    volumen_cristaleria = fields.Char('Capacidad Cristaleria', required=False)
    metodo_fabricacion_corto = fields.Char('Fabricación Corto', required=False)
    metodo_fabricacion_largo = fields.Char('Fabricación Largo', required=False)
    denominacion_origen = fields.Char('Denominación origen')
    puntaje_parker = fields.Float('Parker')
    puntaje_wine_enthusiast = fields.Float('Wine Enthusiast')
    puntaje_jancis_robinson = fields.Float('Jancis Robinson')
    puntaje_wine_spectator = fields.Float('Wine Spectator')
    puntaje_james_suckling = fields.Float('James Suckling')
    puntaje_tim_atkin = fields.Float('Tim Atkin')
    puntaje_international_wine_challenge = fields.Float('International Wine Challenge')
    puntaje_decanter = fields.Float('Decanter')
    puntaje_guia_penin = fields.Float('Guía Peñín')
    puntaje_descorchados = fields.Float('Descorchados')


    def _set_header_and_footer(self, website_description):
        header = """<section class="s_text_block pt32 pb32">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-10 offset-lg-1 pt32 pb32">\n
                    """
        footer = """    </div>
                </div>
            </div>
        </section>\n"""
        return "%s%s%s"%(header, website_description, footer)

    def _get_p(self, field_key, field):
        title = self._get_title(field_key)
        if field and field not in ['0', 0]:
            return """<p class="o_default_snippet_text"><b class="o_default_snippet_text">%s</b>%s</p>\n"""%(title, field)

    def _get_title(self, field_key):
        TITLES = {
            'historia_bodega_larga': 'Historia de la Bodega: ',
            'description': 'Descripción del Producto: ',
            'elaboracion_crianza_larga': 'Elaboración y Crianza: ',
            'metodo_fabricacion_largo': 'Método de Fabricación: ',
            'notas_cata': 'Ficha de Cata: ',
            'maridaje': 'Maridaje: ',
        }
        return TITLES[field_key]

    def _get_full_p(self, fields, vals):
        website_description = ""
        for field in fields:
            if field in vals.keys():
                new_p = self._get_p(field, vals[field])
                if new_p:
                    website_description += new_p
        return website_description

    def get_lista_campos(self):
        return ['historia_bodega_larga',
                'description',
                'elaboracion_crianza_larga',
                'metodo_fabricacion_largo',
                'notas_cata',
                'maridaje'
               ]

    @api.model
    def create(self, vals):
        # historia de la bodega: product_brand_id -> historia_bodega_larga
        # descripción del producto: description
        # elaboración y crianza: elaboracion_crianza_larga
        # ficha de cata: notas_cata
        # maridaje: maridaje
        website_description = ''
        lista_de_campos = self.get_lista_campos()
        website_description = self._get_full_p(lista_de_campos, vals)
        if website_description:
            website_description = self._set_header_and_footer(website_description)
            vals['website_description'] = website_description
        return super(Product, self).create(vals)

    def _get_website_description(self, fields, vals):
        website_description = ''
        dicc = self.read(fields)[0]
        for field in fields:
            if field in vals.keys():
                dicc[field] = vals[field]
        website_description = self._get_full_p(fields, dicc)
        if website_description:
            website_description = self._set_header_and_footer(website_description)
        return website_description

    # def write(self, vals):
    #     #lista_de_campos = self.get_lista_campos()
    #     #vals['website_description'] = self._get_website_description(lista_de_campos, vals) # lista o diccionario con cada parte
    #     return super(Product, self).write(vals)

