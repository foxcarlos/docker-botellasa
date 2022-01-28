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


class SomethingCase(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(SomethingCase, self).setUp(*args, **kwargs)

    def tearDown(self, *args, **kwargs):

        return super(SomethingCase, self).tearDown(*args, **kwargs)

    def test_01_something(self):
        """TEST 01 First line of docstring appears in test logs.
        """
        self.assertEqual(1, 1)
