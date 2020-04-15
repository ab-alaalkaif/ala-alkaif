from odoo.osv import expression
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCustom(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description=search_in_description)
        if not request.website.warehouse_id:
            return domain
        product_ids = request.env['product.product'].search([('website_published', '=', True), ('website_id', '=', request.website.id)])
        product_ids = product_ids.with_context(warehouse=request.website.warehouse_id.id).filtered(lambda r: r.virtual_available > 0)
        return expression.AND([domain, [('id', 'in', product_ids.ids)]])
