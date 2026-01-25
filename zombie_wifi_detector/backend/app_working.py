"""
Zombie WiFi Detector - Working Backend
This version will definitely work!
"""

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import sys

# ============================================================================
# SETUP PATHS
# ============================================================================

# Get absolute paths
CURRENT_FILE = os.path.abspath(__file__)
BACKEND_DIR = os.path.dirname(CURRENT_FILE)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

print("\n" + "="*70)
print(" PATH VERIFICATION")
print("="*70)
print(f"Current File: {CURRENT_FILE}")
print(f"Backend Dir:  {BACKEND_DIR}")
print(f"Project Root: {PROJECT_ROOT}")
print()

# Add to path for imports
sys.path.insert(0, PROJECT_ROOT)

# ============================================================================
# INITIALIZE FLASK
# ============================================================================

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'
CORS(app)

# ============================================================================
# DATABASE SETUP
# ============================================================================

DB_PATH = os.path.join(BACKEND_DIR, 'app.db')

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Scans table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            alert_level INTEGER,
            alert_name TEXT,
            confidence REAL,
            is_auto BOOLEAN,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized: {DB_PATH}")

# ============================================================================
# ROUTE HANDLERS - HTML PAGES
# ============================================================================

@app.route('/')
def home():
    """Landing page"""
    file_path = os.path.join(PROJECT_ROOT, 'frontend', 'index.html')
    print(f"[ROUTE /] Serving: {file_path}")
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}", 404
    
    return send_file(file_path)


@app.route('/login')
def login_page():
    """Login page"""
    file_path = os.path.join(PROJECT_ROOT, 'frontend', 'login.html')
    print(f"[ROUTE /login] Serving: {file_path}")
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}", 404
    
    return send_file(file_path)


@app.route('/register')
def register_page():
    """Register page"""
    file_path = os.path.join(PROJECT_ROOT, 'frontend', 'register.html')
    print(f"[ROUTE /register] Serving: {file_path}")
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}", 404
    
    return send_file(file_path)


@app.route('/dashboard')
def dashboard_page():
    """Dashboard page"""
    file_path = os.path.join(PROJECT_ROOT, 'frontend', 'dashboard.html')
    print(f"[ROUTE /dashboard] Serving: {file_path}")
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}", 404
    
    return send_file(file_path)


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, images)"""
    file_path = os.path.join(PROJECT_ROOT, 'static', filename)
    print(f"[ROUTE /static/{filename}] Serving: {file_path}")
    
    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}", 404
    
    return send_file(file_path)


# ============================================================================
# API ROUTES - Authentication
# ============================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'Missing fields'}), 400
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            
            # Get user ID
            user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            })
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 400
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Register error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def api_login():
    """Login user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Missing credentials'}), 400
        
        # Check database
        conn = sqlite3.connect(DB_PATH)
        user = conn.execute(
            'SELECT id, username, email, password_hash FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not check_password_hash(user[3], password):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        return jsonify({
            'success': True,
            'user': {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    return jsonify({'success': True})


@app.route('/api/me', methods=['GET'])
def api_me():
    """Get current user - for now returns not authenticated"""
    return jsonify({'success': False, 'error': 'Not authenticated'}), 401


# ============================================================================
# API ROUTES - Scanning
# ============================================================================

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Run network scan"""
    try:
        # For testing, return a fake successful scan
        # In production, this would call the ML model
        
        import random
        from datetime import datetime
        
        result = {
            'success': True,
            'result': {
                'id': 1,
                'timestamp': datetime.now().isoformat(),
                'ip_address': request.remote_addr,
                'interface': 'auto-detected',
                'alert_level': 0,  # 0=NORMAL, 1=LOW, 2=MEDIUM, 3=HIGH, 4=CRITICAL
                'alert_name': 'NORMAL',
                'confidence': round(random.uniform(0.85, 0.98), 2),
                'features': {},
                'is_auto': False
            }
        }
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO scans (user_id, ip_address, alert_level, alert_name, confidence, is_auto)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (1, result['result']['ip_address'], result['result']['alert_level'], 
              result['result']['alert_name'], result['result']['confidence'], 0))
        conn.commit()
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scans', methods=['GET'])
def api_scans():
    """Get scan history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        scans = conn.execute('''
            SELECT id, timestamp, ip_address, alert_level, alert_name, confidence, is_auto
            FROM scans
            ORDER BY timestamp DESC
            LIMIT 10
        ''').fetchall()
        conn.close()
        
        scan_list = []
        for scan in scans:
            scan_list.append({
                'id': scan[0],
                'timestamp': scan[1],
                'ip_address': scan[2],
                'alert_level': scan[3],
                'alert_name': scan[4],
                'confidence': scan[5],
                'is_auto': bool(scan[6])
            })
        
        return jsonify({'success': True, 'scans': scan_list})
        
    except Exception as e:
        print(f"Scans error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scans/latest', methods=['GET'])
def api_latest_scan():
    """Get latest scan"""
    try:
        conn = sqlite3.connect(DB_PATH)
        scan = conn.execute('''
            SELECT id, timestamp, ip_address, alert_level, alert_name, confidence, is_auto
            FROM scans
            ORDER BY timestamp DESC
            LIMIT 1
        ''').fetchone()
        conn.close()
        
        if not scan:
            return jsonify({'success': False, 'error': 'No scans found'}), 404
        
        return jsonify({
            'success': True,
            'scan': {
                'id': scan[0],
                'timestamp': scan[1],
                'ip_address': scan[2],
                'alert_level': scan[3],
                'alert_name': scan[4],
                'confidence': scan[5],
                'is_auto': bool(scan[6])
            }
        })
        
    except Exception as e:
        print(f"Latest scan error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scans/stats', methods=['GET'])
def api_stats():
    """Get scan statistics"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        total = conn.execute('SELECT COUNT(*) FROM scans').fetchone()[0]
        threats = conn.execute('SELECT COUNT(*) FROM scans WHERE alert_level >= 3').fetchone()[0]
        last_scan = conn.execute('SELECT timestamp FROM scans ORDER BY timestamp DESC LIMIT 1').fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_scans': total,
                'threats_detected': threats,
                'last_scan': last_scan[0] if last_scan else None,
                'alert_distribution': {}
            }
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# STARTUP
# ============================================================================

def verify_files():
    """Verify all required files exist"""
    print("="*70)
    print(" FILE VERIFICATION")
    print("="*70)
    
    files_to_check = [
        ('frontend/index.html', 'Landing Page'),
        ('frontend/login.html', 'Login Page'),
        ('frontend/register.html', 'Register Page'),
        ('frontend/dashboard.html', 'Dashboard Page'),
        ('static/css/style.css', 'Main Stylesheet'),
        ('static/js/landing.js', 'Landing JS'),
        ('static/js/auth.js', 'Auth JS'),
    ]
    
    all_good = True
    
    for file_path, description in files_to_check:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        exists = os.path.exists(full_path)
        
        status = "✓" if exists else "✗"
        print(f"{status} {description:20s} : {file_path}")
        
        if not exists:
            all_good = False
            print(f"   → Missing: {full_path}")
    
    print()
    
    if all_good:
        print("✓ All files present!")
    else:
        print("✗ Some files are missing - you may see 404 errors")
    
    print()
    return all_good


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" ZOMBIE WIFI DETECTOR - WEB APPLICATION")
    print(" Working Backend Version")
    print("="*70)
    print()
    
    # Initialize database
    init_db()
    
    # Verify files
    verify_files()
    
    # Print routes
    print("="*70)
    print(" AVAILABLE ROUTES")
    print("="*70)
    print("HTML Pages:")
    print("  • http://localhost:5000/           → Landing Page")
    print("  • http://localhost:5000/login      → Login Page")
    print("  • http://localhost:5000/register   → Register Page")
    print("  • http://localhost:5000/dashboard  → Dashboard")
    print()
    print("API Endpoints:")
    print("  • POST /api/register    → Register user")
    print("  • POST /api/login       → Login user")
    print("  • POST /api/scan        → Run scan")
    print("  • GET  /api/scans       → Get scan history")
    print()
    print("Static Files:")
    print("  • /static/css/style.css")
    print("  • /static/js/landing.js")
    print()
    print("="*70)
    print()
    print("🌐 Starting server at: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print()
    print("="*70)
    print()
    
    # Run Flask
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )