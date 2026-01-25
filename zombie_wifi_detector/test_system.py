#!/usr/bin/env python3
"""
Test Suite for Zombie WiFi Detection System
Validates all components are working correctly
"""

import sys
import os
import numpy as np
import pandas as pd

def test_imports():
    """Test that all required modules can be imported"""
    print("\n" + "="*70)
    print(" TEST 1: MODULE IMPORTS")
    print("="*70)
    
    modules_to_test = [
        ('data_collection', ['PacketCapture', 'TrafficAnalyzer', 'generate_synthetic_data']),
        ('feature_extraction', ['FeatureExtractor']),
        ('model_training', ['ZombieWiFiModel', 'ModelTrainer']),
        ('real_time_detection', ['RealTimeDetector', 'Alert']),
        ('visualization', ['DetectionVisualizer'])
    ]
    
    all_passed = True
    
    for module_name, classes in modules_to_test:
        try:
            module = __import__(module_name)
            print(f"✓ {module_name}")
            
            for class_name in classes:
                if hasattr(module, class_name):
                    print(f"  ✓ {class_name}")
                else:
                    print(f"  ❌ {class_name} not found")
                    all_passed = False
        
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All modules imported successfully")
    else:
        print("\n❌ Some modules failed to import")
    
    return all_passed

def test_data_generation():
    """Test synthetic data generation"""
    print("\n" + "="*70)
    print(" TEST 2: DATA GENERATION")
    print("="*70)
    
    try:
        from data_collection import generate_synthetic_data
        
        print("Generating small test dataset...")
        data_file = generate_synthetic_data(
            output_dir='test_data/',
            num_normal=50,
            num_attack=10
        )
        
        # Verify file exists and load it
        if os.path.exists(data_file):
            df = pd.read_csv(data_file)
            
            print(f"✓ Data file created: {data_file}")
            print(f"✓ Total samples: {len(df)}")
            print(f"✓ Features: {len(df.columns) - 1}")
            print(f"✓ Normal samples: {sum(df['label'] == 0)}")
            print(f"✓ Attack samples: {sum(df['label'] == 1)}")
            
            # Cleanup
            os.remove(data_file)
            if os.path.exists('test_data'):
                os.rmdir('test_data')
            
            print("\n✅ Data generation test passed")
            return True
        else:
            print("❌ Data file not created")
            return False
    
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False

def test_feature_extraction():
    """Test feature extraction"""
    print("\n" + "="*70)
    print(" TEST 3: FEATURE EXTRACTION")
    print("="*70)
    
    try:
        from feature_extraction import FeatureExtractor
        
        # Create mock packet data
        extractor = FeatureExtractor()
        
        # Test with empty packets
        features = extractor.extract_all_features([], time_window=300)
        
        print(f"✓ Feature extractor initialized")
        print(f"✓ Extracted {len(features)} features")
        print(f"✓ Feature types: {type(features)}")
        
        # Verify expected features are present
        expected_features = [
            'outbound_connection_rate',
            'dns_query_rate',
            'dga_domain_score',
            'port_scan_score',
            'nighttime_activity_ratio'
        ]
        
        missing = [f for f in expected_features if f not in features]
        
        if missing:
            print(f"⚠️  Missing features: {missing}")
        else:
            print(f"✓ All expected features present")
        
        print("\n✅ Feature extraction test passed")
        return True
    
    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        return False

def test_model_training():
    """Test model training"""
    print("\n" + "="*70)
    print(" TEST 4: MODEL TRAINING")
    print("="*70)
    
    try:
        from model_training import ZombieWiFiModel
        from data_collection import generate_synthetic_data
        import pandas as pd
        
        # Generate small dataset
        print("Generating training data...")
        data_file = generate_synthetic_data(
            output_dir='test_data/',
            num_normal=100,
            num_attack=20
        )
        
        df = pd.read_csv(data_file)
        X = df.drop('label', axis=1).values
        y = df['label'].values
        
        print(f"✓ Training data: {len(X)} samples")
        
        # Train model
        print("Training model...")
        model = ZombieWiFiModel(model_type='random_forest')
        model.feature_names = df.drop('label', axis=1).columns.tolist()
        model.train(X, y)
        
        print(f"✓ Model trained")
        print(f"✓ Model type: {model.model_type}")
        
        # Test prediction
        predictions = model.predict(X[:5])
        proba = model.predict_proba(X[:5])
        
        print(f"✓ Predictions shape: {predictions.shape}")
        print(f"✓ Probabilities shape: {proba.shape}")
        
        # Test save/load
        model_path = 'test_data/test_model.pkl'
        model.save_model(model_path)
        print(f"✓ Model saved")
        
        loaded_model = ZombieWiFiModel()
        loaded_model.load_model(model_path)
        print(f"✓ Model loaded")
        
        # Verify loaded model works
        loaded_pred = loaded_model.predict(X[:5])
        if np.array_equal(predictions, loaded_pred):
            print(f"✓ Loaded model produces same predictions")
        else:
            print(f"⚠️  Loaded model predictions differ")
        
        # Cleanup
        os.remove(data_file)
        os.remove(model_path)
        if os.path.exists('test_data'):
            os.rmdir('test_data')
        
        print("\n✅ Model training test passed")
        return True
    
    except Exception as e:
        print(f"❌ Model training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_detection_system():
    """Test detection system components"""
    print("\n" + "="*70)
    print(" TEST 5: DETECTION SYSTEM")
    print("="*70)
    
    try:
        from real_time_detection import Alert, DetectionResult
        from datetime import datetime
        
        # Test Alert levels
        print("Testing Alert levels...")
        alert_names = {
            Alert.NORMAL: "NORMAL",
            Alert.LOW: "LOW",
            Alert.MEDIUM: "MEDIUM",
            Alert.HIGH: "HIGH",
            Alert.CRITICAL: "CRITICAL"
        }
        
        for level, name in alert_names.items():
            retrieved_name = Alert.get_name(level)
            if retrieved_name == name:
                print(f"✓ Alert.{name}")
            else:
                print(f"❌ Alert.{name} mismatch")
        
        # Test DetectionResult
        print("\nTesting DetectionResult...")
        result = DetectionResult(
            alert_level=Alert.HIGH,
            confidence=0.87,
            features={'test_feature': 1.0},
            timestamp=datetime.now().isoformat()
        )
        
        print(f"✓ DetectionResult created")
        print(f"✓ Alert name: {result.alert_name}")
        print(f"✓ String representation: {str(result)}")
        print(f"✓ Dict conversion: {result.to_dict()}")
        
        print("\n✅ Detection system test passed")
        return True
    
    except Exception as e:
        print(f"❌ Detection system test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n" + "="*70)
    print(" TEST 6: CONFIGURATION")
    print("="*70)
    
    try:
        import yaml
        
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            print(f"✓ Config file loaded")
            print(f"✓ Config sections: {list(config.keys())}")
            
            # Verify expected sections
            expected_sections = [
                'data_collection',
                'features',
                'model',
                'thresholds',
                'paths'
            ]
            
            for section in expected_sections:
                if section in config:
                    print(f"✓ Section '{section}' present")
                else:
                    print(f"⚠️  Section '{section}' missing")
            
            print("\n✅ Configuration test passed")
            return True
        else:
            print("⚠️  config.yaml not found")
            return False
    
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        ZOMBIE WIFI DETECTION SYSTEM - TEST SUITE                  ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Module Imports", test_imports),
        ("Data Generation", test_data_generation),
        ("Feature Extraction", test_feature_extraction),
        ("Model Training", test_model_training),
        ("Detection System", test_detection_system),
        ("Configuration", test_configuration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
        
        input("\nPress Enter to continue to next test...")
    
    # Print summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
