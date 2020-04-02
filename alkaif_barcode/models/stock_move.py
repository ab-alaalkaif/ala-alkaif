from odoo import api, fields, models, tools, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    barcode_id = fields.Many2one("product.barcode")

    @api.onchange('barcode_id')
    def onchange_barcode(self):
        for move in self:
            if move.barcode_id:
                move.price_unit = move.barcode_id.unit_price
                move.product_uom_qty = 1
                move.product_id = move.barcode_id.product_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        super().onchange_product_id()
        if self.barcode_id:
            self.product_uom = self.barcode_id.product_uom_id
