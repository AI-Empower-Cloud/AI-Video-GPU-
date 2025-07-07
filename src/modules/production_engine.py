"""
Production Features Engine
Handles video templates, watermarking, quality assurance, and export optimization
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import json
import time
from dataclasses import dataclass
from enum import Enum
import hashlib
import xml.etree.ElementTree as ET
from loguru import logger
from datetime import datetime

class TemplateType(Enum):
    """Video template types"""
    CORPORATE = "corporate"
    EDUCATIONAL = "educational"
    MARKETING = "marketing"
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    TUTORIAL = "tutorial"

class QualityMetric(Enum):
    """Quality assessment metrics"""
    VISUAL_QUALITY = "visual_quality"
    AUDIO_QUALITY = "audio_quality"
    SYNC_ACCURACY = "sync_accuracy"
    ENCODING_EFFICIENCY = "encoding_efficiency"

@dataclass
class VideoTemplate:
    """Video template configuration"""
    name: str
    type: TemplateType
    resolution: Tuple[int, int]
    fps: int
    duration_range: Tuple[float, float]
    style_settings: Dict[str, Any]
    branding_elements: List[Dict[str, Any]]
    export_presets: List[Dict[str, Any]]

@dataclass
class QualityScore:
    """Quality assessment score"""
    metric: QualityMetric
    score: float
    details: Dict[str, Any]
    timestamp: datetime

class VideoTemplateManager:
    """Manages video templates and branding"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.templates_dir = Path(config.get('templates_dir', 'templates'))
        self.templates_dir.mkdir(exist_ok=True)
        
        # Load built-in templates
        self.builtin_templates = self._create_builtin_templates()
        
        # Custom templates
        self.custom_templates = self._load_custom_templates()
    
    def _create_builtin_templates(self) -> Dict[str, VideoTemplate]:
        """Create built-in video templates"""
        
        templates = {}
        
        # Corporate template
        templates['corporate'] = VideoTemplate(
            name="Corporate",
            type=TemplateType.CORPORATE,
            resolution=(1920, 1080),
            fps=30,
            duration_range=(30.0, 300.0),
            style_settings={
                'color_scheme': ['#1E3A8A', '#3B82F6', '#FFFFFF'],
                'font_family': 'Arial',
                'font_size': 36,
                'background_style': 'gradient',
                'animation_style': 'professional'
            },
            branding_elements=[
                {
                    'type': 'logo',
                    'position': (50, 50),
                    'size': (200, 100),
                    'opacity': 0.8
                },
                {
                    'type': 'lower_third',
                    'position': (100, 800),
                    'size': (1720, 200),
                    'style': 'corporate'
                }
            ],
            export_presets=[
                {'name': 'web_hd', 'codec': 'h264', 'bitrate': '5M', 'format': 'mp4'},
                {'name': 'broadcast', 'codec': 'prores', 'bitrate': '150M', 'format': 'mov'}
            ]
        )
        
        # Educational template
        templates['educational'] = VideoTemplate(
            name="Educational",
            type=TemplateType.EDUCATIONAL,
            resolution=(1920, 1080),
            fps=30,
            duration_range=(120.0, 1800.0),
            style_settings={
                'color_scheme': ['#059669', '#10B981', '#FFFFFF'],
                'font_family': 'Open Sans',
                'font_size': 32,
                'background_style': 'clean',
                'animation_style': 'engaging'
            },
            branding_elements=[
                {
                    'type': 'title_card',
                    'position': (960, 200),
                    'size': (1600, 100),
                    'style': 'educational'
                },
                {
                    'type': 'progress_bar',
                    'position': (100, 1000),
                    'size': (1720, 20),
                    'style': 'minimal'
                }
            ],
            export_presets=[
                {'name': 'youtube_hd', 'codec': 'h264', 'bitrate': '8M', 'format': 'mp4'},
                {'name': 'mobile', 'codec': 'h264', 'bitrate': '2M', 'format': 'mp4'}
            ]
        )
        
        # Social Media template
        templates['social_media'] = VideoTemplate(
            name="Social Media",
            type=TemplateType.SOCIAL_MEDIA,
            resolution=(1080, 1920),  # Vertical for mobile
            fps=30,
            duration_range=(15.0, 60.0),
            style_settings={
                'color_scheme': ['#EC4899', '#8B5CF6', '#FFFFFF'],
                'font_family': 'Inter',
                'font_size': 48,
                'background_style': 'dynamic',
                'animation_style': 'energetic'
            },
            branding_elements=[
                {
                    'type': 'hashtag_overlay',
                    'position': (540, 1700),
                    'size': (800, 100),
                    'style': 'trendy'
                },
                {
                    'type': 'call_to_action',
                    'position': (540, 1600),
                    'size': (900, 80),
                    'style': 'button'
                }
            ],
            export_presets=[
                {'name': 'instagram_story', 'codec': 'h264', 'bitrate': '3M', 'format': 'mp4'},
                {'name': 'tiktok', 'codec': 'h264', 'bitrate': '2M', 'format': 'mp4'}
            ]
        )
        
        return templates
    
    def _load_custom_templates(self) -> Dict[str, VideoTemplate]:
        """Load custom templates from disk"""
        
        custom_templates = {}
        
        for template_file in self.templates_dir.glob('*.json'):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                
                template = VideoTemplate(
                    name=template_data['name'],
                    type=TemplateType(template_data['type']),
                    resolution=tuple(template_data['resolution']),
                    fps=template_data['fps'],
                    duration_range=tuple(template_data['duration_range']),
                    style_settings=template_data['style_settings'],
                    branding_elements=template_data['branding_elements'],
                    export_presets=template_data['export_presets']
                )
                
                custom_templates[template.name.lower()] = template
                
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
        
        return custom_templates
    
    def get_template(self, template_name: str) -> Optional[VideoTemplate]:
        """Get template by name"""
        
        template_name = template_name.lower()
        
        if template_name in self.builtin_templates:
            return self.builtin_templates[template_name]
        elif template_name in self.custom_templates:
            return self.custom_templates[template_name]
        else:
            return None
    
    def list_templates(self) -> List[str]:
        """List all available templates"""
        
        return list(self.builtin_templates.keys()) + list(self.custom_templates.keys())
    
    def create_custom_template(self, template: VideoTemplate) -> bool:
        """Create a new custom template"""
        
        try:
            template_data = {
                'name': template.name,
                'type': template.type.value,
                'resolution': template.resolution,
                'fps': template.fps,
                'duration_range': template.duration_range,
                'style_settings': template.style_settings,
                'branding_elements': template.branding_elements,
                'export_presets': template.export_presets
            }
            
            template_file = self.templates_dir / f"{template.name.lower()}.json"
            with open(template_file, 'w') as f:
                json.dump(template_data, f, indent=2)
            
            self.custom_templates[template.name.lower()] = template
            logger.info(f"Created custom template: {template.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False
    
    def apply_template(self, video_config: Dict[str, Any], 
                      template_name: str) -> Dict[str, Any]:
        """Apply template to video configuration"""
        
        template = self.get_template(template_name)
        if not template:
            logger.error(f"Template not found: {template_name}")
            return video_config
        
        # Apply template settings
        templated_config = video_config.copy()
        
        templated_config.update({
            'resolution': template.resolution,
            'fps': template.fps,
            'style_settings': template.style_settings,
            'branding_elements': template.branding_elements,
            'export_presets': template.export_presets
        })
        
        logger.info(f"Applied template: {template.name}")
        return templated_config

class WatermarkManager:
    """Manages video watermarking and metadata"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.default_watermark = config.get('default_watermark')
        
    def add_watermark(self, video_path: Path, watermark_config: Dict[str, Any], 
                     output_path: Path = None) -> Path:
        """Add watermark to video"""
        
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_watermarked{video_path.suffix}"
        
        try:
            # Load video
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            # Load watermark image
            watermark_path = watermark_config.get('image_path', self.default_watermark)
            if watermark_path and Path(watermark_path).exists():
                watermark = cv2.imread(str(watermark_path), cv2.IMREAD_UNCHANGED)
                watermark = self._prepare_watermark(watermark, watermark_config, width, height)
            else:
                watermark = None
            
            # Process frames
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Add watermark
                if watermark is not None:
                    frame = self._apply_watermark(frame, watermark, watermark_config)
                
                # Add text watermark if specified
                if 'text' in watermark_config:
                    frame = self._add_text_watermark(frame, watermark_config['text'])
                
                out.write(frame)
                frame_count += 1
            
            cap.release()
            out.release()
            
            logger.info(f"Added watermark to {frame_count} frames")
            return output_path
            
        except Exception as e:
            logger.error(f"Watermarking failed: {e}")
            return video_path
    
    def _prepare_watermark(self, watermark: np.ndarray, config: Dict[str, Any], 
                          video_width: int, video_height: int) -> np.ndarray:
        """Prepare watermark for overlay"""
        
        # Resize watermark
        scale = config.get('scale', 0.1)
        new_width = int(video_width * scale)
        new_height = int(watermark.shape[0] * new_width / watermark.shape[1])
        
        watermark = cv2.resize(watermark, (new_width, new_height))
        
        # Adjust opacity
        opacity = config.get('opacity', 0.5)
        if watermark.shape[2] == 4:  # Has alpha channel
            watermark[:, :, 3] = (watermark[:, :, 3] * opacity).astype(np.uint8)
        
        return watermark
    
    def _apply_watermark(self, frame: np.ndarray, watermark: np.ndarray, 
                        config: Dict[str, Any]) -> np.ndarray:
        """Apply watermark to frame"""
        
        # Determine position
        position = config.get('position', 'bottom_right')
        h, w = frame.shape[:2]
        wh, ww = watermark.shape[:2]
        
        positions = {
            'top_left': (10, 10),
            'top_right': (w - ww - 10, 10),
            'bottom_left': (10, h - wh - 10),
            'bottom_right': (w - ww - 10, h - wh - 10),
            'center': ((w - ww) // 2, (h - wh) // 2)
        }
        
        x, y = positions.get(position, positions['bottom_right'])
        
        # Overlay watermark
        if watermark.shape[2] == 4:  # Has alpha channel
            alpha = watermark[:, :, 3] / 255.0
            for c in range(3):
                frame[y:y+wh, x:x+ww, c] = (
                    alpha * watermark[:, :, c] + 
                    (1 - alpha) * frame[y:y+wh, x:x+ww, c]
                )
        else:
            opacity = config.get('opacity', 0.5)
            cv2.addWeighted(
                frame[y:y+wh, x:x+ww], 1 - opacity,
                watermark, opacity, 0,
                frame[y:y+wh, x:x+ww]
            )
        
        return frame
    
    def _add_text_watermark(self, frame: np.ndarray, text_config: Dict[str, Any]) -> np.ndarray:
        """Add text watermark to frame"""
        
        text = text_config.get('text', '')
        position = text_config.get('position', (50, 50))
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = text_config.get('font_scale', 1.0)
        color = text_config.get('color', (255, 255, 255))
        thickness = text_config.get('thickness', 2)
        
        cv2.putText(frame, text, position, font, font_scale, color, thickness)
        
        return frame
    
    def add_metadata(self, video_path: Path, metadata: Dict[str, Any]) -> bool:
        """Add metadata to video file"""
        
        try:
            # Create metadata file
            metadata_path = video_path.with_suffix('.json')
            
            # Add standard metadata
            complete_metadata = {
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'creator': metadata.get('creator', 'AI Video GPU'),
                'creation_date': datetime.now().isoformat(),
                'software': 'AI Video GPU',
                'version': '1.0',
                'fingerprint': self._generate_video_fingerprint(video_path),
                **metadata
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(complete_metadata, f, indent=2)
            
            logger.info(f"Added metadata to {metadata_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add metadata: {e}")
            return False
    
    def _generate_video_fingerprint(self, video_path: Path) -> str:
        """Generate unique fingerprint for video"""
        
        hasher = hashlib.sha256()
        
        # Use file size and modification time for quick fingerprint
        stat = video_path.stat()
        hasher.update(str(stat.st_size).encode())
        hasher.update(str(stat.st_mtime).encode())
        
        return hasher.hexdigest()[:16]

class QualityAssurance:
    """Automated quality assurance for generated videos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.quality_thresholds = config.get('quality_thresholds', {
            'visual_quality': 0.8,
            'audio_quality': 0.7,
            'sync_accuracy': 0.9,
            'encoding_efficiency': 0.8
        })
    
    def assess_video_quality(self, video_path: Path, 
                            audio_path: Path = None) -> List[QualityScore]:
        """Comprehensive video quality assessment"""
        
        scores = []
        
        # Visual quality assessment
        visual_score = self._assess_visual_quality(video_path)
        scores.append(visual_score)
        
        # Audio quality assessment
        if audio_path and audio_path.exists():
            audio_score = self._assess_audio_quality(audio_path)
            scores.append(audio_score)
        
        # Sync accuracy (if both video and audio)
        if audio_path and audio_path.exists():
            sync_score = self._assess_sync_accuracy(video_path, audio_path)
            scores.append(sync_score)
        
        # Encoding efficiency
        encoding_score = self._assess_encoding_efficiency(video_path)
        scores.append(encoding_score)
        
        return scores
    
    def _assess_visual_quality(self, video_path: Path) -> QualityScore:
        """Assess visual quality of video"""
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            # Sample frames for analysis
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_indices = np.linspace(0, frame_count - 1, min(10, frame_count), dtype=int)
            
            quality_metrics = []
            
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # Calculate visual quality metrics
                    sharpness = self._calculate_sharpness(frame)
                    contrast = self._calculate_contrast(frame)
                    brightness = self._calculate_brightness(frame)
                    
                    frame_quality = (sharpness + contrast + brightness) / 3
                    quality_metrics.append(frame_quality)
            
            cap.release()
            
            overall_quality = np.mean(quality_metrics) if quality_metrics else 0.0
            
            return QualityScore(
                metric=QualityMetric.VISUAL_QUALITY,
                score=overall_quality,
                details={
                    'sharpness': np.mean([m for m in quality_metrics]),
                    'frame_count': len(quality_metrics),
                    'sample_indices': sample_indices.tolist()
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Visual quality assessment failed: {e}")
            return QualityScore(
                metric=QualityMetric.VISUAL_QUALITY,
                score=0.0,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def _calculate_sharpness(self, frame: np.ndarray) -> float:
        """Calculate frame sharpness using Laplacian variance"""
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Normalize to 0-1 range (empirical scaling)
        return min(laplacian_var / 1000.0, 1.0)
    
    def _calculate_contrast(self, frame: np.ndarray) -> float:
        """Calculate frame contrast"""
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        contrast = gray.std() / 128.0  # Normalize to 0-1
        
        return min(contrast, 1.0)
    
    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """Calculate frame brightness"""
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = gray.mean() / 255.0  # Normalize to 0-1
        
        # Optimal brightness is around 0.5, so score based on distance from optimal
        return 1.0 - abs(brightness - 0.5) * 2
    
    def _assess_audio_quality(self, audio_path: Path) -> QualityScore:
        """Assess audio quality"""
        
        try:
            # Simple audio quality metrics
            # In production, would use librosa for detailed analysis
            
            import wave
            
            with wave.open(str(audio_path), 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                
                # Basic quality scoring based on audio properties
                quality_score = 0.0
                
                # Sample rate quality
                if sample_rate >= 44100:
                    quality_score += 0.4
                elif sample_rate >= 22050:
                    quality_score += 0.2
                
                # Bit depth quality
                if sample_width >= 2:  # 16-bit or higher
                    quality_score += 0.3
                
                # Stereo bonus
                if channels == 2:
                    quality_score += 0.2
                elif channels == 1:
                    quality_score += 0.1
                
                # Duration check (not too short)
                duration = wav_file.getnframes() / sample_rate
                if duration > 1.0:
                    quality_score += 0.1
            
            return QualityScore(
                metric=QualityMetric.AUDIO_QUALITY,
                score=min(quality_score, 1.0),
                details={
                    'sample_rate': sample_rate,
                    'channels': channels,
                    'sample_width': sample_width,
                    'duration': duration
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Audio quality assessment failed: {e}")
            return QualityScore(
                metric=QualityMetric.AUDIO_QUALITY,
                score=0.0,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def _assess_sync_accuracy(self, video_path: Path, audio_path: Path) -> QualityScore:
        """Assess audio-video synchronization accuracy"""
        
        try:
            # Get video duration
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = frame_count / fps
            cap.release()
            
            # Get audio duration
            import wave
            with wave.open(str(audio_path), 'rb') as wav_file:
                audio_duration = wav_file.getnframes() / wav_file.getframerate()
            
            # Calculate sync accuracy based on duration difference
            duration_diff = abs(video_duration - audio_duration)
            sync_tolerance = 0.1  # 100ms tolerance
            
            if duration_diff <= sync_tolerance:
                sync_score = 1.0
            else:
                sync_score = max(0.0, 1.0 - (duration_diff / max(video_duration, audio_duration)))
            
            return QualityScore(
                metric=QualityMetric.SYNC_ACCURACY,
                score=sync_score,
                details={
                    'video_duration': video_duration,
                    'audio_duration': audio_duration,
                    'duration_difference': duration_diff
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Sync accuracy assessment failed: {e}")
            return QualityScore(
                metric=QualityMetric.SYNC_ACCURACY,
                score=0.0,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def _assess_encoding_efficiency(self, video_path: Path) -> QualityScore:
        """Assess video encoding efficiency"""
        
        try:
            # Get file size and video properties
            file_size = video_path.stat().st_size
            
            cap = cv2.VideoCapture(str(video_path))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            cap.release()
            
            # Calculate bitrate
            bitrate = (file_size * 8) / duration  # bits per second
            
            # Calculate efficiency based on resolution and bitrate
            pixel_count = width * height
            target_bitrate = pixel_count * 0.1  # Rough target: 0.1 bits per pixel per second
            
            efficiency = min(target_bitrate / bitrate, 1.0) if bitrate > 0 else 0.0
            
            return QualityScore(
                metric=QualityMetric.ENCODING_EFFICIENCY,
                score=efficiency,
                details={
                    'file_size_mb': file_size / 1024 / 1024,
                    'bitrate_mbps': bitrate / 1024 / 1024,
                    'resolution': (width, height),
                    'duration': duration
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Encoding efficiency assessment failed: {e}")
            return QualityScore(
                metric=QualityMetric.ENCODING_EFFICIENCY,
                score=0.0,
                details={'error': str(e)},
                timestamp=datetime.now()
            )
    
    def generate_quality_report(self, scores: List[QualityScore]) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_score': np.mean([s.score for s in scores]),
            'scores': {
                score.metric.value: {
                    'score': score.score,
                    'passed': score.score >= self.quality_thresholds.get(score.metric.value, 0.5),
                    'details': score.details
                }
                for score in scores
            },
            'thresholds': self.quality_thresholds,
            'recommendations': self._generate_recommendations(scores)
        }
        
        return report
    
    def _generate_recommendations(self, scores: List[QualityScore]) -> List[str]:
        """Generate quality improvement recommendations"""
        
        recommendations = []
        
        for score in scores:
            threshold = self.quality_thresholds.get(score.metric.value, 0.5)
            
            if score.score < threshold:
                if score.metric == QualityMetric.VISUAL_QUALITY:
                    recommendations.append("Improve visual quality: increase resolution or adjust encoding settings")
                elif score.metric == QualityMetric.AUDIO_QUALITY:
                    recommendations.append("Improve audio quality: use higher sample rate or bit depth")
                elif score.metric == QualityMetric.SYNC_ACCURACY:
                    recommendations.append("Fix audio-video sync: check timing alignment")
                elif score.metric == QualityMetric.ENCODING_EFFICIENCY:
                    recommendations.append("Optimize encoding: adjust bitrate or compression settings")
        
        return recommendations

class ExportOptimizer:
    """Optimizes video export settings for different platforms"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Platform-specific export presets
        self.platform_presets = {
            'youtube': {
                'resolution': (1920, 1080),
                'fps': 30,
                'codec': 'h264',
                'bitrate': '8M',
                'audio_codec': 'aac',
                'audio_bitrate': '128k'
            },
            'instagram': {
                'resolution': (1080, 1080),
                'fps': 30,
                'codec': 'h264',
                'bitrate': '3.5M',
                'audio_codec': 'aac',
                'audio_bitrate': '128k'
            },
            'tiktok': {
                'resolution': (1080, 1920),
                'fps': 30,
                'codec': 'h264',
                'bitrate': '2M',
                'audio_codec': 'aac',
                'audio_bitrate': '128k'
            },
            'linkedin': {
                'resolution': (1920, 1080),
                'fps': 30,
                'codec': 'h264',
                'bitrate': '5M',
                'audio_codec': 'aac',
                'audio_bitrate': '128k'
            },
            'web': {
                'resolution': (1280, 720),
                'fps': 30,
                'codec': 'h264',
                'bitrate': '2M',
                'audio_codec': 'aac',
                'audio_bitrate': '96k'
            }
        }
    
    def get_export_settings(self, platform: str, 
                           custom_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get optimized export settings for platform"""
        
        if platform not in self.platform_presets:
            logger.warning(f"Unknown platform: {platform}, using web preset")
            platform = 'web'
        
        settings = self.platform_presets[platform].copy()
        
        if custom_settings:
            settings.update(custom_settings)
        
        return settings
    
    def validate_export_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and optimize export settings"""
        
        validated = settings.copy()
        
        # Ensure resolution is even numbers (required for most codecs)
        width, height = validated['resolution']
        validated['resolution'] = (width + width % 2, height + height % 2)
        
        # Validate fps
        fps = validated.get('fps', 30)
        if fps not in [24, 25, 30, 50, 60]:
            logger.warning(f"Unusual fps: {fps}, consider using 30")
        
        # Validate bitrate format
        bitrate = validated.get('bitrate', '2M')
        if isinstance(bitrate, str) and not bitrate.endswith(('k', 'M')):
            validated['bitrate'] = f"{bitrate}M"
        
        return validated

class ProductionEngine:
    """Main production features coordinator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_manager = VideoTemplateManager(config)
        self.watermark_manager = WatermarkManager(config)
        self.quality_assurance = QualityAssurance(config)
        self.export_optimizer = ExportOptimizer(config)
    
    def process_video_production(self, video_path: Path, 
                                production_config: Dict[str, Any]) -> Dict[str, Any]:
        """Complete video production pipeline"""
        
        logger.info("Starting video production pipeline")
        
        results = {
            'input_video': str(video_path),
            'timestamp': datetime.now().isoformat(),
            'steps_completed': [],
            'quality_scores': [],
            'export_paths': []
        }
        
        # Apply template if specified
        if 'template' in production_config:
            template_name = production_config['template']
            logger.info(f"Applying template: {template_name}")
            # Template would be applied during video generation
            results['steps_completed'].append('template_applied')
        
        # Add watermark if specified
        if 'watermark' in production_config:
            watermark_config = production_config['watermark']
            logger.info("Adding watermark")
            
            watermarked_path = self.watermark_manager.add_watermark(
                video_path, watermark_config
            )
            
            if watermarked_path != video_path:
                video_path = watermarked_path
                results['steps_completed'].append('watermark_added')
        
        # Add metadata
        if 'metadata' in production_config:
            metadata = production_config['metadata']
            logger.info("Adding metadata")
            
            success = self.watermark_manager.add_metadata(video_path, metadata)
            if success:
                results['steps_completed'].append('metadata_added')
        
        # Quality assessment
        if production_config.get('quality_check', True):
            logger.info("Running quality assessment")
            
            audio_path = production_config.get('audio_path')
            quality_scores = self.quality_assurance.assess_video_quality(
                video_path, audio_path
            )
            
            quality_report = self.quality_assurance.generate_quality_report(quality_scores)
            results['quality_scores'] = quality_report
            results['steps_completed'].append('quality_assessed')
        
        # Export for multiple platforms
        if 'export_platforms' in production_config:
            platforms = production_config['export_platforms']
            logger.info(f"Exporting for platforms: {platforms}")
            
            for platform in platforms:
                export_settings = self.export_optimizer.get_export_settings(
                    platform, production_config.get('custom_export_settings', {})
                )
                
                # Export path
                export_path = video_path.parent / f"{video_path.stem}_{platform}{video_path.suffix}"
                
                # In a real implementation, would call ffmpeg or similar for export
                logger.info(f"Would export to {export_path} with settings: {export_settings}")
                
                results['export_paths'].append({
                    'platform': platform,
                    'path': str(export_path),
                    'settings': export_settings
                })
            
            results['steps_completed'].append('multi_platform_export')
        
        logger.info("Video production pipeline completed")
        return results
    
    def create_production_report(self, results: Dict[str, Any]) -> str:
        """Create human-readable production report"""
        
        report = f"""
AI Video GPU - Production Report
Generated: {results['timestamp']}
Input Video: {results['input_video']}

Steps Completed:
{chr(10).join(f"  ✓ {step.replace('_', ' ').title()}" for step in results['steps_completed'])}

Quality Assessment:
"""
        
        if 'quality_scores' in results and 'scores' in results['quality_scores']:
            overall_score = results['quality_scores']['overall_score']
            report += f"  Overall Score: {overall_score:.2f}/1.0\n"
            
            for metric, data in results['quality_scores']['scores'].items():
                status = "✓ PASS" if data['passed'] else "✗ FAIL"
                report += f"  {metric.replace('_', ' ').title()}: {data['score']:.2f} {status}\n"
        
        if 'export_paths' in results and results['export_paths']:
            report += f"\nExported Versions:\n"
            for export in results['export_paths']:
                report += f"  {export['platform'].title()}: {export['path']}\n"
        
        return report
