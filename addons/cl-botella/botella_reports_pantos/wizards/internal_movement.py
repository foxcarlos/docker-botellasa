# -*- coding: utf-8 -*-
import openpyxl
from openpyxl import Workbook
from io import BytesIO
import base64
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class InternalMovementDowload(models.Model):
    _name = 'botella_reports_pantos.internal_movement'
    file_report = fields.Binary(string="Archivo")
    file_name = fields.Char(string="Nombre Archivo")

    @api.multi
    def export_file(self):
        
        wb = openpyxl.Workbook()
        ws = wb.active
        header_base = [
            "Fecha",
            "tipo de movimiento",
            "",
            "Ub Origen",
            "Producto",
            "Descripcion",
            "Lote",
            "Estado",
            "Cantidad",
            "",
            "Ub Destino",
            "Producto",
            "Descripcion",
            "Lote",
            "Estado",
            "Cantidad",
            "",
            "Usuario",
            ]
        ws.append(header_base)
        print(header_base)
        
        stock_location_obj = self.env['stock.location']
        product_obj = self.env['product.product']
        product_templ_obj = self.env['product.template']
        stock_move_line_obj = self.env['stock.move.line'].search([('id','>',0)])
        res_users_obj = self.env['res.users']

        x = 0
        for linea in stock_move_line_obj:
            if linea.product_id.id:
                location =  stock_location_obj.search([('id','=',linea.location_id.id)])
                location_dest =  stock_location_obj.search([('id','=',linea.location_dest_id.id)])
                prod = product_obj.browse(linea.product_id.id)
                #product =  product_templ_obj.search([('id','=',prod.product_tmpl_id.id)])
                product =  product_templ_obj.browse(prod.product_tmpl_id.id)
                user =  res_users_obj.search([('id','=',linea.create_uid.id)])

                
                content = [
                    linea.date, 
                    linea.reference,
                    " ",
                    location.name,
                    prod.name,
                    product.long_description,
                    linea.lot_name,
                    linea.state,
                    linea.qty_done,
                    " ",     
                    location_dest.name,
                    prod.name,
                    product.long_description,
                    linea.lot_name,
                    linea.state,
                    linea.qty_done,
                    " ", 
                    user.name,
                ]
                ws.append(content)    
                      

    # # #Guardamos el Fichero
        output = BytesIO()
        wb.save(output)
        self.file_report = base64.b64encode(output.getvalue())
        self.file_name = 'archivo_internal.xlsx'
        wb.close()
        output.close()
        return self.action_view_process_import()

    @api.multi
    def action_view_process_import(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('botella_reports_pantos.action_internal_movement_xls')
        form_view_id = imd.xmlid_to_res_id('botella_reports_pantos.internal_movement_xls_view')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['views'] = [(form_view_id, 'form')]
        result['res_id'] = self.id
        return result
