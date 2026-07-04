# ─── Stage 1: Builder ───
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─── Stage 2: Runtime ───
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY intelliquery/ ./intelliquery/
COPY ui/ ./ui/
COPY config.yaml .
COPY data/ ./data/

EXPOSE 7860

# Gradio listens on 0.0.0.0 by default
CMD ["python", "-m", "ui.app"]
