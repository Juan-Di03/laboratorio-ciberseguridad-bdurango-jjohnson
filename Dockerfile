FROM python:alpine

WORKDIR /app

COPY cliente-lan/00-servidor-dmz/app.py /app/app.py
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
