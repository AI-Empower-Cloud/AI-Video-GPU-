# AI Video GPU - API Backend Container
# FastAPI backend with orchestration

FROM python:3.11-slim

LABEL maintainer="AI-Empower-Cloud"
LABEL description="API Backend - FastAPI with Orchestration"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    wget \
    redis-tools \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/api-backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/api/ ./api/
COPY src/core/ ./core/
COPY src/models/ ./models/
COPY src/utils/ ./utils/
COPY config/api/ ./config/

# Copy the API backend service
COPY docker/api-backend/api_backend_service.py ./

# Create directories
RUN mkdir -p /app/uploads /app/downloads /app/cache /app/logs

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting AI Video GPU API Backend..."\n\
\n\
# Wait for Redis\n\
echo "⏳ Waiting for Redis..."\n\
while ! redis-cli -h redis ping > /dev/null 2>&1; do\n\
    sleep 1\n\
done\n\
echo "✅ Redis is ready"\n\
\n\
# Start the API server\n\
echo "🌐 Starting API server on port 8006..."\n\
exec python3 api_backend_service.py\n\
' > /app/start.sh && \
chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8006/health || exit 1

# Expose port
EXPOSE 8006

# Start the API backend
CMD ["/app/start.sh"]
