# Website Product Low Stock Notify - Step-by-Step Build Guide

This guide explains how to build the module manually (human workflow), using your current implementation as the reference, including correction steps for the Odoo 18 issues you faced.

## 1. Create the module structure

Create a module folder named `website_product_low_stock_notify` with this structure:

- `__init__.py`
- `__manifest__.py`
- `models/`
- `controllers/`
- `wizards/`
- `views/`
- `data/`
- `security/`

## 2. Create the manifest

In `__manifest__.py`:

- Set module metadata: name, version, summary, category.
- Add dependencies: `website_sale`, `stock`, `mail`.
- Add data files in proper load order:
  1. security access file
  2. mail template
  3. cron
  4. website/backend views and menu

Why this matters:
- If load order is wrong, referenced records (model/action/template IDs) may not exist yet.

## 3. Wire Python package imports

In these files, import submodules so Odoo loads them:

- `website_product_low_stock_notify/__init__.py`
- `website_product_low_stock_notify/models/__init__.py`
- `website_product_low_stock_notify/controllers/__init__.py`
- `website_product_low_stock_notify/wizards/__init__.py`

## 4. Build the persistent model

Create `models/stock_notification_request.py` with model:

- `_name = "product.stock.notification.request"`
- Fields:
  - `product_id`
  - `product_tmpl_id` (related)
  - `email`
  - `email_normalized`
  - `requested_qty`
  - `state` (`pending`, `sent`)
  - `sent_date`
  - `website_id`

Add constraints:

- SQL: quantity must be positive.
- Python: email must not be empty after trim.
- Python: one pending request per `(product_id, email_normalized)`.

Add normalization behavior:

- In `create`: trim email and set `email_normalized`.
- In `write`: if email changes, update normalized email too.

Add main methods:

- `create_or_update_pending_request(...)`:
  - if matching pending request exists, update it
  - else create new one
- `get_product_url()`:
  - return website-safe URL for email CTA
- `process_pending_notifications()`:
  - find pending rows
  - if product is now in stock, send mail
  - set state to `sent` and write `sent_date`

## 5. Build the transient wizard

Create `wizards/notification_wizard.py` with model:

- `_name = "product.stock.notification.wizard"`

Fields:

- `product_id`, `email`, `requested_qty`, `website_id`

Validation method (`_validate_input`):

- email format is valid
- quantity > 0
- product is currently out of stock

Submit method (`action_submit_request`):

- call model `create_or_update_pending_request`
- return response payload with success message and created/updated flag

Why wizard is useful:
- keeps validation/business checks centralized before writing to persistent model.

## 6. Build website controller

Create `controllers/main.py`:

- POST route: `/stock_notify/request`
- `auth="public"`, `website=True`, `csrf=True`

Flow:

1. Resolve product from `product_id`.
2. Build fallback redirect URL.
3. If product not found: redirect with error query params.
4. Create wizard with submitted data.
5. Call `action_submit_request()`.
6. Catch `ValidationError` and redirect with error message.
7. Redirect back with status/message in query string.

Helper method:

- `_append_query_params(url, params)` to preserve existing query params safely.

## 7. Add website UI (button + modal + alert)

Create/maintain `views/website_templates.xml` inheriting `website_sale.product`.

Inject near add-to-cart area:

- status alert block (success/error message)
- Notify button when product is out of stock
- Bootstrap modal with form fields:
  - email
  - requested quantity
  - hidden CSRF token
  - hidden product_id
  - hidden redirect URL

## 8. Add backend views and action

In `views/stock_notification_request_views.xml`:

- Tree view for list monitoring
- Form view for detail inspection
- Window action for menu binding

## 9. Add backend menu

In `views/menu.xml`:

- root menu: Stock Notifications
- child menu: Requests
- connect to action from previous step

## 10. Add access rights

In `security/ir.model.access.csv`:

- access for `product.stock.notification.request`
- access for `product.stock.notification.wizard`
- scope to internal users (`base.group_user`)

## 11. Add email template

In `data/mail_template.xml`:

- model: notification request
- subject with product name
- recipient: request email
- body with product name, stock qty, and product link
- optional `auto_delete=True`

## 12. Add cron job

In `data/cron.xml`:

- model: `product.stock.notification.request`
- code: `model.process_pending_notifications()`
- interval: every 15 minutes
- active: true

## 13. Module test checklist

After install/upgrade:

1. Open an out-of-stock product page.
2. Confirm Notify button appears.
3. Submit valid email + quantity.
4. Confirm backend request record is created.
5. Restock product.
6. Run cron or wait schedule.
7. Confirm email sent and state switched to `sent`.

---

## Correction steps based on your actual errors

### A) Error: Invalid field `numbercall` on model `ir.cron`

Cause:
- In Odoo 18, `numbercall` is no longer a valid `ir.cron` field.

Fix:
- Remove this line from cron XML:

```xml
<field name="numbercall">-1</field>
```

Result:
- Cron works with default behavior (runs indefinitely unless disabled).

### B) Error: XPath target cannot be located

Error seen:
- `//section[contains(@class, 'oe_website_sale')]` not found in parent template.

Cause:
- Parent template structure differs in this Odoo version.

Fix:
- Anchor to a stable existing node in `website_sale.product`, such as:

```xml
<xpath expr="//div[@id='add_to_cart_wrap']" position="after">
```

Result:
- View inheritance applies successfully.

### C) Warning: Error-prone use of `@class` in XPath

Cause:
- Newer Odoo warns against `contains(@class, ...)` because class matching can be fragile.

Fix options:

1. Prefer stable IDs when available (best).
2. If class matching is required, use `hasclass('class_name')`.

Result:
- Cleaner, more robust template inheritance.

---

## Practical implementation tips

- Keep controller thin; put validation in wizard/model.
- Normalize emails to avoid duplicate logical requests.
- Keep one pending request per product+email to prevent spam.
- Always test XML inheritance after Odoo upgrades.
- Use explicit, stable XPath anchors (ID-based whenever possible).
