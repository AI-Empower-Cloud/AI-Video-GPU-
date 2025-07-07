"""
AI Video GPU - Configuration Management
Centralized configuration for all pipeline components
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import torch

@dataclass
class GPUConfig:
    """GPU acceleration settings"""
    enabled: bool = True
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    memory_fraction: float = 0.8
    mixed_precision: bool = True
    
@dataclass
class TTSConfig:
    """Text-to-Speech configuration"""
    model_name: str = "microsoft/speecht5_tts"
    voice_clone_model: str = "coqui/XTTS-v2"
    sample_rate: int = 22050
    speed: float = 1.0
    
@dataclass
class LipSyncConfig:
    """Lip synchronization settings"""
    model_path: str = "models/wav2lip"
    face_detection_confidence: float = 0.8
    lip_sync_quality: str = "high"  # low, medium, high
    
@dataclass
class VideoConfig:
    """Video generation settings"""
    output_resolution: tuple = (1920, 1080)  # HD by default
    fps: int = 30
    codec: str = "h264"
    bitrate: str = "5M"
    format: str = "mp4"
    
@dataclass
class Audio3DConfig:
    """3D audio and spatial settings"""
    enabled: bool = False
    spatial_audio: bool = False
    reverb_level: float = 0.2
    
@dataclass
class MusicConfig:
    """Background music settings"""
    enabled: bool = True
    volume_level: float = 0.3
    fade_duration: float = 2.0
    auto_generate: bool = False
    
@dataclass
class Pipeline3DConfig:
    """3D animation and rendering"""
    enabled: bool = False
    avatar_model: str = "models/3d_avatar"
    render_engine: str = "blender"  # blender, unity, custom
    lighting_preset: str = "studio"
    
class ConfigManager:
    """Manages all configuration settings for the AI Video GPU pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("config/default.yaml")
        self.gpu = GPUConfig()
        self.tts = TTSConfig()
        self.lip_sync = LipSyncConfig()
        self.video = VideoConfig()
        self.audio_3d = Audio3DConfig()
        self.music = MusicConfig()
        self.pipeline_3d = Pipeline3DConfig()
        
        # Load config if file exists
        if self.config_path.exists():
            self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        if 'gpu' in config_data:
            self.gpu = GPUConfig(**config_data['gpu'])
        if 'tts' in config_data:
            self.tts = TTSConfig(**config_data['tts'])
        if 'lip_sync' in config_data:
            self.lip_sync = LipSyncConfig(**config_data['lip_sync'])
        if 'video' in config_data:
            self.video = VideoConfig(**config_data['video'])
        if 'audio_3d' in config_data:
            self.audio_3d = Audio3DConfig(**config_data['audio_3d'])
        if 'music' in config_data:
            self.music = MusicConfig(**config_data['music'])
        if 'pipeline_3d' in config_data:
            self.pipeline_3d = Pipeline3DConfig(**config_data['pipeline_3d'])
    
    def save_config(self):
        """Save current configuration to YAML file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            'gpu': asdict(self.gpu),
            'tts': asdict(self.tts),
            'lip_sync': asdict(self.lip_sync),
            'video': asdict(self.video),
            'audio_3d': asdict(self.audio_3d),
            'music': asdict(self.music),
            'pipeline_3d': asdict(self.pipeline_3d)
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def get_device(self) -> torch.device:
        """Get the appropriate torch device"""
        if self.gpu.enabled and torch.cuda.is_available():
            return torch.device(self.gpu.device)
        return torch.device("cpu")
    
    def validate_gpu_requirements(self) -> bool:
        """Check if GPU requirements are met"""
        if not torch.cuda.is_available():
            return False
        
        gpu_memory = torch.cuda.get_device_properties(0).total_memory
        # Require at least 8GB for basic operations, 16GB+ recommended
        return gpu_memory >= 8 * 1024**3
