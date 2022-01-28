from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component


class StateArgentinaService(Component):
    _inherit = "base.rest.service"
    _name = "state.argentina.service"
    _usage = "state.argentina.public"
    _collection = "base.rest.demo.prueba.private.services"
    _description = "This module is for states: state.argentina.public.services"


#GET  
    def get(self, _id): 
        """
        Trae informacion de provincias/estados a partir de un ID
        """
        return self._to_json(self._get(_id))

#SEARCH 
    def search(self, name): 
        """
        Trae informacion de provincias/estados a partir de un NOMBRE
        """
        states = self.env["res.country.state"].name_search(name)
        states = self.env["res.country.state"].browse([i[0] for i in states]) 
        filas = []
        answer = {"count": len(states), "rows": filas}
        for state in states:
            filas.append(self._to_json(state))
        return answer
 
#SEARCH ALL
    def search(self): 
        """
        Trae todas las provincias de Argentina
        """
        argentina = self.env["res.country"].name_search('Argentina')
        states = self.env["res.country.state"].search([('country_id', '=', argentina[0][0])]).ids
        states = self.env["res.country.state"].browse([i for i in states]) 
        filas = []
        answer = {"count": len(states), "rows": filas}
        for state in states:
            filas.append(self._to_json(state))          
        return answer   


############## 

#GET  
    def _to_json(self, state): #esto es lo que devuelve
        answer = {               
            "id":state.id,
            "name": state.name,                
        }   
        return answer

    def _get(self, _id):       
        return self.env["res.country.state"].browse(_id)

#CREATE
    def _validator_create(self): #aca hacemos las validaciones del tipo de dato y si es requerido o puede ser null.
        answer = {
            "name": {"type": "string", "required": True, "empty": False},
        }
        return answer

#SEARCH 
    def _validator_search(self): #aca validamos el campo por el que vamos a buscar.
        return {}

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
    def _validator_update(self): #aca validamos la estructura del update
        answer = self._validator_create()
        return answer

    def _validator_return_update(self): #aca validamos lo que devuelve el update
        return self._validator_return_get()
