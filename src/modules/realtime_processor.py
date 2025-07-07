"""
AI Video GPU - Real-time Processing Module
Live streaming, real-time generation, and WebRTC support
"""

import asyncio
import numpy as np
import cv2
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from pathlib import Path
from loguru import logger
import json
import time
from collections import deque
import threading
import queue

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    logger.warning("WebSockets not available. Real-time streaming limited.")

try:
    import aiortc
    from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
    from aiortc.contrib.media import MediaPlayer, MediaRecorder
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    logger.warning("WebRTC not available. Real-time video calls not supported.")

class RealTimeVideoProcessor:
    """
    Real-time video processing for live streams, webcam input, and video calls
    """
    
    def __init__(self, config):
        self.config = config
        self.is_processing = False
        self.frame_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue(maxsize=10)
        self.processing_thread = None
        
        # Performance metrics
        self.fps_counter = deque(maxlen=30)
        self.latency_counter = deque(maxlen=30)
        
        # Initialize processing pipeline
        self._initialize_real_time_pipeline()
        
    def _initialize_real_time_pipeline(self):
        """Initialize optimized pipeline for real-time processing"""
        
        # Lightweight models for real-time processing
        self.fast_tts_engine = None
        self.fast_lip_sync = None
        self.frame_enhancer = None
        
        logger.info("Real-time processing pipeline initialized")
        
    def start_webcam_processing(
        self,
        camera_index: int = 0,
        target_fps: int = 30,
        processing_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Start real-time webcam processing"""
        
        if self.is_processing:
            return {'success': False, 'error': 'Processing already active'}
            
        try:
            # Initialize webcam capture
            cap = cv2.VideoCapture(camera_index)
            cap.set(cv2.CAP_PROP_FPS, target_fps)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            if not cap.isOpened():
                return {'success': False, 'error': f'Cannot open camera {camera_index}'}
                
            self.is_processing = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._process_webcam_frames,
                args=(cap, target_fps, processing_callback),
                daemon=True
            )
            self.processing_thread.start()
            
            logger.info(f"Webcam processing started (camera {camera_index}, {target_fps} FPS)")
            return {'success': True, 'camera_index': camera_index, 'target_fps': target_fps}
            
        except Exception as e:
            logger.error(f"Failed to start webcam processing: {e}")
            return {'success': False, 'error': str(e)}
            
    def _process_webcam_frames(
        self,
        cap: cv2.VideoCapture,
        target_fps: int,
        callback: Optional[Callable]
    ):
        """Process webcam frames in real-time"""
        
        frame_time = 1.0 / target_fps
        
        while self.is_processing:
            start_time = time.time()
            
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to capture frame")
                continue
                
            # Process frame
            try:
                processed_frame = self._process_single_frame(frame)
                
                # Calculate metrics
                processing_time = time.time() - start_time
                self.latency_counter.append(processing_time)
                self.fps_counter.append(1.0 / max(processing_time, 0.001))
                
                # Callback for external processing
                if callback:
                    callback(processed_frame, {
                        'processing_time': processing_time,
                        'fps': self.get_current_fps(),
                        'latency': self.get_average_latency()
                    })
                    
                # Try to maintain target FPS
                elapsed = time.time() - start_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                    
            except Exception as e:
                logger.error(f"Frame processing error: {e}")
                
        cap.release()
        logger.info("Webcam processing stopped")
        
    def _process_single_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process a single frame with optimized pipeline"""
        
        # Apply real-time enhancements
        enhanced_frame = frame
        
        try:
            # Fast face detection and enhancement
            if self.frame_enhancer:
                enhanced_frame = self.frame_enhancer.enhance_frame_fast(frame)
            else:
                # Basic enhancement if no AI model available
                enhanced_frame = cv2.bilateralFilter(frame, 5, 50, 50)
                enhanced_frame = cv2.convertScaleAbs(enhanced_frame, alpha=1.1, beta=10)
                
        except Exception as e:
            logger.warning(f"Frame enhancement failed: {e}")
            enhanced_frame = frame
            
        return enhanced_frame
        
    def stop_processing(self):
        """Stop real-time processing"""
        self.is_processing = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        logger.info("Real-time processing stopped")
        
    def get_current_fps(self) -> float:
        """Get current processing FPS"""
        if self.fps_counter:
            return sum(self.fps_counter) / len(self.fps_counter)
        return 0.0
        
    def get_average_latency(self) -> float:
        """Get average processing latency in seconds"""
        if self.latency_counter:
            return sum(self.latency_counter) / len(self.latency_counter)
        return 0.0
        
    def get_performance_stats(self) -> Dict[str, float]:
        """Get comprehensive performance statistics"""
        return {
            'current_fps': self.get_current_fps(),
            'average_latency_ms': self.get_average_latency() * 1000,
            'is_processing': self.is_processing,
            'frame_queue_size': self.frame_queue.qsize(),
            'result_queue_size': self.result_queue.qsize()
        }

class WebSocketStreamer:
    """
    WebSocket-based real-time video streaming
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        if not WEBSOCKETS_AVAILABLE:
            logger.error("WebSockets not available. Cannot create streamer.")
            return
            
        self.host = host
        self.port = port
        self.connected_clients = set()
        self.server = None
        
    async def start_server(self):
        """Start WebSocket server for video streaming"""
        
        if not WEBSOCKETS_AVAILABLE:
            return
            
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        
        self.connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                # Handle incoming messages (commands, configuration, etc.)
                await self.process_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Client error: {e}")
        finally:
            self.connected_clients.remove(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")
            
    async def process_client_message(self, websocket, message: str):
        """Process messages from WebSocket clients"""
        
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'start_processing':
                # Start video processing for this client
                response = {'type': 'status', 'message': 'Processing started'}
                await websocket.send(json.dumps(response))
                
            elif command == 'stop_processing':
                # Stop video processing for this client
                response = {'type': 'status', 'message': 'Processing stopped'}
                await websocket.send(json.dumps(response))
                
            elif command == 'get_stats':
                # Send performance statistics
                stats = {'type': 'stats', 'data': {}}  # Add stats here
                await websocket.send(json.dumps(stats))
                
        except json.JSONDecodeError:
            error = {'type': 'error', 'message': 'Invalid JSON message'}
            await websocket.send(json.dumps(error))
        except Exception as e:
            error = {'type': 'error', 'message': str(e)}
            await websocket.send(json.dumps(error))
            
    async def broadcast_frame(self, frame_data: bytes):
        """Broadcast video frame to all connected clients"""
        
        if not self.connected_clients:
            return
            
        # Create frame message
        message = {
            'type': 'frame',
            'data': frame_data.hex(),  # Convert bytes to hex string
            'timestamp': time.time()
        }
        
        # Send to all connected clients
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                logger.warning(f"Failed to send frame to client: {e}")
                disconnected.add(client)
                
        # Remove disconnected clients
        for client in disconnected:
            self.connected_clients.discard(client)

class WebRTCVideoChat:
    """
    WebRTC-based real-time video chat with AI processing
    """
    
    def __init__(self):
        if not WEBRTC_AVAILABLE:
            logger.error("WebRTC not available. Video chat not supported.")
            return
            
        self.peer_connections = {}
        self.video_processor = None
        
    async def create_peer_connection(self, session_id: str) -> RTCPeerConnection:
        """Create new WebRTC peer connection"""
        
        if not WEBRTC_AVAILABLE:
            return None
            
        pc = RTCPeerConnection()
        self.peer_connections[session_id] = pc
        
        # Add event handlers
        @pc.on("iceconnectionstatechange")
        async def on_ice_connection_state_change():
            logger.info(f"ICE connection state: {pc.iceConnectionState}")
            
        @pc.on("track")
        def on_track(track):
            logger.info(f"Track received: {track.kind}")
            
            if track.kind == "video":
                # Add AI processing to video track
                processed_track = AIProcessedVideoTrack(track, self.video_processor)
                pc.addTrack(processed_track)
                
        return pc
        
    async def handle_offer(self, session_id: str, offer_sdp: str) -> str:
        """Handle WebRTC offer and return answer"""
        
        if not WEBRTC_AVAILABLE:
            return ""
            
        pc = await self.create_peer_connection(session_id)
        
        # Set remote description
        offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
        await pc.setRemoteDescription(offer)
        
        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return answer.sdp

class AIProcessedVideoTrack(VideoStreamTrack):
    """
    Custom video track that applies AI processing to video frames
    """
    
    def __init__(self, source_track, processor):
        super().__init__()
        self.source_track = source_track
        self.processor = processor
        
    async def recv(self):
        """Receive and process video frame"""
        
        # Get frame from source
        frame = await self.source_track.recv()
        
        # Convert to numpy array for processing
        img = frame.to_ndarray(format="bgr24")
        
        # Apply AI processing
        if self.processor:
            processed_img = self.processor._process_single_frame(img)
        else:
            processed_img = img
            
        # Convert back to video frame
        new_frame = frame.from_ndarray(processed_img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        
        return new_frame

class LiveStreamManager:
    """
    Manager for live streaming to platforms like YouTube, Twitch, etc.
    """
    
    def __init__(self):
        self.active_streams = {}
        self.stream_configs = {
            'youtube': {
                'rtmp_url': 'rtmp://a.rtmp.youtube.com/live2/',
                'video_bitrate': '2500k',
                'audio_bitrate': '128k'
            },
            'twitch': {
                'rtmp_url': 'rtmp://live.twitch.tv/app/',
                'video_bitrate': '3000k',
                'audio_bitrate': '128k'
            },
            'facebook': {
                'rtmp_url': 'rtmps://live-api-s.facebook.com:443/rtmp/',
                'video_bitrate': '2000k',
                'audio_bitrate': '128k'
            }
        }
        
    def start_stream(
        self,
        platform: str,
        stream_key: str,
        video_source: str = "webcam",
        enable_ai_processing: bool = True
    ) -> Dict[str, Any]:
        """Start live stream to platform"""
        
        if platform not in self.stream_configs:
            return {'success': False, 'error': f'Unsupported platform: {platform}'}
            
        try:
            config = self.stream_configs[platform]
            rtmp_url = f"{config['rtmp_url']}{stream_key}"
            
            # FFmpeg command for streaming
            ffmpeg_cmd = [
                'ffmpeg',
                '-f', 'v4l2' if video_source == "webcam" else 'image2pipe',
                '-i', '/dev/video0' if video_source == "webcam" else '-',
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-maxrate', config['video_bitrate'],
                '-bufsize', '3000k',
                '-vf', 'format=yuv420p',
                '-g', '50',
                '-c:a', 'aac',
                '-b:a', config['audio_bitrate'],
                '-ac', '2',
                '-ar', '44100',
                '-f', 'flv',
                rtmp_url
            ]
            
            # Start streaming process
            import subprocess
            process = subprocess.Popen(ffmpeg_cmd)
            
            self.active_streams[platform] = {
                'process': process,
                'stream_key': stream_key,
                'started_at': time.time()
            }
            
            logger.info(f"Live stream started to {platform}")
            return {'success': True, 'platform': platform, 'rtmp_url': rtmp_url}
            
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")
            return {'success': False, 'error': str(e)}
            
    def stop_stream(self, platform: str) -> Dict[str, Any]:
        """Stop live stream"""
        
        if platform not in self.active_streams:
            return {'success': False, 'error': f'No active stream for {platform}'}
            
        try:
            stream_info = self.active_streams[platform]
            process = stream_info['process']
            
            process.terminate()
            process.wait(timeout=10)
            
            del self.active_streams[platform]
            
            logger.info(f"Live stream stopped for {platform}")
            return {'success': True, 'platform': platform}
            
        except Exception as e:
            logger.error(f"Failed to stop stream: {e}")
            return {'success': False, 'error': str(e)}
            
    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all active streams"""
        
        status = {}
        for platform, stream_info in self.active_streams.items():
            process = stream_info['process']
            status[platform] = {
                'active': process.poll() is None,
                'started_at': stream_info['started_at'],
                'duration': time.time() - stream_info['started_at']
            }
            
        return status
