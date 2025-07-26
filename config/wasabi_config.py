"""
Wasabi S3 Configuration
Contains your Wasabi credentials and settings for automatic video upload
"""

# Wasabi S3 Credentials
WASABI_ACCESS_KEY = "5W346VTEQ11HLJLF177I"
WASABI_SECRET_KEY = "RezjHz3kqkdYU6VEODpgcQud4lR5D9gRPCFkVeMA"

# Wasabi S3 Settings
WASABI_ENDPOINT = "https://s3.wasabisys.com"
WASABI_REGION = "us-east-1"  # Default Wasabi region
WASABI_BUCKET = "ai-video-gpu-outputs"
WASABI_FOLDER = "generated_videos"

# Upload Settings
AUTO_UPLOAD = True
MAKE_PUBLIC = True  # Generate public URLs for easy sharing
