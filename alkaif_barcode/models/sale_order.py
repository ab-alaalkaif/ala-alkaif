from odoo import api, fields, models, tools, _


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        barcode_id = self.env['product.barcode'].search([('name', '=', barcode)])
        if barcode_id:
            sol = self.order_line.filtered(lambda r: r.barcode_id.id == barcode_id.id)
            if sol:
                sol[0].product_uom_qty += 1
            else:
                self.order_line.new({
                    'name': barcode_id.product_id.display_name,
                    'price_unit': barcode_id.unit_price,
                    'discount': 0.0,
                    'product_id': barcode_id.product_id.id,
                    'product_uom': barcode_id.product_uom_id.id,
                    'product_uom_qty': 1.0,
                    'order_id': self.id,
                    'barcode_id': barcode_id.id
                })
        else:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)])
            if product_id:
                sol = self.order_line.filtered(lambda r: r.product_id.id == product_id.id)
                if sol:
                    sol[0].product_uom_qty += 1
                else:
                    self.order_line.new({
                        'name': product_id.display_name,
                        'price_unit': product_id.list_price,
                        'discount': 0.0,
                        'product_id': product_id.id,
                        'product_uom': product_id.uom_id.id,
                        'product_uom_qty': 1.0,
                        'order_id': self.id
                    })


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    barcode_id = fields.Many2one('product.barcode')

    @api.onchange('barcode_id')
    def _on_change_barcode(self):
        if self.barcode_id:
            self.product_id = self.barcode_id.product_id

    def product_id_change(self):
        res = super().product_id_change()
        if self.barcode_id:
            self.update({
                'price_unit': self.barcode_id.unit_price,
                'product_uom': self.barcode_id.product_uom_id,
            })
        return res

    def product_uom_change(self):
        super().product_uom_change()
        if self.barcode_id:
            self.update({
                'price_unit': self.barcode_id.unit_price,
                'product_uom': self.barcode_id.product_uom_id,
            })