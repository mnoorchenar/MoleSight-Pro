# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

# System deps for RDKit and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxrender1 \
    libxext6 \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source
COPY . .

# HuggingFace Spaces runs as non-root user (UID 1000)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose HuggingFace default port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/')"

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", \
     "--timeout", "120", "--preload", "--access-logfile", "-", "app:app"]
