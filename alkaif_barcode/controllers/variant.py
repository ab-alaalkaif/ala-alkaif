# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.variant import VariantController


class VariantControllerCustom(VariantController):

    @http.route(['/sale/get_combination_info'], type='json', auth="user", methods=['POST'])
    def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        res = super().get_combination_info(product_template_id, product_id, combination, add_qty, pricelist_id, **kw)
        if kw.get('barcode_id', False):
            barcode_id = request.env['product.barcode'].sudo().browse(int(kw.get('barcode_id')))
            res['price'] = barcode_id.get_pricelist_price_website(compute_tax=True)
        return res
