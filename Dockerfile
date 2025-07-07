# AI Video GPU - Production Docker Image
# Multi-stage build optimized for NVIDIA GPUs with CUDA support

# Base stage with CUDA development environment
FROM nvidia/cuda:12.2-devel-ubuntu22.04 AS base

# Set environment variables for optimal GPU performance
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,video
ENV FORCE_CUDA=1
ENV TORCH_CUDA_ARCH_LIST="6.0;6.1;7.0;7.5;8.0;8.6+PTX"

# System dependencies installation
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python and core utilities
    python3.11 python3.11-dev python3.11-venv python3-pip \
    # Build tools
    build-essential cmake ninja-build git wget curl unzip \
    # Audio/Video processing
    ffmpeg libavcodec-dev libavformat-dev libavutil-dev \
    libswscale-dev libswresample-dev \
    # Graphics and OpenGL
    libgl1-mesa-glx libgl1-mesa-dev libglx-mesa0 \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libfontconfig1-dev libfreetype6-dev \
    # Audio processing
    espeak-ng espeak-data libespeak-ng-dev \
    portaudio19-dev libasound2-dev \
    # Image processing
    libjpeg-dev libpng-dev libtiff-dev \
    # System monitoring
    htop nvtop \
    # Threading and parallel processing
    libgomp1 libomp-dev \
    # Networking
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Node.js for additional tooling
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Development stage with additional tools
FROM base AS development

# Install development and debugging tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdb valgrind strace \
    vim nano tmux \
    && rm -rf /var/lib/apt/lists/*

# Production stage
FROM base AS production

# Create application user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Create directory structure with proper permissions
RUN mkdir -p \
    /app/models \
    /app/cache \
    /app/output \
    /app/temp \
    /app/logs \
    /app/data \
    /app/config/runtime \
    && chown -R appuser:appuser /app

# Copy and install Python requirements first (for better caching)
COPY --chown=appuser:appuser requirements.txt requirements-dev.txt ./

# Upgrade pip and install Python dependencies with optimizations
RUN python3.11 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python3.11 -m pip install --no-cache-dir --find-links https://download.pytorch.org/whl/torch_stable.html \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 && \
    python3.11 -m pip install --no-cache-dir -r requirements.txt && \
    python3.11 -m pip cache purge

# Copy application code
COPY --chown=appuser:appuser . .

# Create Python path symlink for compatibility
RUN ln -sf /usr/bin/python3.11 /usr/bin/python

# Pre-download and cache common models
RUN python3.11 -c "
import torch
import transformers
import diffusers
print('GPU available:', torch.cuda.is_available())
print('CUDA version:', torch.version.cuda)
print('PyTorch version:', torch.__version__)
# Pre-cache common models
try:
    from transformers import pipeline
    pipe = pipeline('text-classification', model='distilbert-base-uncased-finetuned-sst-2-english')
    print('Transformers models cached successfully')
except Exception as e:
    print(f'Model caching warning: {e}')
"

# Set executable permissions
RUN chmod +x /app/main.py /app/setup.sh

# Create entrypoint script
RUN cat > /app/entrypoint.sh << 'EOF'
#!/bin/bash
set -e

# Initialize GPU monitoring
echo "Starting AI Video GPU Container..."
echo "CUDA Version: $(nvcc --version | grep release)"
echo "GPU Devices: $(nvidia-smi -L)"
echo "Available GPUs: $(python3 -c 'import torch; print(torch.cuda.device_count())')"

# Initialize models and cache
echo "Initializing models..."
python3 /app/main.py init --quiet

# Health check
echo "Running health check..."
python3 /app/main.py status

# Execute command
exec "$@"
EOF

RUN chmod +x /app/entrypoint.sh && chown appuser:appuser /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose ports for different services
EXPOSE 8000 7860 6006 8080

# Health check with comprehensive GPU validation
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD python3 /app/main.py status --health-check || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - FastAPI server
CMD ["python3", "main.py", "api", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
