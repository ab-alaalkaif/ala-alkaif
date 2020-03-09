from odoo import api, fields, models, tools, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode_ids = fields.One2many('product.barcode', 'product_id')
