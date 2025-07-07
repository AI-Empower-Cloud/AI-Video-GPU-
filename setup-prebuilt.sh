#!/bin/bash

# =============================================================================
# AI Video GPU - Quick Setup Script
# One-command setup for the complete AI Video GPU system
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SETUP_LOG="$PROJECT_ROOT/setup.log"

# Default options
ENVIRONMENT="development"
SKIP_GPU_CHECK=false
SKIP_DEPENDENCIES=false
AUTO_START=true
VERBOSE=false

# Functions
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$SETUP_LOG"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo -e "${BLUE}${BOLD}"
    cat << 'EOF'
    ___    ____   _    ___     __              ______  ____  __  __
   /   |  /  _/  | |  / (_)___/ /__  ____     / ____/ / __ \/ / / /
  / /| |  / /    | | / / / __  / _ \/ __ \   / / __  / /_/ / / / / 
 / ___ |_/ /     | |/ / / /_/ /  __/ /_/ /  / /_/ / / ____/ /_/ /  
/_/  |_/___/     |___/_/\__,_/\___/\____/   \____/ /_/    \____/   

        Production-Ready GPU-Accelerated AI Video Generation
                           Complete Setup Script
EOF
    echo -e "${NC}"
}

usage() {
    cat << EOF
AI Video GPU - Quick Setup Script

Usage: $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV    Target environment (development|staging|production) [default: development]
    --skip-gpu-check        Skip GPU availability check
    --skip-dependencies     Skip system dependencies installation
    --no-start             Don't auto-start services after setup
    -v, --verbose          Enable verbose output
    -h, --help             Show this help message

EXAMPLES:
    $0                      # Quick setup for development
    $0 -e production        # Setup for production environment
    $0 --skip-gpu-check     # Setup without GPU requirement
    $0 -v                   # Verbose setup

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-gpu-check)
            SKIP_GPU_CHECK=true
            shift
            ;;
        --skip-dependencies)
            SKIP_DEPENDENCIES=true
            shift
            ;;
        --no-start)
            AUTO_START=false
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# System detection
detect_system() {
    log_info "Detecting system configuration..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get >/dev/null 2>&1; then
            DISTRO="ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            DISTRO="rhel"
        elif command -v pacman >/dev/null 2>&1; then
            DISTRO="arch"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        OS="unknown"
        DISTRO="unknown"
    fi
    
    log_info "Detected OS: $OS ($DISTRO)"
    
    # Detect architecture
    ARCH=$(uname -m)
    log_info "Detected architecture: $ARCH"
    
    # Check if running in container
    if [[ -f /.dockerenv ]]; then
        log_info "Running inside Docker container"
        SKIP_DEPENDENCIES=true
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    local requirements_met=true
    
    # Check Python
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        log_success "Python found: $(python3 --version)"
        if [[ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" != "3.9" ]]; then
            log_warning "Python 3.9+ recommended, found $python_version"
        fi
    else
        log_error "Python 3 not found"
        requirements_met=false
    fi
    
    # Check Docker
    if command -v docker >/dev/null 2>&1; then
        log_success "Docker found: $(docker --version)"
        
        # Check if Docker daemon is running
        if ! docker info >/dev/null 2>&1; then
            log_error "Docker daemon is not running"
            requirements_met=false
        fi
    else
        log_error "Docker not found"
        requirements_met=false
    fi
    
    # Check Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        log_success "Docker Compose found: $(docker-compose --version)"
    else
        log_error "Docker Compose not found"
        requirements_met=false
    fi
    
    # Check GPU (if not skipped)
    if [[ "$SKIP_GPU_CHECK" != true ]]; then
        if command -v nvidia-smi >/dev/null 2>&1; then
            log_success "NVIDIA GPU detected:"
            nvidia-smi --query-gpu=name,memory.total --format=csv,noheader | head -1
            
            # Check NVIDIA Docker runtime
            if docker info 2>/dev/null | grep -q "nvidia"; then
                log_success "NVIDIA Docker runtime detected"
            else
                log_warning "NVIDIA Docker runtime not detected"
                log_warning "GPU features may not work properly"
            fi
        else
            log_warning "NVIDIA GPU not detected"
            log_warning "System will run in CPU-only mode"
        fi
    fi
    
    # Check disk space
    local available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    local required_space=20971520  # 20GB in KB
    
    if [[ $available_space -lt $required_space ]]; then
        log_error "Insufficient disk space. Required: 20GB, Available: $((available_space/1024/1024))GB"
        requirements_met=false
    else
        log_success "Sufficient disk space available: $((available_space/1024/1024))GB"
    fi
    
    # Check memory
    if [[ "$OS" == "linux" ]]; then
        local total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        local required_mem=8388608  # 8GB in KB
        
        if [[ $total_mem -lt $required_mem ]]; then
            log_warning "Low memory detected. Required: 8GB, Available: $((total_mem/1024/1024))GB"
        else
            log_success "Sufficient memory available: $((total_mem/1024/1024))GB"
        fi
    fi
    
    if [[ "$requirements_met" != true ]]; then
        log_error "System requirements not met. Please install missing dependencies."
        exit 1
    fi
    
    log_success "All system requirements met"
}

# Install system dependencies
install_dependencies() {
    if [[ "$SKIP_DEPENDENCIES" == true ]]; then
        log_info "Skipping dependency installation"
        return 0
    fi
    
    log_info "Installing system dependencies..."
    
    case "$DISTRO" in
        ubuntu)
            log_info "Installing Ubuntu dependencies..."
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                wget \
                git \
                build-essential \
                python3-pip \
                python3-venv \
                ffmpeg \
                libgl1-mesa-glx \
                libglib2.0-0 \
                libsm6 \
                libxext6 \
                libxrender-dev \
                libgomp1
            ;;
        rhel)
            log_info "Installing RHEL/CentOS dependencies..."
            sudo yum update -y
            sudo yum install -y \
                curl \
                wget \
                git \
                gcc \
                gcc-c++ \
                python3-pip \
                ffmpeg \
                mesa-libGL \
                glib2 \
                libSM \
                libXext \
                libXrender \
                libgomp
            ;;
        macos)
            log_info "Installing macOS dependencies..."
            if command -v brew >/dev/null 2>&1; then
                brew install ffmpeg
            else
                log_warning "Homebrew not found. Please install FFmpeg manually."
            fi
            ;;
        *)
            log_warning "Unknown distribution. Please install dependencies manually."
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Setup Python environment
setup_python() {
    log_info "Setting up Python environment..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install requirements
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    log_success "Python environment setup completed"
}

# Setup configuration
setup_configuration() {
    log_info "Setting up configuration files..."
    
    cd "$PROJECT_ROOT"
    
    # Create config directory if it doesn't exist
    mkdir -p config
    
    # Create environment-specific config
    local config_file="config/${ENVIRONMENT}.yml"
    
    if [[ ! -f "$config_file" ]]; then
        log_info "Creating configuration file: $config_file"
        
        cat > "$config_file" << EOF
# AI Video GPU Configuration - $ENVIRONMENT
environment: $ENVIRONMENT

# API Settings
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: $([ "$ENVIRONMENT" = "development" ] && echo "true" || echo "false")

# GPU Settings
gpu:
  enabled: true
  device_ids: [0]
  memory_fraction: 0.8

# Model Settings
models:
  cache_dir: /app/models
  download_timeout: 300
  preload: true

# Storage Settings
storage:
  output_dir: /app/outputs
  temp_dir: /app/temp
  max_file_size: 1073741824  # 1GB

# Monitoring
monitoring:
  enabled: true
  metrics_port: 9090
  log_level: $([ "$ENVIRONMENT" = "development" ] && echo "DEBUG" || echo "INFO")

# Security
security:
  secret_key: $(openssl rand -hex 32)
  token_expire_hours: 24
  cors_origins: ["*"]

EOF
        log_success "Configuration file created: $config_file"
    else
        log_info "Configuration file already exists: $config_file"
    fi
}

# Build containers
build_containers() {
    log_info "Building AI Video GPU containers..."
    
    cd "$PROJECT_ROOT"
    
    # Build the prebuilt container
    log_info "Building prebuilt container..."
    if [[ "$VERBOSE" == true ]]; then
        docker build -f docker/Dockerfile.prebuilt -t ai-video-gpu:latest . --progress=plain
    else
        docker build -f docker/Dockerfile.prebuilt -t ai-video-gpu:latest .
    fi
    
    # Tag for environment
    docker tag ai-video-gpu:latest "ai-video-gpu:$ENVIRONMENT"
    
    log_success "Container build completed"
}

# Initialize database
init_database() {
    log_info "Initializing database..."
    
    cd "$PROJECT_ROOT"
    
    # Start only PostgreSQL first
    docker-compose -f docker-compose.prebuilt.yml up -d postgres
    
    # Wait for PostgreSQL to be ready
    local attempts=30
    while [[ $attempts -gt 0 ]]; do
        if docker exec ai-video-postgres pg_isready -U aivideo >/dev/null 2>&1; then
            break
        fi
        log_info "Waiting for PostgreSQL to be ready... ($attempts attempts left)"
        sleep 2
        ((attempts--))
    done
    
    if [[ $attempts -eq 0 ]]; then
        log_error "PostgreSQL failed to start"
        return 1
    fi
    
    log_success "Database initialized"
}

# Start services
start_services() {
    if [[ "$AUTO_START" != true ]]; then
        log_info "Skipping service startup (--no-start specified)"
        return 0
    fi
    
    log_info "Starting AI Video GPU services..."
    
    cd "$PROJECT_ROOT"
    
    # Start all services
    docker-compose -f docker-compose.prebuilt.yml up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Health check
    local attempts=30
    while [[ $attempts -gt 0 ]]; do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            log_success "AI Video GPU API is ready"
            break
        fi
        log_info "Waiting for API to be ready... ($attempts attempts left)"
        sleep 5
        ((attempts--))
    done
    
    if [[ $attempts -eq 0 ]]; then
        log_warning "API health check failed, but services are running"
    fi
    
    log_success "All services started"
}

# Show setup summary
show_summary() {
    log_success "AI Video GPU setup completed!"
    
    cat << EOF

${GREEN}${BOLD}🎉 Setup Complete!${NC}

${BLUE}${BOLD}Environment:${NC} $ENVIRONMENT
${BLUE}${BOLD}Project Directory:${NC} $PROJECT_ROOT

${BLUE}${BOLD}Available Services:${NC}
• Main API:        http://localhost:8000
• Web Interface:   http://localhost:8080  
• Gradio UI:       http://localhost:8501
• API Docs:        http://localhost:8000/docs
• Grafana:         http://localhost:3000 (admin/aivideoadmin)
• Prometheus:      http://localhost:9090
• Flower:          http://localhost:5555

${BLUE}${BOLD}Management Commands:${NC}
• View logs:       ./scripts/orchestrate.sh logs
• Check health:    ./scripts/orchestrate.sh health
• Stop services:   ./scripts/orchestrate.sh stop
• Restart:         ./scripts/orchestrate.sh restart
• Open shell:      ./scripts/orchestrate.sh shell

${BLUE}${BOLD}Quick Start:${NC}
1. Test the API:   curl http://localhost:8000/health
2. Open Gradio:    Visit http://localhost:8501
3. Generate video: Use the web interface or API
4. Check logs:     ./scripts/orchestrate.sh logs -s ai-video-gpu

${BLUE}${BOLD}Documentation:${NC}
• README.md
• INTEGRATION_GUIDE.md
• use_cases/ directory

${YELLOW}Setup log saved to: $SETUP_LOG${NC}

EOF
}

# Main setup function
main() {
    print_banner
    
    log_info "Starting AI Video GPU setup..."
    log_info "Environment: $ENVIRONMENT"
    log_info "Project root: $PROJECT_ROOT"
    
    detect_system
    check_requirements
    install_dependencies
    setup_python
    setup_configuration
    build_containers
    init_database
    start_services
    show_summary
    
    log_success "Setup completed successfully!"
}

# Error handling
trap 'log_error "Setup failed at line $LINENO"; exit 1' ERR

# Run main setup
main "$@"
