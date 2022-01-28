import base64
from odoo import _
from odoo.exceptions import MissingError
from odoo.http import request
from odoo.addons.base_rest.components.service import skip_secure_response
from odoo.addons.component.core import Component


class ProductImageService(Component):
    _inherit = "base.rest.service"
    _name = "product.category.image.service"
    _usage = "product_category_image"
    _collection = "base.rest.demo.prueba.private.services"
    _description = """
        Servicio de imagen para categoria productos.
        Es utilizado para recuperar la imagen de la categoria del producto
        El acceso al servicio de imagen solo permite si esta autenticado.
        Si no está autenticado, vaya a <a href='/web/login'> Iniciar sesión </a>
    """

    @skip_secure_response
    def get(self, _id, size):
        """
        Obtener imagen de la categoria del producto
        """
        field = "image"
        if size == "small":
            field = "image_small"
        elif size == "medium":
            field = "image_medium"
        status, headers, content = self.env["ir.http"].binary_content(
            model="product.public.category", id=_id, field=field, env=self.env
        )
        if not content:
            raise MissingError(_("No image found for product category %s") % _id)
        image_base64 = base64.b64decode(content)
        headers.append(("Content-Length", len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status_code = status
        return response

    # Validator
    def _validator_get(self):
        return {
            "size": {
                "type": "string",
                "required": False,
                "default": "small",
                "allowed": ["small", "medium", "large"],
            }
        }
