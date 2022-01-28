from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

class ProductCategoryService(Component):
    _inherit = "base.rest.service"
    _name = "product.category.service"
    _usage = "product.public.category"
    _collection = "base.rest.demo.prueba.private.services"
    _description = "This module is for category: product.public.category.services"


#GET
    def get(self, _id):
        """
        Trae informacion de categorias -de productos- a partir de un ID
        """
        return self._to_json(self._get(_id))


#SEARCH ALL
    def search(self, categoria_padre):
        """
        Trae todas las categorias -de los productos, 999 para las categ. padres.
        """
        if categoria_padre == '999':
            categoria_padre = False
        else:
            categoria_padre = int(categoria_padre)
        args = ('parent_id', '=', categoria_padre)
        categories = self.env["product.public.category"].search([args], order="id")
        filas = []
        answer = {"count": len(categories), "rows": filas}
        for category in categories:
            filas.append(self._to_json(category))
        return answer

##------------

#GET
    def _to_json(self, product):
    #esto es lo que devuelve
        answer = {
            "id":product.id,
            "name": product.name,
        }
        if product.parent_id:
            answer["parent_id"] = {
                "id": product.parent_id.id,
                "name": product.parent_id.name,
            }
        return answer

    def _get(self, _id):
        return self.env["product.public.category"].browse(_id)

#CREATE
    def _validator_create(self): #aca hacemos las validaciones del tipo de dato y si es requerido o puede ser null.
        answer = {
            "name": {"type": "string", "required": True, "empty": False},
            "parent_id": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
        }
        return answer

    # def _prepare_params(self, params): #aca simplemente validamos los parametros antes de crearlos.
    #     for key in ["brand", "company"]:
    #         if key in params:
    #             val = params.pop(key)
    #             if val.get("id"):
    #                 params["%s_id" % key] = val["id"]
    #     return params

#SEARCH
    def _validator_search(self): #aca validamos el campo por el que vamos a buscar.
        return {
                "categoria_padre": {"type": "string", "nullable": False, "required": True}
        }

    def _validator_return_search(self): #aca validamos lo que devuelve el search
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }
    def _validator_return_get(self): #aca validamos lo que devuelve el get.
        answer = self._validator_create()
        answer.update({"id": {"type": "integer", "required": True, "empty": False}})
        return answer


#UPDATE
    # def _validator_update(self): #aca validamos la estructura del update
    #     answer = self._validator_create()
    #     return answer

    # def _validator_return_update(self): #aca validamos lo que devuelve el update
    #     return self._validator_return_get()
