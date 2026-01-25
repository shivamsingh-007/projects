# 🌐 Zombie WiFi Detector - Web Application Setup Guide

## ✨ What You're Getting

A beautiful, fully-functional web application with:
- ✅ User registration & authentication
- ✅ Automatic network detection
- ✅ Hourly automatic scans  
- ✅ Real-time threat detection
- ✅ Beautiful modern dashboard
- ✅ Scan history & statistics
- ✅ One-click manual scanning

## 📋 Quick Start (5 Minutes)

### Step 1: Install Backend Dependencies

```bash
cd zombie_wifi_detector
pip install Flask Flask-CORS Flask-SQLAlchemy Werkzeug
```

### Step 2: Run the Web Server

```bash
# Run as Administrator (Windows) or with sudo (Mac/Linux)
cd backend
python app.py
```

You'll see:
```
🌐 Server running at: http://localhost:5000
📊 Open your browser and go to: http://localhost:5000
```

### Step 3: Open Your Browser

Go to: **http://localhost:5000**

### Step 4: Register Your Account

1. Click "Get Started" or "Register"
2. Fill in:
   - Username
   - Email  
   - Password
3. Click "Create Account"

### Step 5: Start Protecting!

After registration, you'll see your dashboard where you can:
- ✅ View current network status
- ✅ Click "Scan Now" for immediate check
- ✅ View scan history
- ✅ Get automatic hourly scans

## 🎨 Features

### 1. Landing Page
- Beautiful hero section
- Feature showcase
- How it works explanation
- Call-to-action buttons

### 2. Authentication
- **Register**: Create your account
- **Login**: Secure session management
- **Password**: Show/hide toggle, strength indicator

### 3. Dashboard
- **Network Status**: Real-time threat level
- **Statistics**: Total scans, threats detected
- **Manual Scan**: One-click checking
- **Auto Scan**: Hourly automatic protection
- **Scan History**: View past detections
- **Alert System**: 5 levels (Normal → Critical)

## 🔧 How It Works

### Backend (Flask API)

**File**: `backend/app.py`

**Endpoints**:
```
POST /api/register      - Create new account
POST /api/login         - User authentication
POST /api/logout        - End session
GET  /api/me            - Get current user
POST /api/scan          - Run manual scan
GET  /api/scans         - Get scan history
GET  /api/scans/latest  - Get most recent scan
GET  /api/scans/stats   - Get statistics
GET  /api/interfaces    - List network interfaces
```

**Database** (SQLite):
- **Users**: username, email, password_hash
- **Scans**: timestamp, alert_level, confidence, features
- **Settings**: auto_scan_enabled, scan_interval

**Auto-Scan Worker**:
- Background thread
- Checks every 5 minutes
- Scans users with auto-scan enabled
- Respects scan_interval (default 1 hour)

### Frontend (HTML/CSS/JS)

**Pages**:
- `index.html` - Landing page
- `login.html` - Login form
- `register.html` - Registration form
- `dashboard.html` - Main dashboard

**Styling**: `static/css/style.css`
- Modern dark theme
- Responsive design
- Smooth animations
- Beautiful gradients

**JavaScript**: Handles API calls, updates UI, manages state

## 📱 User Flow

```
1. Visit http://localhost:5000
   ↓
2. Click "Get Started" → Register
   ↓
3. Fill form → Create Account
   ↓
4. Auto-redirect to Dashboard
   ↓
5. System automatically:
   - Detects network interface
   - Gets IP address
   - Starts monitoring
   ↓
6. User can:
   - View status
   - Click "Scan Now"
   - View history
```

## 🔒 Security Features

- ✅ Password hashing (Werkzeug)
- ✅ Session management
- ✅ CORS protection
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ XSS protection
- ✅ Secure cookies

## ⚙️ Configuration

### Default Settings

```python
# Auto-scan enabled by default
auto_scan_enabled = True

# Scan interval (1 hour)
scan_interval = 3600

# Session lifetime (7 days)
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
```

### Change Scan Interval

In `backend/app.py`, find:
```python
scan_interval = db.Column(db.Integer, default=3600)
```

Change to:
- 1800 = 30 minutes
- 7200 = 2 hours
- 21600 = 6 hours

## 🎯 How Network Detection Works

### Automatic IP Detection

```python
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ['HTTP_X_FORWARDED_FOR']
    return request.environ.get('REMOTE_ADDR')
```

### Automatic Interface Detection

```python
def get_network_interface():
    from scapy.all import get_if_list
    interfaces = get_if_list()
    # Filter out loopback
    return interfaces[0]  # First active interface
```

### Permission Request

The system automatically requests permission when:
1. User clicks "Scan Now"
2. Auto-scan triggers
3. System needs network access

**No manual configuration needed!**

## 🎨 Dashboard Features

### Status Card

Shows current threat level:
- 🟢 **NORMAL** - Network is safe
- 🔵 **LOW** - Minor anomalies
- 🟡 **MEDIUM** - Suspicious activity
- 🟠 **HIGH** - Likely threat
- 🔴 **CRITICAL** - Immediate action needed

### Statistics Cards

1. **Total Scans** - Number of checks performed
2. **Threats Detected** - High/Critical alerts found
3. **Last Scan** - Time since last check
4. **Next Auto Scan** - Countdown to next automatic check

### Recent Scans List

- Shows last 5 scans
- Alert level badges
- Confidence percentage
- Auto vs Manual indicator
- Timestamp

## 🚀 Advanced Features

### Custom Network Interface

If auto-detection fails, users can specify:

In dashboard settings (coming soon):
```javascript
await fetch('/api/settings', {
    method: 'PUT',
    body: JSON.stringify({
        network_interface: '\\Device\\NPF_{YOUR-GUID}'
    })
});
```

### Enable/Disable Auto-Scan

```javascript
await fetch('/api/settings', {
    method: 'PUT',
    body: JSON.stringify({
        auto_scan_enabled: false  // Turn off auto-scan
    })
});
```

## 📊 Database Schema

```sql
-- Users table
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    created_at DATETIME,
    last_login DATETIME
);

-- Scans table
CREATE TABLE scan (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    timestamp DATETIME,
    ip_address VARCHAR(50),
    interface VARCHAR(200),
    alert_level INTEGER,
    alert_name VARCHAR(20),
    confidence FLOAT,
    features TEXT,  -- JSON
    is_auto BOOLEAN,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Settings table
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    auto_scan_enabled BOOLEAN,
    scan_interval INTEGER,
    network_interface VARCHAR(200),
    last_auto_scan DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

## 🐛 Troubleshooting

### "Permission Denied" Error

**Solution**: Run as Administrator (Windows) or with sudo (Mac/Linux)

```bash
# Windows (Run CMD as Administrator)
cd backend
python app.py

# Mac/Linux
cd backend
sudo python app.py
```

### "Model not found" Error

**Solution**: Run setup first

```bash
cd ..
python main.py setup
```

### Port 5000 Already in Use

**Solution**: Change port in `app.py`

Find:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Change to:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

Then visit: http://localhost:5001

### Database Errors

**Solution**: Delete and recreate database

```bash
cd backend
rm zombie_wifi.db
python app.py  # Will auto-create new database
```

## 🎨 Customization

### Change Theme Colors

Edit `static/css/style.css`:

```css
:root {
    --primary: #6366f1;     /* Change to your color */
    --secondary: #ec4899;   
    --success: #10b981;
    --danger: #ef4444;
}
```

### Change Logo

Replace icon in navigation:
```html
<i class="fas fa-shield-virus"></i>
<!-- Change to any Font Awesome icon -->
```

### Modify Scan Duration

In `backend/app.py`, find:
```python
result = detector.capture_and_analyze(duration=30)
```

Change `30` to desired seconds (60, 120, 300, etc.)

## 📈 Scaling & Production

### Use Production Server

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Use PostgreSQL (Instead of SQLite)

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@localhost/zombiewifi'
```

### Enable HTTPS

Use nginx reverse proxy with SSL certificate

## ✅ Checklist

Before launching:

- [ ] Backend dependencies installed
- [ ] Model trained (`python main.py setup`)
- [ ] Server running (`python backend/app.py`)
- [ ] Browser opened to http://localhost:5000
- [ ] Account registered
- [ ] First scan completed

## 🎉 You're Done!

Your beautiful web application is ready to protect networks!

**Features Working**:
- ✅ User registration/login
- ✅ Automatic IP detection
- ✅ One-click scanning
- ✅ Hourly auto-scans
- ✅ Beautiful dashboard
- ✅ Real-time alerts
- ✅ Scan history

**Next Steps**:
1. Share with friends/family
2. Deploy to cloud (AWS, Heroku, DigitalOcean)
3. Add email notifications
4. Mobile app integration

---

**Need Help?** Check the troubleshooting section or run:
```bash
python backend/app.py --help
```

**Enjoy your AI-powered network security system!** 🔒
