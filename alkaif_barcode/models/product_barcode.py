from odoo import api, fields, models, tools, _


class ProductBarcode(models.Model):
    _name = 'product.barcode'
    _description = 'Product barcodes'

    _sql_constraints = [('barcode_unique', 'unique(name)', 'Barcode must be unique')]

    name = fields.Char(index=True)
    product_template_id = fields.Many2one('product.template')
    product_id = fields.Many2one('product.product', compute='_compute_product_id', store=True)
    unit_price = fields.Float()
    product_uom_id = fields.Many2one('uom.uom')

    @api.depends('product_template_id')
    def _compute_product_id(self):
        for barcode in self:
            barcode.product_id = barcode.product_template_id.product_variant_id
