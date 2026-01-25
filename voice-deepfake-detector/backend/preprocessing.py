"""
Audio Preprocessing Module
Extracts MFCC and spectral features from audio files
"""

# Disable numba to avoid NumPy version conflicts
import os
os.environ['NUMBA_DISABLE_JIT'] = '1'

import librosa
import numpy as np
import logging
from scipy import signal

logger = logging.getLogger(__name__)

class AudioPreprocessor:
    """
    Audio feature extraction for deepfake detection
    Extracts MFCCs, mel-spectrograms, and other acoustic features
    """
    
    def __init__(self, sample_rate=16000, n_mfcc=40, n_fft=2048, hop_length=512):
        """
        Initialize preprocessor
        
        Args:
            sample_rate: Target sample rate for audio
            n_mfcc: Number of MFCC coefficients to extract
            n_fft: FFT window size
            hop_length: Number of samples between successive frames
        """
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.target_length = 128  # Target number of time steps
    
    def load_audio(self, file_path):
        """
        Load audio file and resample to target sample rate
        
        Args:
            file_path: Path to audio file
        
        Returns:
            tuple: (audio_data, sample_rate)
        """
        try:
            # Load audio with librosa
            audio, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            logger.info(f"Loaded audio: duration={len(audio)/sr:.2f}s, sr={sr}Hz")
            return audio, sr
        except Exception as e:
            logger.error(f"Error loading audio: {str(e)}")
            raise
    
    def extract_mfcc(self, audio):
        """
        Extract MFCC features from audio
        
        Args:
            audio: Audio time series
        
        Returns:
            numpy.ndarray: MFCC features (n_mfcc x time_steps)
        """
        # Extract MFCCs
        mfccs = librosa.feature.mfcc(
            y=audio,
            sr=self.sample_rate,
            n_mfcc=self.n_mfcc,
            n_fft=self.n_fft,
            hop_length=self.hop_length
        )
        
        # Apply delta and delta-delta for temporal dynamics
        mfcc_delta = librosa.feature.delta(mfccs)
        mfcc_delta2 = librosa.feature.delta(mfccs, order=2)
        
        # Combine features
        combined = np.vstack([mfccs, mfcc_delta, mfcc_delta2])
        
        return combined
    
    def extract_mel_spectrogram(self, audio):
        """
        Extract mel-spectrogram from audio
        
        Args:
            audio: Audio time series
        
        Returns:
            numpy.ndarray: Mel-spectrogram
        """
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=self.sample_rate,
            n_fft=self.n_fft,
            hop_length=self.hop_length,
            n_mels=128
        )
        
        # Convert to log scale (dB)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        return mel_spec_db
    
    def extract_spectral_features(self, audio):
        """
        Extract additional spectral features
        
        Args:
            audio: Audio time series
        
        Returns:
            dict: Dictionary of spectral features
        """
        features = {}
        
        # Spectral centroid
        features['spectral_centroid'] = librosa.feature.spectral_centroid(
            y=audio, sr=self.sample_rate
        )
        
        # Spectral rolloff
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
            y=audio, sr=self.sample_rate
        )
        
        # Zero crossing rate
        features['zero_crossing_rate'] = librosa.feature.zero_crossing_rate(audio)
        
        # Chroma features
        features['chroma'] = librosa.feature.chroma_stft(
            y=audio, sr=self.sample_rate
        )
        
        return features
    
    def pad_or_truncate(self, features, target_length):
        """
        Pad or truncate features to target length
        
        Args:
            features: Feature array (n_features x time_steps)
            target_length: Target number of time steps
        
        Returns:
            numpy.ndarray: Padded/truncated features
        """
        current_length = features.shape[1]
        
        if current_length < target_length:
            # Pad with zeros
            pad_width = target_length - current_length
            features = np.pad(features, ((0, 0), (0, pad_width)), mode='constant')
        elif current_length > target_length:
            # Truncate
            features = features[:, :target_length]
        
        return features
    
    def normalize_features(self, features):
        """
        Normalize features using mean and standard deviation
        
        Args:
            features: Feature array
        
        Returns:
            numpy.ndarray: Normalized features
        """
        mean = np.mean(features, axis=1, keepdims=True)
        std = np.std(features, axis=1, keepdims=True)
        
        # Avoid division by zero
        std = np.where(std == 0, 1, std)
        
        normalized = (features - mean) / std
        
        return normalized
    
    def extract_features(self, file_path):
        """
        Complete feature extraction pipeline
        
        Args:
            file_path: Path to audio file
        
        Returns:
            numpy.ndarray: Processed features ready for model input (40 x 128)
        """
        try:
            # Load audio
            audio, sr = self.load_audio(file_path)
            
            # Pre-emphasis filter (amplify high frequencies)
            audio = self.apply_preemphasis(audio)
            
            # Extract MFCC features
            mfccs = self.extract_mfcc(audio)
            
            # Take only the base MFCCs (first n_mfcc coefficients)
            # This ensures we get exactly 40 features
            mfccs = mfccs[:self.n_mfcc, :]
            
            # Pad or truncate to target length
            mfccs = self.pad_or_truncate(mfccs, self.target_length)
            
            # Normalize features
            mfccs = self.normalize_features(mfccs)
            
            logger.info(f"Extracted features shape: {mfccs.shape}")
            
            return mfccs
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            raise
    
    def apply_preemphasis(self, audio, coef=0.97):
        """
        Apply pre-emphasis filter to amplify high frequencies
        
        Args:
            audio: Audio signal
            coef: Pre-emphasis coefficient
        
        Returns:
            numpy.ndarray: Filtered audio
        """
        return np.append(audio[0], audio[1:] - coef * audio[:-1])
    
    def remove_silence(self, audio, top_db=20):
        """
        Remove leading and trailing silence
        
        Args:
            audio: Audio signal
            top_db: Threshold for silence detection
        
        Returns:
            numpy.ndarray: Audio with silence removed
        """
        # Trim silence
        audio_trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        return audio_trimmed
    
    def augment_audio(self, audio):
        """
        Apply data augmentation techniques
        Useful for training data augmentation
        
        Args:
            audio: Audio signal
        
        Returns:
            numpy.ndarray: Augmented audio
        """
        augmentation_type = np.random.choice(['time_stretch', 'pitch_shift', 'noise', 'none'])
        
        if augmentation_type == 'time_stretch':
            # Time stretching (0.8x to 1.2x speed)
            rate = np.random.uniform(0.8, 1.2)
            audio = librosa.effects.time_stretch(audio, rate=rate)
        
        elif augmentation_type == 'pitch_shift':
            # Pitch shifting (-2 to +2 semitones)
            n_steps = np.random.uniform(-2, 2)
            audio = librosa.effects.pitch_shift(
                audio, sr=self.sample_rate, n_steps=n_steps
            )
        
        elif augmentation_type == 'noise':
            # Add white noise
            noise_factor = 0.005
            noise = np.random.randn(len(audio))
            audio = audio + noise_factor * noise
        
        return audio


# Data augmentation functions for training
def apply_time_masking(features, max_mask_size=10):
    """
    Apply time masking augmentation (SpecAugment)
    
    Args:
        features: Feature array (n_features x time_steps)
        max_mask_size: Maximum size of time mask
    
    Returns:
        numpy.ndarray: Masked features
    """
    features = features.copy()
    mask_size = np.random.randint(1, max_mask_size)
    mask_start = np.random.randint(0, features.shape[1] - mask_size)
    features[:, mask_start:mask_start + mask_size] = 0
    return features


def apply_frequency_masking(features, max_mask_size=10):
    """
    Apply frequency masking augmentation (SpecAugment)
    
    Args:
        features: Feature array (n_features x time_steps)
        max_mask_size: Maximum size of frequency mask
    
    Returns:
        numpy.ndarray: Masked features
    """
    features = features.copy()
    mask_size = np.random.randint(1, max_mask_size)
    mask_start = np.random.randint(0, features.shape[0] - mask_size)
    features[mask_start:mask_start + mask_size, :] = 0
    return features


if __name__ == '__main__':
    # Test preprocessor
    preprocessor = AudioPreprocessor()
    print("Audio Preprocessor initialized successfully!")
    print(f"Configuration:")
    print(f"  Sample rate: {preprocessor.sample_rate} Hz")
    print(f"  MFCC coefficients: {preprocessor.n_mfcc}")
    print(f"  Target length: {preprocessor.target_length} frames")
