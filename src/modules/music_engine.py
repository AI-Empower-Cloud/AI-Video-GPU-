"""
Music and Audio Composition Engine
Handles background music integration and audio mixing
"""

import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Union, List
from loguru import logger
import scipy.signal
from pydub import AudioSegment
import tempfile

class MusicEngine:
    """
    Advanced audio composition engine for background music and sound effects
    Supports automatic music generation and intelligent mixing
    """
    
    def __init__(self, config):
        self.config = config
        self.sample_rate = config.tts.sample_rate
        
    def compose_audio(
        self,
        speech_audio: str,
        background_music: Optional[str] = None,
        output_path: str = "output/final_audio.wav",
        auto_generate_music: bool = None
    ) -> str:
        """
        Compose final audio with speech and background music
        
        Args:
            speech_audio: Path to speech audio file
            background_music: Path to background music (optional)
            output_path: Where to save the final composed audio
            auto_generate_music: Whether to auto-generate music if none provided
            
        Returns:
            Path to final composed audio file
        """
        logger.info("Starting audio composition...")
        
        try:
            # Load speech audio
            speech, sr = librosa.load(speech_audio, sr=self.sample_rate)
            speech_duration = len(speech) / sr
            
            # Handle background music
            if background_music:
                music = self._load_and_prepare_music(background_music, speech_duration)
            elif auto_generate_music or (auto_generate_music is None and self.config.music.auto_generate):
                music = self._generate_background_music(speech_duration)
            else:
                music = np.zeros_like(speech)
            
            # Mix audio tracks
            final_audio = self._mix_audio_tracks(speech, music)
            
            # Apply audio effects
            final_audio = self._apply_audio_effects(final_audio)
            
            # Save final audio
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            sf.write(str(output_path), final_audio, self.sample_rate)
            
            logger.success(f"Audio composition completed: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Audio composition failed: {e}")
            # Fallback: return original speech audio
            return speech_audio
    
    def _load_and_prepare_music(self, music_path: str, target_duration: float) -> np.ndarray:
        """Load and prepare background music to match target duration"""
        logger.info(f"Loading background music: {music_path}")
        
        # Load music
        music, sr = librosa.load(music_path, sr=self.sample_rate)
        music_duration = len(music) / sr
        
        # Adjust duration to match speech
        if music_duration < target_duration:
            # Loop music if too short
            loops_needed = int(np.ceil(target_duration / music_duration))
            music = np.tile(music, loops_needed)
        
        # Trim to exact duration
        target_samples = int(target_duration * sr)
        music = music[:target_samples]
        
        # Apply fade in/out
        music = self._apply_fade_effects(music)
        
        # Adjust volume
        music = music * self.config.music.volume_level
        
        return music
    
    def _generate_background_music(self, duration: float) -> np.ndarray:
        """Generate background music automatically"""
        logger.info(f"Auto-generating background music for {duration:.2f}s")
        
        # This is a simplified music generator
        # In a real implementation, you might use:
        # - AI music generation models (MusicGen, AudioLM, etc.)
        # - Procedural music generation
        # - Pre-composed loops and stems
        
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        # Generate ambient music with multiple harmonic layers
        fundamental_freq = 220  # A3
        music = np.zeros(samples)
        
        # Add harmonic layers
        for harmonic in [1, 2, 3, 5]:
            freq = fundamental_freq * harmonic
            amplitude = 0.1 / harmonic  # Decreasing amplitude for higher harmonics
            
            # Add some frequency modulation for interest
            fm_freq = 0.5  # Slow modulation
            fm_depth = 5   # Hz
            
            phase = 2 * np.pi * freq * t + fm_depth * np.sin(2 * np.pi * fm_freq * t)
            music += amplitude * np.sin(phase)
        
        # Add subtle percussion
        beat_freq = 1.5  # BPM / 60
        beats = np.sin(2 * np.pi * beat_freq * t) * 0.05
        # Apply envelope to make it more drum-like
        beat_envelope = np.exp(-10 * (t % (1/beat_freq)))
        beats *= beat_envelope
        
        music += beats
        
        # Apply envelope to entire piece
        attack_time = 2.0  # seconds
        release_time = 2.0  # seconds
        
        envelope = np.ones_like(music)
        
        # Attack
        attack_samples = int(attack_time * self.sample_rate)
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Release
        release_samples = int(release_time * self.sample_rate)
        envelope[-release_samples:] = np.linspace(1, 0, release_samples)
        
        music *= envelope
        
        # Normalize and apply volume
        music = music / np.max(np.abs(music)) * self.config.music.volume_level
        
        logger.info("Background music generation completed")
        return music
    
    def _mix_audio_tracks(self, speech: np.ndarray, music: np.ndarray) -> np.ndarray:
        """Mix speech and music tracks with intelligent ducking"""
        logger.info("Mixing audio tracks...")
        
        # Ensure both tracks are the same length
        min_length = min(len(speech), len(music))
        speech = speech[:min_length]
        music = music[:min_length]
        
        # Apply ducking (lower music volume when speech is present)
        ducked_music = self._apply_ducking(speech, music)
        
        # Mix the tracks
        mixed = speech + ducked_music
        
        # Prevent clipping
        max_amplitude = np.max(np.abs(mixed))
        if max_amplitude > 0.95:
            mixed = mixed * (0.95 / max_amplitude)
        
        return mixed
    
    def _apply_ducking(self, speech: np.ndarray, music: np.ndarray) -> np.ndarray:
        """Apply ducking effect to lower music volume during speech"""
        # Calculate speech energy envelope
        window_size = int(0.1 * self.sample_rate)  # 100ms windows
        speech_energy = self._calculate_energy_envelope(speech, window_size)
        
        # Create ducking envelope
        threshold = 0.01  # Speech detection threshold
        duck_amount = 0.3  # How much to duck (0.3 = 70% reduction)
        
        ducking_envelope = np.ones_like(speech_energy)
        speech_present = speech_energy > threshold
        ducking_envelope[speech_present] = duck_amount
        
        # Smooth the ducking envelope
        ducking_envelope = scipy.signal.savgol_filter(ducking_envelope, 
                                                      window_length=int(0.2 * self.sample_rate) | 1, 
                                                      polyorder=3)
        
        # Apply ducking to music
        ducked_music = music * ducking_envelope
        
        return ducked_music
    
    def _calculate_energy_envelope(self, audio: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate energy envelope of audio signal"""
        # Calculate RMS energy in sliding windows
        audio_squared = audio ** 2
        energy = np.convolve(audio_squared, np.ones(window_size) / window_size, mode='same')
        return np.sqrt(energy)
    
    def _apply_fade_effects(self, audio: np.ndarray) -> np.ndarray:
        """Apply fade in/out effects"""
        fade_duration = self.config.music.fade_duration
        fade_samples = int(fade_duration * self.sample_rate)
        
        if len(audio) <= 2 * fade_samples:
            # Audio too short for fade effects
            return audio
        
        # Apply fade in
        fade_in = np.linspace(0, 1, fade_samples)
        audio[:fade_samples] *= fade_in
        
        # Apply fade out
        fade_out = np.linspace(1, 0, fade_samples)
        audio[-fade_samples:] *= fade_out
        
        return audio
    
    def _apply_audio_effects(self, audio: np.ndarray) -> np.ndarray:
        """Apply various audio effects to enhance the final mix"""
        logger.info("Applying audio effects...")
        
        # Apply subtle compression
        audio = self._apply_compression(audio)
        
        # Apply EQ (subtle high-frequency boost)
        audio = self._apply_eq(audio)
        
        # Apply subtle reverb if enabled
        if self.config.audio_3d.enabled and self.config.audio_3d.reverb_level > 0:
            audio = self._apply_reverb(audio)
        
        return audio
    
    def _apply_compression(self, audio: np.ndarray, threshold: float = 0.7, ratio: float = 4.0) -> np.ndarray:
        """Apply dynamic range compression"""
        # Simple compression algorithm
        compressed = audio.copy()
        
        # Find samples above threshold
        above_threshold = np.abs(audio) > threshold
        
        # Apply compression to loud samples
        compressed[above_threshold] = np.sign(audio[above_threshold]) * (
            threshold + (np.abs(audio[above_threshold]) - threshold) / ratio
        )
        
        return compressed
    
    def _apply_eq(self, audio: np.ndarray) -> np.ndarray:
        """Apply basic EQ (high-frequency boost)"""
        # Design a simple high-shelf filter
        nyquist = self.sample_rate / 2
        cutoff = 5000  # Hz
        
        # Butterworth high-pass filter
        sos = scipy.signal.butter(2, cutoff / nyquist, btype='high', output='sos')
        
        # Apply filter with gain
        filtered = scipy.signal.sosfilt(sos, audio)
        
        # Mix with original (subtle boost)
        eq_amount = 0.1
        return audio + eq_amount * filtered
    
    def _apply_reverb(self, audio: np.ndarray) -> np.ndarray:
        """Apply simple reverb effect"""
        reverb_level = self.config.audio_3d.reverb_level
        
        # Simple reverb using multiple delayed copies
        reverb = np.zeros_like(audio)
        
        delays = [0.03, 0.07, 0.11, 0.15]  # seconds
        gains = [0.6, 0.4, 0.3, 0.2]
        
        for delay, gain in zip(delays, gains):
            delay_samples = int(delay * self.sample_rate)
            if delay_samples < len(audio):
                delayed = np.roll(audio, delay_samples)
                delayed[:delay_samples] = 0  # Clear the wrapped portion
                reverb += delayed * gain
        
        # Mix with original
        return audio + reverb * reverb_level
    
    def extract_music_features(self, music_path: str) -> dict:
        """Extract features from music file for intelligent mixing"""
        logger.info(f"Analyzing music features: {music_path}")
        
        # Load music
        y, sr = librosa.load(music_path, sr=self.sample_rate)
        
        # Extract features
        features = {}
        
        # Tempo
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        features['tempo'] = float(tempo)
        
        # Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
        
        # Zero crossing rate (indicates percussive content)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        features['zero_crossing_rate_mean'] = float(np.mean(zcr))
        
        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        features['rms_mean'] = float(np.mean(rms))
        
        # Chroma features (harmony)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
        
        logger.info(f"Music analysis completed: Tempo={tempo:.1f} BPM")
        return features
    
    def create_music_playlist(self, moods: List[str], total_duration: float) -> List[str]:
        """Create a playlist of generated music segments for different moods"""
        logger.info(f"Creating music playlist for moods: {moods}")
        
        playlist = []
        segment_duration = total_duration / len(moods)
        
        for i, mood in enumerate(moods):
            output_path = f"temp/music_segment_{i}_{mood}.wav"
            
            # Generate music for specific mood
            music = self._generate_mood_music(mood, segment_duration)
            
            # Save segment
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            sf.write(output_path, music, self.sample_rate)
            
            playlist.append(output_path)
        
        return playlist
    
    def _generate_mood_music(self, mood: str, duration: float) -> np.ndarray:
        """Generate music based on specified mood"""
        # This would be expanded with more sophisticated mood-based generation
        mood_configs = {
            'calm': {'tempo': 60, 'base_freq': 220, 'complexity': 0.3},
            'energetic': {'tempo': 120, 'base_freq': 440, 'complexity': 0.8},
            'mysterious': {'tempo': 80, 'base_freq': 110, 'complexity': 0.6},
            'happy': {'tempo': 100, 'base_freq': 330, 'complexity': 0.5}
        }
        
        config = mood_configs.get(mood, mood_configs['calm'])
        
        # Generate music with mood-specific parameters
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples, False)
        
        base_freq = config['base_freq']
        complexity = config['complexity']
        
        music = np.zeros(samples)
        
        # Generate harmonics based on complexity
        num_harmonics = int(5 * complexity) + 1
        for i in range(1, num_harmonics + 1):
            amplitude = 0.2 / i * complexity
            music += amplitude * np.sin(2 * np.pi * base_freq * i * t)
        
        # Apply mood-specific envelope
        if mood == 'energetic':
            # Add more dynamic variation
            envelope = 1 + 0.3 * np.sin(2 * np.pi * 2 * t)  # 2 Hz variation
            music *= envelope
        
        return music
