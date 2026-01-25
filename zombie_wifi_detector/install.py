#!/usr/bin/env python3
"""
Installation and Quick Start Script
Checks dependencies and guides through initial setup
"""

import sys
import os
import subprocess
import importlib

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def check_python_version():
    """Check if Python version is compatible"""
    print_header("CHECKING PYTHON VERSION")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("\n❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}")
        return False
    
    print("✓ Python version is compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print_header("CHECKING DEPENDENCIES")
    
    required_packages = {
        'sklearn': 'scikit-learn',
        'xgboost': 'xgboost',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scipy': 'scipy',
        'scapy': 'scapy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'yaml': 'pyyaml',
        'joblib': 'joblib'
    }
    
    missing = []
    installed = []
    
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            installed.append(package_name)
            print(f"✓ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"❌ {package_name} - NOT INSTALLED")
    
    print(f"\nInstalled: {len(installed)}/{len(required_packages)}")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        return False, missing
    
    return True, []

def install_dependencies(missing_packages):
    """Attempt to install missing packages"""
    print_header("INSTALLING DEPENDENCIES")
    
    print(f"Missing packages: {', '.join(missing_packages)}")
    
    response = input("\nAttempt to install missing packages? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\nSkipping installation.")
        print("To install manually, run:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    print("\nInstalling packages...")
    
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '--upgrade'
        ] + missing_packages)
        
        print("\n✓ Installation complete!")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        print("\nTry installing manually:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False

def check_permissions():
    """Check if running with appropriate permissions"""
    print_header("CHECKING PERMISSIONS")
    
    if os.name == 'posix':  # Linux/Mac
        if os.geteuid() == 0:
            print("✓ Running with root privileges (required for packet capture)")
        else:
            print("⚠️  Not running as root")
            print("\nNote: Root/sudo required for:")
            print("  • Live packet capture (main.py detect)")
            print("  • Network monitoring (main.py monitor)")
            print("\nYou can still:")
            print("  • Run setup and training")
            print("  • Use demo mode")
            print("  • Analyze PCAP files")
    else:
        print("Windows detected - Administrator privileges may be required")
    
    return True

def check_project_structure():
    """Verify project structure"""
    print_header("CHECKING PROJECT STRUCTURE")
    
    required_files = [
        'main.py',
        'data_collection.py',
        'feature_extraction.py',
        'model_training.py',
        'real_time_detection.py',
        'demo.py',
        'config.yaml',
        'requirements.txt'
    ]
    
    missing_files = []
    
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"❌ {filename} - NOT FOUND")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        print("Please ensure all project files are present")
        return False
    
    print("\n✓ All project files present")
    return True

def run_initial_setup():
    """Run initial system setup"""
    print_header("INITIAL SETUP")
    
    print("\nThis will:")
    print("  1. Generate synthetic training data")
    print("  2. Train a machine learning model")
    print("  3. Create a baseline profile")
    
    response = input("\nRun initial setup now? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\nSetup skipped. You can run it later with:")
        print("  python main.py setup")
        return False
    
    print("\nRunning setup...")
    
    try:
        subprocess.check_call([sys.executable, 'main.py', 'setup'])
        print("\n✓ Setup complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed: {e}")
        return False

def show_quick_start_guide():
    """Display quick start instructions"""
    print_header("QUICK START GUIDE")
    
    print("""
🚀 GETTING STARTED

1. Run the Demo (No root required):
   python demo.py

2. Initial Setup (if not done):
   python main.py setup

3. Single Detection Scan:
   sudo python main.py detect --interface eth0 --duration 60

4. Continuous Monitoring:
   sudo python main.py monitor --interface eth0

5. Train Custom Model:
   python main.py train --model-type xgboost

6. Analyze PCAP File:
   python main.py analyze capture.pcap

📚 COMMON COMMANDS

• Find your network interface:
  Linux/Mac: ifconfig or ip addr
  Windows:   ipconfig

• Check model performance:
  python main.py compare

• View help:
  python main.py --help

⚠️  IMPORTANT NOTES

• Packet capture requires root/admin privileges
• Use demo.py to test without network access
• Check README.md for detailed documentation

🔗 USEFUL RESOURCES

• Configuration: config.yaml
• Training data: data/training_data.csv
• Trained models: models/
• Detection logs: logs/

Happy detecting! 🔒
    """)

def main():
    """Main installation wizard"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        ZOMBIE WIFI DETECTION SYSTEM - INSTALLATION WIZARD         ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check Python version
    if not check_python_version():
        print("\n❌ Installation cannot proceed. Please upgrade Python.")
        sys.exit(1)
    
    input("\nPress Enter to continue...")
    
    # Step 2: Check dependencies
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        input("\nPress Enter to continue...")
        
        if not install_dependencies(missing):
            print("\n⚠️  Some dependencies are missing.")
            print("Please install them manually and run this script again.")
            response = input("\nContinue anyway? (y/n): ").strip().lower()
            if response != 'y':
                sys.exit(1)
    
    input("\nPress Enter to continue...")
    
    # Step 3: Check permissions
    check_permissions()
    
    input("\nPress Enter to continue...")
    
    # Step 4: Check project structure
    if not check_project_structure():
        print("\n❌ Project structure incomplete.")
        sys.exit(1)
    
    input("\nPress Enter to continue...")
    
    # Step 5: Run initial setup
    setup_done = run_initial_setup()
    
    # Step 6: Show quick start guide
    show_quick_start_guide()
    
    # Final message
    print_header("INSTALLATION COMPLETE")
    
    if setup_done:
        print("\n✅ System is ready to use!")
        print("\nYou can now run:")
        print("  • python demo.py (recommended for first-time users)")
        print("  • sudo python main.py detect (for real network detection)")
    else:
        print("\n⚠️  Setup was skipped.")
        print("\nTo complete setup, run:")
        print("  python main.py setup")
    
    print("\nFor help and documentation:")
    print("  • README.md - Complete documentation")
    print("  • python main.py --help - Command line help")
    print("  • python demo.py - Interactive demo")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
