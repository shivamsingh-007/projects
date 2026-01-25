#!/usr/bin/env python3
"""
Quick Start Script for Zombie WiFi Detector Web App
Run this to start the web application
"""

import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    required = ['flask', 'flask_cors', 'flask_sqlalchemy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        ZOMBIE WIFI DETECTOR - WEB APPLICATION                     ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if model exists
    model_path = os.path.join('models', 'zombie_wifi_detector.pkl')
    if not os.path.exists(model_path):
        print("⚠️  Model not found!")
        print("\nFirst, train the model:")
        print("  python main.py setup\n")
        
        response = input("Do you want to run setup now? (y/n): ")
        if response.lower() == 'y':
            print("\nRunning setup...")
            subprocess.run([sys.executable, 'main.py', 'setup'])
        else:
            print("\nExiting. Run setup before starting web app.")
            sys.exit(1)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing = check_requirements()
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nInstalling...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            'Flask', 'Flask-CORS', 'Flask-SQLAlchemy', 'Werkzeug'
        ])
    else:
        print("✓ All dependencies installed\n")
    
    # Start server
    print("="*70)
    print(" STARTING WEB SERVER")
    print("="*70)
    print("\n🌐 Server will start at: http://localhost:5000")
    print("📊 Open your browser and visit that URL\n")
    print("✨ Features:")
    print("  • User registration & login")
    print("  • Automatic network detection")
    print("  • One-click scanning")
    print("  • Hourly automatic protection")
    print("  • Beautiful dashboard\n")
    print("Press Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    # Change to backend directory and run
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped. Goodbye!")

if __name__ == "__main__":
    main()
