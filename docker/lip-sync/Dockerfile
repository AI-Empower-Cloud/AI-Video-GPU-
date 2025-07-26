# AI Video GPU - Lip Sync Container
# Specialized container for lip synchronization (Wav2Lip, SadTalker)

FROM nvidia/cuda:12.2-devel-ubuntu22.04

LABEL maintainer="AI-Empower-Cloud"
LABEL description="Lip Sync Processing - Wav2Lip, SadTalker, Real-time sync"

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
    cmake \
    build-essential \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/lip-sync/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install lip sync specific packages
RUN pip3 install \
    opencv-contrib-python \
    dlib \
    face-recognition \
    mediapipe \
    insightface \
    scipy \
    librosa \
    soundfile \
    pydub \
    imageio[ffmpeg] \
    scikit-image \
    matplotlib \
    yacs

# Install Wav2Lip
RUN git clone https://github.com/Rudrabha/Wav2Lip.git /tmp/wav2lip && \
    cd /tmp/wav2lip && \
    pip3 install -r requirements.txt && \
    cp -r . /app/wav2lip/

# Install SadTalker dependencies
RUN git clone https://github.com/OpenTalker/SadTalker.git /tmp/sadtalker && \
    cd /tmp/sadtalker && \
    pip3 install -r requirements.txt && \
    cp -r . /app/sadtalker/

# Install additional face analysis tools
RUN pip3 install \
    retinaface \
    facexlib \
    gfpgan \
    basicsr \
    lpips

# Copy application code
COPY src/modules/lip_sync/ ./lip_sync/
COPY src/modules/face_analysis/ ./face_analysis/
COPY src/core/ ./core/
COPY config/lip-sync/ ./config/

# Create directories for models and outputs
RUN mkdir -p /app/models /app/outputs /app/temp /app/cache /app/checkpoints

# Download pre-trained models
RUN mkdir -p /app/models/wav2lip && \
    mkdir -p /app/models/sadtalker && \
    mkdir -p /app/models/face_detection

# Copy the lip sync service
COPY docker/lip-sync/lip_sync_service.py ./

# Set permissions
RUN chmod +x /app/lip_sync_service.py

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Expose port
EXPOSE 8003

# Start the lip sync service
CMD ["python3", "lip_sync_service.py"]
