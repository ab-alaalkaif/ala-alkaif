from odoo import api, fields, models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        res = super()._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)
        return res.filtered(lambda r: not r.barcode_id)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    barcode_id = fields.Many2one('product.barcode')

    @api.onchange('product_tmpl_id', 'applied_on')
    def onchange_product_tmpl_id(self):
        self.barcode_id = False
