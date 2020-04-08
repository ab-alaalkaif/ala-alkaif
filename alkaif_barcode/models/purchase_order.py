from datetime import date

from odoo import api, fields, models, tools, _


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        company_rec = self.env.user.company_id
        barcode_id = self.env['product.barcode'].search([('name', '=', barcode)])
        if barcode_id:
            sol = self.order_line.filtered(lambda r: r.barcode_id.id == barcode_id.id)
            self.create_purchase_order_line(company_rec, barcode_id.product_id, sol, barcode_id=barcode_id)
        else:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)])
            if product_id:
                sol = self.order_line.filtered(lambda r: r.product_id.barcode == barcode)
                self.create_purchase_order_line(company_rec, product_id, sol)

    def create_purchase_order_line(self, company_rec, product_id, sol, barcode_id=False):
        if sol:
            sol[0].product_qty += 1
        else:
            FiscalPosition = self.env['account.fiscal.position']
            fpos = FiscalPosition.with_context(force_company=self.company_id.id).get_fiscal_position(self.partner_id.id)
            fpos = FiscalPosition.browse(fpos)
            if fpos:
                taxes_ids = fpos.map_tax(product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == company_rec)).ids
            else:
                taxes_ids = product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == company_rec).ids
            vals = {
                'name': product_id.display_name,
                'price_unit': product_id.list_price,
                'product_id': product_id.id,
                'product_uom': product_id.uom_id.id,
                'product_qty': 1.0,
                'order_id': self.id,
                'taxes_id': [(6, 0, taxes_ids)],
                'date_planned': date.today()
            }
            if barcode_id:
                vals.update({
                    'barcode_id': barcode_id.id,
                })
            self.order_line.new(vals)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    barcode_id = fields.Many2one('product.barcode')

    @api.onchange('barcode_id')
    def _on_change_barcode(self):
        if self.barcode_id:
            self.product_id = self.barcode_id.product_id

    def _onchange_quantity(self):
        super()._onchange_quantity()
        if self.barcode_id:
            self.update({
                'price_unit': self.barcode_id.unit_price,
                'product_uom': self.barcode_id.product_uom_id,
            })
