#!/usr/bin/env python3
"""Quick launcher for Zombie WiFi Detector Web App"""
import subprocess
import sys
import os

# Change to project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Check if model exists
if not os.path.exists('models/zombie_wifi_detector.pkl'):
    print("\n[WARNING] Model not found!")
    print("Running setup first...\n")
    subprocess.run([sys.executable, 'main.py', 'setup'])

print("\n" + "="*70)
print(" STARTING ZOMBIE WIFI DETECTOR WEB APPLICATION")
print("="*70)
print("\nOpening at: http://localhost:5000")
print("Press Ctrl+C to stop\n")

# Start the web app
try:
    subprocess.run([sys.executable, 'backend/app.py'])
except KeyboardInterrupt:
    print("\n\n[OK] Server stopped. Goodbye!")
