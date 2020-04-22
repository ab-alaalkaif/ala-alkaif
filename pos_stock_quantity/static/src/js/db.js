odoo.define('pos_stock_quantity.db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');
    var utils = require('web.utils');

    PosDB.include({
        init: function (options) {
            this._super.apply(this, arguments);
            this.qty_by_product_id = {};
        },
        add_stock: function (product) {
            this.qty_by_product_id[product.id] = product.qty_available;
        },
        set_stock: function (product, qty) {
            if (!this.qty_by_product_id[product]) {
                this.qty_by_product_id[product] = qty;
            } else {
                this.qty_by_product_id[product] += qty;
            }
        },
        get_stock: function (product_id) {
            if (this.qty_by_product_id.hasOwnProperty(product_id)) {
                return this.qty_by_product_id[product_id];
            }
            else {
                return false;
            }
        },
        reset_stock: function () {
            this.qty_by_product_id = {}
        },
        delete_stock: function(product_id) {
          delete this.qty_by_product_id[product_id];
        },
        reset_product_stock: function (product) {
            this.qty_by_product_id[product] = 0;
        }
    })
});