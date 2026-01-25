"""
Training Script for Voice Deepfake Detector
Trains the model on real and fake audio samples
"""

import os
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import logging
from tqdm import tqdm
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from preprocessing import AudioPreprocessor
from model_lite import DeepfakeDetectorLite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetLoader:
    """Load and process audio dataset"""
    
    def __init__(self, dataset_path='datasets'):
        self.dataset_path = dataset_path
        self.preprocessor = AudioPreprocessor()
    
    def load_audio_files(self, folder_path, label):
        """
        Load all audio files from a folder
        
        Args:
            folder_path: Path to folder containing audio files
            label: 0 for FAKE, 1 for REAL
        
        Returns:
            features: List of extracted features
            labels: List of corresponding labels
        """
        features = []
        labels = []
        
        audio_files = [f for f in os.listdir(folder_path) 
                      if f.endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac'))]
        
        logger.info(f"Processing {len(audio_files)} files from {folder_path}")
        
        for audio_file in tqdm(audio_files, desc=f"Loading {os.path.basename(folder_path)}"):
            try:
                file_path = os.path.join(folder_path, audio_file)
                
                # Extract features
                feature = self.preprocessor.extract_features(file_path)
                
                # Flatten features for Random Forest
                feature_flat = feature.flatten()
                
                features.append(feature_flat)
                labels.append(label)
                
            except Exception as e:
                logger.warning(f"Error processing {audio_file}: {str(e)}")
                continue
        
        return features, labels
    
    def load_dataset(self, split='train'):
        """
        Load entire dataset (train or test)
        
        Args:
            split: 'train' or 'test'
        
        Returns:
            X: Feature array
            y: Label array
        """
        split_path = os.path.join(self.dataset_path, split)
        
        # Load real samples (label = 1)
        real_path = os.path.join(split_path, 'real')
        logger.info(f"\n{'='*60}")
        logger.info(f"Loading REAL samples from {real_path}")
        logger.info(f"{'='*60}")
        real_features, real_labels = self.load_audio_files(real_path, label=1)
        
        # Load fake samples (label = 0)
        fake_path = os.path.join(split_path, 'fake')
        logger.info(f"\n{'='*60}")
        logger.info(f"Loading FAKE samples from {fake_path}")
        logger.info(f"{'='*60}")
        fake_features, fake_labels = self.load_audio_files(fake_path, label=0)
        
        # Combine
        X = np.array(real_features + fake_features)
        y = np.array(real_labels + fake_labels)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Dataset loaded: {len(X)} samples")
        logger.info(f"  REAL: {sum(y == 1)} samples")
        logger.info(f"  FAKE: {sum(y == 0)} samples")
        logger.info(f"{'='*60}\n")
        
        return X, y


def train_model(dataset_path='datasets', save_path='models/deepfake_detector_lite_trained.pkl'):
    """
    Complete training pipeline
    
    Args:
        dataset_path: Path to dataset folder
        save_path: Path to save trained model
    """
    
    print("\n" + "="*70)
    print("  VOICE DEEPFAKE DETECTOR - TRAINING")
    print("="*70 + "\n")
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        logger.error(f"Dataset folder not found: {dataset_path}")
        logger.error("Please create the following structure:")
        logger.error("  datasets/")
        logger.error("    train/")
        logger.error("      real/  <- Put real audio files here")
        logger.error("      fake/  <- Put fake audio files here")
        logger.error("    test/")
        logger.error("      real/")
        logger.error("      fake/")
        return
    
    # Initialize components
    loader = DatasetLoader(dataset_path)
    model = DeepfakeDetectorLite()
    
    # Load training data
    logger.info("Loading training dataset...")
    X_train, y_train = loader.load_dataset('train')
    
    if len(X_train) == 0:
        logger.error("No training data found! Please add audio files to datasets/train/")
        return
    
    # Load test data (if exists)
    test_path = os.path.join(dataset_path, 'test')
    if os.path.exists(test_path):
        logger.info("Loading test dataset...")
        X_test, y_test = loader.load_dataset('test')
    else:
        logger.info("No separate test set found. Splitting training data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
    
    # Train model
    logger.info("\n" + "="*60)
    logger.info("TRAINING MODEL...")
    logger.info("="*60)
    
    model.train(X_train, y_train)
    
    # Evaluate
    logger.info("\n" + "="*60)
    logger.info("EVALUATING MODEL...")
    logger.info("="*60)
    
    # Predictions
    y_pred = model.model.predict(X_test)
    
    # Metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"RESULTS")
    logger.info(f"{'='*60}")
    logger.info(f"Accuracy: {accuracy*100:.2f}%")
    logger.info(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['FAKE', 'REAL']))
    
    logger.info(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"              Predicted")
    print(f"              FAKE  REAL")
    print(f"Actual FAKE   {cm[0][0]:4d}  {cm[0][1]:4d}")
    print(f"       REAL   {cm[1][0]:4d}  {cm[1][1]:4d}")
    
    # Save model
    logger.info(f"\n{'='*60}")
    logger.info(f"SAVING MODEL...")
    logger.info(f"{'='*60}")
    
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        pickle.dump(model.model, f)
    
    logger.info(f"✓ Model saved to: {save_path}")
    
    # Save to default location too (for app to use)
    default_path = 'backend/../models/deepfake_detector_lite.pkl'
    os.makedirs(os.path.dirname(default_path), exist_ok=True)
    with open(default_path, 'wb') as f:
        pickle.dump(model.model, f)
    logger.info(f"✓ Model saved to: {default_path}")
    
    print("\n" + "="*70)
    print("  TRAINING COMPLETE!")
    print(f"  Accuracy: {accuracy*100:.2f}%")
    print("  Model ready to use in the application")
    print("="*70 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Voice Deepfake Detector')
    parser.add_argument('--dataset', type=str, default='datasets',
                       help='Path to dataset folder (default: datasets)')
    parser.add_argument('--output', type=str, default='models/deepfake_detector_lite_trained.pkl',
                       help='Path to save trained model (default: models/deepfake_detector_lite_trained.pkl)')
    
    args = parser.parse_args()
    
    train_model(args.dataset, args.output)
