# Large File Upload Configuration Guide

## Overview

The AI Video GPU system supports unlimited file sizes through advanced multipart upload capabilities. This guide explains how to optimize the system for large file uploads.

## Configuration Settings

### Environment Variables

Set these environment variables to optimize for your use case:

```bash
# Basic Wasabi credentials
export WASABI_ACCESS_KEY="your_access_key"
export WASABI_SECRET_KEY="your_secret_key"
export WASABI_ENDPOINT_URL="https://s3.wasabisys.com"
export WASABI_REGION="us-east-1"

# Upload optimization settings
export WASABI_MULTIPART_THRESHOLD=67108864    # 64MB - Files larger use multipart
export WASABI_MULTIPART_CHUNKSIZE=8388608     # 8MB - Size of each part
export WASABI_MAX_CONCURRENCY=10              # Parallel uploads

# Bucket names (optional - will use defaults if not set)
export WASABI_MODELS_BUCKET="ai-video-gpu-models"
export WASABI_OUTPUTS_BUCKET="ai-video-gpu-outputs"
export WASABI_UPLOADS_BUCKET="ai-video-gpu-uploads"
export WASABI_BACKUPS_BUCKET="ai-video-gpu-backups"
export WASABI_TEMP_BUCKET="ai-video-gpu-temp"
```

### Configuration File

Edit `config/wasabi.yml` for persistent settings:

```yaml
wasabi:
  # Upload settings - Optimized for large files
  multipart_threshold: 67108864      # 64MB
  multipart_chunksize: 8388608       # 8MB
  max_concurrency: 10                # Parallel uploads
  
  # Large file settings
  large_file_threshold: 1073741824   # 1GB
  large_file_chunksize: 33554432     # 32MB
  large_file_max_concurrency: 5      # Fewer parallel for large files
  
  # Retry settings
  retry_attempts: 3
  retry_delay: 2
  
  # Bandwidth limits (0 = unlimited)
  upload_bandwidth_limit: 0
  download_bandwidth_limit: 0
```

## Optimization Guidelines

### For Different File Sizes

#### Small Files (< 64MB)
- Uses standard S3 upload
- Single request
- Fastest for small files

```bash
# Default settings work well
export WASABI_MULTIPART_THRESHOLD=67108864  # 64MB
```

#### Medium Files (64MB - 1GB)
- Uses multipart upload
- 8MB chunks recommended
- Up to 10 concurrent uploads

```bash
export WASABI_MULTIPART_CHUNKSIZE=8388608   # 8MB
export WASABI_MAX_CONCURRENCY=10
```

#### Large Files (1GB+)
- Uses multipart upload with larger chunks
- 32MB chunks recommended
- Fewer concurrent uploads to avoid timeouts

```bash
export WASABI_MULTIPART_CHUNKSIZE=33554432  # 32MB
export WASABI_MAX_CONCURRENCY=5
```

#### Very Large Files (10GB+)
- Use largest chunk size
- Minimal concurrency
- Consider resumable uploads

```bash
export WASABI_MULTIPART_CHUNKSIZE=67108864  # 64MB
export WASABI_MAX_CONCURRENCY=2
```

### Network Optimization

#### High Bandwidth Connections
```bash
export WASABI_MULTIPART_CHUNKSIZE=33554432  # 32MB chunks
export WASABI_MAX_CONCURRENCY=15            # More parallel uploads
```

#### Low Bandwidth Connections
```bash
export WASABI_MULTIPART_CHUNKSIZE=4194304   # 4MB chunks
export WASABI_MAX_CONCURRENCY=3             # Fewer parallel uploads
```

#### Unstable Connections
```bash
export WASABI_MULTIPART_CHUNKSIZE=2097152   # 2MB chunks
export WASABI_MAX_CONCURRENCY=2             # Minimal concurrency
```

## Command Line Usage

### Basic Upload
```bash
# Upload any size file
python -m src.cli.wasabi_commands upload /path/to/file.mp4

# Upload to specific bucket
python -m src.cli.wasabi_commands upload /path/to/file.mp4 --bucket-type outputs

# Make publicly readable
python -m src.cli.wasabi_commands upload /path/to/file.mp4 --public
```

### Large File Upload with Progress
```bash
# Upload with progress tracking
python -m src.cli.wasabi_commands upload-large /path/to/large_file.mp4

# Force multipart for testing
python -m src.cli.wasabi_commands upload-large /path/to/file.mp4 --force-multipart
```

### Resume Failed Uploads
```bash
# List ongoing uploads
python -m src.cli.wasabi_commands list-uploads

# Resume specific upload
python -m src.cli.wasabi_commands resume-upload /path/to/file.mp4 UPLOAD_ID --key remote_key

# Check upload progress
python -m src.cli.wasabi_commands upload-progress UPLOAD_ID remote_key

# Abort upload
python -m src.cli.wasabi_commands abort-upload UPLOAD_ID remote_key
```

### Testing
```bash
# Test upload with generated file
python -m src.cli.wasabi_commands test-large-upload 100  # 100MB test file

# Show current configuration
python -m src.cli.wasabi_commands config
```

## Python API Usage

### Basic Upload
```python
from src.cloud.wasabi_storage import WasabiStorage

storage = WasabiStorage()

# Upload any file
url = storage.upload_file('/path/to/file.mp4')
```

### Large File Upload with Progress
```python
def progress_callback(percent, completed_parts, total_parts):
    print(f"Progress: {percent:.1f}% ({completed_parts}/{total_parts} parts)")

# Upload with progress tracking
url = storage.upload_large_file(
    '/path/to/large_file.mp4',
    bucket_type='outputs',
    progress_callback=progress_callback
)
```

### Resume Upload
```python
# Resume failed upload
url = storage.resume_upload(
    '/path/to/file.mp4',
    bucket_type='outputs',
    upload_id='your_upload_id',
    remote_key='remote_key'
)
```

### Monitor Uploads
```python
# List ongoing uploads
uploads = storage.list_multipart_uploads('outputs')

# Get upload progress
progress = storage.get_upload_progress('outputs', 'upload_id', 'remote_key')

# Abort upload
storage.abort_upload('outputs', 'upload_id', 'remote_key')
```

## Performance Tuning

### Memory Usage
- Larger chunks = more memory usage
- More concurrency = more memory usage
- For memory-constrained environments, use smaller chunks

### Speed Optimization
- Increase chunk size for faster uploads
- Increase concurrency for better throughput
- Monitor network usage to avoid saturation

### Reliability
- Smaller chunks = more resilient to network issues
- Lower concurrency = fewer connection errors
- Enable resume uploads for critical files

## Troubleshooting

### Common Issues

#### Upload Timeout
```bash
# Reduce concurrency
export WASABI_MAX_CONCURRENCY=2

# Smaller chunks
export WASABI_MULTIPART_CHUNKSIZE=4194304  # 4MB
```

#### Memory Errors
```bash
# Smaller chunks
export WASABI_MULTIPART_CHUNKSIZE=2097152  # 2MB

# Reduce concurrency
export WASABI_MAX_CONCURRENCY=3
```

#### Network Errors
```bash
# Very small chunks
export WASABI_MULTIPART_CHUNKSIZE=1048576  # 1MB

# Minimal concurrency
export WASABI_MAX_CONCURRENCY=1
```

### Debug Mode
```bash
# Enable verbose logging
export PYTHONPATH=/workspaces/AI-Video-GPU-/src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from cloud.wasabi_storage import WasabiStorage
storage = WasabiStorage()
storage.upload_file('/path/to/file.mp4')
"
```

## Best Practices

1. **Test with small files first** to verify configuration
2. **Monitor upload progress** for large files
3. **Use resumable uploads** for files > 1GB
4. **Set appropriate timeouts** based on file size
5. **Consider network conditions** when setting concurrency
6. **Enable logging** for troubleshooting
7. **Use temporary bucket** for testing
8. **Clean up failed uploads** regularly

## Examples

See `examples/large_file_upload_demo.py` for complete working examples of:
- Small file uploads
- Large file uploads with progress
- Multipart upload management
- Error handling and recovery
- Performance optimization

Run the demo:
```bash
cd /workspaces/AI-Video-GPU-
python examples/large_file_upload_demo.py
```
