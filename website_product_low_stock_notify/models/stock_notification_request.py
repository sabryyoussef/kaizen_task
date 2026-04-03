import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ProductStockNotificationRequest(models.Model):
    _name = "product.stock.notification.request"
    _description = "Product Stock Notification Request"
    _order = "create_date desc"

    product_id = fields.Many2one("product.product", required=True, index=True)
    product_tmpl_id = fields.Many2one(
        "product.template", related="product_id.product_tmpl_id", store=True, index=True
    )
    email = fields.Char(required=True, index=True)
    email_normalized = fields.Char(required=True, index=True)
    requested_qty = fields.Float(required=True, default=1.0)
    state = fields.Selection(
        [("pending", "Pending"), ("sent", "Sent")], default="pending", required=True, index=True
    )
    sent_date = fields.Datetime()
    website_id = fields.Many2one("website", index=True)

    _sql_constraints = [
        (
            "check_requested_qty_positive",
            "CHECK(requested_qty > 0)",
            "Requested quantity must be greater than zero.",
        ),
    ]

    @api.model
    def _normalize_email(self, email):
        return (email or "").strip().lower()

    @api.constrains("email")
    def _constrain_email_presence(self):
        for record in self:
            if not record._normalize_email(record.email):
                raise ValidationError(_("Email is required."))

    @api.constrains("state", "product_id", "email_normalized")
    def _constrain_single_pending_per_product_email(self):
        for record in self:
            if record.state != "pending":
                continue
            domain = [
                ("id", "!=", record.id),
                ("state", "=", "pending"),
                ("product_id", "=", record.product_id.id),
                ("email_normalized", "=", record.email_normalized),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    _("A pending request for this product and email already exists.")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            email = vals.get("email")
            if email:
                vals["email"] = email.strip()
            vals["email_normalized"] = self._normalize_email(vals.get("email"))
        return super().create(vals_list)

    def write(self, vals):
        if "email" in vals:
            vals["email"] = (vals["email"] or "").strip()
            vals["email_normalized"] = self._normalize_email(vals["email"])
        return super().write(vals)

    @api.model
    def create_or_update_pending_request(self, product, email, requested_qty, website=None):
        email_clean = (email or "").strip()
        email_normalized = self._normalize_email(email_clean)
        existing = self.search(
            [
                ("product_id", "=", product.id),
                ("email_normalized", "=", email_normalized),
                ("state", "=", "pending"),
            ],
            limit=1,
        )
        vals = {
            "product_id": product.id,
            "email": email_clean,
            "requested_qty": requested_qty,
            "website_id": website.id if website else False,
        }
        if existing:
            existing.write(vals)
            return existing, False
        return self.create(vals), True

    def get_product_url(self):
        self.ensure_one()
        path = self.product_id.product_tmpl_id.website_url or "/shop"
        if path.startswith("http://") or path.startswith("https://"):
            return path
        website = self.website_id or self.env["website"].sudo().get_current_website()
        base_url = (website.domain or "").strip() if website else ""
        if not base_url:
            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        base_url = base_url.rstrip("/")
        if not path.startswith("/"):
            path = "/%s" % path
        return "%s%s" % (base_url, path) if base_url else path

    @api.model
    def process_pending_notifications(self):
        template = self.env.ref(
            "website_product_low_stock_notify.mail_template_product_back_in_stock",
            raise_if_not_found=False,
        )
        pending_requests = self.search([("state", "=", "pending")])
        for notification in pending_requests:
            if notification.product_id.qty_available <= 0:
                continue
            try:
                if template:
                    template.send_mail(notification.id, force_send=True)
                notification.write(
                    {
                        "state": "sent",
                        "sent_date": fields.Datetime.now(),
                    }
                )
            except Exception:
                _logger.exception(
                    "Failed to send back-in-stock email for notification request %s",
                    notification.id,
                )

    @api.model
    def _trigger_notifications_for_products(self, product_ids):
        """Trigger notifications for specific products that are now in stock.
        Called by stock.quant when stock levels change from 0 to positive."""
        if not product_ids:
            return
        
        template = self.env.ref(
            "website_product_low_stock_notify.mail_template_product_back_in_stock",
            raise_if_not_found=False,
        )
        
        # Find pending requests for these products
        pending_requests = self.search([
            ("state", "=", "pending"),
            ("product_id", "in", product_ids)
        ])
        
        for notification in pending_requests:
            # Double-check product is actually in stock
            if notification.product_id.qty_available <= 0:
                continue
            
            try:
                if template:
                    template.send_mail(notification.id, force_send=True)
                notification.write({
                    "state": "sent",
                    "sent_date": fields.Datetime.now(),
                })
                _logger.info(
                    "Sent stock notification for product %s to %s",
                    notification.product_id.display_name,
                    notification.email
                )
            except Exception:
                _logger.exception(
                    "Failed to send back-in-stock email for notification request %s",
                    notification.id,
                )
