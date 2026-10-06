"""Tiny auth service for Envoy ext_authz (HTTP mode). Envoy sends the original request to /check<path>."""
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKENS = {"Bearer demo-token": "alice"}  # demo only, not a secret


def decide(headers):
    """Return (status, response headers)."""
    user = TOKENS.get(headers.get("Authorization", ""))
    return (200, {"x-user": user}) if user else (403, {})


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, hdrs = decide(self.headers)
        self.send_response(status)
        for k, v in hdrs.items():
            self.send_header(k, v)
        self.end_headers()

    do_POST = do_GET


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 9000), Handler).serve_forever()
