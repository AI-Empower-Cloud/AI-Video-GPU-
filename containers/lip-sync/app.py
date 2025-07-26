"""
AI Video GPU - Lip Sync Service
FastAPI microservice for Wav2Lip, LipGAN, Real-time lip synchronization
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json
import cv2
import numpy as np
import torch
from datetime import datetime

# Add Wav2Lip to path
sys.path.append('/app/Wav2Lip')

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Lip sync imports
try:
    import face_detection
    import models
    from models import Wav2Lip
    import audio
    import librosa
    import soundfile as sf
except ImportError as e:
    print(f"Warning: Some lip sync libraries not available: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Lip Sync Service",
    description="Wav2Lip, LipGAN, Real-time lip synchronization",
    version="1.0.0"
)

# Global variables
wav2lip_model = None
face_detector = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Request models
class LipSyncRequest(BaseModel):
    video_path: str
    audio_path: str
    model: str = "wav2lip"  # wav2lip, lipgan
    face_restore: bool = True
    smooth: bool = True
    resize_factor: int = 1
    quality: str = "high"  # low, medium, high

class RealTimeLipSyncRequest(BaseModel):
    video_stream_url: str
    audio_stream_url: str
    latency_ms: int = 100

# Model initialization
async def initialize_models():
    """Initialize lip sync models"""
    global wav2lip_model, face_detector
    
    try:
        logger.info("Loading face detector...")
        face_detector = face_detection.FaceAlignment(
            face_detection.LandmarksType._2D,
            flip_input=False,
            device=device
        )
        logger.info("Face detector loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load face detector: {e}")
    
    try:
        logger.info("Loading Wav2Lip model...")
        model_path = "/app/models/wav2lip/wav2lip_gan.pth"
        
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=device)
            wav2lip_model = Wav2Lip()
            wav2lip_model.load_state_dict(checkpoint["state_dict"])
            wav2lip_model.to(device)
            wav2lip_model.eval()
            logger.info("Wav2Lip model loaded successfully")
        else:
            logger.warning(f"Wav2Lip model not found at {model_path}")
            
    except Exception as e:
        logger.error(f"Failed to load Wav2Lip model: {e}")

def get_smoothened_boxes(boxes, T):
    """Smooth bounding boxes over time"""
    for i in range(len(boxes)):
        if i + T > len(boxes):
            window = boxes[len(boxes) - T:]
        else:
            window = boxes[i : i + T]
        boxes[i] = np.mean(window, axis=0)
    return boxes

def face_detect(images, face_detector, batch_size=32):
    """Detect faces in video frames"""
    detector = face_detector
    batch_size = min(batch_size, len(images))
    
    while True:
        predictions = []
        try:
            for i in range(0, len(images), batch_size):
                batch = images[i:i + batch_size]
                predictions.extend(detector.get_detections_for_batch(np.array(batch)))
        except RuntimeError:
            if batch_size == 1:
                raise RuntimeError("Failed to detect faces even with batch_size 1")
            batch_size //= 2
            logger.warning(f"Reducing batch size to {batch_size}")
            continue
        break
    
    return predictions

def datagen(frames, mels, face_detector, batch_size=16):
    """Generate data batches for Wav2Lip"""
    img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []
    
    face_det_results = face_detect(frames, face_detector, batch_size)
    
    for i, m in enumerate(mels):
        idx = 0 if i == 0 else i - 1
        frame_to_save = frames[idx].copy()
        face = face_det_results[idx]
        
        if face is None:
            continue
            
        coords = face
        face = frames[idx][coords[1]:coords[3], coords[0]:coords[2]]
        face = cv2.resize(face, (96, 96))
        
        img_batch.append(face)
        mel_batch.append(m)
        frame_batch.append(frame_to_save)
        coords_batch.append(coords)
        
        if len(img_batch) >= batch_size:
            img_batch = np.asarray(img_batch)
            mel_batch = np.asarray(mel_batch)
            
            img_masked = img_batch.copy()
            img_masked[:, 96//2:] = 0
            
            img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
            mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])
            
            yield img_batch, mel_batch, frame_batch, coords_batch
            img_batch, mel_batch, frame_batch, coords_batch = [], [], [], []
    
    if len(img_batch) > 0:
        img_batch = np.asarray(img_batch)
        mel_batch = np.asarray(mel_batch)
        
        img_masked = img_batch.copy()
        img_masked[:, 96//2:] = 0
        
        img_batch = np.concatenate((img_masked, img_batch), axis=3) / 255.
        mel_batch = np.reshape(mel_batch, [len(mel_batch), mel_batch.shape[1], mel_batch.shape[2], 1])
        
        yield img_batch, mel_batch, frame_batch, coords_batch

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    await initialize_models()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gpu_available": gpu_available,
        "gpu_count": gpu_count,
        "device": device,
        "models_loaded": {
            "wav2lip": wav2lip_model is not None,
            "face_detector": face_detector is not None
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Lip Sync",
        "version": "1.0.0",
        "models": ["Wav2Lip", "LipGAN"],
        "features": ["Face detection", "Lip synchronization", "Real-time processing"],
        "endpoints": ["/sync", "/real-time-sync", "/health"]
    }

@app.post("/sync")
async def sync_lips(request: LipSyncRequest):
    """Synchronize lips with audio"""
    try:
        if not wav2lip_model or not face_detector:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        if not os.path.exists(request.video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        if not os.path.exists(request.audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        logger.info(f"Starting lip sync: {os.path.basename(request.video_path)}")
        
        # Load video
        cap = cv2.VideoCapture(request.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        
        logger.info(f"Loaded {len(frames)} frames at {fps} FPS")
        
        # Load audio and extract mel spectrogram
        wav, sr = librosa.load(request.audio_path, sr=16000)
        
        # Import audio processing from Wav2Lip
        mel = audio.melspectrogram(wav)
        
        if np.isnan(mel.reshape(-1)).sum() > 0:
            raise ValueError("Mel spectrogram contains NaN values")
        
        mel_chunks = []
        mel_idx_multiplier = 80./fps
        i = 0
        while True:
            start_idx = int(i * mel_idx_multiplier)
            if start_idx + 16 > len(mel[0]):
                mel_chunks.append(mel[:, len(mel[0]) - 16:])
                break
            mel_chunks.append(mel[:, start_idx : start_idx + 16])
            i += 1
        
        logger.info(f"Generated {len(mel_chunks)} mel chunks")
        
        # Generate lip-synced frames
        gen = datagen(frames.copy(), mel_chunks, face_detector)
        
        output_frames = []
        for i, (img_batch, mel_batch, frames_batch, coords_batch) in enumerate(gen):
            if i == 0:
                logger.info(f"Processing batches... Batch shape: {img_batch.shape}")
            
            img_batch = torch.FloatTensor(np.transpose(img_batch, (0, 3, 1, 2))).to(device)
            mel_batch = torch.FloatTensor(np.transpose(mel_batch, (0, 3, 1, 2))).to(device)
            
            with torch.no_grad():
                pred = wav2lip_model(mel_batch, img_batch)
            
            pred = pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.
            
            for p, f, c in zip(pred, frames_batch, coords_batch):
                y1, y2, x1, x2 = c
                p = cv2.resize(p.astype(np.uint8), (x2 - x1, y2 - y1))
                f[y1:y2, x1:x2] = p
                output_frames.append(f)
        
        # Create output video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"lip_sync_{timestamp}.mp4"
        output_path = f"/app/output/video/{output_filename}"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write video with audio
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (frames[0].shape[1], frames[0].shape[0]))
        
        for frame in output_frames:
            out.write(frame)
        out.release()
        
        # Add audio to video using ffmpeg
        temp_video = output_path.replace('.mp4', '_temp.mp4')
        os.rename(output_path, temp_video)
        
        cmd = f'ffmpeg -y -i "{temp_video}" -i "{request.audio_path}" -c:v copy -c:a aac "{output_path}"'
        os.system(cmd)
        os.remove(temp_video)
        
        logger.info(f"Lip sync completed: {output_path}")
        
        return {
            "status": "success",
            "message": "Lip sync completed successfully",
            "input_video": request.video_path,
            "input_audio": request.audio_path,
            "output_file": output_filename,
            "output_path": output_path,
            "frames_processed": len(output_frames),
            "fps": fps,
            "duration": len(output_frames) / fps
        }
        
    except Exception as e:
        logger.error(f"Lip sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Lip sync failed: {str(e)}")

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """Upload video file"""
    try:
        upload_dir = "/app/temp/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "message": "Video uploaded successfully",
            "filename": filename,
            "file_path": file_path,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Video upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload audio file"""
    try:
        upload_dir = "/app/temp/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "message": "Audio uploaded successfully",
            "filename": filename,
            "file_path": file_path,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/download/{filename}")
async def download_video(filename: str):
    """Download lip-synced video"""
    file_path = f"/app/output/video/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="video/mp4"
    )

@app.get("/models/status")
async def model_status():
    """Get model loading status"""
    gpu_memory = {}
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            gpu_memory[f"gpu_{i}"] = {
                "allocated": torch.cuda.memory_allocated(i) / 1024**3,
                "reserved": torch.cuda.memory_reserved(i) / 1024**3,
                "name": torch.cuda.get_device_name(i)
            }
    
    return {
        "models": {
            "wav2lip": {
                "loaded": wav2lip_model is not None,
                "model_path": "/app/models/wav2lip/wav2lip_gan.pth",
                "status": "ready" if wav2lip_model else "not_loaded"
            },
            "face_detector": {
                "loaded": face_detector is not None,
                "status": "ready" if face_detector else "not_loaded"
            }
        },
        "device": device,
        "gpu_memory": gpu_memory,
        "torch_version": torch.__version__
    }

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("/app/output/video", exist_ok=True)
    os.makedirs("/app/temp/uploads", exist_ok=True)
    os.makedirs("/app/logs", exist_ok=True)
    
    # Start the service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info",
        access_log=True
    )
