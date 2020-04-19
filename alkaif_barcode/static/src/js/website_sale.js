odoo.define('alkaif_barcode.website_sale', function (require) {
    'use strict';

    let core = require('web.core');
    var config = require('web.config');
    var concurrency = require('web.concurrency');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.WebsiteSale.include({
        events: _.extend({}, publicWidget.registry.WebsiteSale.prototype.events, {
            'change #uom_id': '_onchange_uom',
        }),
        _onchange_uom: function (ev) {
            let select = $(ev.currentTarget)[0];
            console.log(select);
            $('.oe_currency_value').text(select.options[select.selectedIndex].dataset.price);
        }
    })
});
