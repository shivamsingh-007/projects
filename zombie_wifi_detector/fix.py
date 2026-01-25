#!/usr/bin/env python3
"""
Quick Fix Script for Zombie WiFi Detector
Fixes common path and file issues
"""

import os
import sys

def fix_paths():
    """Fix file paths and remove duplicates"""
    
    print("="*70)
    print(" FIXING FILE PATHS AND STRUCTURE")
    print("="*70)
    
    fixes_applied = []
    
    # 1. Remove old index.html from root if exists
    if os.path.exists('index.html'):
        os.remove('index.html')
        fixes_applied.append("Removed old index.html from root")
    
    # 2. Remove duplicate CSS/JS from frontend folder
    old_files = [
        'frontend/app.js',
        'frontend/styles.css'
    ]
    
    for file in old_files:
        if os.path.exists(file):
            os.remove(file)
            fixes_applied.append(f"Removed duplicate {file}")
    
    # 3. Ensure static directory structure exists
    directories = [
        'static/css',
        'static/js',
        'models',
        'data',
        'logs'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            fixes_applied.append(f"Created {directory}/")
    
    # 4. Check if backend app exists
    if not os.path.exists('backend/app.py'):
        if os.path.exists('backend/app_integrated.py'):
            import shutil
            shutil.copy('backend/app_integrated.py', 'backend/app.py')
            fixes_applied.append("Copied app_integrated.py to app.py")
    
    # Report
    print("\nFixes applied:")
    if fixes_applied:
        for fix in fixes_applied:
            print(f"  [OK] {fix}")
    else:
        print("  No fixes needed - everything looks good!")
    
    print("\n[OK] Path fixes complete!")
    
    # Verify structure
    print("\n" + "="*70)
    print(" VERIFYING STRUCTURE")
    print("="*70)
    
    required_files = [
        ('frontend/index.html', 'Landing page'),
        ('frontend/login.html', 'Login page'),
        ('frontend/register.html', 'Register page'),
        ('frontend/dashboard.html', 'Dashboard'),
        ('static/css/style.css', 'Main stylesheet'),
        ('static/js/landing.js', 'Landing page JS'),
        ('backend/app.py', 'Flask backend'),
    ]
    
    all_good = True
    
    for file, description in required_files:
        if os.path.exists(file):
            print(f"  [OK] {description}: {file}")
        else:
            print(f"  [X] MISSING {description}: {file}")
            all_good = False
    
    if all_good:
        print("\n[OK] All required files present!")
    else:
        print("\n[WARNING] Some files are missing")
        print("You may need to re-download the package")
    
    return all_good

def check_model():
    """Check if model is trained"""
    print("\n" + "="*70)
    print(" CHECKING ML MODEL")
    print("="*70)
    
    model_path = 'models/zombie_wifi_detector.pkl'
    
    if os.path.exists(model_path):
        print(f"\n[OK] Model found: {model_path}")
        return True
    else:
        print(f"\n[X] Model not found: {model_path}")
        print("\nYou need to train the model first:")
        print("  python main.py setup")
        return False

def test_imports():
    """Test if dependencies are installed"""
    print("\n" + "="*70)
    print(" TESTING DEPENDENCIES")
    print("="*70)
    
    modules = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'sklearn': 'scikit-learn',
        'scapy': 'Scapy',
        'numpy': 'NumPy',
        'pandas': 'Pandas'
    }
    
    missing = []
    
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [X] {name} - NOT INSTALLED")
            missing.append(name)
    
    if missing:
        print(f"\n[X] Missing packages: {', '.join(missing)}")
        print("\nInstall with:")
        print("  pip install Flask Flask-CORS scikit-learn scapy numpy pandas")
        return False
    else:
        print("\n[OK] All dependencies installed!")
        return True

def main():
    print("""
    ===================================================================
    
        ZOMBIE WIFI DETECTOR - QUICK FIX TOOL
        
    ===================================================================
    
    This tool will:
      1. Fix file paths and remove duplicates
      2. Verify project structure
      3. Check ML model
      4. Test dependencies
    """)
    
    input("Press Enter to begin...")
    
    # Run fixes
    structure_ok = fix_paths()
    model_ok = check_model()
    deps_ok = test_imports()
    
    # Final summary
    print("\n" + "="*70)
    print(" SUMMARY")
    print("="*70)
    
    print("\nStatus:")
    print(f"  File Structure: {'[OK]' if structure_ok else '[NEEDS ATTENTION]'}")
    print(f"  ML Model: {'[OK]' if model_ok else '[NEEDS TRAINING]'}")
    print(f"  Dependencies: {'[OK]' if deps_ok else '[NEEDS INSTALLATION]'}")
    
    if structure_ok and model_ok and deps_ok:
        print("\n[OK] Everything is ready!")
        print("\nTo start the web application:")
        print("  cd backend")
        print("  python app.py")
        print("\nThen open: http://localhost:5000")
    else:
        print("\n[!] Some issues need attention:")
        
        if not model_ok:
            print("\n  1. Train the model:")
            print("     python main.py setup")
        
        if not deps_ok:
            print("\n  2. Install dependencies:")
            print("     pip install Flask Flask-CORS scikit-learn scapy numpy pandas")
        
        print("\nThen run this fix script again:")
        print("  python fix.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nFix cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
