FROM alpine:latest

# Instalamos bind-tools (para nslookup/dig), curl y python3
RUN apk add --no-cache bind-tools curl python3

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
