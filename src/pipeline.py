"""
AI Video GPU - Core Pipeline
Main orchestrator for the modular video generation pipeline
"""

import torch
from pathlib import Path
from typing import Dict, List, Optional, Union
from loguru import logger
import time

from .config import ConfigManager
from .modules.enhanced_tts_engine import EnhancedTTSEngine
from .modules.wav2lip_engine import Wav2LipEngine
from .modules.visual_generation import VisualGenerationEngine
from .modules.music_engine import MusicEngine
from .modules.video_composer import VideoComposer
from .modules.avatar_3d import Avatar3D
from .utils.gpu_monitor import GPUMonitor

class AIVideoPipeline:
    """
    Main pipeline orchestrator for AI Video GPU generation
    
    Features:
    - GPU-accelerated processing
    - Modular component architecture
    - Support for 2D and 3D video generation
    - Voice cloning and lip sync
    - Background music integration
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = ConfigManager(config_path)
        self.gpu_monitor = GPUMonitor()
        
        # Initialize modules
        self.tts_engine = None
        self.lip_sync_engine = None
        self.music_engine = None
        self.video_composer = None
        self.avatar_3d = None
        
        self._initialize_modules()
        
    def _initialize_modules(self):
        """Initialize all pipeline modules based on configuration"""
        logger.info("Initializing AI Video GPU Pipeline...")
        
        # Check GPU requirements
        if not self.config.validate_gpu_requirements():
            logger.warning("GPU requirements not met. Performance may be degraded.")
        
        # Initialize core modules
        self.tts_engine = EnhancedTTSEngine(self.config)
        self.lip_sync_engine = Wav2LipEngine(self.config)
        self.music_engine = MusicEngine(self.config)
        self.video_composer = VideoComposer(self.config)
        self.visual_generator = VisualGenerationEngine(self.config)
        
        # Initialize 3D module if enabled
        if self.config.pipeline_3d.enabled:
            self.avatar_3d = Avatar3D(self.config)
            
        logger.info("Pipeline initialization complete!")
    
    def generate_video(
        self,
        script: str,
        avatar_image: Optional[str] = None,
        voice_sample: Optional[str] = None,
        background_music: Optional[str] = None,
        background_prompt: Optional[str] = None,
        visual_style: str = "photorealistic",
        output_path: str = "output/generated_video.mp4",
        use_3d: bool = False,
        use_ai_backgrounds: bool = False
    ) -> Dict[str, any]:
        """
        Generate a complete AI video from script
        
        Args:
            script: Text script to convert to video
            avatar_image: Path to avatar/face image for lip sync
            voice_sample: Path to voice sample for cloning (optional)
            background_music: Path to background music (optional)
            output_path: Where to save the final video
            use_3d: Enable 3D avatar rendering
            
        Returns:
            Dictionary with generation results and metadata
        """
        start_time = time.time()
        logger.info(f"Starting video generation for script length: {len(script)} characters")
        
        try:
            # Step 1: Generate speech from text
            logger.info("Step 1/5: Generating speech...")
            audio_path = self.tts_engine.generate_speech(
                text=script,
                voice_sample=voice_sample,
                output_path="temp/generated_audio.wav"
            )
            
            # Step 2: Generate or prepare video frames/backgrounds
            if use_ai_backgrounds and background_prompt:
                logger.info("Step 2a/6: Generating AI background...")
                background_path = self.visual_generator.generate_background(
                    prompt=background_prompt,
                    style=visual_style,
                    duration_seconds=self.tts_engine.estimate_audio_duration(script),
                    animated=False
                )
            else:
                background_path = None

            if use_3d and self.avatar_3d:
                logger.info("Step 2b/6: Generating 3D avatar frames...")
                video_frames = self.avatar_3d.generate_animation(
                    audio_path=audio_path,
                    script=script
                )
            else:
                logger.info("Step 2b/6: Preparing 2D avatar frames...")
                video_frames = self._prepare_2d_frames(avatar_image, audio_path, background_path)
            
            # Step 3: Apply lip synchronization
            logger.info("Step 3/6: Applying lip synchronization...")
            synced_video = self.lip_sync_engine.sync_lips(
                video_path=video_frames if isinstance(video_frames, str) else None,
                audio_path=audio_path,
                output_path="temp/lip_synced.mp4",
                quality=self.config.lip_sync.lip_sync_quality
            )
            
            # Step 4: Add background music
            logger.info("Step 4/6: Adding background music...")
            final_audio = self.music_engine.compose_audio(
                speech_audio=audio_path,
                background_music=background_music,
                output_path="temp/final_audio.wav"
            )
            
            # Step 5: Compose final video
            logger.info("Step 5/6: Composing final video...")
            result = self.video_composer.create_final_video(
                video_frames=synced_video,
                audio_path=final_audio,
                output_path=output_path
            )
            
            generation_time = time.time() - start_time
            logger.success(f"Video generation completed in {generation_time:.2f}s")
            
            return {
                'success': True,
                'output_path': output_path,
                'generation_time': generation_time,
                'gpu_stats': self.gpu_monitor.get_stats(),
                'metadata': {
                    'script_length': len(script),
                    'audio_duration': result.get('audio_duration', 0),
                    'video_resolution': self.config.video.output_resolution,
                    'fps': self.config.video.fps,
                    'used_3d': use_3d
                }
            }
            
        except Exception as e:
            logger.error(f"Video generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'generation_time': time.time() - start_time
            }
    
    def _prepare_2d_frames(self, avatar_image: str, audio_path: str, background_path: Optional[str] = None) -> str:
        """Prepare 2D video frames from static avatar image with optional AI background"""
        logger.info("Preparing 2D video frames...")
        
        # Load avatar image
        import cv2
        avatar = cv2.imread(avatar_image)
        if avatar is None:
            raise ValueError(f"Could not load avatar image: {avatar_image}")
        
        # Load or create background
        if background_path and Path(background_path).exists():
            background = cv2.imread(background_path)
            background = cv2.resize(background, self.config.video.output_resolution)
        else:
            # Create default background
            bg_height, bg_width = self.config.video.output_resolution[1], self.config.video.output_resolution[0]
            background = np.full((bg_height, bg_width, 3), (100, 120, 140), dtype=np.uint8)
        
        # Resize avatar to fit in frame (e.g., 1/3 of frame width)
        target_width = self.config.video.output_resolution[0] // 3
        aspect_ratio = avatar.shape[0] / avatar.shape[1]
        target_height = int(target_width * aspect_ratio)
        avatar = cv2.resize(avatar, (target_width, target_height))
        
        # Calculate duration and frame count
        import librosa
        audio, sr = librosa.load(audio_path, sr=22050)
        duration = len(audio) / sr
        fps = self.config.video.fps
        total_frames = int(duration * fps)
        
        # Create temporary video
        temp_video_path = "temp/prepared_frames.mp4"
        Path(temp_video_path).parent.mkdir(parents=True, exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, fps, self.config.video.output_resolution)
        
        for frame_idx in range(total_frames):
            # Composite avatar onto background
            frame = background.copy()
            
            # Position avatar (e.g., center-right)
            y_offset = (frame.shape[0] - avatar.shape[0]) // 2
            x_offset = frame.shape[1] - avatar.shape[1] - 50  # 50px padding from right
            
            # Simple compositing (can be enhanced with alpha blending)
            frame[y_offset:y_offset+avatar.shape[0], x_offset:x_offset+avatar.shape[1]] = avatar
            
            out.write(frame)
            
            if frame_idx % (fps * 5) == 0:
                logger.info(f"Prepared {frame_idx}/{total_frames} frames")
        
        out.release()
        
        logger.success(f"2D frames prepared: {temp_video_path}")
        return temp_video_path
    
    def batch_generate(
        self,
        scripts: List[Dict],
        output_dir: str = "output/batch"
    ) -> List[Dict]:
        """
        Generate multiple videos in batch
        
        Args:
            scripts: List of script dictionaries with generation parameters
            output_dir: Directory to save batch outputs
            
        Returns:
            List of generation results
        """
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, script_config in enumerate(scripts):
            logger.info(f"Processing batch item {i+1}/{len(scripts)}")
            
            output_file = output_path / f"video_{i+1:03d}.mp4"
            result = self.generate_video(
                script=script_config['script'],
                avatar_image=script_config.get('avatar_image'),
                voice_sample=script_config.get('voice_sample'),
                background_music=script_config.get('background_music'),
                output_path=str(output_file),
                use_3d=script_config.get('use_3d', False)
            )
            
            results.append({
                'batch_index': i,
                'script_config': script_config,
                **result
            })
        
        return results
    
    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status and capabilities"""
        return {
            'gpu_available': torch.cuda.is_available(),
            'gpu_memory': torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0,
            'modules_loaded': {
                'tts_engine': self.tts_engine is not None,
                'lip_sync_engine': self.lip_sync_engine is not None,
                'music_engine': self.music_engine is not None,
                'video_composer': self.video_composer is not None,
                'avatar_3d': self.avatar_3d is not None
            },
            'config': {
                'resolution': self.config.video.output_resolution,
                'fps': self.config.video.fps,
                '3d_enabled': self.config.pipeline_3d.enabled
            }
        }
