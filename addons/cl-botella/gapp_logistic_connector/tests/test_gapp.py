# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

#    Forma de correr el test
#    -----------------------
#
#   Definir un subpackage tests que será inspeccionado automáticamente por
#   modulos de test los modulos de test deben enpezar con test_ y estar
#   declarados en el __init__.py, como en cualquier package.
#
#   Hay que crear una base de datos no importa el nombre pero se sugiere
#   [nombre cliente]_test_[nombre modulo] que debe estar vacia pero con el
#   modulo que se quiere testear instalado.
#
#   Debe tener usuario admin y password admin y demo data
#
#   Arrancar el test con:
#
#   oe -Q gapp_logistic_connector -c botella -d botella_test
#

from odoo.tests.common import TransactionCase


class TestCase(TransactionCase):

    def test_01_split_file(self):
        """ TESTEAR todos los productos distintos
        """
        # articulo original
        line1 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;00003020191505;000050.000;548795600;;000050.000\r\n'  # noqa
        # mismo articulo debe ir en otro archivo
        line2 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;10003020191505;000050.000;548795600;;000050.000\r\n'  # noqa
        # mismo articulo otro lote debe ir en otro archivo
        line3 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;20003020191505;000050.000;548795600;;000050.000\r\n'  # noqa
        # distinto articulo y lote se queda en el mismo archivo
        line4 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;30003020191505;000050.000;548795600;;000050.000\r\n'  # noqa

        file = list()
        file.append(line1)
        file.append(line2)
        file.append(line3)
        file.append(line4)

        sp = self.env['stock.picking']

        result0 = sp.split_file(file)
        self.assertEqual(len(result0), 1)

    def test_02_split_file(self):
        """ TESTEAR se generan dos archivos
        """
        # articulo original
        line1 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;00003020191505;000050.000;548795600;;000050.000\r\n'  # noqa
        # mismo articulo debe ir en otro archivo
        line2 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;10003020191505;000050.000;548795600;;000050.000\r\n'  # noqa
        # mismo articulo otro lote debe ir en otro archivo
        line3 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;00003020191505;000050.000;548795600;;000050.000\r\n'  # noqa
        # distinto articulo y lote se queda en el mismo archivo
        line4 = b'RANDOM;A;001;0000000014;0000000123;12/12/2019;Guerrini;1405;Diaz Velez 4565;;;;;30003020191505;000050.000;548795600;;000050.000\r\n'  # noqa

        file = list()
        file.append(line1)
        file.append(line2)
        file.append(line3)
        file.append(line4)

        sp = self.env['stock.picking']

        result0 = sp.split_file(file)[0]
        result1 = sp.split_file(file)[1]

        self.assertTrue(result0 == [line1, line2, line4])
        self.assertTrue(result1 == [line3])
