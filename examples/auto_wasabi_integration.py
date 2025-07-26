#!/usr/bin/env python3
"""
Automatic Wasabi Integration for AI Video GPU
Automatically uploads generated videos to Wasabi cloud storage with public URLs
"""

import os
import sys
import boto3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutoWasabiUploader:
    """Automatic Wasabi cloud storage integration for AI videos"""
    
    def __init__(self, 
                 access_key: str = None,
                 secret_key: str = None,
                 endpoint: str = "https://s3.wasabisys.com",
                 region: str = "us-east-1"):
        """Initialize Wasabi uploader with credentials"""
        
        # Get credentials from environment or parameters
        self.access_key = access_key or os.getenv('WASABI_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('WASABI_SECRET_KEY')
        self.endpoint = endpoint
        self.region = region
        
        # Bucket configuration
        self.buckets = {
            'videos': 'ai-video-gpu-outputs',
            'models': 'ai-video-gpu-models',
            'uploads': 'ai-video-gpu-uploads',
            'temp': 'ai-video-gpu-temp',
            'bhagavad_gita': 'ai-video-gpu-spiritual'
        }
        
        self.s3_client = None
        self.setup_client()
    
    def setup_client(self):
        """Setup Wasabi S3 client and verify connection"""
        
        if not self.access_key or not self.secret_key:
            logger.error("❌ Wasabi credentials not provided")
            logger.info("💡 Set WASABI_ACCESS_KEY and WASABI_SECRET_KEY environment variables")
            return False
        
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            # Test connection
            self.s3_client.list_buckets()
            logger.info("✅ Wasabi connection established")
            
            # Setup buckets
            self.setup_buckets()
            return True
            
        except Exception as e:
            logger.error(f"❌ Wasabi connection failed: {e}")
            self.s3_client = None
            return False
    
    def setup_buckets(self):
        """Create necessary buckets if they don't exist"""
        
        for bucket_type, bucket_name in self.buckets.items():
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                logger.info(f"✅ Bucket '{bucket_name}' exists")
            except ClientError:
                try:
                    # Create bucket
                    self.s3_client.create_bucket(Bucket=bucket_name)
                    
                    # Set public read policy for video bucket
                    if bucket_type == 'videos':
                        self.set_public_read_policy(bucket_name)
                    
                    logger.info(f"✅ Created bucket '{bucket_name}'")
                except Exception as e:
                    logger.warning(f"⚠️ Could not create bucket '{bucket_name}': {e}")
    
    def set_public_read_policy(self, bucket_name: str):
        """Set public read policy for video bucket"""
        
        public_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/public/*"
                }
            ]
        }
        
        try:
            import json
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(public_policy)
            )
            logger.info(f"✅ Set public read policy for {bucket_name}")
        except Exception as e:
            logger.warning(f"⚠️ Could not set public policy: {e}")
    
    def upload_video(self, 
                     local_path: str, 
                     video_type: str = 'standard',
                     make_public: bool = True,
                     metadata: Dict = None) -> Optional[str]:
        """Upload video to Wasabi and return public URL"""
        
        if not self.s3_client:
            logger.error("❌ Wasabi not configured - upload skipped")
            return None
        
        local_path = Path(local_path)
        if not local_path.exists():
            logger.error(f"❌ File not found: {local_path}")
            return None
        
        # Determine bucket and key
        if video_type == 'bhagavad_gita':
            bucket_name = self.buckets['bhagavad_gita']
            remote_key = f"spiritual_videos/{local_path.name}"
        else:
            bucket_name = self.buckets['videos']
            remote_key = f"public/{local_path.name}" if make_public else f"private/{local_path.name}"
        
        try:
            logger.info(f"📤 Uploading to Wasabi: {local_path.name}")
            
            # Prepare metadata
            upload_metadata = {
                'generated_by': 'AI_Video_GPU',
                'upload_date': datetime.now().isoformat(),
                'video_type': video_type,
                'file_size': str(local_path.stat().st_size)
            }
            
            if metadata:
                upload_metadata.update(metadata)
            
            # Upload parameters
            upload_args = {
                'Metadata': upload_metadata,
                'ContentType': 'video/mp4'
            }
            
            if make_public:
                upload_args['ACL'] = 'public-read'
            
            # Perform upload with progress tracking
            file_size = local_path.stat().st_size / 1024 / 1024  # MB
            
            def progress_callback(bytes_transferred):
                percent = (bytes_transferred / local_path.stat().st_size) * 100
                logger.info(f"   📊 Upload progress: {percent:.1f}%")
            
            # Upload file
            self.s3_client.upload_file(
                str(local_path),
                bucket_name,
                remote_key,
                ExtraArgs=upload_args,
                Callback=progress_callback if file_size > 10 else None
            )
            
            # Generate public URL
            public_url = f"{self.endpoint}/{bucket_name}/{remote_key}"
            
            logger.info(f"✅ Upload completed successfully!")
            logger.info(f"🌐 Public URL: {public_url}")
            logger.info(f"📏 File size: {file_size:.1f} MB")
            
            # Save URL to local file for reference
            self.save_url_reference(local_path.name, public_url, video_type)
            
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            return None
    
    def save_url_reference(self, filename: str, url: str, video_type: str):
        """Save video URL reference to local file"""
        
        try:
            # Create references directory
            ref_dir = Path.home() / ".ai_video_gpu" / "wasabi_urls"
            ref_dir.mkdir(parents=True, exist_ok=True)
            
            # Append to reference file
            ref_file = ref_dir / f"{video_type}_videos.txt"
            
            with open(ref_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{datetime.now().isoformat()}\n")
                f.write(f"File: {filename}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Type: {video_type}\n")
                f.write("-" * 50 + "\n")
            
            logger.info(f"📋 URL reference saved: {ref_file}")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not save URL reference: {e}")
    
    def list_videos(self, video_type: str = 'standard') -> List[Dict]:
        """List uploaded videos from Wasabi"""
        
        if not self.s3_client:
            return []
        
        try:
            if video_type == 'bhagavad_gita':
                bucket_name = self.buckets['bhagavad_gita']
                prefix = 'spiritual_videos/'
            else:
                bucket_name = self.buckets['videos']
                prefix = 'public/'
            
            response = self.s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix
            )
            
            videos = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    video_info = {
                        'name': obj['Key'].split('/')[-1],
                        'size_mb': round(obj['Size'] / 1024 / 1024, 1),
                        'url': f"{self.endpoint}/{bucket_name}/{obj['Key']}",
                        'uploaded': obj['LastModified'],
                        'type': video_type
                    }
                    videos.append(video_info)
            
            return videos
            
        except Exception as e:
            logger.error(f"❌ Could not list videos: {e}")
            return []
    
    def get_video_stats(self) -> Dict[str, Any]:
        """Get statistics about uploaded videos"""
        
        stats = {
            'total_videos': 0,
            'total_size_mb': 0,
            'by_type': {},
            'recent_uploads': []
        }
        
        for video_type in ['standard', 'bhagavad_gita']:
            videos = self.list_videos(video_type)
            stats['by_type'][video_type] = {
                'count': len(videos),
                'size_mb': sum(v['size_mb'] for v in videos)
            }
            stats['total_videos'] += len(videos)
            stats['total_size_mb'] += sum(v['size_mb'] for v in videos)
            
            # Add recent videos
            stats['recent_uploads'].extend(videos[-3:])  # Last 3 per type
        
        # Sort recent uploads by date
        stats['recent_uploads'].sort(key=lambda x: x['uploaded'], reverse=True)
        stats['recent_uploads'] = stats['recent_uploads'][:5]  # Top 5 most recent
        
        return stats


def setup_auto_wasabi_integration():
    """Setup automatic Wasabi integration for AI Video GPU"""
    
    print("🌊 Setting up automatic Wasabi integration...")
    print("=" * 50)
    
    # Check for credentials
    access_key = os.getenv('WASABI_ACCESS_KEY')
    secret_key = os.getenv('WASABI_SECRET_KEY')
    
    if not access_key or not secret_key:
        print("❌ Wasabi credentials not found")
        print("\n💡 To enable automatic Wasabi uploads:")
        print("1. Get Wasabi credentials from https://wasabi.com")
        print("2. Set environment variables:")
        print("   export WASABI_ACCESS_KEY='your_access_key'")
        print("   export WASABI_SECRET_KEY='your_secret_key'")
        print("3. Re-run this setup")
        return None
    
    # Initialize uploader
    uploader = AutoWasabiUploader()
    
    if uploader.s3_client:
        print("✅ Wasabi integration ready!")
        print(f"📦 Buckets configured: {len(uploader.buckets)}")
        
        # Show stats if videos exist
        stats = uploader.get_video_stats()
        if stats['total_videos'] > 0:
            print(f"📊 Existing videos: {stats['total_videos']}")
            print(f"💾 Total storage: {stats['total_size_mb']:.1f} MB")
        
        print("\n🎯 Features enabled:")
        print("✅ Automatic video upload after generation")
        print("✅ Public URLs for instant sharing")
        print("✅ Cloud backup and storage")
        print("✅ Global accessibility")
        
        return uploader
    else:
        print("❌ Wasabi setup failed")
        return None


def main():
    """Main function to demonstrate auto Wasabi integration"""
    
    print("🌊 AI Video GPU - Automatic Wasabi Integration")
    print("=" * 60)
    print("Automatically upload generated videos to cloud storage")
    print()
    
    # Setup integration
    uploader = setup_auto_wasabi_integration()
    
    if uploader:
        # Show video library
        print("\n📚 Your Wasabi Video Library:")
        
        for video_type in ['standard', 'bhagavad_gita']:
            videos = uploader.list_videos(video_type)
            if videos:
                print(f"\n🎬 {video_type.title()} Videos ({len(videos)}):")
                for video in videos[-3:]:  # Show last 3
                    print(f"   📹 {video['name']} ({video['size_mb']} MB)")
                    print(f"      🌐 {video['url']}")
        
        # Show statistics
        stats = uploader.get_video_stats()
        print(f"\n📊 Storage Statistics:")
        print(f"   Total videos: {stats['total_videos']}")
        print(f"   Total storage: {stats['total_size_mb']:.1f} MB")
        print(f"   Storage cost: ~${stats['total_size_mb'] * 0.0059:.2f}/month")
        
        print(f"\n✨ Integration ready! All new videos will auto-upload to Wasabi.")
        
    else:
        print("\n💡 Set up Wasabi credentials to enable automatic cloud uploads!")


if __name__ == "__main__":
    main()
