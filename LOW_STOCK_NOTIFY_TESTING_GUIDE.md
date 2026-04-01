# Website Product Low Stock Notify - Testing Guide

This guide provides practical manual test scenarios for the module.

## 1. Scope

Test coverage includes:

- Website product page behavior (Notify button visibility)
- Request submission and validation
- Duplicate request handling
- Backend visibility and access rights
- Cron processing when stock is replenished
- Email notification flow

## 2. Test Environment Setup

Use this setup before running scenarios:

1. Module installed and upgraded.
2. Website and Shop app enabled.
3. Mail server configured (or test mail capture available).
4. At least one stockable product variant exists.
5. You have an internal user for backend verification.

Recommended test product baseline:

- Product name: Three-Seat Sofa
- Product type: Stockable Product
- Website published: Yes
- Out-of-stock selling disabled

## 3. Core Data Preparation

Prepare two product states for testing:

### State A: Out of stock

1. Set product On Hand quantity to 0.
2. Confirm out-of-stock selling is disabled.
3. Open product website page and keep URL for repeated tests.

### State B: Back in stock

1. Set product On Hand quantity to greater than 0 (for example 10).
2. Save product.

## 4. Manual Test Scenarios

## TC-01: Notify button appears for out-of-stock product

Preconditions:

- Product is in State A.

Steps:

1. Open the product page on website.
2. Locate add-to-cart section.

Expected result:

1. Notify button is visible.
2. Add-to-cart purchase path is not the primary path for unavailable stock.

## TC-02: Notify button is hidden when product is in stock

Preconditions:

- Product is in State B.

Steps:

1. Open the same product page.

Expected result:

1. Notify button is not visible.
2. Regular purchase controls are shown.

## TC-03: Submit valid notification request

Preconditions:

- Product is in State A.

Steps:

1. Click Notify.
2. Enter valid email (example: qa.user@example.com).
3. Enter quantity 1.
4. Submit.

Expected result:

1. Redirect returns to product page.
2. Success message appears.
3. One pending request record is created in backend list.

## TC-04: Reject invalid email

Preconditions:

- Product is in State A.

Steps:

1. Click Notify.
2. Enter invalid email (example: qa.user@).
3. Enter quantity 1.
4. Submit.

Expected result:

1. Error message appears.
2. No request record is created.

## TC-05: Reject zero or negative quantity

Preconditions:

- Product is in State A.

Steps:

1. Click Notify.
2. Enter valid email.
3. Enter quantity 0 and submit.
4. Repeat with quantity -1.

Expected result:

1. Validation error is shown each time.
2. No request record is created.

## TC-06: Duplicate pending request updates existing row

Preconditions:

- Product is in State A.
- One pending request already exists for same product and email.

Steps:

1. Submit Notify again with same email.
2. Change requested quantity to a different value (example: 3).

Expected result:

1. Existing pending request is updated.
2. No duplicate pending record for same product + email.
3. Message indicates created or updated behavior correctly.

## TC-07: Product not found handling

Preconditions:

- You can submit a crafted request with invalid product id.

Steps:

1. Send submit request with invalid product identifier.
2. Observe redirected page.

Expected result:

1. Error status message is shown.
2. No request record is created.
3. System remains stable with no server crash.

## TC-08: Backend list and form visibility

Preconditions:

- Internal user logged in.
- At least one request exists.

Steps:

1. Open Stock Notifications menu.
2. Open Requests list view.
3. Open one request form.

Expected result:

1. List shows key columns (product, email, qty, state, sent date, website).
2. Form opens successfully.
3. No access rights error is raised for internal user.

## TC-09: Cron skips still out-of-stock requests

Preconditions:

- Pending request exists.
- Product still has stock 0.

Steps:

1. Run scheduled action manually for notification processing.
2. Reload the request.

Expected result:

1. State remains pending.
2. Sent date remains empty.
3. No notification email is sent.

## TC-10: Cron sends notification when stock is replenished

Preconditions:

- Pending request exists.
- Product moved to State B.

Steps:

1. Run scheduled action manually.
2. Reload the request record.
3. Verify outgoing email record/mailbox.

Expected result:

1. State changes from pending to sent.
2. Sent date is populated.
3. Email is delivered/queued to request email.

## 5. Regression Checklist After Any Code Change

Run this quick pass after controller, wizard, model, XML, or cron edits:

1. Module upgrades without XML/registry errors.
2. Website product page loads without template traceback.
3. Notify button behavior still follows stock and policy rules.
4. Form submit works and returns clear status message.
5. Duplicate logic still prevents duplicate pending rows.
6. Cron still processes only eligible pending rows.
7. Email template still renders product name and product link.

## 6. Useful Troubleshooting Signals

If tests fail, check:

- Module update logs for XML parse/view inheritance errors.
- Invalid field errors in data files (especially cron).
- View architecture errors for list/form tags.
- Access rights issues in model access CSV.
- Mail template external id resolution and email queue state.

## 7. Suggested Evidence to Capture

For each test case, capture:

1. Screenshot of website outcome (button/message/modal).
2. Screenshot of backend request row.
3. Cron run timestamp and request state before/after.
4. Email proof (mail queue entry or received email).

## 8. Exit Criteria

Testing is considered complete when:

1. All critical scenarios (TC-01, TC-03, TC-06, TC-10) pass.
2. No blocking errors appear during module upgrade.
3. No data integrity issue is found for pending request uniqueness.
4. User-facing messages are clear for both success and error paths.
