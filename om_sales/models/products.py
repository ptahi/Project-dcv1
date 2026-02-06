from odoo import api, fields, models


class Sanpham(models.Model):
  _name = 'sm.sanpham'
  _description = 'SanPham'
  _inherit = ["mail.thread"]

  name = fields.Char(string='Tên sản phẩm', required=True, translate=True, tracking=True)
  brand_id = fields.Many2one('sm.brand', string='Hãng', ondelete='restrict', tracking=True)

  code = fields.Char(string='Mã sản phẩm', required=True, index=True, tracking=True, copy=False)

  description_sale = fields.Text(string='Mô tả bán hàng', translate=True, tracking=True)
  note = fields.Text(string='Ghi chú')
  price = fields.Float(string= 'Gía Bán')
  image_1920 = fields.Image(string="Hình ảnh sản phẩm", max_width=1920, max_height=1920, website=True, ) #thêm ảnh để hiển thị

  is_available = fields.Boolean(string='Còn bán', default=True, tracking=True)

  def action_add_to_cart(self): #add sản phẩm mới vào giỏ hàng

    self.ensure_one() #chỉ chứa 1 bản ghi
    #current_price = self.price

    cart = self.env['sm.shopping.cart'].create(
      {'name': 'Mới', 'cart_line_ids': [(0, 0, {'product_id': self.id, 'quantity': 1, 'price_unit': 0, })]}) #thêm sản phẩm vào giỏ hàng lấy price từ bảng products
#'price_unit': 0, 'price': current_price,

    return {'name': 'Giỏ hàng', 'type': 'ir.actions.act_window', 'res_model': 'sm.shopping.cart', 'res_id': cart.id,

      'view_mode': 'form', 'target': 'current', }

  def action_buy_now(self):

    return self.action_add_to_cart()