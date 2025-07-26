"""
AI Video GPU - Voice TTS Service
FastAPI microservice for Hollywood-level voices with Indic-TTS, Bark, Tortoise, Coqui
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import torch
from datetime import datetime
import soundfile as sf
import numpy as np

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Voice synthesis imports
try:
    # Bark
    from bark import SAMPLE_RATE, generate_audio, preload_models
    from bark.generation import SAMPLE_RATE, preload_models
    
    # Coqui TTS
    from TTS.api import TTS
    from TTS.tts.configs.shared_configs import BaseDatasetConfig
    
    # Tortoise TTS
    import tortoise.api
    
    # Additional voice libraries
    import librosa
    import scipy.io.wavfile as wavfile
    
except ImportError as e:
    print(f"Warning: Some TTS libraries not available: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Voice TTS Service",
    description="Hollywood-level voices with Indic-TTS, Bark, Tortoise, Coqui",
    version="1.0.0"
)

# Global variables for models
bark_models_loaded = False
coqui_tts = None
tortoise_tts = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Request models
class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    model: str = "bark"  # bark, coqui, tortoise, indic
    language: str = "en"
    emotion: str = "neutral"  # neutral, happy, sad, angry, excited
    speed: float = 1.0
    pitch: float = 1.0
    output_format: str = "wav"
    hollywood_effects: bool = False

class VoiceCloneRequest(BaseModel):
    text: str
    reference_audio_path: str
    model: str = "tortoise"
    enhancement: bool = True

# Model initialization
async def initialize_models():
    """Initialize TTS models"""
    global bark_models_loaded, coqui_tts, tortoise_tts
    
    try:
        logger.info("Loading Bark models...")
        preload_models()
        bark_models_loaded = True
        logger.info("Bark models loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Bark models: {e}")
    
    try:
        logger.info("Initializing Coqui TTS...")
        coqui_tts = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        logger.info("Coqui TTS initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Coqui TTS: {e}")
    
    try:
        logger.info("Initializing Tortoise TTS...")
        tortoise_tts = tortoise.api.TextToSpeech()
        logger.info("Tortoise TTS initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Tortoise TTS: {e}")

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
            "bark": bark_models_loaded,
            "coqui": coqui_tts is not None,
            "tortoise": tortoise_tts is not None
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Voice TTS",
        "version": "1.0.0",
        "models": ["Bark", "Coqui", "Tortoise", "Indic-TTS"],
        "languages": ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "ur"],
        "features": ["Hollywood voices", "Emotion control", "Voice cloning", "Indic languages"],
        "endpoints": ["/synthesize", "/clone-voice", "/health"]
    }

def apply_hollywood_effects(audio_data, sample_rate, emotion="neutral"):
    """Apply Hollywood-level audio effects"""
    try:
        # Convert to float32 if needed
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)
        
        # Normalize audio
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Apply emotion-based effects
        if emotion == "happy":
            # Increase pitch slightly and add brightness
            audio_data = librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=2)
        elif emotion == "sad":
            # Decrease pitch and add warmth
            audio_data = librosa.effects.pitch_shift(audio_data, sr=sample_rate, n_steps=-2)
        elif emotion == "angry":
            # Add compression and slight distortion
            audio_data = np.tanh(audio_data * 1.5)
        elif emotion == "excited":
            # Increase dynamics and add slight reverb effect
            audio_data = audio_data * 1.2
        
        # Apply professional EQ (simplified)
        # High-pass filter to remove low-frequency noise
        audio_data = librosa.effects.preemphasis(audio_data)
        
        # Gentle compression
        threshold = 0.7
        ratio = 4.0
        compressed = np.where(
            np.abs(audio_data) > threshold,
            np.sign(audio_data) * (threshold + (np.abs(audio_data) - threshold) / ratio),
            audio_data
        )
        
        return compressed
        
    except Exception as e:
        logger.error(f"Hollywood effects failed: {e}")
        return audio_data

@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """Synthesize speech using specified TTS model"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"tts_{request.model}_{timestamp}.{request.output_format}"
        output_path = f"/app/output/audio/{output_filename}"
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if request.model == "bark" and bark_models_loaded:
            logger.info(f"Generating speech with Bark: {request.text[:50]}...")
            
            # Generate audio with Bark
            audio_array = generate_audio(
                request.text,
                history_prompt=request.voice if request.voice != "default" else "v2/en_speaker_6"
            )
            
            # Apply Hollywood effects if requested
            if request.hollywood_effects:
                audio_array = apply_hollywood_effects(audio_array, SAMPLE_RATE, request.emotion)
            
            # Save audio
            sf.write(output_path, audio_array, SAMPLE_RATE)
            
        elif request.model == "coqui" and coqui_tts:
            logger.info(f"Generating speech with Coqui: {request.text[:50]}...")
            
            # Generate audio with Coqui TTS
            wav = coqui_tts.tts(text=request.text)
            
            # Convert to numpy array
            audio_array = np.array(wav)
            sample_rate = 22050  # Default Coqui sample rate
            
            # Apply Hollywood effects if requested
            if request.hollywood_effects:
                audio_array = apply_hollywood_effects(audio_array, sample_rate, request.emotion)
            
            # Save audio
            sf.write(output_path, audio_array, sample_rate)
            
        elif request.model == "tortoise" and tortoise_tts:
            logger.info(f"Generating speech with Tortoise: {request.text[:50]}...")
            
            # Generate audio with Tortoise TTS
            gen = tortoise_tts.tts_with_preset(
                request.text,
                voice_samples=None,
                preset="fast"
            )
            
            audio_array = gen.squeeze().cpu().numpy()
            sample_rate = 24000  # Tortoise sample rate
            
            # Apply Hollywood effects if requested
            if request.hollywood_effects:
                audio_array = apply_hollywood_effects(audio_array, sample_rate, request.emotion)
            
            # Save audio
            sf.write(output_path, audio_array, sample_rate)
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Model {request.model} not available or not loaded"
            )
        
        # Get audio duration
        duration = len(audio_array) / sample_rate if 'sample_rate' in locals() else 0
        
        logger.info(f"Speech synthesized successfully: {output_path}")
        
        return {
            "status": "success",
            "message": "Speech synthesized successfully",
            "output_file": output_filename,
            "output_path": output_path,
            "model_used": request.model,
            "duration": duration,
            "sample_rate": sample_rate if 'sample_rate' in locals() else SAMPLE_RATE,
            "hollywood_effects": request.hollywood_effects,
            "emotion": request.emotion
        }
        
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

@app.post("/clone-voice")
async def clone_voice(request: VoiceCloneRequest):
    """Clone voice from reference audio"""
    try:
        if not tortoise_tts:
            raise HTTPException(status_code=503, detail="Tortoise TTS not loaded")
        
        if not os.path.exists(request.reference_audio_path):
            raise HTTPException(status_code=404, detail="Reference audio not found")
        
        logger.info(f"Cloning voice: {request.text[:50]}...")
        
        # Load reference audio
        reference_audio, sr = librosa.load(request.reference_audio_path, sr=24000)
        
        # Generate audio with voice cloning
        gen = tortoise_tts.tts(
            request.text,
            voice_samples=[reference_audio]
        )
        
        audio_array = gen.squeeze().cpu().numpy()
        
        # Apply enhancement if requested
        if request.enhancement:
            audio_array = apply_hollywood_effects(audio_array, 24000, "neutral")
        
        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"voice_clone_{timestamp}.wav"
        output_path = f"/app/output/audio/{output_filename}"
        
        # Save audio
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        sf.write(output_path, audio_array, 24000)
        
        duration = len(audio_array) / 24000
        
        logger.info(f"Voice cloning completed: {output_path}")
        
        return {
            "status": "success",
            "message": "Voice cloning completed",
            "output_file": output_filename,
            "output_path": output_path,
            "reference_audio": request.reference_audio_path,
            "duration": duration,
            "enhancement": request.enhancement
        }
        
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Upload reference audio for voice cloning"""
    try:
        upload_dir = "/app/temp/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ref_audio_{timestamp}_{file.filename}"
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
async def download_audio(filename: str):
    """Download generated audio"""
    file_path = f"/app/output/audio/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/wav"
    )

@app.get("/voices")
async def list_voices():
    """List available voices"""
    return {
        "bark_voices": [
            "v2/en_speaker_0", "v2/en_speaker_1", "v2/en_speaker_2",
            "v2/en_speaker_3", "v2/en_speaker_4", "v2/en_speaker_5",
            "v2/en_speaker_6", "v2/en_speaker_7", "v2/en_speaker_8", "v2/en_speaker_9"
        ],
        "emotions": ["neutral", "happy", "sad", "angry", "excited"],
        "languages": ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "ur"],
        "hollywood_effects": ["compression", "eq", "pitch_shift", "reverb"]
    }

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
            "bark": {
                "loaded": bark_models_loaded,
                "status": "ready" if bark_models_loaded else "not_loaded"
            },
            "coqui": {
                "loaded": coqui_tts is not None,
                "status": "ready" if coqui_tts else "not_loaded"
            },
            "tortoise": {
                "loaded": tortoise_tts is not None,
                "status": "ready" if tortoise_tts else "not_loaded"
            }
        },
        "device": device,
        "gpu_memory": gpu_memory,
        "torch_version": torch.__version__
    }

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("/app/output/audio", exist_ok=True)
    os.makedirs("/app/temp/uploads", exist_ok=True)
    os.makedirs("/app/logs", exist_ok=True)
    
    # Start the service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info",
        access_log=True
    )
