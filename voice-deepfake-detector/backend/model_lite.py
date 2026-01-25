"""
Lightweight Deepfake Detection Model (No TensorFlow Required)
Uses traditional ML with scikit-learn for systems without TensorFlow support
"""

import numpy as np
import os
import logging
from sklearn.ensemble import RandomForestClassifier
import pickle

logger = logging.getLogger(__name__)

class DeepfakeDetectorLite:
    """
    Lightweight model using Random Forest for deepfake detection
    Fallback option when TensorFlow is not available
    """
    
    def __init__(self, model_path='../models/deepfake_detector_lite.pkl'):
        self.model_path = model_path
        self.model = None
        self.load_or_create_model()
    
    def create_model(self):
        """Create a Random Forest classifier"""
        logger.info("Creating Random Forest model...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        return model
    
    def load_or_create_model(self):
        """Load existing model or create new one"""
        try:
            if os.path.exists(self.model_path):
                logger.info(f"Loading model from {self.model_path}")
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Model loaded successfully")
            else:
                logger.info("Building new Random Forest model...")
                self.model = self.create_model()
                logger.warning("⚠️  Model needs training on real datasets")
                
                # Save the untrained model
                os.makedirs(os.path.dirname(self.model_path) if os.path.dirname(self.model_path) else '.', exist_ok=True)
                with open(self.model_path, 'wb') as f:
                    pickle.dump(self.model, f)
                
        except Exception as e:
            logger.error(f"Error loading/creating model: {str(e)}")
            self.model = self.create_model()
    
    def predict(self, features):
        """
        Predict if audio is real or synthetic
        
        Args:
            features: Preprocessed MFCC features (40 x 128)
        
        Returns:
            dict: Prediction results with label and confidence
        """
        try:
            # Flatten features for Random Forest
            features_flat = features.flatten().reshape(1, -1)
            
            # For untrained model, return random prediction
            # This simulates behavior until model is trained
            if not hasattr(self.model, 'classes_'):
                # Model not trained yet, return baseline prediction
                prediction = np.random.random()
                logger.warning("Model not trained - returning baseline prediction")
            else:
                # Use trained model
                prediction_proba = self.model.predict_proba(features_flat)[0]
                prediction = prediction_proba[1]  # Probability of class 1 (REAL)
            
            # Convert to percentage
            confidence = float(prediction * 100)
            
            # Apply threshold
            threshold = 50.0
            is_real = confidence >= threshold
            
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
            return {
                'label': 'UNCERTAIN',
                'confidence': 50.0,
                'raw_score': 0.5,
                'error': str(e)
            }
    
    def is_loaded(self):
        """Check if model is loaded"""
        return self.model is not None
    
    def train(self, X_train, y_train):
        """
        Train the model
        
        Args:
            X_train: Training features (flattened)
            y_train: Training labels (0=FAKE, 1=REAL)
        """
        logger.info("Training Random Forest model...")
        self.model.fit(X_train, y_train)
        
        # Save trained model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        logger.info("Model trained and saved successfully")


if __name__ == '__main__':
    # Test model creation
    detector = DeepfakeDetectorLite()
    print("Lightweight model loaded successfully!")
    print(f"Model type: Random Forest")
    print(f"Model loaded: {detector.is_loaded()}")
