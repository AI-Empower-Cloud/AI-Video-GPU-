# AI Video GPU - Video Generator Container
# AnimateDiff, SVD, Gen-2 clones specialized container

FROM nvidia/cuda:12.2-devel-ubuntu22.04

LABEL maintainer="AI-Empower-Cloud"
LABEL description="GenAI Video Generation - AnimateDiff, SVD, Gen-2 clones"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libgstreamer1.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/video-generator/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install video generation specific packages
RUN pip3 install \
    diffusers>=0.25.0 \
    transformers>=4.30.0 \
    accelerate>=0.20.0 \
    xformers>=0.0.20 \
    controlnet-aux \
    invisible-watermark \
    safetensors \
    opencv-contrib-python \
    imageio[ffmpeg] \
    imageio-ffmpeg \
    av \
    decord \
    einops \
    omegaconf \
    pytorch-lightning \
    kornia

# Install AnimateDiff dependencies
RUN git clone https://github.com/guoyww/AnimateDiff.git /tmp/animatediff && \
    cd /tmp/animatediff && \
    pip3 install -r requirements.txt

# Install Stable Video Diffusion
RUN pip3 install git+https://github.com/Stability-AI/generative-models.git

# Copy application code
COPY src/modules/video_generation/ ./video_generation/
COPY src/modules/animatediff/ ./animatediff/
COPY src/modules/svd/ ./svd/
COPY src/core/ ./core/
COPY config/video-generator/ ./config/

# Create directories for models and outputs
RUN mkdir -p /app/models /app/outputs /app/temp /app/cache

# Copy the video generator service
COPY docker/video-generator/video_generator_service.py ./

# Set permissions
RUN chmod +x /app/video_generator_service.py

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Start the video generation service
CMD ["python3", "video_generator_service.py"]
