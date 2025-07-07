#!/bin/bash

# =============================================================================
# AI Video GPU - Container Orchestration Script
# Manages the complete containerized AI Video GPU system
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
COMPOSE_FILE="docker-compose.prebuilt.yml"
ENVIRONMENT="development"
ACTION=""
SERVICES=""
VERBOSE=false

# Functions
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') - $1"
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
AI Video GPU - Container Orchestration Script

Usage: $0 ACTION [OPTIONS]

ACTIONS:
    start               Start all services
    stop                Stop all services
    restart             Restart all services
    build               Build all containers
    pull                Pull latest images
    logs                Show logs for services
    status              Show status of all services
    health              Check health of all services
    shell               Open shell in main container
    exec                Execute command in container
    clean               Clean up containers and volumes
    backup              Backup persistent data
    restore             Restore from backup
    scale               Scale services
    update              Update services to latest version
    monitor             Open monitoring dashboard

OPTIONS:
    -e, --environment ENV    Environment (development|staging|production) [default: development]
    -s, --services SERVICES  Specific services to target (comma-separated)
    -f, --file FILE         Custom compose file [default: docker-compose.prebuilt.yml]
    -v, --verbose           Enable verbose output
    -h, --help             Show this help message

EXAMPLES:
    $0 start                                    # Start all services
    $0 stop -s ai-video-gpu,redis              # Stop specific services
    $0 logs -s ai-video-gpu                    # Show logs for main app
    $0 scale -s ai-video-gpu=3                 # Scale main app to 3 replicas
    $0 exec -s ai-video-gpu "python --version" # Execute command in container
    $0 backup                                   # Backup all data
    $0 health                                   # Check all service health

EOF
}

# Parse command line arguments
if [[ $# -eq 0 ]]; then
    usage
    exit 1
fi

ACTION="$1"
shift

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--services)
            SERVICES="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
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
            # If it's not a known option, treat it as additional arguments for exec
            EXTRA_ARGS="$*"
            break
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

# Set Docker Compose command
COMPOSE_CMD="docker-compose -f $COMPOSE_FILE"
if [[ -n "$SERVICES" ]]; then
    # Convert comma-separated services to space-separated
    SERVICE_LIST=$(echo "$SERVICES" | tr ',' ' ')
fi

# Validate compose file
if [[ ! -f "$COMPOSE_FILE" ]]; then
    log_error "Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Main functions
start_services() {
    log_info "Starting AI Video GPU services..."
    
    if [[ -n "$SERVICES" ]]; then
        $COMPOSE_CMD up -d $SERVICE_LIST
    else
        $COMPOSE_CMD up -d
    fi
    
    log_info "Waiting for services to be ready..."
    sleep 10
    
    check_health
    
    log_success "Services started successfully"
    show_access_info
}

stop_services() {
    log_info "Stopping AI Video GPU services..."
    
    if [[ -n "$SERVICES" ]]; then
        $COMPOSE_CMD stop $SERVICE_LIST
    else
        $COMPOSE_CMD down
    fi
    
    log_success "Services stopped"
}

restart_services() {
    log_info "Restarting AI Video GPU services..."
    
    if [[ -n "$SERVICES" ]]; then
        $COMPOSE_CMD restart $SERVICE_LIST
    else
        stop_services
        start_services
    fi
    
    log_success "Services restarted"
}

build_containers() {
    log_info "Building AI Video GPU containers..."
    
    if [[ "$VERBOSE" == true ]]; then
        $COMPOSE_CMD build --progress=plain $SERVICE_LIST
    else
        $COMPOSE_CMD build $SERVICE_LIST
    fi
    
    log_success "Build completed"
}

pull_images() {
    log_info "Pulling latest images..."
    
    $COMPOSE_CMD pull $SERVICE_LIST
    
    log_success "Images pulled"
}

show_logs() {
    log_info "Showing logs..."
    
    if [[ -n "$SERVICES" ]]; then
        $COMPOSE_CMD logs -f $SERVICE_LIST
    else
        $COMPOSE_CMD logs -f
    fi
}

show_status() {
    log_info "Service status:"
    $COMPOSE_CMD ps
    
    echo ""
    log_info "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

check_health() {
    log_info "Checking service health..."
    
    local unhealthy=0
    
    # Check main application
    if ! curl -sf http://localhost:8000/health >/dev/null 2>&1; then
        log_warning "Main application health check failed"
        ((unhealthy++))
    else
        log_success "Main application is healthy"
    fi
    
    # Check database
    if ! docker exec ai-video-postgres pg_isready -U aivideo >/dev/null 2>&1; then
        log_warning "PostgreSQL health check failed"
        ((unhealthy++))
    else
        log_success "PostgreSQL is healthy"
    fi
    
    # Check Redis
    if ! docker exec ai-video-redis redis-cli ping >/dev/null 2>&1; then
        log_warning "Redis health check failed"
        ((unhealthy++))
    else
        log_success "Redis is healthy"
    fi
    
    # Check Nginx
    if ! curl -sf http://localhost/health >/dev/null 2>&1; then
        log_warning "Nginx health check failed"
        ((unhealthy++))
    else
        log_success "Nginx is healthy"
    fi
    
    if [[ $unhealthy -eq 0 ]]; then
        log_success "All services are healthy"
        return 0
    else
        log_warning "$unhealthy service(s) are unhealthy"
        return 1
    fi
}

open_shell() {
    local service="${SERVICE_LIST:-ai-video-gpu}"
    log_info "Opening shell in $service..."
    
    docker exec -it "ai-video-$service" /bin/bash
}

exec_command() {
    local service="${SERVICE_LIST:-ai-video-gpu}"
    local command="${EXTRA_ARGS:-bash}"
    
    log_info "Executing command in $service: $command"
    
    docker exec -it "ai-video-$service" $command
}

clean_system() {
    log_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Cleaning up AI Video GPU system..."
        
        # Stop and remove containers
        $COMPOSE_CMD down -v --remove-orphans
        
        # Remove images
        docker images | grep "ai-video-gpu" | awk '{print $3}' | xargs -r docker rmi -f
        
        # Remove unused volumes
        docker volume prune -f
        
        # Remove unused networks
        docker network prune -f
        
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

backup_data() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    log_info "Creating backup in $backup_dir..."
    
    # Backup database
    log_info "Backing up PostgreSQL database..."
    docker exec ai-video-postgres pg_dump -U aivideo aivideo | gzip > "$backup_dir/database.sql.gz"
    
    # Backup volumes
    log_info "Backing up data volumes..."
    docker run --rm -v ai_video_models:/data -v "$PWD/$backup_dir":/backup alpine tar czf /backup/models.tar.gz -C /data .
    docker run --rm -v ai_video_outputs:/data -v "$PWD/$backup_dir":/backup alpine tar czf /backup/outputs.tar.gz -C /data .
    docker run --rm -v ai_video_logs:/data -v "$PWD/$backup_dir":/backup alpine tar czf /backup/logs.tar.gz -C /data .
    
    # Backup configuration
    log_info "Backing up configuration files..."
    tar czf "$backup_dir/config.tar.gz" config/ docker-compose*.yml
    
    log_success "Backup completed in $backup_dir"
}

restore_data() {
    if [[ -z "${SERVICES:-}" ]]; then
        log_error "Please specify backup directory with -s option"
        exit 1
    fi
    
    local backup_dir="$SERVICES"
    
    if [[ ! -d "$backup_dir" ]]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    log_warning "This will restore data from $backup_dir. Current data will be lost. Continue? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Restoring from backup: $backup_dir"
        
        # Stop services
        $COMPOSE_CMD down
        
        # Restore database
        if [[ -f "$backup_dir/database.sql.gz" ]]; then
            log_info "Restoring PostgreSQL database..."
            $COMPOSE_CMD up -d postgres
            sleep 10
            zcat "$backup_dir/database.sql.gz" | docker exec -i ai-video-postgres psql -U aivideo aivideo
        fi
        
        # Restore volumes
        if [[ -f "$backup_dir/models.tar.gz" ]]; then
            log_info "Restoring models volume..."
            docker run --rm -v ai_video_models:/data -v "$PWD/$backup_dir":/backup alpine tar xzf /backup/models.tar.gz -C /data
        fi
        
        if [[ -f "$backup_dir/outputs.tar.gz" ]]; then
            log_info "Restoring outputs volume..."
            docker run --rm -v ai_video_outputs:/data -v "$PWD/$backup_dir":/backup alpine tar xzf /backup/outputs.tar.gz -C /data
        fi
        
        # Restart all services
        start_services
        
        log_success "Restore completed"
    else
        log_info "Restore cancelled"
    fi
}

scale_services() {
    if [[ -z "$SERVICES" ]]; then
        log_error "Please specify service=replicas format with -s option (e.g., ai-video-gpu=3)"
        exit 1
    fi
    
    log_info "Scaling services: $SERVICES"
    
    # Parse service=replicas format
    local scale_args=""
    IFS=',' read -ra SCALE_ARRAY <<< "$SERVICES"
    for scale_spec in "${SCALE_ARRAY[@]}"; do
        scale_args="$scale_args $scale_spec"
    done
    
    $COMPOSE_CMD up -d --scale $scale_args
    
    log_success "Scaling completed"
    show_status
}

update_services() {
    log_info "Updating AI Video GPU services..."
    
    # Pull latest images
    pull_images
    
    # Recreate containers with new images
    if [[ -n "$SERVICES" ]]; then
        $COMPOSE_CMD up -d --force-recreate $SERVICE_LIST
    else
        $COMPOSE_CMD up -d --force-recreate
    fi
    
    # Check health after update
    sleep 10
    check_health
    
    log_success "Update completed"
}

open_monitoring() {
    log_info "Opening monitoring dashboard..."
    
    # Check if Grafana is running
    if ! docker-compose -f docker-compose.prebuilt.yml ps grafana | grep -q "Up"; then
        log_warning "Grafana is not running. Starting monitoring services..."
        $COMPOSE_CMD up -d grafana prometheus
        sleep 10
    fi
    
    log_info "Grafana dashboard: http://localhost:3000 (admin/aivideoadmin)"
    log_info "Prometheus: http://localhost:9090"
    log_info "Flower (Celery): http://localhost:5555"
    
    # Try to open in browser (Linux)
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open http://localhost:3000
    elif command -v open >/dev/null 2>&1; then
        open http://localhost:3000
    fi
}

show_access_info() {
    cat << EOF

${GREEN}🚀 AI Video GPU System is running!${NC}

${BLUE}Access Points:${NC}
• Main API:        http://localhost:8000
• Web Interface:   http://localhost:8080
• Gradio UI:       http://localhost:8501
• Grafana:         http://localhost:3000 (admin/aivideoadmin)
• Prometheus:      http://localhost:9090
• Flower:          http://localhost:5555
• Nginx:           http://localhost

${BLUE}Quick Commands:${NC}
• View logs:       $0 logs
• Check health:    $0 health
• Open shell:      $0 shell
• Stop services:   $0 stop
• Monitor:         $0 monitor

${BLUE}Documentation:${NC}
• README.md
• API docs:        http://localhost:8000/docs
• Integration:     INTEGRATION_GUIDE.md

EOF
}

# Main execution
case "$ACTION" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    build)
        build_containers
        ;;
    pull)
        pull_images
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    health)
        check_health
        ;;
    shell)
        open_shell
        ;;
    exec)
        exec_command
        ;;
    clean)
        clean_system
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data
        ;;
    scale)
        scale_services
        ;;
    update)
        update_services
        ;;
    monitor)
        open_monitoring
        ;;
    *)
        log_error "Unknown action: $ACTION"
        usage
        exit 1
        ;;
esac
