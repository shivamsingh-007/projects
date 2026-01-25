# Getting Started with Zombie WiFi Detection System

## Quick Start (5 Minutes)

### Option 1: Run the Demo (Easiest - No Root Required)
```bash
python demo.py
```
This interactive demo walks you through the entire system using synthetic data.

### Option 2: Full Installation
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run installation wizard
python install.py

# 3. Test the system
python test_system.py
```

### Option 3: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate training data and train model
python main.py setup

# 3. Run detection (requires root/sudo)
sudo python main.py detect --interface eth0 --duration 60
```

## File Overview

| File | Purpose |
|------|---------|
| `main.py` | Main entry point - run all operations |
| `demo.py` | Interactive demo (no root needed) |
| `install.py` | Installation wizard |
| `test_system.py` | Test suite to verify installation |
| `data_collection.py` | Network packet capture and data generation |
| `feature_extraction.py` | Extract ML features from traffic |
| `model_training.py` | Train and evaluate ML models |
| `real_time_detection.py` | Real-time detection system |
| `visualization.py` | Create plots and dashboards |
| `config.yaml` | Configuration settings |
| `requirements.txt` | Python dependencies |

## Common Commands

```bash
# Setup and Training
python main.py setup                    # Initial setup
python main.py train                    # Train model
python main.py compare                  # Compare models

# Detection (requires root/sudo)
sudo python main.py detect              # Single scan
sudo python main.py monitor             # Continuous monitoring

# Analysis
python main.py analyze capture.pcap     # Analyze PCAP file

# Demo and Testing
python demo.py                          # Interactive demo
python test_system.py                   # Run tests
```

## Network Interface Names

Find your interface name:
```bash
# Linux/Mac
ifconfig
# or
ip addr show

# Common names:
# - eth0, wlan0 (Linux)
# - en0, en1 (Mac)
```

## Troubleshooting

### Permission Denied
```bash
# Run with sudo for packet capture
sudo python main.py detect
```

### Module Not Found
```bash
# Install dependencies
pip install -r requirements.txt
```

### Model Not Found
```bash
# Run setup first
python main.py setup
```

## System Architecture

```
User Input → Data Collection → Feature Extraction → ML Model → Alert
                    ↓                   ↓               ↓
              Packet Capture      30+ Features    Classification
                (Scapy)           (DNS, TCP,      (RF/XGBoost)
                                   Temporal)
```

## What the System Detects

1. **DNS Anomalies**: DGA domains, tunneling, excessive queries
2. **Port Scanning**: Sequential port probing
3. **C&C Beaconing**: Periodic communication patterns
4. **Traffic Injection**: HTTP/DNS manipulation
5. **Unusual Activity**: Nighttime traffic, failed connections
6. **Suspicious Ports**: Known malicious port usage

## Alert Levels

- **NORMAL**: Clean traffic (confidence < 50%)
- **LOW**: Slight suspicion (50-65%)
- **MEDIUM**: Suspicious activity (65-85%)
- **HIGH**: Likely zombie WiFi (85%+)
- **CRITICAL**: Definite zombie WiFi (high confidence + baseline deviation)

## Machine Learning Models

### Random Forest (Default)
- **Best for**: General purpose detection
- **Pros**: Fast, interpretable, robust
- **Cons**: Less accurate on complex patterns

### XGBoost
- **Best for**: Maximum accuracy
- **Pros**: Highest accuracy, handles imbalanced data
- **Cons**: Slightly slower

### Isolation Forest
- **Best for**: Novel attack detection
- **Pros**: Unsupervised, detects unknown attacks
- **Cons**: More false positives

## Expected Performance

On synthetic data:
- **Accuracy**: 95%+
- **Precision**: 93%+
- **Recall**: 91%+
- **F1-Score**: 92%+

Real-world performance varies based on:
- Training data quality
- Network complexity
- Attack sophistication

## Project Structure

```
zombie_wifi_detector/
├── main.py                 # Main entry point
├── demo.py                 # Interactive demo
├── install.py              # Installation wizard
├── test_system.py          # Test suite
├── data_collection.py      # Data collection
├── feature_extraction.py   # Feature engineering
├── model_training.py       # Model training
├── real_time_detection.py  # Detection system
├── visualization.py        # Visualization
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── README.md               # Full documentation
├── GETTING_STARTED.md      # This file
├── data/                   # Training data
├── models/                 # Trained models
└── logs/                   # Detection logs
```

## Next Steps

1. **Start with the demo**: `python demo.py`
2. **Read full documentation**: `README.md`
3. **Run on real traffic**: `sudo python main.py detect`
4. **Customize**: Edit `config.yaml` for your needs
5. **Contribute**: Improve features, add algorithms, enhance detection

## Support and Documentation

- **README.md**: Comprehensive documentation
- **config.yaml**: Configuration options
- **main.py --help**: Command line help
- **demo.py**: Interactive walkthrough

## Security Notice

⚠️ This tool is for educational and research purposes. Always ensure you have permission to monitor network traffic.

## License

Educational and research use only.

---

**Ready to detect zombie WiFi? Start with `python demo.py`!** 🔒
