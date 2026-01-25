#!/usr/bin/env python3
"""
Complete Integration Script for Zombie WiFi Detector
Windows-compatible version without special Unicode characters
"""

import os
import sys
import subprocess
import shutil

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def run_command(cmd, description, check=True):
    """Run a command with nice output"""
    print(f"\n> {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [OK] {description} - Success")
            return True
        else:
            print(f"  [FAIL] {description} - Failed")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] {description} - Error: {e}")
        return False

def check_python_version():
    """Check Python version"""
    print_header("CHECKING PYTHON VERSION")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("\n[X] Python 3.8 or higher is required")
        return False
    
    print("[OK] Python version is compatible")
    return True

def install_dependencies():
    """Install all required dependencies"""
    print_header("INSTALLING DEPENDENCIES")
    
    # All dependencies combined
    all_deps = [
        'Flask==3.0.0',
        'Flask-CORS==4.0.0',
        'Werkzeug==3.0.1',
        'scikit-learn',
        'xgboost',
        'numpy',
        'pandas',
        'scipy',
        'scapy',
        'matplotlib',
        'seaborn',
        'pyyaml',
        'joblib'
    ]
    
    print(f"\nInstalling {len(all_deps)} packages...")
    
    cmd = f'{sys.executable} -m pip install --upgrade ' + ' '.join(all_deps)
    
    if run_command(cmd, "Installing dependencies"):
        print("\n[OK] All dependencies installed successfully")
        return True
    else:
        print("\n[WARNING] Some packages may have failed")
        print("Try installing manually:")
        print(f"  pip install {' '.join(all_deps)}")
        return False

def setup_project_structure():
    """Ensure correct project structure"""
    print_header("SETTING UP PROJECT STRUCTURE")
    
    directories = [
        'backend',
        'frontend',
        'static/css',
        'static/js',
        'models',
        'data',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  [OK] {directory}/")
    
    print("\n[OK] Project structure ready")
    return True

def check_model_exists():
    """Check if ML model is trained"""
    print_header("CHECKING ML MODEL")
    
    model_path = 'models/zombie_wifi_detector.pkl'
    
    if os.path.exists(model_path):
        print(f"[OK] Model found at: {model_path}")
        return True
    else:
        print(f"[X] Model not found at: {model_path}")
        print("\nYou need to train the model first.")
        return False

def train_model():
    """Train the ML model"""
    print_header("TRAINING ML MODEL")
    
    print("\nThis will:")
    print("  1. Generate synthetic training data")
    print("  2. Train a Random Forest model")
    print("  3. Create baseline profile")
    print("\nThis may take 2-3 minutes...")
    
    response = input("\nContinue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("Skipping model training")
        return False
    
    if run_command(f'{sys.executable} main.py setup', 
                  "Training model"):
        print("\n[OK] Model trained successfully")
        return True
    else:
        print("\n[X] Model training failed")
        print("\nTry running manually:")
        print("  python main.py setup")
        return False

def copy_integrated_backend():
    """Use the integrated backend"""
    print_header("SETTING UP BACKEND")
    
    src = 'backend/app_integrated.py'
    dst = 'backend/app.py'
    
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"[OK] Copied {src} to {dst}")
        return True
    else:
        print(f"[WARNING] {src} not found, using existing backend")
        return True

def test_imports():
    """Test that all modules can be imported"""
    print_header("TESTING IMPORTS")
    
    modules = [
        'flask',
        'flask_cors',
        'sklearn',
        'xgboost',
        'numpy',
        'pandas',
        'scapy'
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  [OK] {module}")
        except ImportError:
            print(f"  [X] {module} - NOT INSTALLED")
            failed.append(module)
    
    if failed:
        print(f"\n[X] Failed to import: {', '.join(failed)}")
        print("Try installing:")
        print(f"  pip install {' '.join(failed)}")
        return False
    
    print("\n[OK] All modules imported successfully")
    return True

def create_launcher():
    """Create easy launcher script"""
    print_header("CREATING LAUNCHER")
    
    launcher_content = '''#!/usr/bin/env python3
"""Quick launcher for Zombie WiFi Detector Web App"""
import subprocess
import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check if model exists
if not os.path.exists('models/zombie_wifi_detector.pkl'):
    print("\\n[WARNING] Model not found!")
    print("Running setup first...\\n")
    subprocess.run([sys.executable, 'main.py', 'setup'])

print("\\n" + "="*70)
print(" STARTING ZOMBIE WIFI DETECTOR WEB APPLICATION")
print("="*70)
print("\\nOpening at: http://localhost:5000")
print("Press Ctrl+C to stop\\n")

# Start the web app
try:
    subprocess.run([sys.executable, 'backend/app.py'])
except KeyboardInterrupt:
    print("\\n\\n[OK] Server stopped. Goodbye!")
'''
    
    try:
        with open('start.py', 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # Make executable on Unix
        if os.name != 'nt':
            os.chmod('start.py', 0o755)
        
        print("[OK] Created start.py launcher")
        return True
    except Exception as e:
        print(f"[ERROR] Could not create launcher: {e}")
        return False

def create_readme():
    """Create quick start README"""
    print_header("CREATING DOCUMENTATION")
    
    readme_content = '''# Quick Start Guide

## Start the Web Application

### Easy Way:
```bash
python start.py
```

### Manual Way:
```bash
cd backend
python app.py
```

Then open your browser to: **http://localhost:5000**

## First Time Setup

1. Click "Register" to create your account
2. Enter username, email, and password
3. You'll be automatically logged in
4. Click "Scan Now" to check your network

## Features

- Beautiful web interface
- User registration and login
- Automatic network detection
- One-click scanning
- Hourly automatic protection
- Scan history and statistics

## Troubleshooting

### Permission Denied
Run as Administrator (Windows) or with sudo (Mac/Linux):
```bash
sudo python start.py
```

### Port 5000 In Use
Edit `backend/app.py` and change the port:
```python
app.run(port=5001)  # Change from 5000
```

### Model Not Found
Train the model first:
```bash
python main.py setup
```

## Need Help?

See `WEBAPP_README.md` for complete documentation.
'''
    
    try:
        with open('QUICKSTART.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("[OK] Created QUICKSTART.md")
        return True
    except Exception as e:
        print(f"[ERROR] Could not create README: {e}")
        return False

def main():
    """Main integration process"""
    
    print("""
    ===================================================================
                                                                  
        ZOMBIE WIFI DETECTOR - COMPLETE INTEGRATION WIZARD            
                                                                   
    ===================================================================
    """)
    
    print("This wizard will:")
    print("  1. Check your system")
    print("  2. Install all dependencies")
    print("  3. Set up project structure")
    print("  4. Train the ML model (if needed)")
    print("  5. Configure the web application")
    print("  6. Create launch scripts")
    
    input("\nPress Enter to begin...")
    
    # Step 1: Check Python
    if not check_python_version():
        print("\n[X] Please upgrade Python and try again")
        sys.exit(1)
    
    input("\nPress Enter to continue...")
    
    # Step 2: Setup structure
    setup_project_structure()
    
    input("\nPress Enter to continue...")
    
    # Step 3: Install dependencies
    install_dependencies()
    
    input("\nPress Enter to continue...")
    
    # Step 4: Test imports
    test_imports()
    
    input("\nPress Enter to continue...")
    
    # Step 5: Check/train model
    if not check_model_exists():
        if not train_model():
            print("\n[WARNING] Continuing without model...")
            print("You can train it later with: python main.py setup")
    
    input("\nPress Enter to continue...")
    
    # Step 6: Setup backend
    copy_integrated_backend()
    
    # Step 7: Create launcher
    create_launcher()
    
    # Step 8: Create documentation
    create_readme()
    
    # Final summary
    print_header("INTEGRATION COMPLETE!")
    
    print("""
[OK] System is ready!

To start the web application:

    python start.py

Then open your browser to: http://localhost:5000

Documentation:
  * QUICKSTART.md - Quick start guide
  * WEBAPP_README.md - Complete web app documentation
  * README.md - Full system documentation

Quick Commands:
  * python start.py - Start web app
  * python main.py detect - Command-line detection
  * python demo.py - Interactive demo

Troubleshooting:
  * Run as Administrator/sudo if permission errors
  * Check WEBAPP_README.md for common issues
  * Ensure port 5000 is available

Enjoy your AI-powered network security system!
    """)
    
    # Offer to start now
    response = input("\nStart the web application now? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\nStarting web application...")
        print("Open your browser to: http://localhost:5000\n")
        
        try:
            if os.path.exists('backend/app.py'):
                os.chdir('backend')
                subprocess.run([sys.executable, 'app.py'])
            else:
                print("Backend not found. Please run: python start.py")
        except KeyboardInterrupt:
            print("\n\nServer stopped. Goodbye!")
    else:
        print("\nTo start later, run: python start.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
