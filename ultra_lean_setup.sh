#!/bin/bash
# ultra_lean_setup.sh - Minimal setup for two-person GPU cloud platform

set -e

echo "🚀 Ultra-Lean GPU Cloud Setup - Just You & Me!"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"; }
info() { echo -e "${BLUE}[INFO] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; exit 1; }

# Check if we're on a fresh server
check_environment() {
    log "Checking environment..."
    
    if [ "$EUID" -eq 0 ]; then
        error "Don't run as root! Create a user account first."
    fi
    
    # Check for GPU
    if ! command -v nvidia-smi &> /dev/null; then
        warn "NVIDIA drivers not detected. Install them first!"
    fi
    
    log "✅ Environment check passed"
}

# Install essential tools only
install_essentials() {
    log "Installing essential tools..."
    
    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Essential packages
    sudo apt install -y \
        curl \
        wget \
        git \
        htop \
        ufw \
        fail2ban \
        certbot \
        python3-pip \
        python3-venv \
        nginx
    
    # Docker (lightweight installation)
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com | sh
        sudo usermod -aG docker $USER
        log "✅ Docker installed - please logout and login again"
    fi
    
    # Node.js (for frontend)
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
    
    log "✅ Essential tools installed"
}

# Setup lightweight Kubernetes (k3s)
install_k3s() {
    log "Installing k3s (lightweight Kubernetes)..."
    
    if ! command -v k3s &> /dev/null; then
        curl -sfL https://get.k3s.io | sh -
        sudo chmod 644 /etc/rancher/k3s/k3s.yaml
        echo 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml' >> ~/.bashrc
    fi
    
    log "✅ k3s installed"
}

# NVIDIA Container support
setup_nvidia_support() {
    log "Setting up NVIDIA container support..."
    
    # NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
        sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    
    sudo apt update
    sudo apt install -y nvidia-docker2
    sudo systemctl restart docker
    
    # Test NVIDIA Docker
    if docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
        log "✅ NVIDIA Docker working"
    else
        warn "NVIDIA Docker test failed - check GPU setup"
    fi
}

# Create minimal project structure
create_project() {
    log "Creating ultra-lean project structure..."
    
    mkdir -p gpu-cloud-lean/{backend,frontend,scripts,configs}
    cd gpu-cloud-lean
    
    # Backend structure
    mkdir -p backend/{api,models,utils}
    
    # Frontend structure  
    mkdir -p frontend/{src/{pages,components,hooks},public}
    
    # Config structure
    mkdir -p configs/{nginx,k3s,monitoring}
    
    log "✅ Project structure created"
}

# Generate ultra-minimal backend
generate_minimal_backend() {
    log "Generating minimal backend..."
    
    # Requirements (absolute minimum)
    cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.5.0
sqlite3
stripe==7.8.0
psutil==5.9.6
GPUtil==1.4.0
kubernetes==28.1.0
EOF

    # Ultra-minimal API
    cat > backend/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3
import os
import subprocess
import json
from datetime import datetime

app = FastAPI(title="GPU Cloud Lean", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple SQLite database
DB_PATH = "gpu_cloud.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS instances (
            id INTEGER PRIMARY KEY,
            user_email TEXT,
            status TEXT,
            gpu_type TEXT,
            hourly_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users (email)
        )
    ''')
    conn.commit()
    conn.close()

@app.on_startup
async def startup_event():
    init_db()
    print("🚀 GPU Cloud Lean API Started!")

@app.get("/")
async def root():
    return {"message": "🚀 GPU Cloud Lean API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/instances")
async def create_instance(user_email: str, gpu_type: str = "rtx4090"):
    try:
        # Simple instance creation (placeholder)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO instances (user_email, status, gpu_type, hourly_rate) VALUES (?, ?, ?, ?)",
            (user_email, "starting", gpu_type, 0.90)
        )
        instance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "instance_id": instance_id,
            "status": "starting",
            "gpu_type": gpu_type,
            "hourly_rate": 0.90
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instances")
async def list_instances(user_email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM instances WHERE user_email = ?", (user_email,)
    )
    instances = cursor.fetchall()
    conn.close()
    
    return {"instances": instances}

@app.get("/stats")
async def get_stats():
    try:
        # Simple GPU stats
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        gpu_stats = result.stdout.strip().split('\n')
        
        return {
            "gpu_count": len(gpu_stats),
            "gpu_stats": gpu_stats,
            "timestamp": datetime.now()
        }
    except:
        return {"error": "GPU stats unavailable"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

    # Simple startup script
    cat > backend/start.sh << 'EOF'
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
EOF
    chmod +x backend/start.sh

    log "✅ Minimal backend generated"
}

# Generate ultra-simple frontend
generate_minimal_frontend() {
    log "Generating minimal frontend..."
    
    # Package.json (minimal)
    cat > frontend/package.json << 'EOF'
{
  "name": "gpu-cloud-lean-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.0.0",
    "react": "^18",
    "react-dom": "^18",
    "axios": "^1.6.0"
  }
}
EOF

    # Simple homepage
    mkdir -p frontend/src/pages
    cat > frontend/src/pages/index.js << 'EOF'
import { useState, useEffect } from 'react';
import axios from 'axios';

export default function Home() {
  const [instances, setInstances] = useState([]);
  const [email, setEmail] = useState('');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const createInstance = async () => {
    if (!email) return alert('Please enter your email');
    
    try {
      const response = await axios.post('http://localhost:8000/instances', null, {
        params: { user_email: email }
      });
      alert('Instance created: ' + response.data.instance_id);
      fetchInstances();
    } catch (error) {
      alert('Failed to create instance');
    }
  };

  const fetchInstances = async () => {
    if (!email) return;
    
    try {
      const response = await axios.get('http://localhost:8000/instances', {
        params: { user_email: email }
      });
      setInstances(response.data.instances);
    } catch (error) {
      console.error('Failed to fetch instances:', error);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🚀 GPU Cloud Lean</h1>
      <p>Ultra-simple GPU cloud platform</p>
      
      <div style={{ marginBottom: '20px' }}>
        <h2>📊 GPU Stats</h2>
        {stats && (
          <div>
            <p>GPUs Available: {stats.gpu_count}</p>
            <p>Last Updated: {new Date(stats.timestamp).toLocaleString()}</p>
          </div>
        )}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h2>🎮 Create GPU Instance</h2>
        <input
          type="email"
          placeholder="Your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: '10px', marginRight: '10px', width: '200px' }}
        />
        <button 
          onClick={createInstance}
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer'
          }}
        >
          Create RTX 4090 Instance ($0.90/hour)
        </button>
      </div>

      <div>
        <h2>📋 Your Instances</h2>
        <button 
          onClick={fetchInstances}
          style={{ padding: '5px 10px', marginBottom: '10px' }}
        >
          Refresh
        </button>
        {instances.length > 0 ? (
          <ul>
            {instances.map((instance, index) => (
              <li key={index}>
                Instance {instance[0]} - {instance[2]} - ${instance[4]}/hour
              </li>
            ))}
          </ul>
        ) : (
          <p>No instances found. Enter your email and create one!</p>
        )}
      </div>
    </div>
  );
}
EOF

    # Next.js config
    cat > frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
EOF

    log "✅ Minimal frontend generated"
}

# Setup basic NGINX
setup_nginx() {
    log "Setting up NGINX..."
    
    cat > configs/nginx/gpu-cloud.conf << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

    sudo cp configs/nginx/gpu-cloud.conf /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/gpu-cloud.conf /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx

    log "✅ NGINX configured"
}

# Create startup script
create_startup_script() {
    log "Creating startup script..."
    
    cat > start-lean.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting GPU Cloud Lean Platform..."

# Start backend
echo "Starting backend API..."
cd backend
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Platform started!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: kill $BACKEND_PID $FRONTEND_PID"
echo "PIDs saved to .pids file"
echo "$BACKEND_PID $FRONTEND_PID" > .pids
EOF

    chmod +x start-lean.sh

    # Stop script
    cat > stop-lean.sh << 'EOF'
#!/bin/bash
if [ -f .pids ]; then
    kill $(cat .pids) 2>/dev/null || true
    rm .pids
    echo "✅ Platform stopped"
else
    echo "No running platform found"
fi
EOF

    chmod +x stop-lean.sh

    log "✅ Startup scripts created"
}

# Generate deployment guide
create_deployment_guide() {
    log "Creating deployment guide..."
    
    cat > ULTRA_LEAN_GUIDE.md << 'EOF'
# 🚀 Ultra-Lean GPU Cloud - Deployment Guide

## Quick Start (5 minutes)

### 1. Start the platform
```bash
./start-lean.sh
```

### 2. Access the platform
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Test it
- Enter your email
- Click "Create RTX 4090 Instance"
- Check your instances

## Cost Breakdown

### Monthly Costs
- Hetzner RTX 4090 Server: €169 (~$180)
- Domain + SSL: $5
- Monitoring: $0 (self-hosted)
- **Total: $185/month**

### Revenue Potential
- RTX 4090 @ $0.90/hour
- 50% utilization = 365 hours/month
- Revenue: 365 × $0.90 = $328/month
- **Profit: $143/month (77% margin)**

## Scaling Plan

### Month 1-3: Prove concept
- 1 server, basic features
- Manual customer support
- Target: $300-500/month revenue

### Month 4-6: Add features
- Automated billing
- Better UI/UX
- Second server
- Target: $1,000-2,000/month

### Month 7-12: Scale up
- Multi-GPU support
- Enterprise features
- Marketing push
- Target: $5,000-10,000/month

## Next Steps

1. **Domain Setup**: Buy domain, point to server
2. **SSL Setup**: `sudo certbot --nginx -d yourdomain.com`
3. **Payment Integration**: Add Stripe webhook
4. **Monitoring**: Set up basic alerts
5. **Marketing**: Start with AI/ML communities

## Support

- Check logs: `journalctl -u gpu-cloud`
- Monitor resources: `htop`, `nvidia-smi`
- Restart services: `./stop-lean.sh && ./start-lean.sh`

---

**Remember**: Start small, prove concept, scale fast! 🚀
EOF

    log "✅ Deployment guide created"
}

# Main installation
main() {
    log "Starting ultra-lean GPU cloud setup..."
    
    check_environment
    install_essentials
    install_k3s
    setup_nvidia_support
    create_project
    generate_minimal_backend
    generate_minimal_frontend
    setup_nginx
    create_startup_script
    create_deployment_guide
    
    echo ""
    echo -e "${GREEN}🎉 Ultra-Lean GPU Cloud Setup Complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. cd gpu-cloud-lean"
    echo "2. ./start-lean.sh"
    echo "3. Open http://localhost:3000"
    echo ""
    echo -e "${YELLOW}Total setup cost: $185/month${NC}"
    echo -e "${GREEN}Potential profit: $143/month from day 1!${NC}"
    echo ""
    echo -e "${BLUE}Ready to dominate the GPU cloud market? 🚀${NC}"
}

main "$@"
