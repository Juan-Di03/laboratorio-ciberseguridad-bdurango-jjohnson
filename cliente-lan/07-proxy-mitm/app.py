from flask import Flask, Response, request
import os
import requests
import secrets
from urllib.parse import urlparse

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 65536
TIMEOUT_SECONDS = 5


@app.get("/healthz")
def healthz():
    return {"status": "ok", "module": "07-proxy-mitm"}, 200


def target_url(path):
    base = os.getenv("DMZ_URL", "").rstrip("/")
    allowed_host = os.getenv("AUTHORIZED_DMZ_HOST", "").lower()
    parsed = urlparse(base)
    if (parsed.scheme not in ("http", "https") or not parsed.netloc or not allowed_host
            or parsed.hostname is None or parsed.hostname.lower() != allowed_host
            or parsed.path not in ("", "/") or parsed.username or parsed.password or parsed.query or parsed.fragment):
        return None
    suffix = "/" + path if path else "/"
    return base + suffix


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path):
    token = os.getenv("SIMULATION_TOKEN", "")
    if not token:
        return {"error": "proxy_disabled"}, 503
    if not secrets.compare_digest(request.headers.get("Authorization", ""), "Bearer " + token):
        return {"error": "unauthorized"}, 401
    destination = target_url(path)
    if destination is None:
        app.logger.warning("Proxy deshabilitado: DMZ_URL debe coincidir con AUTHORIZED_DMZ_HOST")
        return {"error": "authorized DMZ is not configured"}, 503

    # No se reenvian cookies ni cabeceras de autenticacion del cliente.
    headers = {}
    if request.content_type:
        headers["Content-Type"] = request.content_type
    try:
        upstream = requests.request(
            method=request.method,
            url=destination,
            params=request.args,
            data=request.get_data(cache=False),
            headers=headers,
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
        )
    except requests.RequestException as error:
        app.logger.warning("Fallo de proxy %s %s: %s", request.method, request.path, error)
        return {"error": "unable to contact configured DMZ"}, 502

    app.logger.info("Proxy %s %s -> HTTP %s", request.method, request.path, upstream.status_code)
    content_type = upstream.headers.get("Content-Type", "application/octet-stream")
    return Response(upstream.content, status=upstream.status_code, content_type=content_type)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)