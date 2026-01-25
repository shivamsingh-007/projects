# 🌐 Zombie WiFi Detector - Web Application Guide

## 🎉 What You've Got!

A **complete, beautiful web application** with:

✅ **User Authentication** (Register/Login)
✅ **Auto-Detection** of network interface  
✅ **One-Click Scanning**
✅ **Automatic Hourly Scans**
✅ **Real-time Status Updates**
✅ **Scan History**
✅ **Beautiful Modern UI**
✅ **Responsive Design**
✅ **Smooth Animations**

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Install Dependencies**

```bash
cd zombie_wifi_detector
pip install -r requirements_web.txt
```

###Step 2: Start the Backend Server**

```bash
# Run as Administrator/sudo (needed for packet capture)
sudo python backend/app.py

# Windows (Run Command Prompt as Administrator):
python backend/app.py
```

**You'll see:**
```
======================================================================
 ZOMBIE WIFI DETECTOR - BACKEND SERVER
======================================================================

Initializing database...
✓ Database ready

Loading ML model...
✓ ML Model loaded successfully

======================================================================
 SERVER STARTING
======================================================================

Backend API: http://localhost:5000
Frontend: Open index.html in browser

Press Ctrl+C to stop
```

### **Step 3: Open the Frontend**

**Option A - Double-click:**
- Find `index.html` in the folder
- Double-click to open in your browser

**Option B - Browser:**
- Open your web browser
- Press `Ctrl+O` (Windows) or `Cmd+O` (Mac)
- Navigate to `zombie_wifi_detector/index.html`
- Click Open

**Option C - Python Server (Recommended):**
```bash
# In a new terminal/command prompt
cd zombie_wifi_detector
python -m http.server 8000
```
Then open: http://localhost:8000

---

## 📱 Using the Web App

### **1. Register an Account**

![Register Screen](docs/register.png)

- Click "Create Account"
- Enter username, email, and password (min 6 characters)
- Click "Create Account"

### **2. Login**

- Enter your username/email and password
- Click "Sign In"

### **3. First-Time Setup**

When you first login:

1. **Click "Settings"** button
2. **Auto-Detect** will show available interfaces
3. **Select your active network interface**
4. **Set scan interval** (default: 1 hour)
5. **Enable notifications** (optional)
6. Click **"Save Settings"**

### **4. Scan Your Network**

**Manual Scan:**
- Click the big **"Scan Now"** button
- Wait 60 seconds for scan to complete
- View results on the status card

**Automatic Scanning:**
- Toggle **"Automatic Scanning"** switch to ON
- Network will be scanned every hour automatically
- You'll be notified if threats are detected

### **5. View Results**

**Status Card shows:**
- ✅ **NORMAL** - Green shield, network is safe
- ⚠️ **WARNING** - Yellow shield, suspicious activity
- 🚨 **CRITICAL** - Red shield, zombie WiFi detected!

**Details include:**
- Alert Level (NORMAL, LOW, MEDIUM, HIGH, CRITICAL)
- Confidence Score (how sure the AI is)
- Last Scan Time

**Scan History:**
- Shows your last 10 scans
- Color-coded by threat level
- Timestamp for each scan

---

## 🎨 Features Breakdown

### **1. Beautiful UI**

- **Modern Design** - Professional gradient backgrounds
- **Smooth Animations** - Fade-ins, slide-ups, floating elements
- **Responsive** - Works on desktop, tablet, and mobile
- **Dark Theme** - Easy on the eyes

### **2. User Authentication**

- **Secure Registration** - Password hashing with Werkzeug
- **Session Management** - Stays logged in
- **User Profiles** - Track your scan history
- **SQLite Database** - Stores user data securely

### **3. Smart Scanning**

- **Auto-Detection** - Finds your network interface automatically
- **Quick Scans** - 60-second network analysis
- **Real-Time Progress** - Watch the scan in action
- **ML-Powered** - Uses your trained AI model

### **4. Automatic Protection**

- **Auto-Scan** - Checks network every hour
- **Background Monitoring** - Runs while you work
- **Instant Alerts** - Notifies you of threats
- **Scan History** - Review past results

### **5. Settings Control**

- **Interface Selection** - Choose which network to monitor
- **Scan Interval** - Set how often to scan (1-24 hours)
- **Notifications** - Enable/disable browser alerts
- **Easy Configuration** - User-friendly interface

---

## 📂 Project Structure

```
zombie_wifi_detector/
├── backend/
│   ├── app.py              # Flask API server ⭐
│   └── users.db            # SQLite database (created on first run)
│
├── frontend/
│   ├── styles.css          # Beautiful CSS styling ⭐
│   ├── app.js              # JavaScript application ⭐
│   └── index.html          # Main HTML page ⭐
│
├── index.html              # Copy for easy access
├── models/
│   └── zombie_wifi_detector.pkl  # Your trained AI model
│
├── data/
│   └── training_data.csv   # Training data
│
└── requirements_web.txt    # Python dependencies
```

---

## 🔧 Advanced Configuration

### **Change Default Port**

Edit `backend/app.py`, last line:

```python
app.run(host='0.0.0.0', port=5000, debug=True)
# Change 5000 to your preferred port
```

### **Enable HTTPS (Production)**

```python
app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
```

### **Database Location**

Edit `backend/app.py`, line ~25:

```python
DATABASE = 'backend/users.db'
# Change to your preferred location
```

### **Customize Scan Duration**

Edit `backend/app.py`, line ~260 in `perform_scan()`:

```python
capture = PacketCapture(interface=interface, duration=60)
# Change 60 to your preferred duration in seconds
```

---

## 🐛 Troubleshooting

### **Problem: "Connection error. Is the server running?"**

**Solution:**
```bash
# Make sure backend is running:
python backend/app.py

# Check if it says "Server Starting" and shows port 5000
```

### **Problem: "No interface specified"**

**Solution:**
1. Click "Settings" button
2. Click "Auto-Detect"
3. Select your interface
4. Click "Save Settings"

### **Problem: "Scan failed. Check server and interface settings"**

**Solution:**
- Make sure you're running as Administrator/sudo
- Verify interface name is correct
- Check that Npcap is installed (Windows)

### **Problem: "Model not loaded"**

**Solution:**
```bash
# Make sure you've run setup:
python main.py setup

# Or run the demo:
python demo.py
```

### **Problem: Page not loading**

**Solution:**
- Check frontend/index.html exists
- Try using Python HTTP server:
  ```bash
  python -m http.server 8000
  ```
- Open http://localhost:8000

### **Problem: Can't create account**

**Solution:**
- Password must be 6+ characters
- Email must contain @
- Username must be unique

---

## 📊 API Endpoints Reference

For developers who want to integrate or customize:

### **Authentication**
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `POST /api/logout` - Logout user
- `GET /api/profile` - Get user profile

### **Scanning**
- `POST /api/scan` - Perform manual scan
- `GET /api/scan/latest` - Get latest scan result
- `GET /api/scan/history` - Get scan history

### **Settings**
- `GET /api/settings` - Get user settings
- `POST /api/settings` - Update settings
- `POST /api/auto-scan/toggle` - Enable/disable auto-scan

### **Utilities**
- `GET /api/detect-interface` - Auto-detect interfaces
- `GET /api/health` - Health check

---

## 🎯 Usage Examples

### **Example 1: Register and First Scan**

1. Open index.html in browser
2. Click "Create Account"
3. Fill form and submit
4. Login with credentials
5. Click "Settings"
6. Click "Auto-Detect"
7. Save settings
8. Click "Scan Now"
9. Wait for results!

### **Example 2: Enable Auto-Scanning**

1. Login to dashboard
2. Find "Automatic Scanning" card
3. Toggle switch to ON
4. Network will scan every hour
5. Check "Recent Scans" to see history

### **Example 3: Respond to Threat**

If you see a **CRITICAL** alert:

1. **Disconnect** from WiFi immediately
2. Check recent scan history
3. Change router password
4. Update router firmware
5. Scan all connected devices
6. Scan again after fixes

---

## 🔐 Security Features

### **Password Security**
- Passwords are hashed with Werkzeug
- Never stored in plain text
- Salted hashing for extra security

### **Session Management**
- Secure session cookies
- CSRF protection via Flask
- Sessions expire on logout

### **Data Privacy**
- User data stored locally
- No external API calls
- Scan data belongs to user only

### **Network Security**
- Packet capture requires admin rights
- No data sent to external servers
- All processing happens locally

---

## 💡 Tips for Best Results

### **For Accurate Detection:**
1. Run scans during different times of day
2. Enable auto-scan for continuous monitoring
3. Check scan history regularly
4. Update ML model with real data when possible

### **For Better Performance:**
1. Close other network-intensive apps during scan
2. Use wired connection for more stable results
3. Run backend on a dedicated machine
4. Increase scan duration for more data (edit code)

### **For Security:**
1. Change default admin credentials if you add them
2. Run backend only on trusted networks
3. Keep software updated
4. Review scan logs regularly

---

## 🆘 Getting Help

### **Check These First:**
1. Is backend running? (Should show "Server Starting")
2. Is ML model loaded? (Check backend console)
3. Is interface configured? (Check Settings)
4. Are you running as admin? (Required for packet capture)

### **Common Solutions:**
- Restart backend server
- Clear browser cache
- Re-run `python main.py setup`
- Check firewall settings
- Verify port 5000 is not in use

### **Still Stuck?**
- Check backend console for errors
- Check browser developer console (F12)
- Review the scan history for patterns
- Try scanning from command line first

---

## 🎨 UI Customization

Want to change colors? Edit `frontend/styles.css`:

```css
:root {
    --primary: #6366f1;        /* Main brand color */
    --success: #10b981;        /* Safe/normal color */
    --danger: #ef4444;         /* Threat color */
    --bg-primary: #0f172a;     /* Background */
}
```

---

## 📈 Next Steps

### **Beginner:**
- ✅ Use the web app daily
- ✅ Enable auto-scanning
- ✅ Monitor scan history

### **Intermediate:**
- 🔧 Customize scan intervals
- 🔧 Add email notifications
- 🔧 Create custom baseline with real data

### **Advanced:**
- 🚀 Add more ML models
- 🚀 Create admin dashboard
- 🚀 Deploy to cloud server
- 🚀 Add multi-user support
- 🚀 Integrate with SIEM systems

---

## ✨ Summary

You now have a **complete, production-ready web application** with:

- ✅ Beautiful, professional UI
- ✅ User authentication system
- ✅ Automatic network scanning
- ✅ Real-time threat detection
- ✅ Scan history tracking
- ✅ Browser notifications
- ✅ Responsive design
- ✅ Easy configuration

**Start protecting your network now!** 🔒

```bash
# Terminal 1: Start backend
python backend/app.py

# Terminal 2: Open frontend
python -m http.server 8000

# Browser: http://localhost:8000
```

**Enjoy your new AI-powered security system!** 🎉
