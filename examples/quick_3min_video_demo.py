#!/usr/bin/env python3
"""
Quick 3-Minute Video Generation Demo
Optimized setup for generating short videos with GPU acceleration
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

try:
    from pipeline import VideoPipeline
    from config import load_config
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Quick3MinVideoDemo:
    """Demo class for generating 3-minute videos quickly"""
    
    def __init__(self):
        """Initialize the demo with optimized settings for 3-minute videos"""
        self.pipeline = None
        self.config = None
        self.setup_pipeline()
    
    def setup_pipeline(self):
        """Setup video generation pipeline with optimized settings"""
        try:
            if not PIPELINE_AVAILABLE:
                logger.error("❌ Pipeline not available. Please run setup first.")
                return False
            
            # Load configuration optimized for short videos
            self.config = load_config("config/default.yaml")
            
            # Override settings for 3-minute videos
            self.config.update({
                # Video settings optimized for 3-minute content
                'video': {
                    'duration': 180,  # 3 minutes in seconds
                    'fps': 24,        # Standard frame rate
                    'resolution': '720p',  # Good quality, faster processing
                    'quality': 'medium',   # Balance speed vs quality
                    'segments': 6,    # 30-second segments for easier processing
                },
                
                # Performance optimizations
                'performance': {
                    'batch_size': 4,
                    'gpu_memory_limit': 0.8,
                    'parallel_processing': True,
                    'low_vram_mode': False,
                },
                
                # Model settings for speed
                'models': {
                    'tts_model': 'xtts-v2',     # Fast, good quality
                    'lip_sync_model': 'wav2lip', # Standard model
                    'enhancement': False,        # Skip for speed
                }
            })
            
            # Initialize pipeline
            self.pipeline = VideoPipeline(self.config)
            
            logger.info("✅ Pipeline setup complete for 3-minute videos")
            logger.info(f"   Duration: {self.config['video']['duration']} seconds")
            logger.info(f"   Resolution: {self.config['video']['resolution']}")
            logger.info(f"   Quality: {self.config['video']['quality']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup pipeline: {e}")
            return False
    
    def estimate_processing_time(self) -> dict:
        """Estimate processing time for 3-minute video"""
        
        # Base estimates for different GPU types (in minutes)
        gpu_estimates = {
            'T4': 15,      # Google Colab, Kaggle
            'V100': 8,     # Google Colab Pro
            'A100': 5,     # Google Colab Pro+
            'P100': 12,    # Kaggle
            'RTX 3080': 6, # Local GPU
            'RTX 4090': 4, # High-end local GPU
        }
        
        # Detect current GPU
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                
                # Match GPU type
                current_gpu = 'T4'  # Default
                for gpu_type in gpu_estimates:
                    if gpu_type.lower() in gpu_name.lower():
                        current_gpu = gpu_type
                        break
                
                estimated_minutes = gpu_estimates[current_gpu]
                
                return {
                    'gpu_detected': gpu_name,
                    'gpu_type': current_gpu,
                    'estimated_time_minutes': estimated_minutes,
                    'estimated_completion': datetime.now() + timedelta(minutes=estimated_minutes)
                }
            else:
                return {
                    'gpu_detected': 'None',
                    'estimated_time_minutes': 60,  # CPU fallback (very slow)
                    'warning': 'No GPU detected - processing will be very slow'
                }
                
        except Exception as e:
            logger.warning(f"Could not detect GPU: {e}")
            return {
                'gpu_detected': 'Unknown',
                'estimated_time_minutes': 15,
                'estimated_completion': datetime.now() + timedelta(minutes=15)
            }
    
    def create_sample_script(self) -> str:
        """Create a sample 3-minute video script"""
        
        sample_script = """
[SCENE 1 - 30 seconds]
Welcome to our AI Video demonstration! Today we'll explore the fascinating world of artificial intelligence and video generation.

[SCENE 2 - 30 seconds] 
AI technology has revolutionized how we create content. With just a few clicks, we can generate professional-quality videos.

[SCENE 3 - 30 seconds]
Voice cloning allows us to create natural-sounding speech in any voice. The technology analyzes speech patterns and recreates them digitally.

[SCENE 4 - 30 seconds]
Lip synchronization ensures that the speaker's mouth movements match the audio perfectly, creating realistic talking videos.

[SCENE 5 - 30 seconds]
Image processing and enhancement make every frame look professional. AI can upscale, enhance, and optimize video quality automatically.

[SCENE 6 - 30 seconds]
Thank you for watching this AI-generated video! The future of content creation is here, and it's more accessible than ever before.
"""
        
        # Save script to file
        script_path = Path("sample_3min_script.txt")
        with open(script_path, 'w') as f:
            f.write(sample_script.strip())
        
        logger.info(f"✅ Sample script created: {script_path}")
        return str(script_path)
    
    def generate_quick_video(
        self,
        script_text: str = None,
        voice_sample: str = None,
        background_image: str = None
    ) -> dict:
        """Generate a 3-minute video quickly"""
        
        if not self.pipeline:
            return {'success': False, 'error': 'Pipeline not initialized'}
        
        start_time = datetime.now()
        
        # Use sample script if none provided
        if not script_text:
            script_path = self.create_sample_script()
            with open(script_path, 'r') as f:
                script_text = f.read()
        
        logger.info("🎬 Starting 3-minute video generation...")
        
        # Estimate completion time
        time_estimate = self.estimate_processing_time()
        logger.info(f"⏱️  Estimated completion: {time_estimate['estimated_time_minutes']} minutes")
        
        try:
            # Generate video with optimized settings
            result = self.pipeline.generate_video(
                script=script_text,
                voice_sample=voice_sample,
                background_image=background_image,
                output_name=f"quick_3min_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() / 60  # in minutes
            
            if result.get('success'):
                logger.info(f"✅ Video generation completed!")
                logger.info(f"   Output: {result['output_path']}")
                logger.info(f"   Duration: {duration:.1f} minutes")
                logger.info(f"   File size: {self._get_file_size(result['output_path'])}")
                
                return {
                    'success': True,
                    'output_path': result['output_path'],
                    'processing_time_minutes': duration,
                    'file_size': self._get_file_size(result['output_path']),
                    'url': result.get('url')  # If uploaded to cloud
                }
            else:
                logger.error(f"❌ Video generation failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error'),
                    'processing_time_minutes': duration
                }
                
        except Exception as e:
            logger.error(f"❌ Video generation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_minutes': (datetime.now() - start_time).total_seconds() / 60
            }
    
    def _get_file_size(self, filepath: str) -> str:
        """Get human-readable file size"""
        try:
            size_bytes = Path(filepath).stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            return f"{size_mb:.1f} MB"
        except:
            return "Unknown"
    
    def demo_workflow(self):
        """Run complete demo workflow for 3-minute video"""
        
        logger.info("🚀 Quick 3-Minute Video Demo")
        logger.info("=" * 50)
        
        # Step 1: Check system
        time_estimate = self.estimate_processing_time()
        logger.info(f"🔍 System Check:")
        logger.info(f"   GPU: {time_estimate['gpu_detected']}")
        logger.info(f"   Estimated time: {time_estimate['estimated_time_minutes']} minutes")
        
        # Step 2: Generate video
        logger.info("\n🎬 Generating 3-minute video...")
        result = self.generate_quick_video()
        
        # Step 3: Results
        if result['success']:
            logger.info("\n🎉 SUCCESS! Your 3-minute video is ready!")
            logger.info(f"📁 File: {result['output_path']}")
            logger.info(f"⏱️  Processing time: {result['processing_time_minutes']:.1f} minutes")
            logger.info(f"📏 File size: {result['file_size']}")
            
            if result.get('url'):
                logger.info(f"🌐 Public URL: {result['url']}")
        else:
            logger.error(f"\n❌ Video generation failed: {result.get('error')}")
        
        return result


def main():
    """Main function"""
    print("🎯 AI Video GPU - Quick 3-Minute Video Demo")
    print("=" * 55)
    print("Optimized for fast generation of 3-minute videos")
    print()
    
    # Check if we're in a supported environment
    environments = []
    
    # Check for Google Colab
    try:
        import google.colab
        environments.append("Google Colab")
    except ImportError:
        pass
    
    # Check for Kaggle
    if os.path.exists('/kaggle'):
        environments.append("Kaggle")
    
    # Check for local GPU
    try:
        import torch
        if torch.cuda.is_available():
            environments.append("Local GPU")
    except ImportError:
        pass
    
    if environments:
        print(f"🔍 Detected environment: {', '.join(environments)}")
    else:
        print("⚠️  No GPU environment detected. Processing will be slow.")
    
    print()
    
    # Run demo
    demo = Quick3MinVideoDemo()
    
    if demo.pipeline:
        result = demo.demo_workflow()
        
        # Provide next steps
        print("\n🎯 Next Steps:")
        print("1. Download your video from the output path")
        print("2. Share using the public URL (if available)")
        print("3. Try different scripts or voice samples")
        print("4. Experiment with longer videos (up to 10 minutes)")
        
    else:
        print("❌ Setup failed. Please check the installation guide.")
        print("💡 Quick fixes:")
        print("   - Ensure GPU runtime is enabled")
        print("   - Run setup cells in the notebook first")
        print("   - Check system requirements")


if __name__ == "__main__":
    main()
