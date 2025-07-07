"""
Enhanced TTS Engine with Tortoise and XTTS support
Supports multiple TTS backends for maximum compatibility
"""

import torch
import torchaudio
from pathlib import Path
import numpy as np
from typing import Optional, Union, List
from loguru import logger
import librosa
import soundfile as sf
import tempfile
import os

class EnhancedTTSEngine:
    """
    Enhanced TTS engine supporting multiple backends:
    - Coqui XTTS (voice cloning)
    - Tortoise TTS (high quality)
    - SpeechT5 (fallback)
    """
    
    def __init__(self, config):
        self.config = config
        self.device = config.get_device()
        
        # Available TTS backends
        self.backends = {
            'xtts': None,
            'tortoise': None,
            'speecht5': None
        }
        
        self.current_backend = None
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Initialize available TTS backends"""
        logger.info("Initializing TTS backends...")
        
        # Try to load XTTS (Coqui)
        try:
            from TTS.api import TTS
            self.backends['xtts'] = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            logger.success("XTTS (Coqui) backend loaded")
            self.current_backend = 'xtts'
        except Exception as e:
            logger.warning(f"XTTS backend failed to load: {e}")
        
        # Try to load Tortoise
        try:
            from tortoise.api import TextToSpeech
            from tortoise.utils.audio import load_voice
            self.backends['tortoise'] = TextToSpeech()
            logger.success("Tortoise TTS backend loaded")
            if not self.current_backend:
                self.current_backend = 'tortoise'
        except Exception as e:
            logger.warning(f"Tortoise backend failed to load: {e}")
        
        # Fallback to SpeechT5
        try:
            from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
            self.backends['speecht5'] = {
                'processor': SpeechT5Processor.from_pretrained("microsoft/speecht5_tts"),
                'model': SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts"),
                'vocoder': SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
            }
            if self.device.type == "cuda":
                self.backends['speecht5']['model'] = self.backends['speecht5']['model'].to(self.device)
                self.backends['speecht5']['vocoder'] = self.backends['speecht5']['vocoder'].to(self.device)
            
            logger.success("SpeechT5 backend loaded as fallback")
            if not self.current_backend:
                self.current_backend = 'speecht5'
        except Exception as e:
            logger.error(f"SpeechT5 fallback failed to load: {e}")
        
        if not self.current_backend:
            raise RuntimeError("No TTS backend could be loaded!")
        
        logger.info(f"Using TTS backend: {self.current_backend}")
    
    def generate_speech(
        self,
        text: str,
        voice_sample: Optional[str] = None,
        output_path: str = "output/generated_speech.wav",
        voice_name: Optional[str] = None,
        language: str = "en",
        speed: float = 1.0
    ) -> str:
        """
        Generate speech using the best available backend
        
        Args:
            text: Text to convert to speech
            voice_sample: Path to voice sample for cloning
            output_path: Where to save the generated audio
            voice_name: Predefined voice name (for Tortoise)
            language: Language code
            speed: Speech speed multiplier
            
        Returns:
            Path to generated audio file
        """
        logger.info(f"Generating speech with {self.current_backend} backend")
        
        try:
            if self.current_backend == 'xtts':
                return self._generate_xtts(text, voice_sample, output_path, language, speed)
            elif self.current_backend == 'tortoise':
                return self._generate_tortoise(text, voice_sample, output_path, voice_name, speed)
            else:
                return self._generate_speecht5(text, voice_sample, output_path, speed)
                
        except Exception as e:
            logger.error(f"Speech generation failed with {self.current_backend}: {e}")
            # Try fallback backends
            return self._fallback_generation(text, voice_sample, output_path, speed)
    
    def _generate_xtts(
        self, 
        text: str, 
        voice_sample: Optional[str], 
        output_path: str, 
        language: str,
        speed: float
    ) -> str:
        """Generate speech using XTTS"""
        logger.info("Generating speech with XTTS...")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        xtts = self.backends['xtts']
        
        if voice_sample and Path(voice_sample).exists():
            # Voice cloning mode
            logger.info(f"Cloning voice from: {voice_sample}")
            xtts.tts_to_file(
                text=text,
                speaker_wav=voice_sample,
                language=language,
                file_path=str(output_path)
            )
        else:
            # Use default speaker
            logger.info("Using default XTTS speaker")
            xtts.tts_to_file(
                text=text,
                language=language,
                file_path=str(output_path)
            )
        
        # Apply speed adjustment if needed
        if speed != 1.0:
            self._adjust_audio_speed(str(output_path), speed)
        
        logger.success(f"XTTS speech generated: {output_path}")
        return str(output_path)
    
    def _generate_tortoise(
        self, 
        text: str, 
        voice_sample: Optional[str], 
        output_path: str, 
        voice_name: Optional[str],
        speed: float
    ) -> str:
        """Generate speech using Tortoise TTS"""
        logger.info("Generating speech with Tortoise...")
        
        from tortoise.utils.audio import load_voice, load_audio
        
        tortoise = self.backends['tortoise']
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare voice
        if voice_sample and Path(voice_sample).exists():
            # Custom voice from sample
            logger.info(f"Using custom voice from: {voice_sample}")
            voice_samples, conditioning_latents = load_voice(voice_sample)
        elif voice_name:
            # Predefined voice
            logger.info(f"Using predefined voice: {voice_name}")
            voice_samples, conditioning_latents = load_voice(voice_name)
        else:
            # Default voice
            logger.info("Using default Tortoise voice")
            voice_samples, conditioning_latents = load_voice("random")
        
        # Generate speech
        gen = tortoise.tts_with_preset(
            text,
            voice_samples=voice_samples,
            conditioning_latents=conditioning_latents,
            preset="fast"  # fast, standard, high_quality
        )
        
        # Save audio
        torchaudio.save(str(output_path), gen.squeeze(0).cpu(), 24000)
        
        # Apply speed adjustment if needed
        if speed != 1.0:
            self._adjust_audio_speed(str(output_path), speed)
        
        logger.success(f"Tortoise speech generated: {output_path}")
        return str(output_path)
    
    def _generate_speecht5(
        self, 
        text: str, 
        voice_sample: Optional[str], 
        output_path: str,
        speed: float
    ) -> str:
        """Generate speech using SpeechT5 (fallback)"""
        logger.info("Generating speech with SpeechT5...")
        
        backend = self.backends['speecht5']
        processor = backend['processor']
        model = backend['model']
        vocoder = backend['vocoder']
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Process text
        inputs = processor(text=text, return_tensors="pt")
        
        # Get speaker embeddings
        if voice_sample:
            speaker_embeddings = self._extract_voice_embeddings_speecht5(voice_sample)
        else:
            speaker_embeddings = torch.randn(1, 512)  # Default embeddings
        
        # Move to device
        if self.device.type == "cuda":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            speaker_embeddings = speaker_embeddings.to(self.device)
        
        # Generate speech
        with torch.no_grad():
            speech = model.generate_speech(
                inputs["input_ids"], 
                speaker_embeddings, 
                vocoder=vocoder
            )
        
        # Save audio
        sf.write(
            str(output_path),
            speech.cpu().numpy(),
            self.config.tts.sample_rate
        )
        
        # Apply speed adjustment if needed
        if speed != 1.0:
            self._adjust_audio_speed(str(output_path), speed)
        
        logger.success(f"SpeechT5 speech generated: {output_path}")
        return str(output_path)
    
    def _extract_voice_embeddings_speecht5(self, voice_sample_path: str) -> torch.Tensor:
        """Extract voice embeddings for SpeechT5"""
        try:
            audio, sr = librosa.load(voice_sample_path, sr=self.config.tts.sample_rate)
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            embeddings = torch.tensor(np.mean(mfcc, axis=1), dtype=torch.float32)
            embeddings = embeddings.unsqueeze(0).repeat(1, 512 // len(embeddings))[:, :512]
            return embeddings
        except Exception as e:
            logger.warning(f"Failed to extract voice embeddings: {e}")
            return torch.randn(1, 512)
    
    def _adjust_audio_speed(self, audio_path: str, speed: float):
        """Adjust audio speed using librosa"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            y_stretched = librosa.effects.time_stretch(y, rate=speed)
            sf.write(audio_path, y_stretched, sr)
            logger.info(f"Audio speed adjusted by factor {speed}")
        except Exception as e:
            logger.warning(f"Speed adjustment failed: {e}")
    
    def _fallback_generation(
        self, 
        text: str, 
        voice_sample: Optional[str], 
        output_path: str,
        speed: float
    ) -> str:
        """Try fallback backends if primary fails"""
        logger.warning("Attempting fallback TTS generation...")
        
        # Try other backends in order of preference
        fallback_order = ['xtts', 'tortoise', 'speecht5']
        fallback_order.remove(self.current_backend)
        
        for backend_name in fallback_order:
            if self.backends[backend_name] is not None:
                try:
                    logger.info(f"Trying fallback backend: {backend_name}")
                    old_backend = self.current_backend
                    self.current_backend = backend_name
                    
                    result = self.generate_speech(text, voice_sample, output_path, speed=speed)
                    
                    logger.warning(f"Fallback successful with {backend_name}")
                    return result
                    
                except Exception as e:
                    logger.error(f"Fallback {backend_name} also failed: {e}")
                    self.current_backend = old_backend
                    continue
        
        raise RuntimeError("All TTS backends failed!")
    
    def list_available_voices(self) -> List[str]:
        """List available predefined voices"""
        voices = []
        
        if self.current_backend == 'tortoise':
            # Tortoise has predefined voices
            try:
                from tortoise.utils.audio import get_voices
                voices = get_voices()
            except:
                voices = ['random', 'angie', 'deniro', 'freeman', 'halle', 'lj', 'myself', 'pat', 'snakes', 'tom', 'train_daws', 'train_dreams', 'train_grace', 'train_lescault', 'weaver', 'william']
        
        elif self.current_backend == 'xtts':
            voices = ['default']  # XTTS primarily uses voice cloning
        
        else:
            voices = ['default']
        
        return voices
    
    def clone_voice_from_samples(
        self,
        voice_samples: List[str],
        output_embedding_path: str,
        voice_name: str = "custom_voice"
    ) -> str:
        """
        Create optimized voice embeddings from multiple samples
        """
        logger.info(f"Creating voice clone from {len(voice_samples)} samples")
        
        if self.current_backend == 'xtts':
            # XTTS handles multiple samples automatically
            # Just use the first sample as reference
            return voice_samples[0] if voice_samples else ""
        
        elif self.current_backend == 'tortoise':
            # For Tortoise, we need to create a voice directory
            voice_dir = Path(output_embedding_path).parent / voice_name
            voice_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy and rename samples
            for i, sample_path in enumerate(voice_samples):
                dest_path = voice_dir / f"{i:02d}.wav"
                # Convert to proper format if needed
                audio, sr = librosa.load(sample_path, sr=22050)
                sf.write(str(dest_path), audio, sr)
            
            logger.success(f"Voice clone created for Tortoise: {voice_dir}")
            return str(voice_dir)
        
        else:
            # For SpeechT5, average the embeddings
            embeddings_list = []
            for sample_path in voice_samples:
                embedding = self._extract_voice_embeddings_speecht5(sample_path)
                embeddings_list.append(embedding)
            
            combined_embedding = torch.stack(embeddings_list).mean(dim=0)
            torch.save(combined_embedding, output_embedding_path)
            
            logger.success(f"Voice embedding saved: {output_embedding_path}")
            return output_embedding_path
    
    def get_backend_info(self) -> dict:
        """Get information about loaded backends"""
        return {
            'current_backend': self.current_backend,
            'available_backends': [name for name, backend in self.backends.items() if backend is not None],
            'supports_voice_cloning': self.current_backend in ['xtts', 'tortoise'],
            'supports_multilingual': self.current_backend == 'xtts'
        }
