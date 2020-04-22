from odoo import api, fields, models, tools, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    barcode_id = fields.Many2one('product.barcode')
    barcode = fields.Char('Barcode used')
