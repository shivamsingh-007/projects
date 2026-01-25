"""
ZOMBIE WIFI DETECTOR - CYBERPUNK EDITION
CyberSentry AI - Tarun, Shivam, Yash

ONE-LINER SERVER - Just run: python app_cyberpunk.py
"""

from flask import Flask, send_file, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import random
import secrets
from datetime import datetime, timedelta
import sqlite3

# ============================================================================
# PATHS & SETUP
# ============================================================================

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

app = Flask(__name__, static_folder=None)  # Disable default static handling
app.secret_key = secrets.token_hex(32)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app, supports_credentials=True)

DB_PATH = os.path.join(BACKEND_DIR, 'cyberpunk.db')

# In-memory scan storage for demo
scans_storage = []
network_threats = []

# Log all requests
@app.before_request
def log_request():
    print(f"\n📨 Request: {request.method} {request.path}")
    if request.method == 'POST':
        print(f"   Content-Type: {request.content_type}")
        print(f"   Data: {request.get_data(as_text=True)[:200]}")
    print()

# ============================================================================
# DATABASE
# ============================================================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        avatar TEXT DEFAULT 'default.png',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT,
        alert_level INTEGER,
        alert_name TEXT,
        confidence REAL,
        networks_found INTEGER,
        threats_detected INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

# ============================================================================
# ROUTES - STATIC FILES
# ============================================================================

@app.route('/static/<path:filepath>')
def serve_static(filepath):
    file_path = os.path.join(PROJECT_ROOT, 'static', filepath)
    print(f"[STATIC] Request: /static/{filepath}")
    print(f"[STATIC] Looking at: {file_path}")
    print(f"[STATIC] Exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"[STATIC] FILE NOT FOUND!")
        return f"File not found: {file_path}", 404
    
    # Determine mimetype
    if filepath.endswith('.css'):
        return send_file(file_path, mimetype='text/css')
    elif filepath.endswith('.js'):
        return send_file(file_path, mimetype='application/javascript')
    elif filepath.endswith('.png'):
        return send_file(file_path, mimetype='image/png')
    elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
        return send_file(file_path, mimetype='image/jpeg')
    else:
        return send_file(file_path)

# ============================================================================
# ROUTES - PAGES
# ============================================================================

@app.route('/')
def home():
    return send_file(os.path.join(PROJECT_ROOT, 'frontend', 'index.html'))

@app.route('/profile')
def profile():
    return send_file(os.path.join(PROJECT_ROOT, 'frontend', 'profile.html'))

@app.route('/test.html')
def test():
    return send_file(os.path.join(PROJECT_ROOT, 'frontend', 'test.html'))

# ============================================================================
# API - AUTHENTICATION
# ============================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                        (username, email, generate_password_hash(password)))
            conn.commit()
            user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            
            session['user_id'] = user_id
            session.permanent = True
            
            user = conn.execute('SELECT id, username, email, avatar, created_at FROM users WHERE id = ?',
                              (user_id,)).fetchone()
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'avatar': user[3],
                    'created_at': user[4]
                }
            })
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute('SELECT id, username, email, password_hash, avatar, created_at FROM users WHERE username = ?',
                          (username,)).fetchone()
        
        if user and check_password_hash(user[3], password):
            conn.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
            conn.commit()
            
            session['user_id'] = user[0]
            session.permanent = True
            
            conn.close()
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'avatar': user[4],
                    'created_at': user[5]
                }
            })
        else:
            conn.close()
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/api/me', methods=['GET'])
def api_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute('SELECT id, username, email, avatar, created_at FROM users WHERE id = ?',
                          (user_id,)).fetchone()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'avatar': user[3],
                    'created_at': user[4]
                }
            })
        return jsonify({'success': False, 'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# API - SCANNING
# ============================================================================

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Run WiFi scan with REAL networks"""
    print("\n" + "="*70)
    print("🎯 /api/scan ENDPOINT HIT!")
    print("="*70)
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print("="*70 + "\n")
    
    global network_threats
    
    user_id = session.get('user_id', 1)
    
    # Import real WiFi scanner
    try:
        from wifi_scanner import scan_real_networks
        print("📡 Scanning for REAL WiFi networks...")
        networks = scan_real_networks()
        
        if not networks:
            print("⚠️  No networks found, using fallback")
            # Fallback to at least show something
            networks = [{
                'ssid': 'No Networks Detected',
                'bssid': '00:00:00:00:00:00',
                'signal': -90,
                'signal_percent': 10,
                'threat_level': 0,
                'threat_name': 'SAFE',
                'channel': 1,
                'encryption': 'N/A',
                'is_zombie': False
            }]
    except Exception as e:
        print(f"❌ Error scanning networks: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback
        networks = [{
            'ssid': 'Scanner Error',
            'bssid': '00:00:00:00:00:00',
            'signal': -90,
            'signal_percent': 10,
            'threat_level': 0,
            'threat_name': 'SAFE',
            'channel': 1,
            'encryption': 'N/A',
            'is_zombie': False
        }]
    
    threats_count = len([n for n in networks if n['threat_level'] >= 3])
    
    # Store networks globally
    network_threats = networks
    
    # Overall alert
    if networks:
        max_threat = max([n['threat_level'] for n in networks])
        alert_name = ['NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][max_threat]
    else:
        max_threat = 0
        alert_name = 'NORMAL'
    
    # Create scan record
    scan = {
        'id': len(scans_storage) + 1,
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr,
        'alert_level': max_threat,
        'alert_name': alert_name,
        'confidence': round(random.uniform(0.88, 0.97), 2),
        'networks_found': len(networks),
        'threats_detected': threats_count,
        'networks': networks
    }
    
    scans_storage.append(scan)
    
    # Save to database
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''INSERT INTO scans (user_id, ip_address, alert_level, alert_name, 
                       confidence, networks_found, threats_detected) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (user_id, scan['ip_address'], scan['alert_level'], scan['alert_name'],
                     scan['confidence'], scan['networks_found'], scan['threats_detected']))
        conn.commit()
        conn.close()
    except:
        pass
    
    print(f"✓ Scan complete: {len(networks)} networks, {threats_count} threats")
    
    return jsonify({'success': True, 'result': scan})

@app.route('/api/networks', methods=['GET'])
def api_networks():
    """Get detected networks"""
    return jsonify({'success': True, 'networks': network_threats})

@app.route('/api/scans/stats', methods=['GET'])
def api_stats():
    """Get scan statistics"""
    user_id = session.get('user_id', 1)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        total = conn.execute('SELECT COUNT(*) FROM scans WHERE user_id = ?', (user_id,)).fetchone()[0]
        threats = conn.execute('SELECT COUNT(*) FROM scans WHERE user_id = ? AND alert_level >= 3',
                              (user_id,)).fetchone()[0]
        last = conn.execute('SELECT timestamp FROM scans WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
                           (user_id,)).fetchone()
        conn.close()
        
        # Add real-time data
        stats = {
            'total_scans': total + len(scans_storage),
            'threats_detected': threats,
            'last_scan': last[0] if last else None,
            'next_auto_scan': 3600,  # 1 hour in seconds
            'network_strength': random.randint(65, 95),
            'available_networks': len(network_threats),
            'active_threats': len([n for n in network_threats if n['threat_level'] >= 3])
        }
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scans/latest', methods=['GET'])
def api_latest():
    """Get latest scan"""
    if scans_storage:
        return jsonify({'success': True, 'scan': scans_storage[-1]})
    return jsonify({'success': False, 'error': 'No scans yet'}), 404

@app.route('/api/scans', methods=['GET'])
def api_scans():
    """Get scan history"""
    limit = request.args.get('limit', 10, type=int)
    recent = scans_storage[-limit:] if scans_storage else []
    return jsonify({'success': True, 'scans': list(reversed(recent))})

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" 🎮 ZOMBIE WIFI DETECTOR - CYBERPUNK EDITION")
    print(" 🤖 CyberSentry AI - Tarun, Shivam, Yash")
    print("="*70)
    print(f"\n📂 Project Root: {PROJECT_ROOT}")
    print(f"💾 Database: {DB_PATH}")
    
    init_db()
    print("✓ Database initialized")
    
    print("\n" + "="*70)
    print(" 🌐 SERVER ROUTES")
    print("="*70)
    print("\n📄 HTML Pages:")
    print("  • GET  / → Landing page")
    print("  • GET  /profile → Profile page")
    print("  • GET  /test.html → Test page")
    
    print("\n🔌 API Endpoints:")
    print("  • POST /api/register → Register user")
    print("  • POST /api/login → Login user")
    print("  • POST /api/logout → Logout user")
    print("  • GET  /api/me → Get current user")
    print("  • POST /api/scan → Run WiFi scan ⚡")
    print("  • GET  /api/networks → Get detected networks")
    print("  • GET  /api/scans/stats → Get statistics")
    print("  • GET  /api/scans/latest → Get latest scan")
    print("  • GET  /api/scans → Get scan history")
    
    print("\n📁 Static Files:")
    print("  • GET  /static/<path> → CSS, JS, images")
    
    print("\n" + "="*70)
    print(" 🚀 STARTING SERVER")
    print("="*70)
    print("  • http://localhost:5000/ → Cyberpunk Login")
    print("  • http://localhost:5000/test.html → Test Page")
    print("  • http://localhost:5000/profile → User Profile")
    
    print("\n💡 Features:")
    print("  • Glitch effects & particle systems")
    print("  • Real-time network scanning")
    print("  • Zombie WiFi threat detection")
    print("  • Cyberpunk aesthetics")
    
    print("\n" + "="*70)
    print("\nPress Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    # Print all registered routes
    print("🔍 Registered Flask Routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"  {methods:6s} {rule.rule}")
    print("\n" + "="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
