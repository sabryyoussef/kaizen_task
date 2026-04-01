{
    "name": "Website Product Low Stock Notification",
    "summary": "Back-in-stock notifications for out-of-stock website products",
    "version": "18.0.1.0.0",
    "category": "Website/Website",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["website_sale", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_template.xml",
        "data/cron.xml",
        "views/website_templates.xml",
        "views/stock_notification_request_views.xml",
        "views/menu.xml"
    ],
    "demo": [
        "demo/stock_notify_demo.xml"
    ],
    "installable": True,
    "application": False,
}
