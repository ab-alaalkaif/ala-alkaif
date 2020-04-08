from odoo import api, fields, models, tools, _


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        company_rec = self.env['res.company']._find_company_from_partner(self.partner_id.id)
        barcode_id = self.env['product.barcode'].search([('name', '=', barcode)])
        if barcode_id:
            sol = self.order_line.filtered(lambda r: r.barcode_id.id == barcode_id.id)
            self.create_sale_order_line(company_rec, barcode_id.product_id, sol, barcode_id=barcode_id)
        else:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)])
            if product_id:
                sol = self.order_line.filtered(lambda r: r.product_id.barcode == barcode)
                self.create_sale_order_line(company_rec, product_id, sol)

    def create_sale_order_line(self, company_rec, product_id, sol, barcode_id=False):
        if sol:
            sol[0].product_uom_qty += 1
        else:
            taxes = product_id.taxes_id
            company_taxes = [tax_rec for tax_rec in taxes if tax_rec.company_id.id == company_rec.id]
            vals = {
                'name': product_id.display_name,
                'price_unit': product_id.list_price,
                'discount': 0.0,
                'product_id': product_id.id,
                'product_uom': product_id.uom_id.id,
                'product_uom_qty': 1.0,
                'tax_id': [(6, 0, company_taxes.ids)],
                'order_id': self.id
            }
            if barcode_id:
                vals.update({
                    'barcode_id': barcode_id.id
                })
            self.order_line.new(vals)


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