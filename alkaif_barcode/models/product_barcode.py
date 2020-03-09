from odoo import api, fields, models, tools, _


class ProductBarcode(models.Model):
    _name = 'product.barcode'
    _description = 'Product barcodes'

    _sql_constraints = [('barcode_unique', 'unique(name)', 'Barcode must be unique')]

    name = fields.Char(index=True)
    product_id = fields.Many2one('product.product')
    unit_price = fields.Float()
    product_uom_id = fields.Many2one('uom.uom')
