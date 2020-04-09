from odoo.osv import expression
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCustom(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domain = super()._get_search_domain(search, category, attrib_values, search_in_description=search_in_description)
        if not request.website.warehouse_id:
            return domain
        location_id = request.website.warehouse_id.lot_stock_id.id
        product_ids = request.env['stock.quant'].search_read([('quantity', '>', 0),
                                                              '|', ('location_id', 'child_of', location_id),
                                                              ('location_id', '=', location_id)],
                                                             ['product_id'])
        uids = set(r.get('product_id')[0] for r in product_ids)
        return expression.AND([domain, [('id', 'in', list(uids))]])
