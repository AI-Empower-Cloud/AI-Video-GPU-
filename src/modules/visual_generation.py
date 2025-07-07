"""
Visual Generation Engine with Stable Diffusion and AnimateDiff
Creates AI-generated backgrounds, scenes, and animations
"""

import torch
import numpy as np
from pathlib import Path
import cv2
from typing import List, Dict, Optional, Union, Tuple
from loguru import logger
import tempfile
import json

class VisualGenerationEngine:
    """
    Advanced visual generation using Stable Diffusion and AnimateDiff
    Creates backgrounds, scenes, and animated sequences for videos
    """
    
    def __init__(self, config):
        self.config = config
        self.device = config.get_device()
        
        # Model components
        self.sd_pipeline = None
        self.animatediff_pipeline = None
        self.controlnet_pipeline = None
        
        # Generation settings
        self.default_size = (512, 512)
        self.video_size = tuple(config.video.output_resolution)
        
        self._initialize_pipelines()
    
    def _initialize_pipelines(self):
        """Initialize Stable Diffusion and AnimateDiff pipelines"""
        logger.info("Initializing visual generation pipelines...")
        
        try:
            # Initialize Stable Diffusion
            self._init_stable_diffusion()
            
            # Initialize AnimateDiff (if available)
            self._init_animatediff()
            
            # Initialize ControlNet (if available)
            self._init_controlnet()
            
            logger.success("Visual generation pipelines initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize visual pipelines: {e}")
            logger.warning("Visual generation will be limited")
    
    def _init_stable_diffusion(self):
        """Initialize Stable Diffusion pipeline"""
        try:
            from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
            
            model_id = "runwayml/stable-diffusion-v1-5"
            
            self.sd_pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            # Use DPM-Solver for faster generation
            self.sd_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                self.sd_pipeline.scheduler.config
            )
            
            self.sd_pipeline = self.sd_pipeline.to(self.device)
            
            # Enable memory efficient attention
            if hasattr(self.sd_pipeline, "enable_attention_slicing"):
                self.sd_pipeline.enable_attention_slicing()
            
            if hasattr(self.sd_pipeline, "enable_xformers_memory_efficient_attention"):
                try:
                    self.sd_pipeline.enable_xformers_memory_efficient_attention()
                except:
                    pass
            
            logger.success("Stable Diffusion pipeline loaded")
            
        except Exception as e:
            logger.error(f"Failed to load Stable Diffusion: {e}")
    
    def _init_animatediff(self):
        """Initialize AnimateDiff pipeline"""
        try:
            from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
            
            # Load motion adapter
            adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
            
            # Initialize pipeline
            self.animatediff_pipeline = AnimateDiffPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                motion_adapter=adapter,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
            
            self.animatediff_pipeline.scheduler = EulerDiscreteScheduler.from_config(
                self.animatediff_pipeline.scheduler.config
            )
            
            self.animatediff_pipeline = self.animatediff_pipeline.to(self.device)
            
            # Memory optimizations
            if hasattr(self.animatediff_pipeline, "enable_attention_slicing"):
                self.animatediff_pipeline.enable_attention_slicing()
            
            logger.success("AnimateDiff pipeline loaded")
            
        except Exception as e:
            logger.warning(f"AnimateDiff not available: {e}")
            self.animatediff_pipeline = None
    
    def _init_controlnet(self):
        """Initialize ControlNet pipeline"""
        try:
            from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
            from controlnet_aux import CannyDetector, OpenposeDetector
            
            # Load ControlNet model
            controlnet = ControlNetModel.from_pretrained(
                "lllyasviel/sd-controlnet-canny",
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32
            )
            
            self.controlnet_pipeline = StableDiffusionControlNetPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                controlnet=controlnet,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )
            
            self.controlnet_pipeline = self.controlnet_pipeline.to(self.device)
            
            # Initialize preprocessors
            self.canny_detector = CannyDetector()
            
            logger.success("ControlNet pipeline loaded")
            
        except Exception as e:
            logger.warning(f"ControlNet not available: {e}")
            self.controlnet_pipeline = None
    
    def generate_background(
        self,
        prompt: str,
        negative_prompt: str = "blurry, low quality, distorted",
        style: str = "photorealistic",
        duration_seconds: float = 10.0,
        animated: bool = False
    ) -> Union[str, List[str]]:
        """
        Generate background images or animations
        
        Args:
            prompt: Description of the background
            negative_prompt: What to avoid in generation
            style: Visual style (photorealistic, artistic, cartoon, etc.)
            duration_seconds: Duration for animated backgrounds
            animated: Whether to generate animated background
            
        Returns:
            Path to generated background or list of frame paths
        """
        logger.info(f"Generating {'animated' if animated else 'static'} background...")
        
        # Enhance prompt with style
        enhanced_prompt = self._enhance_prompt_with_style(prompt, style)
        
        if animated and self.animatediff_pipeline:
            return self._generate_animated_background(
                enhanced_prompt, negative_prompt, duration_seconds
            )
        else:
            return self._generate_static_background(
                enhanced_prompt, negative_prompt
            )
    
    def _enhance_prompt_with_style(self, prompt: str, style: str) -> str:
        """Enhance prompt with style-specific keywords"""
        style_enhancements = {
            "photorealistic": "photorealistic, high detail, 8k, professional photography",
            "artistic": "artistic, painting style, beautiful colors, masterpiece",
            "cartoon": "cartoon style, animated, colorful, clean lines",
            "cinematic": "cinematic lighting, dramatic, film grain, professional",
            "fantasy": "fantasy art, magical, ethereal, detailed",
            "minimalist": "minimalist, clean, simple, elegant design",
            "cyberpunk": "cyberpunk, neon lights, futuristic, high tech",
            "nature": "natural lighting, organic, realistic textures"
        }
        
        enhancement = style_enhancements.get(style, "high quality, detailed")
        return f"{prompt}, {enhancement}"
    
    def _generate_static_background(
        self, 
        prompt: str, 
        negative_prompt: str
    ) -> str:
        """Generate a static background image"""
        if not self.sd_pipeline:
            return self._create_fallback_background()
        
        try:
            logger.info("Generating static background with Stable Diffusion...")
            
            # Generate image
            image = self.sd_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=self.video_size[1],
                width=self.video_size[0],
                num_inference_steps=20,
                guidance_scale=7.5,
                generator=torch.Generator(device=self.device).manual_seed(42)
            ).images[0]
            
            # Save image
            output_path = "temp/generated_background.png"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            
            logger.success(f"Static background generated: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Background generation failed: {e}")
            return self._create_fallback_background()
    
    def _generate_animated_background(
        self, 
        prompt: str, 
        negative_prompt: str, 
        duration_seconds: float
    ) -> List[str]:
        """Generate animated background using AnimateDiff"""
        if not self.animatediff_pipeline:
            return self._create_fallback_animated_background(duration_seconds)
        
        try:
            logger.info("Generating animated background with AnimateDiff...")
            
            # Calculate number of frames
            fps = self.config.video.fps
            num_frames = int(duration_seconds * fps)
            
            # AnimateDiff works with 16 frame chunks
            chunk_size = 16
            frame_paths = []
            
            for chunk_start in range(0, num_frames, chunk_size):
                chunk_frames = min(chunk_size, num_frames - chunk_start)
                
                # Generate video chunk
                video_frames = self.animatediff_pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_frames=chunk_frames,
                    height=self.video_size[1],
                    width=self.video_size[0],
                    num_inference_steps=15,
                    guidance_scale=7.5,
                    generator=torch.Generator(device=self.device).manual_seed(42 + chunk_start)
                ).frames[0]
                
                # Save frames
                for i, frame in enumerate(video_frames):
                    frame_path = f"temp/bg_frame_{chunk_start + i:06d}.png"
                    Path(frame_path).parent.mkdir(parents=True, exist_ok=True)
                    frame.save(frame_path)
                    frame_paths.append(frame_path)
                
                logger.info(f"Generated chunk {chunk_start // chunk_size + 1}")
            
            logger.success(f"Animated background generated: {len(frame_paths)} frames")
            return frame_paths
            
        except Exception as e:
            logger.error(f"Animated background generation failed: {e}")
            return self._create_fallback_animated_background(duration_seconds)
    
    def generate_scene_sequence(
        self,
        script_segments: List[str],
        visual_styles: List[str],
        transitions: List[str] = None
    ) -> List[Dict]:
        """
        Generate a sequence of scene backgrounds based on script segments
        
        Args:
            script_segments: List of script segments
            visual_styles: Corresponding visual styles for each segment
            transitions: Transition types between scenes
            
        Returns:
            List of scene information dictionaries
        """
        logger.info(f"Generating scene sequence for {len(script_segments)} segments...")
        
        scenes = []
        
        for i, (segment, style) in enumerate(zip(script_segments, visual_styles)):
            logger.info(f"Generating scene {i+1}/{len(script_segments)}")
            
            # Extract visual keywords from script
            scene_prompt = self._extract_visual_prompt_from_text(segment)
            
            # Generate background
            background_path = self.generate_background(
                prompt=scene_prompt,
                style=style,
                animated=False
            )
            
            # Determine transition
            transition = transitions[i] if transitions and i < len(transitions) else "fade"
            
            scene_info = {
                'index': i,
                'script_segment': segment,
                'scene_prompt': scene_prompt,
                'visual_style': style,
                'background_path': background_path,
                'transition': transition,
                'duration': len(segment.split()) / 150 * 60  # Estimate duration
            }
            
            scenes.append(scene_info)
        
        logger.success("Scene sequence generation completed")
        return scenes
    
    def _extract_visual_prompt_from_text(self, text: str) -> str:
        """Extract visual elements from text for scene generation"""
        # Keywords that suggest visual elements
        visual_keywords = {
            'location': ['office', 'home', 'park', 'beach', 'mountain', 'city', 'forest', 'studio'],
            'time': ['morning', 'afternoon', 'evening', 'night', 'sunset', 'sunrise'],
            'weather': ['sunny', 'cloudy', 'rainy', 'snowy', 'stormy'],
            'mood': ['peaceful', 'energetic', 'mysterious', 'bright', 'dark', 'warm', 'cool'],
            'objects': ['desk', 'computer', 'books', 'plants', 'window', 'door']
        }
        
        text_lower = text.lower()
        found_elements = []
        
        for category, keywords in visual_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_elements.append(keyword)
        
        if found_elements:
            prompt = ", ".join(found_elements[:5])  # Limit to 5 elements
        else:
            # Default professional background
            prompt = "professional office environment, clean, modern"
        
        return prompt
    
    def generate_character_variations(
        self,
        base_image_path: str,
        expressions: List[str],
        output_dir: str = "temp/character_variations"
    ) -> Dict[str, str]:
        """
        Generate character variations with different expressions using ControlNet
        
        Args:
            base_image_path: Path to base character image
            expressions: List of expressions to generate
            output_dir: Directory to save variations
            
        Returns:
            Dictionary mapping expressions to generated image paths
        """
        if not self.controlnet_pipeline:
            logger.warning("ControlNet not available, skipping character variations")
            return {}
        
        logger.info(f"Generating character variations for {len(expressions)} expressions...")
        
        # Load base image
        base_image = cv2.imread(base_image_path)
        base_image_rgb = cv2.cvtColor(base_image, cv2.COLOR_BGR2RGB)
        
        # Generate canny edge map
        canny_image = self.canny_detector(base_image_rgb)
        
        variations = {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for expression in expressions:
            try:
                prompt = f"portrait of a person with {expression} expression, high quality, detailed"
                
                # Generate variation
                generated_image = self.controlnet_pipeline(
                    prompt=prompt,
                    image=canny_image,
                    num_inference_steps=20,
                    guidance_scale=7.5,
                    controlnet_conditioning_scale=0.8
                ).images[0]
                
                # Save image
                variation_path = output_path / f"character_{expression}.png"
                generated_image.save(str(variation_path))
                
                variations[expression] = str(variation_path)
                logger.info(f"Generated {expression} variation")
                
            except Exception as e:
                logger.error(f"Failed to generate {expression} variation: {e}")
        
        logger.success(f"Character variations completed: {len(variations)} generated")
        return variations
    
    def create_video_from_images(
        self,
        image_paths: List[str],
        output_path: str,
        fps: int = None,
        transition_duration: float = 0.5
    ) -> str:
        """
        Create video from a sequence of images with transitions
        
        Args:
            image_paths: List of image file paths
            output_path: Output video path
            fps: Frames per second (uses config default if None)
            transition_duration: Duration of transitions between images
            
        Returns:
            Path to created video
        """
        logger.info(f"Creating video from {len(image_paths)} images...")
        
        if not fps:
            fps = self.config.video.fps
        
        # Load images
        images = []
        for img_path in image_paths:
            img = cv2.imread(img_path)
            if img is not None:
                # Resize to video resolution
                img = cv2.resize(img, self.video_size)
                images.append(img)
        
        if not images:
            raise ValueError("No valid images found")
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, self.video_size)
        
        transition_frames = int(transition_duration * fps)
        
        for i, image in enumerate(images):
            # Write main image for its duration
            image_duration_frames = fps * 3  # 3 seconds per image
            
            for _ in range(image_duration_frames):
                out.write(image)
            
            # Add transition to next image (except for last image)
            if i < len(images) - 1:
                next_image = images[i + 1]
                
                # Create fade transition
                for frame_idx in range(transition_frames):
                    alpha = frame_idx / transition_frames
                    blended = cv2.addWeighted(image, 1 - alpha, next_image, alpha, 0)
                    out.write(blended)
        
        out.release()
        
        logger.success(f"Video created from images: {output_path}")
        return output_path
    
    def _create_fallback_background(self) -> str:
        """Create a simple fallback background"""
        logger.info("Creating fallback background...")
        
        # Create gradient background
        background = np.zeros((self.video_size[1], self.video_size[0], 3), dtype=np.uint8)
        
        # Create vertical gradient from blue to light blue
        for y in range(self.video_size[1]):
            intensity = int(100 + 100 * (y / self.video_size[1]))
            background[y, :] = [intensity, intensity + 20, intensity + 50]
        
        # Save background
        output_path = "temp/fallback_background.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, background)
        
        return output_path
    
    def _create_fallback_animated_background(self, duration_seconds: float) -> List[str]:
        """Create simple animated fallback background"""
        logger.info("Creating fallback animated background...")
        
        fps = self.config.video.fps
        num_frames = int(duration_seconds * fps)
        frame_paths = []
        
        for frame_idx in range(num_frames):
            # Create animated gradient
            time_factor = frame_idx / fps
            
            background = np.zeros((self.video_size[1], self.video_size[0], 3), dtype=np.uint8)
            
            # Animated color shift
            for y in range(self.video_size[1]):
                base_intensity = int(100 + 50 * np.sin(time_factor + y * 0.01))
                background[y, :] = [
                    base_intensity,
                    base_intensity + 20,
                    base_intensity + 50 + int(20 * np.sin(time_factor * 2))
                ]
            
            # Save frame
            frame_path = f"temp/fallback_bg_frame_{frame_idx:06d}.png"
            Path(frame_path).parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(frame_path, background)
            frame_paths.append(frame_path)
        
        return frame_paths
    
    def get_generation_capabilities(self) -> Dict:
        """Get information about available generation capabilities"""
        return {
            'stable_diffusion': self.sd_pipeline is not None,
            'animatediff': self.animatediff_pipeline is not None,
            'controlnet': self.controlnet_pipeline is not None,
            'supported_styles': [
                'photorealistic', 'artistic', 'cartoon', 'cinematic',
                'fantasy', 'minimalist', 'cyberpunk', 'nature'
            ],
            'max_resolution': self.video_size,
            'device': str(self.device)
        }
