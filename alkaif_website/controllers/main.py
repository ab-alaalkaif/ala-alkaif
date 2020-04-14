import json

from odoo.osv import expression
from odoo.http import request
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCustom(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description=search_in_description)
        if not request.website.warehouse_id:
            return domain
        product_ids = request.env['product.product'].search([('website_published', '=', True), ('website_id', '=', request.website.id)])
        product_ids = product_ids.with_context(warehouse=request.website.warehouse_id.id).filtered(lambda r: r.virtual_available > 0)
        return expression.AND([domain, [('id', 'in', product_ids.ids)]])

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
            barcode_id = request.env['product.barcode'].search([('product_id', '=', int(product_id)), ('product_uom_id', '=', int(kw.get('uom_id', False)))])
            if line.exists() and barcode_id:
                line.write({
                    'product_uom': int(kw.get('uom_id', False)),
                    'price_unit': barcode_id.unit_price,
                    'barcode_id': barcode_id.id,
                    'barcode': barcode_id.name
                })

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")
