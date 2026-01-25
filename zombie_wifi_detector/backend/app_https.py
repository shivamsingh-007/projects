"""
ZOMBIE WIFI DETECTOR - HTTPS ENABLED
Run with SSL/TLS support
"""

from flask import Flask, send_file, request, jsonify, session
from flask_cors import CORS
import os
import sys
import ssl

# Import from existing cyberpunk app
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

# Import the cyberpunk app
from app_cyberpunk import app, init_db

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" 🔒 ZOMBIE WIFI DETECTOR - HTTPS ENABLED")
    print(" 🤖 CyberSentry AI - Tarun, Shivam, Yash")
    print("="*70)
    
    init_db()
    
    print("\n🌐 HTTPS Server starting...")
    print("  • https://localhost:5000/ (HTTPS)")
    print("  • http://localhost:5000/  (HTTP fallback)")
    
    print("\n⚠️  Browser will show security warning - this is normal for self-signed certificates")
    print("   Click 'Advanced' → 'Proceed to localhost (unsafe)'")
    
    print("\n" + "="*70 + "\n")
    
    # Create SSL context with adhoc certificates
    # This automatically generates a self-signed certificate
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        ssl_context='adhoc',  # Auto-generate self-signed cert
        use_reloader=False
    )
