from odoo import api, fields, models


class GeleDistributor(models.Model):
    _name = "gele.distributor"
    _description = "Gele Distributor"
    _order = "name"

    name = fields.Char(required=True)
    code = fields.Char(required=True, index=True)
    contact_name = fields.Char()
    email = fields.Char()
    phone = fields.Char()
    active = fields.Boolean(default=True)
    order_ids = fields.One2many("gele.distributor.order", "distributor_id")
    order_count = fields.Integer(compute="_compute_order_count")

    _code_unique = models.Constraint(
        "unique(code)",
        "Distributor code must be unique.",
    )

    @api.depends("order_ids")
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)


class GeleDistributorOrder(models.Model):
    _name = "gele.distributor.order"
    _description = "Gele Distributor Order"
    _order = "date_order desc, id desc"

    name = fields.Char(string="Order No.", required=True, copy=False, default="New")
    distributor_id = fields.Many2one("gele.distributor", required=True, ondelete="restrict")
    date_order = fields.Datetime(default=fields.Datetime.now, required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("pushed", "Pushed to WDT"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
    )
    line_ids = fields.One2many("gele.distributor.order.line", "order_id")
    amount_total = fields.Monetary(compute="_compute_amount_total", store=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, required=True
    )
    wdt_tid = fields.Char(string="WDT Original No.", copy=False, index=True)
    note = fields.Text()

    @api.depends("line_ids.subtotal")
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped("subtotal"))


class GeleDistributorOrderLine(models.Model):
    _name = "gele.distributor.order.line"
    _description = "Gele Distributor Order Line"

    order_id = fields.Many2one("gele.distributor.order", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True, ondelete="restrict")
    quantity = fields.Float(default=1.0, required=True)
    price_unit = fields.Monetary(required=True)
    currency_id = fields.Many2one(related="order_id.currency_id", store=True)
    subtotal = fields.Monetary(compute="_compute_subtotal", store=True)

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

