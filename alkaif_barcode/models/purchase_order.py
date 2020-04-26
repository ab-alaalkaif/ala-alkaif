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
            self.create_purchase_order_line(company_rec, barcode_id.product_id, sol, barcode, barcode=barcode_id)
        else:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)])
            if product_id:
                sol = self.order_line.filtered(lambda r: r.product_id.barcode == barcode)
                self.create_purchase_order_line(company_rec, product_id, sol)

    def create_purchase_order_line(self, company_rec, product_id, sol, barcode, barcode_id=False):
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
                'price_unit': product_id.list_price if not barcode_id else barcode_id.unit_price,
                'product_id': product_id.id,
                'product_uom': product_id.uom_id.id if not barcode_id else barcode_id.product_uom_id.id,
                'product_qty': 1.0,
                'order_id': self.id,
                'barcode': barcode,
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
    barcode = fields.Char('Barcode used')

    @api.onchange('barcode_id')
    def _on_change_barcode_id(self):
        if self.barcode_id:
            self.product_id = self.barcode_id.product_id

    def _onchange_quantity(self):
        super()._onchange_quantity()
        if self.barcode_id:
            self.update({
                'price_unit': self.barcode_id.unit_price,
                'product_uom': self.barcode_id.product_uom_id,
            })

    def _prepare_account_move_line(self, move):
        res = super()._prepare_account_move_line(move)
        if self.barcode:
            res.update({
                'barcode': self.barcode
            })
        return res

    @api.onchange('barcode')
    def _onchange_barcode(self):
        if not self.barcode:
            return
        barcode_id = self.env['product.barcode'].search([('name', '=', self.barcode)])
        if barcode_id:
            self.update_line(barcode_id.product_id, barcode_id=barcode_id)
            self.barcode_id = barcode_id
        else:
            product_id = self.env['product.product'].search([('barcode', '=', self.barcode)])
            if product_id:
                self.update_line(product_id)

    def update_line(self, product_id, barcode_id=False):
        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_context(force_company=self.company_id.id).get_fiscal_position(self.partner_id.id)
        fpos = FiscalPosition.browse(fpos)
        if fpos:
            taxes_ids = fpos.map_tax(
                product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.company_id)).ids
        else:
            taxes_ids = product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.company_id).ids
        self.name = product_id.display_name
        self.price_unit = product_id.list_price if not barcode_id else barcode_id.unit_price
        self.product_id = product_id.id
        self.product_uom = product_id.uom_id.id if not barcode_id else barcode_id.product_uom_id.id
        self.product_qty = 1.0
        self.order_id = self.id
        self.taxes_id = [(6, 0, taxes_ids)]
        self.date_planned = date.today()
