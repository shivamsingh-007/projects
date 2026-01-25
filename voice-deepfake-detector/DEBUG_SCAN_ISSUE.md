# 🔧 Scan Results Not Loading - Debug Guide

## ✅ Quick Fix (Try This First)

### Option 1: Use Flask Frontend Server (Recommended)

**Stop the current frontend server** (Ctrl+C in Terminal 2)

**Start new frontend server:**
```cmd
cd frontend
python serve.py
```

**Then refresh browser:** `http://localhost:3000`

---

### Option 2: Check Browser Console

1. **Open browser** at `http://localhost:3000`
2. **Press F12** (or right-click → Inspect)
3. **Go to Console tab**
4. **Click "Analyze Audio"**
5. **Look for errors**

---

## 🐛 Common Issues

### Issue 1: JavaScript Not Loading

**Symptoms:** Page looks styled but clicking buttons does nothing

**Check Console for:**
```
Failed to load resource: script.js
```

**Fix:**
```cmd
# Stop frontend server (Ctrl+C)
# Restart with Flask server
cd frontend
python serve.py
```

---

### Issue 2: CORS Error

**Console shows:**
```
Access to fetch at 'http://localhost:5000/api/analyze' blocked by CORS
```

**Fix:** Backend CORS should be enabled. Check if backend is actually running:
```cmd
# In another terminal
curl http://localhost:5000/health
```

Should return JSON with `"status":"healthy"`

---

### Issue 3: API Connection Issue

**Backend shows 200 OK but results don't appear**

**Debug steps:**

1. **Check Network tab** (F12 → Network)
2. **Click "Analyze Audio"**
3. **Look for `/api/analyze` request**
4. **Click on it → Response tab**
5. **See what backend returned**

**If no request appears:**
- JavaScript file not loaded
- Try Option 1 (Flask server)

**If request appears with 200 OK:**
- Check Response tab for actual data
- If data is there but not showing → JavaScript rendering issue

---

### Issue 4: File Upload Issue

**File uploads but analysis doesn't start**

**Check backend terminal** - should show:
```
INFO:app:Processing file: audio.mp3
INFO:preprocessing:Extracting audio features...
```

**If you see nothing:**
- File not reaching backend
- Check browser Network tab for actual POST request

---

## 🔍 Step-by-Step Debugging

### Step 1: Verify Backend Works

```cmd
# Test health endpoint
curl http://localhost:5000/health

# Should return:
{"status":"healthy","model_loaded":true,"version":"1.0.0"}
```

### Step 2: Verify Frontend Loads

1. Open `http://localhost:3000`
2. Press F12 → Console
3. Should see: No errors (maybe warnings about fonts)
4. Type in console: `typeof analyzeAudio`
5. Should return: `"function"`

If returns `"undefined"` → **script.js not loaded!**

### Step 3: Test File Upload Manually

**Open browser console (F12 → Console) and paste:**

```javascript
// Test if fetch works
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(data => console.log('Backend OK:', data))
  .catch(err => console.error('Backend Error:', err));
```

Should log: `Backend OK: {status: "healthy", ...}`

### Step 4: Check Processing Overlay

After clicking "Analyze Audio":

**Should see:**
- Processing overlay appears (animated bars)
- Backend terminal shows activity
- After 2-3 seconds, results appear

**If overlay appears and never goes away:**
- Backend error (check backend terminal)
- API response issue (check Network tab)

---

## 💡 Working Test Procedure

1. **Start Backend:**
   ```cmd
   cd backend
   python app.py
   ```
   Wait for: `Running on http://127.0.0.1:5000`

2. **Start Frontend (Flask):**
   ```cmd
   cd frontend
   python serve.py
   ```
   Wait for: `Running on http://0.0.0.0:3000`

3. **Open Browser:**
   ```
   http://localhost:3000
   ```

4. **Upload Test File:**
   - Drag MP3/WAV file
   - Should see waveform
   - Click "Analyze Audio"

5. **Watch Both Terminals:**
   - **Backend:** Should show processing logs
   - **Frontend:** Should show GET/POST requests

6. **Results:**
   - Processing overlay shows
   - After 2-3 seconds: Results appear
   - Shows REAL or FAKE verdict

---

## 🚨 Emergency Fix: Test with cURL

If UI still doesn't work, test backend directly:

```cmd
# Create test request
curl -X POST http://localhost:5000/api/analyze ^
  -F "audio=@path\to\your\audio.mp3"
```

**Replace `path\to\your\audio.mp3` with actual file path**

Should return JSON:
```json
{
  "verdict": "REAL",
  "confidence": 67.3,
  "is_real": true,
  ...
}
```

If this works → Backend is fine, issue is in frontend
If this fails → Backend issue, check error message

---

## 📝 Detailed Error Messages

### Error: "Failed to fetch"
- **Cause:** Backend not running or wrong port
- **Fix:** Ensure backend on port 5000

### Error: "Network request failed"
- **Cause:** CORS or connection issue  
- **Fix:** Check both servers running

### Error: "Invalid audio file"
- **Cause:** File format not supported or corrupted
- **Fix:** Try WAV or MP3 file, 1-30 seconds

### Error: Nothing happens
- **Cause:** JavaScript not loaded
- **Fix:** Use Flask frontend server (serve.py)

---

## ✅ Verification Checklist

Before clicking "Analyze Audio":

- [ ] Backend shows: `Model loaded: True`
- [ ] Backend running on: `http://127.0.0.1:5000`
- [ ] Frontend running on: `http://localhost:3000`
- [ ] Browser console: No errors (F12)
- [ ] File uploaded: Waveform visible
- [ ] File size: Under 10MB
- [ ] File duration: 1-60 seconds

---

## 🎯 Most Likely Solution

**Based on your 304/404 errors, the issue is Python's http.server not serving files correctly.**

**Solution:**
```cmd
# Terminal 2 - Stop current frontend (Ctrl+C)
cd frontend
python serve.py

# Refresh browser
```

This uses Flask to serve frontend files properly, fixing MIME type and caching issues.

---

## 📞 Still Not Working?

1. **Share browser console errors** (F12 → Console)
2. **Share Network tab** (F12 → Network → filter by "analyze")
3. **Share backend terminal output** when clicking analyze

This will help identify the exact issue!
