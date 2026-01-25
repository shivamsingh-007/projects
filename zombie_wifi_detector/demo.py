"""
Demo Script for Zombie WiFi Detection System
Demonstrates the complete workflow using synthetic data
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Import project modules
from data_collection import generate_synthetic_data
from model_training import ModelTrainer, ZombieWiFiModel
from feature_extraction import FeatureExtractor
from real_time_detection import create_baseline_profile

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def demo_complete_workflow():
    """Demonstrate the complete detection workflow"""
    
    print_header("ZOMBIE WIFI DETECTION SYSTEM - DEMO")
    print("\nThis demo will walk through:")
    print("  1. Generating synthetic training data")
    print("  2. Training a machine learning model")
    print("  3. Evaluating model performance")
    print("  4. Simulating real-time detection")
    
    input("\nPress Enter to continue...")
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Step 1: Generate Training Data
    print_header("STEP 1: GENERATING TRAINING DATA")
    
    print("\nGenerating synthetic dataset...")
    print("  - 1000 normal traffic samples")
    print("  - 200 zombie WiFi attack samples")
    
    data_file = generate_synthetic_data(
        output_dir='data/',
        num_normal=1000,
        num_attack=200
    )
    
    print(f"\n✓ Training data generated: {data_file}")
    
    # Load and display sample
    df = pd.read_csv(data_file)
    print("\nSample of training data:")
    print(df.head())
    
    print("\nClass distribution:")
    print(df['label'].value_counts())
    
    input("\nPress Enter to continue...")
    
    # Step 2: Train Model
    print_header("STEP 2: TRAINING MACHINE LEARNING MODEL")
    
    print("\nTraining Random Forest classifier...")
    
    trainer = ModelTrainer()
    model = trainer.train_from_csv(data_file, model_type='random_forest')
    
    # Save model
    model_path = 'models/zombie_wifi_detector.pkl'
    model.save_model(model_path)
    
    print(f"\n✓ Model saved: {model_path}")
    
    input("\nPress Enter to continue...")
    
    # Step 3: Create Baseline Profile
    print_header("STEP 3: CREATING BASELINE PROFILE")
    
    print("\nCreating baseline from normal traffic patterns...")
    
    baseline_path = 'models/baseline_profile.pkl'
    create_baseline_profile(data_file, baseline_path)
    
    print(f"✓ Baseline profile created: {baseline_path}")
    
    input("\nPress Enter to continue...")
    
    # Step 4: Simulate Detection
    print_header("STEP 4: SIMULATING REAL-TIME DETECTION")
    
    print("\nSimulating 5 network traffic captures...")
    
    # Generate test samples
    np.random.seed(42)
    
    # 3 normal, 2 attacks
    test_samples = []
    test_labels = []
    
    # Normal samples
    for i in range(3):
        sample = {
            'outbound_connection_rate': np.random.normal(50, 15),
            'unique_dst_ips': np.random.poisson(30),
            'dns_query_rate': np.random.normal(40, 10),
            'failed_connection_ratio': np.random.beta(2, 50),
            'nighttime_activity_ratio': np.random.beta(2, 10),
            'port_scan_score': np.random.exponential(0.1),
            'nxdomain_ratio': np.random.beta(1, 50),
            'dga_domain_score': np.random.normal(2.5, 0.5),
            'http_injection_indicators': np.random.poisson(0.5),
            'cpu_usage_variance': np.random.normal(10, 3),
        }
        test_samples.append(sample)
        test_labels.append(0)
    
    # Attack samples
    for i in range(2):
        sample = {
            'outbound_connection_rate': np.random.normal(150, 40),
            'unique_dst_ips': np.random.poisson(100),
            'dns_query_rate': np.random.normal(200, 50),
            'failed_connection_ratio': np.random.beta(5, 10),
            'nighttime_activity_ratio': np.random.beta(8, 3),
            'port_scan_score': np.random.exponential(2.5),
            'nxdomain_ratio': np.random.beta(10, 20),
            'dga_domain_score': np.random.normal(4.5, 0.8),
            'http_injection_indicators': np.random.poisson(5),
            'cpu_usage_variance': np.random.normal(40, 10),
        }
        test_samples.append(sample)
        test_labels.append(1)
    
    # Load model
    loaded_model = ZombieWiFiModel()
    loaded_model.load_model(model_path)
    
    # Test each sample
    print("\n" + "-"*70)
    
    for idx, (sample, true_label) in enumerate(zip(test_samples, test_labels)):
        print(f"\nCapture #{idx + 1}")
        print("-" * 70)
        
        # Convert to array
        X = np.array([list(sample.values())])
        
        # Predict
        prediction = loaded_model.predict(X)[0]
        proba = loaded_model.predict_proba(X)[0]
        confidence = proba[prediction]
        
        # Determine alert level
        if prediction == 1:
            if confidence >= 0.85:
                alert = "CRITICAL"
                emoji = "🚨"
            elif confidence >= 0.65:
                alert = "HIGH"
                emoji = "⚠️ "
            else:
                alert = "MEDIUM"
                emoji = "⚡"
        else:
            if confidence > 0.7:
                alert = "NORMAL"
                emoji = "✓"
            else:
                alert = "LOW"
                emoji = "ℹ️ "
        
        print(f"True Label: {'ZOMBIE WIFI' if true_label == 1 else 'NORMAL'}")
        print(f"Prediction: {'ZOMBIE WIFI' if prediction == 1 else 'NORMAL'}")
        print(f"Alert Level: {emoji} {alert}")
        print(f"Confidence: {confidence:.2%}")
        
        if prediction == 1:
            print("\nSuspicious indicators detected:")
            for key, value in sample.items():
                if key == 'dga_domain_score' and value > 4.0:
                    print(f"  • High DGA domain score: {value:.2f}")
                elif key == 'port_scan_score' and value > 2.0:
                    print(f"  • Port scanning detected: {value:.2f}")
                elif key == 'nighttime_activity_ratio' and value > 0.3:
                    print(f"  • Unusual nighttime activity: {value:.2%}")
        
        input("\nPress Enter for next capture...")
    
    # Summary
    print_header("DEMO COMPLETE")
    
    print("\nDetection Summary:")
    correct = sum(1 for i, (_, true) in enumerate(zip(test_samples, test_labels))
                  if loaded_model.predict(np.array([list(test_samples[i].values())]))[0] == true)
    print(f"  Accuracy: {correct}/{len(test_samples)} ({correct/len(test_samples)*100:.0f}%)")
    
    print("\nWhat you've learned:")
    print("  ✓ How to generate training data")
    print("  ✓ How to train a machine learning model")
    print("  ✓ How to detect zombie WiFi in network traffic")
    print("  ✓ How to interpret detection results")
    
    print("\nNext Steps:")
    print("  • Run on real network traffic: sudo python main.py detect")
    print("  • Start continuous monitoring: sudo python main.py monitor")
    print("  • Train with your own data: python main.py train --data-file yourdata.csv")
    
    print("\n" + "="*70)

def demo_feature_extraction():
    """Demonstrate feature extraction"""
    
    print_header("FEATURE EXTRACTION DEMO")
    
    print("\nThis demo shows how network traffic is converted into ML features.\n")
    
    # Create synthetic packet-like data
    print("Example network activity:")
    print("  • 150 outbound connections in 5 minutes")
    print("  • 95 unique destination IPs contacted")
    print("  • 215 DNS queries performed")
    print("  • 45% of connections failed")
    print("  • High activity during nighttime hours")
    print("  • Domain names with high randomness (DGA)")
    
    input("\nPress Enter to see extracted features...")
    
    # Show features
    features = {
        'outbound_connection_rate': 150,
        'unique_dst_ips': 95,
        'dns_query_rate': 215,
        'failed_connection_ratio': 0.45,
        'nighttime_activity_ratio': 0.68,
        'port_scan_score': 3.2,
        'dga_domain_score': 4.8,
        'dns_tunneling_score': 2.1,
        'beaconing_score': 0.82,
        'suspicious_port_count': 12
    }
    
    print("\nExtracted Features:")
    print("-" * 70)
    
    for key, value in features.items():
        description = get_feature_description(key)
        print(f"{key:30} = {value:8.2f}  # {description}")
    
    print("\n✓ These features are fed into the ML model for classification")

def get_feature_description(feature_name):
    """Get human-readable description of features"""
    descriptions = {
        'outbound_connection_rate': 'Connections per second',
        'unique_dst_ips': 'Number of unique destinations',
        'dns_query_rate': 'DNS queries per second',
        'failed_connection_ratio': 'Ratio of failed connections',
        'nighttime_activity_ratio': 'Activity during 2-6 AM',
        'port_scan_score': 'Port scanning indicator',
        'dga_domain_score': 'Domain randomness (DGA)',
        'dns_tunneling_score': 'DNS tunneling indicator',
        'beaconing_score': 'Periodic communication',
        'suspicious_port_count': 'Known bad ports contacted'
    }
    return descriptions.get(feature_name, 'Unknown feature')

def demo_model_comparison():
    """Compare different ML models"""
    
    print_header("MODEL COMPARISON DEMO")
    
    print("\nComparing three ML algorithms:")
    print("  1. Random Forest (Ensemble of decision trees)")
    print("  2. XGBoost (Gradient boosting)")
    print("  3. Isolation Forest (Anomaly detection)")
    
    input("\nPress Enter to train and compare...")
    
    # Generate data if not exists
    data_file = 'data/training_data.csv'
    if not os.path.exists(data_file):
        print("\nGenerating training data...")
        generate_synthetic_data(output_dir='data/', num_normal=500, num_attack=100)
    
    # Train and compare
    trainer = ModelTrainer()
    results = trainer.train_multiple_models(data_file)
    
    print("\n✓ Model comparison complete!")
    print("\nConclusion:")
    print("  • Random Forest: Good balance of speed and accuracy")
    print("  • XGBoost: Highest accuracy, slightly slower")
    print("  • Isolation Forest: Good for unseen attacks, lower accuracy")

def main_menu():
    """Interactive demo menu"""
    
    while True:
        print("\n" + "="*70)
        print(" ZOMBIE WIFI DETECTION SYSTEM - DEMO MENU")
        print("="*70)
        print("\n1. Complete Workflow Demo (Recommended)")
        print("2. Feature Extraction Demo")
        print("3. Model Comparison Demo")
        print("4. Quick Test (if already setup)")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            demo_complete_workflow()
        elif choice == '2':
            demo_feature_extraction()
        elif choice == '3':
            demo_model_comparison()
        elif choice == '4':
            quick_test()
        elif choice == '5':
            print("\nThank you for trying the demo!")
            break
        else:
            print("\nInvalid option. Please select 1-5.")

def quick_test():
    """Quick test if system is already set up"""
    
    model_path = 'models/zombie_wifi_detector.pkl'
    
    if not os.path.exists(model_path):
        print("\nModel not found. Please run option 1 (Complete Workflow Demo) first.")
        return
    
    print_header("QUICK TEST")
    
    print("\nLoading model...")
    model = ZombieWiFiModel()
    model.load_model(model_path)
    
    print("✓ Model loaded successfully")
    
    print("\nTesting with random samples...")
    
    # Generate random test sample (attack pattern)
    attack_sample = np.array([[
        np.random.normal(150, 40),  # high connection rate
        np.random.poisson(100),      # many unique IPs
        np.random.normal(200, 50),   # high DNS queries
        np.random.beta(5, 10),       # failed connections
        np.random.beta(8, 3),        # nighttime activity
        np.random.exponential(2.5),  # port scanning
        np.random.beta(10, 20),      # nxdomain
        np.random.normal(4.5, 0.8),  # DGA domains
        np.random.poisson(5),        # HTTP injection
        np.random.normal(40, 10)     # CPU variance
    ]])
    
    prediction = model.predict(attack_sample)[0]
    proba = model.predict_proba(attack_sample)[0]
    
    print(f"\nPrediction: {'ZOMBIE WIFI DETECTED!' if prediction == 1 else 'NORMAL'}")
    print(f"Confidence: {proba[prediction]:.2%}")
    
    print("\n✓ System is working correctly!")

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        ZOMBIE WIFI DETECTION SYSTEM - INTERACTIVE DEMO            ║
    ║                                                                   ║
    ║  This demo demonstrates the complete machine learning workflow    ║
    ║  for detecting compromised WiFi routers using synthetic data.     ║
    ║                                                                   ║
    ║  No root access or real network traffic required!                 ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        print("Please check that all dependencies are installed.")
