"""
Wasabi Cloud Storage CLI Commands
Management interface for Wasabi storage operations
"""

import click
import os
import sys
from pathlib import Path
from typing import Optional
import json
from tabulate import tabulate

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from cloud.wasabi_storage import WasabiStorage, get_wasabi_storage, initialize_wasabi_buckets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def wasabi(verbose):
    """Wasabi cloud storage management commands"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@wasabi.command()
def test():
    """Test Wasabi connection"""
    click.echo("Testing Wasabi connection...")
    
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    if storage.test_connection():
        click.echo("✅ Wasabi connection successful")
        
        # Show account info
        try:
            buckets = storage.client.list_buckets()
            click.echo(f"📦 Found {len(buckets['Buckets'])} buckets in account")
        except Exception as e:
            click.echo(f"⚠️  Could not list buckets: {e}")
    else:
        click.echo("❌ Wasabi connection failed", err=True)
        sys.exit(1)


@wasabi.command()
def init():
    """Initialize Wasabi buckets"""
    click.echo("Initializing Wasabi buckets...")
    
    if initialize_wasabi_buckets():
        click.echo("✅ All buckets initialized successfully")
    else:
        click.echo("❌ Failed to initialize some buckets", err=True)
        sys.exit(1)


@wasabi.command()
def status():
    """Show Wasabi storage status and usage"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo("📊 Wasabi Storage Status\n")
    
    # Get usage statistics
    usage = storage.get_storage_usage()
    
    # Prepare table data
    table_data = []
    total_size_gb = 0
    total_files = 0
    
    for bucket_type, stats in usage.items():
        if stats.get('exists', False):
            size_gb = stats.get('total_size_gb', 0)
            file_count = stats.get('file_count', 0)
            
            table_data.append([
                bucket_type.title(),
                storage.buckets[bucket_type],
                f"{file_count:,}",
                f"{stats.get('total_size_mb', 0):.1f} MB",
                f"{size_gb:.3f} GB"
            ])
            
            total_size_gb += size_gb
            total_files += file_count
        else:
            table_data.append([
                bucket_type.title(),
                storage.buckets[bucket_type],
                "N/A",
                "Not Found",
                "N/A"
            ])
    
    # Add total row
    table_data.append([
        "TOTAL",
        "-",
        f"{total_files:,}",
        f"{total_size_gb * 1024:.1f} MB",
        f"{total_size_gb:.3f} GB"
    ])
    
    headers = ["Bucket Type", "Bucket Name", "Files", "Size (MB)", "Size (GB)"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Show configuration
    click.echo(f"\n🔧 Configuration:")
    click.echo(f"   Endpoint: {storage.endpoint_url}")
    click.echo(f"   Region: {storage.region}")
    click.echo(f"   Access Key: {storage.access_key[:8]}...")


@wasabi.command()
@click.argument('local_path', type=click.Path(exists=True))
@click.option('--bucket-type', '-b', default='outputs', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
@click.option('--key', '-k', help='Remote object key (defaults to filename)')
@click.option('--public', is_flag=True, help='Make file publicly readable')
@click.option('--metadata', '-m', help='JSON metadata to attach')
def upload(local_path, bucket_type, key, public, metadata):
    """Upload file to Wasabi"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    # Parse metadata if provided
    file_metadata = None
    if metadata:
        try:
            file_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            click.echo("❌ Invalid JSON metadata", err=True)
            sys.exit(1)
    
    click.echo(f"⬆️  Uploading {local_path} to {bucket_type} bucket...")
    
    url = storage.upload_file(
        local_path=local_path,
        bucket_type=bucket_type,
        remote_key=key,
        metadata=file_metadata,
        public_read=public
    )
    
    if url:
        click.echo(f"✅ Upload successful!")
        click.echo(f"   URL: {url}")
        if public:
            click.echo(f"   🌐 File is publicly accessible")
    else:
        click.echo("❌ Upload failed", err=True)
        sys.exit(1)


@wasabi.command()
@click.argument('remote_key')
@click.argument('local_path', type=click.Path())
@click.option('--bucket-type', '-b', default='outputs',
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Source bucket type')
def download(remote_key, local_path, bucket_type):
    """Download file from Wasabi"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"⬇️  Downloading {remote_key} from {bucket_type} bucket...")
    
    if storage.download_file(remote_key, local_path, bucket_type):
        click.echo(f"✅ Download successful!")
        click.echo(f"   Saved to: {local_path}")
    else:
        click.echo("❌ Download failed", err=True)
        sys.exit(1)


@wasabi.command()
@click.option('--bucket-type', '-b', default='outputs',
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Bucket type to list')
@click.option('--prefix', '-p', default='', help='Object key prefix filter')
@click.option('--limit', '-l', default=50, help='Maximum number of files to show')
def list(bucket_type, prefix, limit):
    """List files in Wasabi bucket"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"📋 Files in {bucket_type} bucket:")
    if prefix:
        click.echo(f"   Filter: {prefix}*")
    click.echo()
    
    files = storage.list_files(bucket_type, prefix, limit)
    
    if not files:
        click.echo("   No files found")
        return
    
    # Prepare table data
    table_data = []
    for file_info in files[:limit]:
        size_mb = file_info['size'] / (1024 * 1024)
        table_data.append([
            file_info['key'],
            f"{size_mb:.2f} MB",
            file_info['last_modified'].strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    headers = ["Object Key", "Size", "Last Modified"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    if len(files) >= limit:
        click.echo(f"\n   (Showing first {limit} files)")


@wasabi.command()
@click.argument('remote_key')
@click.option('--bucket-type', '-b', default='outputs',
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Bucket type')
def info(remote_key, bucket_type):
    """Get information about a file"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    file_info = storage.get_file_info(remote_key, bucket_type)
    
    if not file_info:
        click.echo(f"❌ File not found: {remote_key}", err=True)
        sys.exit(1)
    
    click.echo(f"📄 File Information: {remote_key}\n")
    
    size_mb = file_info['size'] / (1024 * 1024)
    size_gb = size_mb / 1024
    
    info_table = [
        ["Key", file_info['key']],
        ["Size", f"{file_info['size']:,} bytes ({size_mb:.2f} MB)"],
        ["Last Modified", file_info['last_modified'].strftime('%Y-%m-%d %H:%M:%S UTC')],
        ["ETag", file_info['etag']],
        ["Content Type", file_info.get('content_type', 'Unknown')],
        ["URL", file_info['url']]
    ]
    
    click.echo(tabulate(info_table, tablefmt="grid"))
    
    # Show metadata if present
    if file_info.get('metadata'):
        click.echo("\n📋 Metadata:")
        metadata_table = [[k, v] for k, v in file_info['metadata'].items()]
        click.echo(tabulate(metadata_table, headers=["Key", "Value"], tablefmt="grid"))


@wasabi.command()
@click.argument('remote_key')
@click.option('--bucket-type', '-b', default='outputs',
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Bucket type')
@click.option('--expiration', '-e', default=3600, help='URL expiration in seconds')
def url(remote_key, bucket_type, expiration):
    """Generate presigned URL for file access"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    url = storage.generate_presigned_url(
        remote_key=remote_key,
        bucket_type=bucket_type,
        expiration=expiration
    )
    
    if url:
        hours = expiration // 3600
        minutes = (expiration % 3600) // 60
        
        click.echo(f"🔗 Presigned URL (expires in {hours}h {minutes}m):")
        click.echo(f"   {url}")
    else:
        click.echo("❌ Failed to generate URL", err=True)
        sys.exit(1)


@wasabi.command()
@click.argument('local_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--bucket-type', '-b', default='outputs',
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
@click.option('--prefix', '-p', default='', help='Remote prefix for objects')
@click.option('--delete', is_flag=True, help='Delete remote files not in local directory')
def sync(local_dir, bucket_type, prefix, delete):
    """Sync local directory to Wasabi"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"🔄 Syncing {local_dir} to {bucket_type} bucket...")
    if prefix:
        click.echo(f"   Remote prefix: {prefix}")
    if delete:
        click.echo("   ⚠️  Will delete remote files not found locally")
    
    if storage.sync_directory(local_dir, bucket_type, prefix, delete):
        click.echo("✅ Sync completed successfully")
    else:
        click.echo("❌ Sync failed", err=True)
        sys.exit(1)


@wasabi.command()
@click.argument('remote_key')
@click.option('--bucket-type', '-b', default='outputs',
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Bucket type')
@click.confirmation_option(prompt='Are you sure you want to delete this file?')
def delete(remote_key, bucket_type):
    """Delete file from Wasabi"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    if storage.delete_file(remote_key, bucket_type):
        click.echo(f"✅ Deleted {remote_key}")
    else:
        click.echo("❌ Delete failed", err=True)
        sys.exit(1)


@wasabi.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--bucket-type', '-b', default='uploads', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Bucket type to upload to')
@click.option('--remote-key', '-k', help='Custom remote key (defaults to filename)')
@click.option('--metadata', '-m', help='JSON metadata to attach')
@click.option('--public', is_flag=True, help='Make file publicly readable')
@click.option('--force-multipart', is_flag=True, help='Force multipart upload even for small files')
@click.option('--progress', is_flag=True, help='Show upload progress')
def upload_large(file_path, bucket_type, remote_key, metadata, public, force_multipart, progress):
    """Upload large files to Wasabi with multipart support"""
    file_path = Path(file_path)
    
    # Parse metadata if provided
    parsed_metadata = None
    if metadata:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            click.echo(f"❌ Invalid JSON metadata: {metadata}", err=True)
            sys.exit(1)
    
    # Check file size
    file_size = file_path.stat().st_size
    size_mb = file_size / 1024 / 1024
    size_gb = size_mb / 1024
    
    if size_gb > 1:
        click.echo(f"📁 File: {file_path.name}")
        click.echo(f"📊 Size: {size_gb:.2f} GB")
    else:
        click.echo(f"📁 File: {file_path.name}")
        click.echo(f"📊 Size: {size_mb:.1f} MB")
    
    click.echo(f"🪣 Bucket: {bucket_type}")
    click.echo(f"🔓 Public: {'Yes' if public else 'No'}")
    
    if not click.confirm('Continue with upload?'):
        click.echo("Upload cancelled.")
        return
    
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    # Progress callback
    def progress_callback(percent, uploaded_parts, total_parts):
        if progress:
            click.echo(f"📈 Progress: {percent:.1f}% ({uploaded_parts}/{total_parts} parts)")
    
    try:
        if force_multipart or file_size > storage.multipart_threshold:
            click.echo("🔄 Using multipart upload for large file...")
            url = storage.upload_large_file(
                file_path,
                bucket_type=bucket_type,
                remote_key=remote_key,
                metadata=parsed_metadata,
                public_read=public,
                progress_callback=progress_callback if progress else None
            )
        else:
            click.echo("🔄 Using standard upload...")
            url = storage.upload_file(
                file_path,
                bucket_type=bucket_type,
                remote_key=remote_key,
                metadata=parsed_metadata,
                public_read=public
            )
        
        if url:
            click.echo(f"✅ Upload successful!")
            click.echo(f"🌐 URL: {url}")
            
            if public:
                click.echo(f"🔗 Public URL: {url}")
        else:
            click.echo("❌ Upload failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Upload error: {e}", err=True)
        sys.exit(1)


@wasabi.command()
@click.argument('local_path', type=click.Path(exists=True))
@click.option('--bucket-type', '-b', default='outputs', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
@click.option('--key', '-k', help='Remote object key (defaults to filename)')
@click.option('--public', is_flag=True, help='Make file publicly readable')
@click.option('--metadata', '-m', help='JSON metadata to attach')
@click.option('--force-multipart', is_flag=True, help='Force multipart upload even for small files')
def upload_large(local_path, bucket_type, key, public, metadata, force_multipart):
    """Upload large file to Wasabi with progress tracking"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    # Parse metadata if provided
    file_metadata = None
    if metadata:
        try:
            file_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            click.echo("❌ Invalid JSON metadata", err=True)
            sys.exit(1)
    
    # Check file size
    file_path = Path(local_path)
    file_size = file_path.stat().st_size
    size_mb = file_size / 1024 / 1024
    
    click.echo(f"📤 Uploading large file: {file_path.name}")
    click.echo(f"   Size: {size_mb:.1f} MB")
    click.echo(f"   Bucket: {bucket_type}")
    click.echo(f"   Public: {'Yes' if public else 'No'}")
    
    # Progress callback
    def progress_callback(percent, completed_parts, total_parts):
        click.echo(f"   Progress: {percent:.1f}% ({completed_parts}/{total_parts} parts)")
    
    # Force multipart for demonstration if requested
    if force_multipart and file_size < storage.multipart_threshold:
        original_threshold = storage.multipart_threshold
        storage.multipart_threshold = 1024  # 1KB threshold
        
        try:
            url = storage.upload_large_file(
                local_path,
                bucket_type=bucket_type,
                remote_key=key,
                metadata=file_metadata,
                public_read=public,
                progress_callback=progress_callback
            )
        finally:
            storage.multipart_threshold = original_threshold
    else:
        url = storage.upload_large_file(
            local_path,
            bucket_type=bucket_type,
            remote_key=key,
            metadata=file_metadata,
            public_read=public,
            progress_callback=progress_callback
        )
    
    if url:
        click.echo(f"✅ Upload successful!")
        click.echo(f"   URL: {url}")
    else:
        click.echo("❌ Upload failed", err=True)
        sys.exit(1)


@wasabi.command()
@click.argument('local_path', type=click.Path(exists=True))
@click.argument('upload_id')
@click.option('--bucket-type', '-b', default='outputs', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
@click.option('--key', '-k', required=True, help='Remote object key')
def resume_upload(local_path, upload_id, bucket_type, key):
    """Resume a failed multipart upload"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"🔄 Resuming upload...")
    click.echo(f"   File: {local_path}")
    click.echo(f"   Upload ID: {upload_id}")
    click.echo(f"   Key: {key}")
    
    url = storage.resume_upload(
        local_path,
        bucket_type=bucket_type,
        upload_id=upload_id,
        remote_key=key
    )
    
    if url:
        click.echo(f"✅ Upload resumed and completed!")
        click.echo(f"   URL: {url}")
    else:
        click.echo("❌ Failed to resume upload", err=True)
        sys.exit(1)


@wasabi.command()
@click.option('--bucket-type', '-b', default='outputs', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
def list_uploads(bucket_type):
    """List ongoing multipart uploads"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"📋 Ongoing multipart uploads in {bucket_type} bucket:")
    
    uploads = storage.list_multipart_uploads(bucket_type)
    
    if not uploads:
        click.echo("   No ongoing uploads found")
        return
    
    table_data = []
    for upload in uploads:
        table_data.append([
            upload['key'],
            upload['upload_id'][:16] + '...',
            upload['initiated'].strftime('%Y-%m-%d %H:%M:%S'),
            upload.get('storage_class', 'STANDARD')
        ])
    
    headers = ["Key", "Upload ID", "Started", "Storage Class"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))


@wasabi.command()
@click.argument('upload_id')
@click.argument('key')
@click.option('--bucket-type', '-b', default='outputs', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
def upload_progress(upload_id, key, bucket_type):
    """Get progress of an ongoing multipart upload"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"📊 Upload progress for {key}:")
    
    progress = storage.get_upload_progress(bucket_type, upload_id, key)
    
    if 'error' in progress:
        click.echo(f"❌ Error: {progress['error']}")
        return
    
    click.echo(f"   Upload ID: {upload_id}")
    click.echo(f"   Parts completed: {progress['parts_completed']}")
    click.echo(f"   Total size uploaded: {progress['total_size_uploaded'] / 1024 / 1024:.1f} MB")
    if progress['last_modified']:
        click.echo(f"   Last modified: {progress['last_modified']}")


@wasabi.command()
@click.argument('upload_id')
@click.argument('key')
@click.option('--bucket-type', '-b', default='outputs', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
@click.confirmation_option(prompt='Are you sure you want to abort this upload?')
def abort_upload(upload_id, key, bucket_type):
    """Abort a multipart upload"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"🛑 Aborting upload {upload_id}...")
    
    if storage.abort_upload(bucket_type, upload_id, key):
        click.echo("✅ Upload aborted successfully")
    else:
        click.echo("❌ Failed to abort upload", err=True)
        sys.exit(1)


@wasabi.command()
def config():
    """Show large file upload configuration"""
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo("⚙️  Large File Upload Configuration:")
    click.echo(f"   Multipart threshold: {storage.multipart_threshold / 1024 / 1024:.1f} MB")
    click.echo(f"   Chunk size: {storage.chunk_size / 1024 / 1024:.1f} MB")
    click.echo(f"   Max concurrency: {storage.max_concurrency}")
    click.echo(f"   Endpoint: {storage.endpoint_url}")
    click.echo(f"   Region: {storage.region}")
    
    # Show environment variables
    click.echo(f"\n🔧 Environment Variables:")
    env_vars = [
        'WASABI_MULTIPART_THRESHOLD',
        'WASABI_MULTIPART_CHUNKSIZE', 
        'WASABI_MAX_CONCURRENCY',
        'WASABI_ACCESS_KEY',
        'WASABI_SECRET_KEY'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if var in ['WASABI_ACCESS_KEY', 'WASABI_SECRET_KEY']:
            display_value = f"{value[:8]}..." if value else "Not set"
        else:
            display_value = value or "Not set"
        click.echo(f"   {var}: {display_value}")


@wasabi.command()
@click.argument('size_mb', type=int)
@click.option('--bucket-type', '-b', default='temp', 
              type=click.Choice(['models', 'outputs', 'uploads', 'backups', 'temp']),
              help='Target bucket type')
def test_large_upload(size_mb, bucket_type):
    """Test large file upload with a generated file"""
    import tempfile
    import random
    import string
    
    if size_mb < 1:
        click.echo("❌ Size must be at least 1 MB", err=True)
        sys.exit(1)
    
    storage = get_wasabi_storage()
    if not storage:
        click.echo("❌ Failed to initialize Wasabi storage", err=True)
        sys.exit(1)
    
    click.echo(f"🧪 Testing large file upload with {size_mb} MB file...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
        tmp_path = tmp_file.name
        
        # Generate random data
        chunk_size = 1024 * 1024  # 1MB chunks
        for i in range(size_mb):
            data = ''.join(random.choices(string.ascii_letters + string.digits, k=chunk_size))
            tmp_file.write(data.encode())
            
            if i % 10 == 0:  # Progress every 10MB
                click.echo(f"   Generated: {i+1}/{size_mb} MB")
    
    click.echo(f"📁 Created test file: {tmp_path}")
    
    # Progress callback
    def progress_callback(percent, completed_parts, total_parts):
        click.echo(f"   Upload progress: {percent:.1f}% ({completed_parts}/{total_parts} parts)")
    
    try:
        # Upload with progress
        url = storage.upload_large_file(
            tmp_path,
            bucket_type=bucket_type,
            remote_key=f"test_large_file_{size_mb}MB.txt",
            metadata={'test': 'true', 'size_mb': str(size_mb)},
            progress_callback=progress_callback
        )
        
        if url:
            click.echo(f"✅ Test upload successful!")
            click.echo(f"   URL: {url}")
        else:
            click.echo("❌ Test upload failed", err=True)
            
    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
            click.echo(f"🗑️  Cleaned up test file")
        except:
            pass
