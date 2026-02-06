{
   "name":"Mini Sales Management",
   "author":"Pham Van Thai",
   "license":"LGPL-3",
   "version":"17.0.1.1",
   "depends": [
     'mail',
     'website',
     'sale',

   ],
   "data":[
     "security/ir.model.access.csv",
     "views/customer_readonly_views.xml",
     "data/mail_template.xml",
     "data/mail_template_cancel.xml",
     "data/mail_template_shipping.xml",
     "data/mail_template_done.xml",
     "data/sequence.xml",
     "reports/order_report.xml",

     "views/customer_views.xml",
     "views/donhang_views.xml",
     "views/sanpham_views.xml",
     "views/brand_views.xml",
     "views/cart_page.xml",
     "views/payment_method_page.xml",
     "views/payment_qr_page.xml",
     "views/checkout_page.xml",
     "views/compare_toast.xml",
     "views/compare_templates.xml",
     "views/checkout_success.xml",
     "views/product_brand_action.xml",
     "views/track_order_templates.xml",
     "views/contact_request_views.xml",
     "views/templates.xml",
     "views/menu.xml",

   ],
   "assets": {
        'web.assets_frontend': [
            'om_sales/static/src/css/website.css',
            'om_sales/static/src/css/checkout.css',
            'om_sales/static/src/js/compare.js',
            'om_sales/static/src/js/website.js',

            'om_sales/static/src/js/checkout_success.js',
            'om_sales/static/src/js/cart.js',
            'om_sales/static/src/js/compare.js',
            'om_sales/static/src/js/checkout.js',


        ],
    },
}