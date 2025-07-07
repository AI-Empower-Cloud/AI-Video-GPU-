"""
AI Video GPU - Gradio Compatibility Module
Provides drop-in replacement for Gradio-based AI Video Generator interfaces
"""

import gradio as gr
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pipeline import AIVideoPipeline
from src.config import ConfigManager
from loguru import logger

class GradioVideoGenerator:
    """
    Gradio interface for AI Video GPU
    Compatible with common Gradio-based AI video generators
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.pipeline = AIVideoPipeline(config_path)
        self.temp_dir = tempfile.mkdtemp()
        
    def create_interface(self) -> gr.Interface:
        """Create Gradio interface"""
        
        def generate_video(
            script: str,
            avatar_image,
            voice_sample,
            background_music,
            background_prompt: Optional[str] = None,
            visual_style: str = "photorealistic",
            use_3d: bool = False,
            use_ai_backgrounds: bool = False,
            quality: str = "high",
            tts_backend: str = "auto"
        ) -> Tuple[str, str]:
            """Generate video with Gradio interface"""
            
            try:
                # Handle file inputs
                avatar_path = avatar_image.name if avatar_image else None
                voice_path = voice_sample.name if voice_sample else None
                music_path = background_music.name if background_music else None
                
                # Generate output path
                output_path = os.path.join(self.temp_dir, f"generated_video_{len(os.listdir(self.temp_dir))}.mp4")
                
                # Generate video
                result = self.pipeline.generate_video(
                    script=script,
                    avatar_image=avatar_path,
                    voice_sample=voice_path,
                    background_music=music_path,
                    background_prompt=background_prompt,
                    visual_style=visual_style,
                    output_path=output_path,
                    use_3d=use_3d,
                    use_ai_backgrounds=use_ai_backgrounds
                )
                
                if result['success']:
                    return result['output_path'], f"✅ Video generated successfully in {result['generation_time']:.2f}s"
                else:
                    return None, f"❌ Generation failed: {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                logger.error(f"Gradio generation error: {e}")
                return None, f"❌ Error: {str(e)}"
        
        # Create Gradio interface
        interface = gr.Interface(
            fn=generate_video,
            inputs=[
                gr.Textbox(
                    label="Script",
                    placeholder="Enter your video script here...",
                    lines=5
                ),
                gr.File(
                    label="Avatar Image",
                    file_types=["image"],
                    type="file"
                ),
                gr.File(
                    label="Voice Sample (optional)",
                    file_types=["audio"],
                    type="file"
                ),
                gr.File(
                    label="Background Music (optional)",
                    file_types=["audio"],
                    type="file"
                ),
                gr.Textbox(
                    label="AI Background Prompt (optional)",
                    placeholder="Describe the background scene...",
                    lines=2
                ),
                gr.Dropdown(
                    label="Visual Style",
                    choices=["photorealistic", "cartoon", "anime", "artistic"],
                    value="photorealistic"
                ),
                gr.Checkbox(label="Enable 3D Avatar"),
                gr.Checkbox(label="Generate AI Backgrounds"),
                gr.Dropdown(
                    label="Quality",
                    choices=["low", "medium", "high", "ultra"],
                    value="high"
                ),
                gr.Dropdown(
                    label="TTS Backend",
                    choices=["auto", "xtts", "tortoise", "speecht5"],
                    value="auto"
                )
            ],
            outputs=[
                gr.Video(label="Generated Video"),
                gr.Textbox(label="Status")
            ],
            title="🎬 AI Video GPU - Enhanced Video Generation",
            description="Generate high-quality AI videos with GPU acceleration, voice cloning, and lip sync",
            theme=gr.themes.Soft(),
            allow_flagging="never"
        )
        
        return interface
        
    def create_voice_clone_interface(self) -> gr.Interface:
        """Create standalone voice cloning interface"""
        
        def clone_voice(text: str, voice_sample, tts_backend: str = "auto"):
            """Clone voice with Gradio interface"""
            
            try:
                voice_path = voice_sample.name if voice_sample else None
                output_path = os.path.join(self.temp_dir, f"cloned_voice_{len(os.listdir(self.temp_dir))}.wav")
                
                audio_path = self.pipeline.tts_engine.generate_speech(
                    text=text,
                    voice_sample=voice_path,
                    backend=tts_backend,
                    output_path=output_path
                )
                
                return audio_path, "✅ Voice cloned successfully"
                
            except Exception as e:
                logger.error(f"Voice cloning error: {e}")
                return None, f"❌ Error: {str(e)}"
        
        interface = gr.Interface(
            fn=clone_voice,
            inputs=[
                gr.Textbox(
                    label="Text to Speak",
                    placeholder="Enter text to convert to speech...",
                    lines=3
                ),
                gr.File(
                    label="Voice Sample",
                    file_types=["audio"],
                    type="file"
                ),
                gr.Dropdown(
                    label="TTS Backend",
                    choices=["auto", "xtts", "tortoise", "speecht5"],
                    value="auto"
                )
            ],
            outputs=[
                gr.Audio(label="Cloned Voice"),
                gr.Textbox(label="Status")
            ],
            title="🗣️ AI Voice Cloning",
            description="Clone any voice with advanced AI models"
        )
        
        return interface
        
    def create_lip_sync_interface(self) -> gr.Interface:
        """Create standalone lip sync interface"""
        
        def sync_lips(video_file, audio_file, quality: str = "high"):
            """Lip sync with Gradio interface"""
            
            try:
                video_path = video_file.name if video_file else None
                audio_path = audio_file.name if audio_file else None
                output_path = os.path.join(self.temp_dir, f"synced_video_{len(os.listdir(self.temp_dir))}.mp4")
                
                synced_video = self.pipeline.lip_sync_engine.sync_lips(
                    video_path=video_path,
                    audio_path=audio_path,
                    output_path=output_path,
                    quality=quality
                )
                
                return synced_video, "✅ Lip sync completed successfully"
                
            except Exception as e:
                logger.error(f"Lip sync error: {e}")
                return None, f"❌ Error: {str(e)}"
        
        interface = gr.Interface(
            fn=sync_lips,
            inputs=[
                gr.File(
                    label="Video File",
                    file_types=["video"],
                    type="file"
                ),
                gr.File(
                    label="Audio File",
                    file_types=["audio"],
                    type="file"
                ),
                gr.Dropdown(
                    label="Quality",
                    choices=["low", "medium", "high", "ultra"],
                    value="high"
                )
            ],
            outputs=[
                gr.Video(label="Lip Synced Video"),
                gr.Textbox(label="Status")
            ],
            title="👄 AI Lip Sync",
            description="Synchronize lips with audio using advanced AI"
        )
        
        return interface
        
    def create_combined_interface(self) -> gr.TabbedInterface:
        """Create tabbed interface with all features"""
        
        video_interface = self.create_interface()
        voice_interface = self.create_voice_clone_interface()
        lip_sync_interface = self.create_lip_sync_interface()
        
        return gr.TabbedInterface(
            [video_interface, voice_interface, lip_sync_interface],
            ["🎬 Video Generation", "🗣️ Voice Cloning", "👄 Lip Sync"],
            title="AI Video GPU - Complete Toolkit"
        )

def create_gradio_app(config_path: Optional[str] = None) -> gr.TabbedInterface:
    """Create Gradio app for AI Video GPU"""
    generator = GradioVideoGenerator(config_path)
    return generator.create_combined_interface()

# For direct running
if __name__ == "__main__":
    app = create_gradio_app()
    app.launch(share=True, server_name="0.0.0.0")
