odoo.define('alkaif_barcode.VariantMixin', function (require) {
    'use strict';

    var concurrency = require('web.concurrency');
    var core = require('web.core');
    var utils = require('web.utils');
    var ajax = require('web.ajax');
    var _t = core._t;

    var VariantMixin = require('sale.VariantMixin');

    /**
     * @see onChangeVariant
     *
     * @private
     * @param {Event} ev
     * @returns {Deferred}
     */
    VariantMixin._getCombinationInfo = function (ev) {
        var self = this;

        if ($(ev.target).hasClass('variant_custom_value')) {
            return Promise.resolve();
        }

        var $parent = $(ev.target).closest('.js_product');
        var qty = $parent.find('input[name="add_qty"]').val();
        var combination = this.getSelectedVariantValues($parent);
        var parentCombination = $parent.find('ul[data-attribute_exclusions]').data('attribute_exclusions').parent_combination;
        var productTemplateId = parseInt($parent.find('.product_template_id').val());
        const select = $parent.find('#uom_id');
        let barcode_id = false;
        if (select) {
            barcode_id = select[0].options[select[0].selectedIndex].dataset.barcode_id;
        }
        self._checkExclusions($parent, combination);

        return ajax.jsonRpc(this._getUri('/sale/get_combination_info'), 'call', {
            'product_template_id': productTemplateId,
            'product_id': this._getProductId($parent),
            'combination': combination,
            'add_qty': parseInt(qty),
            'pricelist_id': this.pricelistId || false,
            'parent_combination': parentCombination,
            'barcode_id': barcode_id,
        }).then(function (combinationData) {
            self._onChangeCombination(ev, $parent, combinationData);
        });
    };

    return VariantMixin;
});