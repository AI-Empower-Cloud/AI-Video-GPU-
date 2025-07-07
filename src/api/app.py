"""
AI Video GPU - FastAPI Web Application
Web interface for AI video generation compatible with AI Video Generator repos
"""

from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import tempfile
import os
import asyncio
from pathlib import Path
import json

# Import our pipeline components
import sys
sys.path.append(str(Path(__file__).parent.parent))
from pipeline import AIVideoPipeline
from config import ConfigManager

class VideoGenerationRequest(BaseModel):
    script: str
    voice_sample_url: Optional[str] = None
    background_music_url: Optional[str] = None
    background_prompt: Optional[str] = None
    visual_style: str = "photorealistic"
    use_3d: bool = False
    use_ai_backgrounds: bool = False
    quality: str = "high"
    tts_backend: str = "auto"

class VideoGenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str

class CompatibilityAPI:
    """
    Compatibility layer for existing AI Video Generator repos
    Provides standardized endpoints and data structures
    """
    
    def __init__(self):
        self.app = FastAPI(
            title="AI Video GPU",
            description="GPU-accelerated AI video generation with voice cloning and lip sync",
            version="2.0.0"
        )
        self.pipeline = None
        self.tasks = {}
        self.setup_middleware()
        self.setup_routes()
        
    def setup_middleware(self):
        """Setup CORS and other middleware for compatibility"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def setup_routes(self):
        """Setup all API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Initialize pipeline on startup"""
            self.pipeline = AIVideoPipeline()
            
        @self.app.get("/")
        async def root():
            """Root endpoint for health check"""
            return {"message": "AI Video GPU API", "status": "ready"}
            
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "gpu_available": self.pipeline.gpu_monitor.is_available() if self.pipeline else False}
            
        # === VIDEO GENERATION ENDPOINTS ===
        
        @self.app.post("/generate/video", response_model=VideoGenerationResponse)
        async def generate_video(
            background_tasks: BackgroundTasks,
            script: str = Form(...),
            avatar_image: Optional[UploadFile] = File(None),
            voice_sample: Optional[UploadFile] = File(None),
            background_music: Optional[UploadFile] = File(None),
            background_prompt: Optional[str] = Form(None),
            visual_style: str = Form("photorealistic"),
            use_3d: bool = Form(False),
            use_ai_backgrounds: bool = Form(False),
            quality: str = Form("high"),
            tts_backend: str = Form("auto")
        ):
            """Generate AI video - main endpoint compatible with existing repos"""
            task_id = f"task_{len(self.tasks)}"
            
            # Save uploaded files temporarily
            temp_files = {}
            if avatar_image:
                temp_files['avatar'] = await self._save_upload(avatar_image)
            if voice_sample:
                temp_files['voice'] = await self._save_upload(voice_sample)
            if background_music:
                temp_files['music'] = await self._save_upload(background_music)
                
            # Add background task
            background_tasks.add_task(
                self._generate_video_task,
                task_id,
                script,
                temp_files,
                background_prompt,
                visual_style,
                use_3d,
                use_ai_backgrounds,
                quality,
                tts_backend
            )
            
            self.tasks[task_id] = {"status": "processing", "progress": 0}
            
            return VideoGenerationResponse(
                task_id=task_id,
                status="processing",
                message="Video generation started"
            )
            
        @self.app.get("/generate/status/{task_id}")
        async def get_generation_status(task_id: str):
            """Get video generation status"""
            if task_id not in self.tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            return self.tasks[task_id]
            
        @self.app.get("/generate/download/{task_id}")
        async def download_video(task_id: str):
            """Download generated video"""
            if task_id not in self.tasks:
                raise HTTPException(status_code=404, detail="Task not found")
                
            task_data = self.tasks[task_id]
            if task_data["status"] != "completed":
                raise HTTPException(status_code=400, detail="Video not ready")
                
            return FileResponse(
                task_data["output_path"],
                media_type="video/mp4",
                filename=f"generated_video_{task_id}.mp4"
            )
            
        # === VOICE CLONING ENDPOINTS ===
        
        @self.app.post("/voice/clone")
        async def clone_voice(
            text: str = Form(...),
            voice_sample: UploadFile = File(...),
            tts_backend: str = Form("auto")
        ):
            """Clone voice from sample - standalone endpoint"""
            voice_path = await self._save_upload(voice_sample)
            
            try:
                audio_path = self.pipeline.tts_engine.generate_speech(
                    text=text,
                    voice_sample=voice_path,
                    backend=tts_backend,
                    output_path=f"temp/cloned_voice_{len(self.tasks)}.wav"
                )
                return FileResponse(audio_path, media_type="audio/wav")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # === LIP SYNC ENDPOINTS ===
        
        @self.app.post("/lipsync/sync")
        async def sync_lips(
            video: UploadFile = File(...),
            audio: UploadFile = File(...),
            quality: str = Form("high")
        ):
            """Standalone lip sync endpoint"""
            video_path = await self._save_upload(video)
            audio_path = await self._save_upload(audio)
            
            try:
                output_path = f"temp/synced_{len(self.tasks)}.mp4"
                synced_video = self.pipeline.lip_sync_engine.sync_lips(
                    video_path=video_path,
                    audio_path=audio_path,
                    output_path=output_path,
                    quality=quality
                )
                return FileResponse(synced_video, media_type="video/mp4")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
        # === MODEL MANAGEMENT ENDPOINTS ===
        
        @self.app.get("/models/list")
        async def list_models():
            """List available models"""
            return {
                "tts_models": ["xtts", "tortoise", "speecht5"],
                "voice_clone_models": ["xtts-v2", "tortoise"],
                "lip_sync_models": ["wav2lip", "wav2lip-gan"],
                "visual_models": ["stable-diffusion", "animatediff"]
            }
            
        @self.app.post("/models/download")
        async def download_model(model_name: str = Form(...)):
            """Download/install model"""
            # Implementation for model downloading
            return {"status": "downloading", "model": model_name}
            
        # === BATCH PROCESSING ENDPOINTS ===
        
        @self.app.post("/batch/process")
        async def batch_process(
            background_tasks: BackgroundTasks,
            batch_config: str = Form(...)  # JSON string with batch configuration
        ):
            """Process multiple videos in batch"""
            try:
                batch_data = json.loads(batch_config)
                task_id = f"batch_{len(self.tasks)}"
                
                background_tasks.add_task(self._process_batch, task_id, batch_data)
                self.tasks[task_id] = {"status": "processing", "type": "batch", "progress": 0}
                
                return {"task_id": task_id, "status": "processing"}
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON configuration")
                
    async def _save_upload(self, upload_file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        suffix = Path(upload_file.filename).suffix if upload_file.filename else ".tmp"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await upload_file.read()
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
        
    async def _generate_video_task(
        self,
        task_id: str,
        script: str,
        temp_files: Dict[str, str],
        background_prompt: Optional[str],
        visual_style: str,
        use_3d: bool,
        use_ai_backgrounds: bool,
        quality: str,
        tts_backend: str
    ):
        """Background task for video generation"""
        try:
            self.tasks[task_id]["progress"] = 10
            
            output_path = f"output/generated_video_{task_id}.mp4"
            
            # Update pipeline config based on request
            self.pipeline.config.lip_sync.lip_sync_quality = quality
            self.pipeline.config.tts.backend = tts_backend
            
            result = self.pipeline.generate_video(
                script=script,
                avatar_image=temp_files.get('avatar'),
                voice_sample=temp_files.get('voice'),
                background_music=temp_files.get('music'),
                background_prompt=background_prompt,
                visual_style=visual_style,
                output_path=output_path,
                use_3d=use_3d,
                use_ai_backgrounds=use_ai_backgrounds
            )
            
            self.tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "output_path": output_path,
                "result": result
            })
            
        except Exception as e:
            self.tasks[task_id].update({
                "status": "failed",
                "error": str(e),
                "progress": 0
            })
        finally:
            # Clean up temporary files
            for temp_path in temp_files.values():
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
    async def _process_batch(self, task_id: str, batch_data: Dict[str, Any]):
        """Process batch of videos"""
        try:
            items = batch_data.get("items", [])
            total_items = len(items)
            
            for i, item in enumerate(items):
                # Process each item
                progress = int((i / total_items) * 100)
                self.tasks[task_id]["progress"] = progress
                
                # Add individual processing logic here
                await asyncio.sleep(1)  # Placeholder
                
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["progress"] = 100
            
        except Exception as e:
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = str(e)

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    api = CompatibilityAPI()
    return api.app

# For direct running
if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
