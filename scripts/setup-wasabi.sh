#!/bin/bash

# =============================================================================
# Wasabi Cloud Storage Setup Script
# Initialize and configure Wasabi storage for AI Video GPU
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

print_banner() {
    echo -e "${BLUE}${BOLD}"
    cat << 'EOF'
    __        __                _     _    ____       _               
    \ \      / /_ _ ___  __ _  | |__ (_)  / ___|  ___| |_ _   _ _ __  
     \ \ /\ / / _` / __|/ _` | | '_ \| |  \___ \ / _ \ __| | | | '_ \ 
      \ V  V / (_| \__ \ (_| | | |_) | |   ___) |  __/ |_| |_| | |_) |
       \_/\_/ \__,_|___/\__,_| |_.__/|_|  |____/ \___|\__|\__,_| .__/ 
                                                               |_|    
                    Cloud Storage Setup for AI Video GPU
EOF
    echo -e "${NC}"
}

check_environment() {
    log_info "Checking environment variables..."
    
    local missing_vars=()
    
    if [[ -z "${WASABI_ACCESS_KEY:-}" ]]; then
        missing_vars+=("WASABI_ACCESS_KEY")
    fi
    
    if [[ -z "${WASABI_SECRET_KEY:-}" ]]; then
        missing_vars+=("WASABI_SECRET_KEY")
    fi
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing environment variables: ${missing_vars[*]}"
        log_info "Please set these variables or source the .env.wasabi file:"
        log_info "  source config/.env.wasabi"
        return 1
    fi
    
    log_success "Environment variables found"
    log_info "Access Key: ${WASABI_ACCESS_KEY:0:8}..."
    log_info "Endpoint: ${WASABI_ENDPOINT_URL:-https://s3.wasabisys.com}"
    log_info "Region: ${WASABI_REGION:-us-east-1}"
    
    return 0
}

install_dependencies() {
    log_info "Installing Python dependencies for Wasabi..."
    
    cd "$PROJECT_ROOT"
    
    # Check if virtual environment exists
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    
    # Install Wasabi-related packages
    pip install boto3 minio tabulate python-dotenv
    
    log_success "Dependencies installed"
}

load_environment() {
    log_info "Loading Wasabi configuration..."
    
    # Try to load from .env.wasabi file
    local env_file="$PROJECT_ROOT/config/.env.wasabi"
    if [[ -f "$env_file" ]]; then
        log_info "Loading configuration from $env_file"
        set -a  # Automatically export all variables
        source "$env_file"
        set +a
        log_success "Configuration loaded"
    else
        log_warning "Configuration file not found: $env_file"
        log_info "Please create this file with your Wasabi credentials"
        return 1
    fi
}

test_connection() {
    log_info "Testing Wasabi connection..."
    
    cd "$PROJECT_ROOT"
    
    # Use Python to test connection
    python3 << 'EOF'
import sys
import os
sys.path.append('src')

try:
    from cloud.wasabi_storage import WasabiStorage
    
    # Initialize storage
    storage = WasabiStorage()
    
    # Test connection
    if storage.test_connection():
        print("✅ Wasabi connection successful")
        
        # List existing buckets
        try:
            response = storage.client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            if buckets:
                print(f"📦 Existing buckets: {', '.join(buckets)}")
            else:
                print("📦 No existing buckets found")
        except Exception as e:
            print(f"⚠️  Could not list buckets: {e}")
        
        sys.exit(0)
    else:
        print("❌ Wasabi connection failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error testing connection: {e}")
    sys.exit(1)
EOF
    
    if [[ $? -eq 0 ]]; then
        log_success "Connection test passed"
        return 0
    else
        log_error "Connection test failed"
        return 1
    fi
}

create_buckets() {
    log_info "Creating Wasabi buckets..."
    
    cd "$PROJECT_ROOT"
    
    # Define buckets to create
    local buckets=(
        "ai-video-gpu-models"
        "ai-video-gpu-outputs"
        "ai-video-gpu-uploads"
        "ai-video-gpu-backups"
        "ai-video-gpu-temp"
    )
    
    python3 << EOF
import sys
import os
sys.path.append('src')

try:
    from cloud.wasabi_storage import WasabiStorage
    
    storage = WasabiStorage()
    buckets = ${buckets[@]@Q}  # Pass bucket list to Python
    
    for bucket_name in ['${buckets[@]}']:
        if storage.create_bucket(bucket_name):
            print(f"✅ Created/verified bucket: {bucket_name}")
        else:
            print(f"❌ Failed to create bucket: {bucket_name}")
            
    print("🎯 Bucket creation completed")
    
except Exception as e:
    print(f"❌ Error creating buckets: {e}")
    sys.exit(1)
EOF
    
    log_success "Bucket creation completed"
}

show_status() {
    log_info "Checking Wasabi storage status..."
    
    cd "$PROJECT_ROOT"
    
    # Show storage usage
    python3 << 'EOF'
import sys
import os
sys.path.append('src')

try:
    from cloud.wasabi_storage import WasabiStorage
    
    storage = WasabiStorage()
    usage = storage.get_storage_usage()
    
    print("\n📊 Wasabi Storage Status:")
    print("=" * 50)
    
    total_size_gb = 0
    total_files = 0
    
    for bucket_type, stats in usage.items():
        if stats.get('exists', False):
            size_gb = stats.get('total_size_gb', 0)
            file_count = stats.get('file_count', 0)
            bucket_name = storage.buckets[bucket_type]
            
            print(f"📦 {bucket_type.title()}: {bucket_name}")
            print(f"   Files: {file_count:,}")
            print(f"   Size: {stats.get('total_size_mb', 0):.1f} MB ({size_gb:.3f} GB)")
            
            total_size_gb += size_gb
            total_files += file_count
        else:
            bucket_name = storage.buckets[bucket_type]
            print(f"📦 {bucket_type.title()}: {bucket_name} (Not found)")
        print()
    
    print(f"📈 Total: {total_files:,} files, {total_size_gb:.3f} GB")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Error getting status: {e}")
    sys.exit(1)
EOF
}

upload_test_file() {
    log_info "Testing file upload..."
    
    cd "$PROJECT_ROOT"
    
    # Create a test file
    local test_file="/tmp/wasabi_test_$(date +%s).txt"
    echo "Wasabi test file created at $(date)" > "$test_file"
    
    python3 << EOF
import sys
import os
sys.path.append('src')

try:
    from cloud.wasabi_storage import WasabiStorage
    
    storage = WasabiStorage()
    
    # Upload test file
    url = storage.upload_file(
        local_path='$test_file',
        bucket_type='temp',
        remote_key='test/wasabi_test.txt'
    )
    
    if url:
        print(f"✅ Test file uploaded successfully")
        print(f"   URL: {url}")
        
        # Clean up test file
        if storage.delete_file('test/wasabi_test.txt', 'temp'):
            print("🗑️  Test file cleaned up")
        
        print("🎯 Upload test completed successfully")
    else:
        print("❌ Test file upload failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error during upload test: {e}")
    sys.exit(1)
EOF
    
    # Clean up local test file
    rm -f "$test_file"
    
    log_success "Upload test completed"
}

show_cli_examples() {
    log_info "Wasabi CLI usage examples:"
    
    cat << 'EOF'

🔧 Wasabi CLI Commands:

# Test connection
python -m src.cli.wasabi_commands test

# Initialize buckets
python -m src.cli.wasabi_commands init

# Check status
python -m src.cli.wasabi_commands status

# Upload file
python -m src.cli.wasabi_commands upload video.mp4 --bucket-type outputs

# List files
python -m src.cli.wasabi_commands list --bucket-type outputs

# Download file
python -m src.cli.wasabi_commands download video.mp4 ./downloads/

# Sync directory
python -m src.cli.wasabi_commands sync ./outputs --bucket-type outputs

# Generate URL
python -m src.cli.wasabi_commands url video.mp4 --expiration 7200

🌐 Integration with AI Video GPU:

The system will automatically upload generated videos to Wasabi when
CLOUD_STORAGE_ENABLED=true and CLOUD_STORAGE_PROVIDER=wasabi

Generated videos will be available at:
https://s3.wasabisys.com/ai-video-gpu-outputs/your-video.mp4

EOF
}

# Main setup function
main() {
    print_banner
    
    log_info "Starting Wasabi setup for AI Video GPU..."
    
    # Load environment
    if ! load_environment; then
        log_error "Failed to load environment configuration"
        exit 1
    fi
    
    # Check environment variables
    if ! check_environment; then
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Test connection
    if ! test_connection; then
        log_error "Cannot proceed without valid Wasabi connection"
        exit 1
    fi
    
    # Create buckets
    create_buckets
    
    # Test upload
    upload_test_file
    
    # Show status
    show_status
    
    # Show CLI examples
    show_cli_examples
    
    log_success "Wasabi setup completed successfully! 🎉"
    log_info "Your AI Video GPU system is now configured to use Wasabi cloud storage"
}

# Run main function
main "$@"
