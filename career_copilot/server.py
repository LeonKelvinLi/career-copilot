import hmac
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

WEB = Path(__file__).with_name("web")


def create_server(store, port=8765):
    token = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Do not log profile content, URLs or local tokens.

        def reply(self, code, body, mime="application/json"):
            if mime == "application/json":
                body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

        def authorized(self):
            return hmac.compare_digest(self.headers.get("X-Career-Token", ""), token)

        def do_GET(self):
            if not self.valid_host():
                return self.reply(403, {"error": "Open the printed 127.0.0.1 address"})
            path = urlsplit(self.path).path
            if path == "/api/state":
                if not self.authorized():
                    return self.reply(403, {"error": "Reload the dashboard"})
                return self.reply(200, store.state())
            files = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"), "/style.css": ("style.css", "text/css")}
            if path not in files:
                return self.reply(404, {"error": "Not found"})
            name, mime = files[path]
            body = (WEB / name).read_bytes().replace(b"__CAREER_TOKEN__", token.encode())
            self.reply(200, body, mime)

        def do_POST(self):
            origin = f"http://127.0.0.1:{self.server.server_port}"
            if not self.valid_host() or self.headers.get("Origin") != origin or not self.authorized():
                return self.reply(403, {"error": "Request must come from the local dashboard"})
            try:
                if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                    raise ValueError("JSON required")
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 1_000_000:
                    raise ValueError("Invalid request size")
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("Request must be an object")
                path = urlsplit(self.path).path
                if path == "/api/profile":
                    result = store.patch_profile(data)
                elif path in ("/api/application", "/api/task"):
                    item_id = data.pop("id", None)
                    if item_id is not None and (type(item_id) is not int or item_id < 1):
                        raise ValueError("Invalid record ID")
                    method = store.application if path == "/api/application" else store.task
                    result = {"id": method(data, item_id)}
                else:
                    return self.reply(404, {"error": "Not found"})
                self.reply(200, result)
            except (ValueError, TypeError) as exc:
                self.reply(400, {"error": str(exc)})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(store, port, open_browser=False):
    with create_server(store, port) as server:
        url = f"http://127.0.0.1:{server.server_port}"
        print(f"Career Copilot: {url}\nPrivate storage: {store.directory.resolve()}\nPress Ctrl+C to stop.", flush=True)
        if open_browser:
            webbrowser.open(url)
        server.serve_forever()
