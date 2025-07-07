"""
AI Video GPU - Compatibility Layer
Interface layer for seamless integration with existing AI Video Generator repositories
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import importlib.util
from loguru import logger

class RepoCompatibilityManager:
    """
    Manages compatibility with existing AI Video Generator repositories
    Provides standardized interfaces and data transformation
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.config_mappings = {}
        self.api_mappings = {}
        self.detected_frameworks = []
        
        self._detect_existing_frameworks()
        self._setup_compatibility_mappings()
        
    def _detect_existing_frameworks(self):
        """Detect what frameworks/libraries are used in the existing repo"""
        frameworks = {
            'gradio': self._check_gradio,
            'streamlit': self._check_streamlit,
            'flask': self._check_flask,
            'fastapi': self._check_fastapi,
            'wav2lip': self._check_wav2lip,
            'tortoise': self._check_tortoise,
            'coqui': self._check_coqui,
            'stable_diffusion': self._check_stable_diffusion,
            'blender': self._check_blender
        }
        
        for framework, check_func in frameworks.items():
            if check_func():
                self.detected_frameworks.append(framework)
                logger.info(f"Detected framework: {framework}")
                
    def _check_gradio(self) -> bool:
        """Check if Gradio is used"""
        return (
            self._file_contains_import('gradio') or
            self._check_requirements('gradio')
        )
        
    def _check_streamlit(self) -> bool:
        """Check if Streamlit is used"""
        return (
            self._file_contains_import('streamlit') or
            self._check_requirements('streamlit')
        )
        
    def _check_flask(self) -> bool:
        """Check if Flask is used"""
        return (
            self._file_contains_import('flask') or
            self._check_requirements('flask')
        )
        
    def _check_fastapi(self) -> bool:
        """Check if FastAPI is used"""
        return (
            self._file_contains_import('fastapi') or
            self._check_requirements('fastapi')
        )
        
    def _check_wav2lip(self) -> bool:
        """Check if Wav2Lip is used"""
        return (
            (self.repo_path / 'Wav2Lip').exists() or
            self._file_contains_import('wav2lip') or
            self._check_requirements('wav2lip')
        )
        
    def _check_tortoise(self) -> bool:
        """Check if Tortoise TTS is used"""
        return (
            self._file_contains_import('tortoise') or
            self._check_requirements('tortoise')
        )
        
    def _check_coqui(self) -> bool:
        """Check if Coqui TTS is used"""
        return (
            self._file_contains_import('TTS') or
            self._check_requirements('TTS')
        )
        
    def _check_stable_diffusion(self) -> bool:
        """Check if Stable Diffusion is used"""
        return (
            self._file_contains_import('diffusers') or
            self._check_requirements('diffusers') or
            self._file_contains_import('stable_diffusion')
        )
        
    def _check_blender(self) -> bool:
        """Check if Blender is used"""
        return (
            self._file_contains_import('bpy') or
            self._check_requirements('bpy') or
            (self.repo_path / 'blender').exists()
        )
        
    def _file_contains_import(self, module_name: str) -> bool:
        """Check if any Python file contains import for the module"""
        for py_file in self.repo_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if f"import {module_name}" in content or f"from {module_name}" in content:
                        return True
            except:
                continue
        return False
        
    def _check_requirements(self, package_name: str) -> bool:
        """Check if package is in requirements files"""
        req_files = [
            'requirements.txt',
            'requirements-dev.txt',
            'pyproject.toml',
            'setup.py'
        ]
        
        for req_file in req_files:
            req_path = self.repo_path / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r') as f:
                        content = f.read().lower()
                        if package_name.lower() in content:
                            return True
                except:
                    continue
        return False
        
    def _setup_compatibility_mappings(self):
        """Setup API and configuration mappings for different frameworks"""
        
        # Standard AI Video Generator API mappings
        self.api_mappings = {
            'generate_video': {
                'gradio': self._gradio_generate_wrapper,
                'streamlit': self._streamlit_generate_wrapper,
                'flask': self._flask_generate_wrapper,
                'fastapi': self._fastapi_generate_wrapper,
                'default': self._default_generate_wrapper
            },
            'clone_voice': {
                'gradio': self._gradio_voice_wrapper,
                'default': self._default_voice_wrapper
            },
            'sync_lips': {
                'wav2lip': self._wav2lip_wrapper,
                'default': self._default_lipsync_wrapper
            }
        }
        
        # Configuration mappings for different TTS/Video frameworks
        self.config_mappings = {
            'tortoise': {
                'model_path': 'models/tortoise',
                'config_file': 'tortoise_config.json',
                'voice_samples': 'voices/'
            },
            'coqui': {
                'model_path': 'models/coqui',
                'config_file': 'coqui_config.json'
            },
            'wav2lip': {
                'model_path': 'models/wav2lip_gan.pth',
                'face_detection': 'models/face_detection.pth'
            }
        }
        
    def create_compatibility_bridge(self) -> Dict[str, Any]:
        """
        Create a bridge interface that existing repos can use
        Returns a dictionary of compatible functions and configurations
        """
        
        bridge = {
            'generate_video': self._create_video_function(),
            'clone_voice': self._create_voice_function(),
            'sync_lips': self._create_lipsync_function(),
            'get_models': self._create_models_function(),
            'config': self._create_config_bridge(),
            'frameworks': self.detected_frameworks
        }
        
        return bridge
        
    def _create_video_function(self):
        """Create compatible video generation function"""
        def generate_video(*args, **kwargs):
            # Import our pipeline
            from ..pipeline import AIVideoPipeline
            
            pipeline = AIVideoPipeline()
            
            # Map arguments based on detected framework
            mapped_args = self._map_video_arguments(*args, **kwargs)
            
            return pipeline.generate_video(**mapped_args)
            
        return generate_video
        
    def _create_voice_function(self):
        """Create compatible voice cloning function"""
        def clone_voice(*args, **kwargs):
            from ..modules.enhanced_tts_engine import EnhancedTTSEngine
            from ..config import ConfigManager
            
            config = ConfigManager()
            tts_engine = EnhancedTTSEngine(config)
            
            mapped_args = self._map_voice_arguments(*args, **kwargs)
            
            return tts_engine.generate_speech(**mapped_args)
            
        return clone_voice
        
    def _create_lipsync_function(self):
        """Create compatible lip sync function"""
        def sync_lips(*args, **kwargs):
            from ..modules.wav2lip_engine import Wav2LipEngine
            from ..config import ConfigManager
            
            config = ConfigManager()
            lip_sync = Wav2LipEngine(config)
            
            mapped_args = self._map_lipsync_arguments(*args, **kwargs)
            
            return lip_sync.sync_lips(**mapped_args)
            
        return sync_lips
        
    def _create_models_function(self):
        """Create model management function"""
        def get_models():
            return {
                'available_models': {
                    'tts': ['xtts', 'tortoise', 'speecht5'],
                    'lip_sync': ['wav2lip', 'wav2lip-gan'],
                    'voice_clone': ['xtts-v2', 'tortoise'],
                    'visual': ['stable-diffusion', 'animatediff']
                },
                'detected_frameworks': self.detected_frameworks
            }
            
        return get_models
        
    def _create_config_bridge(self):
        """Create configuration bridge for existing repos"""
        from ..config import ConfigManager
        
        config_manager = ConfigManager()
        
        # Merge with existing configurations if found
        existing_configs = self._find_existing_configs()
        
        bridge_config = {
            'ai_video_gpu': config_manager.get_all_config(),
            'existing_configs': existing_configs,
            'compatibility_mappings': self.config_mappings
        }
        
        return bridge_config
        
    def _find_existing_configs(self) -> Dict[str, Any]:
        """Find and parse existing configuration files"""
        configs = {}
        
        config_files = [
            'config.json',
            'config.yaml',
            'config.yml',
            'settings.json',
            'app_config.json'
        ]
        
        for config_file in config_files:
            config_path = self.repo_path / config_file
            if config_path.exists():
                try:
                    if config_file.endswith('.json'):
                        with open(config_path, 'r') as f:
                            configs[config_file] = json.load(f)
                    elif config_file.endswith(('.yaml', '.yml')):
                        import yaml
                        with open(config_path, 'r') as f:
                            configs[config_file] = yaml.safe_load(f)
                except Exception as e:
                    logger.warning(f"Could not parse config file {config_file}: {e}")
                    
        return configs
        
    def _map_video_arguments(self, *args, **kwargs) -> Dict[str, Any]:
        """Map video generation arguments to our standard format"""
        
        # Common argument mappings from different frameworks
        arg_mappings = {
            'text': 'script',
            'input_text': 'script',
            'script_text': 'script',
            'prompt': 'script',
            'avatar': 'avatar_image',
            'face_image': 'avatar_image',
            'reference_image': 'avatar_image',
            'voice': 'voice_sample',
            'voice_file': 'voice_sample',
            'reference_voice': 'voice_sample',
            'music': 'background_music',
            'background': 'background_music',
            'bg_music': 'background_music',
            'output_file': 'output_path',
            'output_video': 'output_path',
            'result_path': 'output_path'
        }
        
        mapped = {}
        
        # Map kwargs
        for old_key, new_key in arg_mappings.items():
            if old_key in kwargs:
                mapped[new_key] = kwargs[old_key]
                
        # Add unmapped kwargs
        for key, value in kwargs.items():
            if key not in arg_mappings:
                mapped[key] = value
                
        # Handle positional arguments (common patterns)
        if args:
            if len(args) >= 1 and 'script' not in mapped:
                mapped['script'] = args[0]
            if len(args) >= 2 and 'avatar_image' not in mapped:
                mapped['avatar_image'] = args[1]
            if len(args) >= 3 and 'voice_sample' not in mapped:
                mapped['voice_sample'] = args[2]
                
        return mapped
        
    def _map_voice_arguments(self, *args, **kwargs) -> Dict[str, Any]:
        """Map voice cloning arguments"""
        arg_mappings = {
            'input_text': 'text',
            'script': 'text',
            'voice_file': 'voice_sample',
            'reference_voice': 'voice_sample',
            'model': 'backend'
        }
        
        mapped = {}
        for old_key, new_key in arg_mappings.items():
            if old_key in kwargs:
                mapped[new_key] = kwargs[old_key]
                
        for key, value in kwargs.items():
            if key not in arg_mappings:
                mapped[key] = value
                
        if args:
            if len(args) >= 1 and 'text' not in mapped:
                mapped['text'] = args[0]
            if len(args) >= 2 and 'voice_sample' not in mapped:
                mapped['voice_sample'] = args[1]
                
        return mapped
        
    def _map_lipsync_arguments(self, *args, **kwargs) -> Dict[str, Any]:
        """Map lip sync arguments"""
        arg_mappings = {
            'video_file': 'video_path',
            'input_video': 'video_path',
            'audio_file': 'audio_path',
            'input_audio': 'audio_path',
            'output_file': 'output_path',
            'result_video': 'output_path'
        }
        
        mapped = {}
        for old_key, new_key in arg_mappings.items():
            if old_key in kwargs:
                mapped[new_key] = kwargs[old_key]
                
        for key, value in kwargs.items():
            if key not in arg_mappings:
                mapped[key] = value
                
        if args:
            if len(args) >= 1 and 'video_path' not in mapped:
                mapped['video_path'] = args[0]
            if len(args) >= 2 and 'audio_path' not in mapped:
                mapped['audio_path'] = args[1]
                
        return mapped
        
    # Framework-specific wrappers
    def _gradio_generate_wrapper(self, *args, **kwargs):
        """Gradio-specific video generation wrapper"""
        return self._default_generate_wrapper(*args, **kwargs)
        
    def _streamlit_generate_wrapper(self, *args, **kwargs):
        """Streamlit-specific video generation wrapper"""
        return self._default_generate_wrapper(*args, **kwargs)
        
    def _flask_generate_wrapper(self, *args, **kwargs):
        """Flask-specific video generation wrapper"""
        return self._default_generate_wrapper(*args, **kwargs)
        
    def _fastapi_generate_wrapper(self, *args, **kwargs):
        """FastAPI-specific video generation wrapper"""
        return self._default_generate_wrapper(*args, **kwargs)
        
    def _default_generate_wrapper(self, *args, **kwargs):
        """Default video generation wrapper"""
        mapped_args = self._map_video_arguments(*args, **kwargs)
        
        from ..pipeline import AIVideoPipeline
        pipeline = AIVideoPipeline()
        
        return pipeline.generate_video(**mapped_args)
        
    def _gradio_voice_wrapper(self, *args, **kwargs):
        """Gradio-specific voice cloning wrapper"""
        return self._default_voice_wrapper(*args, **kwargs)
        
    def _default_voice_wrapper(self, *args, **kwargs):
        """Default voice cloning wrapper"""
        mapped_args = self._map_voice_arguments(*args, **kwargs)
        
        from ..modules.enhanced_tts_engine import EnhancedTTSEngine
        from ..config import ConfigManager
        
        config = ConfigManager()
        tts_engine = EnhancedTTSEngine(config)
        
        return tts_engine.generate_speech(**mapped_args)
        
    def _wav2lip_wrapper(self, *args, **kwargs):
        """Wav2Lip-specific wrapper"""
        return self._default_lipsync_wrapper(*args, **kwargs)
        
    def _default_lipsync_wrapper(self, *args, **kwargs):
        """Default lip sync wrapper"""
        mapped_args = self._map_lipsync_arguments(*args, **kwargs)
        
        from ..modules.wav2lip_engine import Wav2LipEngine
        from ..config import ConfigManager
        
        config = ConfigManager()
        lip_sync = Wav2LipEngine(config)
        
        return lip_sync.sync_lips(**mapped_args)
        
    def create_integration_script(self, output_path: str = "ai_video_gpu_integration.py"):
        """
        Create a standalone integration script for existing repos
        """
        integration_code = f'''"""
AI Video GPU Integration Script
Auto-generated compatibility layer for existing AI Video Generator repositories

Usage:
    from ai_video_gpu_integration import ai_video_gpu

    # Use the same functions as before, but with GPU acceleration
    result = ai_video_gpu.generate_video(
        script="Hello world",
        avatar_image="path/to/avatar.jpg",
        voice_sample="path/to/voice.wav"
    )
"""

import sys
import os
from pathlib import Path

# Add AI Video GPU to path
AI_VIDEO_GPU_PATH = "{Path(__file__).parent.absolute()}"
sys.path.insert(0, AI_VIDEO_GPU_PATH)

try:
    from src.compatibility.repo_compatibility import RepoCompatibilityManager
    
    # Initialize compatibility manager
    _compat_manager = RepoCompatibilityManager()
    
    # Create compatibility bridge
    _bridge = _compat_manager.create_compatibility_bridge()
    
    class AIVideoGPUBridge:
        """
        Compatibility bridge for AI Video GPU
        Provides the same interface as existing repos but with GPU acceleration
        """
        
        def __init__(self):
            self.detected_frameworks = {_bridge['frameworks']}
            self.config = _bridge['config']
            
        def generate_video(self, *args, **kwargs):
            """Generate AI video with GPU acceleration"""
            return _bridge['generate_video'](*args, **kwargs)
            
        def clone_voice(self, *args, **kwargs):
            """Clone voice with enhanced TTS"""
            return _bridge['clone_voice'](*args, **kwargs)
            
        def sync_lips(self, *args, **kwargs):
            """Advanced lip synchronization"""
            return _bridge['sync_lips'](*args, **kwargs)
            
        def get_available_models(self):
            """Get available AI models"""
            return _bridge['get_models']()
            
        # Alias methods for compatibility
        create_video = generate_video
        lip_sync = sync_lips
        voice_clone = clone_voice
        
    # Create global instance
    ai_video_gpu = AIVideoGPUBridge()
    
    # Export main functions for direct import
    generate_video = ai_video_gpu.generate_video
    clone_voice = ai_video_gpu.clone_voice
    sync_lips = ai_video_gpu.sync_lips
    create_video = ai_video_gpu.create_video
    lip_sync = ai_video_gpu.lip_sync
    voice_clone = ai_video_gpu.voice_clone
    
    print("✅ AI Video GPU integration loaded successfully!")
    print(f"📦 Detected frameworks: {{', '.join(ai_video_gpu.detected_frameworks)}}")
    
except ImportError as e:
    print(f"❌ Failed to import AI Video GPU: {{e}}")
    print("Please ensure AI Video GPU is properly installed.")
    
    # Fallback - create dummy functions that show helpful error messages
    def generate_video(*args, **kwargs):
        raise ImportError("AI Video GPU not available. Please check installation.")
        
    def clone_voice(*args, **kwargs):
        raise ImportError("AI Video GPU not available. Please check installation.")
        
    def sync_lips(*args, **kwargs):
        raise ImportError("AI Video GPU not available. Please check installation.")
        
    ai_video_gpu = None
'''
        
        with open(output_path, 'w') as f:
            f.write(integration_code)
            
        logger.info(f"Integration script created: {output_path}")
        return output_path

# Global instance for easy import
compatibility_manager = RepoCompatibilityManager()
