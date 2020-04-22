import json

from odoo.http import request
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCustom(WebsiteSale):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        vals = sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            uom_id=kw.get('uom_id', False)
        )

        if kw.get('uom_id', False):
            line = request.env['sale.order.line'].browse(vals.get('line_id'))
            barcode_id = request.env['product.barcode'].sudo().search([('product_id', '=', int(product_id)),
                                                                       ('product_uom_id', '=', int(kw.get('uom_id', False)))
                                                                       ], limit=1)
            if line.exists() and barcode_id:
                line.sudo().write({
                    'product_uom': int(kw.get('uom_id', False)),
                    'price_unit': barcode_id.unit_price,
                    'barcode_id': barcode_id.id,
                    'barcode': barcode_id.name
                })

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        if not kw.get('country', False):
            kw.update({
                'country_id': str(request.env['res.country'].search([('code', '=', 'SA')]).id)
            })
        return super().address(**kw)

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super().checkout_form_validate(mode, all_form_values, data)
        error.pop('email', None)  # remove email key is it exists
        error.pop('city', None)  # remove city key is it exists
        return error, error_message
