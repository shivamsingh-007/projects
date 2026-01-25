"""
Flask Backend API for Zombie WiFi Detector
Handles authentication, scanning, and ML predictions
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import sys
import threading
import time
from datetime import datetime, timedelta
import secrets

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model_training import ZombieWiFiModel
from feature_extraction import FeatureExtractor
from data_collection import PacketCapture
import numpy as np

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

# Database setup
DATABASE = 'backend/users.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_scan TIMESTAMP,
                auto_scan_enabled BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                alert_level INTEGER NOT NULL,
                confidence REAL NOT NULL,
                status TEXT NOT NULL,
                interface TEXT,
                features TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                interface TEXT,
                scan_interval INTEGER DEFAULT 3600,
                notifications_enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()

# Load ML model
model = None
model_path = 'models/zombie_wifi_detector.pkl'

def load_model():
    """Load the trained ML model"""
    global model
    try:
        if os.path.exists(model_path):
            model = ZombieWiFiModel()
            model.load_model(model_path)
            print("✓ ML Model loaded successfully")
        else:
            print("⚠ Model not found. Run setup first.")
    except Exception as e:
        print(f"Error loading model: {e}")

# Auto-scan scheduler
auto_scan_threads = {}

def auto_scan_task(user_id, interface):
    """Background task for automatic scanning"""
    while True:
        try:
            # Get user settings
            with get_db() as conn:
                settings = conn.execute(
                    'SELECT scan_interval FROM settings WHERE user_id = ?',
                    (user_id,)
                ).fetchone()
                
                user = conn.execute(
                    'SELECT auto_scan_enabled FROM users WHERE id = ?',
                    (user_id,)
                ).fetchone()
            
            if not user or not user['auto_scan_enabled']:
                break
            
            interval = settings['scan_interval'] if settings else 3600
            
            # Perform scan
            result = perform_scan(interface, user_id)
            
            # Wait for next scan
            time.sleep(interval)
            
        except Exception as e:
            print(f"Auto-scan error for user {user_id}: {e}")
            time.sleep(3600)  # Wait 1 hour on error

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if '@' not in email:
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert user
        with get_db() as conn:
            try:
                cursor = conn.execute(
                    'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                    (username, email, password_hash)
                )
                user_id = cursor.lastrowid
                
                # Create default settings
                conn.execute(
                    'INSERT INTO settings (user_id) VALUES (?)',
                    (user_id,)
                )
                
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Registration successful',
                    'user_id': user_id
                }), 201
                
            except sqlite3.IntegrityError:
                return jsonify({'error': 'Username or email already exists'}), 400
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ? OR email = ?',
                (username, username)
            ).fetchone()
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'}), 200

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        with get_db() as conn:
            user = conn.execute(
                'SELECT id, username, email, created_at, last_scan FROM users WHERE id = ?',
                (session['user_id'],)
            ).fetchone()
            
            settings = conn.execute(
                'SELECT * FROM settings WHERE user_id = ?',
                (session['user_id'],)
            ).fetchone()
        
        return jsonify({
            'user': dict(user),
            'settings': dict(settings) if settings else {}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update user settings"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        if request.method == 'GET':
            with get_db() as conn:
                settings = conn.execute(
                    'SELECT * FROM settings WHERE user_id = ?',
                    (session['user_id'],)
                ).fetchone()
            
            return jsonify(dict(settings) if settings else {}), 200
        
        else:  # POST
            data = request.get_json()
            
            with get_db() as conn:
                conn.execute('''
                    INSERT INTO settings (user_id, interface, scan_interval, notifications_enabled)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        interface = excluded.interface,
                        scan_interval = excluded.scan_interval,
                        notifications_enabled = excluded.notifications_enabled
                ''', (
                    session['user_id'],
                    data.get('interface'),
                    data.get('scan_interval', 3600),
                    data.get('notifications_enabled', True)
                ))
                conn.commit()
            
            return jsonify({'success': True, 'message': 'Settings updated'}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_scan(interface, user_id):
    """Perform actual network scan"""
    try:
        if not model:
            return {
                'error': 'Model not loaded',
                'alert_level': 0,
                'confidence': 0,
                'status': 'error'
            }
        
        # Capture packets
        capture = PacketCapture(interface=interface, duration=60)
        packets = capture.capture_packets(timeout=60)
        
        if not packets:
            return {
                'error': 'No packets captured',
                'alert_level': 0,
                'confidence': 0,
                'status': 'error'
            }
        
        # Extract features
        extractor = FeatureExtractor()
        features = extractor.extract_all_features(packets, time_window=60)
        
        # Predict
        feature_array = np.array([list(features.values())])
        prediction = model.predict(feature_array)[0]
        proba = model.predict_proba(feature_array)[0]
        confidence = float(proba[1])
        
        # Determine alert level
        if prediction == 1:
            if confidence >= 0.85:
                alert_level = 4  # CRITICAL
                status = 'critical'
            elif confidence >= 0.65:
                alert_level = 3  # HIGH
                status = 'high'
            else:
                alert_level = 2  # MEDIUM
                status = 'medium'
        else:
            if confidence > 0.5:
                alert_level = 1  # LOW
                status = 'low'
            else:
                alert_level = 0  # NORMAL
                status = 'normal'
        
        # Save to database
        with get_db() as conn:
            conn.execute('''
                INSERT INTO scans (user_id, alert_level, confidence, status, interface, features)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, alert_level, confidence, status, interface, str(features)))
            
            conn.execute(
                'UPDATE users SET last_scan = CURRENT_TIMESTAMP WHERE id = ?',
                (user_id,)
            )
            conn.commit()
        
        return {
            'alert_level': alert_level,
            'confidence': confidence,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'features': features
        }
        
    except Exception as e:
        print(f"Scan error: {e}")
        return {
            'error': str(e),
            'alert_level': 0,
            'confidence': 0,
            'status': 'error'
        }

@app.route('/api/scan', methods=['POST'])
def scan():
    """Perform manual scan"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        interface = data.get('interface')
        
        if not interface:
            # Try to get from settings
            with get_db() as conn:
                settings = conn.execute(
                    'SELECT interface FROM settings WHERE user_id = ?',
                    (session['user_id'],)
                ).fetchone()
                
                if settings and settings['interface']:
                    interface = settings['interface']
                else:
                    return jsonify({'error': 'No interface specified'}), 400
        
        # Perform scan in background thread to avoid timeout
        result = perform_scan(interface, session['user_id'])
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/history', methods=['GET'])
def scan_history():
    """Get scan history"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        limit = request.args.get('limit', 20, type=int)
        
        with get_db() as conn:
            scans = conn.execute('''
                SELECT id, timestamp, alert_level, confidence, status, interface
                FROM scans
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session['user_id'], limit)).fetchall()
        
        return jsonify({
            'scans': [dict(scan) for scan in scans]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/latest', methods=['GET'])
def latest_scan():
    """Get latest scan result"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        with get_db() as conn:
            scan = conn.execute('''
                SELECT * FROM scans
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (session['user_id'],)).fetchone()
        
        if not scan:
            return jsonify({'error': 'No scans found'}), 404
        
        return jsonify(dict(scan)), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auto-scan/toggle', methods=['POST'])
def toggle_auto_scan():
    """Enable/disable automatic scanning"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        with get_db() as conn:
            conn.execute(
                'UPDATE users SET auto_scan_enabled = ? WHERE id = ?',
                (enabled, session['user_id'])
            )
            conn.commit()
        
        if enabled:
            # Start auto-scan thread
            with get_db() as conn:
                settings = conn.execute(
                    'SELECT interface FROM settings WHERE user_id = ?',
                    (session['user_id'],)
                ).fetchone()
            
            if settings and settings['interface']:
                if session['user_id'] not in auto_scan_threads:
                    thread = threading.Thread(
                        target=auto_scan_task,
                        args=(session['user_id'], settings['interface']),
                        daemon=True
                    )
                    thread.start()
                    auto_scan_threads[session['user_id']] = thread
        else:
            # Stop auto-scan
            if session['user_id'] in auto_scan_threads:
                del auto_scan_threads[session['user_id']]
        
        return jsonify({
            'success': True,
            'auto_scan_enabled': enabled
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-interface', methods=['GET'])
def detect_interface():
    """Auto-detect network interface"""
    try:
        from scapy.all import get_if_list
        interfaces = get_if_list()
        
        # Filter out loopback
        active_interfaces = [iface for iface in interfaces if 'Loopback' not in iface]
        
        return jsonify({
            'interfaces': active_interfaces,
            'recommended': active_interfaces[0] if active_interfaces else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# Initialize and run
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" ZOMBIE WIFI DETECTOR - BACKEND SERVER")
    print("="*70)
    
    # Initialize database
    print("\nInitializing database...")
    os.makedirs('backend', exist_ok=True)
    init_db()
    print("✓ Database ready")
    
    # Load ML model
    print("\nLoading ML model...")
    load_model()
    
    print("\n" + "="*70)
    print(" SERVER STARTING")
    print("="*70)
    print("\nBackend API: http://localhost:5000")
    print("Frontend: Open index.html in browser")
    print("\nPress Ctrl+C to stop\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
