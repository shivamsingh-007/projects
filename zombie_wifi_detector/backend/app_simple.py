"""
Zombie WiFi Detector - Simple No-Login Version
Access everything directly - no authentication required
"""

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import os
import random
from datetime import datetime

# Paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

app = Flask(__name__)
CORS(app)

print(f"\n{'='*70}")
print(f" PROJECT PATHS")
print(f"{'='*70}")
print(f"Backend:  {BACKEND_DIR}")
print(f"Root:     {PROJECT_ROOT}")
print(f"{'='*70}\n")

# ============================================================================
# STATIC FILES
# ============================================================================

@app.route('/static/css/<filename>')
def serve_css(filename):
    path = os.path.join(PROJECT_ROOT, 'static', 'css', filename)
    return send_file(path, mimetype='text/css')

@app.route('/static/js/<filename>')
def serve_js(filename):
    path = os.path.join(PROJECT_ROOT, 'static', 'js', filename)
    return send_file(path, mimetype='application/javascript')

@app.route('/static/<path:filepath>')
def serve_static(filepath):
    path = os.path.join(PROJECT_ROOT, 'static', filepath)
    return send_file(path)

# ============================================================================
# HTML PAGES - ALL ACCESSIBLE
# ============================================================================

@app.route('/')
def home():
    """Landing page with Get Started button"""
    path = os.path.join(PROJECT_ROOT, 'frontend', 'index.html')
    return send_file(path)

@app.route('/dashboard')
def dashboard():
    """Dashboard - NO LOGIN REQUIRED"""
    path = os.path.join(PROJECT_ROOT, 'frontend', 'dashboard.html')
    return send_file(path)

@app.route('/login')
def login_page():
    """Login page (optional)"""
    path = os.path.join(PROJECT_ROOT, 'frontend', 'login.html')
    return send_file(path)

@app.route('/register')
def register_page():
    """Register page (optional)"""
    path = os.path.join(PROJECT_ROOT, 'frontend', 'register.html')
    return send_file(path)

# ============================================================================
# API ENDPOINTS - MOCK DATA (NO DATABASE)
# ============================================================================

# Store scans in memory (resets when server restarts)
scans_data = []

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Run a scan - returns mock data"""
    
    # Create fake scan result
    scan = {
        'id': len(scans_data) + 1,
        'timestamp': datetime.now().isoformat(),
        'ip_address': request.remote_addr,
        'interface': 'WiFi',
        'alert_level': random.choice([0, 0, 0, 1, 2]),  # Mostly NORMAL
        'alert_name': '',
        'confidence': round(random.uniform(0.88, 0.97), 2),
        'features': {},
        'is_auto': False
    }
    
    # Set alert name based on level
    alert_names = ['NORMAL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    scan['alert_name'] = alert_names[scan['alert_level']]
    
    # Save to memory
    scans_data.append(scan)
    
    return jsonify({'success': True, 'result': scan})


@app.route('/api/scans', methods=['GET'])
def api_scans():
    """Get scan history"""
    # Return last 10 scans
    recent = scans_data[-10:] if scans_data else []
    return jsonify({'success': True, 'scans': list(reversed(recent))})


@app.route('/api/scans/latest', methods=['GET'])
def api_latest():
    """Get latest scan"""
    if scans_data:
        return jsonify({'success': True, 'scan': scans_data[-1]})
    else:
        return jsonify({'success': False, 'error': 'No scans yet'}), 404


@app.route('/api/scans/stats', methods=['GET'])
def api_stats():
    """Get statistics"""
    total = len(scans_data)
    threats = len([s for s in scans_data if s['alert_level'] >= 3])
    last_scan = scans_data[-1]['timestamp'] if scans_data else None
    
    # Count by alert type
    distribution = {}
    for scan in scans_data:
        name = scan['alert_name']
        distribution[name] = distribution.get(name, 0) + 1
    
    return jsonify({
        'success': True,
        'stats': {
            'total_scans': total,
            'threats_detected': threats,
            'last_scan': last_scan,
            'alert_distribution': distribution
        }
    })


@app.route('/api/me', methods=['GET'])
def api_me():
    """Get current user - always returns success (no auth)"""
    return jsonify({
        'success': True,
        'user': {
            'id': 1,
            'username': 'demo_user',
            'email': 'demo@example.com'
        }
    })


@app.route('/api/register', methods=['POST'])
def api_register():
    """Mock registration - always succeeds"""
    data = request.get_json()
    return jsonify({
        'success': True,
        'user': {
            'id': 1,
            'username': data.get('username', 'user'),
            'email': data.get('email', 'user@example.com')
        }
    })


@app.route('/api/login', methods=['POST'])
def api_login():
    """Mock login - always succeeds"""
    data = request.get_json()
    return jsonify({
        'success': True,
        'user': {
            'id': 1,
            'username': data.get('username', 'user'),
            'email': 'user@example.com'
        }
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout"""
    return jsonify({'success': True})

# ============================================================================
# STARTUP
# ============================================================================

if __name__ == '__main__':
    print(f"{'='*70}")
    print(f" ZOMBIE WIFI DETECTOR - SIMPLE VERSION")
    print(f" No authentication required - direct access")
    print(f"{'='*70}\n")
    
    # Check files
    files_to_check = [
        ('frontend/index.html', 'Landing Page'),
        ('frontend/dashboard.html', 'Dashboard'),
        ('static/css/style.css', 'Stylesheet'),
        ('static/js/landing.js', 'JavaScript'),
    ]
    
    print("Checking files:")
    all_good = True
    for file, desc in files_to_check:
        path = os.path.join(PROJECT_ROOT, file)
        exists = os.path.exists(path)
        status = "✓" if exists else "✗"
        
        if exists:
            size = os.path.getsize(path)
            print(f"  {status} {desc:20s} ({size:,} bytes)")
        else:
            print(f"  {status} {desc:20s} MISSING!")
            all_good = False
    
    print(f"\n{'='*70}")
    print(f" AVAILABLE PAGES")
    print(f"{'='*70}")
    print(f"  • http://localhost:5000/           → Landing Page")
    print(f"  • http://localhost:5000/dashboard  → Dashboard (NO LOGIN NEEDED!)")
    print(f"  • http://localhost:5000/login      → Login (optional)")
    print(f"  • http://localhost:5000/register   → Register (optional)")
    print(f"\n{'='*70}")
    print(f"\n🌐 Server starting at: http://localhost:5000")
    print(f"\n💡 TIP: Go directly to /dashboard to use the app!")
    print(f"\nPress Ctrl+C to stop\n")
    print(f"{'='*70}\n")
    
    if not all_good:
        print("⚠️  WARNING: Some files are missing!")
        print("   The app may not work correctly.\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
