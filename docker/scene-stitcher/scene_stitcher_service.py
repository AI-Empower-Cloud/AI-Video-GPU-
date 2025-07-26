#!/usr/bin/env python3
"""
Scene Stitcher Microservice
GPU-accelerated video composition and scene stitching
"""

import os
import sys
import asyncio
import logging
import traceback
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile
import json
import uuid
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis
import moviepy.editor as mp
import cv2
import numpy as np
from rich.console import Console
from rich.logging import RichHandler

# Initialize console and logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console)]
)
logger = logging.getLogger("scene-stitcher")

app = FastAPI(
    title="AI Video GPU - Scene Stitcher",
    description="GPU-accelerated video composition and scene stitching microservice",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for job queue
try:
    redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Connected to Redis")
except:
    logger.warning("⚠️ Redis not available, using in-memory queue")
    redis_client = None

# Job storage
active_jobs = {}

class SceneStitchRequest(BaseModel):
    """Scene stitching request model"""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenes: List[str] = Field(..., description="List of scene file paths or URLs")
    transitions: List[str] = Field(default=["fade"], description="Transition types between scenes")
    durations: List[float] = Field(default=[], description="Duration for each scene (optional)")
    output_format: str = Field(default="mp4", description="Output video format")
    resolution: str = Field(default="1920x1080", description="Output resolution")
    fps: int = Field(default=30, description="Output frame rate")
    audio_fade: bool = Field(default=True, description="Enable audio fade transitions")
    background_music: Optional[str] = Field(default=None, description="Background music file")
    subtitle_file: Optional[str] = Field(default=None, description="SRT subtitle file")
    effects: List[str] = Field(default=[], description="Video effects to apply")

class JobStatus(BaseModel):
    """Job status model"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float = 0.0
    message: str = ""
    result_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class SceneStitcher:
    """GPU-accelerated scene stitching engine"""
    
    def __init__(self):
        self.temp_dir = Path("/app/temp")
        self.output_dir = Path("/app/outputs")
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize GPU acceleration if available
        self.gpu_available = self._check_gpu()
        logger.info(f"🎬 Scene Stitcher initialized (GPU: {self.gpu_available})")
    
    def _check_gpu(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            import cupy as cp
            cp.cuda.runtime.getDeviceCount()
            return True
        except:
            return False
    
    def _apply_transition(self, clip1: mp.VideoFileClip, clip2: mp.VideoFileClip, 
                         transition_type: str, duration: float = 1.0) -> mp.VideoFileClip:
        """Apply transition between two clips"""
        try:
            if transition_type == "fade":
                # Fade out first clip and fade in second clip
                clip1_fade = clip1.fadeout(duration)
                clip2_fade = clip2.fadein(duration)
                return mp.concatenate_videoclips([clip1_fade, clip2_fade])
            
            elif transition_type == "crossfade":
                # Crossfade transition
                clip1_end = clip1.subclip(-duration)
                clip2_start = clip2.subclip(0, duration)
                
                crossfade = mp.CompositeVideoClip([
                    clip1_end.fadeout(duration),
                    clip2_start.fadein(duration).set_start(0)
                ])
                
                return mp.concatenate_videoclips([
                    clip1.subclip(0, -duration),
                    crossfade,
                    clip2.subclip(duration)
                ])
            
            elif transition_type == "slide":
                # Slide transition
                w, h = clip1.size
                clip1_slide = clip1.fx(mp.vfx.slide_out, duration, "left")
                clip2_slide = clip2.fx(mp.vfx.slide_in, duration, "right")
                return mp.concatenate_videoclips([clip1_slide, clip2_slide])
            
            else:
                # Direct cut (no transition)
                return mp.concatenate_videoclips([clip1, clip2])
                
        except Exception as e:
            logger.warning(f"Transition failed: {e}, using direct cut")
            return mp.concatenate_videoclips([clip1, clip2])
    
    def _apply_effects(self, clip: mp.VideoFileClip, effects: List[str]) -> mp.VideoFileClip:
        """Apply video effects to clip"""
        try:
            for effect in effects:
                if effect == "stabilize":
                    # Video stabilization
                    clip = clip.fx(mp.vfx.stabilize)
                elif effect == "speed_2x":
                    # 2x speed
                    clip = clip.fx(mp.vfx.speedx, 2.0)
                elif effect == "slow_motion":
                    # Slow motion (0.5x speed)
                    clip = clip.fx(mp.vfx.speedx, 0.5)
                elif effect == "black_white":
                    # Black and white
                    clip = clip.fx(mp.vfx.blackwhite)
                elif effect == "mirror_x":
                    # Mirror horizontally
                    clip = clip.fx(mp.vfx.mirror_x)
                elif effect == "mirror_y":
                    # Mirror vertically
                    clip = clip.fx(mp.vfx.mirror_y)
                elif effect == "rotate_90":
                    # Rotate 90 degrees
                    clip = clip.fx(mp.vfx.rotate, 90)
            
            return clip
        except Exception as e:
            logger.warning(f"Effects failed: {e}, using original clip")
            return clip
    
    async def stitch_scenes(self, request: SceneStitchRequest, 
                           progress_callback=None) -> str:
        """Stitch multiple scenes into a single video"""
        job_id = request.job_id
        
        try:
            logger.info(f"🎬 Starting scene stitching job: {job_id}")
            
            # Update progress
            if progress_callback:
                await progress_callback(10, "Loading scenes...")
            
            # Load all scene clips
            clips = []
            for i, scene_path in enumerate(request.scenes):
                try:
                    if scene_path.startswith(('http://', 'https://')):
                        # Download remote file
                        import httpx
                        async with httpx.AsyncClient() as client:
                            response = await client.get(scene_path)
                            temp_file = self.temp_dir / f"scene_{i}_{job_id}.mp4"
                            with open(temp_file, 'wb') as f:
                                f.write(response.content)
                            scene_path = str(temp_file)
                    
                    clip = mp.VideoFileClip(scene_path)
                    
                    # Apply custom duration if specified
                    if i < len(request.durations) and request.durations[i] > 0:
                        clip = clip.subclip(0, request.durations[i])
                    
                    # Apply effects
                    if request.effects:
                        clip = self._apply_effects(clip, request.effects)
                    
                    clips.append(clip)
                    logger.info(f"✅ Loaded scene {i+1}/{len(request.scenes)}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to load scene {scene_path}: {e}")
                    continue
            
            if not clips:
                raise ValueError("No valid scenes to stitch")
            
            # Update progress
            if progress_callback:
                await progress_callback(30, "Applying transitions...")
            
            # Apply transitions between clips
            final_clips = []
            for i in range(len(clips)):
                final_clips.append(clips[i])
                
                # Add transition if not the last clip
                if i < len(clips) - 1:
                    transition_type = (request.transitions[i] 
                                     if i < len(request.transitions) 
                                     else "fade")
                    
                    # Create transition
                    if transition_type != "cut":
                        transition_clip = self._apply_transition(
                            clips[i], clips[i+1], transition_type
                        )
                        final_clips[-1] = transition_clip
                        final_clips.append(clips[i+1])
            
            # Update progress
            if progress_callback:
                await progress_callback(60, "Compositing final video...")
            
            # Concatenate all clips
            if len(final_clips) == 1:
                final_video = final_clips[0]
            else:
                final_video = mp.concatenate_videoclips(final_clips, method="compose")
            
            # Resize to target resolution
            width, height = map(int, request.resolution.split('x'))
            final_video = final_video.resize((width, height))
            
            # Add background music if specified
            if request.background_music:
                try:
                    bg_music = mp.AudioFileClip(request.background_music)
                    bg_music = bg_music.loop(duration=final_video.duration)
                    
                    if final_video.audio:
                        # Mix with existing audio
                        mixed_audio = mp.CompositeAudioClip([
                            final_video.audio,
                            bg_music.volumex(0.3)  # Lower background music volume
                        ])
                    else:
                        mixed_audio = bg_music
                    
                    final_video = final_video.set_audio(mixed_audio)
                    
                except Exception as e:
                    logger.warning(f"Background music failed: {e}")
            
            # Add subtitles if specified
            if request.subtitle_file:
                try:
                    # Parse SRT file and add subtitles
                    # This would require additional subtitle parsing logic
                    logger.info("Subtitle support: TODO - implement SRT parsing")
                except Exception as e:
                    logger.warning(f"Subtitle processing failed: {e}")
            
            # Update progress
            if progress_callback:
                await progress_callback(80, "Rendering final video...")
            
            # Generate output filename
            output_file = self.output_dir / f"stitched_{job_id}.{request.output_format}"
            
            # Render final video with GPU acceleration if available
            codec = "libx264"
            if self.gpu_available and request.output_format == "mp4":
                codec = "h264_nvenc"  # NVIDIA GPU encoding
            
            final_video.write_videofile(
                str(output_file),
                fps=request.fps,
                codec=codec,
                audio_codec="aac",
                temp_audiofile=str(self.temp_dir / f"temp_audio_{job_id}.m4a"),
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up clips
            for clip in clips:
                clip.close()
            final_video.close()
            
            # Update progress
            if progress_callback:
                await progress_callback(100, "Scene stitching completed!")
            
            logger.info(f"✅ Scene stitching completed: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"❌ Scene stitching failed: {e}")
            logger.error(traceback.format_exc())
            raise

# Initialize stitcher
stitcher = SceneStitcher()

async def update_job_status(job_id: str, status: str, progress: float = 0.0, 
                           message: str = "", result_url: str = None):
    """Update job status"""
    job_status = JobStatus(
        job_id=job_id,
        status=status,
        progress=progress,
        message=message,
        result_url=result_url,
        created_at=active_jobs.get(job_id, {}).get('created_at', datetime.now()),
        updated_at=datetime.now()
    )
    
    active_jobs[job_id] = job_status.dict()
    
    if redis_client:
        try:
            await redis_client.set(f"job:{job_id}", json.dumps(job_status.dict()))
        except:
            pass

async def process_stitching_job(request: SceneStitchRequest):
    """Background task to process stitching job"""
    job_id = request.job_id
    
    try:
        await update_job_status(job_id, "processing", message="Starting scene stitching...")
        
        async def progress_callback(progress: float, message: str):
            await update_job_status(job_id, "processing", progress, message)
        
        # Process the stitching
        result_path = await stitcher.stitch_scenes(request, progress_callback)
        result_url = f"/download/{job_id}"
        
        await update_job_status(job_id, "completed", 100.0, 
                               "Scene stitching completed successfully!", result_url)
        
    except Exception as e:
        logger.error(f"❌ Job {job_id} failed: {e}")
        await update_job_status(job_id, "failed", message=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Video GPU - Scene Stitcher",
        "version": "1.0.0",
        "status": "running",
        "gpu_available": stitcher.gpu_available
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "gpu": stitcher.gpu_available}

@app.post("/stitch", response_model=Dict[str, str])
async def stitch_scenes(request: SceneStitchRequest, background_tasks: BackgroundTasks):
    """Stitch scenes into a single video"""
    try:
        job_id = request.job_id
        
        # Initialize job status
        await update_job_status(job_id, "pending", message="Job queued for processing")
        
        # Add to background tasks
        background_tasks.add_task(process_stitching_job, request)
        
        return {
            "job_id": job_id,
            "status": "accepted",
            "message": "Scene stitching job started"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start stitching job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id in active_jobs:
        return active_jobs[job_id]
    
    if redis_client:
        try:
            job_data = await redis_client.get(f"job:{job_id}")
            if job_data:
                return json.loads(job_data)
        except:
            pass
    
    raise HTTPException(status_code=404, detail="Job not found")

@app.get("/download/{job_id}")
async def download_result(job_id: str):
    """Download stitched video result"""
    output_file = stitcher.output_dir / f"stitched_{job_id}.mp4"
    
    if not output_file.exists():
        # Try other formats
        for ext in ['avi', 'mov', 'mkv']:
            alt_file = stitcher.output_dir / f"stitched_{job_id}.{ext}"
            if alt_file.exists():
                output_file = alt_file
                break
        else:
            raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        str(output_file),
        media_type="video/mp4",
        filename=f"stitched_scenes_{job_id}.mp4"
    )

@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    return {"jobs": list(active_jobs.keys())}

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete job and cleanup files"""
    try:
        # Remove from active jobs
        if job_id in active_jobs:
            del active_jobs[job_id]
        
        # Remove from Redis
        if redis_client:
            try:
                await redis_client.delete(f"job:{job_id}")
            except:
                pass
        
        # Cleanup files
        output_file = stitcher.output_dir / f"stitched_{job_id}.mp4"
        if output_file.exists():
            output_file.unlink()
        
        # Cleanup temp files
        for temp_file in stitcher.temp_dir.glob(f"*_{job_id}.*"):
            temp_file.unlink()
        
        return {"message": "Job deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🎬 Starting Scene Stitcher microservice...")
    uvicorn.run(
        "scene_stitcher_service:app",
        host="0.0.0.0",
        port=8004,
        reload=False,
        workers=1
    )
