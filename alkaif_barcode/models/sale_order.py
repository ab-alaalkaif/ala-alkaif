from odoo import api, fields, models, tools, _


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        company_rec = self.env.user.company_id
        barcode_id = self.env['product.barcode'].search([('name', '=', barcode)])
        if barcode_id:
            sol = self.order_line.filtered(lambda r: r.barcode_id.id == barcode_id.id)
            self.create_sale_order_line(company_rec, barcode_id.product_id, sol, barcode, barcode_id=barcode_id)
        else:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)])
            if product_id:
                sol = self.order_line.filtered(lambda r: r.product_id.barcode == barcode)
                self.create_sale_order_line(company_rec, product_id, sol, barcode)

    def create_sale_order_line(self, company_rec, product_id, sol, barcode, barcode_id=False):
        if sol:
            sol[0].product_uom_qty += 1
        else:
            taxes = product_id.taxes_id
            company_taxes = [tax_rec.id for tax_rec in taxes if tax_rec.company_id.id == company_rec.id]
            vals = {
                'name': product_id.display_name,
                'price_unit': product_id.list_price if not barcode_id else barcode_id.unit_price,
                'discount': 0.0,
                'product_id': product_id.id,
                'product_uom': product_id.uom_id.id if not barcode_id else barcode_id.product_uom_id.id,
                'product_uom_qty': 1.0,
                'barcode': barcode,
                'tax_id': [(6, 0, company_taxes)],
                'order_id': self.id
            }
            if barcode_id:
                vals.update({
                    'barcode_id': barcode_id.id
                })
            self.order_line.new(vals)

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        res = super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        sale_line_id = self.env['sale.order.line'].browse(res.get('line_id'))
        if sale_line_id.exists() and sale_line_id.barcode_id:
            sale_line_id.write({
                'product_uom': sale_line_id.barcode_id.product_uom_id.id,
                'price_unit': sale_line_id.barcode_id.unit_price
            })
        return res

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        lines = super()._cart_find_product_line(product_id, line_id, **kwargs)
        if lines and kwargs.get('uom_id', False):
            return lines.filtered(lambda r: r.product_uom.id == int(kwargs.get('uom_id')))
        return lines


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    barcode_id = fields.Many2one('product.barcode')
    barcode = fields.Char('Barcode used')

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

    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        if self.barcode:
            res.update({
                'barcode': self.barcode,
            })
        return res
