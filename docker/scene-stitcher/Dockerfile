# AI Video GPU - Scene Stitcher Container
# FFmpeg, MoviePy, and video composition specialized container

FROM nvidia/cuda:12.2-devel-ubuntu22.04

LABEL maintainer="AI-Empower-Cloud"
LABEL description="Scene Stitcher - FFmpeg, MoviePy, Video Composition"

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:${PATH}
ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install system dependencies including latest FFmpeg
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    software-properties-common \
    && add-apt-repository ppa:jonathonf/ffmpeg-4 \
    && apt-get update \
    && apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    libavdevice-dev \
    x264 \
    x265 \
    libnvidia-encode1 \
    libnvidia-decode1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/scene-stitcher/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Install video processing packages
RUN pip3 install \
    moviepy>=1.0.3 \
    opencv-contrib-python \
    imageio[ffmpeg] \
    imageio-ffmpeg \
    av \
    vidgear \
    ffmpeg-python \
    Pillow \
    numpy \
    scipy \
    matplotlib \
    scikit-image \
    decord

# Install advanced video editing libraries
RUN pip3 install \
    transitions \
    colorama \
    tqdm \
    rich \
    click \
    pydantic

# Install GPU-accelerated libraries
RUN pip3 install \
    cupy-cuda12x \
    numba \
    jinja2

# Copy application code
COPY src/modules/video_composition/ ./video_composition/
COPY src/modules/scene_stitcher/ ./scene_stitcher/
COPY src/modules/transitions/ ./transitions/
COPY src/core/ ./core/
COPY config/scene-stitcher/ ./config/

# Create directories for processing
RUN mkdir -p /app/temp /app/outputs /app/cache /app/templates /app/assets

# Copy FFmpeg configuration and presets
COPY docker/scene-stitcher/ffmpeg_presets/ ./ffmpeg_presets/

# Copy the scene stitcher service
COPY docker/scene-stitcher/scene_stitcher_service.py ./

# Create script for hardware-accelerated encoding
RUN echo '#!/bin/bash\n\
# Hardware-accelerated FFmpeg encoding\n\
ffmpeg -hwaccel cuda -hwaccel_output_format cuda "$@"\n\
' > /usr/local/bin/ffmpeg-cuda && \
chmod +x /usr/local/bin/ffmpeg-cuda

# Set permissions
RUN chmod +x /app/scene_stitcher_service.py

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# Expose port
EXPOSE 8004

# Start the scene stitcher service
CMD ["python3", "scene_stitcher_service.py"]
