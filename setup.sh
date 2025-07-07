#!/bin/bash

# AI Video GPU Setup Script
# This script sets up the environment and installs dependencies

set -e  # Exit on any error

echo "🧠 AI Video GPU Setup Script"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or later and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Python $python_version detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

# Check if CUDA is available (optional)
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1
else
    echo "⚠️  No NVIDIA GPU detected. CPU-only mode will be used."
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is required but not installed."
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
    exit 1
fi
echo "✓ FFmpeg detected"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with CUDA support if available
echo "📦 Installing PyTorch..."
if command -v nvidia-smi &> /dev/null; then
    echo "Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "Installing PyTorch CPU-only version..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install other dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p config
mkdir -p models
mkdir -p output
mkdir -p temp
mkdir -p assets/avatars
mkdir -p assets/music
mkdir -p assets/voices

# Initialize configuration
echo "⚙️  Initializing configuration..."
python main.py init

# Test the installation
echo "🧪 Testing installation..."
python -c "
try:
    from src.pipeline import AIVideoPipeline
    from src.config import ConfigManager
    print('✓ Core modules imported successfully')
    
    # Test GPU availability
    import torch
    if torch.cuda.is_available():
        print(f'✓ CUDA available: {torch.cuda.get_device_name(0)}')
        print(f'✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB')
    else:
        print('⚠️  CUDA not available, using CPU')
    
    print('✓ Installation test passed!')
except Exception as e:
    print(f'❌ Installation test failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Quick start commands:"
echo "  source venv/bin/activate  # Activate virtual environment"
echo "  python main.py status     # Check system status"
echo "  python main.py generate \"Hello world!\"  # Generate first video"
echo ""
echo "For more information, see README.md"
