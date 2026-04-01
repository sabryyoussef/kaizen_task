from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


class WebsiteStockNotifyController(http.Controller):
    def _append_query_params(self, url, params):
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query.update(params)
        return urlunparse(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urlencode(query),
                parsed.fragment,
            )
        )

    @http.route(["/stock_notify/request"], type="http", auth="public", website=True, methods=["POST"], csrf=True)
    def stock_notify_request(self, product_id=None, email=None, requested_qty=1.0, redirect_url=None, **kwargs):
        product = request.env["product.product"].sudo().browse(int(product_id or 0))
        fallback_url = redirect_url or request.httprequest.referrer or "/shop"

        if not product.exists():
            return request.redirect(
                self._append_query_params(
                    fallback_url,
                    {
                        "stock_notify_status": "error",
                        "stock_notify_message": "Product not found.",
                    },
                )
            )

        try:
            wizard = request.env["product.stock.notification.wizard"].sudo().create(
                {
                    "product_id": product.id,
                    "email": email,
                    "requested_qty": float(requested_qty or 0),
                    "website_id": request.website.id,
                }
            )
            result = wizard.action_submit_request()
            status = "success"
            message = result["message"]
        except ValidationError as exc:
            status = "error"
            message = str(exc)

        return request.redirect(
            self._append_query_params(
                fallback_url,
                {
                    "stock_notify_status": status,
                    "stock_notify_message": message,
                },
            )
        )
