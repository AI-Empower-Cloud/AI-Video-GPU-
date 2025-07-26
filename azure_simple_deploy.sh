#!/bin/bash

# Azure AI Video Platform - Simple Deployment
# Optimized for new/trial Azure subscriptions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
RESOURCE_GROUP="ai-video-platform-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="aivideosimple$RANDOM"
VM_NAME="ai-video-vm"
VM_SIZE="Standard_B2s"  # Cost-effective size for testing
ADMIN_USERNAME="azureuser"

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🚀 AZURE AI VIDEO PLATFORM - SIMPLE DEPLOYMENT           ║"
echo "║                                                              ║"
echo "║   Trial/Free-tier optimized deployment                      ║"
echo "║   Estimated cost: $20-50/month                              ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[INFO] Starting simple deployment...${NC}"

# Check if providers are registered
echo -e "${YELLOW}[INFO] Checking Azure provider registration...${NC}"

check_provider() {
    local provider=$1
    local status=$(az provider show --namespace $provider --query "registrationState" --output tsv 2>/dev/null || echo "NotRegistered")
    
    if [ "$status" != "Registered" ]; then
        echo -e "${YELLOW}[INFO] Registering provider: $provider${NC}"
        az provider register --namespace $provider
        
        # Wait for registration
        echo -e "${YELLOW}[INFO] Waiting for $provider registration...${NC}"
        while [ "$(az provider show --namespace $provider --query 'registrationState' --output tsv)" != "Registered" ]; do
            echo -e "${YELLOW}[INFO] Still registering $provider...${NC}"
            sleep 10
        done
        echo -e "${GREEN}[SUCCESS] $provider registered successfully${NC}"
    else
        echo -e "${GREEN}[SUCCESS] $provider already registered${NC}"
    fi
}

# Register required providers
check_provider "Microsoft.Storage"
check_provider "Microsoft.Compute" 
check_provider "Microsoft.Network"

# Check if resource group exists
echo -e "${YELLOW}[INFO] Checking resource group...${NC}"
if ! az group show --name $RESOURCE_GROUP &>/dev/null; then
    echo -e "${YELLOW}[INFO] Creating resource group: $RESOURCE_GROUP${NC}"
    az group create --name $RESOURCE_GROUP --location $LOCATION
    echo -e "${GREEN}[SUCCESS] Resource group created${NC}"
else
    echo -e "${GREEN}[SUCCESS] Resource group already exists${NC}"
fi

# Create storage account
echo -e "${YELLOW}[INFO] Creating storage account: $STORAGE_ACCOUNT${NC}"
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS \
    --kind StorageV2 \
    --access-tier Hot
echo -e "${GREEN}[SUCCESS] Storage account created${NC}"

# Create virtual network
echo -e "${YELLOW}[INFO] Creating virtual network...${NC}"
az network vnet create \
    --resource-group $RESOURCE_GROUP \
    --name ai-video-vnet \
    --address-prefix 10.0.0.0/16 \
    --subnet-name ai-video-subnet \
    --subnet-prefix 10.0.1.0/24
echo -e "${GREEN}[SUCCESS] Virtual network created${NC}"

# Create network security group
echo -e "${YELLOW}[INFO] Creating network security group...${NC}"
az network nsg create \
    --resource-group $RESOURCE_GROUP \
    --name ai-video-nsg

# Add security rules
az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name ai-video-nsg \
    --name allow-ssh \
    --protocol tcp \
    --priority 1000 \
    --destination-port-range 22 \
    --access allow

az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name ai-video-nsg \
    --name allow-http \
    --protocol tcp \
    --priority 1001 \
    --destination-port-range 80 \
    --access allow

az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name ai-video-nsg \
    --name allow-https \
    --protocol tcp \
    --priority 1002 \
    --destination-port-range 443 \
    --access allow

echo -e "${GREEN}[SUCCESS] Network security group created${NC}"

# Create public IP
echo -e "${YELLOW}[INFO] Creating public IP...${NC}"
az network public-ip create \
    --resource-group $RESOURCE_GROUP \
    --name ai-video-ip \
    --sku Standard \
    --allocation-method Static
echo -e "${GREEN}[SUCCESS] Public IP created${NC}"

# Create network interface
echo -e "${YELLOW}[INFO] Creating network interface...${NC}"
az network nic create \
    --resource-group $RESOURCE_GROUP \
    --name ai-video-nic \
    --vnet-name ai-video-vnet \
    --subnet ai-video-subnet \
    --public-ip-address ai-video-ip \
    --network-security-group ai-video-nsg
echo -e "${GREEN}[SUCCESS] Network interface created${NC}"

# Generate SSH key if it doesn't exist
echo -e "${YELLOW}[INFO] Setting up SSH keys...${NC}"
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N ""
    echo -e "${GREEN}[SUCCESS] SSH key generated${NC}"
else
    echo -e "${GREEN}[SUCCESS] SSH key already exists${NC}"
fi

# Create virtual machine
echo -e "${YELLOW}[INFO] Creating virtual machine: $VM_NAME${NC}"
az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --nics ai-video-nic \
    --image Ubuntu2004 \
    --size $VM_SIZE \
    --admin-username $ADMIN_USERNAME \
    --ssh-key-values ~/.ssh/id_rsa.pub \
    --storage-sku Premium_LRS

echo -e "${GREEN}[SUCCESS] Virtual machine created${NC}"

# Get public IP address
PUBLIC_IP=$(az network public-ip show --resource-group $RESOURCE_GROUP --name ai-video-ip --query ipAddress --output tsv)

# Install AI video dependencies
echo -e "${YELLOW}[INFO] Installing AI video platform dependencies...${NC}"
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunShellScript \
    --scripts "
        sudo apt update -y
        sudo apt install -y python3 python3-pip docker.io git curl
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $ADMIN_USERNAME
        
        # Install Python dependencies
        pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        pip3 install opencv-python pillow numpy matplotlib
        pip3 install flask fastapi uvicorn
        
        # Clone AI video platform
        cd /home/$ADMIN_USERNAME
        git clone https://github.com/AI-Empower-Cloud/AI-Video-GPU-.git
        chown -R $ADMIN_USERNAME:$ADMIN_USERNAME AI-Video-GPU-
        
        echo 'AI Video Platform Setup Complete!' > /home/$ADMIN_USERNAME/setup_complete.txt
    "

echo -e "${GREEN}[SUCCESS] Dependencies installed${NC}"

# Create startup script
echo -e "${YELLOW}[INFO] Creating startup script...${NC}"
cat > start_ai_video.sh << 'EOF'
#!/bin/bash
cd ~/AI-Video-GPU-
python3 -m http.server 8080 &
echo "AI Video Platform started on port 8080"
echo "Access at: http://your-vm-ip:8080"
EOF

# Copy startup script to VM
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunShellScript \
    --scripts "echo '$(cat start_ai_video.sh)' > /home/$ADMIN_USERNAME/start_ai_video.sh && chmod +x /home/$ADMIN_USERNAME/start_ai_video.sh"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   🎉 DEPLOYMENT COMPLETE!                                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo -e "${GREEN}✅ Resource Group: $RESOURCE_GROUP${NC}"
echo -e "${GREEN}✅ Storage Account: $STORAGE_ACCOUNT${NC}"
echo -e "${GREEN}✅ Virtual Machine: $VM_NAME${NC}"
echo -e "${GREEN}✅ Public IP: $PUBLIC_IP${NC}"
echo ""
echo -e "${YELLOW}🔗 Access Information:${NC}"
echo -e "${BLUE}SSH Access: ssh $ADMIN_USERNAME@$PUBLIC_IP${NC}"
echo -e "${BLUE}Web Access: http://$PUBLIC_IP:8080${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "1. SSH into your VM: ssh $ADMIN_USERNAME@$PUBLIC_IP"
echo "2. Start the AI video platform: ./start_ai_video.sh"
echo "3. Access the web interface at http://$PUBLIC_IP:8080"
echo "4. Monitor costs at: https://portal.azure.com"
echo ""
echo -e "${GREEN}🎯 Estimated monthly cost: $20-50 (for Standard_B2s VM)${NC}"
echo -e "${BLUE}💰 Your Azure credits: Use $1,000 free credits wisely!${NC}"
