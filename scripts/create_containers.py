#!/usr/bin/env python3
"""
Container Builder for AI Video GPU Microservices
Creates Docker containers for all microservices components
"""

import os
import yaml
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContainerBuilder:
    def __init__(self):
        self.base_dir = Path("/workspaces/AI-Video-GPU-")
        self.containers_dir = self.base_dir / "containers"
        self.containers_dir.mkdir(exist_ok=True)

    def create_video_generator_container(self):
        """Create video generator container"""
        container_dir = self.containers_dir / "video-generator"
        container_dir.mkdir(exist_ok=True)
        
        # Dockerfile for Video Generator
        dockerfile_content = """
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-dev \\
    ffmpeg \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    git \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install video generation specific packages
RUN pip3 install \\
    diffusers \\
    transformers \\
    accelerate \\
    xformers \\
    opencv-python \\
    imageio \\
    imageio-ffmpeg \\
    moviepy \\
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8001/health || exit 1

# Start the service
CMD ["python3", "-m", "src.services.video_generator_service"]
"""
        
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Requirements for video generator
        requirements_content = """
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0
diffusers==0.21.4
transformers==4.35.2
accelerate==0.24.1
xformers==0.0.22.post7
opencv-python==4.8.1.78
imageio==2.31.5
imageio-ffmpeg==0.4.9
moviepy==1.0.3
pillow==10.1.0
numpy==1.24.4
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
pydantic==2.5.0
"""
        
        with open(container_dir / "requirements.txt", 'w') as f:
            f.write(requirements_content)

    def create_voice_tts_container(self):
        """Create voice TTS container"""
        container_dir = self.containers_dir / "voice-tts"
        container_dir.mkdir(exist_ok=True)
        
        # Dockerfile for Voice TTS
        dockerfile_content = """
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-dev \\
    ffmpeg \\
    libsndfile1 \\
    libsndfile1-dev \\
    libportaudio2 \\
    libportaudiocpp0 \\
    portaudio19-dev \\
    git \\
    wget \\
    curl \\
    espeak-ng \\
    espeak-ng-data \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install TTS specific packages
RUN pip3 install \\
    TTS \\
    tortoise-tts \\
    bark \\
    coqui-tts \\
    whisper-openai \\
    librosa \\
    soundfile \\
    pydub \\
    speechbrain \\
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8002/health || exit 1

# Start the service
CMD ["python3", "-m", "src.services.voice_tts_service"]
"""
        
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Requirements for voice TTS
        requirements_content = """
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0
TTS==0.20.6
transformers==4.35.2
librosa==0.10.1
soundfile==0.12.1
pydub==0.25.1
speechbrain==0.5.16
whisper-openai==1.1.10
numpy==1.24.4
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
pydantic==2.5.0
phonemizer==3.2.1
matplotlib==3.8.2
"""
        
        with open(container_dir / "requirements.txt", 'w') as f:
            f.write(requirements_content)

    def create_lip_sync_container(self):
        """Create lip sync container"""
        container_dir = self.containers_dir / "lip-sync"
        container_dir.mkdir(exist_ok=True)
        
        # Dockerfile for Lip Sync
        dockerfile_content = """
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-dev \\
    ffmpeg \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    cmake \\
    libboost-all-dev \\
    git \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install lip sync specific packages
RUN pip3 install \\
    opencv-python \\
    dlib \\
    mediapipe \\
    face-recognition \\
    insightface \\
    deepface \\
    librosa \\
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8003/health || exit 1

# Start the service
CMD ["python3", "-m", "src.services.lip_sync_service"]
"""
        
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Requirements for lip sync
        requirements_content = """
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0
opencv-python==4.8.1.78
dlib==19.24.2
mediapipe==0.10.7
face-recognition==1.3.0
insightface==0.7.3
deepface==0.0.79
librosa==0.10.1
numpy==1.24.4
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
pydantic==2.5.0
pillow==10.1.0
scipy==1.11.4
"""
        
        with open(container_dir / "requirements.txt", 'w') as f:
            f.write(requirements_content)

    def create_scene_stitcher_container(self):
        """Create scene stitcher container"""
        container_dir = self.containers_dir / "scene-stitcher"
        container_dir.mkdir(exist_ok=True)
        
        # Dockerfile for Scene Stitcher
        dockerfile_content = """
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-dev \\
    ffmpeg \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgl1-mesa-glx \\
    libglib2.0-0 \\
    git \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install video processing packages
RUN pip3 install \\
    opencv-python \\
    moviepy \\
    imageio \\
    imageio-ffmpeg \\
    pillow \\
    numpy \\
    scikit-image \\
    matplotlib

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY templates/ ./templates/

# Expose port
EXPOSE 8004

# Health check
HEALTHCHECK --interval=30s --timeout=15s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8004/health || exit 1

# Start the service
CMD ["python3", "-m", "src.services.scene_stitcher_service"]
"""
        
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Requirements for scene stitcher
        requirements_content = """
opencv-python==4.8.1.78
moviepy==1.0.3
imageio==2.31.5
imageio-ffmpeg==0.4.9
pillow==10.1.0
numpy==1.24.4
scikit-image==0.22.0
matplotlib==3.8.2
fastapi==0.104.1
uvicorn==0.24.0
requests==2.31.0
pydantic==2.5.0
"""
        
        with open(container_dir / "requirements.txt", 'w') as f:
            f.write(requirements_content)

    def create_frontend_ui_container(self):
        """Create frontend UI container"""
        container_dir = self.containers_dir / "frontend-ui"
        container_dir.mkdir(exist_ok=True)
        
        # Dockerfile for Frontend UI
        dockerfile_content = """
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY src/ ./src/
COPY public/ ./public/
COPY build/ ./build/

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start the application
CMD ["npm", "start"]
"""
        
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Package.json for frontend
        package_json = {
            "name": "ai-video-gpu-frontend",
            "version": "1.0.0",
            "description": "AI Video GPU Frontend Interface",
            "main": "src/index.js",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "axios": "^1.6.0",
                "socket.io-client": "^4.7.4",
                "react-router-dom": "^6.18.0",
                "@mui/material": "^5.14.18",
                "@mui/icons-material": "^5.14.18",
                "@emotion/react": "^11.11.1",
                "@emotion/styled": "^11.11.0",
                "react-dropzone": "^14.2.3",
                "react-player": "^2.13.0"
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            }
        }
        
        with open(container_dir / "package.json", 'w') as f:
            import json
            json.dump(package_json, f, indent=2)

    def create_api_server_container(self):
        """Create API server container"""
        container_dir = self.containers_dir / "gpu-api-server"
        container_dir.mkdir(exist_ok=True)
        
        # Dockerfile for API Server
        dockerfile_content = """
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$PATH:$CUDA_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CUDA_HOME/lib64

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    python3-dev \\
    postgresql-client \\
    redis-tools \\
    git \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install API server packages
RUN pip3 install \\
    fastapi \\
    uvicorn \\
    websockets \\
    python-multipart \\
    python-jose \\
    passlib \\
    bcrypt \\
    sqlalchemy \\
    psycopg2-binary \\
    redis \\
    celery \\
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Expose ports
EXPOSE 8000
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start the service
CMD ["python3", "-m", "src.services.api_server"]
"""
        
        with open(container_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Requirements for API server
        requirements_content = """
torch==2.1.0
torchvision==0.16.0
torchaudio==2.1.0
fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
requests==2.31.0
pydantic==2.5.0
numpy==1.24.4
pillow==10.1.0
"""
        
        with open(container_dir / "requirements.txt", 'w') as f:
            f.write(requirements_content)

    def create_service_files(self):
        """Create service files for each microservice"""
        services_dir = self.base_dir / "src" / "services"
        services_dir.mkdir(parents=True, exist_ok=True)
        
        # Video Generator Service
        video_service_content = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import uvicorn
import logging

app = FastAPI(title="Video Generator Service", version="1.0.0")
logger = logging.getLogger(__name__)

class VideoGenerationRequest(BaseModel):
    text: str
    style: str = "photorealistic"
    duration: float = 10.0
    resolution: str = "1920x1080"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video-generator", "gpu_available": torch.cuda.is_available()}

@app.post("/generate")
async def generate_video(request: VideoGenerationRequest):
    try:
        # Video generation logic here
        return {
            "status": "success",
            "video_path": f"output/video_{hash(request.text)}.mp4",
            "duration": request.duration,
            "resolution": request.resolution
        }
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
"""
        
        with open(services_dir / "video_generator_service.py", 'w') as f:
            f.write(video_service_content)
        
        # Voice TTS Service
        voice_service_content = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import uvicorn
import logging

app = FastAPI(title="Voice TTS Service", version="1.0.0")
logger = logging.getLogger(__name__)

class TTSRequest(BaseModel):
    text: str
    voice_sample: str = None
    language: str = "en"
    backend: str = "auto"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voice-tts", "gpu_available": torch.cuda.is_available()}

@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    try:
        # TTS logic here
        return {
            "status": "success",
            "audio_path": f"output/audio_{hash(request.text)}.wav",
            "language": request.language,
            "backend": request.backend
        }
    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
"""
        
        with open(services_dir / "voice_tts_service.py", 'w') as f:
            f.write(voice_service_content)
        
        # Lip Sync Service
        lip_sync_service_content = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import uvicorn
import logging

app = FastAPI(title="Lip Sync Service", version="1.0.0")
logger = logging.getLogger(__name__)

class LipSyncRequest(BaseModel):
    video_path: str
    audio_path: str
    quality: str = "high"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lip-sync", "gpu_available": torch.cuda.is_available()}

@app.post("/sync")
async def sync_lips(request: LipSyncRequest):
    try:
        # Lip sync logic here
        return {
            "status": "success",
            "synced_video_path": f"output/synced_{hash(request.video_path)}.mp4",
            "quality": request.quality
        }
    except Exception as e:
        logger.error(f"Lip sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
"""
        
        with open(services_dir / "lip_sync_service.py", 'w') as f:
            f.write(lip_sync_service_content)
        
        # Scene Stitcher Service
        stitcher_service_content = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging

app = FastAPI(title="Scene Stitcher Service", version="1.0.0")
logger = logging.getLogger(__name__)

class StitchRequest(BaseModel):
    video_paths: list
    audio_path: str = None
    output_format: str = "mp4"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scene-stitcher"}

@app.post("/stitch")
async def stitch_scenes(request: StitchRequest):
    try:
        # Scene stitching logic here
        return {
            "status": "success",
            "final_video_path": f"output/final_{hash(str(request.video_paths))}.{request.output_format}",
            "format": request.output_format
        }
    except Exception as e:
        logger.error(f"Scene stitching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
"""
        
        with open(services_dir / "scene_stitcher_service.py", 'w') as f:
            f.write(stitcher_service_content)
        
        # API Server
        api_server_content = """
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import asyncio

app = FastAPI(title="AI Video GPU API Server", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "gpu-api-server"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

@app.get("/")
async def root():
    return {
        "message": "AI Video GPU API Server",
        "version": "1.0.0",
        "services": {
            "video-generator": "http://video-generator:8001",
            "voice-tts": "http://voice-tts:8002",
            "lip-sync": "http://lip-sync:8003",
            "scene-stitcher": "http://scene-stitcher:8004"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
        
        with open(services_dir / "api_server.py", 'w') as f:
            f.write(api_server_content)

    def create_build_script(self):
        """Create build script for all containers"""
        build_script_content = """#!/bin/bash

# AI Video GPU Microservices Build Script
echo "🏗️  Building AI Video GPU Microservices..."

# Define services
SERVICES=(
    "video-generator"
    "voice-tts"
    "lip-sync"
    "scene-stitcher"
    "frontend-ui"
    "gpu-api-server"
)

# Build each service
for service in "${SERVICES[@]}"; do
    echo "📦 Building $service..."
    
    if [ -d "containers/$service" ]; then
        docker build -t "ai-video-gpu/$service:latest" containers/$service/
        
        if [ $? -eq 0 ]; then
            echo "✅ Successfully built $service"
        else
            echo "❌ Failed to build $service"
            exit 1
        fi
    else
        echo "⚠️  Directory containers/$service not found"
    fi
done

echo "🎉 All microservices built successfully!"
echo ""
echo "🚀 To start the services, run:"
echo "   docker-compose -f docker-compose.microservices.yml up -d"
"""
        
        with open(self.base_dir / "build_containers.sh", 'w') as f:
            f.write(build_script_content)
        
        # Make executable
        os.chmod(self.base_dir / "build_containers.sh", 0o755)

    def create_all_containers(self):
        """Create all container configurations"""
        logger.info("Creating all microservice containers...")
        
        self.create_video_generator_container()
        logger.info("✅ Video Generator container created")
        
        self.create_voice_tts_container()
        logger.info("✅ Voice TTS container created")
        
        self.create_lip_sync_container()
        logger.info("✅ Lip Sync container created")
        
        self.create_scene_stitcher_container()
        logger.info("✅ Scene Stitcher container created")
        
        self.create_frontend_ui_container()
        logger.info("✅ Frontend UI container created")
        
        self.create_api_server_container()
        logger.info("✅ API Server container created")
        
        self.create_service_files()
        logger.info("✅ Service files created")
        
        self.create_build_script()
        logger.info("✅ Build script created")

def main():
    """Main function"""
    print("🐳 AI Video GPU Container Builder")
    print("=" * 40)
    
    builder = ContainerBuilder()
    builder.create_all_containers()
    
    print("\n✅ All containers created successfully!")
    print(f"📁 Containers location: {builder.containers_dir}")
    print("🏗️  Build script: build_containers.sh")
    print("\n🚀 Next steps:")
    print("1. Run: chmod +x build_containers.sh")
    print("2. Run: ./build_containers.sh")
    print("3. Run: docker-compose -f docker-compose.microservices.yml up -d")

if __name__ == "__main__":
    main()
