"""
Complete Integrated Flask Backend for Zombie WiFi Detector
Production-ready with all features working
"""

from flask import Flask, request, jsonify, session, send_from_directory, render_template_string
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

# Get the absolute path to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import detection modules
try:
    from model_training import ZombieWiFiModel
    from feature_extraction import FeatureExtractor
    from data_collection import PacketCapture
    import numpy as np
    DETECTION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Detection modules not fully available: {e}")
    DETECTION_AVAILABLE = False

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, supports_credentials=True)

# Database path
DB_PATH = os.path.join(PROJECT_ROOT, 'backend', 'zombie_wifi.db')

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db() as conn:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Scans table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scans (
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
            )
        ''')
        
        # Settings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                auto_scan_enabled BOOLEAN DEFAULT 1,
                scan_interval INTEGER DEFAULT 3600,
                network_interface TEXT,
                last_auto_scan TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
    
    print(f"✓ Database initialized at: {DB_PATH}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_client_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    return request.environ.get('REMOTE_ADDR', 'Unknown')

def get_network_interface():
    """Auto-detect network interface"""
    try:
        from scapy.all import get_if_list
        interfaces = get_if_list()
        interfaces = [i for i in interfaces if 'Loopback' not in i and 'loopback' not in i.lower()]
        return interfaces[0] if interfaces else None
    except Exception as e:
        print(f"Error getting interface: {e}")
        return None

def run_detection(user_id, interface=None, is_auto=False):
    """Run zombie WiFi detection"""
    
    if not DETECTION_AVAILABLE:
        return {
            'success': False,
            'error': 'Detection modules not available. Please run setup first.'
        }
    
    try:
        # Get or auto-detect interface
        if not interface:
            interface = get_network_interface()
        
        if not interface:
            return {'success': False, 'error': 'Could not detect network interface'}
        
        # Check if model exists
        model_path = os.path.join(PROJECT_ROOT, 'models', 'zombie_wifi_detector.pkl')
        
        if not os.path.exists(model_path):
            return {
                'success': False,
                'error': 'Model not found. Please run: python main.py setup'
            }
        
        # Load model
        model = ZombieWiFiModel()
        model.load_model(model_path)
        
        # Capture packets (30 seconds for quick scan)
        print(f"Starting packet capture on {interface}...")
        capture = PacketCapture(interface=interface, duration=30)
        packets = capture.capture_packets(timeout=30)
        
        if not packets:
            return {'success': False, 'error': 'No packets captured'}
        
        print(f"Captured {len(packets)} packets, extracting features...")
        
        # Extract features
        extractor = FeatureExtractor()
        features = extractor.extract_all_features(packets, time_window=30)
        
        # Make prediction
        feature_array = np.array([list(features.values())])
        prediction = model.predict(feature_array)[0]
        proba = model.predict_proba(feature_array)[0]
        confidence = proba[prediction]
        
        # Determine alert level
        alert_levels = ['NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if prediction == 1:  # Zombie WiFi
            if confidence >= 0.85:
                alert_level = 4  # CRITICAL
            elif confidence >= 0.65:
                alert_level = 3  # HIGH
            else:
                alert_level = 2  # MEDIUM
        else:
            if confidence < 0.7:
                alert_level = 1  # LOW
            else:
                alert_level = 0  # NORMAL
        
        alert_name = alert_levels[alert_level]
        
        # Save to database
        with get_db() as conn:
            cursor = conn.execute('''
                INSERT INTO scans (user_id, ip_address, interface, alert_level, 
                                 alert_name, confidence, features, is_auto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, get_client_ip(), interface, alert_level, 
                  alert_name, float(confidence), json.dumps(features), is_auto))
            
            scan_id = cursor.lastrowid
            conn.commit()
        
        # Get the scan data
        with get_db() as conn:
            scan = conn.execute('SELECT * FROM scans WHERE id = ?', (scan_id,)).fetchone()
        
        return {
            'success': True,
            'result': {
                'id': scan['id'],
                'timestamp': scan['timestamp'],
                'ip_address': scan['ip_address'],
                'interface': scan['interface'],
                'alert_level': scan['alert_level'],
                'alert_name': scan['alert_name'],
                'confidence': scan['confidence'],
                'features': json.loads(scan['features']),
                'is_auto': bool(scan['is_auto'])
            }
        }
        
    except PermissionError:
        return {
            'success': False,
            'error': 'Permission denied. Please run as Administrator/sudo.'
        }
    except Exception as e:
        print(f"Detection error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': f'Detection failed: {str(e)}'
        }

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        with get_db() as conn:
            # Check if user exists
            existing = conn.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (data['username'], data['email'])
            ).fetchone()
            
            if existing:
                return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
            
            # Create user
            password_hash = generate_password_hash(data['password'])
            cursor = conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (data['username'], data['email'], password_hash)
            )
            user_id = cursor.lastrowid
            
            # Create default settings
            conn.execute(
                'INSERT INTO settings (user_id) VALUES (?)',
                (user_id,)
            )
            
            conn.commit()
            
            # Log in user
            session['user_id'] = user_id
            session.permanent = True
            
            # Get user data
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            })
    
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Missing credentials'}), 400
    
    try:
        with get_db() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (data['username'],)
            ).fetchone()
            
            if not user or not check_password_hash(user['password_hash'], data['password']):
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
            # Update last login
            conn.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            conn.commit()
            
            # Set session
            session['user_id'] = user['id']
            session.permanent = True
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            })
    
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/me', methods=['GET'])
def get_current_user():
    """Get current logged-in user"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        with get_db() as conn:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'created_at': user['created_at']
                }
            })
    
    except Exception as e:
        print(f"Error getting user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# DETECTION ROUTES
# ============================================================================

@app.route('/api/scan', methods=['POST'])
def run_scan():
    """Run manual WiFi scan"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    data = request.get_json() or {}
    interface = data.get('interface')
    
    result = run_detection(user_id, interface, is_auto=False)
    return jsonify(result)

@app.route('/api/scans', methods=['GET'])
def get_scans():
    """Get user's scan history"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    limit = request.args.get('limit', 10, type=int)
    
    try:
        with get_db() as conn:
            scans = conn.execute('''
                SELECT * FROM scans 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit)).fetchall()
            
            return jsonify({
                'success': True,
                'scans': [{
                    'id': scan['id'],
                    'timestamp': scan['timestamp'],
                    'ip_address': scan['ip_address'],
                    'interface': scan['interface'],
                    'alert_level': scan['alert_level'],
                    'alert_name': scan['alert_name'],
                    'confidence': scan['confidence'],
                    'features': json.loads(scan['features']) if scan['features'] else {},
                    'is_auto': bool(scan['is_auto'])
                } for scan in scans]
            })
    
    except Exception as e:
        print(f"Error getting scans: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scans/latest', methods=['GET'])
def get_latest_scan():
    """Get user's latest scan"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        with get_db() as conn:
            scan = conn.execute('''
                SELECT * FROM scans 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (user_id,)).fetchone()
            
            if not scan:
                return jsonify({'success': False, 'error': 'No scans found'}), 404
            
            return jsonify({
                'success': True,
                'scan': {
                    'id': scan['id'],
                    'timestamp': scan['timestamp'],
                    'ip_address': scan['ip_address'],
                    'interface': scan['interface'],
                    'alert_level': scan['alert_level'],
                    'alert_name': scan['alert_name'],
                    'confidence': scan['confidence'],
                    'features': json.loads(scan['features']) if scan['features'] else {},
                    'is_auto': bool(scan['is_auto'])
                }
            })
    
    except Exception as e:
        print(f"Error getting latest scan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scans/stats', methods=['GET'])
def get_scan_stats():
    """Get scan statistics"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        with get_db() as conn:
            # Total scans
            total = conn.execute(
                'SELECT COUNT(*) as count FROM scans WHERE user_id = ?',
                (user_id,)
            ).fetchone()['count']
            
            # Threats detected (HIGH or CRITICAL)
            threats = conn.execute(
                'SELECT COUNT(*) as count FROM scans WHERE user_id = ? AND alert_level >= 3',
                (user_id,)
            ).fetchone()['count']
            
            # Last scan
            last_scan = conn.execute(
                'SELECT timestamp FROM scans WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
                (user_id,)
            ).fetchone()
            
            # Alert distribution
            distribution = conn.execute('''
                SELECT alert_name, COUNT(*) as count 
                FROM scans 
                WHERE user_id = ? 
                GROUP BY alert_name
            ''', (user_id,)).fetchall()
            
            alert_dist = {row['alert_name']: row['count'] for row in distribution}
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_scans': total,
                    'threats_detected': threats,
                    'last_scan': last_scan['timestamp'] if last_scan else None,
                    'alert_distribution': alert_dist
                }
            })
    
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve landing page"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), 'index.html')

@app.route('/login')
def login_page():
    """Serve login page"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), 'login.html')

@app.route('/register')
def register_page():
    """Serve register page"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), 'register.html')

@app.route('/dashboard')
def dashboard():
    """Serve dashboard page"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'frontend'), 'dashboard.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(PROJECT_ROOT, 'static'), filename)

# ============================================================================
# AUTO-SCAN WORKER
# ============================================================================

def auto_scan_worker():
    """Background worker for automatic scans"""
    while True:
        try:
            with app.app_context():
                with get_db() as conn:
                    # Find users with auto-scan enabled
                    users = conn.execute('''
                        SELECT s.user_id, s.scan_interval, s.last_auto_scan, s.network_interface
                        FROM settings s
                        WHERE s.auto_scan_enabled = 1
                    ''').fetchall()
                    
                    for user in users:
                        # Check if scan is due
                        if user['last_auto_scan']:
                            last_scan = datetime.fromisoformat(user['last_auto_scan'])
                            time_since = (datetime.now() - last_scan).total_seconds()
                            
                            if time_since < user['scan_interval']:
                                continue
                        
                        # Run scan
                        print(f"Running auto-scan for user {user['user_id']}")
                        run_detection(
                            user['user_id'],
                            user['network_interface'],
                            is_auto=True
                        )
                        
                        # Update last scan time
                        conn.execute(
                            'UPDATE settings SET last_auto_scan = CURRENT_TIMESTAMP WHERE user_id = ?',
                            (user['user_id'],)
                        )
                        conn.commit()
        
        except Exception as e:
            print(f"Auto-scan error: {e}")
        
        # Sleep for 5 minutes before checking again
        time.sleep(300)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start auto-scan worker
    auto_scan_thread = threading.Thread(target=auto_scan_worker, daemon=True)
    auto_scan_thread.start()
    print("✓ Auto-scan worker started")
    
    # Print startup info
    print("\n" + "="*70)
    print(" ZOMBIE WIFI DETECTOR - WEB APPLICATION")
    print("="*70)
    print("\n🌐 Server starting at: http://localhost:5000")
    print("📊 Open your browser and visit that URL")
    print("\n✨ Features:")
    print("  • User registration & login")
    print("  • Automatic network detection")
    print("  • One-click scanning")
    print("  • Hourly automatic protection")
    print("  • Beautiful dashboard")
    print("\nPress Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    # Run app
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
