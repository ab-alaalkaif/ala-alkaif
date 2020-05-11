odoo.define('alkaif_barcode.db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');
    var utils = require('web.utils');

    PosDB.include({
        init: function (options) {
            this._super.apply(this, arguments);
            this.category_search_string_barcode = {};
        },
        _product_search_string_barcode: function (product) {
            var str = product.display_name;
            if (product.barcode) {
                str += '|' + product.barcode;
            }
            if (product.default_code) {
                str += '|' + product.default_code;
            }
            if (product.description) {
                str += '|' + product.description;
            }
            if (product.description_sale) {
                str += '|' + product.description_sale;
            }
            str = product.barcode + ':' + str.replace(/:/g, '') + '\n';
            return str;
        },
        add_barcodes: function (barcode_ids) {
            for (let i = 0, len = barcode_ids.length; i < len; i++) {
                let barcode_id = barcode_ids[i];
                let new_product;
                if (!this.product_by_id[barcode_id.product_id[0]]) {
                    continue;
                }
                new_product = Object.assign({}, this.product_by_id[barcode_id.product_id[0]]);
                new_product.lst_price = barcode_id.unit_price;
                new_product.uom_id = barcode_id.product_uom_id;
                new_product.barcode = barcode_id.name;
                new_product.is_multi_barcode = true;
                Object.setPrototypeOf(new_product, Object.getPrototypeOf(this.product_by_id[barcode_id.product_id[0]]));
                this.product_by_barcode[barcode_id.name] = new_product;
                let search_string = utils.unaccent(this._product_search_string_barcode(new_product));
                let categ_id = new_product.pos_categ_id ? new_product.pos_categ_id[0] : this.root_category_id;
                this.category_search_string_barcode[categ_id] += search_string;
            }
        },
        search_product_in_category: function (category_id, query) {
            let results = this._super.apply(this, arguments);
            if (results.length === 0) {
                try {
                    query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g, '.');
                    query = query.replace(/ /g, '.+');
                    var re = RegExp("([0-9]+\-?[0-9]+):.*?" + utils.unaccent(query), "gi");
                } catch (e) {
                    return [];
                }
                results = [];
                let r;
                for (let i = 0; i < this.limit; i++) {
                    r = re.exec(this.category_search_string_barcode[category_id]);
                    if (r) {
                        results.push(this.get_product_by_barcode(r[1]));
                    } else {
                        break;
                    }
                }
            }
            return results;
        },
    })
});