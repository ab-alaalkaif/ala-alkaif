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
                move.product_uom = move.barcode_id.product_uom_id
                move.product_id = move.barcode_id.product_id
