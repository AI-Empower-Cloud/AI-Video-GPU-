"""
AI Video GPU - Integration Examples
Demonstrates how to integrate with existing AI Video Generator repositories
"""

import os
import sys
from pathlib import Path
import json

# Add AI Video GPU to path
sys.path.insert(0, str(Path(__file__).parent))

from src.compatibility.repo_compatibility import RepoCompatibilityManager
from src.pipeline import AIVideoPipeline

def example_basic_integration():
    """
    Example 1: Basic integration with any existing repo
    This shows how to use AI Video GPU as a drop-in replacement
    """
    
    print("🔄 Example 1: Basic Integration")
    print("-" * 40)
    
    # Initialize compatibility manager
    compat_manager = RepoCompatibilityManager()
    
    # Create compatibility bridge
    bridge = compat_manager.create_compatibility_bridge()
    
    # Use the bridge functions (same interface as existing repos)
    generate_video = bridge['generate_video']
    clone_voice = bridge['clone_voice']
    sync_lips = bridge['sync_lips']
    
    # Example usage (commented out to avoid running)
    """
    # Generate a video - same interface as before but with GPU acceleration
    result = generate_video(
        script="Hello, this is a test of AI Video GPU!",
        avatar_image="path/to/avatar.jpg",
        voice_sample="path/to/voice.wav",
        output_path="output/test_video.mp4"
    )
    
    # Clone a voice
    audio_path = clone_voice(
        text="This is cloned speech",
        voice_sample="path/to/voice.wav"
    )
    
    # Sync lips
    synced_video = sync_lips(
        video_path="path/to/video.mp4",
        audio_path="path/to/audio.wav"
    )
    """
    
    print("✅ Basic integration functions available:")
    print(f"   📹 generate_video: {generate_video}")
    print(f"   🗣️  clone_voice: {clone_voice}")
    print(f"   👄 sync_lips: {sync_lips}")

def example_gradio_integration():
    """
    Example 2: Gradio interface integration
    Shows how to create a web interface compatible with Gradio-based repos
    """
    
    print("\n🌐 Example 2: Gradio Integration")
    print("-" * 40)
    
    try:
        from src.interfaces.gradio_interface import create_gradio_app
        
        # Create Gradio app
        app = create_gradio_app()
        
        print("✅ Gradio interface created successfully!")
        print("   To launch: app.launch()")
        print("   Features: Video generation, voice cloning, lip sync")
        
        # Show how to customize
        print("\n🔧 Customization example:")
        print("""
        from src.interfaces.gradio_interface import GradioVideoGenerator
        
        # Create custom generator
        generator = GradioVideoGenerator("config/custom.yaml")
        
        # Create specific interfaces
        video_interface = generator.create_interface()
        voice_interface = generator.create_voice_clone_interface()
        
        # Launch
        video_interface.launch()
        """)
        
    except ImportError:
        print("❌ Gradio not available. Install with: pip install gradio")

def example_fastapi_integration():
    """
    Example 3: FastAPI/REST API integration
    Shows how to create REST endpoints compatible with API-based repos
    """
    
    print("\n🚀 Example 3: FastAPI Integration")
    print("-" * 40)
    
    try:
        from src.api.app import create_app
        
        app = create_app()
        
        print("✅ FastAPI app created successfully!")
        print("   Available endpoints:")
        print("   📹 POST /generate/video")
        print("   🗣️  POST /voice/clone")
        print("   👄 POST /lipsync/sync")
        print("   📊 GET /health")
        print("   🔧 GET /models/list")
        
        print("\n🔧 Usage example:")
        print("""
        # Start server
        uvicorn src.api.app:create_app --reload --host 0.0.0.0 --port 8000
        
        # Or use CLI
        python main.py serve --port 8000
        
        # Test with curl
        curl -X POST "http://localhost:8000/generate/video" \\
             -F "script=Hello world" \\
             -F "avatar_image=@avatar.jpg"
        """)
        
    except ImportError as e:
        print(f"❌ FastAPI dependencies not available: {e}")

def example_existing_repo_migration():
    """
    Example 4: Migrating an existing repository
    Shows step-by-step migration process
    """
    
    print("\n🔄 Example 4: Repository Migration")
    print("-" * 40)
    
    migration_steps = [
        "1. Analyze existing repository",
        "2. Create integration script",
        "3. Update imports",
        "4. Test compatibility",
        "5. Optimize for GPU"
    ]
    
    for step in migration_steps:
        print(f"   {step}")
    
    print("\n📝 Migration script example:")
    print("""
    # Analyze existing repo
    python main.py integrate --repo-path /path/to/existing/repo --analyze-only
    
    # Create integration script
    python main.py integrate --repo-path /path/to/existing/repo --output integration.py
    
    # In your existing repo, replace:
    # OLD:
    from your_video_generator import generate_video, clone_voice
    
    # NEW:
    from integration import generate_video, clone_voice
    
    # Use same function calls - now with GPU acceleration!
    """)

def example_batch_processing():
    """
    Example 5: Batch processing for multiple videos
    Shows how to process multiple videos efficiently
    """
    
    print("\n📦 Example 5: Batch Processing")
    print("-" * 40)
    
    # Example batch configuration
    batch_config = {
        "videos": [
            {
                "script": "First video script",
                "avatar": "avatars/person1.jpg",
                "voice": "voices/voice1.wav",
                "output": "output/video1.mp4"
            },
            {
                "script": "Second video script", 
                "avatar": "avatars/person2.jpg",
                "voice": "voices/voice2.wav",
                "output": "output/video2.mp4"
            }
        ],
        "global_settings": {
            "quality": "high",
            "use_3d": False,
            "tts_backend": "xtts"
        }
    }
    
    print("✅ Batch configuration example:")
    print(json.dumps(batch_config, indent=2))
    
    print("\n🔧 CLI usage:")
    print("""
    # Save config to file
    echo '{}' > batch_config.json
    
    # Run batch processing
    python main.py batch --config batch_config.json
    
    # Or use API
    curl -X POST "http://localhost:8000/batch/process" \\
         -F "batch_config=@batch_config.json"
    """.format(json.dumps(batch_config)))

def example_custom_pipeline():
    """
    Example 6: Custom pipeline integration
    Shows how to create custom workflows
    """
    
    print("\n🛠️  Example 6: Custom Pipeline")
    print("-" * 40)
    
    print("✅ Custom pipeline example:")
    print("""
    from src.pipeline import AIVideoPipeline
    from src.modules.enhanced_tts_engine import EnhancedTTSEngine
    from src.modules.wav2lip_engine import Wav2LipEngine
    
    # Create custom pipeline
    class CustomVideoGenerator:
        def __init__(self):
            self.pipeline = AIVideoPipeline()
            
        def generate_with_effects(self, script, avatar, effects=None):
            # Custom processing with effects
            result = self.pipeline.generate_video(script, avatar)
            
            if effects:
                # Apply custom effects
                self.apply_effects(result['output_path'], effects)
            
            return result
            
        def apply_effects(self, video_path, effects):
            # Custom effect processing
            pass
    
    # Use custom generator
    generator = CustomVideoGenerator()
    result = generator.generate_with_effects(
        "Hello world",
        "avatar.jpg",
        effects=["blur", "color_grade"]
    )
    """)

def example_model_management():
    """
    Example 7: Model management and optimization
    Shows how to manage AI models efficiently
    """
    
    print("\n🧠 Example 7: Model Management")
    print("-" * 40)
    
    print("✅ Model management examples:")
    print("""
    # List available models
    python main.py list-models
    
    # Download specific model
    python main.py download-model --model xtts-v2
    
    # Test model performance
    python main.py test-model --model tortoise --sample "test text"
    
    # Benchmark different models
    python main.py benchmark --models xtts,tortoise,speecht5
    
    # Optimize for specific GPU
    python main.py calibrate --gpu-memory 8192
    """)
    
    print("\n🔧 API model management:")
    print("""
    # Get available models
    curl http://localhost:8000/models/list
    
    # Download model
    curl -X POST http://localhost:8000/models/download \\
         -F "model_name=xtts-v2"
    
    # Check model status
    curl http://localhost:8000/models/status/xtts-v2
    """)

def main():
    """Run all integration examples"""
    
    print("🎬 AI Video GPU - Integration Examples")
    print("=" * 50)
    print("This script demonstrates various ways to integrate")
    print("AI Video GPU with existing repositories.\n")
    
    # Run all examples
    example_basic_integration()
    example_gradio_integration()
    example_fastapi_integration()
    example_existing_repo_migration()
    example_batch_processing()
    example_custom_pipeline()
    example_model_management()
    
    print("\n" + "=" * 50)
    print("🚀 Ready to integrate AI Video GPU!")
    print("Choose the example that best fits your needs.")
    print("\n📚 For more information:")
    print("   - Documentation: README.md")
    print("   - CLI help: python main.py --help")
    print("   - API docs: http://localhost:8000/docs (when server running)")

if __name__ == "__main__":
    main()
