FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# ROLE menentukan app mana yang di-serve: api atau worker. Image-nya sama.
ENV ROLE=api PORT=8080
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
