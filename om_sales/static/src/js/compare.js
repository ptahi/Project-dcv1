odoo.define('om_sales.compare', [
    'web.public.widget',
    'web.ajax'
], function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.CompareProducts = publicWidget.Widget.extend({
        selector: 'body',

        events: {
            'click .js-add-to-compare': '_onAddToCompare',
            'click .remove-compare': '_onRemoveItem',
        },

        start: function () {
            this._super.apply(this, arguments);
            console.log('[Compare] Widget started');
            this._loadCompareData();
            return this;
        },

        // =============================
        // LOAD DATA BAN ĐẦU
        // =============================
        _loadCompareData: function () {
            var self = this;
            ajax.jsonRpc('/compare/get', 'call', {}).then(function (data) {
                self._updateCompareBar(data);
            });
        },

        // =============================
        // ADD PRODUCT
        // =============================
        _onAddToCompare: function (ev) {
            ev.preventDefault();

            var productId = parseInt($(ev.currentTarget).data('product-id'), 10);
            var self = this;

            ajax.jsonRpc('/compare/add', 'call', {
                product_id: productId
            }).then(function (data) {

                if (data.error === 'max') {
                    alert('Chỉ được so sánh tối đa 2 sản phẩm');
                    return;
                }

                self._updateCompareBar(data);

                // 👉 HIỆN POPUP TOAST
                self._showToast(data.added_product);
            });
        },

        // =============================
        // REMOVE PRODUCT
        // =============================
        _onRemoveItem: function (ev) {
            var productId = parseInt($(ev.currentTarget).data('id'), 10);
            var self = this;

            ajax.jsonRpc('/compare/remove', 'call', {
                product_id: productId
            }).then(function (data) {
                self._updateCompareBar(data);
            });
        },

        // =============================
        // UPDATE COMPARE BAR
        // =============================
        _updateCompareBar: function (data) {
            var $bar = $('#compare_bar');
            var $items = $('#compare_items');

            $items.empty();

            if (!data || data.count === 0) {
                $bar.hide();
                return;
            }

            for (var i = 0; i < data.products.length; i++) {
                var p = data.products[i];

                var $item = $('<div/>', {
                    class: 'me-3 text-center position-relative',
                    css: { maxWidth: '120px' }
                });

                $item.append('<img src="' + p.image +
                    '" style="height:60px; object-fit:contain"/>');

                $item.append('<small class="d-block text-truncate">' +
                    p.name + '</small>');

                $item.append(
                    '<button class="btn btn-sm btn-danger position-absolute top-0 end-0 remove-compare" ' +
                    'data-id="' + p.id + '">×</button>'
                );

                $items.append($item);
            }

            $bar.show();
        },

        // =============================
        // SHOW TOAST POPUP
        // =============================
        _showToast: function (product) {
            if (!product) {
                return;
            }

            $('#compare_toast_image').attr('src', product.image);
            $('#compare_toast_name').text(product.name);

            var toastEl = document.getElementById('compareToast');
            if (!toastEl) {
                return;
            }

            var toast = bootstrap.Toast.getOrCreateInstance(toastEl);
            toast.show();
        },
    });
});
