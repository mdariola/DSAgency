FROM python:3.11-slim

WORKDIR /app

# Esta línea es la clave que permite que los imports 'backend.' funcionen
ENV PYTHONPATH="${PYTHONPATH}:/app"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend /app/backend
COPY ./frontend/dist /app/static

EXPOSE 8000

# LÍNEA NUEVA Y CORREGIDA
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]