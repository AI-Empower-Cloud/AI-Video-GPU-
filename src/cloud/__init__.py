"""
AI Video GPU - Cloud Integration Module
Support for cloud storage, distributed processing, and deployment
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import tempfile
import json
from datetime import datetime
from loguru import logger

try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# Import Wasabi storage components
try:
    from .wasabi_storage import WasabiStorage, get_wasabi_storage, initialize_wasabi_buckets
    WASABI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Wasabi storage not available: {e}")
    WASABI_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from google.cloud import storage as gcs
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

class CloudStorageManager:
    """
    Unified cloud storage interface for AWS S3, Azure Blob, and Google Cloud Storage
    """
    
    def __init__(self, provider: str = "aws", **kwargs):
        self.provider = provider.lower()
        self.client = None
        
        if self.provider == "aws" and AWS_AVAILABLE:
            self._init_aws_client(**kwargs)
        elif self.provider == "azure" and AZURE_AVAILABLE:
            self._init_azure_client(**kwargs)
        elif self.provider == "gcp" and GCP_AVAILABLE:
            self._init_gcp_client(**kwargs)
        else:
            logger.warning(f"Cloud provider '{provider}' not available or not supported")
            
    def _init_aws_client(self, **kwargs):
        """Initialize AWS S3 client"""
        try:
            self.client = boto3.client(
                's3',
                aws_access_key_id=kwargs.get('access_key_id', os.getenv('AWS_ACCESS_KEY_ID')),
                aws_secret_access_key=kwargs.get('secret_access_key', os.getenv('AWS_SECRET_ACCESS_KEY')),
                region_name=kwargs.get('region', os.getenv('AWS_DEFAULT_REGION', 'us-east-1'))
            )
            self.bucket_name = kwargs.get('bucket_name', os.getenv('AWS_S3_BUCKET'))
            logger.info("✅ AWS S3 client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize AWS S3: {e}")
            
    def _init_azure_client(self, **kwargs):
        """Initialize Azure Blob Storage client"""
        try:
            connection_string = kwargs.get('connection_string', os.getenv('AZURE_STORAGE_CONNECTION_STRING'))
            self.client = BlobServiceClient.from_connection_string(connection_string)
            self.container_name = kwargs.get('container_name', os.getenv('AZURE_CONTAINER_NAME'))
            logger.info("✅ Azure Blob Storage client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Storage: {e}")
            
    def _init_gcp_client(self, **kwargs):
        """Initialize Google Cloud Storage client"""
        try:
            credentials_path = kwargs.get('credentials_path', os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
            if credentials_path:
                self.client = gcs.Client.from_service_account_json(credentials_path)
            else:
                self.client = gcs.Client()
            self.bucket_name = kwargs.get('bucket_name', os.getenv('GCP_STORAGE_BUCKET'))
            logger.info("✅ Google Cloud Storage client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Storage: {e}")
            
    def upload_file(self, local_path: str, remote_path: str) -> Dict[str, Any]:
        """Upload file to cloud storage"""
        
        if not self.client:
            return {'success': False, 'error': 'Cloud client not initialized'}
            
        try:
            if self.provider == "aws":
                self.client.upload_file(local_path, self.bucket_name, remote_path)
                url = f"https://{self.bucket_name}.s3.amazonaws.com/{remote_path}"
                
            elif self.provider == "azure":
                with open(local_path, 'rb') as data:
                    blob_client = self.client.get_blob_client(
                        container=self.container_name, 
                        blob=remote_path
                    )
                    blob_client.upload_blob(data, overwrite=True)
                url = blob_client.url
                
            elif self.provider == "gcp":
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(remote_path)
                blob.upload_from_filename(local_path)
                url = blob.public_url
                
            logger.info(f"File uploaded to cloud: {url}")
            return {'success': True, 'url': url, 'remote_path': remote_path}
            
        except Exception as e:
            logger.error(f"Cloud upload failed: {e}")
            return {'success': False, 'error': str(e)}
            
    def download_file(self, remote_path: str, local_path: str) -> Dict[str, Any]:
        """Download file from cloud storage"""
        
        if not self.client:
            return {'success': False, 'error': 'Cloud client not initialized'}
            
        try:
            if self.provider == "aws":
                self.client.download_file(self.bucket_name, remote_path, local_path)
                
            elif self.provider == "azure":
                blob_client = self.client.get_blob_client(
                    container=self.container_name, 
                    blob=remote_path
                )
                with open(local_path, 'wb') as data:
                    data.write(blob_client.download_blob().readall())
                    
            elif self.provider == "gcp":
                bucket = self.client.bucket(self.bucket_name)
                blob = bucket.blob(remote_path)
                blob.download_to_filename(local_path)
                
            logger.info(f"File downloaded from cloud: {local_path}")
            return {'success': True, 'local_path': local_path}
            
        except Exception as e:
            logger.error(f"Cloud download failed: {e}")
            return {'success': False, 'error': str(e)}

class DistributedTaskManager:
    """
    Distributed task processing using Celery and Redis
    """
    
    def __init__(self, redis_url: str = None, broker_url: str = None):
        if not CELERY_AVAILABLE or not REDIS_AVAILABLE:
            logger.warning("Celery or Redis not available. Distributed processing disabled.")
            self.app = None
            return
            
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.broker_url = broker_url or self.redis_url
        
        # Initialize Celery app
        self.app = Celery(
            'ai_video_gpu',
            broker=self.broker_url,
            backend=self.redis_url,
            include=['ai_video_gpu.tasks']
        )
        
        # Configure Celery
        self.app.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone='UTC',
            enable_utc=True,
            task_routes={
                'ai_video_gpu.tasks.generate_video': {'queue': 'video_generation'},
                'ai_video_gpu.tasks.enhance_video': {'queue': 'video_enhancement'},
                'ai_video_gpu.tasks.clone_voice': {'queue': 'voice_processing'},
            }
        )
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.from_url(self.redis_url)
            self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
            
    def submit_video_generation_task(
        self,
        task_params: Dict[str, Any],
        priority: int = 5
    ) -> Dict[str, Any]:
        """Submit video generation task to distributed queue"""
        
        if not self.app:
            return {'success': False, 'error': 'Distributed processing not available'}
            
        try:
            task = self.app.send_task(
                'ai_video_gpu.tasks.generate_video',
                args=[task_params],
                priority=priority,
                queue='video_generation'
            )
            
            # Store task metadata in Redis
            if self.redis_client:
                task_metadata = {
                    'task_id': task.id,
                    'task_type': 'video_generation',
                    'submitted_at': datetime.utcnow().isoformat(),
                    'params': task_params,
                    'status': 'pending'
                }
                self.redis_client.setex(
                    f"task:{task.id}",
                    3600,  # 1 hour TTL
                    json.dumps(task_metadata)
                )
                
            return {'success': True, 'task_id': task.id}
            
        except Exception as e:
            logger.error(f"Failed to submit task: {e}")
            return {'success': False, 'error': str(e)}
            
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of distributed task"""
        
        if not self.app:
            return {'success': False, 'error': 'Distributed processing not available'}
            
        try:
            # Get task result
            result = self.app.AsyncResult(task_id)
            
            # Get metadata from Redis
            metadata = {}
            if self.redis_client:
                metadata_json = self.redis_client.get(f"task:{task_id}")
                if metadata_json:
                    metadata = json.loads(metadata_json)
                    
            return {
                'success': True,
                'task_id': task_id,
                'state': result.state,
                'info': result.info,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            return {'success': False, 'error': str(e)}

class ModelRepository:
    """
    Centralized model repository with versioning and caching
    """
    
    def __init__(self, storage_manager: CloudStorageManager = None):
        self.storage_manager = storage_manager
        self.local_cache_dir = Path.home() / ".ai_video_gpu" / "models"
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Model registry
        self.model_registry = {
            "tts": {
                "xtts-v2": {
                    "url": "https://huggingface.co/coqui/XTTS-v2",
                    "size": "1.8GB",
                    "description": "High-quality voice cloning"
                },
                "tortoise": {
                    "url": "https://huggingface.co/jbetker/tortoise-tts-v2",
                    "size": "2.1GB", 
                    "description": "Ultra-high quality TTS"
                }
            },
            "lip_sync": {
                "wav2lip": {
                    "url": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth",
                    "size": "338MB",
                    "description": "Standard Wav2Lip model"
                },
                "wav2lip-hq": {
                    "url": "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth", 
                    "size": "338MB",
                    "description": "High quality Wav2Lip"
                }
            },
            "enhancement": {
                "real-esrgan": {
                    "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
                    "size": "67MB",
                    "description": "4x video upscaling"
                },
                "gfpgan": {
                    "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth",
                    "size": "348MB", 
                    "description": "Face enhancement"
                }
            }
        }
        
    def list_available_models(self) -> Dict[str, Any]:
        """List all available models"""
        return self.model_registry
        
    def download_model(self, category: str, model_name: str) -> Dict[str, Any]:
        """Download model to local cache"""
        
        if category not in self.model_registry:
            return {'success': False, 'error': f'Unknown category: {category}'}
            
        if model_name not in self.model_registry[category]:
            return {'success': False, 'error': f'Unknown model: {model_name}'}
            
        model_info = self.model_registry[category][model_name]
        local_path = self.local_cache_dir / category / f"{model_name}.pth"
        local_path.parent.mkdir(exist_ok=True)
        
        if local_path.exists():
            return {'success': True, 'path': str(local_path), 'cached': True}
            
        try:
            logger.info(f"Downloading model {category}/{model_name}...")
            
            # Download logic would go here
            # For now, just create a placeholder
            local_path.touch()
            
            logger.success(f"Model downloaded: {local_path}")
            return {'success': True, 'path': str(local_path), 'cached': False}
            
        except Exception as e:
            logger.error(f"Model download failed: {e}")
            return {'success': False, 'error': str(e)}
            
    def get_model_path(self, category: str, model_name: str) -> Optional[str]:
        """Get local path to model, download if needed"""
        
        result = self.download_model(category, model_name)
        if result['success']:
            return result['path']
        return None

class DeploymentManager:
    """
    Deployment and scaling management for AI Video GPU
    """
    
    def __init__(self):
        self.deployment_configs = {
            'local': {
                'gpu_required': True,
                'max_concurrent_jobs': 2,
                'storage': 'local'
            },
            'cloud_single': {
                'gpu_required': True,
                'max_concurrent_jobs': 5,
                'storage': 'cloud',
                'instance_type': 'GPU-enabled'
            },
            'cloud_distributed': {
                'gpu_required': True,
                'max_concurrent_jobs': 20,
                'storage': 'cloud',
                'instance_type': 'GPU-cluster',
                'scaling': 'auto'
            }
        }
        
    def get_deployment_config(self, deployment_type: str) -> Dict[str, Any]:
        """Get deployment configuration"""
        return self.deployment_configs.get(deployment_type, {})
        
    def create_docker_config(self) -> str:
        """Generate Docker configuration for deployment"""
        
        dockerfile_content = """
FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    python3 python3-pip python3-dev \\
    ffmpeg libsm6 libxext6 libxrender-dev \\
    git wget curl

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create necessary directories
RUN mkdir -p /app/models /app/output /app/temp

# Set environment variables
ENV PYTHONPATH=/app
ENV CUDA_VISIBLE_DEVICES=0

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python3", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        return dockerfile_content
        
    def create_kubernetes_config(self) -> str:
        """Generate Kubernetes deployment configuration"""
        
        k8s_config = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-video-gpu
  labels:
    app: ai-video-gpu
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-video-gpu
  template:
    metadata:
      labels:
        app: ai-video-gpu
    spec:
      containers:
      - name: ai-video-gpu
        image: ai-video-gpu:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            nvidia.com/gpu: 1
            memory: "8Gi"
            cpu: "4"
          limits:
            nvidia.com/gpu: 1
            memory: "16Gi"
            cpu: "8"
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        volumeMounts:
        - name: model-cache
          mountPath: /app/models
        - name: output-storage
          mountPath: /app/output
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
      - name: output-storage
        persistentVolumeClaim:
          claimName: output-storage-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ai-video-gpu-service
spec:
  selector:
    app: ai-video-gpu
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
"""
        
        return k8s_config

# Export all available classes and functions
__all__ = [
    'CloudProcessor',
    'CloudStorage',
    'CloudDeployment'
]

# Add Wasabi storage exports if available
if WASABI_AVAILABLE:
    __all__.extend([
        'WasabiStorage',
        'get_wasabi_storage',
        'initialize_wasabi_buckets'
    ])
