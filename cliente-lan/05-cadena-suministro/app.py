import json
import os
import secrets
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

last_run = None
run_lock = threading.Lock()


def simulate():
    manifest = "/app/requirements.txt"
    try:
        result = subprocess.run(
            ["pip-audit", "--requirement", manifest],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 504, {"error": "audit_timeout"}
    except OSError:
        return 500, {"error": "pip_audit_unavailable"}
    output = (result.stdout + result.stderr)[-12000:]
    print(output, flush=True)
    return (200 if result.returncode == 0 else 422), {
        "exit_code": result.returncode,
        "output": output,
    }


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path == "/healthz":
            self.reply(200, {"status": "ok", "module": "05-cadena-suministro"})
        else:
            self.reply(404, {"error": "not_found"})

    def do_POST(self):
        global last_run
        if urlparse(self.path).path != "/run":
            self.reply(404, {"error": "not_found"})
            return
        try:
            body_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            body_length = -1
        if body_length != 0:
            self.close_connection = True
            self.reply(400, {"error": "request_body_not_allowed"})
            return
        token = os.getenv("SIMULATION_TOKEN", "")
        if not token:
            self.reply(503, {"error": "simulation_disabled"})
            return
        if not secrets.compare_digest(self.headers.get("Authorization", ""), "Bearer " + token):
            self.reply(401, {"error": "unauthorized"})
            return
        with run_lock:
            now = time.monotonic()
            if last_run is not None and now - last_run < 60:
                self.reply(429, {"error": "cooldown", "retry_after_seconds": int(60 - (now - last_run))})
                return
            last_run = now
        status, result = simulate()
        self.reply(status, result)

    def log_message(self, format_string, *args):
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        print(f"{timestamp} {self.command} {self.path} {args[0] if len(args) > 0 else ''}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()