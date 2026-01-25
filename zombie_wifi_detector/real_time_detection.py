"""
Real-time Detection System
Monitors network traffic and detects zombie WiFi in real-time
"""

import time
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from collections import deque
import os
import yaml

from data_collection import PacketCapture
from feature_extraction import FeatureExtractor
from model_training import ZombieWiFiModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Alert:
    """Alert levels for detection"""
    NORMAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    @staticmethod
    def get_name(level):
        names = {0: "NORMAL", 1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
        return names.get(level, "UNKNOWN")


class DetectionResult:
    """Container for detection results"""
    
    def __init__(self, alert_level, confidence, features, timestamp):
        self.alert_level = alert_level
        self.confidence = confidence
        self.features = features
        self.timestamp = timestamp
        self.alert_name = Alert.get_name(alert_level)
    
    def __str__(self):
        return (f"[{self.timestamp}] Alert: {self.alert_name} "
                f"(Confidence: {self.confidence:.2%})")
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'alert_level': self.alert_level,
            'alert_name': self.alert_name,
            'confidence': self.confidence,
            'features': self.features
        }


class RealTimeDetector:
    """Real-time zombie WiFi detection system"""
    
    def __init__(self, model_path, config_path='config.yaml', interface='eth0'):
        """
        Initialize detector
        
        Args:
            model_path: Path to trained model file
            config_path: Path to configuration file
            interface: Network interface to monitor
        """
        self.interface = interface
        self.model = None
        self.feature_extractor = FeatureExtractor()
        self.config = self._load_config(config_path)
        self.baseline_profile = None
        self.detection_history = deque(maxlen=100)
        
        # Load model
        self._load_model(model_path)
        
        # Thresholds from config
        self.threshold_high = self.config['thresholds']['high_confidence']
        self.threshold_medium = self.config['thresholds']['medium_confidence']
        self.anomaly_threshold = self.config['thresholds']['anomaly_score']
        
        # Capture settings
        self.capture_duration = self.config['data_collection']['capture_duration']
        
        logger.info("Real-time detector initialized")
        logger.info(f"Monitoring interface: {self.interface}")
        logger.info(f"Model type: {self.model.model_type}")
    
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._default_config()
    
    def _default_config(self):
        """Return default configuration"""
        return {
            'data_collection': {'capture_duration': 300},
            'thresholds': {
                'high_confidence': 0.85,
                'medium_confidence': 0.65,
                'anomaly_score': 2.5
            }
        }
    
    def _load_model(self, model_path):
        """Load trained model"""
        logger.info(f"Loading model from {model_path}...")
        self.model = ZombieWiFiModel()
        self.model.load_model(model_path)
        logger.info("Model loaded successfully")
    
    def load_baseline_profile(self, baseline_path):
        """Load baseline normal behavior profile"""
        if os.path.exists(baseline_path):
            import pickle
            with open(baseline_path, 'rb') as f:
                self.baseline_profile = pickle.load(f)
            logger.info(f"Baseline profile loaded from {baseline_path}")
        else:
            logger.warning(f"Baseline profile not found: {baseline_path}")
    
    def capture_and_analyze(self, duration=None):
        """
        Capture traffic and analyze for zombie WiFi
        
        Args:
            duration: Capture duration in seconds (uses config default if None)
            
        Returns:
            DetectionResult object
        """
        duration = duration or self.capture_duration
        
        logger.info(f"Capturing traffic for {duration} seconds...")
        
        # Capture packets
        capture = PacketCapture(interface=self.interface, duration=duration)
        packets = capture.capture_packets(timeout=duration)
        
        if not packets:
            logger.warning("No packets captured")
            return DetectionResult(
                alert_level=Alert.NORMAL,
                confidence=0.0,
                features={},
                timestamp=datetime.now().isoformat()
            )
        
        # Extract features
        logger.info("Extracting features...")
        features = self.feature_extractor.extract_all_features(packets, duration)
        
        # Make prediction
        result = self.detect_zombie_wifi(features)
        
        # Store in history
        self.detection_history.append(result)
        
        return result
    
    def detect_zombie_wifi(self, features):
        """
        Detect zombie WiFi from features
        
        Args:
            features: Dictionary of extracted features
            
        Returns:
            DetectionResult object
        """
        # Convert features to array
        feature_array = np.array([list(features.values())])
        
        # Get prediction
        prediction = self.model.predict(feature_array)[0]
        
        # Get confidence score
        if self.model.model_type != 'isolation_forest':
            proba = self.model.predict_proba(feature_array)[0]
            confidence = proba[1]  # Probability of being zombie WiFi
        else:
            # For isolation forest, use decision function
            score = self.model.model.decision_function(
                self.model.scaler.transform(feature_array)
            )[0]
            # Convert to confidence (lower score = more anomalous)
            confidence = 1 / (1 + np.exp(score))  # Sigmoid transformation
        
        # Determine alert level
        if prediction == 1:  # Zombie WiFi detected
            if confidence >= self.threshold_high:
                alert_level = Alert.CRITICAL
            elif confidence >= self.threshold_medium:
                alert_level = Alert.HIGH
            else:
                alert_level = Alert.MEDIUM
        else:  # Normal traffic
            if confidence > 0.5:  # Some suspicion
                alert_level = Alert.LOW
            else:
                alert_level = Alert.NORMAL
        
        # Compare with baseline if available
        if self.baseline_profile is not None:
            deviation_score = self._calculate_baseline_deviation(features)
            if deviation_score > self.anomaly_threshold:
                alert_level = max(alert_level, Alert.MEDIUM)
                logger.warning(f"Baseline deviation detected: {deviation_score:.2f}")
        
        # Create result
        result = DetectionResult(
            alert_level=alert_level,
            confidence=confidence,
            features=features,
            timestamp=datetime.now().isoformat()
        )
        
        # Log result
        self._log_detection(result)
        
        return result
    
    def _calculate_baseline_deviation(self, features):
        """Calculate deviation from baseline normal behavior"""
        if self.baseline_profile is None:
            return 0.0
        
        # Calculate Mahalanobis distance or simple Z-score
        deviations = []
        for key, value in features.items():
            if key in self.baseline_profile:
                baseline_mean = self.baseline_profile[key]['mean']
                baseline_std = self.baseline_profile[key]['std']
                
                if baseline_std > 0:
                    z_score = abs((value - baseline_mean) / baseline_std)
                    deviations.append(z_score)
        
        if deviations:
            return np.mean(deviations)
        return 0.0
    
    def _log_detection(self, result):
        """Log detection result"""
        log_msg = str(result)
        
        if result.alert_level >= Alert.HIGH:
            logger.warning(log_msg)
        elif result.alert_level >= Alert.MEDIUM:
            logger.info(log_msg)
        else:
            logger.debug(log_msg)
        
        # Write to file if configured
        if self.config.get('alerts', {}).get('enable_logging', False):
            log_file = self.config['alerts'].get('log_file', 'logs/detections.log')
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            with open(log_file, 'a') as f:
                f.write(f"{log_msg}\n")
    
    def monitor_continuous(self, interval=None):
        """
        Continuously monitor network traffic
        
        Args:
            interval: Time between captures in seconds (uses config default if None)
        """
        interval = interval or self.capture_duration
        
        logger.info("Starting continuous monitoring...")
        logger.info(f"Capture interval: {interval} seconds")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                result = self.capture_and_analyze(duration=interval)
                
                # Print alert
                print(f"\n{result}")
                
                if result.alert_level >= Alert.HIGH:
                    print("⚠️  ZOMBIE WIFI DETECTED! ⚠️")
                    print(f"Confidence: {result.confidence:.2%}")
                    print("\nTop suspicious features:")
                    self._print_suspicious_features(result.features)
                
                # Brief pause before next capture
                time.sleep(2)
                
        except KeyboardInterrupt:
            logger.info("\nMonitoring stopped by user")
            self.print_summary()
    
    def _print_suspicious_features(self, features, top_n=5):
        """Print most suspicious feature values"""
        # Define thresholds for suspicious values
        suspicious_thresholds = {
            'dga_domain_score': 4.0,
            'port_scan_score': 2.0,
            'nighttime_activity_ratio': 0.3,
            'dns_tunneling_score': 3.0,
            'beaconing_score': 0.7,
            'failed_connection_ratio': 0.2
        }
        
        suspicious_features = []
        for key, value in features.items():
            if key in suspicious_thresholds:
                if value > suspicious_thresholds[key]:
                    suspicious_features.append((key, value))
        
        # Sort by value
        suspicious_features.sort(key=lambda x: x[1], reverse=True)
        
        for key, value in suspicious_features[:top_n]:
            print(f"  • {key}: {value:.2f}")
    
    def print_summary(self):
        """Print summary of detection history"""
        if not self.detection_history:
            print("\nNo detections in history")
            return
        
        print("\n" + "="*60)
        print("DETECTION SUMMARY")
        print("="*60)
        
        alert_counts = {
            Alert.NORMAL: 0,
            Alert.LOW: 0,
            Alert.MEDIUM: 0,
            Alert.HIGH: 0,
            Alert.CRITICAL: 0
        }
        
        for result in self.detection_history:
            alert_counts[result.alert_level] += 1
        
        total = len(self.detection_history)
        print(f"Total checks: {total}")
        print(f"\nAlert distribution:")
        for level, count in alert_counts.items():
            percentage = (count / total) * 100
            print(f"  {Alert.get_name(level)}: {count} ({percentage:.1f}%)")
        
        # Calculate detection rate
        threats = alert_counts[Alert.HIGH] + alert_counts[Alert.CRITICAL]
        if threats > 0:
            print(f"\n⚠️  Zombie WiFi detected in {threats} checks!")
        else:
            print(f"\n✓ No zombie WiFi detected")


def create_baseline_profile(data_file, output_file='models/baseline_profile.pkl'):
    """
    Create baseline profile from normal traffic data
    
    Args:
        data_file: CSV file with normal traffic features
        output_file: Where to save baseline profile
    """
    import pickle
    
    logger.info(f"Creating baseline profile from {data_file}...")
    
    df = pd.read_csv(data_file)
    
    # Remove label column if present
    if 'label' in df.columns:
        df = df[df['label'] == 0]  # Only normal traffic
        df = df.drop('label', axis=1)
    
    # Calculate statistics for each feature
    baseline = {}
    for col in df.columns:
        baseline[col] = {
            'mean': df[col].mean(),
            'std': df[col].std(),
            'min': df[col].min(),
            'max': df[col].max(),
            'median': df[col].median()
        }
    
    # Save baseline
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'wb') as f:
        pickle.dump(baseline, f)
    
    logger.info(f"Baseline profile saved to {output_file}")
    return baseline


if __name__ == "__main__":
    import sys
    
    print("=== Real-time Zombie WiFi Detection System ===\n")
    
    model_path = "models/zombie_wifi_detector.pkl"
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        print("Please run model_training.py first to train a model")
        sys.exit(1)
    
    # Initialize detector
    try:
        detector = RealTimeDetector(
            model_path=model_path,
            interface='eth0'  # Change to your network interface
        )
        
        print("Detection system ready!")
        print("\nOptions:")
        print("1. Single capture and analysis")
        print("2. Continuous monitoring")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            result = detector.capture_and_analyze()
            print(f"\n{result}")
            
            if result.alert_level >= Alert.HIGH:
                print("\n⚠️  ZOMBIE WIFI DETECTED! ⚠️")
                detector._print_suspicious_features(result.features)
            else:
                print("\n✓ Network appears normal")
        
        elif choice == '2':
            detector.monitor_continuous()
        
        else:
            print("Exiting...")
    
    except PermissionError:
        print("\nError: Packet capture requires root/admin privileges")
        print("Please run with sudo: sudo python real_time_detection.py")
    except Exception as e:
        print(f"\nError: {e}")
        logger.exception("Exception in main")
