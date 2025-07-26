# AI Video GPU - Video Generator Container
# Specialized container for AnimateDiff, SVD, Gen-2 clones and Hollywood/Bollywood VFX

FROM nvidia/cuda:12.2-devel-ubuntu22.04

# Metadata
LABEL maintainer="AI Video GPU Team"
LABEL description="GenAI Video Generation Service - AnimateDiff, SVD, Gen-2 clones"
LABEL version="1.0.0"

# Set environment variables
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
    libgthread-2.0-0 \
    libgtk-3-0 \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies for video generation
COPY containers/video-generator/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install video generation models and libraries
RUN pip3 install \
    # Core video generation
    diffusers==0.25.0 \
    transformers==4.36.0 \
    accelerate==0.25.0 \
    xformers==0.0.23 \
    # Video models
    animatediff \
    svd-temporal-unet \
    stable-video-diffusion \
    # VFX and effects
    opencv-contrib-python==4.8.1.78 \
    imageio==2.33.1 \
    imageio-ffmpeg==0.4.9 \
    moviepy==1.0.3 \
    # 3D and advanced rendering
    trimesh==4.0.5 \
    moderngl==5.8.2 \
    pyrr==0.10.3 \
    # Hollywood VFX libraries
    scikit-image==0.22.0 \
    pillow-simd==10.0.1 \
    # Professional video codecs
    av==11.0.0

# Copy application code
COPY src/modules/video_generator/ ./modules/video_generator/
COPY src/modules/visual_generation.py ./modules/
COPY src/modules/video_enhancer.py ./modules/
COPY src/core/ ./core/
COPY containers/video-generator/app.py ./

# Create necessary directories
RUN mkdir -p /app/models/animatediff \
             /app/models/svd \
             /app/models/gen2 \
             /app/cache \
             /app/output/video \
             /app/temp \
             /app/logs

# Download base models (will be cached in volumes)
RUN python3 -c "
import torch
from diffusers import StableVideoDiffusionPipeline, AnimateDiffPipeline

# Download and cache SVD model
print('Downloading Stable Video Diffusion model...')
try:
    svd_pipe = StableVideoDiffusionPipeline.from_pretrained(
        'stabilityai/stable-video-diffusion-img2vid-xt',
        torch_dtype=torch.float16,
        cache_dir='/app/models/svd'
    )
    print('SVD model downloaded successfully')
except Exception as e:
    print(f'SVD download error (will retry at runtime): {e}')

# Download AnimateDiff model
print('Downloading AnimateDiff model...')
try:
    animate_pipe = AnimateDiffPipeline.from_pretrained(
        'runwayml/stable-diffusion-v1-5',
        torch_dtype=torch.float16,
        cache_dir='/app/models/animatediff'
    )
    print('AnimateDiff model downloaded successfully')
except Exception as e:
    print(f'AnimateDiff download error (will retry at runtime): {e}')

print('Model download phase completed')
" || echo "Model download will complete at runtime"

# Set permissions
RUN chmod +x /app/app.py

# Expose service port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the video generation service
CMD ["python3", "app.py"]
