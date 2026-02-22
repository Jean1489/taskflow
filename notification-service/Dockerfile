FROM python:3.11-slim

# ----------------------------
# Environment variables
# ----------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

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
# Start application
# ----------------------------
CMD ["python", "main.py"]