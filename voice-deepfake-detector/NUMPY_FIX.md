# 🔧 NumPy Version Compatibility Fix

## Error Message:
```
Invalid audio file: Numba needs NumPy 2.3 or less. Got NumPy 2.4.
```

## ✅ Solution 1: Downgrade NumPy (Recommended)

**Stop the backend server** (Ctrl+C)

**Run these commands:**
```cmd
cd C:\Users\shiva\Documents\projects\voice-deepfake-detector
venv\Scripts\activate
pip uninstall numpy -y
pip install "numpy<2.0"
```

**Verify the fix:**
```cmd
python -c "import numpy; print(numpy.__version__)"
```

**Should show:** `1.26.4` or similar (anything below 2.0)

**Restart backend:**
```cmd
cd backend
python app.py
```

**Test it works:**
- Upload an audio file
- Click "Analyze Audio"
- Should work now! ✅

---

## ✅ Solution 2: Disable Numba JIT (Already Applied)

The updated code now automatically disables numba JIT compilation which causes the NumPy conflict.

**Just restart your backend:**
```cmd
cd backend
python app.py
```

This will be slightly slower but avoids the NumPy version issue entirely.

---

## ✅ Solution 3: Reinstall All Dependencies

If the above don't work, reinstall everything cleanly:

```cmd
cd C:\Users\shiva\Documents\projects\voice-deepfake-detector
venv\Scripts\activate

# Uninstall problematic packages
pip uninstall numpy numba librosa -y

# Reinstall with correct versions
pip install "numpy<2.0"
pip install numba librosa
```

---

## ✅ Solution 4: Use Updated Package

Download the new ZIP file I just created with the fixes already applied:

1. **Stop both servers** (Ctrl+C)
2. **Extract new ZIP** over your existing folder
3. **Restart backend:**
   ```cmd
   cd backend
   python app.py
   ```
4. **Start frontend:**
   ```cmd
   cd frontend
   python -m http.server 3000
   ```

---

## 🔍 Verify It's Fixed

After applying any solution:

1. **Start backend**
2. **Upload audio file**
3. **Click "Analyze Audio"**

**Check backend terminal:**
- ❌ Before: `Invalid audio file: Numba needs NumPy 2.3 or less`
- ✅ After: `INFO:app:Processing file: audio.mp3`

**Check browser:**
- ✅ Results should appear!

---

## 📋 Why This Happens

NumPy 2.0+ introduced breaking changes. Numba (used by librosa for speed) hasn't fully caught up yet.

**Two solutions:**
1. Use older NumPy (< 2.0) - Works perfectly
2. Disable numba JIT - Slightly slower but no conflicts

---

## 🚀 Quick Command (Copy-Paste)

**All-in-one fix:**
```cmd
venv\Scripts\activate && pip uninstall numpy -y && pip install "numpy<2.0" && cd backend && python app.py
```

This will:
1. Activate venv
2. Remove new NumPy
3. Install compatible version
4. Start backend

---

## ✅ Expected Output After Fix

Backend terminal should show:
```
INFO:model:Using lightweight Random Forest model
INFO:__main__:Model loaded: True
 * Running on http://127.0.0.1:5000
```

Then when you analyze:
```
INFO:app:Processing file: audio.mp3
INFO:preprocessing:Extracting audio features...
INFO:app:Running deepfake detection model...
INFO:app:Analysis complete: REAL (67.3%)
```

No more NumPy errors! 🎉

---

## 🆘 Still Getting Error?

Share the **exact output** of:
```cmd
pip list | findstr numpy
pip list | findstr numba
pip list | findstr librosa
```

This will help diagnose the exact version conflict.
