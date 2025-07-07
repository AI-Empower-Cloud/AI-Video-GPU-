"""
Enhanced Wav2Lip Integration
Professional lip synchronization with multiple model support
"""

import cv2
import torch
import numpy as np
from pathlib import Path
import subprocess
import tempfile
from typing import List, Union, Optional, Dict, Tuple
from loguru import logger
import face_recognition
import mediapipe as mp
from scipy.spatial import distance as dist

class Wav2LipEngine:
    """
    Enhanced Wav2Lip engine with professional lip synchronization
    Supports multiple face detection backends and quality settings
    """
    
    def __init__(self, config):
        self.config = config
        self.device = config.get_device()
        
        # Wav2Lip model paths
        self.wav2lip_model_path = Path("models/wav2lip_gan.pth")
        self.wav2lip_model = None
        
        # Face detection setup
        self.setup_face_detection()
        
        # Quality settings
        self.quality_settings = {
            'low': {'batch_size': 32, 'face_size': 96},
            'medium': {'batch_size': 16, 'face_size': 128},
            'high': {'batch_size': 8, 'face_size': 256},
            'ultra': {'batch_size': 4, 'face_size': 512}
        }
        
        self._download_wav2lip_model()
        self._load_wav2lip_model()
    
    def setup_face_detection(self):
        """Initialize face detection backends"""
        logger.info("Setting up face detection...")
        
        # MediaPipe face detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=self.config.lip_sync.face_detection_confidence
        )
        
        # MediaPipe face mesh for landmarks
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        logger.success("Face detection initialized")
    
    def _download_wav2lip_model(self):
        """Download Wav2Lip model if not present"""
        if not self.wav2lip_model_path.exists():
            logger.info("Downloading Wav2Lip model...")
            
            # Create models directory
            self.wav2lip_model_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download URL for Wav2Lip GAN model
            model_url = "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
            
            try:
                import urllib.request
                urllib.request.urlretrieve(model_url, str(self.wav2lip_model_path))
                logger.success("Wav2Lip model downloaded successfully")
            except Exception as e:
                logger.error(f"Failed to download Wav2Lip model: {e}")
                logger.info("Please download manually from: https://github.com/Rudrabha/Wav2Lip")
    
    def _load_wav2lip_model(self):
        """Load the Wav2Lip model"""
        if not self.wav2lip_model_path.exists():
            logger.warning("Wav2Lip model not found. Lip sync will use fallback method.")
            return
        
        try:
            logger.info("Loading Wav2Lip model...")
            
            # Import Wav2Lip modules (assuming they're available)
            # Note: This requires the Wav2Lip repository to be properly installed
            from models import Wav2Lip
            
            # Load model
            checkpoint = torch.load(str(self.wav2lip_model_path), map_location=self.device)
            self.wav2lip_model = Wav2Lip()
            self.wav2lip_model.load_state_dict(checkpoint['state_dict'])
            self.wav2lip_model = self.wav2lip_model.to(self.device)
            self.wav2lip_model.eval()
            
            logger.success("Wav2Lip model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Wav2Lip model: {e}")
            logger.warning("Using fallback lip sync method")
            self.wav2lip_model = None
    
    def sync_lips(
        self,
        video_path: str,
        audio_path: str,
        output_path: str = "output/lip_synced_video.mp4",
        quality: str = "high",
        face_rect: Optional[Tuple[int, int, int, int]] = None,
        smooth_factor: float = 0.8
    ) -> str:
        """
        Apply lip synchronization to video
        
        Args:
            video_path: Path to input video
            audio_path: Path to audio for synchronization
            output_path: Where to save lip-synced video
            quality: Quality setting (low, medium, high, ultra)
            face_rect: Optional face rectangle (x, y, w, h)
            smooth_factor: Smoothing factor for transitions
            
        Returns:
            Path to lip-synced video
        """
        logger.info(f"Starting lip synchronization with {quality} quality...")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.wav2lip_model is not None:
            return self._sync_with_wav2lip(
                video_path, audio_path, str(output_path), quality, face_rect, smooth_factor
            )
        else:
            logger.warning("Using fallback lip sync method")
            return self._sync_with_fallback(
                video_path, audio_path, str(output_path), smooth_factor
            )
    
    def _sync_with_wav2lip(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        quality: str,
        face_rect: Optional[Tuple[int, int, int, int]],
        smooth_factor: float
    ) -> str:
        """Perform lip sync using Wav2Lip model"""
        logger.info("Performing Wav2Lip synchronization...")
        
        # Use Wav2Lip inference script
        # This assumes you have the Wav2Lip repository set up
        cmd = [
            "python", "inference.py",
            "--checkpoint_path", str(self.wav2lip_model_path),
            "--face", video_path,
            "--audio", audio_path,
            "--outfile", output_path
        ]
        
        # Add quality settings
        settings = self.quality_settings.get(quality, self.quality_settings['high'])
        cmd.extend([
            "--static", "False",
            "--fps", str(self.config.video.fps),
            "--pads", "0", "10", "0", "0",  # Padding around detected face
            "--face_det_batch_size", str(settings['batch_size']),
            "--wav2lip_batch_size", str(settings['batch_size']),
            "--resize_factor", "1"
        ])
        
        try:
            # Run Wav2Lip inference
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True,
                cwd="models/Wav2Lip"  # Assuming Wav2Lip is in models directory
            )
            
            logger.success(f"Wav2Lip synchronization completed: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Wav2Lip failed: {e.stderr}")
            # Fallback to basic method
            return self._sync_with_fallback(video_path, audio_path, output_path, smooth_factor)
        except FileNotFoundError:
            logger.error("Wav2Lip inference script not found")
            return self._sync_with_fallback(video_path, audio_path, output_path, smooth_factor)
    
    def _sync_with_fallback(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        smooth_factor: float
    ) -> str:
        """Fallback lip sync using basic face manipulation"""
        logger.info("Using fallback lip synchronization...")
        
        # Load video
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Load audio for analysis
        import librosa
        audio, sr = librosa.load(audio_path, sr=22050)
        
        # Calculate audio features for mouth movement
        hop_length = int(sr / fps)
        rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
        
        # Normalize RMS for mouth opening
        rms_normalized = (rms - np.min(rms)) / (np.max(rms) - np.min(rms))
        
        # Process video frames
        temp_video = tempfile.mktemp(suffix='.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, fps, 
                             (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                              int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Get audio intensity for this frame
            audio_idx = min(frame_idx, len(rms_normalized) - 1)
            mouth_openness = rms_normalized[audio_idx]
            
            # Apply mouth manipulation
            processed_frame = self._manipulate_mouth(frame, mouth_openness, smooth_factor)
            out.write(processed_frame)
            
            frame_idx += 1
            
            if frame_idx % (fps * 5) == 0:
                logger.info(f"Processed {frame_idx}/{frame_count} frames")
        
        cap.release()
        out.release()
        
        # Combine with audio
        self._combine_video_audio(temp_video, audio_path, output_path)
        
        # Cleanup
        Path(temp_video).unlink()
        
        logger.success(f"Fallback lip sync completed: {output_path}")
        return output_path
    
    def _manipulate_mouth(self, frame: np.ndarray, mouth_openness: float, smooth_factor: float) -> np.ndarray:
        """Apply basic mouth manipulation based on audio intensity"""
        result_frame = frame.copy()
        
        # Detect face landmarks
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get mouth landmarks (indices for lips)
            mouth_indices = [61, 84, 17, 314, 405, 320, 308, 324, 318]
            
            height, width = frame.shape[:2]
            mouth_points = []
            
            for idx in mouth_indices:
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                mouth_points.append((x, y))
            
            if mouth_points:
                # Calculate mouth center
                mouth_center = np.mean(mouth_points, axis=0).astype(int)
                
                # Apply mouth opening effect
                mouth_scale = 1.0 + (mouth_openness * 0.3)  # Scale factor based on audio
                
                # Create mouth region mask
                mouth_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
                mouth_points_array = np.array(mouth_points, dtype=np.int32)
                cv2.fillPoly(mouth_mask, [mouth_points_array], 255)
                
                # Apply subtle scaling to mouth region
                M = cv2.getRotationMatrix2D(tuple(mouth_center), 0, mouth_scale)
                mouth_region = cv2.warpAffine(frame, M, (width, height))
                
                # Blend the modified mouth back
                mouth_region_masked = cv2.bitwise_and(mouth_region, mouth_region, mask=mouth_mask)
                frame_masked = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mouth_mask))
                
                result_frame = cv2.add(frame_masked, mouth_region_masked)
        
        return result_frame
    
    def _combine_video_audio(self, video_path: str, audio_path: str, output_path: str):
        """Combine video and audio using FFmpeg"""
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Video-audio combination failed: {e}")
            # Fallback: copy video file
            import shutil
            shutil.copy(video_path, output_path)
    
    def detect_best_face(self, video_path: str, max_frames: int = 30) -> Optional[Dict]:
        """
        Detect the best face in video for lip sync
        
        Returns:
            Dictionary with face information or None
        """
        logger.info("Detecting best face for lip sync...")
        
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames throughout the video
        frame_indices = np.linspace(0, frame_count - 1, min(max_frames, frame_count), dtype=int)
        
        best_face = None
        best_score = 0
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue
            
            # Detect faces using face_recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            
            for (top, right, bottom, left) in face_locations:
                # Calculate face quality score
                face_width = right - left
                face_height = bottom - top
                face_area = face_width * face_height
                
                # Prefer larger, more centered faces
                center_x = (left + right) / 2
                center_y = (top + bottom) / 2
                frame_center_x = frame.shape[1] / 2
                frame_center_y = frame.shape[0] / 2
                
                distance_from_center = np.sqrt(
                    (center_x - frame_center_x)**2 + (center_y - frame_center_y)**2
                )
                
                # Scoring: larger faces and closer to center get higher scores
                score = face_area / (1 + distance_from_center * 0.01)
                
                if score > best_score:
                    best_score = score
                    best_face = {
                        'bbox': (left, top, right, bottom),
                        'center': (center_x, center_y),
                        'area': face_area,
                        'score': score,
                        'frame_idx': frame_idx
                    }
        
        cap.release()
        
        if best_face:
            logger.success(f"Best face detected with score: {best_face['score']:.2f}")
        else:
            logger.warning("No suitable face detected")
        
        return best_face
    
    def preprocess_video_for_lipsync(
        self, 
        video_path: str, 
        output_path: str,
        target_face: Optional[Dict] = None
    ) -> str:
        """
        Preprocess video for optimal lip sync results
        
        Args:
            video_path: Input video path
            output_path: Output preprocessed video path
            target_face: Target face information from detect_best_face
            
        Returns:
            Path to preprocessed video
        """
        logger.info("Preprocessing video for lip sync...")
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Create output video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(
            output_path, fourcc, fps,
            (self.config.video.output_resolution[0], self.config.video.output_resolution[1])
        )
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize to target resolution
            frame = cv2.resize(frame, self.config.video.output_resolution)
            
            # Apply preprocessing
            # 1. Stabilize the frame
            frame = self._stabilize_frame(frame)
            
            # 2. Enhance face region
            if target_face:
                frame = self._enhance_face_region(frame, target_face)
            
            # 3. Color correction
            frame = self._apply_color_correction(frame)
            
            out.write(frame)
            frame_count += 1
            
            if frame_count % (fps * 10) == 0:
                logger.info(f"Preprocessed {frame_count} frames")
        
        cap.release()
        out.release()
        
        logger.success(f"Video preprocessing completed: {output_path}")
        return output_path
    
    def _stabilize_frame(self, frame: np.ndarray) -> np.ndarray:
        """Apply basic frame stabilization"""
        # Simple noise reduction
        return cv2.bilateralFilter(frame, 9, 75, 75)
    
    def _enhance_face_region(self, frame: np.ndarray, target_face: Dict) -> np.ndarray:
        """Enhance the face region for better lip sync"""
        # Apply sharpening to face region
        bbox = target_face['bbox']
        left, top, right, bottom = bbox
        
        # Extract face region
        face_region = frame[top:bottom, left:right]
        
        # Apply sharpening kernel
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened_face = cv2.filter2D(face_region, -1, kernel)
        
        # Replace face region
        enhanced_frame = frame.copy()
        enhanced_frame[top:bottom, left:right] = sharpened_face
        
        return enhanced_frame
    
    def _apply_color_correction(self, frame: np.ndarray) -> np.ndarray:
        """Apply basic color correction"""
        # Convert to LAB color space for better color correction
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge and convert back
        lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def benchmark_quality_settings(self, video_path: str, audio_path: str) -> Dict:
        """
        Benchmark different quality settings to find optimal performance
        
        Returns:
            Dictionary with benchmark results
        """
        logger.info("Benchmarking lip sync quality settings...")
        
        results = {}
        test_output_dir = Path("temp/benchmark")
        test_output_dir.mkdir(parents=True, exist_ok=True)
        
        for quality in ['low', 'medium', 'high']:
            logger.info(f"Testing {quality} quality...")
            
            start_time = time.time()
            
            try:
                output_path = test_output_dir / f"test_{quality}.mp4"
                self.sync_lips(
                    video_path=video_path,
                    audio_path=audio_path,
                    output_path=str(output_path),
                    quality=quality
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Get file size
                file_size = output_path.stat().st_size / (1024 * 1024)  # MB
                
                results[quality] = {
                    'processing_time': processing_time,
                    'file_size_mb': file_size,
                    'success': True
                }
                
                logger.info(f"{quality} quality: {processing_time:.2f}s, {file_size:.1f}MB")
                
            except Exception as e:
                logger.error(f"{quality} quality failed: {e}")
                results[quality] = {
                    'processing_time': 0,
                    'file_size_mb': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Cleanup test files
        import shutil
        shutil.rmtree(test_output_dir, ignore_errors=True)
        
        return results
