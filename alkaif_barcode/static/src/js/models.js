odoo.define('alkaif_barcode.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var PosDB = require('pos_stock_quantity.db');
    var core = require('web.core');

    models.load_models([{
        model: 'product.barcode',
        fields: ['name', 'product_uom_id', 'product_id', 'unit_price'],
        domain: function (self) {
            return [['available_in_pos', '=', true]];
        },
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
            } else if (selectedOrder.pricelist) {
                const items = selectedOrder.pricelist.items;
                let found = false;
                for (var i = 0; i < items.length; i++) {
                    /*comparing the pricelist items with the selected item*/
                    if (items[i].barcode_id && items[i].barcode_id[1] === parsed_code.base_code) {
                        selectedOrder.add_product(product, {
                            price: items[i].fixed_price,
                            barcode: parsed_code.base_code
                        });
                        found = true;
                    }
                }
                if (!found) {
                    selectedOrder.add_product(product, {barcode: parsed_code.base_code});
                }
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

    var _super_orderline = models.Orderline.prototype;
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
        export_as_JSON: function () {
            let result = _super_orderline.export_as_JSON.call(this);
            result.product_uom_id = this.get_product().uom_id[0];
            return result;
        },
    });

    models.Product = models.Product.extend({
        get_price: function (pricelist, quantity) {
            var self = this;
            var date = moment().startOf('day');

            // In case of nested pricelists, it is necessary that all pricelists are made available in
            // the POS. Display a basic alert to the user in this case.
            if (pricelist === undefined) {
                alert(_t(
                    'An error occurred when loading product prices. ' +
                    'Make sure all pricelists are available in the POS.'
                ));
            }

            var category_ids = [];
            var category = this.categ;
            while (category) {
                category_ids.push(category.id);
                category = category.parent;
            }

            var pricelist_items = _.filter(pricelist.items, function (item) {
                return (!item.product_tmpl_id || item.product_tmpl_id[0] === self.product_tmpl_id) &&
                    (!item.product_id || item.product_id[0] === self.id) &&
                    (!item.categ_id || _.contains(category_ids, item.categ_id[0])) &&
                    (!item.date_start || moment(item.date_start).isSameOrBefore(date)) &&
                    (!item.date_end || moment(item.date_end).isSameOrAfter(date)) &&
                    (!self.is_multi_barcode || item.barcode_id && item.barcode_id === self.barcode);
            });

            var price = self.lst_price;
            _.find(pricelist_items, function (rule) {
                if (rule.min_quantity && quantity < rule.min_quantity) {
                    return false;
                }

                if (rule.base === 'pricelist') {
                    price = self.get_price(rule.base_pricelist, quantity);
                } else if (rule.base === 'standard_price') {
                    price = self.standard_price;
                }

                if (rule.compute_price === 'fixed') {
                    price = rule.fixed_price;
                    return true;
                } else if (rule.compute_price === 'percentage') {
                    price = price - (price * (rule.percent_price / 100));
                    return true;
                } else {
                    var price_limit = price;
                    price = price - (price * (rule.price_discount / 100));
                    if (rule.price_round) {
                        price = round_pr(price, rule.price_round);
                    }
                    if (rule.price_surcharge) {
                        price += rule.price_surcharge;
                    }
                    if (rule.price_min_margin) {
                        price = Math.max(price, price_limit + rule.price_min_margin);
                    }
                    if (rule.price_max_margin) {
                        price = Math.min(price, price_limit + rule.price_max_margin);
                    }
                    return true;
                }

                return false;
            });

            // This return value has to be rounded with round_di before
            // being used further. Note that this cannot happen here,
            // because it would cause inconsistencies with the backend for
            // pricelist that have base == 'pricelist'.
            return price;
        },
    });

    return models
});