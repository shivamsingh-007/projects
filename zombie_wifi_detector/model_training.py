"""
Model Training Module
Trains ML models for zombie WiFi detection
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
import xgboost as xgb
import joblib
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZombieWiFiModel:
    """Machine learning model for zombie WiFi detection"""
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize model
        
        Args:
            model_type: 'random_forest', 'xgboost', or 'isolation_forest'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.trained = False
        self.metrics = {}
        
    def train(self, X_train, y_train, X_val=None, y_val=None, hyperparameter_tuning=False):
        """
        Train the model
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            hyperparameter_tuning: Whether to perform hyperparameter tuning
        """
        logger.info(f"Training {self.model_type} model...")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if self.model_type == 'random_forest':
            self.model = self._train_random_forest(
                X_train_scaled, y_train, hyperparameter_tuning
            )
        elif self.model_type == 'xgboost':
            self.model = self._train_xgboost(
                X_train_scaled, y_train, X_val, y_val, hyperparameter_tuning
            )
        elif self.model_type == 'isolation_forest':
            self.model = self._train_isolation_forest(X_train_scaled)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.trained = True
        logger.info("Model training completed")
        
        # Evaluate on training data
        train_pred = self.predict(X_train)
        self._calculate_metrics(y_train, train_pred, 'train')
        
        # Evaluate on validation data if provided
        if X_val is not None and y_val is not None:
            val_pred = self.predict(X_val)
            self._calculate_metrics(y_val, val_pred, 'validation')
        
        return self.model
    
    def _train_random_forest(self, X_train, y_train, hyperparameter_tuning):
        """Train Random Forest classifier"""
        
        if hyperparameter_tuning:
            logger.info("Performing hyperparameter tuning...")
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            rf = RandomForestClassifier(random_state=42)
            grid_search = GridSearchCV(
                rf, param_grid, cv=5, 
                scoring='f1', n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train, y_train)
            
            logger.info(f"Best parameters: {grid_search.best_params_}")
            return grid_search.best_estimator_
        else:
            # Default parameters
            rf = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=10,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            rf.fit(X_train, y_train)
            return rf
    
    def _train_xgboost(self, X_train, y_train, X_val, y_val, hyperparameter_tuning):
        """Train XGBoost classifier"""
        
        if hyperparameter_tuning:
            logger.info("Performing hyperparameter tuning...")
            param_grid = {
                'n_estimators': [100, 150, 200],
                'max_depth': [5, 10, 15],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            }
            
            xgb_model = xgb.XGBClassifier(random_state=42)
            grid_search = GridSearchCV(
                xgb_model, param_grid, cv=5,
                scoring='f1', n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train, y_train)
            
            logger.info(f"Best parameters: {grid_search.best_params_}")
            return grid_search.best_estimator_
        else:
            # Default parameters
            xgb_model = xgb.XGBClassifier(
                n_estimators=150,
                max_depth=15,
                learning_rate=0.1,
                subsample=0.9,
                random_state=42
            )
            
            # Use validation set if provided
            eval_set = [(X_train, y_train)]
            if X_val is not None and y_val is not None:
                X_val_scaled = self.scaler.transform(X_val)
                eval_set.append((X_val_scaled, y_val))
            
            xgb_model.fit(
                X_train, y_train,
                eval_set=eval_set,
                verbose=False
            )
            return xgb_model
    
    def _train_isolation_forest(self, X_train):
        """Train Isolation Forest for anomaly detection"""
        
        iso_forest = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42,
            n_jobs=-1
        )
        iso_forest.fit(X_train)
        return iso_forest
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X: Features to predict
            
        Returns:
            Predictions (0 = normal, 1 = zombie WiFi)
        """
        if not self.trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        
        if self.model_type == 'isolation_forest':
            # Isolation Forest returns -1 for anomalies, 1 for normal
            predictions = self.model.predict(X_scaled)
            # Convert to 0/1 format
            predictions = np.where(predictions == -1, 1, 0)
        else:
            predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def predict_proba(self, X):
        """
        Predict probability scores
        
        Args:
            X: Features to predict
            
        Returns:
            Probability scores for each class
        """
        if not self.trained:
            raise ValueError("Model must be trained before prediction")
        
        if self.model_type == 'isolation_forest':
            # Isolation Forest uses decision_function instead
            X_scaled = self.scaler.transform(X)
            scores = self.model.decision_function(X_scaled)
            # Convert to probability-like scores (0-1 range)
            proba = (scores - scores.min()) / (scores.max() - scores.min())
            return np.column_stack([1 - proba, proba])
        else:
            X_scaled = self.scaler.transform(X)
            return self.model.predict_proba(X_scaled)
    
    def _calculate_metrics(self, y_true, y_pred, dataset_name):
        """Calculate and store performance metrics"""
        
        self.metrics[dataset_name] = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0)
        }
        
        # Add AUC-ROC if probabilities available
        if self.model_type != 'isolation_forest':
            try:
                y_proba = self.predict_proba(y_true.reshape(-1, len(self.feature_names)) 
                                            if isinstance(y_true, np.ndarray) else y_true)
                self.metrics[dataset_name]['auc_roc'] = roc_auc_score(y_true, y_proba[:, 1])
            except:
                pass
        
        logger.info(f"\n{dataset_name.upper()} Metrics:")
        for metric, value in self.metrics[dataset_name].items():
            logger.info(f"  {metric}: {value:.4f}")
    
    def get_feature_importance(self, feature_names=None):
        """Get feature importance scores"""
        
        if not self.trained:
            raise ValueError("Model must be trained before getting feature importance")
        
        if self.model_type == 'isolation_forest':
            logger.warning("Isolation Forest doesn't provide feature importance")
            return None
        
        importance = self.model.feature_importances_
        
        if feature_names is not None:
            self.feature_names = feature_names
            return dict(zip(feature_names, importance))
        
        return importance
    
    def save_model(self, filepath):
        """Save model to file"""
        
        if not self.trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'metrics': self.metrics,
            'trained_date': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load model from file"""
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.feature_names = model_data.get('feature_names')
        self.metrics = model_data.get('metrics', {})
        self.trained = True
        
        logger.info(f"Model loaded from {filepath}")
        logger.info(f"Model type: {self.model_type}")
        logger.info(f"Trained on: {model_data.get('trained_date', 'unknown')}")
        
        return self


class ModelTrainer:
    """Handles the complete training pipeline"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.models = {}
        
    def train_from_csv(self, csv_file, model_type='random_forest', 
                       test_size=0.2, val_size=0.1):
        """
        Train model from CSV file
        
        Args:
            csv_file: Path to CSV file with features and labels
            model_type: Type of model to train
            test_size: Proportion of data for testing
            val_size: Proportion of training data for validation
        """
        logger.info(f"Loading data from {csv_file}...")
        df = pd.read_csv(csv_file)
        
        # Separate features and labels
        if 'label' not in df.columns:
            raise ValueError("CSV must contain 'label' column")
        
        X = df.drop('label', axis=1)
        y = df['label']
        
        feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size, random_state=42, stratify=y_train
        )
        
        logger.info(f"Training set: {len(X_train)} samples")
        logger.info(f"Validation set: {len(X_val)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        logger.info(f"Features: {len(feature_names)}")
        
        # Train model
        model = ZombieWiFiModel(model_type=model_type)
        model.feature_names = feature_names
        model.train(X_train.values, y_train.values, X_val.values, y_val.values)
        
        # Evaluate on test set
        logger.info("\n=== Test Set Evaluation ===")
        y_pred = model.predict(X_test.values)
        model._calculate_metrics(y_test.values, y_pred, 'test')
        
        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, 
                                   target_names=['Normal', 'Zombie WiFi']))
        
        # Print confusion matrix
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        if model_type in ['random_forest', 'xgboost']:
            print("\nTop 10 Important Features:")
            importance_dict = model.get_feature_importance(feature_names)
            sorted_features = sorted(importance_dict.items(), 
                                   key=lambda x: x[1], reverse=True)
            for feat, imp in sorted_features[:10]:
                print(f"  {feat}: {imp:.4f}")
        
        self.models[model_type] = model
        return model
    
    def train_multiple_models(self, csv_file):
        """Train multiple model types and compare"""
        
        model_types = ['random_forest', 'xgboost', 'isolation_forest']
        results = {}
        
        for model_type in model_types:
            logger.info(f"\n{'='*60}")
            logger.info(f"Training {model_type.upper()} model")
            logger.info(f"{'='*60}")
            
            try:
                model = self.train_from_csv(csv_file, model_type=model_type)
                results[model_type] = model.metrics.get('test', {})
            except Exception as e:
                logger.error(f"Error training {model_type}: {e}")
                results[model_type] = None
        
        # Compare results
        print("\n" + "="*60)
        print("MODEL COMPARISON")
        print("="*60)
        
        comparison_df = pd.DataFrame(results).T
        print(comparison_df)
        
        return results


if __name__ == "__main__":
    print("=== Model Training Module ===\n")
    
    # Example usage
    csv_file = "data/training_data.csv"
    
    if os.path.exists(csv_file):
        print(f"Training model from {csv_file}...")
        
        trainer = ModelTrainer()
        
        # Train single model
        model = trainer.train_from_csv(csv_file, model_type='random_forest')
        
        # Save model
        model.save_model('models/zombie_wifi_detector.pkl')
        print("\nModel saved to models/zombie_wifi_detector.pkl")
        
        # Optional: Train and compare multiple models
        # trainer.train_multiple_models(csv_file)
    else:
        print(f"Training data not found at {csv_file}")
        print("Please run data_collection.py first to generate synthetic data")
