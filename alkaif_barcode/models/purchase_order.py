from datetime import date

from odoo import api, fields, models, tools, _


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'barcodes.barcode_events_mixin']

    barcode_id = fields.Many2one('product.barcode', string='Add barcode')

    @api.onchange('barcode_id')
    def _on_change_barcode(self):
        for so in self:
            if so.barcode_id:
                so.on_barcode_scanned(so.barcode_id.name)
                so.barcode_id = False

    def on_barcode_scanned(self, barcode):
        barcode_id = self.env['product.barcode'].search([('name', '=', barcode)])
        if barcode_id:
            sol = self.order_line.filtered(lambda r: r.barcode_id.id == barcode_id.id)
            if sol:
                sol[0].product_qty += 1
            else:
                self.order_line.new({
                    'name': barcode_id.product_id.display_name,
                    'price_unit': barcode_id.unit_price,
                    'product_id': barcode_id.product_id.id,
                    'product_uom': barcode_id.product_uom_id.id,
                    'product_qty': 1.0,
                    'order_id': self.id,
                    'barcode_id': barcode_id.id,
                    'date_planned': date.today()
                })
        else:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)])
            if product_id:
                sol = self.order_line.filtered(lambda r: r.product_id.id == product_id.id)
                if sol:
                    sol[0].product_qty += 1
                else:
                    self.order_line.new({
                        'name': product_id.display_name,
                        'price_unit': product_id.list_price,
                        'product_id': product_id.id,
                        'product_uom': product_id.uom_id.id,
                        'product_qty': 1.0,
                        'order_id': self.id,
                        'date_planned': date.today()
                    })


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    barcode_id = fields.Many2one('product.barcode')
