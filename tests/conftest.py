"""
Test Configuration for AI Video GPU
"""

import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'gpu': {
            'enabled': False,  # Use CPU for tests
            'device': 'cpu'
        },
        'video': {
            'output_resolution': [640, 480],
            'fps': 24
        },
        'tts': {
            'sample_rate': 16000
        }
    }
