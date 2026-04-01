from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError


class ProductStockNotificationWizard(models.TransientModel):
    _name = "product.stock.notification.wizard"
    _description = "Product Stock Notification Wizard"

    product_id = fields.Many2one("product.product", required=True)
    email = fields.Char(required=True)
    requested_qty = fields.Float(required=True, default=1.0)
    website_id = fields.Many2one("website")

    def _validate_input(self):
        self.ensure_one()
        email_clean = (self.email or "").strip()
        if not email_clean or not tools.single_email_re.fullmatch(email_clean):
            raise ValidationError(_("Please provide a valid email address."))
        if self.requested_qty <= 0:
            raise ValidationError(_("Quantity must be greater than zero."))
        if self.product_id.qty_available > 0:
            raise ValidationError(_("This product is currently in stock."))

    def action_submit_request(self):
        self.ensure_one()
        self._validate_input()
        request_model = self.env["product.stock.notification.request"].sudo()
        notification, created = request_model.create_or_update_pending_request(
            self.product_id,
            self.email,
            self.requested_qty,
            self.website_id,
        )
        return {
            "notification_id": notification.id,
            "created": created,
            "message": _("Notification request created.")
            if created
            else _("Existing pending request updated."),
        }
