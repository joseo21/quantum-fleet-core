FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el server actualizado
COPY server.py .

# Defaults (se sobreescriben desde compose)
ENV TCP_HOST=0.0.0.0
ENV TCP_PORT=5027
ENV API_BASE=http://api:8000
ENV LOG_LEVEL=INFO

CMD ["python", "server.py"]
