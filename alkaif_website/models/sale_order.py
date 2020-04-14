from odoo import api, fields, models, tools, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        lines = super()._cart_find_product_line(product_id, line_id, **kwargs)
        if lines and kwargs.get('uom_id', False):
            return lines.filtered(lambda r: r.product_uom.id == int(kwargs.get('uom_id')))
        return lines
