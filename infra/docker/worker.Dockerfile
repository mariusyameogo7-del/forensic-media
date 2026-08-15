FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System dependencies for ExifTool, WeasyPrint, Pillow, C2PA
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    libmagic1 \
    exiftool \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY workers/analysis/requirements.txt /app/worker-requirements.txt
RUN pip install --no-cache-dir -r /app/worker-requirements.txt

COPY apps/api /app/apps/api
COPY workers/analysis /app/workers/analysis

ENV PYTHONPATH="/app/apps/api:/app/workers/analysis:${PYTHONPATH}"

CMD ["celery", "-A", "worker.celery_app:celery_app", "worker", "--loglevel=info", "-c", "2"]
