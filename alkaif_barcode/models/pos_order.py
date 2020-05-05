from odoo import api, fields, models, tools, _


class POSOrder(models.Model):
    _inherit = 'pos.order'


class POSOrderLine(models.Model):
    _inherit = 'pos.order.line'

    barcode_id = fields.Many2one('product.barcode')
    product_uom_id = fields.Many2one('uom.uom', string='Product UoM', related='')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.qty = res.product_uom_id._compute_quantity(res.qty, res.product_uom_id, rounding_method='HALF-UP')
        res.product_uom_id = res.product_id.uom_id
        return res
