"""
AI Video GPU - Web API
FastAPI interface for web-based video generation
"""

from .app import create_app
from .routes import video_routes, audio_routes, model_routes

__all__ = ["create_app", "video_routes", "audio_routes", "model_routes"]
