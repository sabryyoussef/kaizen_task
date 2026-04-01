# Product Low Stock Notification (Odoo 18)

## Feature Summary
This workspace contains a minimal Odoo 18 addon named website_product_low_stock_notify for website back-in-stock notifications.

Implemented features:
- Notify button on product page when product is out of stock (qty_available <= 0 and out-of-stock ordering disabled)
- Modal form flow to collect email and requested quantity
- Email format validation and quantity validation
- Persistent storage of requests in custom model linked to product
- Duplicate pending handling: same product + same email updates existing pending request
- Send-once notification state handling (pending -> sent)
- Notification email includes product name, current stock, product link, and CTA button
- Cron-based processing to send notifications when stock becomes available
- Backend admin views/menu for request monitoring

## Installation Notes
1. Copy addon folder website_product_low_stock_notify into your Odoo addons path.
2. Update Odoo apps list.
3. Install module Website Product Low Stock Notification.
4. Ensure outbound email is configured in Odoo for template delivery.
5. Confirm scheduled action Process Product Stock Notifications is active.

Dependencies declared in manifest:
- website_sale
- stock
- mail

## Test Scenarios
1. Product out of stock -> Notify button appears.
Expected: Notify button visible on product page.

2. Product in stock -> Notify button does not appear.
Expected: Notify button hidden.

3. Valid email + quantity submission.
Expected: Request stored (new pending or existing pending updated).

4. Invalid email submission.
Expected: Validation error message.

5. Same email requests same product again.
Expected: Existing pending request updated, not duplicated.

6. Stock changes zero -> positive.
Expected: Cron sends notification email.

7. Same request not emailed twice.
Expected: Request state changes to sent and is skipped in later cron runs.

8. Product link in email opens correct page.
Expected: CTA points to product website URL.

Execution note:
- Scenarios are implemented and documented in code and plan.
- Runtime validation requires an actual Odoo 18 instance with website, stock data, and mail setup.