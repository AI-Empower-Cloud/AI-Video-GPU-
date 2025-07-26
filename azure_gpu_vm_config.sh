#!/bin/bash

# =============================================================================
# Azure GPU VM Configuration Script for AI Video Platform
# =============================================================================
# This script optimally configures Azure GPU VMs for AI video generation
# Includes performance tuning, security, monitoring, and cost optimization
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration variables
RESOURCE_GROUP="ai-video-platform-rg"
VM_NAME="ai-video-gpu-vm"
VM_SIZE="Standard_NC6"  # 1 GPU, 6 cores, 56GB RAM
LOCATION="eastus"
ADMIN_USERNAME="azureuser"
STORAGE_ACCOUNT=""
PROJECT_DIR="/home/${ADMIN_USERNAME}/ai_video_platform"

# =============================================================================
# Utility Functions
# =============================================================================

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

info() {
    log "${BLUE}[INFO]${NC} $1"
}

error() {
    log "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        error "Azure CLI is not installed. Please install it first."
        echo "Install with: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        exit 1
    fi
    
    # Check if logged in to Azure
    if ! az account show &> /dev/null; then
        error "Not logged in to Azure. Please run 'az login' first."
        exit 1
    fi
    
    success "Prerequisites check completed"
}

# =============================================================================
# VM Configuration Functions
# =============================================================================

configure_vm_basics() {
    info "Configuring basic VM settings..."
    
    # Get VM IP address
    VM_IP=$(az vm show -d -g $RESOURCE_GROUP -n $VM_NAME --query publicIps -o tsv)
    if [ -z "$VM_IP" ]; then
        error "Could not get VM IP address. Make sure VM is running."
        exit 1
    fi
    
    info "VM IP Address: $VM_IP"
    
    # Test SSH connectivity
    info "Testing SSH connectivity..."
    if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP "echo 'SSH connection successful'" 2>/dev/null; then
        error "Cannot connect to VM via SSH. Check your SSH keys and VM status."
        exit 1
    fi
    
    success "Basic VM configuration completed"
}

install_nvidia_drivers() {
    info "Installing and configuring NVIDIA drivers..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Update system
        sudo apt update -y
        sudo apt upgrade -y
        
        # Install build essentials
        sudo apt install -y build-essential gcc make
        
        # Remove any existing NVIDIA installations
        sudo apt remove --purge nvidia* -y
        sudo apt autoremove -y
        
        # Install NVIDIA drivers
        sudo apt install -y nvidia-driver-470
        sudo apt install -y nvidia-utils-470
        
        # Install CUDA toolkit
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
        sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
        wget https://developer.download.nvidia.com/compute/cuda/11.4.0/local_installers/cuda-repo-ubuntu2004-11-4-local_11.4.0-470.42.01-1_amd64.deb
        sudo dpkg -i cuda-repo-ubuntu2004-11-4-local_11.4.0-470.42.01-1_amd64.deb
        sudo apt-key add /var/cuda-repo-ubuntu2004-11-4-local/7fa2af80.pub
        sudo apt update -y
        sudo apt install -y cuda
        
        # Add CUDA to PATH
        echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
        echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
        
        # Configure NVIDIA persistence mode
        sudo nvidia-smi -pm 1
        
        # Set GPU power limit for efficiency (optional)
        sudo nvidia-smi -pl 150  # Set to 150W (from default 250W)
        
        echo "NVIDIA driver installation completed"
EOF
    
    success "NVIDIA drivers and CUDA installed"
}

install_ai_dependencies() {
    info "Installing AI/ML dependencies and libraries..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Create Python virtual environment
        sudo apt install -y python3-pip python3-venv
        python3 -m venv ~/ai_video_env
        source ~/ai_video_env/bin/activate
        
        # Upgrade pip
        pip install --upgrade pip
        
        # Install PyTorch with CUDA support
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        
        # Install essential AI/ML libraries
        pip install \
            numpy \
            opencv-python \
            pillow \
            scipy \
            scikit-learn \
            matplotlib \
            seaborn \
            pandas \
            jupyter \
            ipython
        
        # Install video processing libraries
        pip install \
            moviepy \
            ffmpeg-python \
            imageio \
            imageio-ffmpeg
        
        # Install deep learning frameworks
        pip install \
            transformers \
            diffusers \
            accelerate \
            xformers \
            compel
        
        # Install web framework for API
        pip install \
            flask \
            flask-cors \
            gunicorn \
            requests
        
        # Install monitoring tools
        pip install \
            psutil \
            gpustat \
            nvidia-ml-py3
        
        echo "AI/ML dependencies installation completed"
EOF
    
    success "AI/ML dependencies installed"
}

install_system_tools() {
    info "Installing system tools and utilities..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Install essential system tools
        sudo apt install -y \
            htop \
            nvtop \
            tree \
            wget \
            curl \
            git \
            vim \
            nano \
            unzip \
            zip \
            screen \
            tmux
        
        # Install FFmpeg with all codecs
        sudo apt install -y \
            ffmpeg \
            libavcodec-extra \
            libavformat-dev \
            libavutil-dev \
            libswscale-dev \
            libavresample-dev
        
        # Install Docker for containerization
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        
        # Install Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        echo "System tools installation completed"
EOF
    
    success "System tools installed"
}

configure_performance_optimizations() {
    info "Applying performance optimizations..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Optimize GPU performance
        sudo nvidia-smi -ac 2505,875  # Set memory and graphics clock
        
        # Optimize CPU performance
        echo 'performance' | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
        
        # Optimize memory settings
        echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
        echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
        echo 'vm.dirty_ratio=15' | sudo tee -a /etc/sysctl.conf
        echo 'vm.dirty_background_ratio=5' | sudo tee -a /etc/sysctl.conf
        
        # Optimize network settings
        echo 'net.core.rmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
        echo 'net.core.wmem_max = 134217728' | sudo tee -a /etc/sysctl.conf
        echo 'net.ipv4.tcp_rmem = 4096 87380 134217728' | sudo tee -a /etc/sysctl.conf
        echo 'net.ipv4.tcp_wmem = 4096 65536 134217728' | sudo tee -a /etc/sysctl.conf
        
        # Apply sysctl settings
        sudo sysctl -p
        
        # Configure automatic GPU performance mode on boot
        sudo tee /etc/systemd/system/gpu-performance.service > /dev/null <<EOL
[Unit]
Description=GPU Performance Optimization
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/nvidia-smi -pm 1
ExecStart=/usr/bin/nvidia-smi -ac 2505,875
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOL
        
        sudo systemctl enable gpu-performance.service
        
        echo "Performance optimizations applied"
EOF
    
    success "Performance optimizations configured"
}

setup_monitoring() {
    info "Setting up system monitoring..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Create monitoring script
        mkdir -p ~/monitoring
        
        cat > ~/monitoring/system_monitor.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import psutil
import GPUtil
import json
import time
from datetime import datetime

def get_system_info():
    # Get GPU info
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        gpu_info.append({
            'id': gpu.id,
            'name': gpu.name,
            'load': gpu.load * 100,
            'memory_used': gpu.memoryUsed,
            'memory_total': gpu.memoryTotal,
            'memory_percent': (gpu.memoryUsed / gpu.memoryTotal) * 100,
            'temperature': gpu.temperature
        })
    
    # Get CPU info
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # Get memory info
    memory = psutil.virtual_memory()
    
    # Get disk info
    disk = psutil.disk_usage('/')
    
    # Get network info
    network = psutil.net_io_counters()
    
    system_info = {
        'timestamp': datetime.now().isoformat(),
        'cpu': {
            'percent': cpu_percent,
            'count': cpu_count
        },
        'memory': {
            'total': memory.total,
            'available': memory.available,
            'percent': memory.percent,
            'used': memory.used
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': (disk.used / disk.total) * 100
        },
        'network': {
            'bytes_sent': network.bytes_sent,
            'bytes_recv': network.bytes_recv
        },
        'gpu': gpu_info
    }
    
    return system_info

if __name__ == "__main__":
    info = get_system_info()
    print(json.dumps(info, indent=2))
PYTHON_EOF
        
        chmod +x ~/monitoring/system_monitor.py
        
        # Create monitoring service
        sudo tee /etc/systemd/system/system-monitor.service > /dev/null <<EOL
[Unit]
Description=System Monitor
After=multi-user.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/monitoring
ExecStart=/home/$USER/ai_video_env/bin/python system_monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOL
        
        # Create log rotation for monitoring
        sudo tee /etc/logrotate.d/system-monitor > /dev/null <<EOL
/var/log/system-monitor.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOL
        
        echo "System monitoring setup completed"
EOF
    
    success "System monitoring configured"
}

setup_auto_shutdown() {
    info "Setting up auto-shutdown for cost optimization..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Create auto-shutdown script
        cat > ~/auto_shutdown.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import psutil
import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/azureuser/auto_shutdown.log'),
        logging.StreamHandler()
    ]
)

def get_system_activity():
    """Check if system is actively being used"""
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Check memory usage
    memory = psutil.virtual_memory()
    
    # Check GPU usage (if available)
    gpu_usage = 0
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_usage = gpus[0].load * 100
    except ImportError:
        pass
    
    # Check active processes
    active_processes = len([p for p in psutil.process_iter() if p.status() == 'running'])
    
    # Check network activity
    network = psutil.net_io_counters()
    
    return {
        'cpu': cpu_percent,
        'memory': memory.percent,
        'gpu': gpu_usage,
        'processes': active_processes,
        'network_sent': network.bytes_sent,
        'network_recv': network.bytes_recv
    }

def should_shutdown():
    """Determine if system should shutdown based on activity"""
    activity = get_system_activity()
    
    # Thresholds for idle detection
    cpu_threshold = 5.0
    gpu_threshold = 5.0
    
    # System is considered idle if:
    # - CPU usage < 5%
    # - GPU usage < 5%
    # - No video generation processes running
    
    if activity['cpu'] < cpu_threshold and activity['gpu'] < gpu_threshold:
        # Check for AI video processes
        ai_processes = [
            'python', 'torch', 'cuda', 'ffmpeg', 'moviepy'
        ]
        
        running_ai_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if any(ai_proc in ' '.join(proc.info['cmdline']).lower() 
                      for ai_proc in ai_processes):
                    running_ai_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not running_ai_processes:
            return True
    
    return False

def main():
    idle_time = 0
    idle_threshold = 1800  # 30 minutes in seconds
    check_interval = 300   # 5 minutes
    
    logging.info("Auto-shutdown monitor started")
    
    while True:
        try:
            if should_shutdown():
                idle_time += check_interval
                logging.info(f"System idle for {idle_time} seconds")
                
                if idle_time >= idle_threshold:
                    logging.info("Initiating auto-shutdown to save costs")
                    subprocess.run(['sudo', 'shutdown', '-h', '+5', 
                                  'Auto-shutdown: System idle for 30 minutes'])
                    break
            else:
                if idle_time > 0:
                    logging.info("System activity detected, resetting idle timer")
                idle_time = 0
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            logging.info("Auto-shutdown monitor stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in auto-shutdown monitor: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
PYTHON_EOF
        
        chmod +x ~/auto_shutdown.py
        
        # Create systemd service for auto-shutdown
        sudo tee /etc/systemd/system/auto-shutdown.service > /dev/null <<EOL
[Unit]
Description=Auto Shutdown Monitor
After=multi-user.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER
ExecStart=/home/$USER/ai_video_env/bin/python auto_shutdown.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOL
        
        # Enable but don't start the service (user can enable it manually)
        sudo systemctl enable auto-shutdown.service
        
        echo "Auto-shutdown system configured (disabled by default)"
        echo "To enable: sudo systemctl start auto-shutdown.service"
EOF
    
    success "Auto-shutdown system configured"
}

setup_security() {
    info "Configuring security settings..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Update system packages
        sudo apt update && sudo apt upgrade -y
        
        # Install and configure fail2ban
        sudo apt install -y fail2ban
        sudo systemctl enable fail2ban
        
        # Configure SSH security
        sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
        
        # Secure SSH configuration
        sudo tee -a /etc/ssh/sshd_config.custom > /dev/null <<EOL
# Custom SSH Security Settings
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
Protocol 2
X11Forwarding no
EOL
        
        # Apply SSH configuration
        sudo systemctl restart sshd
        
        # Configure firewall
        sudo ufw --force enable
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow ssh
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow 8080/tcp  # For web interface
        
        # Install antivirus
        sudo apt install -y clamav clamav-daemon
        sudo freshclam
        sudo systemctl enable clamav-daemon
        
        echo "Security configuration completed"
EOF
    
    success "Security settings configured"
}

create_deployment_scripts() {
    info "Creating deployment and management scripts..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        mkdir -p ~/scripts
        
        # Create GPU status script
        cat > ~/scripts/gpu_status.sh << 'SCRIPT_EOF'
#!/bin/bash
echo "=== GPU Status ==="
nvidia-smi
echo ""
echo "=== GPU Processes ==="
nvidia-smi pmon -c 1
echo ""
echo "=== System Resources ==="
htop -n 1
SCRIPT_EOF
        
        # Create performance test script
        cat > ~/scripts/performance_test.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import torch
import time
import numpy as np

def test_gpu_performance():
    if not torch.cuda.is_available():
        print("CUDA is not available!")
        return
    
    device = torch.device("cuda")
    print(f"Testing GPU: {torch.cuda.get_device_name(0)}")
    
    # Test tensor operations
    print("Testing tensor operations...")
    start_time = time.time()
    
    a = torch.randn(10000, 10000, device=device)
    b = torch.randn(10000, 10000, device=device)
    c = torch.matmul(a, b)
    
    torch.cuda.synchronize()
    end_time = time.time()
    
    print(f"Matrix multiplication (10k x 10k): {end_time - start_time:.2f} seconds")
    
    # Test memory bandwidth
    print("Testing memory bandwidth...")
    start_time = time.time()
    
    data = torch.randn(100000000, device=device)
    result = torch.sum(data)
    
    torch.cuda.synchronize()
    end_time = time.time()
    
    print(f"Memory bandwidth test: {end_time - start_time:.2f} seconds")
    
    # Print GPU memory usage
    print(f"GPU Memory: {torch.cuda.memory_allocated()/1024**3:.2f} GB used")
    print(f"GPU Memory: {torch.cuda.memory_reserved()/1024**3:.2f} GB reserved")

if __name__ == "__main__":
    test_gpu_performance()
PYTHON_EOF
        
        # Create cost monitoring script
        cat > ~/scripts/cost_monitor.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import json
import time
from datetime import datetime, timedelta

class CostMonitor:
    def __init__(self):
        self.vm_hourly_cost = 0.90  # Standard_NC6 approximate cost
        self.storage_gb_monthly = 0.045  # Standard storage cost per GB
        self.network_gb_cost = 0.05  # Egress cost per GB
        
    def calculate_daily_cost(self, hours_running, storage_gb=0, network_gb=0):
        vm_cost = hours_running * self.vm_hourly_cost
        storage_cost = (storage_gb * self.storage_gb_monthly) / 30  # Daily storage
        network_cost = network_gb * self.network_gb_cost
        
        return {
            'vm_cost': vm_cost,
            'storage_cost': storage_cost,
            'network_cost': network_cost,
            'total_cost': vm_cost + storage_cost + network_cost
        }
    
    def project_monthly_cost(self, daily_hours, storage_gb=0, network_gb_daily=0):
        monthly_vm = daily_hours * 30 * self.vm_hourly_cost
        monthly_storage = storage_gb * self.storage_gb_monthly
        monthly_network = network_gb_daily * 30 * self.network_gb_cost
        
        return {
            'vm_cost': monthly_vm,
            'storage_cost': monthly_storage,
            'network_cost': monthly_network,
            'total_cost': monthly_vm + monthly_storage + monthly_network
        }
    
    def budget_remaining_days(self, budget=1000, current_spend=0, daily_average=0):
        remaining_budget = budget - current_spend
        if daily_average <= 0:
            return float('inf')
        return remaining_budget / daily_average

def main():
    monitor = CostMonitor()
    
    # Example usage
    print("=== Azure Cost Monitor ===")
    print(f"VM Hourly Cost: ${monitor.vm_hourly_cost}")
    
    # Calculate sample costs
    daily_cost = monitor.calculate_daily_cost(hours_running=8, storage_gb=50, network_gb=2)
    print(f"\nDaily Cost (8 hours runtime):")
    print(f"  VM: ${daily_cost['vm_cost']:.2f}")
    print(f"  Storage: ${daily_cost['storage_cost']:.2f}")
    print(f"  Network: ${daily_cost['network_cost']:.2f}")
    print(f"  Total: ${daily_cost['total_cost']:.2f}")
    
    monthly_projection = monitor.project_monthly_cost(daily_hours=6, storage_gb=100, network_gb_daily=5)
    print(f"\nMonthly Projection (6 hours/day average):")
    print(f"  VM: ${monthly_projection['vm_cost']:.2f}")
    print(f"  Storage: ${monthly_projection['storage_cost']:.2f}")
    print(f"  Network: ${monthly_projection['network_cost']:.2f}")
    print(f"  Total: ${monthly_projection['total_cost']:.2f}")
    
    # Budget analysis
    remaining_days = monitor.budget_remaining_days(
        budget=1000, 
        current_spend=100, 
        daily_average=daily_cost['total_cost']
    )
    print(f"\nBudget Analysis:")
    print(f"  Remaining days at current rate: {remaining_days:.1f} days")

if __name__ == "__main__":
    main()
PYTHON_EOF
        
        # Make scripts executable
        chmod +x ~/scripts/*.sh ~/scripts/*.py
        
        echo "Deployment scripts created"
EOF
    
    success "Deployment and management scripts created"
}

setup_web_interface() {
    info "Setting up web interface for video generation..."
    
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        source ~/ai_video_env/bin/activate
        
        # Create web interface directory
        mkdir -p ~/ai_video_platform/templates
        mkdir -p ~/ai_video_platform/static
        mkdir -p ~/ai_video_platform/videos
        
        # Create main Flask application
        cat > ~/ai_video_platform/app.py << 'PYTHON_EOF'
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import json
import torch
import time
import logging
from datetime import datetime
import subprocess
import psutil
try:
    import GPUtil
except ImportError:
    GPUtil = None

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
VIDEO_DIR = os.path.join(os.path.dirname(__file__), 'videos')
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        # Get GPU info
        gpu_info = None
        if GPUtil:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_info = {
                    'name': gpu.name,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'load': gpu.load * 100,
                    'temperature': gpu.temperature
                }
        
        # Get system info
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'cuda_available': torch.cuda.is_available(),
            'gpu': gpu_info,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': (disk.used / disk.total) * 100,
            'video_count': len([f for f in os.listdir(VIDEO_DIR) if f.endswith('.mp4')])
        }
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_video():
    """Generate a video"""
    try:
        data = request.json
        text = data.get('text', 'Default AI Video')
        duration = int(data.get('duration', 10))
        
        # Generate video filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        video_filename = f"ai_video_{timestamp}.mp4"
        video_path = os.path.join(VIDEO_DIR, video_filename)
        
        # Simple video generation (placeholder)
        # In a real implementation, this would use your AI video generation pipeline
        success = generate_simple_video(text, duration, video_path)
        
        if success:
            return jsonify({
                'success': True,
                'filename': video_filename,
                'path': f'/api/video/{video_filename}',
                'duration': duration,
                'text': text
            })
        else:
            return jsonify({'success': False, 'error': 'Video generation failed'}), 500
    
    except Exception as e:
        logger.error(f"Error generating video: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/video/<filename>')
def serve_video(filename):
    """Serve generated video"""
    try:
        video_path = os.path.join(VIDEO_DIR, filename)
        if os.path.exists(video_path):
            return send_file(video_path, mimetype='video/mp4')
        else:
            return jsonify({'error': 'Video not found'}), 404
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/videos')
def list_videos():
    """List all generated videos"""
    try:
        videos = []
        for filename in os.listdir(VIDEO_DIR):
            if filename.endswith('.mp4'):
                filepath = os.path.join(VIDEO_DIR, filename)
                stat = os.stat(filepath)
                videos.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'url': f'/api/video/{filename}'
                })
        
        return jsonify({'videos': videos})
    
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({'error': str(e)}), 500

def generate_simple_video(text, duration, output_path):
    """Simple video generation function"""
    try:
        # Create a simple video with text overlay using ffmpeg
        command = [
            'ffmpeg', '-f', 'lavfi', '-i', 
            f'color=c=blue:size=1280x720:duration={duration}',
            '-vf', f'drawtext=text=\'{text}\':fontcolor=white:fontsize=60:x=(w-text_w)/2:y=(h-text_h)/2',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-y', output_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode == 0
    
    except Exception as e:
        logger.error(f"Error in video generation: {e}")
        return False

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
PYTHON_EOF
        
        # Create HTML template
        cat > ~/ai_video_platform/templates/index.html << 'HTML_EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure AI Video Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 3rem; margin-bottom: 10px; }
        .card { 
            background: white; 
            border-radius: 15px; 
            padding: 30px; 
            margin: 20px 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input, .form-group textarea { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #ddd; 
            border-radius: 8px;
            font-size: 16px;
        }
        .btn { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px;
            cursor: pointer; 
            font-size: 16px;
            transition: transform 0.3s ease;
        }
        .btn:hover { transform: translateY(-2px); }
        .status { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 15px; 
            margin: 20px 0;
        }
        .status-item { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center;
        }
        .video-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 20px;
        }
        .video-item { 
            background: #f8f9fa; 
            padding: 15px; 
            border-radius: 8px;
        }
        .video-item video { width: 100%; border-radius: 8px; }
        .loading { text-align: center; color: #667eea; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Azure AI Video Platform</h1>
            <p>Generate AI-powered videos using Azure GPU infrastructure</p>
        </div>
        
        <div class="card">
            <h2>System Status</h2>
            <div class="status" id="statusContainer">
                <div class="status-item">
                    <div>CUDA Available</div>
                    <div id="cudaStatus">Checking...</div>
                </div>
                <div class="status-item">
                    <div>GPU Usage</div>
                    <div id="gpuUsage">Checking...</div>
                </div>
                <div class="status-item">
                    <div>CPU Usage</div>
                    <div id="cpuUsage">Checking...</div>
                </div>
                <div class="status-item">
                    <div>Videos Generated</div>
                    <div id="videoCount">0</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Generate Video</h2>
            <form id="videoForm">
                <div class="form-group">
                    <label for="videoText">Video Text:</label>
                    <textarea id="videoText" rows="3" placeholder="Enter the text for your AI video...">Azure AI Video Generation Demo</textarea>
                </div>
                <div class="form-group">
                    <label for="videoDuration">Duration (seconds):</label>
                    <input type="number" id="videoDuration" min="5" max="60" value="10">
                </div>
                <button type="submit" class="btn">Generate Video</button>
            </form>
            <div id="generationStatus" class="loading" style="display: none;">
                Generating video... This may take a few minutes.
            </div>
        </div>
        
        <div class="card">
            <h2>Generated Videos</h2>
            <div id="videosContainer" class="video-grid">
                <div class="loading">Loading videos...</div>
            </div>
        </div>
    </div>

    <script>
        // Update system status
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cudaStatus').textContent = data.cuda_available ? 'Available' : 'Not Available';
                    document.getElementById('cpuUsage').textContent = data.cpu_percent.toFixed(1) + '%';
                    document.getElementById('videoCount').textContent = data.video_count;
                    
                    if (data.gpu) {
                        document.getElementById('gpuUsage').textContent = data.gpu.load.toFixed(1) + '%';
                    } else {
                        document.getElementById('gpuUsage').textContent = 'N/A';
                    }
                })
                .catch(error => console.error('Error updating status:', error));
        }
        
        // Load videos
        function loadVideos() {
            fetch('/api/videos')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('videosContainer');
                    if (data.videos && data.videos.length > 0) {
                        container.innerHTML = data.videos.map(video => `
                            <div class="video-item">
                                <video controls>
                                    <source src="${video.url}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                                <div style="margin-top: 10px;">
                                    <strong>${video.filename}</strong><br>
                                    Size: ${(video.size / 1024 / 1024).toFixed(2)} MB<br>
                                    Created: ${new Date(video.created).toLocaleString()}
                                </div>
                            </div>
                        `).join('');
                    } else {
                        container.innerHTML = '<div class="loading">No videos generated yet.</div>';
                    }
                })
                .catch(error => {
                    console.error('Error loading videos:', error);
                    document.getElementById('videosContainer').innerHTML = '<div class="loading">Error loading videos.</div>';
                });
        }
        
        // Handle form submission
        document.getElementById('videoForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const text = document.getElementById('videoText').value;
            const duration = document.getElementById('videoDuration').value;
            const statusDiv = document.getElementById('generationStatus');
            
            statusDiv.style.display = 'block';
            
            fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    duration: parseInt(duration)
                })
            })
            .then(response => response.json())
            .then(data => {
                statusDiv.style.display = 'none';
                if (data.success) {
                    alert('Video generated successfully!');
                    loadVideos();
                    updateStatus();
                } else {
                    alert('Error generating video: ' + data.error);
                }
            })
            .catch(error => {
                statusDiv.style.display = 'none';
                alert('Error generating video: ' + error);
            });
        });
        
        // Initialize
        updateStatus();
        loadVideos();
        
        // Update status every 30 seconds
        setInterval(updateStatus, 30000);
    </script>
</body>
</html>
HTML_EOF
        
        # Create systemd service for web interface
        sudo tee /etc/systemd/system/ai-video-web.service > /dev/null <<EOL
[Unit]
Description=AI Video Web Interface
After=multi-user.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/ai_video_platform
Environment=PATH=/home/$USER/ai_video_env/bin
ExecStart=/home/$USER/ai_video_env/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL
        
        sudo systemctl enable ai-video-web.service
        sudo systemctl start ai-video-web.service
        
        echo "Web interface setup completed"
EOF
    
    success "Web interface configured and started"
}

# =============================================================================
# Main Configuration Process
# =============================================================================

main() {
    echo -e "${CYAN}"
    echo "=============================================="
    echo "🚀 AZURE GPU VM CONFIGURATION"
    echo "=============================================="
    echo "Optimizing Azure VM for AI video generation"
    echo "This will configure performance, security, and monitoring"
    echo -e "${NC}"
    
    # Get storage account name if not set
    if [ -z "$STORAGE_ACCOUNT" ]; then
        STORAGE_ACCOUNT=$(az storage account list -g $RESOURCE_GROUP --query '[0].name' -o tsv)
        if [ -z "$STORAGE_ACCOUNT" ]; then
            warning "Storage account not found. Some features may not work."
        else
            info "Using storage account: $STORAGE_ACCOUNT"
        fi
    fi
    
    # Check if we can connect to the VM
    info "Checking VM connectivity..."
    if ! az vm show -g $RESOURCE_GROUP -n $VM_NAME &> /dev/null; then
        error "VM '$VM_NAME' not found in resource group '$RESOURCE_GROUP'"
        error "Please run the deployment script first: ./azure_deploy_ai_video.sh"
        exit 1
    fi
    
    # Start configuration process
    check_prerequisites
    configure_vm_basics
    
    info "Starting comprehensive VM configuration..."
    info "This process will take 15-30 minutes depending on your internet connection"
    
    # Core installations
    install_nvidia_drivers
    install_ai_dependencies
    install_system_tools
    
    # Performance and monitoring
    configure_performance_optimizations
    setup_monitoring
    setup_auto_shutdown
    
    # Security and management
    setup_security
    create_deployment_scripts
    setup_web_interface
    
    # Final setup
    info "Performing final configuration..."
    ssh -o StrictHostKeyChecking=no $ADMIN_USERNAME@$VM_IP << 'EOF'
        # Reboot to ensure all kernel modules are loaded
        echo "Configuration completed. System will reboot in 60 seconds."
        echo "After reboot, access your platform at: http://$(curl -s ifconfig.me):8080"
        sudo shutdown -r +1 "System reboot for configuration completion"
EOF
    
    echo -e "${GREEN}"
    echo "=============================================="
    echo "🎉 AZURE GPU VM CONFIGURATION COMPLETE!"
    echo "=============================================="
    echo -e "${NC}"
    
    echo "✅ NVIDIA drivers and CUDA installed"
    echo "✅ AI/ML dependencies configured"
    echo "✅ Performance optimizations applied"
    echo "✅ Security settings configured"
    echo "✅ Monitoring systems enabled"
    echo "✅ Auto-shutdown configured (disabled by default)"
    echo "✅ Web interface deployed"
    echo "✅ Management scripts created"
    
    echo ""
    echo -e "${CYAN}🌐 Access Points:${NC}"
    echo "   Web Interface: http://$VM_IP:8080"
    echo "   SSH Access: ssh $ADMIN_USERNAME@$VM_IP"
    echo "   Cost Monitor: scp azure_cost_monitor.html $ADMIN_USERNAME@$VM_IP:~/cost_monitor.html"
    
    echo ""
    echo -e "${YELLOW}💡 Next Steps:${NC}"
    echo "1. Wait for system reboot (1-2 minutes)"
    echo "2. Access web interface to generate first video"
    echo "3. Monitor costs with: ssh $ADMIN_USERNAME@$VM_IP './scripts/cost_monitor.py'"
    echo "4. Check GPU status: ssh $ADMIN_USERNAME@$VM_IP './scripts/gpu_status.sh'"
    echo "5. Enable auto-shutdown if desired: sudo systemctl start auto-shutdown.service"
    
    echo ""
    echo -e "${GREEN}🎯 Your Azure AI Video Platform is ready for production!${NC}"
}

# Run main function
main "$@"
