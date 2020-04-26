from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    barcode_id = fields.Many2one('product.barcode')

    @api.onchange('product_tmpl_id', 'applied_on')
    def onchange_product_tmpl_id(self):
        self.barcode_id = False
