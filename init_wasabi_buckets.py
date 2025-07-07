#!/usr/bin/env python3
"""
Initialize Wasabi buckets for AI Video GPU system
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
load_dotenv()

from cloud.wasabi_storage import WasabiStorage


def main():
    """Initialize all Wasabi buckets"""
    print("🚀 Initializing Wasabi buckets for AI Video GPU system...")

    try:
        # Initialize Wasabi storage
        storage = WasabiStorage()
        print(f"✅ Connected to Wasabi in region: {storage.region}")

        # Test connection first
        if not storage.test_connection():
            print("❌ Failed to connect to Wasabi")
            return False

        print("✅ Wasabi connection successful!")

        # Create all buckets
        created_buckets = []
        failed_buckets = []

        for bucket_type, bucket_name in storage.buckets.items():
            print(f"\n📦 Creating bucket: {bucket_name} ({bucket_type})")

            if storage.create_bucket(bucket_name):
                created_buckets.append(bucket_name)
                print(f"✅ Successfully created bucket: {bucket_name}")
            else:
                failed_buckets.append(bucket_name)
                print(f"❌ Failed to create bucket: {bucket_name}")

        # Summary
        print(f"\n📊 Summary:")
        print(f"✅ Created buckets: {len(created_buckets)}")
        print(f"❌ Failed buckets: {len(failed_buckets)}")

        if created_buckets:
            print(f"\n🎉 Successfully created buckets:")
            for bucket in created_buckets:
                print(f"  - {bucket}")

        if failed_buckets:
            print(f"\n⚠️  Failed to create buckets:")
            for bucket in failed_buckets:
                print(f"  - {bucket}")

        # List all buckets to verify
        print(f"\n📋 Listing all buckets in your Wasabi account:")
        try:
            response = storage.client.list_buckets()
            buckets = response.get("Buckets", [])

            if buckets:
                for bucket in buckets:
                    print(f"  - {bucket['Name']} (created: {bucket['CreationDate']})")
            else:
                print("  No buckets found")

        except Exception as e:
            print(f"❌ Failed to list buckets: {e}")

        return len(failed_buckets) == 0

    except Exception as e:
        print(f"❌ Error initializing Wasabi: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
