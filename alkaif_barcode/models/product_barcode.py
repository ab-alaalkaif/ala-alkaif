from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class ProductBarcode(models.Model):
    _name = 'product.barcode'
    _description = 'Product barcodes'

    _sql_constraints = [('barcode_unique', 'unique(name)', 'Barcode must be unique')]

    name = fields.Char(index=True, required=True)
    product_template_id = fields.Many2one('product.template')
    product_id = fields.Many2one('product.product', compute='_compute_product_id', store=True)
    unit_price = fields.Float()
    product_uom_id = fields.Many2one('uom.uom')
    available_in_pos = fields.Boolean(compute='_compute_available_in_pos', store=True)

    @api.constrains('product_uom_id', 'name')
    def _constrains_unique_pair_name_uom(self):
        for barcode in self:
            res = self.search([('product_template_id', '=', barcode.product_template_id.id),
                               ('product_uom_id', '=', barcode.product_uom_id.id),
                               ('id', '!=', barcode.id)])
            if res:
                raise UserError('You can not have two barcode for the same product and uom')

    @api.depends('product_template_id')
    def _compute_product_id(self):
        for barcode in self:
            barcode.product_id = barcode.product_template_id.product_variant_id

    @api.depends('product_template_id', 'product_template_id.available_in_pos')
    def _compute_available_in_pos(self):
        for barcode in self:
            product_id = barcode.product_template_id.product_variant_id
            barcode.available_in_pos = product_id.available_in_pos

    def get_pricelist_price_website(self):
        self.ensure_one()

        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        partner = self.env.user.partner_id
        company_id = current_website.company_id
        product = self.product_id

        tax_display = self.env.user.has_group(
            'account.group_show_line_subtotals_tax_excluded') and 'total_excluded' or 'total_included'
        taxes = partner.property_account_position_id.map_tax(
            product.sudo().taxes_id.filtered(lambda x: x.company_id == company_id), product, partner)

        # The list_price is always the price of one.
        quantity_1 = 1
        price = taxes.compute_all(self.unit_price, pricelist.currency_id, quantity_1, product, partner)[tax_display]
        return round(price, pricelist.currency_id.decimal_places)

