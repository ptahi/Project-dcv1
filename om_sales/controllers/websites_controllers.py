import json
from odoo import http
from odoo.http import request
import urllib.parse
import hashlib




class WebsiteSales(http.Controller):

    # FORM CHI TIẾT SẢN PHẨM

    @http.route('/product/<int:product_id>', type='http', auth='public', website=True)
    def product_detail(self, product_id):
        product = request.env['sm.sanpham'].sudo().browse(product_id)
        if not product.exists():
            return request.not_found()

        return request.render('om_sales.product_detail_page', {
            'product': product
        })


    # FORM MUA NGAY

    @http.route('/buy-now/<int:product_id>', type='http', auth='public', website=True)
    def buy_now_form(self, product_id):
        product = request.env['sm.sanpham'].sudo().browse(product_id)
        if not product.exists():
            return request.not_found()

        return request.render('om_sales.buy_now_page', {
            'product': product
        })


    # TRANG NHẬP THÔNG TIN NGƯỜI DÙNG

    @http.route('/buy-now/submit', type='http', auth='public', website=True, methods=['POST'])
    def buy_now_submit(self, **post):

        request.session['pending_order'] = {'type': 'buy_now', 'product_id': int(post.get('product_id')),
            'name': post.get('name'), 'phone': post.get('phone'), 'email': post.get('email'),
            'address': post.get('address'), }

        return request.render('om_sales.payment_method_page', {'order':  None})

    @http.route('/order/cod', type='http', auth='public', website=True)
    def order_cod(self):

        data = request.session.get('pending_order')
        if not data:
            return request.redirect('/shop')

        cart = request.env['sm.shopping.cart'].sudo().create(
            {'customer_name': data['name'], 'customer_phone': data['phone'], 'customer_email': data.get('email'),
                'customer_address': data.get('address'), })

        CartLine = request.env['sm.shopping.cart.line'].sudo()

        if data['type'] == 'buy_now':
            CartLine.create({'cart_id': cart.id, 'product_id': data['product_id'], 'quantity': 1, })

        if data['type'] == 'cart':
            for item in data['cart_items']:
                CartLine.create(
                    {'cart_id': cart.id, 'product_id': item['id'], 'quantity': int(item.get('quantity', 1)), })

        cart.action_awaiting_confirmation()

        request.session.pop('pending_order', None)

        return request.redirect('/order/success/%s' % cart.id)


    # TRANG THÔNG BÁO THÀNH CÔNG

    @http.route('/order/success/<int:order_id>', type='http', auth='public', website=True)
    def order_success(self, order_id):
        order = request.env['sm.shopping.cart'].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()

        return request.render('om_sales.order_success_page', {
            'order': order
        })


    # LỌC SẢN PHẨM

    @http.route(['/shop', '/shop/page/<int:page>'], type='http', auth='public', website=True)
    def shop_page(self, page=1, brand=None, search=None, **kwargs):

        domain = [('is_available', '=', True)]

        if brand:
            domain.append(('brand_id', '=', int(brand)))

        if search:
            domain.append(('name', 'ilike', search))

        Product = request.env['sm.sanpham'].sudo()

        # =============================
        # SORT THEO GIÁ
        # =============================
        sort = kwargs.get('sort')

        order = 'id desc'
        if sort == 'price_asc':
            order = 'price asc'
        elif sort == 'price_desc':
            order = 'price desc'

        # =============================
        # PHÂN TRANG
        # =============================

        page_size = 8
        offset = (page - 1) * page_size

        total_products = Product.search_count(domain)
        products = Product.search(domain, order=order,  #  QUAN TRỌNG
            limit=page_size, offset=offset)

        pager = request.website.pager(url='/shop', total=total_products, page=page, step=page_size,
            url_args={'brand': brand, 'search': search, 'sort': sort,  #  GIỮ SORT
            })

        brands = request.env['sm.brand'].sudo().search([])

        return request.render('om_sales.shop_page',
                              {'products': products, 'brands': brands, 'selected_brand': brand, 'search': search,
                                  'sort': sort, 'pager': pager, })

        # TRANG LIÊN HỆ


    @http.route('/contact', type='http', auth='public', website=True)
    def contact_page(self, **kwargs):
        return request.render('om_sales.contact_page')


    # CONTACT SUBMIT (Xử lý lưu dữ liệu)

    @http.route('/contact/submit', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def contact_submit(self, **post):
        # Tạo bản ghi trong bảng contact.request
        # Sử dụng .sudo() vì người dùng website (public) không có quyền ghi vào model
        request.env['contact.request'].sudo().create(
            {'name': post.get('name'), 'email': post.get('email'), 'phone': post.get('phone'),
             'subject': post.get('subject'), 'message': post.get('message'), 'state': 'new', })

        # Sau khi lưu xong, chuyển sang trang thông báo thành công
        return request.render('om_sales.contact_success_page')

    @http.route('/cart', type='http', auth='public', website=True)
    def cart_page(self, **kwargs):
        """Trang giỏ hàng"""
        return request.render('om_sales.cart_page')

    @http.route('/checkout', type='http', auth='public', website=True)
    def checkout_page(self, **kwargs):
        print("==================")
        print(kwargs)
        return request.render('om_sales.checkout_page')

    @http.route('/checkout/submit', type='http', auth='public', website=True, methods=['POST'])
    def checkout_submit(self, **post):

        cart_data = post.get('cart_data')
        if not cart_data:
            return request.redirect('/cart')

        try:
            cart_items = json.loads(cart_data)
        except Exception:
            return request.redirect('/cart')

        if not cart_items:
            return request.redirect('/cart')

        # 🔑 LƯU SESSION – CHƯA TẠO ĐƠN
        request.session['pending_order'] = {'type': 'cart', 'name': post.get('name'), 'phone': post.get('phone'),
            'email': post.get('email'), 'address': post.get('address'), 'cart_items': cart_items, }

        # 👉 CHUYỂN SANG CHỌN THANH TOÁN
        return request.render('om_sales.payment_method_page', {'order': None})

    # =============================
    # TRANG SUCCESS
    # =============================
    # @http.route('/checkout/success', type='http', auth='public', website=True)
    # def checkout_success(self, order_id=None, **kwargs):
    #     if not order_id:
    #         return request.redirect('/shop')
    #
    #     order = request.env['sm.shopping.cart'].sudo().browse(int(order_id))
    #     if not order.exists():
    #         return request.redirect('/shop')
    #
    #     return request.render('om_sales.checkout_success', {'order': order})

    @http.route('/track-order', type='http', auth='public', website=True)
    def track_order_form(self, **kwargs):
        return request.render('om_sales.track_order_form', {})

    @http.route('/track-order/result', type='http', auth='public', website=True, methods=['POST'])
    def track_order_result(self, **post):
        order_code = post.get('order_code')
        phone = post.get('phone')

        order = request.env['sm.shopping.cart'].sudo().search(
            [('name', '=', order_code), ('customer_phone', '=', phone)], limit=1)

        values = {'order': order, 'order_code': order_code, 'phone': phone, }
        return request.render('om_sales.track_order_result', values)

    #     # =================================================
    #     # PAGE: /compare
    #     # =================================================
    #
    # @http.route('/compare', type='http', auth='public', website=True)
    # def compare_page(self):
    #     compare_ids = request.session.get('compare_ids', [])
    #     products = request.env['sm.sanpham'].sudo().browse(compare_ids)
    #
    #     return request.render('om_sales.compare_page', {'products': products})
    #
    # # =================================================
    # # JSON: GET COMPARE DATA
    # # =================================================
    # @http.route('/compare/get', type='json', auth='public', website=True)
    # def compare_get(self):
    #     compare_ids = request.session.get('compare_ids', [])
    #     products = request.env['sm.sanpham'].sudo().browse(compare_ids)
    #
    #     return self._prepare_response(products)
    #
    # # =================================================
    # # JSON: ADD PRODUCT
    # # =================================================
    # @http.route('/compare/add', type='json', auth='public', website=True)
    # def compare_add(self, product_id):
    #     try:
    #         product_id = int(product_id)
    #     except (TypeError, ValueError):
    #         return {'error': 'invalid', 'message': 'ID không hợp lệ'}
    #
    #     compare_ids = request.session.get('compare_ids', [])
    #
    #     product = request.env['sm.sanpham'].sudo().browse(product_id)
    #     if not product.exists():
    #         return {'error': 'not_found', 'message': 'Không tìm thấy sản phẩm'}
    #
    #     if product_id in compare_ids:
    #         return self._prepare_response(request.env['sm.sanpham'].sudo().browse(compare_ids))
    #
    #     if len(compare_ids) >= 2:
    #         return {'error': 'max', 'message': 'Chỉ được so sánh tối đa 2 sản phẩm'}
    #
    #     compare_ids.append(product_id)
    #     request.session['compare_ids'] = compare_ids
    #
    #     products = request.env['sm.sanpham'].sudo().browse(compare_ids)
    #     return self._prepare_response(products, added_product=product)
    #
    # # =================================================
    # # JSON: REMOVE PRODUCT
    # # =================================================
    # @http.route('/compare/remove', type='json', auth='public', website=True)
    # def compare_remove(self, product_id):
    #     try:
    #         product_id = int(product_id)
    #     except (TypeError, ValueError):
    #         return {'error': 'invalid'}
    #
    #     compare_ids = request.session.get('compare_ids', [])
    #
    #     if product_id in compare_ids:
    #         compare_ids.remove(product_id)
    #         request.session['compare_ids'] = compare_ids
    #
    #     products = request.env['sm.sanpham'].sudo().browse(compare_ids)
    #     return self._prepare_response(products)

    # =================================================
    # HELPER
    # =================================================
    # def _prepare_response(self, products, added_product=None):
    #     return {'count': len(products),
    #             'products': [{'id': p.id, 'name': p.name, 'image': '/web/image/sm.sanpham/%s/image_1920' % p.id} for p
    #                          in products],
    #             'added_product': added_product and {'id': added_product.id, 'name': added_product.name,
    #                                                 'image': '/web/image/sm.sanpham/%s/image_1920' % added_product.id}}

    @http.route('/payment/qr/<int:order_id>', type='http', auth='public', website=True)
    def payment_qr(self, order_id):
        order = request.env['sm.shopping.cart'].sudo().browse(order_id)
        if not order.exists():
            return request.redirect('/shop')

        # ---- THÔNG TIN VIETQR ----
        bank_code = '970415'  # VietinBank
        account_no = '0868134068'
        account_name = 'PHAM VAN THAI'

        amount = int(order.total_price or 0)
        add_info = f"SM_{order.id}"

        # Encode nội dung
        add_info = urllib.parse.quote(add_info)

        # ---- URL VIETQR ----
        qr_url = (f"https://api.vietqr.io/image/"
                  f"{bank_code}-{account_no}-print.png"
                  f"?amount={amount}&addInfo={add_info}&accountName={account_name}")

        return request.render('om_sales.payment_qr_page', {'order': order, 'qr_url': qr_url, })

    # =========================
    # KHÁCH XÁC NHẬN ĐÃ THANH TOÁN
    # =========================
    @http.route('/payment/confirm/<int:order_id>', type='http', auth='public', website=True)
    def payment_confirm(self, order_id):
        order = request.env['sm.shopping.cart'].sudo().browse(order_id)
        if not order.exists():
            return request.redirect('/shop')

        # 👉 XÁC NHẬN ĐƠN (KHÔNG THÊM TRẠNG THÁI THANH TOÁN)
        order.action_confirm()

        return request.redirect('/order/success/%s' % order.id)

    # =========================
    # TẠO ORDER TỪ SESSION → QR
    # =========================
    @http.route('/order/qr', type='http', auth='public', website=True)
    def order_qr(self):
        data = request.session.get('pending_order')
        if not data:
            return request.redirect('/shop')

        cart = request.env['sm.shopping.cart'].sudo().create(
            {'customer_name': data['name'], 'customer_phone': data['phone'], 'customer_email': data.get('email'),
                'customer_address': data.get('address'), })

        CartLine = request.env['sm.shopping.cart.line'].sudo()

        if data['type'] == 'buy_now':
            CartLine.create({'cart_id': cart.id, 'product_id': data['product_id'], 'quantity': 1, })

        if data['type'] == 'cart':
            for item in data['cart_items']:
                CartLine.create(
                    {'cart_id': cart.id, 'product_id': item['id'], 'quantity': int(item.get('quantity', 1)), })

        request.session.pop('pending_order', None)

        return request.redirect('/payment/qr/%s' % cart.id)

