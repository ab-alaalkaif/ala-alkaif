from odoo import api, fields, models, tools, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def on_barcode_scanned(self, barcode):
        if not self.env.company.nomenclature_id:
            # Logic for products
            barcode_id = self.env['stock.barcode'].search([('name', '=', barcode)], limit=1)
            if barcode_id:
                product = barcode_id.product_id
                if product:
                    if self._check_product(product):
                        return
        else:
            parsed_result = self.env.company.nomenclature_id.parse_barcode(barcode)
            if parsed_result['type'] in ['weight', 'product']:
                if parsed_result['type'] == 'weight':
                    product_barcode = parsed_result['base_code']
                    qty = parsed_result['value']
                else:  # product
                    product_barcode = parsed_result['code']
                    qty = 1.0
                barcode_id = self.env['stock.barcode'].search([('name', '=', barcode)], limit=1)
                if barcode_id:
                    product = barcode_id.product_id
                    if product:
                        if self._check_product(product, qty):
                            return
        return super().on_barcode_scanned(barcode)
