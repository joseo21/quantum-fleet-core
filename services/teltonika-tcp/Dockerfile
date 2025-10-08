FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
ENV LISTEN_HOST=0.0.0.0
ENV LISTEN_PORT=5027
ENV API_BASE=http://api:8000
CMD ["python", "server.py"]
