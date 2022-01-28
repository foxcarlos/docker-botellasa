# Copyright 2018 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.base_rest.controllers import main
from odoo.http import content_disposition, dispatch_rpc, request, \
    serialize_exception as _serialize_exception, Response
from odoo import http
from openerp.http import request
from odoo import fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.auth_signup.models.res_users import SignupError
import logging
_logger = logging.getLogger(__name__)
try:
    from pysimplesoap.client import SoapFault
except ImportError:
    SoapFault = None

class BaseRestDemoPublicApiController(main.RestController):
    _root_path = "/base_rest_demo_api/public/"
    _collection_name = "base.rest.demo.prueba.public.services"
    _default_auth = "public"


class BaseRestDemoPrivateApiController(main.RestController):
    _root_path = "/base_rest_demo_api/private/"
    _collection_name = "base.rest.demo.prueba.private.services"
    _default_auth = "user"

class ConsultaPadronAfip(http.Controller):
    @http.route('/base_rest_demo_api/padron_afip', type='json', auth="user", cors="*")
    def get_data_from_padron_afip(self, cuit):
        _logger.info('cuit %s'%(cuit))
        # GET COMPANY
        # if there is certificate for user company, use that one, if not
        # use the company for the first certificate found
        _logger.info('request.uid %s' % (request.uid))
        # company = request.env['res.users'].browse(request.uid).company_id
        ## Hardcodeo id de botellasas, porque al cambiar de compañia en la base de datos se pierden los certificados
        ## por ejemplo : cambio a crystal y dicha compañía no tiene certificados
        company_id = 2
        company = request.env['res.company'].browse(company_id)
        env_type = company._get_environment_type()
        try:
            certificate = company.get_key_and_certificate(
                company._get_environment_type())
        except Exception:
            certificate = request.env['afipws.certificate'].sudo().search([
                ('alias_id.type', '=', env_type),
                ('alias_id.company_id', '=', company_id),
                ('state', '=', 'confirmed'),
            ], limit=1)
            if not certificate:
                raise UserError(_(
                    'Not confirmed certificate found on database'))
            company = certificate.alias_id.company_id

        # consultamos a5 ya que extiende a4 y tiene validez de constancia
        # padron = company.get_connection('ws_sr_padron_a4').connect()
        padron = company.get_connection('ws_sr_padron_a5').connect()
        error_msg = _(
            'No pudimos actualizar desde padron afip al cuit %s.\n'
            'Recomendamos verificar manualmente en la página de AFIP.\n'
            'Obtuvimos este error: %s')
        try:
            padron.Consultar(cuit)
        except SoapFault as e:
            raise UserError(error_msg % (cuit, e.faultstring))
        except Exception as e:
            raise UserError(error_msg % (cuit, e))
        print (padron)
        print (padron.denominacion)

        if not padron.denominacion or padron.denominacion == ', ':
            raise UserError(error_msg % (cuit, 'La afip no devolvió nombre'))

        # porque imp_iva activo puede ser S o AC
        imp_iva = padron.imp_iva
        if imp_iva == 'S':
            imp_iva = 'AC'
        elif imp_iva == 'N':
            # por ej. monotributista devuelve N
            imp_iva = 'NI'

        vals = {
            'name': padron.denominacion,
            'tipo_persona': padron.tipo_persona,
            'tipo_doc': padron.tipo_doc,
            'dni': padron.dni,
            'estado_padron': padron.estado,
            'street': padron.direccion,
            'city': padron.localidad,
            'zip': padron.cod_postal,
            # 'actividades_padron': self.actividades_padron.search(
            #     [('code', 'in', padron.actividades)]).ids,
            'actividades_padron': padron.actividades,
            # 'impuestos_padron': self.impuestos_padron.search(
            #     [('code', 'in', padron.impuestos)]).ids,
            'impuestos_padron': padron.impuestos,
            'imp_iva_padron': imp_iva,
            # TODAVIA no esta funcionando
            # 'imp_ganancias_padron': padron.imp_ganancias,
            'monotributo_padron': padron.monotributo,
            'actividad_monotributo_padron': padron.actividad_monotributo,
            'empleador_padron': padron.empleador == 'S' and True,
            'integrante_soc_padron': padron.integrante_soc,
            'last_update_padron': fields.Date.today(),
        }
        ganancias_inscripto = [10, 11]
        ganancias_exento = [12]
        if set(ganancias_inscripto) & set(padron.impuestos):
            vals['imp_ganancias_padron'] = 'AC'
        elif set(ganancias_exento) & set(padron.impuestos):
            vals['imp_ganancias_padron'] = 'EX'
        elif padron.monotributo == 'S':
            vals['imp_ganancias_padron'] = 'NC'
        else:
            _logger.info(
                "We couldn't get impuesto a las ganancias from padron, you"
                "must set it manually")

        if padron.provincia:
            # depending on the database, caba can have one of this codes
            caba_codes = ['C', 'CABA', 'ABA']
            # if not localidad then it should be CABA.
            if not padron.localidad:
                state = request.env['res.country.state'].search([
                    ('code', 'in', caba_codes),
                    ('country_id.code', '=', 'AR')], limit=1)
            # If localidad cant be caba
            else:
                state = request.env['res.country.state'].search([
                    ('name', 'ilike', padron.provincia),
                    ('code', 'not in', caba_codes),
                    ('country_id.code', '=', 'AR')], limit=1)
            if state:
                vals['state_id'] = state.id

        if imp_iva == 'NI' and padron.monotributo == 'S':
            vals['afip_responsability_type_id'] = request.env.ref(
                'l10n_ar_account.res_RM').id
        elif imp_iva == 'AC':
            vals['afip_responsability_type_id'] = request.env.ref(
                'l10n_ar_account.res_IVARI').id
        elif imp_iva == 'EX':
            vals['afip_responsability_type_id'] = request.env.ref(
                'l10n_ar_account.res_IVAE').id
        else:
            _logger.info(
                "We couldn't infer the AFIP responsability from padron, you"
                "must set it manually.")

        print (vals)
        return vals

class Session(http.Controller):
    @http.route('/web/session/authenticate', type='json', auth="none", cors="*")
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()

class AuthSignupHomeApi(http.Controller):
    @http.route('/base_rest_demo_api/signup', type='json', auth='public', cors="*")
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        print ('qcontext', qcontext)
        print ('args', args)
        print ('kw', kw)
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                session = self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                # return self.web_login(*args, **kw)
                return session
            except UserError as e:
                # qcontext['error'] = e.name or e.value
                raise ValidationError(_("%s"%(e.name or e.value)))
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    # qcontext["error"] = _("Another user is already registered using this email address.")
                    raise ValidationError(_("Another user is already registered using this email address."))
                else:
                    _logger.error("%s", e)
                    # qcontext['error'] = _("Could not create a new account.")
                    raise ValidationError(_("Could not create a new account."))
        print ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('passwordConfirm'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        session = self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()
        return session

    def _signup_with_values(self, token, values):
        print ('values', values)
        values['name'] = values['login']
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        if not uid:
            raise SignupError(_('Authentication Failed.'))
        return request.env['ir.http'].session_info()

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        print ('request.params', request.params)
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
        }
