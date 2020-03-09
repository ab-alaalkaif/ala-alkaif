from odoo import api, fields, models, tools, _


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    barcode_id = fields.Many2one('product.barcode')
