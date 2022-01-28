# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import csv
import urllib.request
import base64
import sys
from odoo import models, fields, api, _
from odoo.exceptions import Warning
import openpyxl
from tempfile import TemporaryFile
import logging
_logger = logging.getLogger(__name__)
EXTENSIONES = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']


class ProductImageImportWizard(models.TransientModel):
    _name = 'import.product_image'

    product_model = fields.Selection(
        [
            ('product.template', 'Product Template'),
            ('product.brand', 'Product Manufacture'),
            # ('2', 'Product Variants')
        ], string="Product Model",
        default='1',
        required=True)
    pdt_operation = fields.Selection(
        [
            # ('1', 'Product Creation'),
            ('2', 'Image Updation')],
        string="Product Operation",
        default='2',
        required=True)
    search_field = fields.Selection(
        [
            ('barcode', 'barcode'),
            ('default_code', 'default_code - SKU'),
            ('code', 'Manufacture code'),
        ],
        string="Buscar por",
        default='barcode',
        required=True
        )
    url = fields.Char('URL', required=True)
    file = fields.Binary('File to import', required=True)
    info = fields.Text('Info')
    state = fields.Selection([('choose', 'choose'), ('done', 'done')], default="choose")

    def import_file(self):
        skip_header = True
        warn_msg_product = ''
        warn_msg_url = ''
        count_update = 0
        count_warn = 0
        # Generating of the excel file to be read by openpyxl
        file = base64.b64decode(self.file)
        excel_fileobj = TemporaryFile('wb+')
        excel_fileobj.write(file)
        excel_fileobj.seek(0)

        workbook = openpyxl.load_workbook(excel_fileobj)
        sheet_obj = workbook.active

        # Get the first sheet of excel file
        sheet = workbook[workbook.get_sheet_names()[0]]
        url = self.url

        if not url:
            raise Warning("Please provide and URL value.!")

        ## CONTROLO QUE LA URL TERMINE CON / SINO DA ERROR QUE NO ENCONTRÓ LA IMAGEN
        print ('url', url[-1:])
        if url[-1:] != '/':
            url += '/'

        for line in sheet.rows:
            image_found = False
            if skip_header:
                skip_header = False
                continue
            if line[1].value == None or line[1].value == ' ':
                continue
            product = str(line[0].value).replace(u'\xa0', '')
            image_path = url + str(line[1].value).replace(u'\xa0', '')
            _logger.info('image_path %s'%(image_path))
            if "http://" in image_path or "https://" in image_path:
                for extension in EXTENSIONES:
                    # print (extension)
                    try:
                        image_path_extension = "%s%s" % (image_path, extension)
                        _logger.info('image_path_extension %s', image_path_extension)
                        link = urllib.request.urlopen(image_path_extension).read()
                        image_base64 = base64.encodestring(link)
                        image_found = True
                        break
                    except:
                        continue
                if not image_found:
                    count_warn += 1
                    warn_msg_url += "Imagen no encontrada %s.[png | jpg | jpeg | PNG | JPG | JPEG]\n" % (
                        image_path)
                    continue
                product_obj = self.env[self.product_model]# product template o manufacture
                search_field = self.search_field # barcode, default_code o code
                args = [(search_field, 'ilike', product)]
                product_id = product_obj.search(args)

                if self.product_model in ['product.template']:
                    vals = {
                        'image_medium': image_base64,
                    }
                else:
                    vals = {
                        'logo': image_base64,
                    }
                if self.pdt_operation == '2' and product_id:
                    count_update += 1
                    product_id.write(vals)
                elif not product_id and self.pdt_operation == '2':
                    count_warn += 1
                    # warn_msg_product += "No se pudo encontrar el producto %s %s\n" % (product, str(args))
                    warn_msg_product += "No se pudo encontrar el producto %s\n" % (product)

            # else:
            #     try:
            #         with open(image_path, 'rb') as image:
            #             image_base64 = image.read().encode("base64")
            #             if self.product_model == '1':
            #                 product_obj = self.env['product.template']
            #             else:
            #                 product_obj = self.env['product.product']
            #             product_id = product_obj.search([(self.search_field, '=', product)])
            #             vals = {
            #                 'image_medium': image_base64,
            #                 # 'name': product,
            #             }
            #             if self.pdt_operation == '1' and not product_id:
            #                 product_obj.create(vals)
            #             elif self.pdt_operation == '1' and product_id:
            #                 product_id.write(vals)
            #             elif self.pdt_operation == '2' and product_id:
            #                 product_id.write(vals)
            #             elif not product_id and self.pdt_operation == '2':
            #                 raise Warning("Could not find the product '%s'" % product)
            #     except IOError:
            #         raise Warning("Could not find the image '%s' - please make sure it is accessible to this script" %
            #                       product)
        msg = '%s%s\n\nCantidad de imagenes importadas %s.\nCantidad de advertencias:%s'%(
            warn_msg_url, warn_msg_product, count_update, count_warn)
        self.state = 'done'
        self.info = msg
        view_id = self.env['ir.ui.view'].search([('model', '=', 'import.product_image')])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.product_image',
            'name': _('Importar imagenes'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
            'nodestroy': True,
            'context': {}
        }


