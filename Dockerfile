FROM python:alpine

WORKDIR /app

COPY cliente-lan/00-servidor-dmz/app.py /app/app.py

EXPOSE 8080

CMD ["python", "app.py"]
