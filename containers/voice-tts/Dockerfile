# AI Voice TTS Container
# Hollywood-level voices with Indic-TTS, Bark, Tortoise, Coqui

FROM nvidia/cuda:12.2-devel-ubuntu22.04

# Metadata
LABEL maintainer="AI Video GPU Team"
LABEL description="AI Voice TTS Service - Hollywood + Indic voices"
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
    espeak-ng \
    espeak-ng-data \
    libsndfile1 \
    libportaudio2 \
    portaudio19-dev \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY containers/voice-tts/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY containers/voice-tts/app.py ./
COPY src/modules/ai_voice_generation_pipeline.py ./modules/
COPY setup_indic_tts.sh ./

# Create necessary directories
RUN mkdir -p /app/models/bark \
             /app/models/tortoise \
             /app/models/coqui \
             /app/models/indic-tts \
             /app/cache \
             /app/output/audio \
             /app/temp \
             /app/logs

# Install Indic TTS models
RUN chmod +x setup_indic_tts.sh && ./setup_indic_tts.sh

# Download and cache initial models
RUN python3 -c "
import warnings
warnings.filterwarnings('ignore')

print('Pre-downloading TTS models...')

# Bark model
try:
    from bark import SAMPLE_RATE, generate_audio, preload_models
    print('Downloading Bark models...')
    preload_models()
    print('Bark models ready')
except Exception as e:
    print(f'Bark setup will complete at runtime: {e}')

# Coqui TTS
try:
    from TTS.api import TTS
    print('Initializing Coqui TTS...')
    tts = TTS('tts_models/en/ljspeech/tacotron2-DDC')
    print('Coqui TTS ready')
except Exception as e:
    print(f'Coqui setup will complete at runtime: {e}')

print('Model pre-download completed')
" || echo "Models will be downloaded at runtime"

# Expose service port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=180s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Start the voice TTS service
CMD ["python3", "app.py"]
