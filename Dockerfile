# Multi-stage Dockerfile for P_098 Emotion Detection
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Create non-root system user
RUN groupadd -r appuser && useradd --create-home --uid 1000 -g appuser appuser

# Copy installed wheels from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy project files
COPY --chown=appuser:appuser . .

# Environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    HF_HOME=/home/appuser/.cache/huggingface \
    LLM_MODE=mock \
    USE_MODELS=1

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
  CMD python -c "import os, urllib.request; port = os.getenv('PORT', os.getenv('FLASK_PORT', '5000')); urllib.request.urlopen('http://localhost:' + port + '/health', timeout=4)"

CMD ["python", "serve.py"]
