from odoo import api, fields, models, tools, _
from odoo.addons.website.models import ir_http


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_ids = fields.One2many('product.barcode', 'product_template_id')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_cart_qty(self):
        website = ir_http.get_request_website()
        if not website:
            self.cart_qty = 0
            return
        cart = website.sale_get_order()
        for product in self:
            qty = 0
            for line in cart.order_line.filtered(lambda p: p.product_id.id == product.id):
                qty += line.product_uom_qty * line.product_uom.factor_inv
            product.cart_qty = qty
