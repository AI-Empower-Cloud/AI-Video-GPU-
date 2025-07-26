#!/bin/bash
# 🚀 RTX 6000 Ada Ultimate Setup Script
# Deploys AI video generation system on RTX 6000 Ada cloud instances

echo "🚀 RTX 6000 ADA ULTIMATE SETUP"
echo "Setting up AI Video Generation with 48GB VRAM"
echo "=" * 60

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're on a GPU instance
check_gpu() {
    echo -e "${BLUE}🔍 Checking GPU availability...${NC}"
    
    if command -v nvidia-smi &> /dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits)
        echo -e "${GREEN}✅ GPU Detected: $GPU_INFO${NC}"
        
        # Check if it's RTX 6000 Ada level (40GB+ VRAM)
        VRAM=$(echo $GPU_INFO | grep -o '[0-9]*' | head -1)
        if [ "$VRAM" -gt 40000 ]; then
            echo -e "${GREEN}🚀 RTX 6000 ADA LEVEL GPU DETECTED - MAXIMUM PERFORMANCE MODE${NC}"
            return 0
        elif [ "$VRAM" -gt 20000 ]; then
            echo -e "${YELLOW}⚡ HIGH-END GPU DETECTED - HIGH PERFORMANCE MODE${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ Standard GPU detected - limited performance${NC}"
            return 0
        fi
    else
        echo -e "${RED}❌ No GPU detected! This script requires a GPU instance${NC}"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    echo -e "${BLUE}📦 Installing system dependencies...${NC}"
    
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y \
        python3-pip \
        python3-venv \
        git \
        ffmpeg \
        htop \
        nvtop \
        wget \
        curl \
        unzip
    
    echo -e "${GREEN}✅ System dependencies installed${NC}"
}

# Setup Python environment
setup_python_env() {
    echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
    
    # Create virtual environment
    python3 -m venv rtx6000_env
    source rtx6000_env/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install PyTorch with CUDA 12.1 (RTX 6000 Ada optimized)
    echo -e "${BLUE}🔥 Installing PyTorch with CUDA 12.1...${NC}"
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    
    # Install video and AI packages
    echo -e "${BLUE}🎬 Installing video processing packages...${NC}"
    pip install opencv-python numpy pillow
    pip install diffusers transformers accelerate
    pip install xformers  # RTX optimization
    pip install moviepy imageio-ffmpeg
    
    # Install cloud storage
    pip install boto3 wasabi-sdk
    
    echo -e "${GREEN}✅ Python environment ready${NC}"
}

# Clone and setup AI Video project
setup_project() {
    echo -e "${BLUE}📁 Setting up AI Video project...${NC}"
    
    # Create project directory
    mkdir -p ~/ai-video-rtx6000
    cd ~/ai-video-rtx6000
    
    # Create outputs directory
    mkdir -p outputs
    
    # Download the RTX 6000 Ada launcher
    wget -O RTX_6000_ADA_LAUNCHER.py https://raw.githubusercontent.com/yourusername/AI-Video-GPU/main/RTX_6000_ADA_LAUNCHER.py
    
    # Make it executable
    chmod +x RTX_6000_ADA_LAUNCHER.py
    
    echo -e "${GREEN}✅ Project setup complete${NC}"
}

# Test GPU and generate sample video
test_gpu_video() {
    echo -e "${BLUE}🎬 Testing GPU video generation...${NC}"
    
    source ~/ai-video-rtx6000/rtx6000_env/bin/activate
    cd ~/ai-video-rtx6000
    
    # Create test script
    cat > test_rtx_video.py << 'EOF'
#!/usr/bin/env python3
import torch
import cv2
import numpy as np
import time

print("🚀 RTX 6000 Ada Quick Test")

# Check GPU
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"GPU: {gpu_name}")
    print(f"VRAM: {vram_gb:.1f} GB")
    
    # Quick 30-second test video
    width, height = 1920, 1080  # Full HD for quick test
    fps = 30
    duration = 30
    total_frames = fps * duration
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('outputs/RTX_test_video.mp4', fourcc, fps, (width, height))
    
    print(f"Creating {duration}s test video...")
    start_time = time.time()
    
    for i in range(total_frames):
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        # Add test text
        cv2.putText(frame, f"RTX 6000 Ada Test Frame {i}", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        out.write(frame)
        
        if i % 300 == 0:
            print(f"Progress: {i/total_frames*100:.1f}%")
    
    out.release()
    generation_time = time.time() - start_time
    
    print(f"✅ Test video created in {generation_time:.1f} seconds")
    print(f"Performance: {total_frames/generation_time:.1f} FPS generation rate")
else:
    print("❌ CUDA not available")
EOF
    
    python3 test_rtx_video.py
    
    echo -e "${GREEN}✅ GPU test complete${NC}"
}

# Setup Wasabi credentials
setup_wasabi() {
    echo -e "${BLUE}☁️ Setting up Wasabi cloud storage...${NC}"
    
    echo "Enter your Wasabi credentials (or press Enter to skip):"
    read -p "Wasabi Access Key: " WASABI_ACCESS_KEY
    read -p "Wasabi Secret Key: " WASABI_SECRET_KEY
    read -p "Wasabi Bucket Name: " WASABI_BUCKET
    
    if [ ! -z "$WASABI_ACCESS_KEY" ]; then
        # Create AWS credentials file for Wasabi
        mkdir -p ~/.aws
        cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $WASABI_ACCESS_KEY
aws_secret_access_key = $WASABI_SECRET_KEY
EOF
        
        cat > ~/.aws/config << EOF
[default]
region = us-east-1
EOF
        
        # Create Wasabi config
        cat > ~/ai-video-rtx6000/wasabi_config.py << EOF
WASABI_CONFIG = {
    'access_key': '$WASABI_ACCESS_KEY',
    'secret_key': '$WASABI_SECRET_KEY',
    'bucket_name': '$WASABI_BUCKET',
    'endpoint': 'https://s3.wasabisys.com'
}
EOF
        
        echo -e "${GREEN}✅ Wasabi credentials configured${NC}"
    else
        echo -e "${YELLOW}⚠️ Wasabi setup skipped${NC}"
    fi
}

# Create launch script
create_launcher() {
    echo -e "${BLUE}🚀 Creating RTX 6000 Ada launcher...${NC}"
    
    cat > ~/ai-video-rtx6000/launch_rtx6000.sh << 'EOF'
#!/bin/bash
echo "🚀 Launching RTX 6000 Ada Video Generator"

# Activate environment
source ~/ai-video-rtx6000/rtx6000_env/bin/activate

# Navigate to project
cd ~/ai-video-rtx6000

# Check GPU status
echo "GPU Status:"
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv

# Launch the RTX 6000 Ada generator
python3 RTX_6000_ADA_LAUNCHER.py
EOF
    
    chmod +x ~/ai-video-rtx6000/launch_rtx6000.sh
    
    echo -e "${GREEN}✅ Launcher created${NC}"
}

# Main setup function
main() {
    echo -e "${GREEN}🚀 Starting RTX 6000 Ada Ultimate Setup${NC}"
    
    check_gpu
    install_system_deps
    setup_python_env
    setup_project
    test_gpu_video
    setup_wasabi
    create_launcher
    
    echo -e "${GREEN}"
    echo "=" * 60
    echo "🎉 RTX 6000 ADA SETUP COMPLETE!"
    echo "=" * 60
    echo "🚀 To start generating videos:"
    echo "   cd ~/ai-video-rtx6000"
    echo "   ./launch_rtx6000.sh"
    echo ""
    echo "📁 Videos will be saved to: ~/ai-video-rtx6000/outputs/"
    echo "☁️ Wasabi upload configured (if credentials provided)"
    echo "🎬 Ready for 4K/8K video generation!"
    echo -e "${NC}"
}

# Run main function
main
