#!/bin/bash

# =============================================================================
# AI Video GPU - Complete Build and Deployment Script
# Automated build, test, and deployment with monitoring
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/deployment_$TIMESTAMP.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="development"
SKIP_TESTS=false
SKIP_BUILD=false
SKIP_DEPLOY=false
VERBOSE=false
GPU_ENABLED=true
MONITORING_ENABLED=true

# Functions
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
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

usage() {
    cat << EOF
AI Video GPU - Complete Build and Deployment Script

Usage: $0 [OPTIONS]

OPTIONS:
    -e, --environment ENV     Target environment (development|staging|production) [default: development]
    -t, --skip-tests         Skip test execution
    -b, --skip-build         Skip container build
    -d, --skip-deploy        Skip deployment
    -v, --verbose            Enable verbose output
    --no-gpu                 Disable GPU support
    --no-monitoring          Disable monitoring
    -h, --help              Show this help message

EXAMPLES:
    $0                                          # Build and deploy to development
    $0 -e staging                               # Deploy to staging
    $0 -e production --skip-tests               # Deploy to production without tests
    $0 --skip-deploy                            # Only build, don't deploy
    $0 -v --no-gpu                             # Verbose mode without GPU

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -b|--skip-build)
            SKIP_BUILD=true
            shift
            ;;
        -d|--skip-deploy)
            SKIP_DEPLOY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-gpu)
            GPU_ENABLED=false
            shift
            ;;
        --no-monitoring)
            MONITORING_ENABLED=false
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

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    log_error "Invalid environment: $ENVIRONMENT"
    exit 1
fi

# Setup
setup() {
    log_info "Setting up build environment..."
    
    # Create directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$PROJECT_ROOT/outputs"
    mkdir -p "$PROJECT_ROOT/temp"
    
    # Check dependencies
    command -v docker >/dev/null 2>&1 || { log_error "Docker is required but not installed."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { log_error "Docker Compose is required but not installed."; exit 1; }
    
    if [[ "$GPU_ENABLED" == true ]]; then
        if ! docker info | grep -q "nvidia"; then
            log_warning "NVIDIA Docker runtime not detected. GPU support may not work."
        fi
    fi
    
    log_success "Setup completed"
}

# Pre-flight checks
preflight_checks() {
    log_info "Running pre-flight checks..."
    
    # Check disk space
    AVAILABLE_SPACE=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [[ $AVAILABLE_SPACE -lt 10000000 ]]; then  # 10GB
        log_warning "Low disk space available: ${AVAILABLE_SPACE}KB"
    fi
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Validate configuration files
    if [[ ! -f "$PROJECT_ROOT/docker-compose.prebuilt.yml" ]]; then
        log_error "Docker Compose file not found"
        exit 1
    fi
    
    # Validate Docker Compose configuration
    if ! docker-compose -f "$PROJECT_ROOT/docker-compose.prebuilt.yml" config >/dev/null; then
        log_error "Invalid Docker Compose configuration"
        exit 1
    fi
    
    log_success "Pre-flight checks passed"
}

# Code quality checks
code_quality() {
    log_info "Running code quality checks..."
    
    cd "$PROJECT_ROOT"
    
    # Python linting
    if command -v flake8 >/dev/null 2>&1; then
        log_info "Running flake8..."
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics || {
            log_warning "Flake8 found issues"
        }
    fi
    
    # Code formatting
    if command -v black >/dev/null 2>&1; then
        log_info "Checking code formatting..."
        black --check src/ || {
            log_warning "Code formatting issues found"
        }
    fi
    
    # Security checks
    if command -v bandit >/dev/null 2>&1; then
        log_info "Running security analysis..."
        bandit -r src/ -f json -o "$LOG_DIR/bandit_$TIMESTAMP.json" || {
            log_warning "Security issues found, check bandit report"
        }
    fi
    
    log_success "Code quality checks completed"
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == true ]]; then
        log_info "Skipping tests as requested"
        return 0
    fi
    
    log_info "Running test suite..."
    
    cd "$PROJECT_ROOT"
    
    # Unit tests
    log_info "Running unit tests..."
    python -m pytest tests/unit/ -v --tb=short || {
        log_error "Unit tests failed"
        return 1
    }
    
    # Integration tests
    log_info "Running integration tests..."
    python -m pytest tests/integration/ -v --tb=short || {
        log_error "Integration tests failed"
        return 1
    }
    
    # API tests
    log_info "Running API tests..."
    python -m pytest tests/api/ -v --tb=short || {
        log_error "API tests failed"
        return 1
    }
    
    log_success "All tests passed"
}

# Build containers
build_containers() {
    if [[ "$SKIP_BUILD" == true ]]; then
        log_info "Skipping build as requested"
        return 0
    fi
    
    log_info "Building containers..."
    
    cd "$PROJECT_ROOT"
    
    # Build main application container
    log_info "Building AI Video GPU container..."
    if [[ "$VERBOSE" == true ]]; then
        docker build -f docker/Dockerfile.prebuilt -t ai-video-gpu:latest . --progress=plain
    else
        docker build -f docker/Dockerfile.prebuilt -t ai-video-gpu:latest . >/dev/null
    fi
    
    # Tag for environment
    docker tag ai-video-gpu:latest "ai-video-gpu:$ENVIRONMENT"
    docker tag ai-video-gpu:latest "ai-video-gpu:$TIMESTAMP"
    
    log_success "Container build completed"
}

# Security scanning
security_scan() {
    log_info "Running security scans..."
    
    # Container vulnerability scanning
    if command -v trivy >/dev/null 2>&1; then
        log_info "Scanning container for vulnerabilities..."
        trivy image --format json --output "$LOG_DIR/trivy_$TIMESTAMP.json" ai-video-gpu:latest || {
            log_warning "Vulnerabilities found, check trivy report"
        }
    fi
    
    log_success "Security scans completed"
}

# Deploy services
deploy() {
    if [[ "$SKIP_DEPLOY" == true ]]; then
        log_info "Skipping deployment as requested"
        return 0
    fi
    
    log_info "Deploying to $ENVIRONMENT environment..."
    
    cd "$PROJECT_ROOT"
    
    # Set environment variables
    export ENVIRONMENT="$ENVIRONMENT"
    export GPU_ENABLED="$GPU_ENABLED"
    export MONITORING_ENABLED="$MONITORING_ENABLED"
    
    # Deploy based on environment
    case "$ENVIRONMENT" in
        development)
            log_info "Starting development environment..."
            docker-compose -f docker-compose.prebuilt.yml up -d
            ;;
        staging)
            log_info "Deploying to staging..."
            docker-compose -f docker-compose.prebuilt.yml -f docker-compose.staging.yml up -d
            ;;
        production)
            log_info "Deploying to production..."
            docker-compose -f docker-compose.prebuilt.yml -f docker-compose.production.yml up -d
            ;;
    esac
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Health checks
    health_check
    
    log_success "Deployment completed"
}

# Health checks
health_check() {
    log_info "Running health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            log_success "Application is healthy"
            return 0
        fi
        
        log_info "Health check attempt $attempt/$max_attempts failed, retrying..."
        sleep 10
        ((attempt++))
    done
    
    log_error "Health checks failed after $max_attempts attempts"
    return 1
}

# Performance tests
performance_test() {
    if [[ "$ENVIRONMENT" != "production" ]]; then
        log_info "Skipping performance tests (not production environment)"
        return 0
    fi
    
    log_info "Running performance tests..."
    
    # Simple load test
    if command -v ab >/dev/null 2>&1; then
        log_info "Running Apache Bench load test..."
        ab -n 100 -c 10 http://localhost:8000/health > "$LOG_DIR/performance_$TIMESTAMP.txt"
    fi
    
    log_success "Performance tests completed"
}

# Monitoring setup
setup_monitoring() {
    if [[ "$MONITORING_ENABLED" != true ]]; then
        log_info "Monitoring disabled"
        return 0
    fi
    
    log_info "Setting up monitoring..."
    
    # Check if monitoring services are running
    if docker-compose -f docker-compose.prebuilt.yml ps prometheus | grep -q "Up"; then
        log_info "Prometheus is running"
    else
        log_warning "Prometheus is not running"
    fi
    
    if docker-compose -f docker-compose.prebuilt.yml ps grafana | grep -q "Up"; then
        log_info "Grafana is running"
    else
        log_warning "Grafana is not running"
    fi
    
    log_success "Monitoring setup completed"
}

# Cleanup
cleanup() {
    log_info "Running cleanup..."
    
    # Clean up old containers
    docker image prune -f >/dev/null 2>&1 || true
    
    # Clean up old logs (keep last 30 days)
    find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Generate report
generate_report() {
    log_info "Generating deployment report..."
    
    local report_file="$LOG_DIR/deployment_report_$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# AI Video GPU Deployment Report

- **Date**: $(date)
- **Environment**: $ENVIRONMENT
- **Version**: $(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
- **GPU Enabled**: $GPU_ENABLED
- **Monitoring Enabled**: $MONITORING_ENABLED

## Services Status

$(docker-compose -f docker-compose.prebuilt.yml ps)

## Health Check

$(curl -s http://localhost:8000/health 2>/dev/null || echo "Health check failed")

## System Resources

### Memory Usage
$(free -h)

### Disk Usage
$(df -h)

### Docker Images
$(docker images | grep ai-video-gpu)

## Logs Location

- Main log: $LOG_FILE
- Report: $report_file

EOF
    
    log_info "Report generated: $report_file"
}

# Rollback function
rollback() {
    log_warning "Rolling back deployment..."
    
    # Stop current deployment
    docker-compose -f docker-compose.prebuilt.yml down
    
    # TODO: Implement proper rollback logic
    # This would typically involve:
    # 1. Restoring previous container version
    # 2. Restoring database backup
    # 3. Updating load balancer
    
    log_info "Rollback completed"
}

# Signal handlers
trap 'log_error "Script interrupted"; cleanup; exit 130' INT TERM

# Main execution
main() {
    log_info "Starting AI Video GPU deployment pipeline..."
    log_info "Environment: $ENVIRONMENT"
    log_info "GPU Enabled: $GPU_ENABLED"
    log_info "Monitoring Enabled: $MONITORING_ENABLED"
    
    setup
    preflight_checks
    code_quality
    
    if ! run_tests; then
        log_error "Tests failed, aborting deployment"
        exit 1
    fi
    
    build_containers
    security_scan
    
    if ! deploy; then
        log_error "Deployment failed, consider rollback"
        exit 1
    fi
    
    performance_test
    setup_monitoring
    generate_report
    cleanup
    
    log_success "Deployment pipeline completed successfully!"
    log_info "Access the application at: http://localhost:8000"
    log_info "Access Grafana at: http://localhost:3000 (admin/aivideoadmin)"
    log_info "Access Flower at: http://localhost:5555"
}

# Run main function
main "$@"
