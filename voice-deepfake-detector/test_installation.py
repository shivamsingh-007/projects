#!/usr/bin/env python3
"""
Quick test script to verify Voice Deepfake Detector installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask installed")
    except ImportError:
        print("✗ Flask not installed")
        return False
    
    try:
        import tensorflow
        print("✓ TensorFlow installed")
    except ImportError:
        print("✗ TensorFlow not installed")
        return False
    
    try:
        import librosa
        print("✓ Librosa installed")
    except ImportError:
        print("✗ Librosa not installed")
        return False
    
    try:
        import numpy
        print("✓ NumPy installed")
    except ImportError:
        print("✗ NumPy not installed")
        return False
    
    return True

def test_model():
    """Test if model can be initialized"""
    print("\nTesting model initialization...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from model import DeepfakeDetector
        
        detector = DeepfakeDetector()
        print("✓ Model initialized successfully")
        
        if detector.is_loaded():
            print("✓ Model loaded successfully")
        else:
            print("✗ Model not loaded")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Model initialization failed: {str(e)}")
        return False

def test_preprocessor():
    """Test if audio preprocessor works"""
    print("\nTesting audio preprocessor...")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from preprocessing import AudioPreprocessor
        
        preprocessor = AudioPreprocessor()
        print("✓ Preprocessor initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Preprocessor initialization failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Voice Deepfake Detector - Installation Test")
    print("=" * 50)
    print()
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
        print("\n⚠️  Some dependencies are missing. Please run: pip install -r backend/requirements.txt")
    
    # Test model
    if not test_model():
        all_passed = False
    
    # Test preprocessor
    if not test_preprocessor():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! Installation successful.")
        print("\nYou can now run the application with:")
        print("  ./start.sh (Linux/Mac)")
        print("  start.bat (Windows)")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
