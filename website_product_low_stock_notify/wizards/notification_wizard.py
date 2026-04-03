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
        
        # Comprehensive email validation
        if not email_clean:
            raise ValidationError(_("Email address is required."))
        
        if not tools.single_email_re.fullmatch(email_clean):
            raise ValidationError(_("Please provide a valid email address format."))
        
        # Check for common invalid patterns
        if email_clean.count('@') != 1:
            raise ValidationError(_("Email must contain exactly one @ symbol."))
        
        local, domain = email_clean.rsplit('@', 1)
        if not local or not domain or '.' not in domain:
            raise ValidationError(_("Please provide a valid email address with a proper domain."))
        
        if self.requested_qty <= 0:
            raise ValidationError(_("Quantity must be greater than zero."))
        
        # Remove the "product already in stock" validation to avoid race conditions
        # Instead, let the notification system handle it gracefully

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
