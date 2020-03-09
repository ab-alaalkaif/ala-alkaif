odoo.define('alkaif_barcode.db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');

    PosDB.include({
        add_barcodes: function (barcode_ids) {
            for(let i = 0, len = barcode_ids.length; i < len; i++){
                let barcode_id = barcode_ids[i];
                let new_product;
                new_product = Object.assign({}, this.product_by_id[barcode_id.product_id[0]]);
                new_product.lst_price = barcode_id.unit_price;
                new_product.uom_id = barcode_id.product_uom_id;
                Object.setPrototypeOf(new_product, Object.getPrototypeOf(this.product_by_id[barcode_id.product_id[0]]));
                this.product_by_barcode[barcode_id.name] = new_product;
            }
        }
    })
});