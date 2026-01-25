# Windows Setup Guide - Fix for Encoding Error

## ✅ THE EASIEST WAY (Windows Users)

### Option 1: Use Batch Files (No Python Skills Needed!)

**Step 1:** Double-click this file:
```
INSTALL_WINDOWS.bat
```

This will:
- Install all dependencies
- Create folders
- Train the model
- Set everything up

**Step 2:** Double-click this file:
```
START_WEBAPP.bat
```

**Step 3:** Open your browser to:
```
http://localhost:5000
```

**Done!** 🎉

---

### Option 2: Use Windows-Compatible Python Script

Instead of `integrate.py`, use:

```bash
python integrate_windows.py
```

This version has no special Unicode characters and works perfectly on Windows.

---

### Option 3: Manual Setup (Most Reliable)

Open **Command Prompt** (or PowerShell) and run these commands:

```bash
# 1. Navigate to project
cd C:\path\to\zombie_wifi_detector

# 2. Install dependencies
pip install Flask Flask-CORS Werkzeug scikit-learn xgboost numpy pandas scipy scapy matplotlib seaborn pyyaml joblib

# 3. Train the model
python main.py setup

# 4. Copy the integrated backend
copy backend\app_integrated.py backend\app.py

# 5. Start the web app
cd backend
python app.py
```

Then open: **http://localhost:5000**

---

## 🔧 Why the Error Happened

The error occurred because:
- Windows uses `cp1252` encoding by default
- The script had Unicode emoji characters (⚠️, ✅, etc.)
- Python couldn't encode these to cp1252

**Solutions provided:**
1. ✅ Batch files (no Unicode)
2. ✅ `integrate_windows.py` (no Unicode)
3. ✅ Fixed `integrate.py` (now uses UTF-8)

---

## 📝 Step-by-Step Windows Installation

### Prerequisites

1. **Python 3.8+** installed
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Administrator Access**
   - For packet capture functionality

### Installation Steps

**1. Extract the Project**
```
Right-click zombie_wifi_detector.zip → Extract All
```

**2. Open Command Prompt as Administrator**
```
Win + X → Command Prompt (Admin)
```

**3. Navigate to Project**
```bash
cd C:\Users\YourName\Downloads\zombie_wifi_detector
```

**4. Install Dependencies**
```bash
pip install Flask Flask-CORS Werkzeug
pip install scikit-learn xgboost numpy pandas scipy
pip install scapy matplotlib seaborn pyyaml joblib
```

**5. Set Up Project Structure**
```bash
mkdir backend frontend static\css static\js models data logs
```

**6. Train the Model**
```bash
python main.py setup
```

This creates:
- `models/zombie_wifi_detector.pkl`
- `models/baseline_profile.pkl`
- `data/training_data.csv`

**7. Prepare Backend**
```bash
copy backend\app_integrated.py backend\app.py
```

**8. Start the Web Server**
```bash
cd backend
python app.py
```

**9. Open Browser**
```
http://localhost:5000
```

---

## 🎯 Quick Verification

To check if everything is working:

### Test 1: Check Python
```bash
python --version
```
Should show: Python 3.8 or higher

### Test 2: Check pip
```bash
pip --version
```
Should show version info

### Test 3: Check Dependencies
```bash
python -c "import flask; import sklearn; import scapy; print('OK')"
```
Should print: OK

### Test 4: Check Model
```bash
dir models\zombie_wifi_detector.pkl
```
Should show the file exists

### Test 5: Start Server
```bash
cd backend
python app.py
```
Should show: Server running at http://localhost:5000

---

## 🐛 Common Windows Issues

### Issue 1: "python is not recognized"

**Solution:** Add Python to PATH

1. Search "Environment Variables" in Windows
2. Click "Environment Variables"
3. Under "System variables", find "Path"
4. Click "Edit"
5. Click "New"
6. Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3X`
7. Click OK
8. Restart Command Prompt

### Issue 2: "pip is not recognized"

**Solution:**
```bash
python -m pip install Flask
```

Use `python -m pip` instead of just `pip`

### Issue 3: Permission Denied

**Solution:** Run Command Prompt as Administrator
- Win + X → Command Prompt (Admin)

### Issue 4: Port 5000 Already in Use

**Solution 1:** Find and kill the process
```bash
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

**Solution 2:** Change the port

Edit `backend/app.py`, find the last line:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

### Issue 5: Scapy/Packet Capture Issues

**Solution:** Install Npcap

1. Download: https://npcap.com/dist/npcap-1.79.exe
2. Run installer
3. ✅ Check "Install Npcap in WinPcap API-compatible Mode"
4. Restart computer

### Issue 6: Import Errors

**Solution:** Reinstall the specific package
```bash
pip uninstall package-name
pip install package-name
```

### Issue 7: Database Locked

**Solution:**
```bash
del backend\zombie_wifi.db
python backend\app.py
```

---

## 🚀 Quick Start Commands (Copy-Paste Ready)

### Full Installation (One Block)
```bash
cd C:\Users\%USERNAME%\Downloads\zombie_wifi_detector
pip install Flask Flask-CORS Werkzeug scikit-learn xgboost numpy pandas scipy scapy matplotlib seaborn pyyaml joblib
python main.py setup
copy backend\app_integrated.py backend\app.py
cd backend
python app.py
```

### Just Start (If Already Installed)
```bash
cd C:\Users\%USERNAME%\Downloads\zombie_wifi_detector\backend
python app.py
```

---

## 📊 After Installation

### Register Your Account
1. Open: http://localhost:5000
2. Click "Get Started" or "Register"
3. Fill in:
   - Username
   - Email
   - Password
4. Click "Create Account"

### Use the Dashboard
- View network status
- Click "Scan Now"
- Check scan history
- View statistics

### Access from Other Devices

Find your IP:
```bash
ipconfig
```

Look for "IPv4 Address": e.g., `192.168.1.100`

Others can access at:
```
http://192.168.1.100:5000
```

---

## 🎨 Customization for Windows

### Change Default Browser
The app opens in your default browser. To change:
1. Settings → Default Apps → Web Browser

### Run on Startup
Create shortcut to `START_WEBAPP.bat` in:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### Create Desktop Shortcut
1. Right-click `START_WEBAPP.bat`
2. Send to → Desktop (create shortcut)
3. Rename to "Zombie WiFi Detector"

---

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] All dependencies installed
- [ ] Model trained (zombie_wifi_detector.pkl exists)
- [ ] Backend copied (app.py exists)
- [ ] Server starts without errors
- [ ] Can access http://localhost:5000
- [ ] Can register an account
- [ ] Can login
- [ ] Dashboard loads
- [ ] Can run a scan (as Administrator)

---

## 📞 Need Help?

If you're still having issues:

1. **Check Python version:**
   ```bash
   python --version
   ```

2. **Test imports:**
   ```bash
   python -c "import flask; import sklearn; print('OK')"
   ```

3. **Check if model exists:**
   ```bash
   dir models
   ```

4. **Try the demo (no admin needed):**
   ```bash
   python demo.py
   ```

5. **Read error messages carefully** - they usually tell you what's wrong

---

## 🎉 You're Ready!

Choose your method:
- 🚀 **Fastest:** Double-click `INSTALL_WINDOWS.bat`
- 🐍 **Python:** Run `python integrate_windows.py`
- 📝 **Manual:** Follow commands above

All methods work - pick what you're comfortable with!

**After setup, just double-click:**
```
START_WEBAPP.bat
```

**Then open:** http://localhost:5000

Enjoy your AI-powered network security! 🔒
