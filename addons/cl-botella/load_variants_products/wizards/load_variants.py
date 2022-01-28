# -*- coding: utf-8 -*-
import base64
import datetime
import openpyxl
from datetime import date
from tempfile import TemporaryFile
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class CargaProductosVariantes(models.TransientModel):
    _name = 'townconnection.carga_masiva_productos_wizard'
    file = fields.Binary('Archivo para importar productos/variantes', required=True)
    info = fields.Text('Info')
    state = fields.Selection([('choose', 'choose'), ('done', 'done')], default="choose")

    def import_file(self):
        # Generación del archivo  Excel para ser leído por openpyxl
        file = base64.b64decode(self.file)
        excel_fileobj = TemporaryFile('wb+')
        excel_fileobj.write(file)
        excel_fileobj.seek(0)
        workbook = openpyxl.load_workbook(excel_fileobj)
        # Obtener la primera hoja de archivo de Excel
        sheet = workbook[workbook.get_sheet_names()[0]]
        msg = ''
        warn_msg = ''
        count_update = 0
        count_create_atributo = 0
        count_create_valor = 0
        count_alternativo_create = 0
        count_update_producto_alternativo = 0
        count_update_producto_accesorios = 0
        header = {}
        bandera = True
        lista_productos = []
        atribute_obj = self.env['product.attribute']
        atribute_value_obj = self.env['product.attribute.value']
        product_obj = self.env['product.product']
        product_tmpl_attribute_value = self.env['product.template.attribute.value']
        product_templ_obj = self.env['product.template']

        # Cargamos datos del excel en un diccionario
        for fila in sheet.rows:
            diccionario = {}
            contador = 0
            for dato in fila:
                if dato:
                    #primer fila completa el header{}
                    if bandera:
                        header[contador] = dato.value
                        contador += 1
                    else: #a partir de la segunda fila.. agrego el dato con su respectivo encabezado
                        diccionario[header[contador]] = dato.value
                        contador += 1
            if not bandera:
                lista_productos.append(diccionario)
            bandera = False


        for diccionario in lista_productos:
            barc = str(diccionario['ID']).strip()
            product_id = product_obj.search([('barcode', 'ilike', barc)])
            if not product_id:
                warn_msg += 'Barcode no encontrado: %s\n'%(barc)
                continue
            for header, value in diccionario.items():
                if header not in ('Impuesto Interno',
                                  'Producto Alternativo',
                                  'Producto Accesorio', 'ID', '', None):
                    atributo = atribute_obj.search([('name', '=', header)])
                    if not atributo:
                        atributo = atribute_obj.create({'name':header,
                                                        'type':'radio',
                                                        'create_variant':'no_variant'})
                        count_create_atributo += 1
                    valores_nuevos = str(value).split(',')
                    valores_atributos = []
                    for val in valores_nuevos:
                        valor = val.strip()
                        if valor in [None, 'None', 0, '0']:
                            continue
                        valor_atributo = atribute_value_obj.search(
                            [('attribute_id', '=', atributo.id), ('name', '=', valor)])
                        if not valor_atributo:
                            print ('creado....', valor)
                            valor_atributo = atribute_value_obj.create({'attribute_id':atributo.id,
                                                                        'name':valor})
                            count_create_valor += 1
                        valores_atributos.append(valor_atributo)
                    if not valores_atributos:
                        continue
                    value5 = [(4, attr5.id) for attr5 in valores_atributos]
                    args = [('product_tmpl_id', '=', product_id.product_tmpl_id.id),
                            ('attribute_id', '=', atributo.id)]
                    linea_de_atributos = product_tmpl_attribute_value.search(args)
                    if not len(linea_de_atributos):
                        product_id.write({'attribute_line_ids': [(0, 0,
                                                                  {'attribute_id': atributo.id,
                                                                   'value_ids':value5})]})
                        count_update += 1

                else:# Si es producto alternativo o accesorio:
                    producto = product_templ_obj.search([('barcode', '=', barc)])
                    _logger.info('==> (107) PRODUCTO ID = %s'%(producto.id))
                    codigos = str(value).split(',')
                    lista_codigos = []
                    for val in codigos:
                        codigo_barra = val.strip()
                        if codigo_barra in [None, 'None']:
                            continue
                        # Comprobamos que el codigo de barras exista en BD.
                        codigo = product_templ_obj.search(
                            [('barcode', '=', codigo_barra)])
                        if codigo.id in [None, 0, False]:
                            _logger.info('==> (118) NO EXISTE EL CODIGO EN BD = %s'%(codigo.name))
                            continue
                        else:
                            _logger.info('==> (121) EXISTE EN BD, AGREGO A LISTA EL = %s'%(codigo.id))
                            lista_codigos.append(codigo.id)
                    if not lista_codigos:
                        continue
                    if (header == 'Producto Alternativo') and (value not in [None, 'None']):
                        _logger.info('==> (126) LISTA DE CODIGOS ALTERNATIVOS = %s'%(lista_codigos))
                        producto.write({'alternative_product_ids': [(6, 0, lista_codigos)]})
                        _logger.info('==> (128) CARGANDO..  producto alt. = %s'%(producto))
                        count_update_producto_alternativo += 1

                    if (header == 'Producto Accesorio') and (value not in [None, 'None']):
                        _logger.info('==> (132) SOY UN PRODUCTO ACCESORIO = %s'%(producto.name))
                        _logger.info('==> (134) LISTA DE CODIGOS ACCESORIOS= %s'%(lista_codigos))
                        producto.write({'accessory_product_ids': [(6, 0, lista_codigos)]})
                        _logger.info('==> (135) CARGANDO accesorios= %s'%(producto))
                        count_update_producto_accesorios += 1


        msg = "%s\nCantidad de variantes creadas: %s\n" \
              "Cantidad de valores de variantes creadas: %s\n" \
              "Cantidad de valores alternativos creados: %s\n" \
              "Cantidad de valores en productos actualizados: %s"%(warn_msg, count_create_atributo,
                                                                   count_create_valor,
                                                                   count_alternativo_create,
                                                                   count_update
                                                                  )
        self.state = 'done'
        self.info = msg
        view_id = self.env['ir.ui.view'].search([('model', '=', 'townconnection.carga_masiva_productos_wizard')])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'townconnection.carga_masiva_productos_wizard',
            'name': _('Importar variantes'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
            'nodestroy': True,
            'context': {}
        }
