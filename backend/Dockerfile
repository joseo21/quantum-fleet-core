FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
# Como el contexto es ./backend, requirements.txt está en la raíz del contexto
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos TODO el contenido del contexto (./backend) a /app
COPY . /app

# En dev puedes usar --reload; si consume CPU, quítalo.
CMD ["uvicorn", "app.main:app", "--host","0.0.0.0","--port","8000","--workers","2","--reload"]

