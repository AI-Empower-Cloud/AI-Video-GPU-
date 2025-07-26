#!/usr/bin/env python3
"""
AI Video GPU - API Backend Microservice
FastAPI backend with orchestration and coordination
"""

import os
import sys
import asyncio
import logging
import traceback
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import tempfile
import json
import uuid
from datetime import datetime, timedelta
import mimetypes
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import redis.asyncio as redis
import httpx
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
logger = logging.getLogger("api-backend")

# Service endpoints
SERVICES = {
    "video_generator": "http://video-generator:8001",
    "voice_tts": "http://voice-tts:8002",
    "lip_sync": "http://lip-sync:8003",
    "scene_stitcher": "http://scene-stitcher:8004"
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting AI Video GPU API Backend...")
    
    # Initialize Redis connection
    try:
        app.state.redis = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
        await app.state.redis.ping()
        logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        app.state.redis = None
    
    # Test service connections
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name} is healthy")
                else:
                    logger.warning(f"⚠️ {service_name} returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ {service_name} is not responding: {e}")
    
    yield
    
    # Cleanup
    if app.state.redis:
        await app.state.redis.close()
    logger.info("🛑 API Backend shutdown complete")

app = FastAPI(
    title="AI Video GPU - API Backend",
    description="Orchestration and coordination API for AI Video GPU Studio",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Models
class VideoCreationRequest(BaseModel):
    """Complete video creation request"""
    project_name: str = Field(..., description="Project name")
    script: str = Field(..., description="Video script or text")
    voice_model: str = Field(default="bark", description="TTS model to use")
    voice_settings: Dict[str, Any] = Field(default_factory=dict, description="Voice generation settings")
    video_style: str = Field(default="cinematic", description="Video generation style")
    video_settings: Dict[str, Any] = Field(default_factory=dict, description="Video generation settings")
    lip_sync_enabled: bool = Field(default=True, description="Enable lip synchronization")
    background_music: Optional[str] = Field(default=None, description="Background music file")
    transitions: List[str] = Field(default=["fade"], description="Scene transitions")
    output_format: str = Field(default="mp4", description="Output video format")
    resolution: str = Field(default="1920x1080", description="Output resolution")

class PipelineStatus(BaseModel):
    """Pipeline execution status"""
    pipeline_id: str
    status: str  # pending, processing, completed, failed
    current_stage: str
    progress: float = 0.0
    stages: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class ServiceHealthResponse(BaseModel):
    """Service health check response"""
    service: str
    status: str
    gpu_available: bool = False
    version: str = "1.0.0"

# Storage
active_pipelines = {}

async def get_redis() -> Optional[redis.Redis]:
    """Get Redis connection"""
    return getattr(app.state, 'redis', None)

async def update_pipeline_status(pipeline_id: str, status: str, current_stage: str = "", 
                               progress: float = 0.0, stage_data: Dict = None, 
                               result_url: str = None, error_message: str = None):
    """Update pipeline status"""
    pipeline_status = PipelineStatus(
        pipeline_id=pipeline_id,
        status=status,
        current_stage=current_stage,
        progress=progress,
        stages=active_pipelines.get(pipeline_id, {}).get('stages', {}),
        result_url=result_url,
        error_message=error_message,
        created_at=active_pipelines.get(pipeline_id, {}).get('created_at', datetime.now()),
        updated_at=datetime.now()
    )
    
    if stage_data:
        pipeline_status.stages[current_stage] = stage_data
    
    active_pipelines[pipeline_id] = pipeline_status.dict()
    
    # Store in Redis
    redis_client = await get_redis()
    if redis_client:
        try:
            await redis_client.set(f"pipeline:{pipeline_id}", json.dumps(pipeline_status.dict(), default=str))
        except:
            pass
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "pipeline_update",
        "pipeline_id": pipeline_id,
        "status": status,
        "current_stage": current_stage,
        "progress": progress,
        "message": stage_data.get('message', '') if stage_data else ''
    })

async def call_service(service_name: str, endpoint: str, method: str = "GET", 
                      data: Dict = None, files: Dict = None, timeout: int = 300) -> Dict:
    """Call a microservice"""
    service_url = SERVICES.get(service_name)
    if not service_url:
        raise ValueError(f"Unknown service: {service_name}")
    
    url = f"{service_url}{endpoint}"
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            if files:
                response = await client.post(url, data=data, files=files)
            else:
                response = await client.post(url, json=data)
        elif method == "PUT":
            response = await client.put(url, json=data)
        elif method == "DELETE":
            response = await client.delete(url)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()

async def execute_video_pipeline(request: VideoCreationRequest) -> str:
    """Execute complete video creation pipeline"""
    pipeline_id = str(uuid.uuid4())
    
    try:
        logger.info(f"🎬 Starting video pipeline: {pipeline_id}")
        
        # Stage 1: Generate voice/narration
        await update_pipeline_status(pipeline_id, "processing", "voice_generation", 10, 
                                   {"message": "Generating voice narration..."})
        
        voice_request = {
            "text": request.script,
            "model": request.voice_model,
            "settings": request.voice_settings,
            "job_id": f"{pipeline_id}_voice"
        }
        
        voice_result = await call_service("voice_tts", "/generate", "POST", voice_request)
        voice_job_id = voice_result["job_id"]
        
        # Wait for voice generation to complete
        voice_completed = False
        while not voice_completed:
            voice_status = await call_service("voice_tts", f"/status/{voice_job_id}")
            if voice_status["status"] == "completed":
                voice_completed = True
                voice_url = voice_status["result_url"]
            elif voice_status["status"] == "failed":
                raise Exception(f"Voice generation failed: {voice_status.get('message', 'Unknown error')}")
            await asyncio.sleep(2)
        
        await update_pipeline_status(pipeline_id, "processing", "voice_generation", 25, 
                                   {"message": "Voice narration completed", "result_url": voice_url})
        
        # Stage 2: Generate video content
        await update_pipeline_status(pipeline_id, "processing", "video_generation", 30, 
                                   {"message": "Generating video content..."})
        
        video_request = {
            "prompt": request.script,
            "style": request.video_style,
            "settings": request.video_settings,
            "job_id": f"{pipeline_id}_video"
        }
        
        video_result = await call_service("video_generator", "/generate", "POST", video_request)
        video_job_id = video_result["job_id"]
        
        # Wait for video generation to complete
        video_completed = False
        while not video_completed:
            video_status = await call_service("video_generator", f"/status/{video_job_id}")
            if video_status["status"] == "completed":
                video_completed = True
                video_url = video_status["result_url"]
            elif video_status["status"] == "failed":
                raise Exception(f"Video generation failed: {video_status.get('message', 'Unknown error')}")
            await asyncio.sleep(2)
        
        await update_pipeline_status(pipeline_id, "processing", "video_generation", 55, 
                                   {"message": "Video content completed", "result_url": video_url})
        
        # Stage 3: Lip sync (if enabled)
        if request.lip_sync_enabled:
            await update_pipeline_status(pipeline_id, "processing", "lip_sync", 60, 
                                       {"message": "Applying lip synchronization..."})
            
            lip_sync_request = {
                "video_url": video_url,
                "audio_url": voice_url,
                "job_id": f"{pipeline_id}_lipsync"
            }
            
            lip_sync_result = await call_service("lip_sync", "/sync", "POST", lip_sync_request)
            lip_sync_job_id = lip_sync_result["job_id"]
            
            # Wait for lip sync to complete
            lip_sync_completed = False
            while not lip_sync_completed:
                lip_sync_status = await call_service("lip_sync", f"/status/{lip_sync_job_id}")
                if lip_sync_status["status"] == "completed":
                    lip_sync_completed = True
                    video_url = lip_sync_status["result_url"]  # Update video URL
                elif lip_sync_status["status"] == "failed":
                    logger.warning(f"Lip sync failed: {lip_sync_status.get('message', 'Unknown error')}")
                    break
                await asyncio.sleep(2)
            
            await update_pipeline_status(pipeline_id, "processing", "lip_sync", 75, 
                                       {"message": "Lip synchronization completed", "result_url": video_url})
        
        # Stage 4: Final composition/stitching
        await update_pipeline_status(pipeline_id, "processing", "final_composition", 80, 
                                   {"message": "Compositing final video..."})
        
        stitch_request = {
            "scenes": [video_url],
            "transitions": request.transitions,
            "output_format": request.output_format,
            "resolution": request.resolution,
            "background_music": request.background_music,
            "job_id": f"{pipeline_id}_final"
        }
        
        stitch_result = await call_service("scene_stitcher", "/stitch", "POST", stitch_request)
        stitch_job_id = stitch_result["job_id"]
        
        # Wait for final composition to complete
        stitch_completed = False
        while not stitch_completed:
            stitch_status = await call_service("scene_stitcher", f"/status/{stitch_job_id}")
            if stitch_status["status"] == "completed":
                stitch_completed = True
                final_video_url = stitch_status["result_url"]
            elif stitch_status["status"] == "failed":
                raise Exception(f"Final composition failed: {stitch_status.get('message', 'Unknown error')}")
            await asyncio.sleep(2)
        
        await update_pipeline_status(pipeline_id, "completed", "final_composition", 100, 
                                   {"message": "Video creation completed successfully!", 
                                    "result_url": final_video_url}, 
                                   result_url=final_video_url)
        
        logger.info(f"✅ Video pipeline completed: {pipeline_id}")
        return final_video_url
        
    except Exception as e:
        logger.error(f"❌ Pipeline {pipeline_id} failed: {e}")
        logger.error(traceback.format_exc())
        await update_pipeline_status(pipeline_id, "failed", error_message=str(e))
        raise

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Video GPU - API Backend",
        "version": "1.0.0",
        "status": "running",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/services/health")
async def check_services_health():
    """Check health of all microservices"""
    results = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5)
                if response.status_code == 200:
                    results[service_name] = response.json()
                else:
                    results[service_name] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
            except Exception as e:
                results[service_name] = {"status": "unhealthy", "error": str(e)}
    
    return {"services": results}

@app.post("/create-video")
async def create_video(request: VideoCreationRequest, background_tasks: BackgroundTasks):
    """Create complete video from script"""
    try:
        pipeline_id = str(uuid.uuid4())
        
        # Initialize pipeline status
        await update_pipeline_status(pipeline_id, "pending", "initialization", 0, 
                                   {"message": "Video creation pipeline queued"})
        
        # Add to background tasks
        background_tasks.add_task(execute_video_pipeline, request)
        
        return {
            "pipeline_id": pipeline_id,
            "status": "accepted",
            "message": "Video creation pipeline started"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start video creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    """Get pipeline status"""
    if pipeline_id in active_pipelines:
        return active_pipelines[pipeline_id]
    
    redis_client = await get_redis()
    if redis_client:
        try:
            pipeline_data = await redis_client.get(f"pipeline:{pipeline_id}")
            if pipeline_data:
                return json.loads(pipeline_data)
        except:
            pass
    
    raise HTTPException(status_code=404, detail="Pipeline not found")

@app.get("/pipelines")
async def list_pipelines():
    """List all pipelines"""
    return {"pipelines": list(active_pipelines.keys())}

@app.delete("/pipeline/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Delete pipeline and cleanup"""
    try:
        # Remove from active pipelines
        if pipeline_id in active_pipelines:
            del active_pipelines[pipeline_id]
        
        # Remove from Redis
        redis_client = await get_redis()
        if redis_client:
            try:
                await redis_client.delete(f"pipeline:{pipeline_id}")
            except:
                pass
        
        # Cleanup files in services (call cleanup endpoints)
        cleanup_tasks = []
        for service_name in SERVICES.keys():
            try:
                cleanup_tasks.append(call_service(service_name, f"/jobs/{pipeline_id}", "DELETE"))
            except:
                pass
        
        # Wait for cleanup to complete
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        return {"message": "Pipeline deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Proxy endpoints for direct service access
@app.api_route("/services/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_service(service_name: str, path: str, request):
    """Proxy requests to microservices"""
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service_url = SERVICES[service_name]
    url = f"{service_url}/{path}"
    
    # Forward the request
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body()
        )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

if __name__ == "__main__":
    logger.info("🌐 Starting API Backend microservice...")
    uvicorn.run(
        "api_backend_service:app",
        host="0.0.0.0",
        port=8006,
        reload=False,
        workers=1
    )
