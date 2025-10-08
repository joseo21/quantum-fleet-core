FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY collector.py .
ENV API_BASE=http://api:8000
ENV INTERVAL_SEC=30
ENV SOURCES_JSON=[]
CMD ["python", "collector.py"]
