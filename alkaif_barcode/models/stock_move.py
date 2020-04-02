from odoo import api, fields, models, tools, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    barcode_id = fields.Many2one("product.barcode")
    barcode_scan = fields.Char()

    @api.onchange('barcode_scan')
    def onchange_barcode(self):
        for move in self:
            barcode = self.env['product.barcode'].search([('name', '=', move.barcode_scan)])
            if barcode:
                move.product_uom_qty = 1
                move.product_id = move.barcode_id.product_id
                move.barcode_id = barcode
                move.product_id = move.barcode_id.product_id  # this is not a mistake, it fixes a bug ... ... ...
            elif move.barcode_scan:
                product = self.env['product.template'].search([('barcode', '=', move.barcode_scan)])
                if product:
                    move.product_uom_qty = 1
                    move.product_id = product.product_variant_id
                    move.barcode_id = False

    @api.onchange('product_id')
    def onchange_product_id(self):
        super().onchange_product_id()
        if self.barcode_id:
            self.product_uom = self.barcode_id.product_uom_id
