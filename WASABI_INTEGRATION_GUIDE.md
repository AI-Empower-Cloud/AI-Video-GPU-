# Wasabi Cloud Storage Integration Guide

## 🌊 Overview

Wasabi is a high-performance, S3-compatible cloud storage service that provides fast, affordable object storage. This guide shows how to integrate Wasabi with your AI Video GPU system for storing models, outputs, and backups.

## 🔧 Setup

### 1. Quick Setup
```bash
# Setup Wasabi storage
make wasabi-setup

# Or run the setup script directly
./scripts/setup-wasabi.sh
```

### 2. Manual Configuration

#### Environment Variables
Create `config/.env.wasabi` with your credentials:
```bash
# Wasabi Credentials
WASABI_ACCESS_KEY=your_access_key
WASABI_SECRET_KEY=your_secret_key
WASABI_ENDPOINT_URL=https://s3.wasabisys.com
WASABI_REGION=us-east-1

# Bucket Configuration
WASABI_MODELS_BUCKET=ai-video-gpu-models
WASABI_OUTPUTS_BUCKET=ai-video-gpu-outputs
WASABI_UPLOADS_BUCKET=ai-video-gpu-uploads
WASABI_BACKUPS_BUCKET=ai-video-gpu-backups
WASABI_TEMP_BUCKET=ai-video-gpu-temp

# Storage Settings
CLOUD_STORAGE_PROVIDER=wasabi
CLOUD_STORAGE_ENABLED=true
AUTO_UPLOAD_ENABLED=true
```

#### Load Environment
```bash
# Load Wasabi configuration
source config/.env.wasabi

# Verify configuration
make wasabi-test
```

## 🪣 Bucket Structure

The system creates five buckets for different purposes:

- **`ai-video-gpu-models`** - Pre-trained AI models and weights
- **`ai-video-gpu-outputs`** - Generated videos and final outputs
- **`ai-video-gpu-uploads`** - User uploaded content (images, audio, etc.)
- **`ai-video-gpu-backups`** - System backups and snapshots
- **`ai-video-gpu-temp`** - Temporary files (auto-cleaned)

## 🚀 Usage

### Command Line Interface

#### Basic Commands
```bash
# Test connection
make wasabi-test

# Check storage status
make wasabi-status

# Initialize buckets
make wasabi-init
```

#### File Operations
```bash
# Upload file
make wasabi-upload FILE=video.mp4 BUCKET=outputs

# List files
make wasabi-list BUCKET=outputs

# Sync directory
make wasabi-sync DIR=./outputs BUCKET=outputs
```

#### Advanced CLI
```bash
# Upload with metadata
python -m src.cli.wasabi_commands upload video.mp4 \
  --bucket-type outputs \
  --metadata '{"project": "demo", "version": "1.0"}'

# Generate presigned URL (valid for 2 hours)
python -m src.cli.wasabi_commands url video.mp4 \
  --bucket-type outputs \
  --expiration 7200

# Download file
python -m src.cli.wasabi_commands download video.mp4 ./downloads/

# Get file information
python -m src.cli.wasabi_commands info video.mp4 --bucket-type outputs

# Delete file (with confirmation)
python -m src.cli.wasabi_commands delete old_video.mp4 --bucket-type outputs
```

### Python API

#### Basic Usage
```python
from src.cloud.wasabi_storage import get_wasabi_storage

# Get storage instance
storage = get_wasabi_storage()

# Upload file
url = storage.upload_file(
    local_path="video.mp4",
    bucket_type="outputs",
    public_read=True
)

# Download file
storage.download_file(
    remote_key="video.mp4",
    local_path="./downloads/video.mp4",
    bucket_type="outputs"
)

# List files
files = storage.list_files(bucket_type="outputs", prefix="2024/")

# Get storage usage
usage = storage.get_storage_usage()
```

#### Advanced Usage
```python
# Upload with metadata
url = storage.upload_file(
    local_path="video.mp4",
    bucket_type="outputs",
    remote_key="projects/demo/video_v1.mp4",
    metadata={
        "project": "demo",
        "version": "1.0",
        "resolution": "1080p"
    },
    public_read=True
)

# Sync directory
storage.sync_directory(
    local_dir="./outputs",
    bucket_type="outputs",
    remote_prefix="batch_001/",
    delete_missing=False
)

# Generate presigned URL
url = storage.generate_presigned_url(
    remote_key="video.mp4",
    bucket_type="outputs",
    expiration=3600  # 1 hour
)
```

## 🔄 Integration with AI Video GPU

### Automatic Upload
When `AUTO_UPLOAD_ENABLED=true`, the system automatically uploads:

- Generated videos to the `outputs` bucket
- Trained models to the `models` bucket
- System backups to the `backups` bucket

### Configuration
```yaml
# config/wasabi.yml
wasabi:
  enabled: true
  endpoint_url: "https://s3.wasabisys.com"

  # Auto-upload settings
  auto_upload:
    models: true
    outputs: true
    backups: true
    logs: false

  # Performance settings
  multipart_threshold: 67108864  # 64MB
  parallel_uploads: 5
  compression: true
```

### API Integration
```python
# In your AI video generation code
from src.cloud.wasabi_storage import get_wasabi_storage

def generate_video(prompt, output_path):
    # Generate video
    video = create_video(prompt)
    video.save(output_path)

    # Auto-upload to Wasabi
    if os.getenv('AUTO_UPLOAD_ENABLED', 'false').lower() == 'true':
        storage = get_wasabi_storage()
        if storage:
            url = storage.upload_file(
                local_path=output_path,
                bucket_type="outputs",
                public_read=True
            )
            return {"local_path": output_path, "cloud_url": url}

    return {"local_path": output_path}
```

## 📊 Monitoring

### Storage Usage
```bash
# Check storage usage
make wasabi-status

# Output:
# 📊 Wasabi Storage Status
# ╒═════════════╤══════════════════════════╤═════════╤════════════╤═══════════╕
# │ Bucket Type │ Bucket Name              │ Files   │ Size (MB)  │ Size (GB) │
# ├─────────────┼──────────────────────────┼─────────┼────────────┼───────────┤
# │ Models      │ ai-video-gpu-models      │ 15      │ 8,432.1 MB │ 8.234 GB  │
# │ Outputs     │ ai-video-gpu-outputs     │ 127     │ 2,156.7 MB │ 2.106 GB  │
# │ Uploads     │ ai-video-gpu-uploads     │ 43      │ 892.3 MB   │ 0.871 GB  │
# │ Backups     │ ai-video-gpu-backups     │ 8       │ 1,234.5 MB │ 1.205 GB  │
# │ Temp        │ ai-video-gpu-temp        │ 2       │ 45.2 MB    │ 0.044 GB  │
# ╘═════════════╧══════════════════════════╧═════════╧════════════╧═══════════╛
```

### Performance Metrics
The system tracks:
- Upload/download speeds
- Error rates
- Storage usage over time
- Cost optimization opportunities

## 🔒 Security

### Access Control
- Uses IAM-style access keys
- Supports bucket policies
- Optional public read access for outputs
- Server-side encryption (AES256)

### Best Practices
```bash
# Use environment variables for credentials
export WASABI_ACCESS_KEY="your_key"
export WASABI_SECRET_KEY="your_secret"

# Don't commit credentials to version control
echo "config/.env.wasabi" >> .gitignore

# Use presigned URLs for temporary access
python -m src.cli.wasabi_commands url video.mp4 --expiration 3600
```

## 💰 Cost Optimization

### Lifecycle Management
```yaml
# config/wasabi.yml
lifecycle:
  temp_files_expire_days: 7      # Auto-delete temp files
  backup_transition_days: 30     # Move old backups to cheaper storage
  outputs_expire_days: 365       # Delete old outputs after 1 year
```

### Storage Classes
- **Hot Storage**: Frequently accessed files (outputs, models)
- **Cool Storage**: Infrequent access (old backups)
- **Archive**: Long-term retention (historical data)

## 🐛 Troubleshooting

### Common Issues

#### Connection Failed
```bash
# Check credentials
echo $WASABI_ACCESS_KEY
echo $WASABI_SECRET_KEY

# Test connection
make wasabi-test

# Verify endpoint
curl -I https://s3.wasabisys.com
```

#### Upload Failed
```bash
# Check file permissions
ls -la your_file.mp4

# Check bucket exists
python -m src.cli.wasabi_commands list --bucket-type outputs

# Check available space
df -h .

# Enable debug logging
WASABI_DEBUG=true make wasabi-upload FILE=video.mp4 BUCKET=outputs
```

#### Slow Performance
```bash
# Check network speed
curl -o /dev/null -s -w "%{speed_download}\n" https://s3.wasabisys.com

# Optimize settings
export MULTIPART_THRESHOLD=67108864  # 64MB
export PARALLEL_UPLOADS=10
export MAX_CONCURRENCY=20
```

### Debug Mode
```bash
# Enable verbose logging
export WASABI_DEBUG=true
export PYTHONPATH=/app

# Run with debug output
python -m src.cli.wasabi_commands status --verbose
```

## 🌐 Public Access

### Making Files Public
```bash
# Upload with public read access
python -m src.cli.wasabi_commands upload video.mp4 \
  --bucket-type outputs \
  --public

# Files will be accessible at:
# https://s3.wasabisys.com/ai-video-gpu-outputs/video.mp4
```

### CDN Integration
For better performance, consider using a CDN:
- CloudFlare
- AWS CloudFront
- KeyCDN

## 📈 Scaling

### Multi-Region Setup
```yaml
# config/wasabi.yml
regions:
  primary: us-east-1
  backup: eu-central-1

replication:
  enabled: true
  cross_region: true
  backup_regions: ["eu-central-1"]
```

### Batch Operations
```bash
# Sync large directories
make wasabi-sync DIR=./large_dataset BUCKET=models

# Parallel uploads
python scripts/batch_upload.py --directory ./outputs --parallel 10
```

## 🔗 Integration Examples

### With Docker
```yaml
# docker-compose.yml
services:
  ai-video-gpu:
    environment:
      - WASABI_ACCESS_KEY=${WASABI_ACCESS_KEY}
      - WASABI_SECRET_KEY=${WASABI_SECRET_KEY}
      - CLOUD_STORAGE_PROVIDER=wasabi
      - AUTO_UPLOAD_ENABLED=true
```

### With CI/CD
```yaml
# .github/workflows/deploy.yml
- name: Upload artifacts to Wasabi
  env:
    WASABI_ACCESS_KEY: ${{ secrets.WASABI_ACCESS_KEY }}
    WASABI_SECRET_KEY: ${{ secrets.WASABI_SECRET_KEY }}
  run: |
    make wasabi-sync DIR=./artifacts BUCKET=outputs
```

### With Monitoring
```python
# Monitor storage usage
import schedule
from src.cloud.wasabi_storage import get_wasabi_storage

def monitor_storage():
    storage = get_wasabi_storage()
    usage = storage.get_storage_usage()

    # Send metrics to monitoring system
    send_metrics("wasabi.storage.usage", usage)

schedule.every(1).hours.do(monitor_storage)
```

---

**🎯 Ready to use Wasabi with your AI Video GPU system!**

Start with: `make wasabi-setup`
