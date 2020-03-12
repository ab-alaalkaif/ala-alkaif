odoo.define('alkaif_barcode.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var PosDB = require('point_of_sale.DB');
    var core = require('web.core');

    models.load_models([{
        model: 'product.barcode',
        fields: ['name', 'product_uom_id', 'product_id', 'unit_price'],
        domain: function(self) { return [['available_in_pos','=',true]]; },
        loaded: function (self, barcodes) {
            self.db.add_barcodes(barcodes);
        },
    }]);

    models.PosModel = models.PosModel.extend({
        scan_product: function (parsed_code) {
            var selectedOrder = this.get_order();
            var product = this.db.get_product_by_barcode(parsed_code.base_code);

            if (!product) {
                return false;
            }

            if (parsed_code.type === 'price') {
                selectedOrder.add_product(product, {price: parsed_code.value, barcode: parsed_code.base_code});
            } else if (parsed_code.type === 'weight') {
                selectedOrder.add_product(product, {
                    quantity: parsed_code.value,
                    merge: false,
                    barcode: parsed_code.base_code
                });
            } else if (parsed_code.type === 'discount') {
                selectedOrder.add_product(product, {
                    discount: parsed_code.value,
                    merge: false,
                    barcode: parsed_code.base_code
                });
            } else {
                selectedOrder.add_product(product, {barcode: parsed_code.base_code});
            }
            return true;
        },
    });

    models.Order = models.Order.extend({
        add_product: function (product, options) {
            if (this._printed) {
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
            this.fix_tax_included_price(line);

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }

            if (options.price !== undefined) {
                line.set_unit_price(options.price);
                this.fix_tax_included_price(line);
            }

            if (options.lst_price !== undefined) {
                line.set_lst_price(options.lst_price);
            }

            if (options.discount !== undefined) {
                line.set_discount(options.discount);
            }

            if (options.barcode) {
                line.set_barcode(options.barcode)
            }

            if (options.extras !== undefined) {
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }

            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if (this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false) {
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline) {
                to_merge_orderline.merge(line);
                this.select_orderline(to_merge_orderline);
            } else {
                this.orderlines.add(line);
                this.select_orderline(this.get_last_orderline());
            }

            if (line.has_product_lot) {
                this.display_lot_popup();
            }
            if (this.pos.config.iface_customer_facing_display) {
                this.pos.send_current_order_to_customer_facing_display();
            }
        },
    });

    models.Orderline = models.Orderline.extend({

        get_product: function () {
            let product = this.pos.db.product_by_barcode[this.barcode];
            if (product) {
                return product
            } else {
                return this.product;
            }
        },
        set_barcode: function (barcode) {
            this.barcode = barcode;
        },

    });

    return models
});