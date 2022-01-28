# -*- coding: utf-8 -*-


from odoo import fields, http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.website_sale.controllers import main
from odoo.addons.website.controllers.main import Website
from odoo.addons.web_editor.controllers.main import Web_Editor
from lxml import etree, html
import math
import os
import base64
import uuid
import werkzeug

main.PPG = 20
PPG = main.PPG

class WebsiteSale(WebsiteSale):

    def _get_product_price(self, price, pricelist):
        if price:
            request.cr.execute(
            'select id from product_template where list_price = %s' % price)
            prod_id = request.cr.fetchall()
            if prod_id:
                price = request.env['product.template'].browse(
                    prod_id[0][0]).with_context(pricelist=pricelist.id).price
                return price
        return 0

    def _get_product_filter_price(self, product_ids, min_val, max_val, pricelist):
        prod_ids = []
        for product in product_ids:
            price = product.with_context(pricelist=pricelist.id).price
            if price >= min_val and price <= max_val:
                prod_ids.append(product.id)
        return prod_ids

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        quantities_per_page = None
        max_val = 0
        min_val = 0
        custom_min_val = custom_max_val = 0
        quantities_per_page = request.env[
            'product.qty_per_page'].search([], order='sequence')

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = quantities_per_page[0].name if quantities_per_page else 20
        if not ppg:
            if quantities_per_page:
                ppg = quantities_per_page[0].name
            else:
                ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)
        pre_domain = self._get_search_domain(search, category, attrib_values)

        brand_ids = []
        if post.get('brand'):
            brand_list = request.httprequest.args.getlist('brand')
            brand_values = [[str(x) for x in v.split("-")]
                        for v in brand_list if v]
            brand_ids = list(set([int(v[1]) for v in brand_values]))
            if len(brand_ids) > 0:
                domain += [('product_brand_id', 'in', brand_ids)]

        tag_ids = []
        if post.get('tags'):
            tag_list = request.httprequest.args.getlist('tags')
            tag_values = [[str(x) for x in v.split("-")] for v in tag_list if v]
            tag_ids = list(set([int(v[1]) for v in tag_values]))
            if len(tag_ids) > 0:
                domain += [('tag_ids', 'in', tag_ids)]

        ######### Variedades
        variedad_ids = []
        if post.get('variedades'):
            variedad_list = request.httprequest.args.getlist('variedades')
            variedad_values = [[str(x) for x in v.split("-")]
                        for v in variedad_list if v]
            variedad_ids = list(set([int(v[1]) for v in variedad_values]))
            if len(variedad_ids) > 0:
                domain += [('variedad_id', 'in', variedad_ids)]
        ##### fin variedades
        ######### country
        country_ids = []
        if post.get('countries'):
            country_list = request.httprequest.args.getlist('countries')
            country_values = [[str(x) for x in v.split("-")]
                        for v in country_list if v]
            country_ids = list(set([int(v[1]) for v in country_values]))
            if len(country_ids) > 0:
                domain += [('country_id', 'in', country_ids)]
        # ##### fin country
        ######### region
        region_ids = []
        if post.get('regions'):
            region_list = request.httprequest.args.getlist('regions')
            region_values = [[str(x) for x in v.split("-")]
                        for v in region_list if v]
            region_ids = list(set([int(v[1]) for v in region_values]))
            if len(region_ids) > 0:
                domain += [('region_id', 'in', region_ids)]
        # ##### fin region
        ######### zona
        zona_ids = []
        if post.get('zonas'):
            zona_list = request.httprequest.args.getlist('zonas')
            zona_values = [[str(x) for x in v.split("-")]
                        for v in zona_list if v]
            zona_ids = list(set([int(v[1]) for v in zona_values]))
            if len(zona_ids) > 0:
                domain += [('zona_id', 'in', zona_ids)]
        ###### fin zona
        ######### state
        provincia_ids = []
        if post.get('provincias'):
            provincia_list = request.httprequest.args.getlist('provincias')
            provincia_values = [[str(x) for x in v.split("-")]
                        for v in provincia_list if v]
            provincia_ids = list(set([int(v[1]) for v in provincia_values]))
            if len(provincia_ids) > 0:
                domain += [('state_id', 'in', provincia_ids)]
        ###### fin state
        ######### puntajes
        puntajes = []
        puntajes_ids = []
        if post.get('puntajes'):
            puntaje_list = request.httprequest.args.getlist('puntajes')
            for punt in puntaje_list:
                domain += [(punt, '!=', 0)]
            puntajes_ids = puntaje_list
        puntajes = [
            ('puntaje_parker', 'Parker'),
            ('puntaje_wine_enthusiast', 'Wine Enthusiast'),
            ('puntaje_jancis_robinson', 'Jancis Robinson'),
            ('puntaje_wine_spectator', 'Wine Spectator'),
            ('puntaje_james_suckling', 'James Suckling'),
            ('puntaje_tim_atkin', 'Tim Atkin'),
            ('puntaje_international_wine_challenge', 'International Wine Challenge'),
            ('puntaje_decanter', 'Decanter'),
            ('puntaje_guia_penin', 'Guía Peñín'),
            ('puntaje_descorchados', 'Descorchados'),
        ]
        ###### fin puntajes
        


        if post.get('product_collection'):
            prod_collection_rec = request.env['multitab.configure'].search(
                [('id', '=', int(post.get('product_collection')))])
            if prod_collection_rec:
                prod_id_list = list({each_p.product_id.id for each_p in prod_collection_rec.product_ids})
                domain += [('id', 'in', prod_id_list)]

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        pre_search_product = Product.search(pre_domain)
        search_product = Product.search(domain)
        ###
        if search_product and search_product.ids:
            request.cr.execute(
                'select min(list_price),max(list_price) from product_template where id in %s', (tuple(search_product.ids),))
            min_max_vals = request.cr.fetchall()
            price_min_val = self._get_product_price(min_max_vals[0][0], pricelist)
            price_max_val = self._get_product_price(min_max_vals[0][1], pricelist)

            custom_min_val = min_val = round(price_min_val, 2) or 0
            if int(min_val) == 0:
                custom_min_val = min_val = 1
            custom_max_val = max_val = round(price_max_val, 2) or 1

            max_vals = min_max_vals[0][1] or 0

            if post.get('min_val') and post.get('max_val'):
                custom_min_val = float(post.get('min_val'))
                custom_max_val = float(post.get('max_val'))
                post.update(
                    {'attrib_price': '%s-%s' % (custom_min_val, custom_max_val)})
            else:
                post.update({'attrib_price': '%s-%s' % (min_val, max_val)})
        ###
        ###### precio
        if post.get('min_val') and post.get('max_val'):
            product_filter_price_ids = self._get_product_filter_price(search_product,
                                                                      float(post.get('min_val')),
                                                                      float(post.get('max_val')),
                                                                      pricelist)
            domain += [('id', 'in', product_filter_price_ids)]
            search_product = Product.search(domain)
        ###### fin precio
        
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))
        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
            brands = request.env['product.brand'].search(
                [('active','=',True),
                ('visible_slider','=',True),
                ('product_ids', 'in', search_product.ids)
                ])
            tags = request.env['product.tag'].search([('active','=',True), ('product_ids', 'in', search_product.ids)])
            variedades = request.env['product.variety'].search([
                ('product_ids', 'in', search_product.ids)]
            )
            countries = request.env['res.country'].search([
                ('product_ids', 'in', search_product.ids)]
            )
            regions = request.env['res.country.region'].search([
                ('product_ids', 'in', search_product.ids)]
            )
            zonas = request.env['res.country.zone'].search([
                ('product_ids', 'in', search_product.ids)]
            )
            provincias = request.env['res.country.state'].search([
                ('product_ids', 'in', search_product.ids)]
            )
        else:
            attributes = ProductAttribute.browse(attributes_ids)
            brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True)])
            tags = request.env['product.tag'].search([('active','=',True)])
            variedades = request.env['product.variety'].search([])
            countries = request.env['res.country'].search([])
            regions = request.env['res.country.region'].search([])
            zonas = request.env['res.country.zone'].search([])
            provincias = request.env['res.country.state'].search([])

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'brands': brands,
            'brand_set': brand_ids,
            ####
            'variedades': variedades,
            'variedad_set': variedad_ids,
            ####
            'countries': countries,
            'country_set': country_ids,
            ####
            'regions': regions,
            'region_set': region_ids,
            ####
            'zonas': zonas,
            'zona_set': zona_ids,
            ####
            'provincias': provincias,
            'provincia_set': provincia_ids,
            ####
            'puntajes': puntajes,
            'puntaje_set': puntajes_ids,
            ####
            'tags': tags,
            'tag_set': tag_ids,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'quantities_per_page': quantities_per_page,
            'add_more': True if request.website.shop_product_loader == 'infinite_loader' else False,
            'min_val': min_val,
            'max_val': max_val,
            'custom_min_val': custom_min_val,
            'custom_max_val': custom_max_val,
            'floor': math.floor,
            'ceil': math.ceil,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)


    @http.route(['/shop/load_next_products'], type="http", auth="public", website=True)
    def load_next_products(self, category='', loaded_products=0, search='', ppg=0, **post):
        if ppg:
            Category = request.env['product.public.category']

            attrib_list = request.httprequest.args.getlist('attrib[]')
            attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
            attributes_ids = {v[0] for v in attrib_values}
            attrib_set = {v[1] for v in attrib_values}

            domain = self._get_search_domain(search, category, attrib_values)

            brand_ids = []
            if post.get('brand[]'):
                brand_list = request.httprequest.args.getlist('brand[]')
                brand_values = [[str(x) for x in v.split("-")]
                            for v in brand_list if v]
                brand_ids = list(set([int(v[1]) for v in brand_values]))
                if len(brand_ids) > 0:
                    domain += [('product_brand_id', 'in', brand_ids)]

            tag_ids = []
            if post.get('tags[]'):
                tag_list = request.httprequest.args.getlist('tags[]')
                tag_values = [[str(x) for x in v.split("-")] for v in tag_list if v]
                tag_ids = list(set([int(v[1]) for v in tag_values]))
                if len(tag_ids) > 0:
                    domain += [('tag_ids', 'in', tag_ids)]

            keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

            pricelist_context, pricelist = self._get_pricelist_context()

            request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

            url = "/shop"
            if search:
                post["search"] = search
            if attrib_list:
                post['attrib'] = attrib_list

            Product = request.env['product.template'].with_context(bin_size=True)

            search_product = Product.search(domain)
            website_domain = request.website.website_domain()
            categs_domain = [('parent_id', '=', False)] + website_domain
            if search:
                search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
                categs_domain.append(('id', 'in', search_categories.ids))
            else:
                search_categories = Category
            categs = Category.search(categs_domain)

            if category:
                url = "/shop/category/%s" % slug(category)

            product_count = len(search_product)
            #pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(domain, limit=int(ppg), offset=int(loaded_products), order=self._get_search_order(post))

            ProductAttribute = request.env['product.attribute']
            if products:
                # get all products without limit
                attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
                brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True), ('product_ids', 'in', search_product.ids)])
                tags = request.env['product.tag'].search([('active','=',True), ('product_ids', 'in', search_product.ids)])
            else:
                attributes = ProductAttribute.browse(attributes_ids)
                brands = request.env['product.brand'].search([('active','=',True),('visible_slider','=',True)])
                tags = request.env['product.tag'].search([('active','=',True)])

            layout_mode = request.session.get('website_sale_shop_layout_mode')
            if not layout_mode:
                if request.website.viewref('website_sale.products_list_view').active:
                    layout_mode = 'list'
                else:
                    layout_mode = 'grid'

            values = {
                'add_more': True if request.website.shop_product_loader == 'infinite_loader' else False,
                'products': products,
                #'pager': pager,
                'pricelist': pricelist,
                'keep': keep,
                'brands': brands,
                'brand_set': brand_ids,
                'tags': tags,
                'tag_set': tag_ids,
                'layout_mode': layout_mode,
            }
            return request.render('atharva_theme_general.newly_loaded_products', values)
        else:
            return None
