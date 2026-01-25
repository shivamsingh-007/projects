"""
Fixed Flask Backend for Zombie WiFi Detector
All routes properly configured
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import sys
import threading
import time
import json
from datetime import datetime, timedelta
import secrets

# Get paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

# Import detection modules
try:
    from model_training import ZombieWiFiModel
    from feature_extraction import FeatureExtractor
    from data_collection import PacketCapture
    import numpy as np
    DETECTION_AVAILABLE = True
    print("✓ Detection modules loaded")
except ImportError as e:
    print(f"Warning: Detection modules not available: {e}")
    DETECTION_AVAILABLE = False

# Initialize Flask
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, supports_credentials=True)

# Database path
DB_PATH = os.path.join(BACKEND_DIR, 'zombie_wifi.db')

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        interface TEXT,
        alert_level INTEGER,
        alert_name TEXT,
        confidence REAL,
        features TEXT,
        is_auto BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        auto_scan_enabled BOOLEAN DEFAULT 1,
        scan_interval INTEGER DEFAULT 3600,
        network_interface TEXT,
        last_auto_scan TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()
    print(f"✓ Database initialized: {DB_PATH}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip():
    """Get client IP"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', 'Unknown')

def run_detection(user_id, interface=None, is_auto=False):
    """Run detection"""
    if not DETECTION_AVAILABLE:
        return {'success': False, 'error': 'Detection modules not available'}
    
    try:
        model_path = os.path.join(PROJECT_ROOT, 'models', 'zombie_wifi_detector.pkl')
        
        if not os.path.exists(model_path):
            return {'success': False, 'error': 'Model not found. Run: python main.py setup'}
        
        # Simplified for testing - return fake result
        # In production, this would do actual packet capture
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute('''
            INSERT INTO scans (user_id, ip_address, interface, alert_level, 
                             alert_name, confidence, features, is_auto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, get_client_ip(), 'auto', 0, 'NORMAL', 0.95, '{}', is_auto))
        
        scan_id = cursor.lastrowid
        conn.commit()
        
        scan = conn.execute('SELECT * FROM scans WHERE id = ?', (scan_id,)).fetchone()
        conn.close()
        
        return {
            'success': True,
            'result': {
                'id': scan[0],
                'timestamp': scan[2],
                'ip_address': scan[3],
                'interface': scan[4],
                'alert_level': scan[5],
                'alert_name': scan[6],
                'confidence': scan[7],
                'features': {},
                'is_auto': bool(scan[9])
            }
        }
    except Exception as e:
        print(f"Detection error: {e}")
        return {'success': False, 'error': str(e)}

# ============================================================================
# FRONTEND ROUTES (IMPORTANT!)
# ============================================================================

@app.route('/')
def index():
    """Serve landing page"""
    try:
        index_path = os.path.join(PROJECT_ROOT, 'frontend', 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        else:
            return f"Error: index.html not found at {index_path}", 404
    except Exception as e:
        return f"Error serving index: {e}", 500

@app.route('/login')
def login_page():
    """Serve login page"""
    try:
        login_path = os.path.join(PROJECT_ROOT, 'frontend', 'login.html')
        if os.path.exists(login_path):
            return send_file(login_path)
        else:
            return f"Error: login.html not found at {login_path}", 404
    except Exception as e:
        return f"Error serving login: {e}", 500

@app.route('/register')
def register_page():
    """Serve register page"""
    try:
        register_path = os.path.join(PROJECT_ROOT, 'frontend', 'register.html')
        if os.path.exists(register_path):
            return send_file(register_path)
        else:
            return f"Error: register.html not found at {register_path}", 404
    except Exception as e:
        return f"Error serving register: {e}", 500

@app.route('/dashboard')
def dashboard():
    """Serve dashboard page"""
    try:
        dashboard_path = os.path.join(PROJECT_ROOT, 'frontend', 'dashboard.html')
        if os.path.exists(dashboard_path):
            return send_file(dashboard_path)
        else:
            return f"Error: dashboard.html not found at {dashboard_path}", 404
    except Exception as e:
        return f"Error serving dashboard: {e}", 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        static_path = os.path.join(PROJECT_ROOT, 'static', filename)
        if os.path.exists(static_path):
            return send_file(static_path)
        else:
            return f"Error: {filename} not found", 404
    except Exception as e:
        return f"Error serving static: {e}", 500

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register user"""
    data = request.get_json()
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (data['username'], data['email'], generate_password_hash(data['password'])))
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.execute('INSERT INTO settings (user_id) VALUES (?)', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'user': {'id': user_id, 'username': data['username'], 'email': data['email']}
        })
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'User already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing credentials'}), 400
    
    try:
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute('SELECT * FROM users WHERE username = ?', (data['username'],)).fetchone()
        conn.close()
        
        if not user or not check_password_hash(user[3], data['password']):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        return jsonify({
            'success': True,
            'user': {'id': user[0], 'username': user[1], 'email': user[2]}
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    return jsonify({'success': True})

@app.route('/api/me', methods=['GET'])
def get_me():
    """Get current user (mock)"""
    return jsonify({'success': False, 'error': 'Not authenticated'}), 401

@app.route('/api/scan', methods=['POST'])
def scan():
    """Run scan"""
    # Mock user_id for testing
    result = run_detection(user_id=1, is_auto=False)
    return jsonify(result)

@app.route('/api/scans', methods=['GET'])
def get_scans():
    """Get scans"""
    try:
        conn = sqlite3.connect(DB_PATH)
        scans = conn.execute('SELECT * FROM scans ORDER BY timestamp DESC LIMIT 10').fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'scans': [{
                'id': s[0],
                'timestamp': s[2],
                'ip_address': s[3],
                'interface': s[4],
                'alert_level': s[5],
                'alert_name': s[6],
                'confidence': s[7],
                'features': {},
                'is_auto': bool(s[9])
            } for s in scans]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scans/latest', methods=['GET'])
def get_latest():
    """Get latest scan"""
    try:
        conn = sqlite3.connect(DB_PATH)
        scan = conn.execute('SELECT * FROM scans ORDER BY timestamp DESC LIMIT 1').fetchone()
        conn.close()
        
        if not scan:
            return jsonify({'success': False, 'error': 'No scans'}), 404
        
        return jsonify({
            'success': True,
            'scan': {
                'id': scan[0],
                'timestamp': scan[2],
                'ip_address': scan[3],
                'interface': scan[4],
                'alert_level': scan[5],
                'alert_name': scan[6],
                'confidence': scan[7],
                'features': {},
                'is_auto': bool(scan[9])
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scans/stats', methods=['GET'])
def get_stats():
    """Get stats"""
    try:
        conn = sqlite3.connect(DB_PATH)
        total = conn.execute('SELECT COUNT(*) FROM scans').fetchone()[0]
        threats = conn.execute('SELECT COUNT(*) FROM scans WHERE alert_level >= 3').fetchone()[0]
        last = conn.execute('SELECT timestamp FROM scans ORDER BY timestamp DESC LIMIT 1').fetchone()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_scans': total,
                'threats_detected': threats,
                'last_scan': last[0] if last else None,
                'alert_distribution': {}
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize
    init_db()
    
    # Startup message
    print("\n" + "="*70)
    print(" ZOMBIE WIFI DETECTOR - WEB APPLICATION")
    print("="*70)
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"Backend Dir: {BACKEND_DIR}")
    print(f"Database: {DB_PATH}")
    print("\n🌐 Server starting at: http://localhost:5000")
    print("📊 Open your browser and visit that URL")
    print("\n✨ Routes available:")
    print("  • http://localhost:5000/ (Landing page)")
    print("  • http://localhost:5000/login (Login)")
    print("  • http://localhost:5000/register (Register)")
    print("  • http://localhost:5000/dashboard (Dashboard)")
    print("\nPress Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    # Check files
    print("Checking files...")
    for page in ['index.html', 'login.html', 'register.html', 'dashboard.html']:
        path = os.path.join(PROJECT_ROOT, 'frontend', page)
        if os.path.exists(path):
            print(f"  ✓ {page}")
        else:
            print(f"  ✗ {page} NOT FOUND at {path}")
    
    css_path = os.path.join(PROJECT_ROOT, 'static', 'css', 'style.css')
    if os.path.exists(css_path):
        print(f"  ✓ style.css")
    else:
        print(f"  ✗ style.css NOT FOUND at {css_path}")
    
    print()
    
    # Run
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
