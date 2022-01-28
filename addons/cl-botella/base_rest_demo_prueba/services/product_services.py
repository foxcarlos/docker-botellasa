from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component

class ProductService(Component):
    _inherit = "base.rest.service"
    _name = "product.service"
    _usage = "product"
    _collection = "base.rest.demo.prueba.private.services"
    _description = "This module is for product: product.services"


#GET
    def get(self, _id):
        """
        Trae informacion del producto a partir de un ID
        """
        return self._to_json(self._get(_id))


#CREATE
    def create(self, **params):
        """
        Crea un nuevo producto
        """
        params['name'] = params['long_description']
        product = self.env["product.template"].create(self._prepare_params(params))
        return self._to_json(product)

#SEARCH
    def search(self, name=False, categ_id=False):
        """
        Trae informacion del producto a partir de un NOMBRE
        """
        if name:
            products = self.env["product.template"].name_search(name)
            products = self.env["product.template"].browse([i[0] for i in products])
        if categ_id:
            products = self.env["product.template"].search([('public_categ_ids', 'in', int(categ_id))])
        filas = []
        answer = {"count": len(products), "rows": filas}
        for product in products:
            filas.append(self._to_json(product))
        return answer


#UPDATE
    def update(self, _id, **params):
        """
        Actualiza informacion de producto
        """
        product = self._get(_id)
        product.write(params)
        return self._to_json(product)

##############

#GET
    def _to_json(self, product): #esto es lo que devuelve
        tarifa_publica_botellasas = 1
        answer = {
            "id":product.id,
            "name": product.long_description and product.long_description or product.name,
            # "sale_ok": product.sale_ok,
            # "purchase_ok": product.purchase_ok,
            "barcode": product.barcode and product.barcode or '',
            # "standard_price": product.standard_price,
            # "lst_price": product.lst_price,
            "precio_cons_final": product.with_context(pricelist=tarifa_publica_botellasas).price,
            "rating": product.rating_get_stats(),
        }
        if product.product:
            answer["producto"] = product.product
        if product.area:
            answer["area"] = product.area
        if product.varietal_web:
            answer["variedad"] = product.varietal_web
        if product.enologo:
            answer["enologo"] = product.enologo
        if product.alcohol:
            answer["alcohol"] = product.alcohol
        if product.puntajes:
            answer["puntajes"] = product.puntajes
        if product.description:
            answer["descripcion"] = product.description
        if product.elaboracion_crianza_corta:
            answer["elaboracion_crianza"] = product.elaboracion_crianza_corta
        if product.notas_cata:
            answer["ficha_cata"] = product.notas_cata
        if product.maridaje:
            answer["maridaje"] = product.maridaje
        if product.product_brand_id:
            answer["brand"] = {
                "id": product.product_brand_id.id,
                "name": product.product_brand_id.name,
            }
        # if product.company_id:
        #     answer["company"] = {
        #         "id": product.company_id.id,
        #         "name": product.company_id.name,
        #     }

        # tipo
        if product.public_categ_ids:
            answer['tipo'] = product.public_categ_ids[0].name
        # bodega
        if product.product_brand_id.bodega_id:
            answer["bodega"] = product.product_brand_id.bodega_id.name
        # region
        if product.product_brand_id.bodega_id.region_id:
            answer["region"] = product.product_brand_id.bodega_id.region_id.name
        if product.product_brand_id.manufacter_id.region_id and not product.product_brand_id.bodega_id:
            answer["region"] = product.product_brand_id.manufacter_id.region_id.name
        # pais
        if product.product_brand_id.bodega_id.region_id.country_id:
            answer["pais"] = product.product_brand_id.bodega_id.region_id.country_id.name
        if product.product_brand_id.manufacter_id.country_id and not product.product_brand_id.bodega_id:
            answer["pais"] = product.product_brand_id.manufacter_id.country_id.name
        # Año
        for line in product.attribute_line_ids:
            if line.attribute_id.name == 'Año':
                answer["cosecha"] = line.value_ids.name
        if product.product_brand_id.historia_bodega_corta:
            answer["historia_bodega"] = product.product_brand_id.historia_bodega_corta
        # mesage
        messages = self.env['mail.message'].search([
            ('model', '=', 'product.template'),
            ('res_id', '=', product.id),
            ])
        msg_list = []
        answer['comentarios'] = {
            'message_counter': len(messages),
            'messages': msg_list
        }
        for msg in messages:
            msg_list.append({
                    'datetime': msg.date,
                    'body': msg.body,
                    'author': msg.author_id.name,
                    'rating_value': msg.rating_value,
                })
        return answer

    def _get(self, _id):
        return self.env["product.template"].browse(_id)

#CREATE
    def _validator_create(self): #aca hacemos las validaciones del tipo de dato y si es requerido o puede ser null.
        answer = {
            "name": {"type": "string", "required": True, "empty": False},
            # "sale_ok": {"type": "boolean", "required": True, "empty": False},
            # "purchase_ok": {"type": "boolean", "required": True, "empty": False},
            "barcode": {"type": "string", "nullable": True, "empty": True},
            # "standard_price": {"type": "float", "required": True, "empty": False},
            # "lst_price": {"type": "float", "required": True, "empty": False},
            "precio_cons_final": {"type": "float", "nullable": True},
            "brand": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string", "nullable": True},
                },
            },
            # "company": {
            #     "type": "dict",
            #     "schema": {
            #         "id": {"type": "integer","coerce": to_int,"required": True,"nullable": False,},
            #         "name": {"type": "string"},
            #     },
            # },
            "rating": {
                "type": "dict",
                "schema": {
                    "avg": {"type": "float" ,"nullable": True,},
                    "total": {"type": "integer","coerce": to_int,"nullable": True,},
                    "percent": {
                        "type": "dict",
                        "schema": {
                            1: {"type": "float" ,"nullable": True,},
                            2: {"type": "float" ,"nullable": True,},
                            3: {"type": "float" ,"nullable": True,},
                            4: {"type": "float" ,"nullable": True,},
                            5: {"type": "float" ,"nullable": True,},
                            6: {"type": "float" ,"nullable": True,},
                            7: {"type": "float" ,"nullable": True,},
                            8: {"type": "float" ,"nullable": True,},
                            9: {"type": "float" ,"nullable": True,},
                            10: {"type": "float" ,"nullable": True,},
                        }
                    }
                },
            },
            "comentarios": {
                "type": "dict",
                "schema": {
                    "message_counter": {"type": "integer","nullable": True,},
                    "messages": {
                        "type": "list",
                        "schema": {
                            "type": "dict",
                            "schema": {
                                "datetime": {"type": "datetime" ,"nullable": True,},
                                "body": {"type": "string" ,"nullable": True,},
                                "author": {"type": "string" ,"nullable": True,},
                                "rating_value": {"type": "float" ,"nullable": True,},
                            }
                        }
                    }
                },
            },
            "bodega": {"type": "string", "nullable": True},
            "producto": {"type": "string", "nullable": True},
            "area": {"type": "string", "nullable": True},
            "tipo": {"type": "string", "nullable": True},
            "cosecha": {"type": "string", "nullable": True},
            "variedad": {"type": "string", "nullable": True},
            "region": {"type": "string", "nullable": True},
            "pais": {"type": "string", "nullable": True},
            "enologo": {"type": "string", "nullable": True},
            "alcohol": {"type": "string", "nullable": True},
            "puntajes": {"type": "string", "nullable": True},
            "historia_bodega": {"type": "string", "nullable": True},
            "descripcion": {"type": "string", "nullable": True},
            "elaboracion_crianza": {"type": "string", "nullable": True},
            "ficha_cata": {"type": "string", "nullable": True},
            "maridaje": {"type": "string", "nullable": True},
            "rating_val": {"type": "float", "nullable": True},
        }
        return answer

    def _prepare_params(self, params): #aca simplemente validamos los parametros antes de crearlos.
        for key in ["brand", "company"]:
            if key in params:
                val = params.pop(key)
                if val.get("id"):
                    params["%s_id" % key] = val["id"]
        return params

#SEARCH
    def _validator_search(self): #aca validamos el campo por el que vamos a buscar.
        return {
                "name": {"type": "string", "nullable": True, "required": False},
                "categ_id": {"type": "string", "nullable": True, "required": False},
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
    def _validator_update(self): #aca validamos la estructura del update
        answer = self._validator_create()
        return answer

    def _validator_return_update(self): #aca validamos lo que devuelve el update
        return self._validator_return_get()
