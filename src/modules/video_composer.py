"""
Video Composition and Rendering Engine
Final video assembly with effects and optimization
"""

import cv2
import numpy as np
from pathlib import Path
import subprocess
import tempfile
from typing import List, Dict, Optional, Union
from loguru import logger
import json

class VideoComposer:
    """
    Advanced video composition engine for final video assembly
    Supports HD/4K output, effects, and GPU-accelerated encoding
    """
    
    def __init__(self, config):
        self.config = config
        self.output_resolution = config.video.output_resolution
        self.fps = config.video.fps
        self.codec = config.video.codec
        self.bitrate = config.video.bitrate
    
    def create_final_video(
        self,
        video_frames: Union[str, List[np.ndarray]],
        audio_path: str,
        output_path: str = "output/final_video.mp4",
        effects: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Compose final video with all elements
        
        Args:
            video_frames: Path to video file or list of frame arrays
            audio_path: Path to final audio track
            output_path: Where to save the final video
            effects: List of video effects to apply
            metadata: Video metadata to embed
            
        Returns:
            Dictionary with composition results
        """
        logger.info("Starting final video composition...")
        
        try:
            # Load video frames
            frames = self._load_frames(video_frames)
            
            # Apply video effects
            if effects:
                frames = self._apply_effects(frames, effects)
            
            # Add overlays and graphics
            frames = self._add_overlays(frames)
            
            # Create temporary video file
            temp_video_path = self._create_temp_video(frames)
            
            # Combine with audio and encode final video
            final_video_path = self._encode_final_video(
                temp_video_path, 
                audio_path, 
                output_path,
                metadata
            )
            
            # Get video information
            video_info = self._get_video_info(final_video_path)
            
            # Cleanup temporary files
            Path(temp_video_path).unlink(missing_ok=True)
            
            logger.success(f"Video composition completed: {final_video_path}")
            
            return {
                'success': True,
                'output_path': final_video_path,
                'video_info': video_info,
                'frame_count': len(frames),
                'audio_duration': video_info.get('duration', 0)
            }
            
        except Exception as e:
            logger.error(f"Video composition failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_frames(self, video_source: Union[str, List[np.ndarray]]) -> List[np.ndarray]:
        """Load video frames from various sources"""
        if isinstance(video_source, str):
            # Load from video file
            logger.info(f"Loading frames from video file: {video_source}")
            
            cap = cv2.VideoCapture(video_source)
            frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize to target resolution
                frame = cv2.resize(frame, self.output_resolution)
                frames.append(frame)
            
            cap.release()
            logger.info(f"Loaded {len(frames)} frames from video file")
            
        elif isinstance(video_source, list):
            # Already a list of frames
            frames = []
            for frame in video_source:
                # Ensure correct resolution
                if frame.shape[:2][::-1] != self.output_resolution:
                    frame = cv2.resize(frame, self.output_resolution)
                frames.append(frame)
            
            logger.info(f"Processed {len(frames)} frame arrays")
        else:
            raise ValueError("Invalid video source type")
        
        return frames
    
    def _apply_effects(self, frames: List[np.ndarray], effects: List[Dict]) -> List[np.ndarray]:
        """Apply video effects to frames"""
        logger.info(f"Applying {len(effects)} video effects...")
        
        processed_frames = frames.copy()
        
        for effect in effects:
            effect_type = effect.get('type')
            params = effect.get('params', {})
            
            if effect_type == 'color_correction':
                processed_frames = self._apply_color_correction(processed_frames, params)
            elif effect_type == 'stabilization':
                processed_frames = self._apply_stabilization(processed_frames, params)
            elif effect_type == 'noise_reduction':
                processed_frames = self._apply_noise_reduction(processed_frames, params)
            elif effect_type == 'sharpening':
                processed_frames = self._apply_sharpening(processed_frames, params)
            elif effect_type == 'vignette':
                processed_frames = self._apply_vignette(processed_frames, params)
            else:
                logger.warning(f"Unknown effect type: {effect_type}")
        
        return processed_frames
    
    def _apply_color_correction(self, frames: List[np.ndarray], params: Dict) -> List[np.ndarray]:
        """Apply color correction to frames"""
        logger.info("Applying color correction...")
        
        brightness = params.get('brightness', 0)
        contrast = params.get('contrast', 1.0)
        saturation = params.get('saturation', 1.0)
        
        corrected_frames = []
        
        for frame in frames:
            # Convert to float for processing
            frame_float = frame.astype(np.float32) / 255.0
            
            # Apply brightness
            frame_float = frame_float + brightness / 100.0
            
            # Apply contrast
            frame_float = (frame_float - 0.5) * contrast + 0.5
            
            # Apply saturation (convert to HSV)
            if saturation != 1.0:
                hsv = cv2.cvtColor(frame_float, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] *= saturation
                frame_float = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # Clip and convert back to uint8
            frame_float = np.clip(frame_float, 0, 1)
            corrected_frame = (frame_float * 255).astype(np.uint8)
            corrected_frames.append(corrected_frame)
        
        return corrected_frames
    
    def _apply_stabilization(self, frames: List[np.ndarray], params: Dict) -> List[np.ndarray]:
        """Apply video stabilization"""
        logger.info("Applying video stabilization...")
        
        if len(frames) < 2:
            return frames
        
        stabilized_frames = [frames[0]]  # First frame as reference
        
        # Calculate transformations between consecutive frames
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Detect features
            corners = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30)
            
            if corners is not None and len(corners) > 10:
                # Track features
                next_corners, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, corners, None)
                
                # Filter good matches
                good_old = corners[status == 1]
                good_new = next_corners[status == 1]
                
                if len(good_old) > 10:
                    # Calculate transformation matrix
                    transform_matrix = cv2.estimateAffinePartial2D(good_old, good_new)[0]
                    
                    if transform_matrix is not None:
                        # Apply stabilization
                        h, w = frames[i].shape[:2]
                        stabilized_frame = cv2.warpAffine(frames[i], transform_matrix, (w, h))
                        stabilized_frames.append(stabilized_frame)
                        continue
            
            # If stabilization fails, use original frame
            stabilized_frames.append(frames[i])
        
        return stabilized_frames
    
    def _apply_noise_reduction(self, frames: List[np.ndarray], params: Dict) -> List[np.ndarray]:
        """Apply noise reduction to frames"""
        logger.info("Applying noise reduction...")
        
        strength = params.get('strength', 0.5)
        
        denoised_frames = []
        for frame in frames:
            # Apply bilateral filter for noise reduction
            denoised = cv2.bilateralFilter(frame, 9, 75 * strength, 75 * strength)
            denoised_frames.append(denoised)
        
        return denoised_frames
    
    def _apply_sharpening(self, frames: List[np.ndarray], params: Dict) -> List[np.ndarray]:
        """Apply sharpening filter to frames"""
        logger.info("Applying sharpening...")
        
        strength = params.get('strength', 0.5)
        
        # Sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1, 9 + strength * 8, -1],
                          [-1, -1, -1]])
        
        sharpened_frames = []
        for frame in frames:
            sharpened = cv2.filter2D(frame, -1, kernel)
            sharpened_frames.append(sharpened)
        
        return sharpened_frames
    
    def _apply_vignette(self, frames: List[np.ndarray], params: Dict) -> List[np.ndarray]:
        """Apply vignette effect to frames"""
        logger.info("Applying vignette effect...")
        
        intensity = params.get('intensity', 0.3)
        
        h, w = frames[0].shape[:2]
        
        # Create vignette mask
        X, Y = np.meshgrid(np.arange(w), np.arange(h))
        center_x, center_y = w // 2, h // 2
        
        # Calculate distance from center
        distance = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
        max_distance = np.sqrt(center_x**2 + center_y**2)
        
        # Create vignette mask
        vignette_mask = 1 - (distance / max_distance) * intensity
        vignette_mask = np.clip(vignette_mask, 0, 1)
        
        # Apply to all frames
        vignetted_frames = []
        for frame in frames:
            vignetted = frame.copy().astype(np.float32)
            for c in range(3):  # Apply to each color channel
                vignetted[:, :, c] *= vignette_mask
            vignetted = np.clip(vignetted, 0, 255).astype(np.uint8)
            vignetted_frames.append(vignetted)
        
        return vignetted_frames
    
    def _add_overlays(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """Add overlays and graphics to frames"""
        logger.info("Adding overlays and graphics...")
        
        # This could include:
        # - Watermarks
        # - Subtitles
        # - Logo overlays
        # - Progress bars
        # - Custom graphics
        
        # For now, we'll add a simple timestamp overlay as an example
        overlay_frames = []
        
        for i, frame in enumerate(frames):
            frame_with_overlay = frame.copy()
            
            # Add timestamp (optional)
            if hasattr(self.config, 'add_timestamp') and self.config.add_timestamp:
                timestamp = f"{i / self.fps:.2f}s"
                cv2.putText(
                    frame_with_overlay,
                    timestamp,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
            
            overlay_frames.append(frame_with_overlay)
        
        return overlay_frames
    
    def _create_temp_video(self, frames: List[np.ndarray]) -> str:
        """Create temporary video file from frames"""
        logger.info("Creating temporary video file...")
        
        temp_path = tempfile.mktemp(suffix='.mp4')
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        height, width = frames[0].shape[:2]
        out = cv2.VideoWriter(temp_path, fourcc, self.fps, (width, height))
        
        # Write frames
        for frame in frames:
            out.write(frame)
        
        out.release()
        logger.info(f"Temporary video created: {temp_path}")
        
        return temp_path
    
    def _encode_final_video(
        self, 
        video_path: str, 
        audio_path: str, 
        output_path: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Encode final video with audio using FFmpeg"""
        logger.info("Encoding final video with audio...")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build FFmpeg command
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-i', video_path,  # Video input
            '-i', audio_path,  # Audio input
            '-c:v', 'libx264',  # Video codec
            '-preset', 'medium',  # Encoding speed/quality tradeoff
            '-crf', '23',  # Quality (lower = better quality)
            '-c:a', 'aac',  # Audio codec
            '-b:a', '128k',  # Audio bitrate
            '-movflags', '+faststart',  # Web optimization
        ]
        
        # Add hardware acceleration if available (NVIDIA)
        try:
            subprocess.run(['nvidia-smi'], capture_output=True, check=True)
            cmd.extend(['-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda'])
            logger.info("Using NVIDIA GPU acceleration for encoding")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Using CPU encoding")
        
        # Add metadata if provided
        if metadata:
            for key, value in metadata.items():
                cmd.extend(['-metadata', f'{key}={value}'])
        
        cmd.append(str(output_path))
        
        try:
            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.success(f"Video encoding completed: {output_path}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg encoding failed: {e.stderr}")
            
            # Fallback: simple copy without re-encoding
            fallback_cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c', 'copy',
                str(output_path)
            ]
            
            try:
                subprocess.run(fallback_cmd, check=True, capture_output=True)
                logger.warning("Used fallback encoding method")
            except subprocess.CalledProcessError:
                # Final fallback: just copy the video file
                import shutil
                shutil.copy(video_path, output_path)
                logger.warning("Audio encoding failed, saved video without audio")
        
        return str(output_path)
    
    def _get_video_info(self, video_path: str) -> Dict:
        """Get information about the video file"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(result.stdout)
            
            # Extract relevant information
            video_info = {}
            
            if 'format' in info:
                video_info['duration'] = float(info['format'].get('duration', 0))
                video_info['size'] = int(info['format'].get('size', 0))
                video_info['bitrate'] = int(info['format'].get('bit_rate', 0))
            
            for stream in info.get('streams', []):
                if stream['codec_type'] == 'video':
                    video_info['width'] = stream.get('width')
                    video_info['height'] = stream.get('height')
                    video_info['fps'] = eval(stream.get('r_frame_rate', '0/1'))
                    video_info['codec'] = stream.get('codec_name')
                    break
            
            return video_info
            
        except Exception as e:
            logger.warning(f"Could not get video info: {e}")
            return {}
    
    def create_preview(
        self, 
        video_path: str, 
        preview_duration: float = 10.0,
        output_path: str = "output/preview.mp4"
    ) -> str:
        """Create a preview clip from the video"""
        logger.info(f"Creating {preview_duration}s preview...")
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-t', str(preview_duration),
            '-c', 'copy',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.success(f"Preview created: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Preview creation failed: {e}")
            return video_path
