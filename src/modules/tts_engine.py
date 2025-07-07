"""
Text-to-Speech Engine with Voice Cloning
Supports multiple TTS models and voice cloning capabilities
"""

import torch
import torchaudio
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from pathlib import Path
import numpy as np
from typing import Optional, Union
from loguru import logger
import librosa
import soundfile as sf

class TTSEngine:
    """
    Advanced TTS engine with voice cloning support
    Optimized for GPU acceleration
    """
    
    def __init__(self, config):
        self.config = config
        self.device = config.get_device()
        
        # Initialize models
        self.processor = None
        self.model = None
        self.vocoder = None
        self.voice_embeddings = {}
        
        self._load_models()
    
    def _load_models(self):
        """Load TTS models onto GPU"""
        logger.info("Loading TTS models...")
        
        try:
            # Load SpeechT5 for high-quality TTS
            self.processor = SpeechT5Processor.from_pretrained(self.config.tts.model_name)
            self.model = SpeechT5ForTextToSpeech.from_pretrained(self.config.tts.model_name)
            self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
            
            # Move to GPU if available
            if self.device.type == "cuda":
                self.model = self.model.to(self.device)
                self.vocoder = self.vocoder.to(self.device)
                
            logger.success("TTS models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load TTS models: {e}")
            raise
    
    def generate_speech(
        self,
        text: str,
        voice_sample: Optional[str] = None,
        output_path: str = "output/generated_speech.wav",
        speed: float = None
    ) -> str:
        """
        Generate speech from text with optional voice cloning
        
        Args:
            text: Text to convert to speech
            voice_sample: Path to voice sample for cloning
            output_path: Where to save the generated audio
            speed: Speech speed multiplier
            
        Returns:
            Path to generated audio file
        """
        logger.info(f"Generating speech for text: '{text[:50]}...'")
        
        try:
            # Process text input
            inputs = self.processor(text=text, return_tensors="pt")
            
            # Get voice embeddings
            if voice_sample:
                speaker_embeddings = self._extract_voice_embeddings(voice_sample)
            else:
                # Use default speaker embeddings
                speaker_embeddings = self._get_default_embeddings()
            
            # Move inputs to device
            if self.device.type == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                speaker_embeddings = speaker_embeddings.to(self.device)
            
            # Generate speech
            with torch.no_grad():
                speech = self.model.generate_speech(
                    inputs["input_ids"], 
                    speaker_embeddings, 
                    vocoder=self.vocoder
                )
            
            # Apply speed adjustment if specified
            if speed and speed != 1.0:
                speech = self._adjust_speed(speech, speed)
            
            # Save audio
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            sf.write(
                str(output_path),
                speech.cpu().numpy(),
                self.config.tts.sample_rate
            )
            
            logger.success(f"Speech generated and saved to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            raise
    
    def _extract_voice_embeddings(self, voice_sample_path: str) -> torch.Tensor:
        """
        Extract voice embeddings from a sample audio file
        This is a simplified version - in practice, you'd use more sophisticated
        speaker verification models like resemblyzer or similar
        """
        if voice_sample_path in self.voice_embeddings:
            return self.voice_embeddings[voice_sample_path]
        
        try:
            # Load and preprocess audio
            audio, sr = librosa.load(voice_sample_path, sr=self.config.tts.sample_rate)
            
            # Extract features (simplified - use proper speaker encoding in production)
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            embeddings = torch.tensor(np.mean(mfcc, axis=1), dtype=torch.float32)
            
            # Reshape to match expected dimensions (this is model-specific)
            embeddings = embeddings.unsqueeze(0).repeat(1, 512 // len(embeddings))[:, :512]
            
            # Cache embeddings
            self.voice_embeddings[voice_sample_path] = embeddings
            
            logger.info(f"Voice embeddings extracted from {voice_sample_path}")
            return embeddings
            
        except Exception as e:
            logger.warning(f"Failed to extract voice embeddings: {e}. Using default.")
            return self._get_default_embeddings()
    
    def _get_default_embeddings(self) -> torch.Tensor:
        """Get default speaker embeddings"""
        # This would typically be pre-computed embeddings for a default voice
        return torch.randn(1, 512)  # Placeholder dimensions
    
    def _adjust_speed(self, audio: torch.Tensor, speed: float) -> torch.Tensor:
        """Adjust speech speed using time-stretching"""
        try:
            audio_np = audio.cpu().numpy()
            stretched = librosa.effects.time_stretch(audio_np, rate=speed)
            return torch.from_numpy(stretched)
        except Exception as e:
            logger.warning(f"Speed adjustment failed: {e}")
            return audio
    
    def clone_voice_from_samples(
        self,
        voice_samples: list,
        output_embedding_path: str
    ) -> str:
        """
        Create a voice embedding from multiple samples for better cloning
        
        Args:
            voice_samples: List of paths to voice sample files
            output_embedding_path: Where to save the combined embedding
            
        Returns:
            Path to saved embedding file
        """
        logger.info(f"Creating voice embedding from {len(voice_samples)} samples")
        
        embeddings_list = []
        for sample_path in voice_samples:
            embedding = self._extract_voice_embeddings(sample_path)
            embeddings_list.append(embedding)
        
        # Average the embeddings
        combined_embedding = torch.stack(embeddings_list).mean(dim=0)
        
        # Save embedding
        output_path = Path(output_embedding_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(combined_embedding, output_path)
        
        logger.success(f"Voice embedding saved to {output_path}")
        return str(output_path)
    
    def load_voice_embedding(self, embedding_path: str) -> torch.Tensor:
        """Load a pre-computed voice embedding"""
        return torch.load(embedding_path, map_location=self.device)
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages for TTS"""
        return ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"]
    
    def estimate_audio_duration(self, text: str) -> float:
        """Estimate the duration of generated audio based on text length"""
        # Rough estimation: ~150 words per minute average speech
        words = len(text.split())
        duration = (words / 150) * 60  # Convert to seconds
        return duration
