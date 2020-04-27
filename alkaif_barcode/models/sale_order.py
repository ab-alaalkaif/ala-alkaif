from math import floor

from odoo import api, fields, models, tools, _
from odoo.addons.website_sale_stock.models.sale_order import SaleOrder


def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
    return super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)


SaleOrder._cart_update = _cart_update


class SaleOrderCustom(models.Model):
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
        values = super(SaleOrderCustom, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        sale_line_id = self.env['sale.order.line'].browse(values.get('line_id'))
        if sale_line_id.exists() and sale_line_id.barcode_id:
            sale_line_id.write({
                'product_uom': sale_line_id.barcode_id.product_uom_id.id,
                'price_unit': sale_line_id.barcode_id.get_pricelist_price_website()
            })
        elif sale_line_id.exists() and kwargs.get('uom_id', False):
            barcode_id = self.env['product.barcode'].search([('product_id', '=', sale_line_id.product_id.id),
                                                             ('product_uom_id', '=', int(kwargs.get('uom_id', False)))
                                                             ], limit=1)
            if barcode_id:
                sale_line_id.write({
                    'product_uom': barcode_id.product_uom_id.id,
                    'price_unit': barcode_id.get_pricelist_price_website(),
                    'barcode_id': barcode_id.id,
                    'barcode': barcode_id.name
                })
        # odoo.addons.website_sale_stock.models.sale_order._cart_update
        line_id = values.get('line_id')

        for line in self.order_line:
            if line.product_id.type == 'product' and line.product_id.inventory_availability in ['always', 'threshold']:
                cart_qty = 0
                old_qty = line.product_uom_qty
                for order_line in self.order_line.filtered(lambda p: p.product_id.id == line.product_id.id):
                    cart_qty += order_line.product_uom_qty * order_line.product_uom.factor_inv
                warehouse = self.website_id.warehouse_id if self.website_id else self.warehouse_id
                if cart_qty > line.product_id.with_context(warehouse=warehouse.id).virtual_available and line_id == line.id:
                    qty = line.product_id.with_context(warehouse=warehouse.id).virtual_available - cart_qty
                    if line.barcode_id:
                        qty = floor(qty / line.barcode_id.product_uom_id.factor_inv)
                    new_val = super(SaleOrderCustom, self)._cart_update(line.product_id.id, line.id, qty, 0, **kwargs)
                    values.update(new_val)

                    # Make sure line still exists, it may have been deleted in super()_cartupdate because qty can be <= 0
                    if line.exists() and new_val['quantity']:
                        line.warning_stock = _('You ask for %s products but only %s is available') % (old_qty, new_val['quantity'])
                        values['warning'] = line.warning_stock
                    else:
                        self.warning_stock = _("Some products became unavailable and your cart has been updated. We're sorry for the inconvenience.")
                        values['warning'] = self.warning_stock
        # end of patch
        return values

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
    def _on_change_barcode_id(self):
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
        taxes = product_id.taxes_id
        company_taxes = [tax_rec.id for tax_rec in taxes if tax_rec.company_id.id == self.company_id.id]
        self.name = product_id.display_name
        self.price_unit = product_id.list_price if not barcode_id else barcode_id.unit_price
        self.discount = 0.0
        self.product_id = product_id
        self.product_uom = product_id.uom_id.id if not barcode_id else barcode_id.product_uom_id
        self.product_uom_qty = 1.0
        self.tax_id = [(6, 0, company_taxes)]
