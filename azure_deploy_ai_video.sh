#!/bin/bash

# 🚀 Azure AI Video Platform - Complete Deployment Script
# Deploy GPU-based AI video generation platform on Azure

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration variables
RESOURCE_GROUP="ai-video-platform-rg"
LOCATION="eastus"  # Choose region with GPU availability
VM_NAME="ai-video-gpu-vm"
VM_SIZE="Standard_NC6"  # 1 GPU, cost-effective for testing
STORAGE_ACCOUNT="aivideostorage$(date +%s)"
CONTAINER_NAME="videos"
ADMIN_USERNAME="azureuser"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI is not installed. Please install it first."
        echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check if logged in
    if ! az account show &> /dev/null; then
        print_warning "Not logged into Azure. Please login:"
        az login
    fi
    
    print_success "Prerequisites check completed"
}

# Create resource group
create_resource_group() {
    print_status "Creating resource group: $RESOURCE_GROUP"
    
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
    
    print_success "Resource group created"
}

# Create storage account for videos and models
create_storage() {
    print_status "Creating storage account: $STORAGE_ACCOUNT"
    
    az storage account create \
        --name $STORAGE_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --kind StorageV2 \
        --access-tier Hot \
        --output table
    
    # Create container for videos
    print_status "Creating storage container: $CONTAINER_NAME"
    
    az storage container create \
        --name $CONTAINER_NAME \
        --account-name $STORAGE_ACCOUNT \
        --public-access blob \
        --output table
    
    print_success "Storage account and container created"
}

# Create network security group with required ports
create_network_security() {
    print_status "Creating network security group..."
    
    NSG_NAME="${VM_NAME}-nsg"
    
    az network nsg create \
        --resource-group $RESOURCE_GROUP \
        --name $NSG_NAME \
        --location $LOCATION \
        --output table
    
    # Allow SSH
    az network nsg rule create \
        --resource-group $RESOURCE_GROUP \
        --nsg-name $NSG_NAME \
        --name AllowSSH \
        --protocol tcp \
        --priority 1001 \
        --destination-port-range 22 \
        --access allow \
        --output table
    
    # Allow HTTP for web interface
    az network nsg rule create \
        --resource-group $RESOURCE_GROUP \
        --nsg-name $NSG_NAME \
        --name AllowHTTP \
        --protocol tcp \
        --priority 1002 \
        --destination-port-range 80 \
        --access allow \
        --output table
    
    # Allow HTTPS for web interface
    az network nsg rule create \
        --resource-group $RESOURCE_GROUP \
        --nsg-name $NSG_NAME \
        --name AllowHTTPS \
        --protocol tcp \
        --priority 1003 \
        --destination-port-range 443 \
        --access allow \
        --output table
    
    print_success "Network security group created with rules"
}

# Create GPU virtual machine
create_gpu_vm() {
    print_status "Creating GPU virtual machine: $VM_NAME"
    print_warning "This will use ~$1-3/hour of your Azure credits"
    
    # Generate SSH key if it doesn't exist
    if [ ! -f ~/.ssh/id_rsa ]; then
        print_status "Generating SSH key..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    fi
    
    az vm create \
        --resource-group $RESOURCE_GROUP \
        --name $VM_NAME \
        --image "Canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2:latest" \
        --size $VM_SIZE \
        --admin-username $ADMIN_USERNAME \
        --ssh-key-values ~/.ssh/id_rsa.pub \
        --nsg "${VM_NAME}-nsg" \
        --storage-sku Premium_LRS \
        --os-disk-size-gb 128 \
        --output table
    
    print_success "GPU virtual machine created"
}

# Install AI/ML dependencies on the VM
install_dependencies() {
    print_status "Installing AI/ML dependencies on VM..."
    
    # Get VM public IP
    VM_IP=$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)
    print_status "VM Public IP: $VM_IP"
    
    # Wait for VM to be ready
    print_status "Waiting for VM to be ready..."
    sleep 60
    
    # Create installation script
    cat > install_deps.sh << 'EOF'
#!/bin/bash
set -e

echo "🔧 Installing AI/ML dependencies..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Install NVIDIA drivers and CUDA (for GPU support)
sudo apt install -y nvidia-driver-470 nvidia-cuda-toolkit

# Install FFmpeg for video processing
sudo apt install -y ffmpeg

# Create Python virtual environment
python3 -m venv ~/ai_video_env
source ~/ai_video_env/bin/activate

# Install Python packages
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install transformers diffusers accelerate
pip install moviepy pillow opencv-python numpy pandas
pip install flask gunicorn
pip install azure-storage-blob azure-identity

# Create project directory
mkdir -p ~/ai_video_platform
cd ~/ai_video_platform

echo "✅ Dependencies installed successfully!"
echo "📁 Project directory: ~/ai_video_platform"
echo "🐍 Virtual environment: ~/ai_video_env"
echo ""
echo "To activate the environment, run:"
echo "source ~/ai_video_env/bin/activate"
EOF

    # Copy and execute installation script
    scp -o StrictHostKeyChecking=no install_deps.sh $ADMIN_USERNAME@$VM_IP:~/
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP 'chmod +x install_deps.sh && ./install_deps.sh'
    
    # Clean up local script
    rm install_deps.sh
    
    print_success "Dependencies installed on VM"
}

# Deploy AI video generation code
deploy_code() {
    print_status "Deploying AI video generation code..."
    
    VM_IP=$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)
    
    # Create a simple AI video generation script
    cat > ai_video_generator.py << 'EOF'
#!/usr/bin/env python3
"""
Simple AI Video Generator for Azure Deployment
Generates basic AI-powered videos using available models
"""

import os
import sys
import argparse
from datetime import datetime
import torch
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
import numpy as np

class SimpleAIVideoGenerator:
    def __init__(self, output_dir="./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if GPU is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
    
    def create_text_video(self, text, duration=10, resolution=(1280, 720)):
        """Create a simple text-based video"""
        print(f"Creating text video: '{text}'")
        
        # Create frames
        frames = []
        fps = 24
        total_frames = duration * fps
        
        for frame_num in range(total_frames):
            # Create image
            img = Image.new('RGB', resolution, color='darkblue')
            draw = ImageDraw.Draw(img)
            
            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # Calculate text position
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (resolution[0] - text_width) // 2
            y = (resolution[1] - text_height) // 2
            
            # Animate text color
            progress = frame_num / total_frames
            red = int(255 * (1 - progress))
            green = int(255 * progress)
            blue = 255
            color = (red, green, blue)
            
            # Draw text
            draw.text((x, y), text, font=font, fill=color)
            
            # Convert PIL to numpy array
            frame = np.array(img)
            frames.append(frame)
        
        return frames
    
    def create_demo_video(self, text="AI Empower GPU Cloud", duration=10):
        """Create a demo video"""
        print("🎬 Creating demo video...")
        
        # Generate frames
        frames = self.create_text_video(text, duration)
        
        # Create video using moviepy
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"ai_demo_{timestamp}.mp4")
        
        # Convert frames to video clip
        clip = mp.ImageSequenceClip(frames, fps=24)
        
        # Add audio (optional - create a simple tone)
        try:
            # Create a simple audio tone
            audio_duration = duration
            sample_rate = 44100
            frequency = 440  # A4 note
            t = np.linspace(0, audio_duration, int(sample_rate * audio_duration))
            audio_wave = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            # Create audio clip
            audio_clip = mp.AudioArrayClip(audio_wave, fps=sample_rate)
            
            # Combine video and audio
            final_clip = clip.set_audio(audio_clip)
        except:
            print("Audio generation failed, creating video without audio")
            final_clip = clip
        
        # Write video file
        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac' if hasattr(final_clip, 'audio') else None
        )
        
        print(f"✅ Demo video created: {output_path}")
        return output_path
    
    def get_system_info(self):
        """Get system information for monitoring"""
        info = {
            "device": self.device,
            "gpu_available": torch.cuda.is_available(),
            "python_version": sys.version,
            "pytorch_version": torch.__version__,
        }
        
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
        
        return info

def main():
    parser = argparse.ArgumentParser(description="AI Video Generator for Azure")
    parser.add_argument("--text", default="AI Empower GPU Cloud - Demo", help="Text to display in video")
    parser.add_argument("--duration", type=int, default=10, help="Video duration in seconds")
    parser.add_argument("--output", default="./output", help="Output directory")
    
    args = parser.parse_args()
    
    # Create generator
    generator = SimpleAIVideoGenerator(args.output)
    
    # Print system info
    print("🖥️  System Information:")
    info = generator.get_system_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    print()
    
    # Generate demo video
    video_path = generator.create_demo_video(args.text, args.duration)
    
    print(f"🎉 Video generation completed!")
    print(f"📁 Output: {video_path}")
    print(f"💰 Estimated Azure cost: ~$0.05-0.10 for this generation")

if __name__ == "__main__":
    main()
EOF

    # Create web interface
    cat > web_interface.py << 'EOF'
#!/usr/bin/env python3
"""
Simple Web Interface for AI Video Generation
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Empower GPU Cloud - Video Generator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            input, select { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #2980b9; }
            .status { margin: 20px 0; padding: 15px; border-radius: 5px; background: #e8f6f3; }
            .cost-info { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI Empower GPU Cloud - Video Generator</h1>
            <p>Generate AI-powered videos using Azure GPU infrastructure</p>
            
            <div class="cost-info">
                💰 <strong>Cost Estimate:</strong> ~$0.05-0.10 per video generation
            </div>
            
            <form id="videoForm">
                <div>
                    <label>Text to Display:</label><br>
                    <input type="text" id="text" value="AI Empower GPU Cloud - Demo" style="width: 400px;">
                </div>
                <div>
                    <label>Duration (seconds):</label><br>
                    <select id="duration">
                        <option value="5">5 seconds</option>
                        <option value="10" selected>10 seconds</option>
                        <option value="15">15 seconds</option>
                        <option value="30">30 seconds</option>
                    </select>
                </div>
                <div style="margin-top: 20px;">
                    <button type="submit">🎬 Generate Video</button>
                </div>
            </form>
            
            <div id="status" class="status" style="display: none;"></div>
            <div id="result" style="margin-top: 20px;"></div>
        </div>
        
        <script>
        document.getElementById('videoForm').onsubmit = function(e) {
            e.preventDefault();
            
            const text = document.getElementById('text').value;
            const duration = document.getElementById('duration').value;
            const status = document.getElementById('status');
            const result = document.getElementById('result');
            
            status.style.display = 'block';
            status.innerHTML = '🔄 Generating video... This may take a few minutes.';
            result.innerHTML = '';
            
            fetch('/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text, duration: parseInt(duration)})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    status.innerHTML = '✅ Video generated successfully!';
                    result.innerHTML = '<a href="/download/' + data.filename + '" download>📥 Download Video</a>';
                } else {
                    status.innerHTML = '❌ Error: ' + data.error;
                }
            })
            .catch(error => {
                status.innerHTML = '❌ Error: ' + error;
            });
        };
        </script>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate_video():
    try:
        data = request.json
        text = data.get('text', 'AI Empower GPU Cloud')
        duration = data.get('duration', 10)
        
        # Run video generation
        cmd = [
            'python3', 'ai_video_generator.py',
            '--text', text,
            '--duration', str(duration)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='/home/azureuser/ai_video_platform')
        
        if result.returncode == 0:
            # Find the generated video file
            output_dir = '/home/azureuser/ai_video_platform/output'
            files = os.listdir(output_dir)
            video_files = [f for f in files if f.endswith('.mp4')]
            
            if video_files:
                latest_video = max(video_files, key=lambda f: os.path.getctime(os.path.join(output_dir, f)))
                return jsonify({'success': True, 'filename': latest_video})
        
        return jsonify({'success': False, 'error': result.stderr or 'Generation failed'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def download_file(filename):
    file_path = f'/home/azureuser/ai_video_platform/output/{filename}'
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/status')
def status():
    try:
        # Get system information
        import torch
        info = {
            "status": "running",
            "gpu_available": torch.cuda.is_available(),
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "timestamp": datetime.now().isoformat()
        }
        
        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
        
        return jsonify(info)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
EOF

    # Copy files to VM
    scp -o StrictHostKeyChecking=no ai_video_generator.py $ADMIN_USERNAME@$VM_IP:~/ai_video_platform/
    scp -o StrictHostKeyChecking=no web_interface.py $ADMIN_USERNAME@$VM_IP:~/ai_video_platform/
    
    # Clean up local files
    rm ai_video_generator.py web_interface.py
    
    print_success "AI video generation code deployed"
}

# Create startup script for web interface
setup_web_service() {
    print_status "Setting up web service..."
    
    VM_IP=$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)
    
    # Create systemd service for the web interface
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
# Create systemd service file
sudo tee /etc/systemd/system/ai-video-web.service > /dev/null << 'SERVICE'
[Unit]
Description=AI Video Generator Web Interface
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/ai_video_platform
Environment=PATH=/home/azureuser/ai_video_env/bin
ExecStart=/home/azureuser/ai_video_env/bin/python web_interface.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ai-video-web.service
sudo systemctl start ai-video-web.service

echo "✅ Web service configured and started"
EOF

    print_success "Web service setup completed"
    print_success "Web interface available at: http://$VM_IP"
}

# Display deployment summary
show_summary() {
    VM_IP=$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)
    STORAGE_KEY=$(az storage account keys list --resource-group $RESOURCE_GROUP --account-name $STORAGE_ACCOUNT --query '[0].value' --output tsv)
    
    echo ""
    echo -e "${GREEN}🎉 Azure AI Video Platform Deployment Complete!${NC}"
    echo -e "${BLUE}=================================================${NC}"
    echo ""
    echo -e "${YELLOW}📊 Deployment Summary:${NC}"
    echo "   Resource Group: $RESOURCE_GROUP"
    echo "   Location: $LOCATION"
    echo "   VM Name: $VM_NAME"
    echo "   VM Size: $VM_SIZE (~$1-3/hour)"
    echo "   Public IP: $VM_IP"
    echo "   Storage Account: $STORAGE_ACCOUNT"
    echo ""
    echo -e "${YELLOW}🌐 Access Points:${NC}"
    echo "   Web Interface: http://$VM_IP"
    echo "   SSH Access: ssh $ADMIN_USERNAME@$VM_IP"
    echo "   Status API: http://$VM_IP/status"
    echo ""
    echo -e "${YELLOW}💰 Cost Monitoring:${NC}"
    echo "   Estimated VM cost: $1-3/hour"
    echo "   Storage cost: ~$0.02/GB/month"
    echo "   Monitor spending: Azure Portal > Cost Management"
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo "   1. Visit http://$VM_IP to generate your first AI video"
    echo "   2. Monitor costs in Azure Portal"
    echo "   3. Stop VM when not in use: az vm stop --resource-group $RESOURCE_GROUP --name $VM_NAME"
    echo "   4. Start VM when needed: az vm start --resource-group $RESOURCE_GROUP --name $VM_NAME"
    echo ""
    echo -e "${GREEN}Ready to generate AI videos on Azure! 🎬${NC}"
}

# Main deployment flow
main() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🚀 AZURE AI VIDEO PLATFORM DEPLOYMENT                     ║
║                                                              ║
║   Deploying GPU-based AI video generation on Azure          ║
║   Estimated cost: $1-3/hour for GPU VM                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    print_status "Starting Azure AI Video Platform deployment..."
    
    check_prerequisites
    create_resource_group
    create_storage
    create_network_security
    create_gpu_vm
    install_dependencies
    deploy_code
    setup_web_service
    show_summary
    
    print_success "🎉 Deployment completed successfully!"
}

# Run main function
main "$@"
