"""
AI Video GPU - Video Quality Enhancement Module
Advanced video post-processing, upscaling, and enhancement using state-of-the-art AI models
"""

import cv2
import numpy as np
import torch
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from loguru import logger
import tempfile
import subprocess

try:
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False
    logger.warning("Real-ESRGAN not available. Video upscaling will be limited.")

try:
    import gfpgan
    GFPGAN_AVAILABLE = True
except ImportError:
    GFPGAN_AVAILABLE = False
    logger.warning("GFPGAN not available. Face enhancement will be limited.")

try:
    from rembg import remove, new_session
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    logger.warning("rembg not available. Background removal will be limited.")

class VideoEnhancer:
    """
    Advanced video enhancement using AI models for upscaling, face restoration, and quality improvement
    """
    
    def __init__(self, config):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize enhancement models
        self.upscaler = None
        self.face_enhancer = None
        self.background_remover = None
        
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize AI enhancement models"""
        
        # Initialize Real-ESRGAN for video upscaling
        if REALESRGAN_AVAILABLE:
            try:
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                self.upscaler = RealESRGANer(
                    scale=4,
                    model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                    model=model,
                    tile=0,
                    tile_pad=10,
                    pre_pad=0,
                    half=True if self.device.type == 'cuda' else False,
                    gpu_id=0 if self.device.type == 'cuda' else None
                )
                logger.info("✅ Real-ESRGAN upscaler initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Real-ESRGAN: {e}")
                
        # Initialize GFPGAN for face enhancement
        if GFPGAN_AVAILABLE:
            try:
                from gfpgan import GFPGANer
                self.face_enhancer = GFPGANer(
                    model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
                    upscale=2,
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=self.upscaler
                )
                logger.info("✅ GFPGAN face enhancer initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GFPGAN: {e}")
                
        # Initialize background remover
        if REMBG_AVAILABLE:
            try:
                self.background_remover = new_session('u2net')
                logger.info("✅ Background remover initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize background remover: {e}")
                
    def enhance_video(
        self,
        input_path: str,
        output_path: str,
        enhancement_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Enhance video quality using various AI models
        
        Args:
            input_path: Path to input video
            output_path: Path to save enhanced video
            enhancement_options: Dictionary of enhancement settings
            
        Returns:
            Dictionary with enhancement results
        """
        
        if enhancement_options is None:
            enhancement_options = {
                'upscale': True,
                'enhance_faces': True,
                'denoise': True,
                'stabilize': False,
                'color_correct': True
            }
            
        logger.info(f"Starting video enhancement: {input_path}")
        
        try:
            # Read video
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Determine output dimensions
            if enhancement_options.get('upscale', False) and self.upscaler:
                out_width, out_height = width * 4, height * 4
            else:
                out_width, out_height = width, height
                
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (out_width, out_height))
            
            frame_count = 0
            enhanced_frames = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Enhance frame
                enhanced_frame = self._enhance_frame(frame, enhancement_options)
                
                # Write enhanced frame
                out.write(enhanced_frame)
                
                frame_count += 1
                enhanced_frames += 1
                
                if frame_count % 30 == 0:  # Progress every 30 frames
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Enhancement progress: {progress:.1f}% ({frame_count}/{total_frames})")
                    
            cap.release()
            out.release()
            
            # Post-process with FFmpeg for better compression
            self._optimize_video_with_ffmpeg(output_path)
            
            result = {
                'success': True,
                'input_resolution': (width, height),
                'output_resolution': (out_width, out_height),
                'total_frames': total_frames,
                'enhanced_frames': enhanced_frames,
                'output_path': output_path
            }
            
            logger.success(f"Video enhancement completed: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Video enhancement failed: {e}")
            return {'success': False, 'error': str(e)}
            
    def _enhance_frame(self, frame: np.ndarray, options: Dict[str, Any]) -> np.ndarray:
        """Enhance a single frame using available AI models"""
        
        enhanced_frame = frame.copy()
        
        try:
            # Face enhancement
            if options.get('enhance_faces', False) and self.face_enhancer:
                _, _, enhanced_frame = self.face_enhancer.enhance(
                    enhanced_frame, 
                    has_aligned=False, 
                    only_center_face=False, 
                    paste_back=True
                )
                
            # Upscaling (if face enhancement didn't already upscale)
            elif options.get('upscale', False) and self.upscaler:
                enhanced_frame, _ = self.upscaler.enhance(enhanced_frame, outscale=4)
                
            # Denoising
            if options.get('denoise', False):
                enhanced_frame = cv2.bilateralFilter(enhanced_frame, 9, 75, 75)
                
            # Color correction
            if options.get('color_correct', False):
                enhanced_frame = self._apply_color_correction(enhanced_frame)
                
        except Exception as e:
            logger.warning(f"Frame enhancement error: {e}")
            # Return original frame if enhancement fails
            return frame
            
        return enhanced_frame
        
    def _apply_color_correction(self, frame: np.ndarray) -> np.ndarray:
        """Apply basic color correction to improve video quality"""
        
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels and convert back
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Adjust brightness and contrast slightly
        enhanced = cv2.convertScaleAbs(enhanced, alpha=1.1, beta=10)
        
        return enhanced
        
    def _optimize_video_with_ffmpeg(self, video_path: str):
        """Optimize video file size and quality using FFmpeg"""
        
        try:
            temp_path = video_path.replace('.mp4', '_temp.mp4')
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',
                temp_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Replace original with optimized version
            Path(video_path).unlink()
            Path(temp_path).rename(video_path)
            
            logger.info("Video optimized with FFmpeg")
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"FFmpeg optimization failed: {e}")
        except Exception as e:
            logger.warning(f"Video optimization error: {e}")
            
    def upscale_video(self, input_path: str, output_path: str, scale_factor: int = 4) -> Dict[str, Any]:
        """Dedicated video upscaling function"""
        
        return self.enhance_video(
            input_path,
            output_path,
            {'upscale': True, 'enhance_faces': False, 'denoise': False}
        )
        
    def enhance_faces_in_video(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Dedicated face enhancement function"""
        
        return self.enhance_video(
            input_path,
            output_path,
            {'upscale': False, 'enhance_faces': True, 'denoise': True}
        )
        
    def remove_background_from_video(
        self,
        input_path: str,
        output_path: str,
        background_color: Tuple[int, int, int] = (0, 255, 0)
    ) -> Dict[str, Any]:
        """Remove background from video and replace with solid color or transparency"""
        
        if not REMBG_AVAILABLE:
            return {'success': False, 'error': 'Background removal not available'}
            
        logger.info(f"Removing background from video: {input_path}")
        
        try:
            cap = cv2.VideoCapture(input_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Setup video writer with transparency support
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Remove background
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = remove(frame_rgb, session=self.background_remover)
                
                # Convert back to BGR and handle transparency
                result_bgr = cv2.cvtColor(result, cv2.COLOR_RGBA2BGR)
                
                # Replace transparent areas with background color
                alpha = result[:, :, 3]
                mask = alpha == 0
                result_bgr[mask] = background_color
                
                out.write(result_bgr)
                
                frame_count += 1
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    logger.info(f"Background removal progress: {progress:.1f}%")
                    
            cap.release()
            out.release()
            
            logger.success(f"Background removal completed: {output_path}")
            return {
                'success': True,
                'total_frames': total_frames,
                'output_path': output_path
            }
            
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            return {'success': False, 'error': str(e)}
            
    def get_enhancement_capabilities(self) -> Dict[str, bool]:
        """Get available enhancement capabilities"""
        
        return {
            'upscaling': self.upscaler is not None,
            'face_enhancement': self.face_enhancer is not None,
            'background_removal': self.background_remover is not None,
            'denoising': True,  # Always available with OpenCV
            'color_correction': True,  # Always available with OpenCV
            'video_optimization': True  # Always available with FFmpeg
        }
