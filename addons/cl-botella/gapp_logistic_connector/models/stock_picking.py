# Copyright 2019 jeo Software
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import date
from odoo import models, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @staticmethod
    def split_file(file):
        """ llega en data una lista de todos los productos a enviar, hay que
            partirla en listas con el siguiente criterio:
            no se pueden repetir los productos, que es el item 13 de la lista
            line = lista con los elementos de una linea del archivo
            file = lista con las lineas de un archivo
            data = lista con todos los archivos
        """
        data = list()

        def get_default_code(line):
            """ dada una linea del archivo devuelve el codigo de producto
            """
            return line.split(b';')[13]

        def line_in_file(ln, file):
            """ dada una linea y un archivo devuelve True si el archivo
                contiene la linea
            """
            default_code = get_default_code(ln)
            for line in file:
                if default_code == get_default_code(line):
                    return True
            return False

        def insert_in_data(ln):
            """ Inserta la linea en un archivo en el que no esta, de manera
                que no se repita.
            """
            for file in data:
                if not line_in_file(ln, file):
                    file.append(ln)
                    return
            data.append([ln])

        for line in file:
            insert_in_data(line)

        return data

    def send_to_gapp(self):
        """ Enviar el archivo attachado a GAPP
        """

        template_id = self.env.ref(
            'gapp_logistic_connector.gapp_mail_template')

        # have model_description in template language
        lang = self.env.context.get('lang')
        if template_id and template_id.lang:
            lang = template_id._render_template(template_id.lang,
                                                'stock.picking', self.id)
        self = self.with_context(lang=lang)

        # obtengo una lista con los datos de cada linea de envio pueden estar
        # repetidos los productos porque hay dos lineas iguales o porque tienen
        # lotes distintos
        gapp_data = self.encode_data_file()

        # procesar los datos y devolver una lista de lineas que corresponde
        # a un solo archivo
        ids = []

        for ix, gapp_file in enumerate(self.split_file(gapp_data)):
            datas = b''.join(gapp_file)

            attachment = self.env['ir.attachment'].create({
                'name': self.data_filename(ix),
                'datas': base64.b64encode(datas),
                'datas_fname': self.data_filename(ix),
                'res_model': 'stock.picking',
                'res_id': self.id,
            })
            ids.append(attachment.id)

        template_id.attachment_ids = [(6, 0, ids)]
        gapp = self.env['res.partner'].search([('ref', '=', 'gapp')])

        if not gapp:
            raise exceptions.UserError('No existe el partner GAPP o no tiene '
                                       'cargada la referencia gapp')

        # enviar el mail con el attach
        template_id.sudo().send_mail(gapp.id,
                                     raise_exception=True,
                                     force_send=True)

    def data_filename(self, ix):
        """ Genera el nombre para el archivo GAPP
            NNNNNNNNN_DDMMYYYY
        """
        today = date.today()
        number = self.id * 100 + ix
        return '{:09}_{}.TXT'.format(number, today.strftime('%d%m%Y'))

    @staticmethod
    def encode_state(state_id):
        # el 564 es La Rioja y no esta en la spec.
        codes = {
            553: 'BA', 554: 'BUE', 555: 'CAT', 556: 'CHA', 557: 'CHU',
            558: 'COR', 559: 'CRR', 560: 'ENT', 561: 'FOR', 562: 'JUJ',
            563: 'PAM', 564: '???', 565: 'MEN', 566: 'MIS', 567: 'NEU',
            568: 'RIO', 569: 'SAL', 570: 'SNJ', 571: 'SNL', 572: 'SCR',
            573: 'SFE', 574: 'SES', 575: 'TIE', 576: 'TUC'
        }
        return codes.get(state_id, False)

    def encode_data_file(self):
        """ Codificar archivo para GAPP
        """
        datas = list()
        # chequear que cada linea tiene al menos un lote
        for line in self.move_lines:
            if not line.move_line_ids:
                raise exceptions.UserError('No hay lotes definidos para el '
                                           'producto %s' %
                                           line.product_id.name)

        for line in self.move_lines:
            for lot in line.move_line_ids:
                cols = list()

                # 1. Código del propietario del LOTE/ARCHIVO.
                cols.append('BOTELLA')

                # 2. Letra del comprobante que respalda el pedido. Ej:”A”
                origin = self.origin
                sale_order_obj = self.env['sale.order']
                so = sale_order_obj.search([('name', '=', origin)])
                if not so:
                    raise exceptions.UserError(_('No se puede encontrar la '
                                                 'orden de venta relacionada '
                                                 'con este envio.'))

                if not (so.invoice_ids and so.invoice_ids[0]):
                    raise exceptions.UserError(_('No se puede encontrar la '
                                                 'factura de venta que '
                                                 'respalda este envio.'))

                letter = so.invoice_ids[0].document_letter_name
                cols.append('{}'.format(letter))

                # 3. Centro Emisor (Uso Interno) Siempre = “001”
                cols.append('001')

                # 4. Numero de pedido. El numero que representa al pedido
                # del registro.
                cols.append('{:010}'.format(self.id))

                # 5. Código del cliente/sucursal a la que pertenece el pedido.
                ref = self.partner_id.ref
                try:
                    ref = int(ref)
                except:
                    raise exceptions.UserError(_('La referencia del cliente '
                                                 'debe ser un numero entero'))
                cols.append('{:010}'.format(ref))

                # 6. Es la fecha propuesta de entrega al cliente.
                dt = self.scheduled_date
                if dt:
                    cols.append('{}'.format(dt.strftime('%d/%m/%Y')))
                else:
                    cols.append('')

                # 7. Nombre o razón social asociado al campo 5, que representa
                # al destinatario del pedido.
                name = self.partner_id.name
                name = name.replace(';', ' ')
                cols.append('{}'.format(name))

                # 8. Código postal asociado a la dirección del destinatario.
                zipcode = self.partner_id.zip or ''
                zipcode = zipcode.replace(';', ' ')
                cols.append('{}'.format(zipcode))

                # 9. Nombre de la calle y altura asociado a la dirección del
                # destinatario.
                street = self.partner_id.street
                street = street.replace(';', ' ')
                if not street:
                    raise exceptions.UserError('El cliente %s no tiene '
                                               'direccion (calle y nro)' %
                                               self.partner_id.name)
                cols.append('{}'.format(street))

                # 10. Nombre de la localidad asociada a la dirección del
                # destinatario.
                city = self.partner_id.street2 or ''
                city += ' ' + (self.partner_id.state_id.name or '')
                city = city.replace(';', ' ')
                city = city.strip()
                if not city:
                    raise exceptions.UserError('El cliente %s no tiene '
                                               'localidad' %
                                               self.partner_id.name)
                cols.append('{}'.format(city))

                # 11. Código de provincia asociada a la dirección del
                # destinatario.
                provincia = self.encode_state(self.partner_id.state_id.id or
                                              False)
                if provincia:
                    cols.append('{}'.format(provincia))
                else:
                    cols.append('')

                # 12. Peso asociado a la cantidad de productos de la línea
                # actual del archivo. Ej: Si se solicitan 10 unidades  del
                # producto 000001, que el peso individual es 2.5 kilos, el
                # valor será = 25.000 (veinticinco con 3 ceros decimales).
                peso = lot.product_id.weight * lot.product_uom_qty
                if peso:
                    cols.append('{0:0.3f}'.format(peso))
                else:
                    cols.append('')

                # 13. Una observación asociada al pedido.
                obs = self.note or ''
                obs = obs.replace(';', ' ')
                cols.append('{}'.format(obs))

                # 14. Código del producto solicitado.
                default_code = lot.product_id.default_code
                default_code = default_code.replace(';', ' ')
                if default_code:
                    cols.append('{}'.format(default_code))
                else:
                    raise UserWarning('El producto %s no tiene '
                                      'codigo' % lot.product_id.name)

                # 15. Cantidad solicitada del producto en el registro vigente.
                qty = lot.product_uom_qty
                cols.append('{:010.3f}'.format(qty))

                # 16. Lote particular al cual debe pertenecer el producto
                # solicitado.

                lot_name = lot.lot_id.name
                if not lot_name:
                    lot_name = ''
                lot_name = lot_name.replace(';', ' ')
                cols.append('{}'.format(lot_name))

                # 17. Código seriado del producto solicitado. NO SE USA
                serial = ''
                cols.append('{}'.format(serial))

                # 18. Monto, Subtotal o importe que representa la cantidad
                # solicitada del producto en el registro. (Sin incluir IVA).

                # para hacer esto voy a la factura que representa este
                # movimiento y busco el precio unitario de este producto luego
                # lo multiplico por la cantidad de este lote
                monto = False
                invoice = so.invoice_ids[0]
                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.product_id.id == lot.product_id.id:
                        monto = lot.product_uom_qty * invoice_line.price_unit
                if monto:
                    cols.append('{:010.3f}'.format(monto))
                else:
                    cols.append('')

                line_data = ';'.join(cols)
                line_data = b'%s\r\n' % bytes(line_data, encoding='utf8')
                # datas += b'%s\r\n' % bytes(line_data, encoding='utf8')
                datas.append(line_data)

        return datas
