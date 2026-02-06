from odoo import api, fields, models


class ShoppingCart(models.Model):
  _name = 'sm.shopping.cart'
  _description = 'Giỏ hàng'
  _inherit = ['mail.thread']

  name = fields.Char(string='Mã đơn hàng', copy=False, readonly=True, default='Mới')

  date_order = fields.Datetime(string='Ngày đặt',
                               default=fields.Datetime.now)
  customer_name = fields.Char(string='Tên khách hàng', required=True) #, required=True
  customer_phone = fields.Char(string='Số điện thoại', required=True) # đang bị ảo ở đấy xóa đi được đặt lại lỗi
  customer_email = fields.Char(string='Email')
  customer_address = fields.Text(string='Địa chỉ giao hàng')


  cart_line_ids = fields.One2many('sm.shopping.cart.line',
                                  'cart_id',
                                  string='Danh sách sản phẩm')

  total_price = fields.Float(string='Tổng tiền',
                             compute='_compute_total_price',
                             store=True)
  state = fields.Selection(
    [('draft', 'Nháp'), ('awaiting_confirmation', 'Chờ xác nhận'), ('confirmed', 'Đã xác nhận'), ('shipping', 'Đang giao hàng'), ('done', 'Hoàn thành'),
      ('cancel', 'Đã hủy')], string='Trạng thái', default='draft', tracking=True, copy=False)

  def action_awaiting_confirmation(self):
   for rec in self:
      rec.state = 'awaiting_confirmation'
      rec.message_post(body='Đơn hàng đang chờ được xác nhận')

  def action_confirm(self):
   for rec in self:
      rec.state = 'confirmed'
      rec.message_post(body='Đơn hàng đã được xác nhận')


  def action_shipping(self):

   for rec in self:
    rec.state = 'shipping'
    rec.message_post(body='Đơn hàng đang được giao')


  def action_done(self):
   for rec in self:
    rec.state = 'done'
    rec.message_post(body='Đơn hàng đã hoàn thành')


  def action_cancel(self):

   for rec in self:
    rec.state = 'cancel'
    rec.message_post(body='Đơn hàng đã bị hủy')



  def action_draft(self):

   for rec in self:
    rec.state = 'draft'
    rec.message_post(body='Đơn hàng được đặt lại về nháp')

#gửi mail confirm
  def action_confirm(self):
    template = self.env.ref(
        'om_sales.email_template_cart_confirm',
        raise_if_not_found=False
    )

    for rec in self:
        rec.state = 'confirmed'
        rec.message_post(body='Đơn hàng đã được xác nhận')

        if template and rec.customer_email:
            template.with_context(
                lang=self.env.lang
            ).send_mail(
                rec.id,
                force_send=True,
                raise_exception=True
            )
#mail hủy
  def action_cancel(self):
    template = self.env.ref('om_sales.email_template_cart_cancel', raise_if_not_found=False)

    for rec in self:
      rec.state = 'cancel'
      rec.message_post(body='Đơn hàng đã bị hủy')

      if template and rec.customer_email:
        template.send_mail(rec.id, force_send=True)
#mail shipping
  def action_shipping(self):
    template = self.env.ref('om_sales.email_template_cart_shipping', raise_if_not_found=False)

    for rec in self:
      rec.state = 'shipping'
      rec.message_post(body='Đơn hàng đang giao')

      if template and rec.customer_email:
        template.send_mail(rec.id, force_send=True)
        #mail hoàn thành
  def action_done(self):
    template = self.env.ref('om_sales.email_template_cart_done', raise_if_not_found=False)

    for rec in self:
      rec.state = 'done'
      rec.message_post(body='Đơn hàng đã giao thành công')

      if template and rec.customer_email:
        template.send_mail(rec.id, force_send=True)

  def action_print_order(self):
    self.ensure_one()
    return self.env.ref('om_sales.action_report_shopping_cart').report_action(self)


  @api.depends('cart_line_ids.price_subtotal')
  def _compute_total_price(self):
    for rec in self:
      rec.total_price = sum(line.price_subtotal for line in rec.cart_line_ids)

  @api.model
  def create(self, vals):
    if vals.get('name', 'Mới') == 'Mới':

      vals['name'] = self.env['ir.sequence'].next_by_code('sm.shopping.cart') or 'GH0001'
    return super(ShoppingCart, self).create(vals)


class ShoppingCartLine(models.Model):
  _name = 'sm.shopping.cart.line'
  _description = 'Chi tiết đơn hàng'

  cart_id = fields.Many2one('sm.shopping.cart', string='Đơn hàng', ondelete='cascade')
  product_id = fields.Many2one('sm.sanpham', string='Tên sản phẩm')
  quantity = fields.Integer(string='Số lượng', default=1)
  price_unit = fields.Float(related='product_id.price', string='Đơn giá') # price = fields.Float( string='Đơn giá')
  price_subtotal = fields.Float(string='Thành tiền', compute='_compute_subtotal', store=True)


  @api.depends('quantity', 'price_unit') #tính tổng tiền
  def _compute_subtotal(self):
    for line in self:
      line.price_subtotal = line.quantity * line.price_unit