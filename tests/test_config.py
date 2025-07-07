"""
Test Configuration Manager
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from src.config import ConfigManager

def test_config_creation():
    """Test configuration manager creation"""
    config = ConfigManager()
    assert config.gpu is not None
    assert config.tts is not None
    assert config.video is not None

def test_config_save_load(temp_dir):
    """Test saving and loading configuration"""
    config_path = temp_dir / "test_config.yaml"
    
    # Create and save config
    config = ConfigManager(str(config_path))
    config.gpu.enabled = False
    config.video.fps = 25
    config.save_config()
    
    # Load config
    config2 = ConfigManager(str(config_path))
    assert config2.gpu.enabled == False
    assert config2.video.fps == 25

def test_device_selection():
    """Test device selection logic"""
    config = ConfigManager()
    device = config.get_device()
    assert device.type in ['cpu', 'cuda']
