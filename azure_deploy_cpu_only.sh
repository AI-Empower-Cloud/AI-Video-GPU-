#!/bin/bash

# 🚀 Azure AI Video Platform - CPU-Only Deployment
# Deploy immediately while waiting for GPU quota approval

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║          🚀 AI VIDEO PLATFORM - CPU DEPLOYMENT              ║${NC}"
    echo -e "${CYAN}║            Deploy immediately without GPU quota             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

main() {
    print_header
    
    echo "🎯 Deploy AI Video Platform with CPU-only processing"
    echo "   Cost: ~$0.10-0.20/hour (very affordable)"
    echo "   Features: Full platform with slower video processing"
    echo "   Upgrade: Easy switch to GPU when quota approved"
    echo ""
    
    read -p "Deploy CPU-only version now? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        echo "CPU deployment cancelled"
        exit 0
    fi
    
    # Use the same resource group from previous attempt
    RG_NAME="ai-video-platform-rg"
    
    print_status "Checking if resource group exists..."
    if az group show --name $RG_NAME &> /dev/null; then
        print_success "Using existing resource group: $RG_NAME"
    else
        print_status "Creating resource group: $RG_NAME"
        az group create --name $RG_NAME --location eastus --output table
    fi
    
    print_status "Creating CPU-optimized VM for AI Video Platform..."
    
    # Create CPU VM with Docker and AI libraries
    az vm create \
        --resource-group $RG_NAME \
        --name ai-video-cpu-vm \
        --image "Ubuntu2204" \
        --size "Standard_D4s_v3" \
        --admin-username azureuser \
        --generate-ssh-keys \
        --public-ip-sku Standard \
        --nsg-rule SSH \
        --custom-data cloud-init-cpu.yaml \
        --output table
    
    if [ $? -eq 0 ]; then
        print_success "CPU VM created successfully!"
        
        # Get VM IP
        VM_IP=$(az vm show --resource-group $RG_NAME --name ai-video-cpu-vm --show-details --query "publicIps" --output tsv)
        
        echo ""
        print_success "🎉 AI Video Platform CPU deployment completed!"
        echo ""
        echo "📋 Deployment Details:"
        echo "   Resource Group: $RG_NAME"
        echo "   VM Name: ai-video-cpu-vm"
        echo "   Public IP: $VM_IP"
        echo "   Cost: ~$0.15/hour"
        echo ""
        echo "📝 Next steps:"
        echo "1. SSH to VM: ssh azureuser@$VM_IP"
        echo "2. Platform will be ready in ~5 minutes (Docker setup)"
        echo "3. Access web interface: http://$VM_IP:8080"
        echo "4. Upload to GitHub when GPU quota approved"
        echo ""
        echo "🔄 Upgrade to GPU:"
        echo "   When GPU quota approved, run: ./upgrade_to_gpu.sh"
        
    else
        print_error "VM creation failed"
        exit 1
    fi
}

# Create cloud-init configuration for CPU setup
cat > cloud-init-cpu.yaml << 'EOF'
#cloud-config
packages:
  - docker.io
  - docker-compose
  - python3-pip
  - git
  - nginx

runcmd:
  - systemctl enable docker
  - systemctl start docker
  - usermod -aG docker azureuser
  - pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
  - pip3 install opencv-python pillow numpy flask gunicorn
  - git clone https://github.com/AI-Empower-Cloud/AI-Video-GPU-.git /home/azureuser/ai-video-platform
  - chown -R azureuser:azureuser /home/azureuser/ai-video-platform
  - cd /home/azureuser/ai-video-platform && docker-compose -f docker-compose.cpu.yml up -d
  - systemctl enable nginx
  - systemctl start nginx

write_files:
  - path: /home/azureuser/ai-video-platform/docker-compose.cpu.yml
    content: |
      version: '3.8'
      services:
        ai-video-frontend:
          build: ./frontend
          ports:
            - "8080:3000"
          environment:
            - NODE_ENV=production
        
        ai-video-api:
          build: ./backend
          ports:
            - "8081:5000"
          environment:
            - PROCESSING_MODE=cpu
            - TORCH_DEVICE=cpu
          volumes:
            - ./uploads:/app/uploads
            - ./outputs:/app/outputs
        
        redis:
          image: redis:alpine
          ports:
            - "6379:6379"
        
        nginx:
          image: nginx:alpine
          ports:
            - "80:80"
          volumes:
            - ./nginx.cpu.conf:/etc/nginx/nginx.conf
EOF

main
