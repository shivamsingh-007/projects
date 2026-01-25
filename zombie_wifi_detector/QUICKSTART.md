# Quick Start Guide

## Start the Web Application

### Easy Way:
```bash
python start.py
```

### Manual Way:
```bash
cd backend
python app.py
```

Then open your browser to: **http://localhost:5000**

## First Time Setup

1. Click "Register" to create your account
2. Enter username, email, and password
3. You'll be automatically logged in
4. Click "Scan Now" to check your network

## Features

- Beautiful web interface
- User registration and login
- Automatic network detection
- One-click scanning
- Hourly automatic protection
- Scan history and statistics

## Troubleshooting

### Permission Denied
Run as Administrator (Windows) or with sudo (Mac/Linux):
```bash
sudo python start.py
```

### Port 5000 In Use
Edit `backend/app.py` and change the port:
```python
app.run(port=5001)  # Change from 5000
```

### Model Not Found
Train the model first:
```bash
python main.py setup
```

## Need Help?

See `WEBAPP_README.md` for complete documentation.
