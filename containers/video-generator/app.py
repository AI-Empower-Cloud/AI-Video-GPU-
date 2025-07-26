"""
AI Video GPU - Video Generator Service
FastAPI microservice for AnimateDiff, SVD, Gen-2 clones and Hollywood/Bollywood VFX
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import torch
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uvicorn

# Video generation imports
try:
    from diffusers import StableVideoDiffusionPipeline, AnimateDiffPipeline
    from diffusers.utils import export_to_video
    import cv2
    import numpy as np
    from PIL import Image
    import imageio
except ImportError as e:
    print(f"Warning: Some video generation libraries not available: {e}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Video Generator Service",
    description="GenAI Video Generation - AnimateDiff, SVD, Gen-2 clones",
    version="1.0.0"
)

# Global variables for models
svd_pipeline = None
animate_pipeline = None
device = "cuda" if torch.cuda.is_available() else "cpu"

# Request models
class VideoGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = ""
    width: int = 1024
    height: int = 576
    num_frames: int = 25
    num_inference_steps: int = 25
    guidance_scale: float = 7.5
    fps: int = 8
    motion_bucket_id: int = 127
    noise_aug_strength: float = 0.02
    seed: Optional[int] = None
    model_type: str = "svd"  # svd, animatediff, gen2

class ImageToVideoRequest(BaseModel):
    image_path: str
    prompt: Optional[str] = ""
    num_frames: int = 25
    fps: int = 8
    motion_bucket_id: int = 127
    noise_aug_strength: float = 0.02
    seed: Optional[int] = None

# Model initialization
async def initialize_models():
    """Initialize video generation models"""
    global svd_pipeline, animate_pipeline
    
    try:
        logger.info("Initializing Stable Video Diffusion model...")
        svd_pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid-xt",
            torch_dtype=torch.float16,
            variant="fp16",
            cache_dir="/app/models/svd"
        )
        svd_pipeline = svd_pipeline.to(device)
        svd_pipeline.enable_model_cpu_offload()
        logger.info("SVD model initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize SVD model: {e}")
    
    try:
        logger.info("Initializing AnimateDiff model...")
        animate_pipeline = AnimateDiffPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            cache_dir="/app/models/animatediff"
        )
        animate_pipeline = animate_pipeline.to(device)
        animate_pipeline.enable_model_cpu_offload()
        logger.info("AnimateDiff model initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AnimateDiff model: {e}")

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
            "svd": svd_pipeline is not None,
            "animatediff": animate_pipeline is not None
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Video Generator",
        "version": "1.0.0",
        "models": ["SVD", "AnimateDiff", "Gen-2 Clone"],
        "endpoints": ["/generate", "/image-to-video", "/health"]
    }

@app.post("/generate")
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Generate video from text prompt"""
    try:
        # Create unique output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"generated_video_{timestamp}.mp4"
        output_path = f"/app/output/video/{output_filename}"
        
        # Set seed for reproducibility
        if request.seed:
            torch.manual_seed(request.seed)
            np.random.seed(request.seed)
        
        if request.model_type == "svd" and svd_pipeline:
            # Generate initial image from prompt
            logger.info(f"Generating video with SVD: {request.prompt}")
            
            # For SVD, we need an initial image
            # This is a simplified approach - in production, you'd generate the image first
            initial_image = Image.new('RGB', (request.width, request.height), color='black')
            
            # Generate video frames
            video_frames = svd_pipeline(
                initial_image,
                height=request.height,
                width=request.width,
                num_frames=request.num_frames,
                num_inference_steps=request.num_inference_steps,
                motion_bucket_id=request.motion_bucket_id,
                noise_aug_strength=request.noise_aug_strength,
                fps=request.fps
            ).frames[0]
            
        elif request.model_type == "animatediff" and animate_pipeline:
            logger.info(f"Generating video with AnimateDiff: {request.prompt}")
            
            # Generate video with AnimateDiff
            video_frames = animate_pipeline(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt,
                height=request.height,
                width=request.width,
                num_frames=request.num_frames,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale
            ).frames[0]
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Model {request.model_type} not available or not loaded"
            )
        
        # Export video
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        export_to_video(video_frames, output_path, fps=request.fps)
        
        logger.info(f"Video generated successfully: {output_path}")
        
        return {
            "status": "success",
            "message": "Video generated successfully",
            "output_file": output_filename,
            "output_path": output_path,
            "model_used": request.model_type,
            "frames": len(video_frames),
            "fps": request.fps,
            "duration": len(video_frames) / request.fps
        }
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.post("/image-to-video")
async def image_to_video(request: ImageToVideoRequest):
    """Convert image to video using SVD"""
    try:
        if not svd_pipeline:
            raise HTTPException(status_code=503, detail="SVD model not loaded")
        
        # Load input image
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail="Input image not found")
        
        input_image = Image.open(request.image_path)
        
        # Set seed for reproducibility
        if request.seed:
            torch.manual_seed(request.seed)
            np.random.seed(request.seed)
        
        # Generate video from image
        logger.info(f"Converting image to video: {request.image_path}")
        
        video_frames = svd_pipeline(
            input_image,
            num_frames=request.num_frames,
            motion_bucket_id=request.motion_bucket_id,
            noise_aug_strength=request.noise_aug_strength,
            fps=request.fps
        ).frames[0]
        
        # Create output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"img2vid_{timestamp}.mp4"
        output_path = f"/app/output/video/{output_filename}"
        
        # Export video
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        export_to_video(video_frames, output_path, fps=request.fps)
        
        logger.info(f"Image-to-video conversion completed: {output_path}")
        
        return {
            "status": "success",
            "message": "Image to video conversion completed",
            "input_image": request.image_path,
            "output_file": output_filename,
            "output_path": output_path,
            "frames": len(video_frames),
            "fps": request.fps,
            "duration": len(video_frames) / request.fps
        }
        
    except Exception as e:
        logger.error(f"Image-to-video conversion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image for processing"""
    try:
        # Create uploads directory
        upload_dir = "/app/temp/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "status": "success",
            "message": "Image uploaded successfully",
            "filename": filename,
            "file_path": file_path,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Image upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/download/{filename}")
async def download_video(filename: str):
    """Download generated video"""
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
                "allocated": torch.cuda.memory_allocated(i) / 1024**3,  # GB
                "reserved": torch.cuda.memory_reserved(i) / 1024**3,    # GB
                "name": torch.cuda.get_device_name(i)
            }
    
    return {
        "models": {
            "svd": {
                "loaded": svd_pipeline is not None,
                "model_id": "stabilityai/stable-video-diffusion-img2vid-xt",
                "status": "ready" if svd_pipeline else "not_loaded"
            },
            "animatediff": {
                "loaded": animate_pipeline is not None,
                "model_id": "runwayml/stable-diffusion-v1-5",
                "status": "ready" if animate_pipeline else "not_loaded"
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
        port=8001,
        log_level="info",
        access_log=True
    )
