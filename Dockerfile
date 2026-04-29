# ─── Stage 1: Builder ───────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── Stage 2: Runtime ───────────────────────────────────
FROM python:3.11-slim

# Create non-root user (required by HF Spaces)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/
COPY data/ ./data/
COPY README.md .

# Create directory for pre-trained models
RUN mkdir -p app/ml/pretrained && chown -R appuser:appuser /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TRANSFORMERS_CACHE=/tmp/transformers
ENV HF_HOME=/tmp/hf_home
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/st_home

# Expose HF Spaces port
EXPOSE 7860

# Switch to non-root user
USER appuser

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2"]
