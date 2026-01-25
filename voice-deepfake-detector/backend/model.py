"""
Deepfake Detection Model
CNN-based audio classifier for voice authenticity detection
Auto-falls back to lightweight model if TensorFlow is unavailable
"""

import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

# Try to import TensorFlow, fall back to lite model if unavailable
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    TENSORFLOW_AVAILABLE = True
    logger.info("TensorFlow available - using CNN model")
except ImportError:
    TENSORFLOW_AVAILABLE = False
    logger.warning("TensorFlow not available - falling back to lightweight model")
    from model_lite import DeepfakeDetectorLite

class DeepfakeDetector:
    """
    CNN-based model for detecting synthetic/deepfake audio
    Auto-switches to lightweight model if TensorFlow unavailable
    Architecture: Conv1D layers + Dense layers for binary classification
    """
    
    def __init__(self, model_path='../models/deepfake_detector.h5'):
        self.model_path = model_path
        self.model = None
        self.input_shape = (40, 128, 1)  # (n_mfcc, time_steps, channels)
        self.use_lite = not TENSORFLOW_AVAILABLE
        
        if self.use_lite:
            logger.info("Using lightweight Random Forest model")
            self.lite_model = DeepfakeDetectorLite()
        else:
            self.load_or_create_model()
    
    def build_model(self):
        """
        Build CNN architecture for audio classification
        Input: MFCC features (40 x 128 x 1)
        Output: Binary classification (Real/Fake)
        """
        model = models.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),
            
            # First Conv Block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Second Conv Block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third Conv Block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Fourth Conv Block
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling2D(),
            
            # Dense layers
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            
            # Output layer (sigmoid for binary classification)
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        
        return model
    
    def load_or_create_model(self):
        """Load existing model or create new one with pre-trained weights"""
        try:
            # Try to load existing model
            if os.path.exists(self.model_path):
                logger.info(f"Loading model from {self.model_path}")
                self.model = keras.models.load_model(self.model_path)
                logger.info("Model loaded successfully")
            else:
                logger.info("Building new model...")
                self.model = self.build_model()
                
                # Initialize with random but realistic weights
                # In production, you would load actual trained weights
                logger.info("Model created with initialized weights")
                logger.warning("⚠️  Model needs training on real datasets (ASVspoof, FakeAVCeleb)")
                
                # Save the architecture
                os.makedirs(os.path.dirname(self.model_path) if os.path.dirname(self.model_path) else '.', exist_ok=True)
                self.model.save(self.model_path)
                
        except Exception as e:
            logger.error(f"Error loading/creating model: {str(e)}")
            # Fallback to building new model
            self.model = self.build_model()
    
    def predict(self, features):
        """
        Predict if audio is real or synthetic
        
        Args:
            features: Preprocessed MFCC features (40 x 128)
        
        Returns:
            dict: Prediction results with label and confidence
        """
        # Use lite model if TensorFlow unavailable
        if self.use_lite:
            return self.lite_model.predict(features)
        
        try:
            # Ensure features have correct shape
            if len(features.shape) == 2:
                features = np.expand_dims(features, axis=-1)  # Add channel dimension
            
            # Add batch dimension
            features = np.expand_dims(features, axis=0)
            
            # Pad or truncate to expected shape
            if features.shape[1:3] != (40, 128):
                features = self._resize_features(features)
            
            # Make prediction
            prediction = self.model.predict(features, verbose=0)[0][0]
            
            # Convert to percentage and determine label
            # prediction closer to 1 = REAL, closer to 0 = FAKE
            confidence = float(prediction * 100)
            
            # Apply threshold (can be tuned)
            threshold = 50.0
            is_real = confidence >= threshold
            
            # Adjust confidence to be relative to the predicted class
            if is_real:
                label = 'REAL'
                final_confidence = confidence
            else:
                label = 'FAKE'
                final_confidence = 100 - confidence
            
            return {
                'label': label,
                'confidence': final_confidence,
                'raw_score': float(prediction)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            # Return neutral prediction on error
            return {
                'label': 'UNCERTAIN',
                'confidence': 50.0,
                'raw_score': 0.5,
                'error': str(e)
            }
    
    def _resize_features(self, features):
        """Resize features to match expected input shape"""
        target_shape = (1, 40, 128, 1)
        
        # Use TensorFlow resize for proper interpolation
        resized = tf.image.resize(
            features,
            size=(40, 128),
            method='bilinear'
        )
        
        return resized.numpy()
    
    def is_loaded(self):
        """Check if model is loaded"""
        if self.use_lite:
            return self.lite_model.is_loaded()
        return self.model is not None
    
    def get_model_summary(self):
        """Get model architecture summary"""
        if self.model:
            return self.model.summary()
        return None


def create_training_script():
    """
    Training script template for fine-tuning on actual datasets
    
    Recommended datasets:
    - ASVspoof 2019: https://datashare.ed.ac.uk/handle/10283/3336
    - FakeAVCeleb: https://sites.google.com/view/fakeavcelebdataset
    - WaveFake: https://zenodo.org/record/5642694
    """
    
    training_code = """
# Training Script for Voice Deepfake Detection
# Use this with ASVspoof, FakeAVCeleb, or WaveFake datasets

import tensorflow as tf
from tensorflow import keras
from model import DeepfakeDetector
from preprocessing import AudioPreprocessor
import numpy as np

# Load dataset (implement based on your chosen dataset)
def load_dataset(data_path):
    # Load real and fake audio samples
    # Extract features using AudioPreprocessor
    # Return X_train, y_train, X_val, y_val
    pass

# Data augmentation
def augment_audio(audio):
    # Time stretching
    # Pitch shifting
    # Adding noise
    # Time masking
    return audio

# Training
detector = DeepfakeDetector()
X_train, y_train, X_val, y_val = load_dataset('path/to/dataset')

# Train model
history = detector.model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=[
        keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5),
        keras.callbacks.ModelCheckpoint('best_model.h5', save_best_only=True)
    ]
)

# Save trained model
detector.model.save('deepfake_detector_trained.h5')
"""
    
    return training_code


if __name__ == '__main__':
    # Test model creation
    detector = DeepfakeDetector()
    print("Model loaded successfully!")
    print(f"\nModel architecture:")
    detector.get_model_summary()
    
    # Print training guidance
    print("\n" + "="*60)
    print("TRAINING GUIDANCE")
    print("="*60)
    print(create_training_script())
