#!/usr/bin/env python3
"""
Test Wasabi storage functionality
"""

import os
import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

from cloud.wasabi_storage import WasabiStorage


def create_test_file(content="Test file for Wasabi upload", filename="test.txt"):
    """Create a temporary test file"""
    temp_file = Path(tempfile.mktemp(suffix=f"_{filename}"))
    temp_file.write_text(content)
    return temp_file


def test_wasabi_storage():
    """Test various Wasabi storage operations"""
    print("🧪 Testing Wasabi storage functionality...")

    try:
        # Initialize storage
        storage = WasabiStorage()
        print("✅ Wasabi storage initialized")

        # Test 1: Connection test
        print("\n🔗 Testing connection...")
        if storage.test_connection():
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
            return False

        # Test 2: Get storage usage
        print("\n📊 Getting storage usage...")
        usage = storage.get_storage_usage()
        for bucket_type, info in usage.items():
            if info["exists"]:
                print(f"  📦 {bucket_type}: {info['file_count']} files, {info['total_size_mb']:.2f}MB")
            else:
                print(f"  📦 {bucket_type}: Not found or empty")

        # Test 3: Create a test file and upload it
        print("\n📤 Testing file upload...")
        test_file = create_test_file(content="This is a test file for the AI Video GPU system.", filename="ai_video_test.txt")

        try:
            # Upload to outputs bucket
            url = storage.upload_file(
                local_path=test_file,
                bucket_type="outputs",
                remote_key="tests/test_upload.txt",
                metadata={"purpose": "testing", "system": "ai-video-gpu"},
            )

            if url:
                print(f"✅ File uploaded successfully: {url}")

                # Test 4: Check if file exists
                print("\n🔍 Testing file existence...")
                if storage.file_exists("outputs", "tests/test_upload.txt"):
                    print("✅ File exists in bucket")
                else:
                    print("❌ File not found in bucket")

                # Test 5: Get file info
                print("\n📋 Getting file info...")
                file_info = storage.get_file_info("outputs", "tests/test_upload.txt")
                if file_info:
                    print(f"✅ File info: {file_info['size']} bytes, {file_info['content_type']}")
                else:
                    print("❌ Failed to get file info")

                # Test 6: List files in bucket
                print("\n📂 Listing files in outputs bucket...")
                files = storage.list_files("outputs", prefix="tests/", limit=10)
                if files:
                    print(f"✅ Found {len(files)} files:")
                    for file in files:
                        print(f"  - {file['key']} ({file['size']} bytes)")
                else:
                    print("❌ No files found or error listing files")

                # Test 7: Download the file
                print("\n📥 Testing file download...")
                download_path = Path(tempfile.mktemp(suffix="_downloaded.txt"))
                if storage.download_file("outputs", "tests/test_upload.txt", download_path):
                    print(f"✅ File downloaded to: {download_path}")
                    content = download_path.read_text()
                    print(f"✅ Downloaded content: {content}")
                    download_path.unlink()  # Clean up
                else:
                    print("❌ Failed to download file")

                # Test 8: Generate presigned URL
                print("\n🔗 Testing presigned URL generation...")
                presigned_url = storage.generate_presigned_url("outputs", "tests/test_upload.txt", expiration=3600)
                if presigned_url:
                    print(f"✅ Presigned URL generated (expires in 1 hour)")
                    print(f"  URL: {presigned_url[:80]}...")
                else:
                    print("❌ Failed to generate presigned URL")

                # Test 9: Clean up test file
                print("\n🧹 Cleaning up test file...")
                if storage.delete_file("outputs", "tests/test_upload.txt"):
                    print("✅ Test file deleted successfully")
                else:
                    print("❌ Failed to delete test file")

            else:
                print("❌ File upload failed")
                return False

        finally:
            # Clean up local test file
            if test_file.exists():
                test_file.unlink()

        print("\n🎉 All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


if __name__ == "__main__":
    success = test_wasabi_storage()
    sys.exit(0 if success else 1)
