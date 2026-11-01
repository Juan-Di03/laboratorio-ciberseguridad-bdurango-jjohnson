FROM python:3.12-alpine

WORKDIR /app
COPY app.py /app/app.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PORT=10000
EXPOSE 10000
ENTRYPOINT ["/app/entrypoint.sh"]