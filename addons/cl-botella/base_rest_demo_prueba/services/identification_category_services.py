from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component


class IdentificationCategoryService(Component):
    _inherit = "base.rest.service"
    _name = "identification.category.service"
    _usage = "identification.category.public"
    _collection = "base.rest.demo.prueba.private.services"
    _description = "This module is for identification category: identification.category.public.services"


#GET
    def get(self, _id):
        """
        Trae informacion de  una categoria de identificacion principal a partir de un ID
        """
        return self._to_json(self._get(_id))
#SEARCH ALL
    def search(self):
        """
        Trae todas las categorias de identificacion principal
        """
        categ = self.env["res.partner.id_category"].search([])
        filas = []
        answer = {"count": len(categ), "rows": filas}
        for data in categ:
            filas.append(self._to_json(data))
        return answer


#GET   #esto es lo que devuelve
    def _to_json(self, id_categ):
        answer = {
            "id":id_categ.id,
            "name": id_categ.name,
        }
        return answer

    def _get(self, _id):
        return self.env["res.partner.id_category"].browse(_id)

#CREATE #aca hacemos las validaciones del tipo de dato y si es requerido o puede ser null.
    def _validator_create(self):
        answer = {
            "name": {"type": "string", "required": True, "empty": False},
        }
        return answer

#SEARCH  #aca validamos el campo por el que vamos a buscar.
    def _validator_search(self):
        return {}
#RETURN: #aca validamos lo que devuelve el search
    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }
#RETURN: #aca validamos lo que devuelve el get.
    def _validator_return_get(self):
        answer = self._validator_create()
        answer.update({"id": {"type": "integer", "required": True, "empty": False}})
        return answer
#UPDATE #aca validamos la estructura del update
    def _validator_update(self):
        answer = self._validator_create()
        return answer
#UPDATE: #aca validamos lo que devuelve el update
    def _validator_return_update(self):
        return self._validator_return_get()
