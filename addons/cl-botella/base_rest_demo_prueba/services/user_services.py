from odoo.addons.base_rest.components.service import to_bool, to_int
from odoo.addons.component.core import Component


class UsuariosService(Component):
    _inherit = "base.rest.service"
    _name = "users.service"
    _usage = "users"
    _collection = "base.rest.demo.prueba.public.services"
    _description = "This module is for users: user.services"


#GET
    def get(self, _id):
        """
        Trae info del usuario a partir de un ID
        """
        return self._to_json(self._get(_id))

#CREATE
    def create(self, **params):
        """
        Crea un nuevo usuario. CAMPOS OBLIGATORIOS: email, mobile, password, cuit
        """
        ## cuit, email, mobil, proveedor, vendedor o mayorista, cuit empresa, cuit proveedor, password
        group_portal = self.env.ref('base.group_portal')
        group_wholesaler = self.env.ref('botella_product.group_botellasas_wholesaler')
        group_supplier = self.env.ref('botella_product.group_botellasas_supplier')
        group_agent = self.env.ref('botella_product.group_botellasas_agent')
        ## params lo deberia separar en 2 diccionarios, uno de alta de usuario y otro para write de partner
        print ('params', params)
        vals_user = {
            'name': params['email'],
            'login': params['email'],
            'password': params['password'],
        }
        group_ids = []
        user = self.env["res.users"].create(vals_user)
        # user.write({'active': True, 'groups_id': [(6, 0, [group_portal.id])]})
        user.write({'active': True})
        group_ids.append(group_portal.id)
        ## aca debo hacer un read de partner_id
        ## y actualizar datos
        partner_id = user.read(['partner_id'])[0]['partner_id'][0]
        partner = self.env['res.partner'].browse(partner_id)
        partner.email = params['email']
        cuit_id = self.env['res.partner.id_category'].search([('code', '=', 'CUIT')])
        print (cuit_id)
        partner.main_id_category_id = cuit_id.id
        partner.main_id_number = params['cuit']
        partner.mobile = params['mobile']
        # si es cons. final es person y customer
        partner.company_type = 'person'
        partner.customer = True
        if params['seller']: # si es vendedor / cobrador entonces agent
            partner.agent = True
            group_ids.append(group_agent.id)
        if params['wholesaler'] or params['provider']: # si es mayorista y/o proveedor creo el partner de la compañia
            vals_company_partner = {
                'name': params['email'],
                'company_type': 'company',
                'main_id_category_id': cuit_id.id,
                'main_id_number': params['cuitCompany']
            }
            if params['wholesaler']:
                group_ids.append(group_wholesaler.id)
            else:
                vals_company_partner['customer'] = False # hago esto porque por defecto es true
            if params['provider']:
                vals_company_partner['supplier'] = True
                group_ids.append(group_supplier.id)
            print ('vals_company_partner', vals_company_partner)
            company_partner = self.env["res.partner"].create(vals_company_partner)
            # relaciono el partner consumidor final con el de la compañia
            partner.parent_id = company_partner.id
            # TODO: property_product_pricelist voy a tener que setear esto cuando tenga las tarifas de mayorista
            print ('group_ids', group_ids)
            user.write({'groups_id': [(6, 0, group_ids)]})

        return self._to_json(user)

#SEARCH
    def search(self, email):
        """
        Trae info del usuario a partir del email
        """
        users = self.env["res.users"].search([('login', '=', email)])
        filas = []
        answer = {"count": len(users), "rows": filas}
        for user in users:
            filas.append(self._to_json(user))
        return answer

    def _update_address(self, user, params):
        if 'street' in params:
            user.sudo().partner_id.street = params['street']
        if 'numero' in params:
            user.sudo().partner_id.street_number = params['numero']
        if 'piso' in params:
            user.sudo().partner_id.street_number2 = params['piso']
        if 'zip' in params:
            user.sudo().partner_id.zip = params['zip']
        if 'city' in params:
            user.sudo().partner_id.city = params['city']
        if 'state_id' in params:
            user.sudo().partner_id.state_id = params['state_id']['id']

#UPDATE
    def update(self, _id, **params):
        """
        Actualiza informacion de usuario, se debe pasar como parametro el ID
        """
        # name = False
        # nombre = 'nombre' in params and params['nombre'] or False
        # apellido = 'apellido' in params and params['apellido'] or False
        # if nombre and apellido:
        #     name = "%s, %s"%(apellido, nombre)
        # elif nombre and not apellido:
        #     name = nombre
        # elif apellido and not nombre:
        #     name = apellido
        print ('params', params)
        user = self._get(_id)
        if 'name' in params:
            user.sudo().write({'name': params['name']})
        self._update_address(user, params)
        if 'mobile' in params:
            user.sudo().partner_id.mobile = params['mobile']
        if 'email' in params:
            user.sudo().partner_id.email = params['email']
        if 'afip_responsability_type_id' in params:
            user.sudo().partner_id.afip_responsability_type_id = params['afip_responsability_type_id']['id']
        if 'birthdate_date' in params:
            user.sudo().partner_id.birthdate_date = params['birthdate_date']
        if 'cuit' in params:
            cuit_id = self.env['res.partner.id_category'].sudo().search([('code', '=', 'CUIT')])
            print (cuit_id)
            user.sudo().partner_id.main_id_category_id = cuit_id.id
            user.sudo().partner_id.main_id_number = params['cuit']
        ## Datos de la compañía
        if 'nameCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.name = params['nameCompany']
        if 'streetCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.street = params['streetCompany']
        # if 'cuitCompany' in params and user.partner_id.parent_id:
        #     user.partner_id.parent_id.name = params['cuitCompany']
        if 'numberCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.sudo().street_number = params['numberCompany']
        if 'floorCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.street_number2 = params['floorCompany']
        if 'zipCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.zip = params['zipCompany']
        if 'cityCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.city = params['cityCompany']
        if 'emailCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.email = params['emailCompany']
        if 'mobileCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.mobile = params['mobileCompany']
        if 'stateCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.state_id = params['stateCompany']['id']
        if 'afipResponsabilityTypeCompany' in params and user.sudo().partner_id.parent_id:
            user.sudo().partner_id.parent_id.afip_responsability_type_id = params['afipResponsabilityTypeCompany']['id']
        if user.sudo().partner_id.parent_id: # si tiene company vuelvo a escribir la direccion porque la del company la pisa
            user.sudo().partner_id.type = 'delivery'
            self._update_address(user, params)
        return self._to_json(user)

##############

#GET
    def _to_json(self, user):
        answer = {
            "email": user.sudo().login,
            "name": user.sudo().name,
            "id": user.sudo().id,
            "cuit": user.sudo().partner_id.main_id_number and user.sudo().partner_id.main_id_number or '',
            "mobile": user.sudo().partner_id.mobile and user.sudo().partner_id.mobile or '',
            "seller": user.sudo().partner_id.agent,
            "wholesaler": user.sudo().partner_id.parent_id.customer and True or False,
            "provider": user.sudo().partner_id.parent_id.supplier and True or False,
            # "password": user.password
            }
        return answer

    def _get(self, _id):
        return self.env["res.users"].browse(_id)

#CREATE
    def _validator_create(self):
        answer = {
            "password": {"type": "string", "nullable": True},
            "cuit": {"type": "string", "nullable": True}, ## main_id_number
            # main_id_category_id
            "email": {"type": "string", "nullable": True, "empty": False},
            "mobile": {"type": "string", "nullable": True},

            ## login va a ser email
            # "login": {"type": "string", "required": True, "empty": False},
            ## name null porque se completa con datos de afip en 2do paso de registro
            "name": {"type": "string", "nullable": True},
            "nombre": {"type": "string", "nullable": True},
            "apellido": {"type": "string", "nullable": True},
            ## campos de partner
            "wholesaler": {"type": "boolean"}, ## mayorista
            "provider": {"type": "boolean"}, ## proveedor / supplier
            "seller": {"type": "boolean"}, ## vendedor / cobrador / agent
            "cuitCompany": {"type": "string", "nullable": True}, ## street_name

            ## mayorista
            ## cuit empresa
            ## cuit proveedor
            ## campos update
            "street": {"type": "string", "nullable": True}, ## street_name
            "numero": {"type": "string", "nullable": True}, ## street_number
            "piso": {"type": "string", "nullable": True}, ## street_number2
            "zip": {"type": "string", "nullable": True},
            "city": {"type": "string", "nullable": True},
            "state_id": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
            "afip_responsability_type_id": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
            "birthdate_date": {"type": "string", "nullable": True},
            ## Campos del company
            "nameCompany": {"type": "string", "nullable": True},
            "streetCompany": {"type": "string", "nullable": True},
            "cuitCompany": {"type": "string", "nullable": True},
            "numberCompany": {"type": "string", "nullable": True},
            "floorCompany": {"type": "string", "nullable": True},
            "zipCompany": {"type": "string", "nullable": True},
            "cityCompany": {"type": "string", "nullable": True},
            "stateCompany": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
            "afipResponsabilityTypeCompany": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer", "coerce": to_int, "nullable": True},
                    "name": {"type": "string"},
                },
            },
            "emailCompany": {"type": "string", "nullable": True},
            "mobileCompany": {"type": "string", "nullable": True},
            }
        return answer


#SEARCH
    def _validator_search(self):
        return {
                "email": {"type": "string", "nullable": False, "required": True}
        }
    def _validator_return_search(self):
        return {
            "count": {"type": "integer", "required": True},
            "rows": {
                "type": "list",
                "required": True,
                "schema": {"type": "dict", "schema": self._validator_return_get()},
            },
        }
    def _validator_return_get(self):
        answer = self._validator_create()
        answer.update({"id": {"type": "integer", "required": True, "empty": False}})
        return answer




#UPDATE
    def _validator_update(self):
        answer = self._validator_create()
        return answer

    def _validator_return_update(self):
        return self._validator_return_get()


