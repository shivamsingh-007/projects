"""
Main Entry Point for Zombie WiFi Detection System
Provides a unified interface for all operations
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Import project modules
from data_collection import generate_synthetic_data, PacketCapture, TrafficAnalyzer
from feature_extraction import FeatureExtractor
from model_training import ModelTrainer, ZombieWiFiModel
from real_time_detection import RealTimeDetector, create_baseline_profile

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZombieWiFiDetectionSystem:
    """Main system orchestrator"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.project_root, 'data')
        self.model_dir = os.path.join(self.project_root, 'models')
        self.logs_dir = os.path.join(self.project_root, 'logs')
        
        # Create directories
        for directory in [self.data_dir, self.model_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def setup(self):
        """Initial setup - generate training data and train model"""
        print("\n" + "="*70)
        print(" ZOMBIE WIFI DETECTION SYSTEM - SETUP")
        print("="*70)
        
        # Step 1: Generate synthetic training data
        print("\n[1/3] Generating synthetic training data...")
        data_file = os.path.join(self.data_dir, 'training_data.csv')
        
        if os.path.exists(data_file):
            overwrite = input(f"  Training data exists at {data_file}. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                print("  Using existing training data")
            else:
                data_file = generate_synthetic_data(
                    output_dir=self.data_dir,
                    num_normal=1000,
                    num_attack=200
                )
        else:
            data_file = generate_synthetic_data(
                output_dir=self.data_dir,
                num_normal=1000,
                num_attack=200
            )
        
        print(f"  ✓ Training data ready: {data_file}")
        
        # Step 2: Train model
        print("\n[2/3] Training machine learning model...")
        trainer = ModelTrainer()
        
        model_type = input("  Select model type (random_forest/xgboost/isolation_forest) [random_forest]: ").strip()
        if not model_type:
            model_type = 'random_forest'
        
        try:
            model = trainer.train_from_csv(data_file, model_type=model_type)
            
            # Save model
            model_path = os.path.join(self.model_dir, 'zombie_wifi_detector.pkl')
            model.save_model(model_path)
            print(f"  ✓ Model saved: {model_path}")
            
        except Exception as e:
            print(f"  ✗ Error training model: {e}")
            return False
        
        # Step 3: Create baseline profile
        print("\n[3/3] Creating baseline profile...")
        try:
            baseline_path = os.path.join(self.model_dir, 'baseline_profile.pkl')
            create_baseline_profile(data_file, baseline_path)
            print(f"  ✓ Baseline profile saved: {baseline_path}")
        except Exception as e:
            print(f"  ✗ Error creating baseline: {e}")
        
        print("\n" + "="*70)
        print(" SETUP COMPLETE!")
        print("="*70)
        print("\nYou can now run detection with: python main.py detect")
        
        return True
    
    def train_model(self, data_file=None, model_type='random_forest'):
        """Train or retrain model"""
        print("\n" + "="*70)
        print(" TRAINING MODEL")
        print("="*70)
        
        if data_file is None:
            data_file = os.path.join(self.data_dir, 'training_data.csv')
        
        if not os.path.exists(data_file):
            print(f"\nError: Training data not found at {data_file}")
            print("Run 'python main.py setup' first")
            return False
        
        trainer = ModelTrainer()
        
        try:
            print(f"\nTraining {model_type} model...")
            model = trainer.train_from_csv(data_file, model_type=model_type)
            
            # Save model
            model_path = os.path.join(self.model_dir, 'zombie_wifi_detector.pkl')
            model.save_model(model_path)
            
            print(f"\n✓ Model trained and saved: {model_path}")
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            logger.exception("Training error")
            return False
    
    def compare_models(self, data_file=None):
        """Train and compare multiple model types"""
        print("\n" + "="*70)
        print(" COMPARING MODELS")
        print("="*70)
        
        if data_file is None:
            data_file = os.path.join(self.data_dir, 'training_data.csv')
        
        if not os.path.exists(data_file):
            print(f"\nError: Training data not found at {data_file}")
            return False
        
        trainer = ModelTrainer()
        
        try:
            results = trainer.train_multiple_models(data_file)
            return True
        except Exception as e:
            print(f"\n✗ Error: {e}")
            return False
    
    def detect_once(self, interface='eth0', duration=60):
        """Run detection once on current traffic"""
        print("\n" + "="*70)
        print(" ZOMBIE WIFI DETECTION - SINGLE SCAN")
        print("="*70)
        
        model_path = os.path.join(self.model_dir, 'zombie_wifi_detector.pkl')
        
        if not os.path.exists(model_path):
            print(f"\nError: Model not found at {model_path}")
            print("Run 'python main.py setup' first")
            return
        
        try:
            print(f"\nInitializing detector...")
            print(f"Interface: {interface}")
            print(f"Capture duration: {duration} seconds")
            
            detector = RealTimeDetector(
                model_path=model_path,
                interface=interface
            )
            
            # Load baseline if available
            baseline_path = os.path.join(self.model_dir, 'baseline_profile.pkl')
            if os.path.exists(baseline_path):
                detector.load_baseline_profile(baseline_path)
            
            print("\nStarting capture...")
            result = detector.capture_and_analyze(duration=duration)
            
            print("\n" + "-"*70)
            print(f"RESULT: {result}")
            print("-"*70)
            
            if result.alert_level >= 3:  # HIGH or CRITICAL
                print("\n⚠️  ZOMBIE WIFI DETECTED! ⚠️")
                print(f"\nConfidence: {result.confidence:.2%}")
                print("\nSuspicious Features:")
                detector._print_suspicious_features(result.features, top_n=10)
                print("\nRECOMMENDATIONS:")
                print("  • Disconnect from this network immediately")
                print("  • Change your router password")
                print("  • Update router firmware")
                print("  • Scan for malware on connected devices")
            else:
                print("\n✓ Network appears normal")
                print(f"Confidence: {(1-result.confidence):.2%}")
            
        except PermissionError:
            print("\n✗ Error: Packet capture requires root/admin privileges")
            print("Please run with sudo: sudo python main.py detect")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            logger.exception("Detection error")
    
    def monitor_continuous(self, interface='eth0', interval=300):
        """Continuously monitor network traffic"""
        print("\n" + "="*70)
        print(" ZOMBIE WIFI DETECTION - CONTINUOUS MONITORING")
        print("="*70)
        
        model_path = os.path.join(self.model_dir, 'zombie_wifi_detector.pkl')
        
        if not os.path.exists(model_path):
            print(f"\nError: Model not found at {model_path}")
            print("Run 'python main.py setup' first")
            return
        
        try:
            detector = RealTimeDetector(
                model_path=model_path,
                interface=interface
            )
            
            # Load baseline if available
            baseline_path = os.path.join(self.model_dir, 'baseline_profile.pkl')
            if os.path.exists(baseline_path):
                detector.load_baseline_profile(baseline_path)
            
            detector.monitor_continuous(interval=interval)
            
        except PermissionError:
            print("\n✗ Error: Packet capture requires root/admin privileges")
            print("Please run with sudo: sudo python main.py monitor")
        except Exception as e:
            print(f"\n✗ Error: {e}")
            logger.exception("Monitoring error")
    
    def analyze_pcap(self, pcap_file):
        """Analyze a saved PCAP file"""
        print("\n" + "="*70)
        print(" ANALYZING PCAP FILE")
        print("="*70)
        
        if not os.path.exists(pcap_file):
            print(f"\nError: File not found: {pcap_file}")
            return
        
        print(f"\nLoading packets from {pcap_file}...")
        
        # Load packets
        from scapy.all import rdpcap
        packets = rdpcap(pcap_file)
        
        print(f"Loaded {len(packets)} packets")
        
        # Basic analysis
        print("\n--- Traffic Summary ---")
        analyzer = TrafficAnalyzer(packets)
        analyzer.print_summary()
        
        # ML detection
        model_path = os.path.join(self.model_dir, 'zombie_wifi_detector.pkl')
        
        if os.path.exists(model_path):
            print("\n--- ML Detection ---")
            
            # Extract features
            extractor = FeatureExtractor()
            features = extractor.extract_all_features(packets)
            
            # Load model and predict
            model = ZombieWiFiModel()
            model.load_model(model_path)
            
            import numpy as np
            feature_array = np.array([list(features.values())])
            prediction = model.predict(feature_array)[0]
            proba = model.predict_proba(feature_array)[0]
            
            print(f"\nPrediction: {'ZOMBIE WIFI' if prediction == 1 else 'NORMAL'}")
            print(f"Confidence: {proba[prediction]:.2%}")
        else:
            print("\nNote: Model not found, skipping ML detection")


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description='Zombie WiFi Detection System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py setup                    # Initial setup
  python main.py train                    # Train model
  python main.py detect                   # Run single detection
  python main.py monitor                  # Continuous monitoring
  python main.py analyze capture.pcap     # Analyze PCAP file
        """
    )
    
    parser.add_argument(
        'command',
        choices=['setup', 'train', 'compare', 'detect', 'monitor', 'analyze'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='File path (for analyze command)'
    )
    
    parser.add_argument(
        '--interface', '-i',
        default='eth0',
        help='Network interface to monitor (default: eth0)'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=int,
        default=60,
        help='Capture duration in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--model-type', '-m',
        choices=['random_forest', 'xgboost', 'isolation_forest'],
        default='random_forest',
        help='Model type for training (default: random_forest)'
    )
    
    parser.add_argument(
        '--data-file',
        help='Custom training data file'
    )
    
    args = parser.parse_args()
    
    # Initialize system
    system = ZombieWiFiDetectionSystem()
    
    # Execute command
    if args.command == 'setup':
        system.setup()
    
    elif args.command == 'train':
        system.train_model(
            data_file=args.data_file,
            model_type=args.model_type
        )
    
    elif args.command == 'compare':
        system.compare_models(data_file=args.data_file)
    
    elif args.command == 'detect':
        system.detect_once(
            interface=args.interface,
            duration=args.duration
        )
    
    elif args.command == 'monitor':
        system.monitor_continuous(
            interface=args.interface,
            interval=args.duration
        )
    
    elif args.command == 'analyze':
        if not args.file:
            print("Error: Please specify a PCAP file to analyze")
            sys.exit(1)
        system.analyze_pcap(args.file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.exception("Fatal error in main")
        sys.exit(1)
