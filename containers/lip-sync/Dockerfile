# AI Lip Sync Container
# Wav2Lip, LipGAN, Real-time lip synchronization

FROM nvidia/cuda:12.2-devel-ubuntu22.04

# Metadata
LABEL maintainer="AI Video GPU Team"
LABEL description="AI Lip Sync Service - Wav2Lip, LipGAN, Real-time sync"
LABEL version="1.0.0"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=/usr/local/cuda/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    unzip \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY containers/lip-sync/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY containers/lip-sync/app.py ./
COPY src/modules/lip_sync_engine.py ./modules/

# Create directories
RUN mkdir -p /app/models/wav2lip \
             /app/models/lipgan \
             /app/cache \
             /app/output/video \
             /app/temp \
             /app/logs

# Clone and setup Wav2Lip
RUN git clone https://github.com/Rudrabha/Wav2Lip.git /app/Wav2Lip && \
    cd /app/Wav2Lip && \
    pip3 install -r requirements.txt

# Download pre-trained models
RUN mkdir -p /app/models/wav2lip && \
    wget -O /app/models/wav2lip/wav2lip_gan.pth \
    "https://iiitaphyd-my.sharepoint.com/personal/radrabha_m_research_iiit_ac_in/_layouts/15/download.aspx?share=EdjI7bZlgApMqsVoEUUXpLsBxqXbn5z8VTmoxp2pgHDo"

# Expose service port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Start the lip sync service
CMD ["python3", "app.py"]
