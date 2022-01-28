##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"


    @api.multi
    def check_vat_tax(self):
        """For recs of argentinian companies with company_requires_vat (that
        comes from the responsability), we ensure one and only one vat tax is
        configured
        TODO: we could also integrate with so_type invoice journal id or
        with sale_checkbook_id
        """
        # por ahora, para no romper el install de sale_timesheet lo
        # desactivamos en la instalacion
        if self.env.context.get('install_mode'):
            return True
        for rec in self.filtered(
                lambda x: not x.display_type and
                x.company_id.localization == 'argentina' and
                x.company_id.company_requires_vat):
            print ('rec......', rec)
            print ('rec.tax_id', rec.tax_id)
            vat_taxes = rec.tax_id.filtered(
                lambda x:
                x.tax_group_id.tax == 'vat' and x.tax_group_id.type == 'tax')
            print ('\n\n\nvat_taxes', vat_taxes)
            if len(vat_taxes) != 1 and self.order_id.company_id.id == 2:
                ## esto me podria traerme problemas si el producto tiene otros imp. como impuesto interno
                # busco iva 21% de botellasas
                iva_venta_id = self.env['account.tax'].search([('name', '=', 'IVA Ventas 21%'),
                                                               ('company_id', '=', 2)])
                print ('iva_venta_id', iva_venta_id)
                rec.tax_id = iva_venta_id
                # raise UserError(_(
                #     'Debe haber un y solo un impuestos de IVA por línea. '
                #     'Verificar líneas con producto "%s"' % (
                #         rec.product_id.name)))

