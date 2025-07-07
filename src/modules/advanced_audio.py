"""
Advanced Audio Processing Engine
Handles audio denoising, enhancement, multi-speaker separation, and emotion transfer
"""

import numpy as np
import librosa
import soundfile as sf
import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import json
from loguru import logger
from scipy import signal
from scipy.signal import butter, filtfilt
import noisereduce as nr

class AudioDenoiser:
    """Advanced audio denoising and enhancement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sample_rate = config.get('sample_rate', 22050)
        self.n_fft = config.get('n_fft', 2048)
        self.hop_length = config.get('hop_length', 512)
        
        # Initialize spectral subtraction parameters
        self.alpha = config.get('noise_alpha', 2.0)
        self.beta = config.get('noise_beta', 0.01)
        
    def spectral_subtraction(self, audio: np.ndarray, noise_profile: Optional[np.ndarray] = None) -> np.ndarray:
        """Apply spectral subtraction for noise reduction"""
        
        # Estimate noise profile if not provided
        if noise_profile is None:
            # Use first 0.5 seconds as noise estimate
            noise_samples = int(0.5 * self.sample_rate)
            noise_profile = audio[:noise_samples]
        
        # Compute STFT
        stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise spectrum
        noise_stft = librosa.stft(noise_profile, n_fft=self.n_fft, hop_length=self.hop_length)
        noise_magnitude = np.mean(np.abs(noise_stft), axis=1, keepdims=True)
        
        # Apply spectral subtraction
        enhanced_magnitude = magnitude - self.alpha * noise_magnitude
        enhanced_magnitude = np.maximum(enhanced_magnitude, self.beta * magnitude)
        
        # Reconstruct audio
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=self.hop_length)
        
        return enhanced_audio
    
    def adaptive_filter(self, audio: np.ndarray) -> np.ndarray:
        """Apply adaptive filtering for noise reduction"""
        
        # Use noisereduce library for advanced denoising
        denoised = nr.reduce_noise(
            y=audio, 
            sr=self.sample_rate,
            stationary=False,
            prop_decrease=0.8
        )
        
        return denoised
    
    def enhance_speech(self, audio: np.ndarray) -> np.ndarray:
        """Enhance speech clarity and quality"""
        
        # Apply band-pass filter for speech frequencies (85-8000 Hz)
        nyquist = self.sample_rate // 2
        low_freq = 85 / nyquist
        high_freq = 8000 / nyquist
        
        b, a = butter(4, [low_freq, high_freq], btype='band')
        filtered = filtfilt(b, a, audio)
        
        # Apply dynamic range compression
        compressed = self._apply_compression(filtered)
        
        # Enhance formants
        enhanced = self._enhance_formants(compressed)
        
        return enhanced
    
    def _apply_compression(self, audio: np.ndarray, threshold: float = 0.1, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        
        # Simple compression algorithm
        compressed = np.copy(audio)
        
        # Find samples above threshold
        above_threshold = np.abs(audio) > threshold
        
        # Apply compression ratio
        compressed[above_threshold] = np.sign(audio[above_threshold]) * (
            threshold + (np.abs(audio[above_threshold]) - threshold) / ratio
        )
        
        return compressed
    
    def _enhance_formants(self, audio: np.ndarray) -> np.ndarray:
        """Enhance formant frequencies for speech clarity"""
        
        # Get spectral features
        stft = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Enhance formant regions (typically 800-2000 Hz for speech)
        freqs = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        formant_mask = (freqs >= 800) & (freqs <= 2000)
        
        enhanced_magnitude = magnitude.copy()
        enhanced_magnitude[formant_mask] *= 1.2  # Boost formant frequencies
        
        # Reconstruct
        enhanced_stft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = librosa.istft(enhanced_stft, hop_length=self.hop_length)
        
        return enhanced_audio

class MultiSpeakerSeparation:
    """Multi-speaker voice separation and isolation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sample_rate = config.get('sample_rate', 22050)
        
    def separate_speakers(self, mixed_audio: np.ndarray, num_speakers: int = 2) -> List[np.ndarray]:
        """Separate multiple speakers from mixed audio"""
        
        # Use Independent Component Analysis (ICA) for basic separation
        from sklearn.decomposition import FastICA
        
        # Convert to spectrogram domain
        stft = librosa.stft(mixed_audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Apply ICA to magnitude spectrogram
        ica = FastICA(n_components=num_speakers, random_state=42)
        separated_magnitudes = ica.fit_transform(magnitude.T).T
        
        # Reconstruct separated audio signals
        separated_audios = []
        for i in range(num_speakers):
            # Use original phase (simplified approach)
            separated_stft = separated_magnitudes[i:i+1] * np.exp(1j * phase)
            separated_audio = librosa.istft(separated_stft)
            separated_audios.append(separated_audio)
        
        return separated_audios
    
    def identify_speaker(self, audio: np.ndarray, speaker_embeddings: Dict[str, np.ndarray]) -> str:
        """Identify speaker using voice embeddings"""
        
        # Extract MFCC features as simple speaker representation
        mfcc = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=13)
        audio_embedding = np.mean(mfcc, axis=1)
        
        # Compare with known speaker embeddings
        best_match = None
        best_similarity = -1
        
        for speaker_name, embedding in speaker_embeddings.items():
            # Cosine similarity
            similarity = np.dot(audio_embedding, embedding) / (
                np.linalg.norm(audio_embedding) * np.linalg.norm(embedding)
            )
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = speaker_name
        
        return best_match if best_similarity > 0.5 else "unknown"

class AudioMixer:
    """Advanced audio mixing and mastering"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sample_rate = config.get('sample_rate', 22050)
        
    def mix_tracks(self, tracks: List[Dict[str, Any]]) -> np.ndarray:
        """Mix multiple audio tracks with levels and effects"""
        
        if not tracks:
            return np.array([])
        
        # Find maximum duration
        max_duration = max(len(track['audio']) for track in tracks)
        
        # Initialize mixed audio
        mixed = np.zeros(max_duration)
        
        for track in tracks:
            audio = track['audio']
            level = track.get('level', 1.0)
            pan = track.get('pan', 0.0)  # -1 = left, 0 = center, 1 = right
            
            # Apply level
            processed_audio = audio * level
            
            # Pad audio to match duration
            if len(processed_audio) < max_duration:
                processed_audio = np.pad(processed_audio, (0, max_duration - len(processed_audio)))
            
            # Add to mix
            mixed += processed_audio[:max_duration]
        
        # Apply limiting to prevent clipping
        mixed = self._apply_limiter(mixed)
        
        return mixed
    
    def apply_eq(self, audio: np.ndarray, eq_bands: List[Dict[str, float]]) -> np.ndarray:
        """Apply parametric EQ"""
        
        processed = audio.copy()
        
        for band in eq_bands:
            freq = band['frequency']
            gain = band['gain']
            q = band.get('q', 1.0)
            
            # Apply peaking EQ filter
            processed = self._peaking_eq(processed, freq, gain, q)
        
        return processed
    
    def _peaking_eq(self, audio: np.ndarray, freq: float, gain: float, q: float) -> np.ndarray:
        """Apply peaking EQ filter"""
        
        nyquist = self.sample_rate / 2
        w = freq / nyquist
        
        # Convert gain from dB
        A = 10 ** (gain / 40)
        
        # Design peaking filter
        if gain >= 0:
            # Boost
            b, a = signal.iirpeak(w, q)
            filtered = signal.filtfilt(b * A, a, audio)
        else:
            # Cut
            b, a = signal.iirnotch(w, q)
            filtered = signal.filtfilt(b, a / A, audio)
        
        return filtered
    
    def _apply_limiter(self, audio: np.ndarray, threshold: float = 0.95) -> np.ndarray:
        """Apply audio limiter to prevent clipping"""
        
        # Find peak
        peak = np.max(np.abs(audio))
        
        if peak > threshold:
            # Apply limiting
            ratio = threshold / peak
            limited = audio * ratio
        else:
            limited = audio
        
        return limited
    
    def master_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply mastering chain"""
        
        # Apply standard mastering EQ
        eq_bands = [
            {'frequency': 80, 'gain': -2, 'q': 0.7},    # High-pass
            {'frequency': 2000, 'gain': 1, 'q': 1.0},   # Presence boost
            {'frequency': 8000, 'gain': 0.5, 'q': 0.7}  # Air boost
        ]
        
        mastered = self.apply_eq(audio, eq_bands)
        
        # Apply gentle compression
        mastered = self._apply_compression(mastered, threshold=0.7, ratio=2.0)
        
        # Final limiting
        mastered = self._apply_limiter(mastered, threshold=0.98)
        
        return mastered

class VoiceEmotionTransfer:
    """Voice emotion and style transfer"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sample_rate = config.get('sample_rate', 22050)
        
        # Emotion-specific prosody parameters
        self.emotion_profiles = {
            'happy': {'pitch_scale': 1.1, 'tempo_scale': 1.05, 'energy_scale': 1.2},
            'sad': {'pitch_scale': 0.9, 'tempo_scale': 0.95, 'energy_scale': 0.8},
            'angry': {'pitch_scale': 1.05, 'tempo_scale': 1.1, 'energy_scale': 1.3},
            'calm': {'pitch_scale': 0.95, 'tempo_scale': 0.9, 'energy_scale': 0.9},
            'excited': {'pitch_scale': 1.15, 'tempo_scale': 1.15, 'energy_scale': 1.4},
        }
    
    def transfer_emotion(self, audio: np.ndarray, target_emotion: str) -> np.ndarray:
        """Transfer emotion to voice"""
        
        if target_emotion not in self.emotion_profiles:
            logger.warning(f"Unknown emotion: {target_emotion}")
            return audio
        
        profile = self.emotion_profiles[target_emotion]
        
        # Apply pitch scaling
        pitched = librosa.effects.pitch_shift(
            audio, 
            sr=self.sample_rate, 
            n_steps=12 * np.log2(profile['pitch_scale'])
        )
        
        # Apply tempo scaling
        tempo_scaled = librosa.effects.time_stretch(pitched, rate=profile['tempo_scale'])
        
        # Apply energy scaling
        energy_scaled = tempo_scaled * profile['energy_scale']
        
        # Normalize to prevent clipping
        energy_scaled = energy_scaled / np.max(np.abs(energy_scaled)) * 0.95
        
        return energy_scaled
    
    def extract_prosody_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract prosodic features from audio"""
        
        # Extract fundamental frequency (pitch)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7')
        )
        
        # Calculate prosodic features
        features = {
            'f0_mean': np.nanmean(f0),
            'f0_std': np.nanstd(f0),
            'f0_range': np.nanmax(f0) - np.nanmin(f0),
            'voiced_ratio': np.mean(voiced_flag),
            'energy_mean': np.mean(librosa.feature.rms(y=audio)),
            'duration': len(audio) / self.sample_rate,
        }
        
        return features

class AdvancedAudioEngine:
    """Main audio processing engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.denoiser = AudioDenoiser(config)
        self.separator = MultiSpeakerSeparation(config)
        self.mixer = AudioMixer(config)
        self.emotion_transfer = VoiceEmotionTransfer(config)
        
    def process_audio_complete(self, audio_path: Path, 
                              processing_options: Dict[str, Any]) -> np.ndarray:
        """Complete audio processing pipeline"""
        
        logger.info(f"Processing audio: {audio_path}")
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=self.config.get('sample_rate', 22050))
        
        processed_audio = audio
        
        # Apply denoising if requested
        if processing_options.get('denoise', False):
            logger.info("Applying audio denoising")
            processed_audio = self.denoiser.adaptive_filter(processed_audio)
        
        # Apply speech enhancement if requested
        if processing_options.get('enhance_speech', False):
            logger.info("Enhancing speech clarity")
            processed_audio = self.denoiser.enhance_speech(processed_audio)
        
        # Apply emotion transfer if requested
        if 'target_emotion' in processing_options:
            logger.info(f"Applying emotion transfer: {processing_options['target_emotion']}")
            processed_audio = self.emotion_transfer.transfer_emotion(
                processed_audio, processing_options['target_emotion']
            )
        
        # Apply mastering if requested
        if processing_options.get('master', False):
            logger.info("Applying audio mastering")
            processed_audio = self.mixer.master_audio(processed_audio)
        
        return processed_audio
    
    def save_processed_audio(self, audio: np.ndarray, output_path: Path) -> bool:
        """Save processed audio to file"""
        try:
            sf.write(output_path, audio, self.config.get('sample_rate', 22050))
            logger.info(f"Saved processed audio: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return False
