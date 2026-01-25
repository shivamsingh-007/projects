# 🔧 Installation Troubleshooting Guide

## TensorFlow Installation Issues

### Problem: "Could not find a version that satisfies the requirement tensorflow"

This error occurs when TensorFlow isn't available for your system architecture (e.g., ARM-based systems like Raspberry Pi, Apple Silicon M1/M2 without Rosetta, or certain Linux distributions).

### ✅ Solution: Use Lightweight Mode

The application automatically falls back to a **lightweight Random Forest model** that doesn't require TensorFlow.

#### Option 1: Automatic Fallback (Recommended)
The setup script will automatically try TensorFlow first, then fall back to the lite version:

```bash
./setup.sh  # Linux/Mac
# or
setup.bat   # Windows
```

#### Option 2: Manual Lite Installation
If you want to skip TensorFlow entirely:

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install lite dependencies
cd backend
pip install -r requirements-lite.txt
```

### Differences Between Modes

| Feature | CNN Mode (TensorFlow) | Lite Mode (No TensorFlow) |
|---------|----------------------|---------------------------|
| **Deep Learning** | ✅ Yes (CNN) | ❌ No (Random Forest) |
| **Dependencies** | TensorFlow 2.10+ | scikit-learn only |
| **Size** | ~500MB | ~50MB |
| **Speed** | 2-3 seconds | 1-2 seconds (faster!) |
| **Accuracy (after training)** | 92-96% | 85-90% |
| **Works on** | x86_64, ARM64 (some) | All platforms |

**Both modes work out of the box** and provide the same user interface!

---

## Common Installation Issues

### Issue 1: Python Version
**Error:** `python: command not found` or version mismatch

**Solution:**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# If not installed, install Python 3.8+
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip python3-venv

# macOS (with Homebrew):
brew install python@3.11

# Windows: Download from python.org
```

### Issue 2: pip not found
**Error:** `pip: command not found`

**Solution:**
```bash
# Linux/Mac
python3 -m ensurepip --upgrade

# Windows
python -m ensurepip --upgrade
```

### Issue 3: Virtual Environment Fails
**Error:** Issues creating virtual environment

**Solution:**
```bash
# Install venv package
# Ubuntu/Debian:
sudo apt install python3-venv

# Then retry
python3 -m venv venv
```

### Issue 4: NumPy/SciPy Build Errors
**Error:** Failed to build wheel for numpy/scipy

**Solution:**
```bash
# Install build dependencies
# Ubuntu/Debian:
sudo apt install python3-dev build-essential libffi-dev

# macOS:
xcode-select --install

# Then install pre-built wheels
pip install --upgrade pip setuptools wheel
pip install numpy scipy --prefer-binary
```

### Issue 5: Librosa/soundfile Issues
**Error:** Cannot import librosa or soundfile

**Solution:**
```bash
# Install system audio libraries
# Ubuntu/Debian:
sudo apt install libsndfile1 ffmpeg

# macOS:
brew install libsndfile ffmpeg

# Windows: Usually works without extra steps
# If issues, download ffmpeg from ffmpeg.org
```

### Issue 6: Port Already in Use
**Error:** Address already in use (port 5000 or 3000)

**Solution:**
```bash
# Find and kill process using port
# Linux/Mac:
lsof -ti:5000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or change port in app.py:
# Line: app.run(port=5001)  # Change 5000 to 5001
```

---

## Platform-Specific Issues

### macOS Apple Silicon (M1/M2)

**TensorFlow not available:**
```bash
# Option 1: Use lite mode (recommended)
pip install -r backend/requirements-lite.txt

# Option 2: Use TensorFlow for macOS
# Install miniforge first
brew install miniforge
conda create -n deepfake python=3.10
conda activate deepfake
conda install -c apple tensorflow-deps
pip install tensorflow-macos tensorflow-metal
```

### Raspberry Pi / ARM Linux

**TensorFlow issues:**
```bash
# Use lite mode - it's faster on ARM anyway!
pip install -r backend/requirements-lite.txt

# Everything else should work fine
```

### Windows (without C++ Build Tools)

**Build errors for packages:**
```bash
# Download Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or use pre-built wheels
pip install --upgrade pip
pip install numpy scipy librosa --only-binary :all:
```

---

## Verification Steps

After installation, verify everything works:

### 1. Test Imports
```bash
cd backend
python3 -c "import flask, librosa, numpy; print('✓ All imports successful')"
```

### 2. Test Model
```bash
python3 -c "from model import DeepfakeDetector; d=DeepfakeDetector(); print('✓ Model loaded')"
```

### 3. Test Backend
```bash
# Start backend
python3 app.py

# In another terminal, test health endpoint
curl http://localhost:5000/health
# Should return: {"status":"healthy",...}
```

### 4. Run Test Script
```bash
cd ..
python3 test_installation.py
```

---

## Quick Fixes

### Reset Everything
```bash
# Remove virtual environment
rm -rf venv

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Start fresh
./setup.sh  # or setup.bat
```

### Minimal Installation
If you just want it to work quickly:
```bash
# Create venv
python3 -m venv venv
source venv/bin/activate

# Install minimal requirements
cd backend
pip install flask flask-cors librosa numpy scipy scikit-learn soundfile

# Start backend
python3 app.py
```

---

## Getting Help

If you're still having issues:

1. **Check Python version:** `python3 --version` (must be 3.8+)
2. **Check pip version:** `pip --version` (update with `pip install --upgrade pip`)
3. **Try lite mode:** Use `requirements-lite.txt` instead
4. **Check logs:** Look at terminal output for specific errors
5. **Google the error:** Most errors have solutions online
6. **Create an issue:** Share your OS, Python version, and error message

---

## Success Indicators

✅ Setup is successful when:
- No error messages during `./setup.sh`
- `test_installation.py` passes all tests
- Backend starts on `http://localhost:5000`
- Frontend loads at `http://localhost:3000`
- You can upload and analyze an audio file

**If you can see the UI and upload files, you're good to go!** 🎉
