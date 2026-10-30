from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        # Personalizar con el nombre del estudiante / grupo
        estudiante = os.getenv("ESTUDIANTE_NOMBRE", "Estudiante / Grupo Demo")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Servidor Web DMZ</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
                .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; }}
                .status {{ color: #27ae60; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛡️ Servidor Objetivo DMZ</h1>
                <p>Estado del servicio: <span class="status">ONLINE / ACTIVO</span></p>
                <hr>
                <p><strong>Laboratorio de Ciberseguridad:</strong> {estudiante}</p>
                <p>Este nodo actúa como objetivo central para las pruebas de tráfico y análisis de logs.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html_content.encode("utf-8"))

if __name__ == "__main__":
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, CustomHandler)
    print("Servidor DMZ iniciado y escuchando en el puerto 8080...")
    httpd.serve_forever()
