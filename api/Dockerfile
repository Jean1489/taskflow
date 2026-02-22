FROM python:3.11-slim

# ----------------------------
# Environment variables
# ----------------------------
ENV PYTHONUNBUFFERED=1\
    PYTHONDONTWRITEBYTECODE=1\
    PORT=8080

# ----------------------------
# Working directory
# ----------------------------
WORKDIR /app


# ----------------------------
# Dependencies first — cache optimization
# ----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------
# Application code
# ----------------------------
COPY . .

# ----------------------------
# Security — non root user
# ----------------------------
RUN useradd -m appuser
USER appuser

# ----------------------------
# Port
# ----------------------------
EXPOSE 8080

# ----------------------------
# Health check
# ----------------------------
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# ----------------------------
# Start application
# ----------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]