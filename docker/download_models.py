#!/usr/bin/env python3
"""
Model download script for prebuilt container
Downloads and caches commonly used AI models
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download and cache AI models"""
    
    # Create cache directory
    cache_dir = Path("/app/models/huggingface")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from transformers import AutoTokenizer, AutoModel
        from diffusers import StableDiffusionPipeline
        import torch
        
        # Download text models
        models = [
            'microsoft/DialoGPT-medium',
            'microsoft/speecht5_tts', 
            'microsoft/speecht5_vc',
            'facebook/wav2vec2-base-960h',
            'openai/whisper-base',
            'sentence-transformers/all-MiniLM-L6-v2'
        ]
        
        for model_name in models:
            try:
                print(f'Downloading {model_name}...')
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name, 
                    cache_dir=str(cache_dir)
                )
                model = AutoModel.from_pretrained(
                    model_name, 
                    cache_dir=str(cache_dir)
                )
                print(f'Downloaded {model_name}')
            except Exception as e:
                print(f'Failed to download {model_name}: {e}')
                
        # Download Stable Diffusion pipeline
        try:
            print('Downloading Stable Diffusion...')
            pipe = StableDiffusionPipeline.from_pretrained(
                'runwayml/stable-diffusion-v1-5',
                torch_dtype=torch.float16,
                cache_dir=str(cache_dir)
            )
            print('Downloaded Stable Diffusion')
        except Exception as e:
            print(f'Failed to download Stable Diffusion: {e}')
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some dependencies may not be available yet")
        
    print("Model download complete")

if __name__ == "__main__":
    download_models()
