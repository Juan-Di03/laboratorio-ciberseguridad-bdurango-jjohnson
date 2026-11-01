# Laboratorio de Ciberseguridad S25

Laboratorio académico modular para demostrar conceptos y controles de seguridad informática sobre servicios propios autorizados. Los módulos cliente exponen únicamente endpoints JSON; no sirven sus directorios de trabajo ni sus scripts.

## Datos académicos

- **Estudiantes:** Brayan Alejandro Durango Urrea y Juan Diego Johnson Posada
- **Institución:** IU Digital de Antioquia
- **Asignatura:** Seguridad informática
- **Grupo:** PREICA2602B020077
- **Docente:** Esteban Betancur Londoño
- **Fecha:** noviembre de 2026
- **Repositorio:** https://github.com/Juan-Di03/laboratorio-ciberseguridad-bdurango-jjohnson

## Arquitectura y estructura

Cada módulo tiene su propio Dockerfile y contexto de construcción. Los servicios `01` a `06` ofrecen `GET /healthz` y aceptan simulaciones solo mediante `POST /run`, un token configurado y un intervalo mínimo de 60 segundos entre ejecuciones. `07` ofrece su health check local y funciona como proxy protegido hacia el host DMZ permitido.

```text
Repositorio (raíz Git)/
├── README.md
└── cliente-lan/
    ├── README.md
    ├── 00-servidor-dmz/          app.py, Dockerfile
    ├── 01-ataque-dos/            app.py, entrypoint.sh, Dockerfile
    ├── 02-escaneo-puertos/       app.py, entrypoint.sh, Dockerfile
    ├── 03-fuerza-bruta-rutas/    app.py, entrypoint.sh, Dockerfile
    ├── 04-exfiltracion-dns/      app.py, entrypoint.sh, Dockerfile
    ├── 05-cadena-suministro/     app.py, entrypoint.sh, requirements.txt, Dockerfile
    ├── 06-credential-stuffing/  app.py, entrypoint.sh, Dockerfile
    └── 07-proxy-mitm/            app.py, requirements.txt, Dockerfile
```

## Módulos

| Módulo | Función | Límites y controles |
|---|---|---|
| `00-servidor-dmz` | Página web, `GET /healthz`, `GET /login`, pruebas controladas (`/test/redirect`, `/test/forbidden`, 404) y `POST /auth`. | Registra fecha UTC, método, ruta y código. Usa usuarios ficticios y limita intentos por IP en memoria. |
| `01-ataque-dos` | `POST /run` genera hasta 10 GET secuenciales a `/healthz`. | Requiere token y host permitido; timeout de 2 s por solicitud, pausa de 1 s y cooldown de 60 s. |
| `02-escaneo-puertos` | `POST /run` revisa TCP 80 y 443. | Requiere token y coincidencia exacta entre `DMZ_HOST` y `AUTHORIZED_DMZ_HOST`; timeout de 2 s por puerto. |
| `03-fuerza-bruta-rutas` | `POST /run` consulta cinco rutas y muestra sus estados HTTP sin seguir redirecciones. | Requiere token y host permitido; máximo cinco solicitudes, timeout de 3 s por ruta y cooldown de 60 s. |
| `04-exfiltracion-dns` | `POST /run` fragmenta un dato ficticio y devuelve consultas de ejemplo. | Requiere token. No consulta DNS ni envía datos; usa `.invalid`. |
| `05-cadena-suministro` | `POST /run` ejecuta `pip-audit` sobre el manifiesto del proxy. | Requiere token y limita la auditoría a 30 s. La consulta de vulnerabilidades necesita conectividad. |
| `06-credential-stuffing` | `POST /run` prueba tres credenciales ficticias contra `/auth`. | Requiere token y host permitido; timeout de 3 s por intento, pausa de 1 s y cooldown de 60 s. |
| `07-proxy-mitm` | Reenvía GET/POST al destino configurado. | `GET /healthz` es local e independiente de la DMZ. El reenvío requiere token y host permitido; timeout de 5 s y cuerpo máximo de 64 KiB. No reenvía cookies ni cabeceras de autenticación. |

El endpoint de autenticación usa exclusivamente cuentas ficticias de demostración definidas en el servicio DMZ. No se deben reutilizar credenciales reales.

## Configuración

Todos los servicios web escuchan en `0.0.0.0` usando `PORT`, cuyo valor predeterminado en las imágenes es `10000`; los Dockerfiles exponen `10000`. En Render, verifica que el valor de `PORT` del servicio coincida con el puerto de escucha.

| Variable | Módulos | Uso |
|---|---|---|
| `PORT` | `00`–`07` | Puerto HTTP; predeterminado `10000`. |
| `ESTUDIANTE_NOMBRE` | `00` | Nombre mostrado en la página DMZ. |
| `DEMO_AUTH_USER`, `DEMO_AUTH_PASSWORD` | `00`, `06` | Credenciales ficticias compartidas para el endpoint `/auth` y la simulación de `06`; configura ambos valores como secretos y nunca en el código. |
| `SIMULATION_TOKEN` | `01`–`06`, `07` | En `01`–`06`, autoriza `POST /run`; en `07`, autoriza las solicitudes reenviadas. Usa `Authorization: Bearer <token>` y un valor secreto distinto por servicio. |
| `DMZ_URL` | `01`, `03`, `06`, `07` | URL base HTTP(S) de la DMZ propia, sin ruta, query ni credenciales. |
| `AUTHORIZED_DMZ_HOST` | `01`, `02`, `03`, `06`, `07` | Nombre de host permitido; debe coincidir con el host de `DMZ_URL` en los módulos que la usan. |
| `DMZ_HOST` | `02` | Host que se escanea; debe coincidir exactamente con `AUTHORIZED_DMZ_HOST`. |

Sin token configurado, las simulaciones quedan deshabilitadas. No uses dominios, cuentas ni datos ajenos al laboratorio.

## Ejecución local con Docker

Ejecuta desde la carpeta `cliente-lan` del repositorio. Construye y arranca primero la DMZ:

```sh
docker build -t s25-dmz ./00-servidor-dmz
docker run --rm -p 8080:10000 -e PORT=10000 s25-dmz
```

Comprueba la salud con `GET http://localhost:8080/healthz`. Construye, por ejemplo, el módulo de rutas. Define previamente `SIMULATION_TOKEN` en el entorno local:

```sh
docker build -t s25-rutas ./03-fuerza-bruta-rutas
docker run --rm -p 8081:10000 -e PORT=10000 -e SIMULATION_TOKEN="$SIMULATION_TOKEN" -e DMZ_URL=http://host.docker.internal:8080 -e AUTHORIZED_DMZ_HOST=host.docker.internal s25-rutas
```

Consulta su salud y solicita explícitamente la simulación:

```sh
curl http://localhost:8081/healthz
curl -X POST -H "Authorization: Bearer $SIMULATION_TOKEN" http://localhost:8081/run
```

En Linux, configura una dirección del host que el contenedor pueda alcanzar. Para `02`, pasa `DMZ_HOST` y `AUTHORIZED_DMZ_HOST` con el mismo host. Usa el mismo patrón para solicitar `/run` en `01`, `02`, `04`, `05` y `06`. `07` requiere `DMZ_URL`, `AUTHORIZED_DMZ_HOST` y token; su health check funciona aunque la DMZ esté caída.

## Despliegue en Render

Crea un servicio web Docker por módulo. Configura las siguientes rutas **relativas a la raíz Git**:

| Módulo | Docker build context | Dockerfile path |
|---|---|---|
| `00` | `cliente-lan/00-servidor-dmz` | `cliente-lan/00-servidor-dmz/Dockerfile` |
| `01` | `cliente-lan/01-ataque-dos` | `cliente-lan/01-ataque-dos/Dockerfile` |
| `02` | `cliente-lan/02-escaneo-puertos` | `cliente-lan/02-escaneo-puertos/Dockerfile` |
| `03` | `cliente-lan/03-fuerza-bruta-rutas` | `cliente-lan/03-fuerza-bruta-rutas/Dockerfile` |
| `04` | `cliente-lan/04-exfiltracion-dns` | `cliente-lan/04-exfiltracion-dns/Dockerfile` |
| `05` | `cliente-lan/05-cadena-suministro` | `cliente-lan/05-cadena-suministro/Dockerfile` |
| `06` | `cliente-lan/06-credential-stuffing` | `cliente-lan/06-credential-stuffing/Dockerfile` |
| `07` | `cliente-lan/07-proxy-mitm` | `cliente-lan/07-proxy-mitm/Dockerfile` |

Guarda `SIMULATION_TOKEN` como variable secreta en cada servicio cliente. Configura `AUTHORIZED_DMZ_HOST` con el host de la DMZ propia y las otras variables que aparecen en la tabla anterior. En `00` y `06`, configura el mismo usuario y contraseña ficticios como secretos `DEMO_AUTH_USER` y `DEMO_AUTH_PASSWORD`. Configura el health check de cada servicio cliente en `/healthz`. No se encontró un `render.yaml`, así que los ajustes actuales del Dashboard no se pudieron comprobar.

Render establece `PORT` para los servicios web y requiere que la aplicación escuche en `0.0.0.0`; mantén alineados `PORT` y `EXPOSE`. [Documentación de Render sobre servicios web y puertos](https://render.com/docs/web-services). Las rutas de `dockerfilePath` y `dockerContext` se especifican relativas a la raíz del repositorio. [Referencia de Docker para Blueprints](https://render.com/docs/blueprint-spec).

## URLs de referencia

Se conservan las URLs que fueron proporcionadas para el proyecto; no se ha verificado su estado ni configuración actual.

- Servicio principal: https://cliente-lan-alejandro-y-diego.onrender.com
- 00 DMZ: https://zero0-servidor-dmz-alejandro-y-diego.onrender.com
- 01 DoS: https://zero1-ataque-dos-alejandro-y-diego.onrender.com
- 02 Escaneo de puertos: https://zero2-escaneo-puertos-alejandro-y-diego.onrender.com
- 03 Fuerza bruta de rutas: https://zero3-fuerza-bruta-rutas-alejandro-y.onrender.com
- 04 Exfiltración DNS: https://zero4-exfiltracion-dns-alejandro-y-diego.onrender.com
- 05 Cadena de suministro: https://zero5-cadena-suministro-alejandro-y-diego.onrender.com
- 06 Credential stuffing: https://zero6-credential-stuffing-alejandro-y.onrender.com
- 07 Proxy MITM: https://zero7-proxy-mitm-alejandro-y-diego.onrender.com

## Validación pendiente

Las modificaciones de esta fase no se han probado en ejecución, no se han construido imágenes y no se han comprobado servicios en Render. Antes de considerar los cambios verificados, construye las ocho imágenes, confirma `GET /healthz`, comprueba que las rutas desconocidas no sirven archivos y prueba `POST /run` con token incorrecto/correcto y destinos que coinciden/no coinciden con el host autorizado. Revisa los logs para confirmar los códigos HTTP y los límites de cada simulación.

## Seguridad y limitaciones

Usa exclusivamente infraestructura autorizada. El token evita ejecuciones anónimas, el destino debe coincidir con el host permitido, y cada operación tiene un límite y cooldown. El token se configura fuera del repositorio. La limitación de ejecuciones es en memoria por instancia y se reinicia con el proceso; no equivale a un control distribuido. La DMZ y las cuentas de demostración no están diseñadas para producción.

## Autores

Brayan Alejandro Durango Urrea y Juan Diego Johnson Posada — IU Digital de Antioquia, Seguridad informática, grupo PREICA2602B020077.