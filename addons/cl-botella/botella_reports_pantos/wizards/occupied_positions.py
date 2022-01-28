# -*- coding: utf-8 -*-
import openpyxl
from openpyxl import Workbook
from io import BytesIO
import base64
from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class OccupiedPositionDowload(models.Model):
    _name = 'botella_reports_pantos.occupied_position'
    file_report = fields.Binary(string="Archivo")
    file_name = fields.Char(string="Nombre Archivo")

    @api.multi
    def export_file(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        header = [
            "Descripcion",
            "Codigo Barra Un.",
            "Barra Caja.",
            "SKU",
            "Un.xCaja",
            "Estado",
            "Ubicación",
            "Cantidad Un.",
        ]
        print(header)
        ws.append(header)

        stock_report_location_obj = self.env['stock.report.quantity.by.location'].search([('quantity','>',0)])
        stock_location_obj = self.env['stock.location']
        product_obj = self.env['product.product']

        for location in stock_report_location_obj:
            if location:
                productos = product_obj.search([('id','=',location.product_id.id)])
                product_templ = product_obj.search([('id','=',productos.product_tmpl_id.id)])
                loc = stock_location_obj.search([('id','=',location.location_id.id)])
                content = [
                    productos.name,
                    productos.barcode,
                    product_templ.box_barcode,
                    product_templ.default_code,
                    product_templ.uom_po_id.id,
                    productos.type,
                    loc.complete_name,
                    location.quantity,
                ]
                ws.append(content)

# # # Guardamos el Fichero
        output = BytesIO()
        wb.save(output)
        #wb.save("/tmp/occupied_position.xlsx")
        self.file_report = base64.b64encode(output.getvalue())
        self.file_name = 'archivo_novedades.xlsx'
        wb.close()
        output.close()
        print('====> TERMINE!')
        return self.action_view_process_import()

    @api.multi
    def action_view_process_import(self):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('botella_reports_pantos.action_occupied_position_xls')
        # list_view_id = imd.xmlid_to_res_id('botella_reports_pantos.attendance_process_import_tree')
        form_view_id = imd.xmlid_to_res_id('botella_reports_pantos.occupied_position_xls_view')

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
