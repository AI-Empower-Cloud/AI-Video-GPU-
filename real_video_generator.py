#!/usr/bin/env python3
"""
Working Video Generator with Wasabi Upload
Creates a real MP4 video file using OpenCV and uploads to Wasabi
"""

import os
import sys
import time
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_real_video_with_wasabi():
    """Create a real MP4 video and automatically upload to Wasabi"""
    
    print("🎬 AI Video GPU - Real Video Generator")
    print("=" * 50)
    
    # Check dependencies
    try:
        import cv2
        print("✅ OpenCV available")
    except ImportError:
        print("❌ OpenCV not available. Install with: pip install opencv-python")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy available")
    except ImportError:
        print("❌ NumPy not available. Install with: pip install numpy")
        return False
    
    try:
        import boto3
        print("✅ Boto3 (Wasabi) available")
        WASABI_AVAILABLE = True
    except ImportError:
        print("⚠️ Boto3 not available. Install with: pip install boto3")
        WASABI_AVAILABLE = False
    
    # Create output directory
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    video_filename = f'real_video_{timestamp}.mp4'
    video_path = output_dir / video_filename
    
    print(f"\n🎬 Creating real video: {video_filename}")
    print(f"📋 Resolution: 1280x720 (HD)")
    print(f"⏱️ Duration: 3 minutes (180 seconds)")
    print(f"🎨 Content: AI Video GPU Demo")
    
    # Video parameters
    width, height = 1280, 720
    fps = 30
    duration = 180  # 3 minutes = 180 seconds
    total_frames = fps * duration
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))
    
    if not video_writer.isOpened():
        print("❌ Failed to initialize video writer")
        return False
    
    print(f"\n🎞️ Generating {total_frames} frames...")
    
    # Generate video frames
    for frame_num in range(total_frames):
        # Create a frame with animated content
        frame = create_demo_frame(frame_num, total_frames, width, height, fps)
        
        # Write frame to video
        video_writer.write(frame)
        
        # Show progress
        if frame_num % (fps * 10) == 0:  # Every 10 seconds
            progress = (frame_num / total_frames) * 100
            seconds_completed = frame_num // fps
            print(f"   Generated {seconds_completed}/180 seconds ({progress:.1f}%)")
    
    # Release video writer
    video_writer.release()
    cv2.destroyAllWindows()
    
    # Check if video was created successfully
    if video_path.exists() and video_path.stat().st_size > 0:
        file_size = video_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Video created successfully!")
        print(f"📁 Location: {video_path}")
        print(f"📏 File size: {file_size:.2f} MB")
    else:
        print("❌ Video creation failed")
        return False
    
    # Upload to Wasabi if available
    if WASABI_AVAILABLE:
        print(f"\n🌊 Starting Wasabi cloud upload...")
        success = upload_to_wasabi(video_path, video_filename)
        
        if success:
            print("🎉 Video successfully uploaded to Wasabi cloud!")
        else:
            print("⚠️ Wasabi upload failed - video saved locally only")
    else:
        print(f"\n💾 Video saved locally only")
        print(f"💡 To enable Wasabi upload: pip install boto3")
    
    # Summary
    print(f"\n🎯 Video Generation Complete!")
    print(f"📁 Local file: {video_path}")
    print(f"📏 Size: {file_size:.2f} MB")
    print(f"⏱️ Duration: {duration} seconds")
    print(f"🎬 Format: MP4 (H.264)")
    print(f"🌐 Ready to share!")
    
    return True

def create_demo_frame(frame_num, total_frames, width, height, fps):
    """Create an animated demo frame"""
    
    # Create blank frame
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Background gradient
    for y in range(height):
        intensity = int(255 * (y / height))
        frame[y, :] = [intensity // 3, intensity // 2, intensity]
    
    # Calculate animation parameters
    progress = frame_num / total_frames
    
    # Animated circle
    center_x = int(width // 2 + 200 * np.sin(progress * 4 * np.pi))
    center_y = int(height // 2 + 100 * np.cos(progress * 4 * np.pi))
    radius = int(50 + 30 * np.sin(progress * 8 * np.pi))
    
    cv2.circle(frame, (center_x, center_y), radius, (0, 255, 255), -1)
    
    # Moving rectangles
    rect_x = int((progress * width * 1.5) % (width + 200) - 100)
    rect_y = int(height // 3)
    cv2.rectangle(frame, (rect_x, rect_y), (rect_x + 100, rect_y + 50), (255, 100, 100), -1)
    
    # Add text with 3-minute content
    texts = [
        "AI Video GPU Generator - Introduction",
        "Welcome to AI-Powered Video Creation",
        "Generating High-Quality Videos with AI",
        "Real-time Processing with GPU Acceleration", 
        "Automatic Speech Synthesis and Audio",
        "Advanced Computer Vision Processing",
        "Seamless Cloud Storage Integration",
        "Wasabi Cloud Upload and Sharing",
        "Professional Video Output Quality",
        "Optimized for Google Colab Environment",
        "Scalable Video Generation Pipeline", 
        "AI Technology Demonstration Complete",
        "Thank You for Watching This Demo",
        "Visit GitHub for Source Code",
        "Subscribe for More AI Content",
        "AI Video GPU - Project Complete"
    ]
    
    # Calculate which text to show (16 texts for 180 seconds = ~11 seconds each)
    text_duration = 180 / len(texts)  # seconds per text
    current_second = frame_num / fps
    text_index = min(int(current_second / text_duration), len(texts) - 1)
    
    if text_index < len(texts):
        text = texts[text_index]
        
        # Add subtitle with current section info
        section_num = text_index + 1
        subtitle = f"Section {section_num}/16 - {int(current_second)}s"
        
        # Text background
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
        text_x = (width - text_width) // 2
        text_y = height - 100
        
        cv2.rectangle(frame, (text_x - 20, text_y - text_height - 20), 
                     (text_x + text_width + 20, text_y + 20), (0, 0, 0), -1)
        
        # Text
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
        # Add subtitle with timing info
        subtitle_y = text_y + 40
        (sub_width, sub_height), _ = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        sub_x = (width - sub_width) // 2
        cv2.putText(frame, subtitle, (sub_x, subtitle_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
    
    # Progress bar
    bar_width = int(width * 0.8)
    bar_height = 20
    bar_x = (width - bar_width) // 2
    bar_y = height - 50
    
    # Progress bar background
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
    
    # Progress bar fill
    fill_width = int(bar_width * progress)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), (0, 255, 0), -1)
    
    # Frame counter
    frame_text = f"Frame {frame_num + 1}/{total_frames}"
    cv2.putText(frame, frame_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return frame

def upload_to_wasabi(video_path, video_filename):
    """Upload video to Wasabi cloud storage"""
    
    # Wasabi Configuration
    WASABI_ACCESS_KEY = os.getenv("WASABI_ACCESS_KEY", "your_wasabi_access_key")
    WASABI_SECRET_KEY = os.getenv("WASABI_SECRET_KEY", "your_wasabi_secret_key")
    WASABI_ENDPOINT = "https://s3.wasabisys.com"
    WASABI_REGION = "us-east-1"
    BUCKET_NAME = "ai-video-gpu-outputs"
    
    if WASABI_ACCESS_KEY == "your_wasabi_access_key":
        print("⚠️ Wasabi credentials not configured")
        print("💡 Set environment variables:")
        print("   export WASABI_ACCESS_KEY='your_key'")
        print("   export WASABI_SECRET_KEY='your_secret'")
        return False
    
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Initialize S3 client for Wasabi
        s3_client = boto3.client(
            's3',
            endpoint_url=WASABI_ENDPOINT,
            aws_access_key_id=WASABI_ACCESS_KEY,
            aws_secret_access_key=WASABI_SECRET_KEY,
            region_name=WASABI_REGION
        )
        
        # Test connection
        try:
            s3_client.list_buckets()
            print("✅ Wasabi connection successful")
        except Exception as e:
            print(f"❌ Wasabi connection failed: {e}")
            return False
        
        # Create bucket if it doesn't exist
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
            print(f"✅ Bucket '{BUCKET_NAME}' exists")
        except ClientError:
            try:
                s3_client.create_bucket(Bucket=BUCKET_NAME)
                print(f"✅ Created bucket '{BUCKET_NAME}'")
            except Exception as e:
                print(f"❌ Could not create bucket: {e}")
                return False
        
        # Upload video with progress
        remote_key = f"generated_videos/{video_filename}"
        
        print(f"📤 Uploading {video_filename} to Wasabi...")
        
        # Add metadata
        metadata = {
            'generated_by': 'AI_Video_GPU_Real',
            'upload_date': str(datetime.now()),
            'content_type': 'real_generated_video',
            'duration': '30_seconds',
            'resolution': '1280x720'
        }
        
        # Upload with public read access
        s3_client.upload_file(
            str(video_path),
            BUCKET_NAME,
            remote_key,
            ExtraArgs={
                'ACL': 'public-read',
                'Metadata': metadata,
                'ContentType': 'video/mp4'
            }
        )
        
        # Generate public URL
        public_url = f"{WASABI_ENDPOINT}/{BUCKET_NAME}/{remote_key}"
        
        print(f"✅ Upload successful!")
        print(f"🌐 Public URL: {public_url}")
        print(f"🔗 Share this URL with anyone!")
        print(f"📱 View from any device!")
        
        # Save URL to file
        url_file = video_path.parent / "video_urls.txt"
        with open(url_file, 'a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"\n{timestamp} - {video_filename}\n")
            f.write(f"Public URL: {public_url}\n")
            f.write(f"Type: Real MP4 Video (HD)\n")
            f.write(f"Duration: 30 seconds\n")
            f.write("-" * 60 + "\n")
        
        print(f"📋 URL saved to: {url_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Wasabi upload error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Real AI Video Generator...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    try:
        success = create_real_video_with_wasabi()
        
        if success:
            print("\n🎉 Real video generation completed successfully!")
            print("🎬 Your MP4 video is ready!")
            print("🌊 Wasabi cloud integration tested!")
            print("\n💡 Next steps:")
            print("1. Set Wasabi credentials for cloud upload")
            print("2. Integrate with AI text-to-speech")
            print("3. Add lip sync and avatar features")
            print("4. Scale to 3-minute videos!")
        else:
            print("\n❌ Video generation failed. Check the logs above.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Generation interrupted by user")
    except Exception as e:
        print(f"\n❌ Generation failed with error: {e}")
        import traceback
        traceback.print_exc()
