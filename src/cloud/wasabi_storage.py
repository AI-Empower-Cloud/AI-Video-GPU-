"""
Wasabi Cloud Storage Integration
S3-Compatible Object Storage for AI Video GPU System
"""

import os
import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
import aiofiles
import aiohttp
from datetime import datetime, timedelta
import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class WasabiStorage:
    """Wasabi cloud storage client for AI Video GPU system with large file support"""
    
    def __init__(self, 
                 access_key: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 endpoint_url: str = "https://s3.wasabisys.com",
                 region: str = "us-east-1"):
        """
        Initialize Wasabi storage client
        
        Args:
            access_key: Wasabi access key
            secret_key: Wasabi secret key
            endpoint_url: Wasabi endpoint URL
            region: Wasabi region
        """
        self.access_key = access_key or os.getenv('WASABI_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('WASABI_SECRET_KEY')
        self.endpoint_url = endpoint_url or os.getenv('WASABI_ENDPOINT_URL', 'https://s3.wasabisys.com')
        self.region = region or os.getenv('WASABI_REGION', 'us-east-1')
        
        if not self.access_key or not self.secret_key:
            raise ValueError("Wasabi credentials not provided")
        
        # Enhanced configuration for large file uploads
        self.config = Config(
            region_name=self.region,
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            max_pool_connections=50,
            # Enhanced settings for large files
            s3={
                'multipart_threshold': int(os.getenv('WASABI_MULTIPART_THRESHOLD', '67108864')),  # 64MB
                'multipart_chunksize': int(os.getenv('WASABI_MULTIPART_CHUNKSIZE', '8388608')),  # 8MB
                'max_concurrency': int(os.getenv('WASABI_MAX_CONCURRENCY', '10')),
                'max_bandwidth': None,  # No bandwidth limit
                'use_threads': True
            }
        )
        
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=self.config
        )
        
        # Default bucket configuration
        self.buckets = {
            'models': os.getenv('WASABI_MODELS_BUCKET', 'ai-video-gpu-models'),
            'outputs': os.getenv('WASABI_OUTPUTS_BUCKET', 'ai-video-gpu-outputs'),
            'uploads': os.getenv('WASABI_UPLOADS_BUCKET', 'ai-video-gpu-uploads'),
            'backups': os.getenv('WASABI_BACKUPS_BUCKET', 'ai-video-gpu-backups'),
            'temp': os.getenv('WASABI_TEMP_BUCKET', 'ai-video-gpu-temp')
        }
        
        # Upload settings for large files
        self.multipart_threshold = int(os.getenv('WASABI_MULTIPART_THRESHOLD', '67108864'))  # 64MB
        self.chunk_size = int(os.getenv('WASABI_MULTIPART_CHUNKSIZE', '8388608'))  # 8MB
        self.max_concurrency = int(os.getenv('WASABI_MAX_CONCURRENCY', '10'))
        
        logger.info(f"Initialized Wasabi storage client for region: {self.region}")
        logger.info(f"Multipart threshold: {self.multipart_threshold / 1024 / 1024:.1f}MB")
        logger.info(f"Chunk size: {self.chunk_size / 1024 / 1024:.1f}MB")
    
    def test_connection(self) -> bool:
        """Test connection to Wasabi"""
        try:
            self.client.list_buckets()
            logger.info("Wasabi connection test successful")
            return True
        except Exception as e:
            logger.error(f"Wasabi connection test failed: {e}")
            return False
    
    def create_bucket(self, bucket_name: str, public_read: bool = False) -> bool:
        """
        Create a bucket in Wasabi
        
        Args:
            bucket_name: Name of the bucket to create
            public_read: Whether to allow public read access
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if bucket exists
            if self.bucket_exists(bucket_name):
                logger.info(f"Bucket {bucket_name} already exists")
                return True
            
            # Create bucket
            self.client.create_bucket(Bucket=bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
            
            # Set public read policy if requested
            if public_read:
                self.set_bucket_public_read(bucket_name)
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to create bucket {bucket_name}: {e}")
            return False
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if bucket exists"""
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            return False
    
    def set_bucket_public_read(self, bucket_name: str) -> bool:
        """Set bucket to allow public read access"""
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            self.client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(policy)
            )
            logger.info(f"Set public read policy for bucket: {bucket_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to set public read policy for {bucket_name}: {e}")
            return False
    
    def upload_file(self, 
                   local_path: Union[str, Path], 
                   bucket_type: str = 'outputs',
                   remote_key: Optional[str] = None,
                   metadata: Optional[Dict[str, str]] = None,
                   public_read: bool = False) -> Optional[str]:
        """
        Upload file to Wasabi
        
        Args:
            local_path: Local file path
            bucket_type: Type of bucket (models, outputs, uploads, backups, temp)
            remote_key: Remote object key (defaults to filename)
            metadata: Additional metadata
            public_read: Whether file should be publicly readable
            
        Returns:
            URL of uploaded file or None if failed
        """
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return None
            
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return None
            
            # Ensure bucket exists
            self.create_bucket(bucket_name, public_read=public_read)
            
            # Generate remote key if not provided
            if not remote_key:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                remote_key = f"{timestamp}_{local_path.name}"
            
            # Prepare extra args
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            if public_read:
                extra_args['ACL'] = 'public-read'
            
            # Add content type based on file extension
            content_type = self._get_content_type(local_path)
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Check file size and choose upload method
            file_size = local_path.stat().st_size
            size_mb = file_size / 1024 / 1024
            
            if file_size > self.multipart_threshold:
                # Use multipart upload for large files
                logger.info(f"Using multipart upload for large file: {size_mb:.1f}MB")
                self._multipart_upload(local_path, bucket_name, remote_key, extra_args)
            else:
                # Regular upload for smaller files
                logger.info(f"Using standard upload for file: {size_mb:.1f}MB")
                self.client.upload_file(
                    str(local_path),
                    bucket_name,
                    remote_key,
                    ExtraArgs=extra_args
                )
            
            # Generate URL
            url = f"{self.endpoint_url}/{bucket_name}/{remote_key}"
            logger.info(f"Uploaded {local_path} to {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return None
    
    def _multipart_upload(self, 
                         local_path: Path, 
                         bucket_name: str, 
                         remote_key: str, 
                         extra_args: Dict[str, Any]) -> None:
        """Perform multipart upload for large files"""
        try:
            file_size = local_path.stat().st_size
            part_size = self.chunk_size
            part_count = (file_size + part_size - 1) // part_size
            
            logger.info(f"Starting multipart upload for {remote_key}")
            logger.info(f"File size: {file_size / 1024 / 1024:.1f}MB, Parts: {part_count}")
            
            # Create multipart upload
            response = self.client.create_multipart_upload(
                Bucket=bucket_name,
                Key=remote_key,
                **extra_args
            )
            upload_id = response['UploadId']
            logger.info(f"Created multipart upload: {upload_id}")
            
            # Upload parts in parallel
            parts = []
            with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                futures = {}
                
                for part_number in range(1, part_count + 1):
                    offset = (part_number - 1) * part_size
                    size = min(part_size, file_size - offset)
                    
                    future = executor.submit(
                        self._upload_part,
                        bucket_name,
                        remote_key,
                        upload_id,
                        part_number,
                        str(local_path),
                        offset,
                        size
                    )
                    futures[part_number] = future
                
                # Collect results
                for part_number in sorted(futures.keys()):
                    try:
                        etag = futures[part_number].result()
                        parts.append({
                            'ETag': etag,
                            'PartNumber': part_number
                        })
                        logger.debug(f"Part {part_number}/{part_count} uploaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to upload part {part_number}: {e}")
                        # Abort multipart upload on failure
                        self.client.abort_multipart_upload(
                            Bucket=bucket_name,
                            Key=remote_key,
                            UploadId=upload_id
                        )
                        raise e
            
            # Complete multipart upload
            self.client.complete_multipart_upload(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            logger.info(f"Successfully completed multipart upload for {remote_key}")
            
        except Exception as e:
            logger.error(f"Multipart upload failed for {remote_key}: {e}")
            raise e
    
    def _upload_part(self, 
                    bucket_name: str, 
                    remote_key: str, 
                    upload_id: str, 
                    part_number: int, 
                    file_path: str, 
                    offset: int, 
                    size: int) -> str:
        """Upload a single part of a multipart upload"""
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(size)
            
            response = self.client.upload_part(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=data
            )
            
            return response['ETag']
            
        except Exception as e:
            logger.error(f"Failed to upload part {part_number}: {e}")
            raise e

    def upload_large_file(self, 
                         local_path: Union[str, Path], 
                         bucket_type: str = 'outputs',
                         remote_key: Optional[str] = None,
                         metadata: Optional[Dict[str, str]] = None,
                         public_read: bool = False,
                         progress_callback: Optional[callable] = None) -> Optional[str]:
        """
        Upload large file to Wasabi with progress tracking
        
        Args:
            local_path: Local file path
            bucket_type: Type of bucket (models, outputs, uploads, backups, temp)
            remote_key: Remote object key (defaults to filename)
            metadata: Additional metadata
            public_read: Whether file should be publicly readable
            progress_callback: Callback function for progress updates
            
        Returns:
            URL of uploaded file or None if failed
        """
        try:
            local_path = Path(local_path)
            if not local_path.exists():
                logger.error(f"Local file not found: {local_path}")
                return None
            
            file_size = local_path.stat().st_size
            size_mb = file_size / 1024 / 1024
            logger.info(f"Uploading large file: {local_path.name} ({size_mb:.1f}MB)")
            
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return None
            
            # Ensure bucket exists
            self.create_bucket(bucket_name, public_read=public_read)
            
            # Generate remote key if not provided
            if not remote_key:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                remote_key = f"large_files/{timestamp}_{local_path.name}"
            
            # Prepare extra args
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            if public_read:
                extra_args['ACL'] = 'public-read'
            
            # Add content type based on file extension
            content_type = self._get_content_type(local_path)
            if content_type:
                extra_args['ContentType'] = content_type
            
            # Use multipart upload for better reliability
            self._multipart_upload_with_progress(
                local_path, bucket_name, remote_key, extra_args, progress_callback
            )
            
            # Generate URL
            url = f"{self.endpoint_url}/{bucket_name}/{remote_key}"
            logger.info(f"Successfully uploaded large file to {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload large file {local_path}: {e}")
            return None
    
    def _multipart_upload_with_progress(self, 
                                       local_path: Path, 
                                       bucket_name: str, 
                                       remote_key: str, 
                                       extra_args: Dict[str, Any],
                                       progress_callback: Optional[callable] = None) -> None:
        """Multipart upload with progress tracking"""
        try:
            file_size = local_path.stat().st_size
            part_size = self.chunk_size
            part_count = (file_size + part_size - 1) // part_size
            
            logger.info(f"Starting multipart upload with progress tracking")
            logger.info(f"File: {remote_key}, Size: {file_size / 1024 / 1024:.1f}MB, Parts: {part_count}")
            
            # Create multipart upload
            response = self.client.create_multipart_upload(
                Bucket=bucket_name,
                Key=remote_key,
                **extra_args
            )
            upload_id = response['UploadId']
            
            # Progress tracking
            uploaded_parts = 0
            lock = threading.Lock()
            
            def update_progress():
                nonlocal uploaded_parts
                with lock:
                    uploaded_parts += 1
                    progress = (uploaded_parts / part_count) * 100
                    logger.info(f"Upload progress: {progress:.1f}% ({uploaded_parts}/{part_count} parts)")
                    if progress_callback:
                        progress_callback(progress, uploaded_parts, part_count)
            
            # Upload parts in parallel
            parts = []
            with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                futures = {}
                
                for part_number in range(1, part_count + 1):
                    offset = (part_number - 1) * part_size
                    size = min(part_size, file_size - offset)
                    
                    future = executor.submit(
                        self._upload_part_with_progress,
                        bucket_name,
                        remote_key,
                        upload_id,
                        part_number,
                        str(local_path),
                        offset,
                        size,
                        update_progress
                    )
                    futures[part_number] = future
                
                # Collect results
                for part_number in sorted(futures.keys()):
                    try:
                        etag = futures[part_number].result()
                        parts.append({
                            'ETag': etag,
                            'PartNumber': part_number
                        })
                    except Exception as e:
                        logger.error(f"Failed to upload part {part_number}: {e}")
                        self.client.abort_multipart_upload(
                            Bucket=bucket_name,
                            Key=remote_key,
                            UploadId=upload_id
                        )
                        raise e
            
            # Complete multipart upload
            self.client.complete_multipart_upload(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            logger.info(f"Successfully completed multipart upload for {remote_key}")
            if progress_callback:
                progress_callback(100, part_count, part_count)
            
        except Exception as e:
            logger.error(f"Multipart upload with progress failed: {e}")
            raise e
    
    def _upload_part_with_progress(self, 
                                  bucket_name: str, 
                                  remote_key: str, 
                                  upload_id: str, 
                                  part_number: int, 
                                  file_path: str, 
                                  offset: int, 
                                  size: int,
                                  progress_callback: callable) -> str:
        """Upload a single part with progress callback"""
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(size)
            
            response = self.client.upload_part(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=data
            )
            
            # Update progress
            progress_callback()
            
            return response['ETag']
            
        except Exception as e:
            logger.error(f"Failed to upload part {part_number}: {e}")
            raise e
    
    def resume_upload(self, 
                     local_path: Union[str, Path], 
                     bucket_type: str = 'outputs',
                     upload_id: str = None,
                     remote_key: str = None) -> Optional[str]:
        """
        Resume a failed multipart upload
        
        Args:
            local_path: Local file path
            bucket_type: Type of bucket
            upload_id: Upload ID from previous attempt
            remote_key: Remote object key
            
        Returns:
            URL of uploaded file or None if failed
        """
        try:
            local_path = Path(local_path)
            bucket_name = self.buckets.get(bucket_type)
            
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return None
            
            # List existing parts
            response = self.client.list_parts(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id
            )
            
            existing_parts = {part['PartNumber']: part['ETag'] for part in response.get('Parts', [])}
            logger.info(f"Found {len(existing_parts)} existing parts for upload {upload_id}")
            
            # Calculate remaining parts
            file_size = local_path.stat().st_size
            part_size = self.chunk_size
            part_count = (file_size + part_size - 1) // part_size
            
            remaining_parts = []
            for part_number in range(1, part_count + 1):
                if part_number not in existing_parts:
                    remaining_parts.append(part_number)
            
            logger.info(f"Resuming upload: {len(remaining_parts)} parts remaining")
            
            # Upload remaining parts
            with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
                futures = {}
                
                for part_number in remaining_parts:
                    offset = (part_number - 1) * part_size
                    size = min(part_size, file_size - offset)
                    
                    future = executor.submit(
                        self._upload_part,
                        bucket_name,
                        remote_key,
                        upload_id,
                        part_number,
                        str(local_path),
                        offset,
                        size
                    )
                    futures[part_number] = future
                
                # Wait for completion
                for part_number, future in futures.items():
                    try:
                        etag = future.result()
                        existing_parts[part_number] = etag
                        logger.info(f"Uploaded remaining part {part_number}")
                    except Exception as e:
                        logger.error(f"Failed to upload part {part_number}: {e}")
                        return None
            
            # Complete multipart upload
            parts = [{'ETag': existing_parts[part_number], 'PartNumber': part_number} 
                    for part_number in sorted(existing_parts.keys())]
            
            self.client.complete_multipart_upload(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            url = f"{self.endpoint_url}/{bucket_name}/{remote_key}"
            logger.info(f"Successfully resumed and completed upload: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Failed to resume upload: {e}")
            return None
    
    def get_upload_progress(self, bucket_type: str, upload_id: str, remote_key: str) -> Dict[str, Any]:
        """Get progress of an ongoing multipart upload"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                return {'error': f'Unknown bucket type: {bucket_type}'}
            
            response = self.client.list_parts(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id
            )
            
            parts = response.get('Parts', [])
            total_size = sum(part['Size'] for part in parts)
            
            return {
                'upload_id': upload_id,
                'parts_completed': len(parts),
                'total_size_uploaded': total_size,
                'last_modified': max([part['LastModified'] for part in parts]) if parts else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get upload progress: {e}")
            return {'error': str(e)}
    
    def abort_upload(self, bucket_type: str, upload_id: str, remote_key: str) -> bool:
        """Abort a multipart upload"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return False
            
            self.client.abort_multipart_upload(
                Bucket=bucket_name,
                Key=remote_key,
                UploadId=upload_id
            )
            
            logger.info(f"Aborted multipart upload: {upload_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to abort upload: {e}")
            return False
    
    def list_multipart_uploads(self, bucket_type: str) -> List[Dict[str, Any]]:
        """List ongoing multipart uploads"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return []
            
            response = self.client.list_multipart_uploads(Bucket=bucket_name)
            
            uploads = []
            for upload in response.get('Uploads', []):
                uploads.append({
                    'key': upload['Key'],
                    'upload_id': upload['UploadId'],
                    'initiated': upload['Initiated'],
                    'initiator': upload.get('Initiator', {}),
                    'storage_class': upload.get('StorageClass', 'STANDARD')
                })
            
            return uploads
            
        except Exception as e:
            logger.error(f"Failed to list multipart uploads: {e}")
            return []
    
    def _get_content_type(self, file_path: Path) -> Optional[str]:
        """Get content type based on file extension"""
        content_types = {
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            '.webm': 'video/webm',
            '.flv': 'video/x-flv',
            '.wmv': 'video/x-ms-wmv',
            '.m4v': 'video/x-m4v',
            '.3gp': 'video/3gpp',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.m4a': 'audio/mp4',
            '.wma': 'audio/x-ms-wma',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.md': 'text/markdown',
            '.yml': 'application/x-yaml',
            '.yaml': 'application/x-yaml',
            '.ini': 'text/plain',
            '.conf': 'text/plain',
            '.log': 'text/plain'
        }
        
        suffix = file_path.suffix.lower()
        return content_types.get(suffix, 'application/octet-stream')
    
    def get_storage_usage(self) -> Dict[str, Dict[str, Any]]:
        """Get storage usage statistics for all buckets"""
        usage = {}
        
        for bucket_type, bucket_name in self.buckets.items():
            try:
                if not self.bucket_exists(bucket_name):
                    usage[bucket_type] = {
                        'exists': False,
                        'file_count': 0,
                        'total_size_bytes': 0,
                        'total_size_mb': 0,
                        'total_size_gb': 0
                    }
                    continue
                
                # List objects in bucket
                response = self.client.list_objects_v2(Bucket=bucket_name)
                objects = response.get('Contents', [])
                
                file_count = len(objects)
                total_size_bytes = sum(obj['Size'] for obj in objects)
                total_size_mb = total_size_bytes / 1024 / 1024
                total_size_gb = total_size_mb / 1024
                
                usage[bucket_type] = {
                    'exists': True,
                    'bucket_name': bucket_name,
                    'file_count': file_count,
                    'total_size_bytes': total_size_bytes,
                    'total_size_mb': total_size_mb,
                    'total_size_gb': total_size_gb,
                    'last_modified': max([obj['LastModified'] for obj in objects]) if objects else None
                }
                
            except Exception as e:
                logger.error(f"Failed to get usage for bucket {bucket_name}: {e}")
                usage[bucket_type] = {
                    'exists': False,
                    'error': str(e),
                    'file_count': 0,
                    'total_size_bytes': 0,
                    'total_size_mb': 0,
                    'total_size_gb': 0
                }
        
        return usage
    
    def list_files(self, bucket_type: str, prefix: str = '', limit: int = 100) -> List[Dict[str, Any]]:
        """List files in a bucket"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return []
            
            # List objects with pagination
            response = self.client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"'),
                    'storage_class': obj.get('StorageClass', 'STANDARD'),
                    'url': f"{self.endpoint_url}/{bucket_name}/{obj['Key']}"
                })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files in bucket {bucket_type}: {e}")
            return []
    
    def download_file(self, bucket_type: str, remote_key: str, local_path: Union[str, Path]) -> bool:
        """Download file from Wasabi"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return False
            
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            self.client.download_file(bucket_name, remote_key, str(local_path))
            
            logger.info(f"Downloaded {remote_key} to {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {remote_key}: {e}")
            return False
    
    def delete_file(self, bucket_type: str, remote_key: str) -> bool:
        """Delete file from Wasabi"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return False
            
            # Delete object
            self.client.delete_object(Bucket=bucket_name, Key=remote_key)
            
            logger.info(f"Deleted {remote_key} from {bucket_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete {remote_key}: {e}")
            return False
    
    def generate_presigned_url(self, bucket_type: str, remote_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for temporary access"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return None
            
            # Generate presigned URL
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': remote_key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for {remote_key} (expires in {expiration}s)")
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {remote_key}: {e}")
            return None
    
    def file_exists(self, bucket_type: str, remote_key: str) -> bool:
        """Check if file exists in Wasabi"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                return False
            
            # Check if object exists
            self.client.head_object(Bucket=bucket_name, Key=remote_key)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Failed to check if {remote_key} exists: {e}")
            return False
    
    def get_file_info(self, bucket_type: str, remote_key: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            bucket_name = self.buckets.get(bucket_type)
            if not bucket_name:
                logger.error(f"Unknown bucket type: {bucket_type}")
                return None
            
            # Get object metadata
            response = self.client.head_object(Bucket=bucket_name, Key=remote_key)
            
            return {
                'key': remote_key,
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'etag': response['ETag'].strip('"'),
                'content_type': response.get('ContentType', 'application/octet-stream'),
                'metadata': response.get('Metadata', {}),
                'storage_class': response.get('StorageClass', 'STANDARD'),
                'url': f"{self.endpoint_url}/{bucket_name}/{remote_key}"
            }
            
        except Exception as e:
            logger.error(f"Failed to get info for {remote_key}: {e}")
            return None
    
    def cleanup_temp_files(self, older_than_days: int = 7) -> int:
        """Clean up temporary files older than specified days"""
        try:
            bucket_name = self.buckets.get('temp')
            if not bucket_name:
                logger.error("Temp bucket not configured")
                return 0
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            
            # List all objects in temp bucket
            response = self.client.list_objects_v2(Bucket=bucket_name)
            objects = response.get('Contents', [])
            
            # Find old objects
            old_objects = [
                obj for obj in objects 
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date
            ]
            
            # Delete old objects
            deleted_count = 0
            for obj in old_objects:
                try:
                    self.client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                    deleted_count += 1
                    logger.info(f"Deleted old temp file: {obj['Key']}")
                except Exception as e:
                    logger.error(f"Failed to delete {obj['Key']}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} temporary files older than {older_than_days} days")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
            return 0


# Helper functions for easy access
def get_wasabi_storage() -> Optional[WasabiStorage]:
    """Get a configured Wasabi storage instance"""
    try:
        return WasabiStorage()
    except Exception as e:
        logger.error(f"Failed to initialize Wasabi storage: {e}")
        return None


def initialize_wasabi_buckets() -> bool:
    """Initialize all Wasabi buckets"""
    try:
        storage = get_wasabi_storage()
        if not storage:
            return False
        
        success = True
        for bucket_type, bucket_name in storage.buckets.items():
            if not storage.create_bucket(bucket_name):
                success = False
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to initialize buckets: {e}")
        return False
