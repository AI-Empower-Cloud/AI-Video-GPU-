#!/usr/bin/env python3
"""
Large File Upload Example for AI Video GPU
Demonstrates uploading large files to Wasabi storage with progress tracking
"""

import sys
import os
import tempfile
import random
import string
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from cloud.wasabi_storage import WasabiStorage
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LargeFileUploadDemo:
    """Demo class for large file uploads"""
    
    def __init__(self):
        """Initialize the demo"""
        self.storage = None
        self.setup_storage()
    
    def setup_storage(self):
        """Setup Wasabi storage connection"""
        try:
            self.storage = WasabiStorage()
            
            # Test connection
            if not self.storage.test_connection():
                raise Exception("Failed to connect to Wasabi")
            
            logger.info("✅ Wasabi storage connected successfully")
            logger.info(f"   Endpoint: {self.storage.endpoint_url}")
            logger.info(f"   Region: {self.storage.region}")
            logger.info(f"   Multipart threshold: {self.storage.multipart_threshold / 1024 / 1024:.1f} MB")
            logger.info(f"   Chunk size: {self.storage.chunk_size / 1024 / 1024:.1f} MB")
            logger.info(f"   Max concurrency: {self.storage.max_concurrency}")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup storage: {e}")
            sys.exit(1)
    
    def create_test_file(self, size_mb: int, filename: str = None) -> str:
        """Create a test file of specified size"""
        if not filename:
            filename = f"test_file_{size_mb}MB_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        filepath = Path(tempfile.gettempdir()) / filename
        
        logger.info(f"📝 Creating test file: {filepath}")
        logger.info(f"   Size: {size_mb} MB")
        
        # Create file with random data
        chunk_size = 1024 * 1024  # 1MB chunks
        with open(filepath, 'w') as f:
            for i in range(size_mb):
                # Generate random text
                data = ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=chunk_size))
                f.write(data)
                
                # Progress update every 10MB
                if i % 10 == 0 and i > 0:
                    logger.info(f"   Generated: {i} MB")
        
        logger.info(f"✅ Test file created: {filepath}")
        return str(filepath)
    
    def upload_with_progress(self, filepath: str, bucket_type: str = 'temp') -> str:
        """Upload file with progress tracking"""
        filepath = Path(filepath)
        file_size = filepath.stat().st_size
        size_mb = file_size / 1024 / 1024
        
        logger.info(f"📤 Starting upload: {filepath.name}")
        logger.info(f"   Size: {size_mb:.1f} MB")
        logger.info(f"   Bucket: {bucket_type}")
        
        # Progress callback
        def progress_callback(percent, completed_parts, total_parts):
            logger.info(f"   📊 Progress: {percent:.1f}% ({completed_parts}/{total_parts} parts)")
        
        # Upload file
        start_time = datetime.now()
        
        url = self.storage.upload_large_file(
            filepath,
            bucket_type=bucket_type,
            remote_key=f"demo/{filepath.name}",
            metadata={
                'demo': 'true',
                'size_mb': str(size_mb),
                'created': datetime.now().isoformat()
            },
            progress_callback=progress_callback
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if url:
            logger.info(f"✅ Upload completed successfully!")
            logger.info(f"   URL: {url}")
            logger.info(f"   Duration: {duration:.2f} seconds")
            logger.info(f"   Average speed: {size_mb / duration:.2f} MB/s")
        else:
            logger.error("❌ Upload failed")
        
        return url
    
    def demo_small_file(self):
        """Demo small file upload (uses standard upload)"""
        logger.info("🔹 Demo 1: Small file upload (standard method)")
        
        # Create 10MB file
        filepath = self.create_test_file(10, "small_file_demo.txt")
        
        try:
            url = self.upload_with_progress(filepath)
            if url:
                logger.info("✅ Small file demo completed")
            else:
                logger.error("❌ Small file demo failed")
        finally:
            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info("🗑️  Cleaned up test file")
    
    def demo_large_file(self):
        """Demo large file upload (uses multipart upload)"""
        logger.info("🔹 Demo 2: Large file upload (multipart method)")
        
        # Create 100MB file
        filepath = self.create_test_file(100, "large_file_demo.txt")
        
        try:
            url = self.upload_with_progress(filepath)
            if url:
                logger.info("✅ Large file demo completed")
            else:
                logger.error("❌ Large file demo failed")
        finally:
            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info("🗑️  Cleaned up test file")
    
    def demo_very_large_file(self):
        """Demo very large file upload"""
        logger.info("🔹 Demo 3: Very large file upload (500MB)")
        
        # Create 500MB file
        filepath = self.create_test_file(500, "very_large_file_demo.txt")
        
        try:
            url = self.upload_with_progress(filepath)
            if url:
                logger.info("✅ Very large file demo completed")
            else:
                logger.error("❌ Very large file demo failed")
        finally:
            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info("🗑️  Cleaned up test file")
    
    def demo_multipart_uploads_list(self):
        """Demo listing multipart uploads"""
        logger.info("🔹 Demo 4: List multipart uploads")
        
        uploads = self.storage.list_multipart_uploads('temp')
        
        if uploads:
            logger.info(f"📋 Found {len(uploads)} ongoing uploads:")
            for upload in uploads:
                logger.info(f"   - {upload['key']} (ID: {upload['upload_id'][:16]}...)")
        else:
            logger.info("📋 No ongoing multipart uploads found")
    
    def demo_upload_limits(self):
        """Demo upload with various file sizes to show thresholds"""
        logger.info("🔹 Demo 5: Upload threshold demonstration")
        
        # Test different sizes around the multipart threshold
        test_sizes = [32, 64, 128]  # MB
        
        for size_mb in test_sizes:
            logger.info(f"\n--- Testing {size_mb}MB file ---")
            
            filepath = self.create_test_file(size_mb, f"threshold_test_{size_mb}MB.txt")
            
            try:
                # Check if it will use multipart
                file_size = Path(filepath).stat().st_size
                will_use_multipart = file_size > self.storage.multipart_threshold
                
                logger.info(f"   File size: {file_size / 1024 / 1024:.1f} MB")
                logger.info(f"   Will use multipart: {will_use_multipart}")
                
                url = self.upload_with_progress(filepath)
                
                if url:
                    logger.info(f"✅ Upload successful for {size_mb}MB file")
                else:
                    logger.error(f"❌ Upload failed for {size_mb}MB file")
                    
            finally:
                # Cleanup
                if os.path.exists(filepath):
                    os.remove(filepath)
    
    def run_all_demos(self):
        """Run all demonstrations"""
        logger.info("🚀 Starting Large File Upload Demonstrations")
        logger.info("=" * 60)
        
        try:
            self.demo_small_file()
            print("\n")
            
            self.demo_large_file()
            print("\n")
            
            self.demo_multipart_uploads_list()
            print("\n")
            
            self.demo_upload_limits()
            print("\n")
            
            # Skip very large file demo by default to save time
            # self.demo_very_large_file()
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  Demo interrupted by user")
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
        finally:
            logger.info("🏁 Demo completed")


def main():
    """Main function"""
    print("🎯 AI Video GPU - Large File Upload Demo")
    print("=" * 50)
    
    # Check environment
    required_env = ['WASABI_ACCESS_KEY', 'WASABI_SECRET_KEY']
    missing_env = [var for var in required_env if not os.getenv(var)]
    
    if missing_env:
        print(f"❌ Missing required environment variables: {missing_env}")
        print("Please set your Wasabi credentials:")
        print("   export WASABI_ACCESS_KEY=your_access_key")
        print("   export WASABI_SECRET_KEY=your_secret_key")
        sys.exit(1)
    
    # Run demo
    demo = LargeFileUploadDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()
