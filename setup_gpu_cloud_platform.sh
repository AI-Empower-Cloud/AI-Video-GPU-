#!/bin/bash
# setup_gpu_cloud_platform.sh - Automated setup script for GPU cloud platform

set -e

echo "🚀 GPU Cloud Platform Setup Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi

# System requirements check
check_requirements() {
    log "Checking system requirements..."
    
    # Check for NVIDIA GPU
    if ! command -v nvidia-smi &> /dev/null; then
        error "NVIDIA GPU and drivers not detected. Please install NVIDIA drivers first."
    fi
    
    # Check for Docker
    if ! command -v docker &> /dev/null; then
        warn "Docker not found. Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
    fi
    
    # Check for kubectl
    if ! command -v kubectl &> /dev/null; then
        warn "kubectl not found. Installing kubectl..."
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        rm kubectl
    fi
    
    log "✅ System requirements check completed"
}

# Install NVIDIA Container Toolkit
install_nvidia_docker() {
    log "Installing NVIDIA Container Toolkit..."
    
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    
    sudo apt-get update
    sudo apt-get install -y nvidia-docker2
    sudo systemctl restart docker
    
    # Test NVIDIA Docker
    if docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi; then
        log "✅ NVIDIA Docker installation successful"
    else
        error "NVIDIA Docker installation failed"
    fi
}

# Install Kubernetes (kind for development)
install_kubernetes() {
    log "Installing Kubernetes (kind)..."
    
    # Install kind
    if ! command -v kind &> /dev/null; then
        curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
        chmod +x ./kind
        sudo mv ./kind /usr/local/bin/kind
    fi
    
    # Create kind cluster with GPU support
    cat <<EOF > kind-gpu-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraMounts:
  - hostPath: /dev/nvidia0
    containerPath: /dev/nvidia0
  - hostPath: /dev/nvidiactl
    containerPath: /dev/nvidiactl
  - hostPath: /dev/nvidia-uvm
    containerPath: /dev/nvidia-uvm
  - hostPath: /usr/bin/nvidia-smi
    containerPath: /usr/bin/nvidia-smi
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
    protocol: TCP
EOF
    
    kind create cluster --config kind-gpu-config.yaml --name gpu-cloud
    
    # Install NVIDIA device plugin
    kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.1/nvidia-device-plugin.yml
    
    log "✅ Kubernetes cluster created with GPU support"
    rm kind-gpu-config.yaml
}

# Create project structure
create_project_structure() {
    log "Creating project structure..."
    
    mkdir -p gpu-cloud-platform/{backend,frontend,k8s,monitoring,scripts}
    cd gpu-cloud-platform
    
    # Backend structure
    mkdir -p backend/{api,models,services,utils}
    
    # Frontend structure
    mkdir -p frontend/{src/{components,pages,hooks,utils},public}
    
    # Kubernetes manifests
    mkdir -p k8s/{base,overlays/{dev,prod}}
    
    # Monitoring
    mkdir -p monitoring/{prometheus,grafana,alertmanager}
    
    log "✅ Project structure created"
}

# Generate backend API code
generate_backend() {
    log "Generating backend API code..."
    
    # Create requirements.txt
    cat <<EOF > backend/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
kubernetes==28.1.0
redis==5.0.1
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
prometheus-client==0.19.0
psutil==5.9.6
GPUtil==1.4.0
stripe==7.8.0
boto3==1.34.0
asyncpg==0.29.0
EOF
    
    # Create main API file
    cat <<'EOF' > backend/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from api.gpu_instances import router as gpu_router
from api.billing import router as billing_router
from api.monitoring import router as monitoring_router
from services.kubernetes_manager import KubernetesManager
from services.billing_manager import BillingManager

app = FastAPI(
    title="GPU Cloud Platform",
    description="Scalable GPU cloud infrastructure platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(gpu_router, prefix="/api/v1/gpu", tags=["GPU Instances"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["Monitoring"])

@app.on_startup
async def startup_event():
    """Initialize services on startup"""
    print("🚀 Starting GPU Cloud Platform...")
    
    # Initialize Kubernetes manager
    k8s_manager = KubernetesManager()
    app.state.k8s_manager = k8s_manager
    
    # Initialize billing manager
    billing_manager = BillingManager()
    app.state.billing_manager = billing_manager
    
    print("✅ All services initialized")

@app.get("/")
async def root():
    return {
        "message": "🚀 GPU Cloud Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
EOF
    
    log "✅ Backend API code generated"
}

# Generate frontend code
generate_frontend() {
    log "Generating frontend code..."
    
    # Create package.json
    cat <<EOF > frontend/package.json
{
  "name": "gpu-cloud-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18",
    "react-dom": "^18",
    "axios": "^1.6.0",
    "tailwindcss": "^3.3.0",
    "typescript": "^5",
    "@types/react": "^18",
    "@types/node": "^20",
    "socket.io-client": "^4.7.0",
    "recharts": "^2.8.0"
  },
  "devDependencies": {
    "eslint": "^8",
    "eslint-config-next": "14.0.0",
    "autoprefixer": "^10",
    "postcss": "^8"
  }
}
EOF
    
    # Create main page
    cat <<'EOF' > frontend/src/pages/index.tsx
import React, { useState, useEffect } from 'react';
import GPUInstanceManager from '../components/GPUInstanceManager';
import Dashboard from '../components/Dashboard';

const HomePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-2xl font-bold">🚀 GPU Cloud Platform</h1>
        <nav className="mt-4">
          <button
            className={`mr-4 px-4 py-2 rounded ${
              activeTab === 'dashboard' ? 'bg-blue-800' : 'bg-blue-500'
            }`}
            onClick={() => setActiveTab('dashboard')}
          >
            Dashboard
          </button>
          <button
            className={`mr-4 px-4 py-2 rounded ${
              activeTab === 'instances' ? 'bg-blue-800' : 'bg-blue-500'
            }`}
            onClick={() => setActiveTab('instances')}
          >
            Instances
          </button>
        </nav>
      </header>
      
      <main className="container mx-auto p-4">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'instances' && <GPUInstanceManager />}
      </main>
    </div>
  );
};

export default HomePage;
EOF
    
    log "✅ Frontend code generated"
}

# Generate Kubernetes manifests
generate_k8s_manifests() {
    log "Generating Kubernetes manifests..."
    
    # Create namespace
    cat <<EOF > k8s/base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gpu-cloud
EOF
    
    # Backend deployment
    cat <<EOF > k8s/base/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-cloud-backend
  namespace: gpu-cloud
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gpu-cloud-backend
  template:
    metadata:
      labels:
        app: gpu-cloud-backend
    spec:
      containers:
      - name: backend
        image: gpu-cloud-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@postgres:5432/gpucloud"
        - name: REDIS_URL
          value: "redis://redis:6379"
EOF
    
    # Backend service
    cat <<EOF > k8s/base/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: gpu-cloud-backend-service
  namespace: gpu-cloud
spec:
  selector:
    app: gpu-cloud-backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: NodePort
EOF
    
    log "✅ Kubernetes manifests generated"
}

# Generate monitoring configuration
generate_monitoring() {
    log "Generating monitoring configuration..."
    
    # Prometheus configuration
    cat <<EOF > monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'gpu-cloud-backend'
    static_configs:
      - targets: ['gpu-cloud-backend-service:8000']
    metrics_path: '/metrics'
    
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
      
  - job_name: 'gpu-metrics'
    static_configs:
      - targets: ['nvidia-dcgm-exporter:9400']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF
    
    # Docker compose for development
    cat <<EOF > docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/gpucloud
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ~/.kube:/root/.kube
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: gpucloud
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  grafana_data:
EOF
    
    log "✅ Monitoring configuration generated"
}

# Generate Dockerfiles
generate_dockerfiles() {
    log "Generating Dockerfiles..."
    
    # Backend Dockerfile
    cat <<EOF > backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/\$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \\
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    
    # Frontend Dockerfile
    cat <<EOF > frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
EOF
    
    log "✅ Dockerfiles generated"
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat <<'EOF' > start.sh
#!/bin/bash

echo "🚀 Starting GPU Cloud Platform..."

# Check if kind cluster exists
if ! kind get clusters | grep -q gpu-cloud; then
    echo "❌ Kind cluster 'gpu-cloud' not found. Please run setup first."
    exit 1
fi

# Set kubectl context
kubectl cluster-info --context kind-gpu-cloud

# Start development environment
echo "Starting development environment with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check service status
echo "Checking service status..."
docker-compose ps

echo "✅ GPU Cloud Platform is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3001 (admin/admin)"
echo ""
echo "To stop: docker-compose down"
EOF
    
    chmod +x start.sh
    
    log "✅ Startup script created"
}

# Main installation flow
main() {
    log "Starting GPU Cloud Platform setup..."
    
    check_requirements
    install_nvidia_docker
    install_kubernetes
    create_project_structure
    generate_backend
    generate_frontend
    generate_k8s_manifests
    generate_monitoring
    generate_dockerfiles
    create_startup_script
    
    echo ""
    echo -e "${GREEN}🎉 GPU Cloud Platform setup completed!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. cd gpu-cloud-platform"
    echo "2. ./start.sh"
    echo ""
    echo -e "${BLUE}Development URLs:${NC}"
    echo "• Frontend: http://localhost:3000"
    echo "• Backend API: http://localhost:8000"
    echo "• API Docs: http://localhost:8000/docs"
    echo "• Prometheus: http://localhost:9090"
    echo "• Grafana: http://localhost:3001"
    echo ""
    echo -e "${YELLOW}Remember to:${NC}"
    echo "• Configure your domain and SSL certificates for production"
    echo "• Set up proper authentication and authorization"
    echo "• Configure payment processing (Stripe, PayPal)"
    echo "• Set up backup and disaster recovery"
    echo "• Monitor resource usage and costs"
    echo ""
    echo -e "${GREEN}Happy building! 🚀${NC}"
}

# Run main function
main "$@"
