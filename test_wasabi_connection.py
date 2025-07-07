#!/usr/bin/env python3
"""
Test Wasabi connection with provided credentials
"""
import os
import sys

sys.path.append("/workspaces/AI-Video-GPU-/src")

from cloud.wasabi_storage import WasabiStorage


def test_wasabi_connection():
    """Test Wasabi connection"""
    print("🔗 Testing Wasabi connection...")

    try:
        # Load from environment variables
        storage = WasabiStorage()

        # Test connection
        if storage.test_connection():
            print("✅ Wasabi connection successful!")

            # Get storage usage
            print("\n📊 Storage usage:")
            usage = storage.get_storage_usage()
            for bucket_type, info in usage.items():
                status = "✅" if info["exists"] else "❌"
                print(f"  {status} {bucket_type}: {info['file_count']} files, {info['total_size_mb']:.2f} MB")

            return True
        else:
            print("❌ Wasabi connection failed!")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_wasabi_connection()
