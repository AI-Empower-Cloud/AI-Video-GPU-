"""
AI Video GPU - Interface Modules
Provides web interfaces for compatibility with existing repos
"""

from .gradio_interface import GradioVideoGenerator, create_gradio_app

__all__ = ["GradioVideoGenerator", "create_gradio_app"]
