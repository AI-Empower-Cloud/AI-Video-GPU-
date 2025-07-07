#!/bin/bash

# AI Video GPU - Codespace Integration Setup
# Automatic setup script for integrating with existing AI Video Generator repos in Codespace

set -e

echo "🚀 AI Video GPU - Codespace Integration Setup"
echo "=============================================="

# Check if we're in a Codespace
if [ -n "$CODESPACES" ]; then
    echo "✅ Running in GitHub Codespace"
    WORKSPACE_DIR="/workspaces"
else
    echo "ℹ️  Not in Codespace, using current directory"
    WORKSPACE_DIR="$(pwd)"
fi

# Function to detect existing AI video repos
detect_ai_video_repos() {
    echo "🔍 Scanning for existing AI Video Generator repositories..."
    
    # Common AI video repo patterns
    AI_REPO_PATTERNS=(
        "*video*generator*"
        "*ai*video*"
        "*wav2lip*"
        "*tortoise*"
        "*voice*clone*"
        "*lip*sync*"
        "*tts*"
    )
    
    FOUND_REPOS=()
    
    for pattern in "${AI_REPO_PATTERNS[@]}"; do
        for dir in ${WORKSPACE_DIR}/${pattern}/; do
            if [ -d "$dir" ] && [ "$dir" != "${WORKSPACE_DIR}/AI-Video-GPU-/" ]; then
                # Check if it contains Python files
                if find "$dir" -name "*.py" -type f | head -1 | grep -q .; then
                    FOUND_REPOS+=("$dir")
                    echo "  📦 Found: $(basename "$dir")"
                fi
            fi
        done
    done
    
    return ${#FOUND_REPOS[@]}
}

# Function to setup AI Video GPU
setup_ai_video_gpu() {
    echo "🔧 Setting up AI Video GPU..."
    
    # Install dependencies
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    # Create necessary directories
    mkdir -p models output temp config
    
    # Download basic models if needed
    echo "🧠 Setting up basic models..."
    python -c "
import torch
from transformers import AutoModel, AutoTokenizer
print('✅ PyTorch and Transformers ready')
"
    
    echo "✅ AI Video GPU setup complete!"
}

# Function to create integration for found repos
create_integrations() {
    echo "🔗 Creating integrations for found repositories..."
    
    for repo_dir in "${FOUND_REPOS[@]}"; do
        repo_name=$(basename "$repo_dir")
        echo "  🔄 Processing: $repo_name"
        
        # Create integration script for this repo
        python main.py integrate --repo-path "$repo_dir" --output "${repo_dir}/ai_video_gpu_integration.py"
        
        # Copy quick start script
        cat > "${repo_dir}/quick_start_ai_video_gpu.py" << 'EOF'
"""
AI Video GPU Quick Start
Replace your existing video generation with this GPU-accelerated version
"""

# Import AI Video GPU functions
from ai_video_gpu_integration import generate_video, clone_voice, sync_lips

def example_usage():
    """Example of how to use AI Video GPU in your existing workflow"""
    
    # Replace your existing generate_video calls with this:
    result = generate_video(
        script="Hello, this is AI Video GPU!",
        avatar_image="path/to/your/avatar.jpg",
        voice_sample="path/to/your/voice.wav",  # Optional: for voice cloning
        background_music="path/to/music.mp3",   # Optional: background music
        use_3d=False,                           # Enable for 3D avatars
        use_ai_backgrounds=True,                # Generate AI backgrounds
        quality="high"                          # low, medium, high, ultra
    )
    
    if result['success']:
        print(f"✅ Video generated: {result['output_path']}")
        print(f"⏱️  Generation time: {result['generation_time']:.2f}s")
    else:
        print(f"❌ Error: {result['error']}")

def voice_cloning_example():
    """Example of voice cloning"""
    
    audio_path = clone_voice(
        text="This is cloned speech with AI Video GPU",
        voice_sample="path/to/reference_voice.wav",
        backend="xtts"  # xtts, tortoise, or auto
    )
    print(f"🗣️  Voice cloned: {audio_path}")

def lip_sync_example():
    """Example of lip synchronization"""
    
    synced_video = sync_lips(
        video_path="path/to/video.mp4",
        audio_path="path/to/audio.wav",
        quality="high"
    )
    print(f"👄 Lip sync complete: {synced_video}")

if __name__ == "__main__":
    print("🚀 AI Video GPU Quick Start Examples")
    print("Replace your existing function calls with these GPU-accelerated versions!")
    
    # Uncomment to run examples:
    # example_usage()
    # voice_cloning_example()
    # lip_sync_example()
EOF
        
        echo "    ✅ Created integration for $repo_name"
        echo "    📝 Files created:"
        echo "       - ai_video_gpu_integration.py (main integration)"
        echo "       - quick_start_ai_video_gpu.py (usage examples)"
    done
}

# Function to create universal integration
create_universal_integration() {
    echo "🌐 Creating universal integration script..."
    
    cat > "${WORKSPACE_DIR}/universal_ai_video_gpu.py" << 'EOF'
"""
Universal AI Video GPU Integration
Works with any Python project in the workspace
"""

import sys
from pathlib import Path

# Add AI Video GPU to path
ai_video_gpu_path = None
for workspace_dir in ["/workspaces", "."]:
    potential_path = Path(workspace_dir) / "AI-Video-GPU-"
    if potential_path.exists():
        ai_video_gpu_path = potential_path
        break

if ai_video_gpu_path:
    sys.path.insert(0, str(ai_video_gpu_path))
    
    from src.pipeline import AIVideoPipeline
    from src.modules.enhanced_tts_engine import EnhancedTTSEngine
    from src.modules.wav2lip_engine import Wav2LipEngine
    from src.config import ConfigManager
    
    # Create global instances
    config = ConfigManager()
    pipeline = AIVideoPipeline()
    
    def generate_video(script, avatar_image=None, voice_sample=None, **kwargs):
        """Generate AI video with GPU acceleration"""
        return pipeline.generate_video(
            script=script,
            avatar_image=avatar_image,
            voice_sample=voice_sample,
            **kwargs
        )
    
    def clone_voice(text, voice_sample, backend="auto"):
        """Clone voice using advanced TTS"""
        tts_engine = EnhancedTTSEngine(config)
        return tts_engine.generate_speech(
            text=text,
            voice_sample=voice_sample,
            backend=backend
        )
    
    def sync_lips(video_path, audio_path, quality="high"):
        """Advanced lip synchronization"""
        lip_sync = Wav2LipEngine(config)
        return lip_sync.sync_lips(
            video_path=video_path,
            audio_path=audio_path,
            quality=quality
        )
    
    # Export functions
    __all__ = ["generate_video", "clone_voice", "sync_lips", "pipeline", "config"]
    
    print("✅ Universal AI Video GPU integration loaded!")
    print("🚀 Use generate_video(), clone_voice(), sync_lips() in any project")
    
else:
    print("❌ AI Video GPU not found in workspace")
    print("Please ensure AI-Video-GPU- directory exists")
EOF
    
    echo "✅ Universal integration created: ${WORKSPACE_DIR}/universal_ai_video_gpu.py"
}

# Function to create README for integrations
create_integration_readme() {
    cat > "${WORKSPACE_DIR}/AI_VIDEO_GPU_INTEGRATION_README.md" << 'EOF'
# AI Video GPU Integration Guide

This workspace has been set up with AI Video GPU integration for enhanced video generation with GPU acceleration.

## 🚀 Quick Start

### Option 1: Universal Integration (Works with any project)
```python
from universal_ai_video_gpu import generate_video, clone_voice, sync_lips

# Generate video with GPU acceleration
result = generate_video(
    script="Hello from AI Video GPU!",
    avatar_image="avatar.jpg",
    voice_sample="voice.wav"
)
```

### Option 2: Repository-Specific Integration
If you have existing AI video repositories, use their specific integration scripts:
- `ai_video_gpu_integration.py` - Main integration
- `quick_start_ai_video_gpu.py` - Usage examples

## 🛠️ Available Functions

### generate_video()
Generate complete AI videos with:
- Voice cloning from samples
- Lip synchronization
- Background music
- AI-generated backgrounds
- 3D avatar support

### clone_voice()
Clone any voice using:
- XTTS for real-time cloning
- Tortoise for high-quality cloning
- Multiple language support

### sync_lips()
Advanced lip synchronization:
- High-quality Wav2Lip integration
- Face detection and tracking
- Batch processing support

## 🔧 Configuration

Edit `config/default.yaml` to customize:
- GPU settings
- Model preferences
- Quality settings
- Output formats

## 📊 Performance

AI Video GPU provides:
- 🚀 GPU acceleration for all models
- ⚡ Faster generation times
- 🎯 Higher quality outputs
- 🔄 Batch processing capabilities

## 🆘 Support

- Documentation: `/workspaces/AI-Video-GPU-/README.md`
- CLI help: `python /workspaces/AI-Video-GPU-/main.py --help`
- Web interface: `python /workspaces/AI-Video-GPU-/main.py serve`

## 📝 Examples

Check `quick_start_ai_video_gpu.py` in each repository for specific examples.

Happy GPU-accelerated video generation! 🎬
EOF
    
    echo "📚 Integration README created: ${WORKSPACE_DIR}/AI_VIDEO_GPU_INTEGRATION_README.md"
}

# Main setup process
main() {
    echo "🏁 Starting AI Video GPU integration setup..."
    
    # Detect existing repos
    detect_ai_video_repos
    num_repos=$?
    
    if [ $num_repos -gt 0 ]; then
        echo "✅ Found $num_repos existing AI video repositories"
        
        # Setup AI Video GPU
        setup_ai_video_gpu
        
        # Create integrations for found repos
        create_integrations
        
    else
        echo "ℹ️  No existing AI video repositories detected"
        echo "   Setting up for general use..."
        
        # Setup AI Video GPU
        setup_ai_video_gpu
    fi
    
    # Always create universal integration
    create_universal_integration
    
    # Create documentation
    create_integration_readme
    
    echo ""
    echo "🎉 AI Video GPU Integration Setup Complete!"
    echo "================================================"
    echo ""
    echo "📁 What was created:"
    echo "   ✅ AI Video GPU installed and configured"
    echo "   ✅ Universal integration: universal_ai_video_gpu.py"
    echo "   ✅ Integration documentation: AI_VIDEO_GPU_INTEGRATION_README.md"
    
    if [ $num_repos -gt 0 ]; then
        echo "   ✅ Repository-specific integrations for $num_repos repos"
    fi
    
    echo ""
    echo "🚀 Quick Test:"
    echo "   python -c \"from universal_ai_video_gpu import generate_video; print('✅ Ready!')\""
    echo ""
    echo "📚 Read the integration guide:"
    echo "   cat AI_VIDEO_GPU_INTEGRATION_README.md"
    echo ""
    echo "🎬 Happy GPU-accelerated video generation!"
}

# Run main function
main "$@"
