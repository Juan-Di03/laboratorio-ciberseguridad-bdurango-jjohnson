FROM alpine:latest

# Instalamos las herramientas necesarias: curl, bind-tools y python3
RUN apk add --no-cache curl bind-tools python3

WORKDIR /app

# Copiamos el script de inicio y le damos permisos de ejecución
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
