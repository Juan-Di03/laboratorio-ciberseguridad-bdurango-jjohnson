FROM python:3.12-alpine

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir pip-audit==2.10.1
COPY requirements.txt /app/requirements.txt
COPY app.py /app/app.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV PORT=10000
EXPOSE 10000
ENTRYPOINT ["/app/entrypoint.sh"]