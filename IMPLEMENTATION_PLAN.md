# Product Low Stock Notification - Implementation Plan

## 1. Objective
Implement a minimal, production-minded Odoo 18 module that allows website visitors to request a back-in-stock notification for out-of-stock products and receive a single email once stock is available again.

## 2. Scope
Included:
- Website product page Notify button for out-of-stock products
- User input flow to collect email and quantity
- Email format validation
- Persistent notification request storage linked to product
- Send-once email notification when stock becomes available
- Email template with product details and CTA link
- Admin visibility of requests
- Cron-driven processing to minimize stock core coupling

Excluded:
- Complex marketing automation workflows
- Multi-channel notifications (SMS, push)
- Real-time stock event hooks into core stock internals
- Advanced segmentation or recommendation logic

## 3. Functional Requirements
- Show Notify button on product page only when product stock is zero/out-of-stock.
- Open a user input flow (wizard-equivalent website modal/form).
- Collect email and requested quantity.
- Validate email format before storing.
- Store request in custom model linked to product.
- Detect stock availability change from zero to positive and send email.
- Ensure each request is emailed only once.
- Email content includes product name, current stock, product page URL, and CTA button.

## 4. Technical Design
Minimal architecture:
- Website button: inherit website_sale product template and inject Notify button/modal.
- Input flow: lightweight website modal form posting to website controller route (wizard-equivalent).
- Custom model: persistent request model with state tracking.
- Mail template: XML mail.template referencing request record and product fields.
- Stock availability trigger: scheduled cron scans pending requests with available stock and sends template.
- Notification engine: model method processes pending records, sends mail, marks as sent with timestamp.

## 5. Minimal-Code Approach
Reuse standard Odoo features:
- website_sale product page template inheritance
- mail.template and mail subsystem for email delivery
- ir.cron for periodic processing
- Odoo ORM constraints and model methods
- Existing stock quantity fields on product.product

Unavoidable custom code:
- Custom request model
- Small website controller/form handler
- Template extension for Notify button/modal
- Cron processing method and send-once state handling

## 6. Data Model
Model: product.stock.notification.request
- product_id (Many2one to product.product, required)
- product_tmpl_id (Many2one to product.template, related/stored for convenience)
- email (Char, required)
- requested_qty (Float, required, default 1.0)
- state (Selection: pending, sent; default pending)
- sent_date (Datetime)
- website_id (Many2one to website)
- create_date / write_date (standard audit)

Behavior notes:
- Pending request can be deduplicated per product_id + normalized email.
- Send-once guaranteed by state transition pending -> sent.

## 7. UI Plan
- Add Notify button near purchase actions on website product page.
- Show button only when displayed product is out of stock.
- Button opens Bootstrap modal with form fields: email + quantity.
- Submit posts to website route; success/error feedback shown on product page.

## 8. Notification Logic
- Cron job periodically selects requests where state = pending.
- For each request, check product stock (qty_available > 0).
- If available: send mail via template and mark state = sent with sent_date.
- If not available: keep pending.
- Send-once guarantee: only pending requests are processed; sent requests are never reprocessed.

## 9. Email Template Plan
Template variables:
- Product name: object.product_id.display_name
- Current stock: object.product_id.qty_available
- Product link: computed helper method for website URL
- CTA button: HTML anchor to product URL

## 10. File-by-File Plan
Planned module: website_product_low_stock_notify
- website_product_low_stock_notify/__init__.py
- website_product_low_stock_notify/__manifest__.py
- website_product_low_stock_notify/models/__init__.py
- website_product_low_stock_notify/models/stock_notification_request.py
- website_product_low_stock_notify/wizards/__init__.py
- website_product_low_stock_notify/wizards/notification_wizard.py
- website_product_low_stock_notify/controllers/__init__.py
- website_product_low_stock_notify/controllers/main.py
- website_product_low_stock_notify/security/ir.model.access.csv
- website_product_low_stock_notify/data/mail_template.xml
- website_product_low_stock_notify/data/cron.xml
- website_product_low_stock_notify/views/website_templates.xml
- website_product_low_stock_notify/views/stock_notification_request_views.xml
- website_product_low_stock_notify/views/menu.xml

## 11. Risks / Decisions
Decisions:
- Use cron instead of deep stock hooks to minimize coupling and upgrade risk.
- Use modal website form instead of heavy JS app or deep checkout integration.
- Keep duplicate handling simple and explicit.

Risks:
- Variant stock display behavior may differ with complex product configurations.
- Public website submissions may need anti-spam hardening in future.
- Multi-website URL generation must be handled carefully.

## 12. Step-by-Step Execution Checklist
- [x] Step 1: Prepare/update module manifest and dependencies
- [x] Step 2: Create security access
- [x] Step 3: Create custom notification request model
- [x] Step 4: Create wizard/transient model (or equivalent minimal website flow)
- [x] Step 5: Create backend methods for request creation and validation
- [x] Step 6: Add website product page button
- [x] Step 7: Add popup/form flow for email + quantity
- [x] Step 8: Create mail template
- [x] Step 9: Implement notification sending logic
- [x] Step 10: Add cron job
- [x] Step 11: Add admin views for stored requests
- [x] Step 12: Test scenarios and document results
- [x] Step 13: Final cleanup and update plan file

## 13. Status Log
- 2026-04-01: Plan initialized. Awaiting workspace analysis before coding.

## Analysis Findings
### Workspace Analysis
- Workspace currently contains only README.md and this plan file.
- No existing Odoo addon/module scaffold detected.
- No existing website_sale customization to extend.
- No dependency manifest files (requirements, pyproject, setup) detected.

### Project Type Identification
- This is a new module implementation in a clean workspace.

### Available/Required Dependencies
- Target Odoo dependencies to declare in addon manifest: website_sale, stock, mail.
- No external Python dependency is required for this implementation.

### Refined Plan Based on Findings
- Create a standalone addon folder website_product_low_stock_notify from scratch.
- Keep implementation self-contained and avoid cross-module assumptions.
- Use cron-based availability processing as default notification trigger.

- 2026-04-01: Workspace analysis completed. Confirmed new module setup is required. Proceeding to Step 1 implementation.
- 2026-04-01: Step 1 completed. Created module scaffold and manifest with dependencies website_sale, stock, mail. Next action: implement security access rules.
- 2026-04-01: Step 2 completed. Added ACL entries for request model and transient wizard model. Next action: implement persistent request model fields and constraints.
- 2026-04-01: Step 3 completed. Implemented request model fields, normalization, pending-duplicate constraint, and positive quantity check. Next action: create transient wizard model for website submission flow.
- 2026-04-01: Step 4 completed. Added transient wizard model with product/email/quantity/website fields for input flow. Next action: implement backend creation and validation methods.
- 2026-04-01: Step 5 completed. Added wizard validation (email, quantity, out-of-stock check) and backend create/update method for pending requests. Duplicate pending requests now update existing record. Next action: add website product page Notify button.
- 2026-04-01: Step 6 completed. Added Notify button on website product page using template inheritance, visible only when variant stock is zero and out-of-stock ordering is disabled. Next action: implement popup/form submission flow.
- 2026-04-01: Step 7 completed. Added modal form for email/quantity input and website controller POST route to process submissions and show feedback message via query params. Next action: define mail template for notification content.
- 2026-04-01: Step 8 completed. Added mail template with product name, current stock, and CTA product link. Next action: implement backend send-once notification processing logic.
- 2026-04-01: Step 9 completed. Added send-once processing method for pending requests with stock check, mail template dispatch, sent timestamp update, and exception logging. Next action: add scheduled cron trigger.
- 2026-04-01: Step 10 completed. Added ir.cron scheduled action to process pending notifications every 15 minutes. Next action: add backend list/form views and menu.
- 2026-04-01: Step 11 completed. Added backend tree/form views, action, and menu entries to manage notification requests. Next action: execute scenario-based test checklist and document results.
- 2026-04-01: Step 12 completed. Documented required test scenarios and expected outcomes; runtime execution was not performed in this workspace because Odoo server/database is not available here.
- 2026-04-01: Step 13 completed. Final cleanup done and plan finalized with implementation details, test notes, and decisions.

### Test Scenario Results
1. Product is out of stock -> Notify button appears.
Status: Implemented by template condition using current variant qty_available <= 0 and allow_out_of_stock_order = False. Runtime execution pending.

2. Product is in stock -> Notify button does not appear.
Status: Implemented by inverse of the same template condition. Runtime execution pending.

3. User submits valid email and quantity -> request stored.
Status: Implemented through controller + wizard + model create/update logic. Runtime execution pending.

4. Invalid email -> validation error.
Status: Implemented in wizard _validate_input() using tools.single_email_re.fullmatch(). Runtime execution pending.

5. Same email requests same product again -> expected business rule documented and handled.
Status: Implemented as update existing pending request (no duplicate pending row), with success message indicating update. Runtime execution pending.

6. Stock changes from zero to positive -> email sent.
Status: Implemented in process_pending_notifications() with qty_available > 0 check and template send. Runtime execution pending.

7. Same request is not emailed twice.
Status: Implemented by state transition pending -> sent and processing only pending state. Runtime execution pending.

8. Product link in email opens correct product page.
Status: Implemented with get_product_url() using product template website_url and website/base URL. Runtime execution pending.
