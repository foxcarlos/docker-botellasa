# -*- coding: utf-8 -*-
import base64
import datetime
import openpyxl
from datetime import date
from tempfile import TemporaryFile
from odoo import api, fields, models, _


class LoadFilters(models.TransientModel):
    _name = 'cargo.filtros'
    file = fields.Binary('Archivo para importar filtros/marcas', required=True)
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
        contador_contenidos_creados = 0
        header = {}
        bandera = True
        lista_productos = []
        brand_obj = self.env['product.brand']
        bodega_obj = self.env['product.bodega']
        manufacter_obj = self.env['product.manufacter']
        country_obj = self.env['res.country']
        state_obj = self.env['res.country.state']
        region_obj = self.env['res.country.region']
        zone_obj = self.env['res.country.zone']
        cont_bodega_creada = 0
        cont_bodega_actualizada = 0
        cont_manufacter_creada = 0
        cont_manufacter_actualizada = 0
        mensaje_provincia = ''


        # Obtener Diccionario: header - valor
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

        # Recorremos el diccionario
        for diccionario in lista_productos:
            code = str(diccionario['Code'])
            if code == 'None':
                continue
            brand = brand_obj.search([('code', '=', code)])
            if not brand:
                warn_msg += 'Codigo no encontrado: %s\n'%(code)
                continue
#ZONA
            zona_name = str(diccionario['zona_bodega'])
            if zona_name != 'None':
                zona = zone_obj.search([('name', 'ilike', zona_name)])
                if not zona:
                    print('* 78 ===> NO HAY ZONA BODEGA EN BD... CREANDO!')
                    zona = zone_obj.create({'name':zona_name})
            else:
                zona = False
#REGION
            country_bodega_name = str(diccionario['pais_bodega'])
            if country_bodega_name != 'None':
                country_bodega = country_obj.search([('name', 'ilike', country_bodega_name)])
            else:
                country_bodega = False
            region_name = str(diccionario['region_bodega'])
            if region_name != 'None':
                args = [('name', '=', region_name)]
                if country_bodega:
                    args.append(('country_id', '=', country_bodega.id))
                region = region_obj.search(args)
                if not region:
                    print('* 95 ===> NO HAY REGION BODEGA EN BD... CREANDO!')
                    region = region_obj.create({'name': region_name,
                                                'country_id': country_bodega and country_bodega.id or False})
            else:
                region = False
#PROVINCIA
            state_name = str(diccionario['provincia_bodega'])
            if state_name != 'None':
                state = state_obj.search([('name', 'ilike', state_name)])
            else:
                mensaje_provincia += 'Provincia que no se puede crear: %s\n'%(
                    diccionario['provincia_bodega'])
                state = False
#FABRICANTE
            # No hago control de none en pais_fabricante porque siempre viene ese dato.
            country_manufacter_name = str(diccionario['pais_fabricante'])
            country_manufacter = country_obj.search([('name',
                                                      'ilike', country_manufacter_name)])
            manufacter_name = str(diccionario['fabricante_grupo'])
            if manufacter_name != 'None':
                manufacter = manufacter_obj.search([('name', 'ilike', manufacter_name),
                                                   ])
                if not manufacter:
                    print('* 118 ===> NO HAY FABRICANTE/MANUFACTER EN BD... CREANDO!')
                    manufacter = manufacter_obj.create({
                        'name': manufacter_name,
                        'zona_id': zona and zona.id or False,
                        'region_id': region and region.id or False,
                        'country_id': country_manufacter and country_manufacter.id or False})
                    cont_manufacter_creada += 1
                else:
                    print('* 126 ===> HAY FABRICANTE/MANUFACTER EN BD!...ACTUALIZANDO!')
                    manufacter.write({
                        'zona_id': zona and zona.id or False,
                        'region_id': region and region.id or False,
                        'state_id':state and state.id or False,
                        'country_id': country_manufacter and country_manufacter.id or False})
                    brand.write({'manufacter_id':manufacter.id})
                    cont_manufacter_actualizada += 1
            else:
                manufacter = False
#BODEGA
            country_bodega_name = str(diccionario['pais_bodega'])
            if country_bodega_name != 'None':
                country_bodega = country_obj.search([('name', 'ilike', country_bodega_name)])
                bodega_name = str(diccionario['bodega'])
                bodega = bodega_obj.search([('name', 'ilike', bodega_name)])
                if not bodega:
                    print('* 143 ===> NO HAY BODEGA EN BD... CREANDO!')
                    bodega = bodega_obj.create({'name': bodega_name,
                                                'manufacter_id': manufacter and manufacter.id or False,
                                                'zona_id': zona and zona.id or False,
                                                'state_id':state and state.id or False,
                                                'region_id': region and region.id or False})
                    cont_bodega_creada += 1
                else:
                    print('* 151 ===> HAY BODEGA EN BD!...ACTUALIZANDO!')
                    bodega.write({'name': bodega_name,
                                  'manufacter_id': manufacter and manufacter.id or False,
                                  'zona_id': zona and zona.id or False,
                                  'state_id':state and state.id or False,
                                  'region_id':region and region.id or False})
                    brand.write({'manufacter_id': manufacter and manufacter.id or False})
                    cont_bodega_actualizada += 1
            else:
                bodega = False
            if bodega:
                brand.bodega_id = bodega
            if manufacter:
                brand.manufacter_id = manufacter

        msg = "%s\nCantidad de bodegas creadas: %s\n" \
                "Cantidad de bodegas actualizadas: %s\n" \
                "Cantidad de fabricantes creadas: %s\n" \
                "Cantidad de fabricantes actualizados: %s\n" \
              " %s"%(warn_msg, cont_bodega_creada,
                     cont_bodega_actualizada,
                     cont_manufacter_creada,
                     cont_manufacter_actualizada,
                     mensaje_provincia
                    )
        self.state = 'done'
        self.info = msg
        view_id = self.env['ir.ui.view'].search([('model', '=', 'cargo.filtros')])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cargo.filtros',
            'name': _('Importar Filtros Bodegas/Fabricantes'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
            'nodestroy': True,
            'context': {}
        }
