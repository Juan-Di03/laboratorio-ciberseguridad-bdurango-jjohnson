from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import json
import os
import time
from urllib.parse import urlparse

DEMO_USER = os.getenv("DEMO_AUTH_USER", "")
DEMO_PASSWORD = os.getenv("DEMO_AUTH_PASSWORD", "")
TEST_USERS = {DEMO_USER: DEMO_PASSWORD} if DEMO_USER and DEMO_PASSWORD else {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 60
failed_attempts = {}


class DMZHandler(BaseHTTPRequestHandler):
    server_version = "LaboratorioDMZ/1.0"

    def log_request(self, code="-", size="-"):
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"{timestamp} method={self.command} path={self.path} status={code}", flush=True)

    def send_body(self, status, body, content_type="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            names = escape(os.getenv(
                "ESTUDIANTE_NOMBRE",
                "Brayan Alejandro Durango Urrea y Juan Diego Johnson Posada",
            ))
            page = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Servidor web DMZ - Laboratorio S25</title></head>
<body><main><h1>Servidor objetivo DMZ</h1><p>Estado: ONLINE / ACTIVO</p>
<p>Laboratorio de Ciberseguridad S25: {names}</p>
<p>Endpoints controlados: <code>/healthz</code> y <code>/auth</code>.</p></main></body></html>"""
            self.send_body(200, page, "text/html; charset=utf-8")
        elif path == "/healthz":
            self.send_body(200, json.dumps({"status": "ok", "service": "dmz"}))
        elif path == "/login":
            self.send_body(200, json.dumps({"endpoint": "/auth", "method": "POST", "format": "JSON"}))
        elif path == "/test/redirect":
            self.send_response(301)
            self.send_header("Location", "/")
            self.send_header("Content-Length", "0")
            self.end_headers()
        elif path == "/test/forbidden":
            self.send_body(403, json.dumps({"error": "forbidden"}))
        else:
            self.send_body(404, json.dumps({"error": "not_found"}))

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/auth", "/login"):
            self.send_body(404, json.dumps({"error": "not_found"}))
            return

        client_ip = self.client_address[0]
        now = time.monotonic()
        attempts = [t for t in failed_attempts.get(client_ip, []) if now - t < LOCKOUT_SECONDS]
        if len(attempts) >= MAX_FAILED_ATTEMPTS:
            failed_attempts[client_ip] = attempts
            self.send_body(429, json.dumps({"error": "too_many_attempts"}))
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 4096:
                raise ValueError("invalid body size")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("JSON object required")
            username = str(payload.get("username", ""))
            password = str(payload.get("password", ""))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_body(400, json.dumps({"error": "invalid_json"}))
            return

        if TEST_USERS.get(username) == password:
            failed_attempts.pop(client_ip, None)
            self.send_body(200, json.dumps({"authenticated": True, "user": username}))
        else:
            attempts.append(now)
            failed_attempts[client_ip] = attempts
            self.send_body(401, json.dumps({"authenticated": False, "error": "invalid_credentials"}))

    def do_HEAD(self):
        path = urlparse(self.path).path
        status = 200 if path in ("/", "/healthz", "/login") else 404
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format_string, *args):
        return


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), DMZHandler)
    print(f"Servidor DMZ escuchando en 0.0.0.0:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()