FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install minimal OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY apps/api /app/apps/api
COPY workers/analysis /app/workers/analysis

ENV PYTHONPATH="/app:/app/apps/api:/app/workers/analysis:${PYTHONPATH}"

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn apps.api.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
