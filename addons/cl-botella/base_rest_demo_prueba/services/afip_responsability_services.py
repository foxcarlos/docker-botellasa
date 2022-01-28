from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component


class AfipResponsabilityService(Component):
    _inherit = "base.rest.service"
    _name = "afip.responsability.service"
    _usage = "afip.responsability.public"
    _collection = "base.rest.demo.prueba.private.services"
    _description = "This module is for afip responsability: afip.responsability.public.services"

    def get(self, _id):
        """
        Trae informacion de  una responsabilidad de Afip a partir de un ID
        """
        return self._to_json(self._get(_id))
    def search(self):
        """
        Trae todas las responsabilidades de AFIP
        """
        afip_resp = self.env["afip.responsability.type"].search([])
        filas = []
        answer = {"count": len(afip_resp), "rows": filas}
        for data in afip_resp:
            filas.append(self._to_json(data))
        return answer
#GET  : #esto es lo que devuelve
    def _to_json(self, afip_resp):
        answer = {
            "id":afip_resp.id,
            "name": afip_resp.name,
        }
        return answer

    def _get(self, _id): 
        return self.env["afip.responsability.type"].browse(_id)
#CREATE  #aca hacemos las validaciones del tipo de dato y si es requerido o puede ser null.
    def _validator_create(self):
        answer = {
            "name": {"type": "string", "required": True, "empty": False},
        }
        return answer
#SEARCH  #aca validamos el campo por el que vamos a buscar.
    def _validator_search(self):
        return {}
#SEARCH: aca validamos lo que devuelve el search
    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }
#RETURN:  #aca validamos lo que devuelve el get.
    def _validator_return_get(self):
        answer = self._validator_create()
        answer.update({"id": {"type": "integer", "required": True, "empty": False}})
        return answer
#UPDATE #aca validamos la estructura del update
    def _validator_update(self):
        answer = self._validator_create()
        return answer
#UPDATE:  #aca validamos lo que devuelve el update
    def _validator_return_update(self):
        return self._validator_return_get()
