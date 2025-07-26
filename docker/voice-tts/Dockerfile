# AI Video GPU - Voice TTS Container
# Specialized container for voice generation and TTS

FROM nvidia/cuda:12.2-devel-ubuntu22.04

LABEL maintainer="AI-Empower-Cloud"
LABEL description="Voice Generation and TTS - Bark, Tortoise, Coqui, Indic-TTS"

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
    libsndfile1 \
    libsndfile1-dev \
    libffi-dev \
    libssl-dev \
    espeak-ng \
    espeak-ng-data \
    libespeak-ng-dev \
    pulseaudio \
    alsa-utils \
    portaudio19-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY docker/voice-tts/requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install core TTS packages
RUN pip3 install \
    TTS>=0.20.0 \
    bark \
    tortoise-tts \
    XTTS \
    coqui-tts \
    transformers>=4.30.0 \
    librosa>=0.10.0 \
    soundfile>=0.12.0 \
    pydub \
    scipy \
    numpy

# Install advanced voice packages
RUN pip3 install \
    so-vits-svc \
    real-time-voice-cloning \
    resemblyzer \
    speechbrain \
    whisper-openai \
    noisereduce \
    pyroomacoustics \
    webrtcvad \
    phonemizer \
    fairseq

# Install Indic TTS and regional language support
RUN pip3 install \
    ai4bharat-transliteration \
    aksharamukha \
    indic-nlp-library \
    indic-numtowords \
    pyworld \
    nemo_text_processing \
    asteroid \
    numba==0.56.2 \
    protobuf==3.20

# Install neural vocoders
RUN pip3 install \
    vocoder \
    univnet \
    melgan

# Copy application code
COPY src/modules/tts/ ./tts/
COPY src/modules/voice_generation/ ./voice_generation/
COPY src/modules/indic_tts/ ./indic_tts/
COPY src/core/ ./core/
COPY config/voice-tts/ ./config/

# Create directories for models and outputs
RUN mkdir -p /app/models /app/outputs /app/temp /app/cache /app/voices

# Copy the voice TTS service
COPY docker/voice-tts/voice_tts_service.py ./

# Download essential models (this can be optimized with model caching)
RUN python3 -c "
import torch
from TTS.api import TTS
from bark import SAMPLE_RATE, generate_audio, preload_models

# Preload Bark models
print('Preloading Bark models...')
preload_models()

# Download TTS models
print('Downloading TTS models...')
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=torch.cuda.is_available())
print('Models preloaded successfully')
"

# Set permissions
RUN chmod +x /app/voice_tts_service.py

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Start the voice TTS service
CMD ["python3", "voice_tts_service.py"]
