import logging
from odoo import models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def write(self, vals):
        """Override write to trigger stock notifications when quantity changes from 0 to positive."""
        # Store products that were out of stock before the update
        products_previously_oos = set()
        
        if 'quantity' in vals or 'reserved_quantity' in vals:
            for quant in self:
                if quant.product_id and quant.location_id.usage == 'internal':
                    available_before = quant.quantity - quant.reserved_quantity
                    if available_before <= 0:
                        products_previously_oos.add(quant.product_id.id)
        
        result = super().write(vals)
        
        # After update, check if any products went from out-of-stock to in-stock
        if products_previously_oos:
            products_now_in_stock = set()
            for quant in self:
                if quant.product_id.id in products_previously_oos:
                    available_after = quant.quantity - quant.reserved_quantity
                    if available_after > 0:
                        products_now_in_stock.add(quant.product_id.id)
            
            # Trigger notifications for products that are now in stock
            if products_now_in_stock:
                self.env['product.stock.notification.request'].sudo()._trigger_notifications_for_products(
                    list(products_now_in_stock)
                )
        
        return result

    def _update_available_quantity(self, product_id, location_id, quantity, *args, **kwargs):
        """Override to catch stock updates via this method as well."""
        # Check if product was out of stock before
        product = self.env['product.product'].browse(product_id)
        was_oos = product.qty_available <= 0 if product else False
        
        result = super()._update_available_quantity(product_id, location_id, quantity, *args, **kwargs)
        
        # Check if product is now in stock
        if was_oos and product:
            product.invalidate_recordset(['qty_available'])
            if product.qty_available > 0:
                self.env['product.stock.notification.request'].sudo()._trigger_notifications_for_products([product_id])
        
        return result
