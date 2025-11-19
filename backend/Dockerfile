FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app:/app/..:/app/backend:/app/backend/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# First try to run from backend/main.py directly
CMD ["sh", "-c", "cd /app && uvicorn main:app --host 0.0.0.0 --port 8000 || uvicorn backend.main:app --host 0.0.0.0 --port 8000"]

